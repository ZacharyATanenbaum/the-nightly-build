"""Targeted search, retrieval, and source-pack construction."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import io
import json
import pathlib
import re
import urllib.parse
from collections import Counter
from typing import Any

import feedparser
import trafilatura
from bs4 import BeautifulSoup
from pypdf import PdfReader

from nb_web.common import (
    WORK,
    clean_title,
    ensure_work,
    host_for,
    normalize_url,
    parse_action_json,
    parse_date,
    primary_hint,
    request,
    strip_markup,
    write_output,
)

MAX_SOURCE_TEXT = 7_500
MAX_RESEARCH_SOURCES = 14


def search_gdelt(query: str) -> list[dict[str, Any]]:
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": "75",
        "format": "json",
        "sort": "hybridrel",
        "timespan": "7d",
    }
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(
        params
    )
    try:
        payload = request(url).json()
    except Exception:
        return []
    rows = []
    for article in payload.get("articles", []):
        item_url = normalize_url(article.get("url") or "")
        if not item_url:
            continue
        rows.append(
            {
                "title": clean_title(article.get("title") or ""),
                "url": item_url,
                "summary": "",
                "published": article.get("seendate"),
                "source_name": article.get("domain") or host_for(item_url),
                "kind_hint": primary_hint(item_url),
            }
        )
    return rows


def search_bing(query: str) -> list[dict[str, Any]]:
    url = "https://www.bing.com/news/search?" + urllib.parse.urlencode(
        {"q": query, "format": "rss", "setlang": "en-US"}
    )
    try:
        feed = feedparser.parse(request(url).content)
    except Exception:
        return []
    rows = []
    for entry in feed.entries:
        item_url = normalize_url(entry.get("link") or "")
        if item_url:
            rows.append(
                {
                    "title": clean_title(entry.get("title") or ""),
                    "url": item_url,
                    "summary": strip_markup(entry.get("summary") or ""),
                    "published": entry.get("published"),
                    "source_name": "Bing News",
                    "kind_hint": primary_hint(item_url),
                }
            )
    return rows


def search_google_news(query: str) -> list[dict[str, Any]]:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": f"{query} when:7d", "hl": "en-US", "gl": "US", "ceid": "US:en"}
    )
    try:
        feed = feedparser.parse(request(url).content)
    except Exception:
        return []
    rows = []
    for entry in feed.entries:
        item_url = normalize_url(entry.get("link") or "")
        if not item_url:
            continue
        source = entry.get("source", {})
        source_name = source.get("title") if isinstance(source, dict) else "Google News"
        rows.append(
            {
                "title": clean_title(entry.get("title") or ""),
                "url": item_url,
                "summary": strip_markup(entry.get("summary") or ""),
                "published": entry.get("published"),
                "source_name": source_name or "Google News",
                "kind_hint": "secondary",
            }
        )
    return rows


def extract_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    parts = []
    for page in reader.pages[:16]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def extract_html(content: bytes, url: str, encoding: str | None) -> str:
    text = content.decode(encoding or "utf-8", errors="replace")
    extracted = trafilatura.extract(
        text,
        url=url,
        include_comments=False,
        include_tables=True,
        include_links=False,
        favor_precision=True,
    )
    if extracted:
        return extracted
    soup = BeautifulSoup(text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)


def jina_fallback(url: str) -> str:
    reader_url = "https://r.jina.ai/http://" + url.removeprefix(
        "https://"
    ).removeprefix("http://")
    try:
        return request(reader_url, max_bytes=2 * 1024 * 1024).text
    except Exception:
        return ""


def official_feed_record(
    row: dict[str, Any], *, reason: str | None = None
) -> dict[str, Any] | None:
    """Preserve a substantive owner-authored feed record when its page blocks bots.

    The fallback is deliberately unavailable to secondary and aggregator rows. It
    carries only text the owner published in its feed, records why the full page
    was unavailable, and never upgrades a search result into a primary source.
    """
    url = str(row.get("url") or "")
    if primary_hint(url, row.get("kind_hint")) != "primary":
        return None
    title = clean_title(str(row.get("title") or ""))
    summary = strip_markup(str(row.get("summary") or ""))
    if not title or len(summary) < 120:
        return None
    publisher = str(row.get("source_name") or host_for(url))
    published = str(row.get("published") or "unknown")
    text = (
        f"Official feed record from {publisher}.\n"
        f"Title: {title}\n"
        f"Published: {published}\n\n"
        f"{summary}"
    )
    return {
        **row,
        "url": url,
        "domain": host_for(url),
        "kind_hint": "primary",
        "text": text[:MAX_SOURCE_TEXT],
        "text_length": len(text),
        "retrieval": "official-feed-record",
        "fetch_error": reason,
    }


def fetch_source(row: dict[str, Any]) -> dict[str, Any] | None:
    url = row["url"]
    try:
        response = request(url)
        final_url = normalize_url(response.url) or url
        content_type = (response.headers.get("content-type") or "").lower()
        if "pdf" in content_type or final_url.lower().endswith(".pdf"):
            text = extract_pdf(response.content)
        else:
            text = extract_html(response.content, final_url, response.encoding)
    except Exception as first_error:
        text = jina_fallback(url)
        final_url = url
        if not text:
            reason = f"{type(first_error).__name__}: {first_error}"
            fallback = official_feed_record(row, reason=reason)
            if fallback is not None:
                return fallback
            row["fetch_error"] = reason
            return None
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) < 450:
        fallback = official_feed_record(
            row, reason=f"extracted page was only {len(text)} characters"
        )
        if fallback is not None:
            return fallback
        return None
    return {
        **row,
        "url": final_url,
        "domain": host_for(final_url),
        "kind_hint": primary_hint(final_url, row.get("kind_hint")),
        "text": text[:MAX_SOURCE_TEXT],
        "text_length": len(text),
        "retrieval": "page",
    }


def _search_rows(queries: list[str]) -> list[dict[str, Any]]:
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for query in queries:
            futures.extend(
                [
                    pool.submit(search_gdelt, query),
                    pool.submit(search_bing, query),
                    pool.submit(search_google_news, query),
                ]
            )
        for future in concurrent.futures.as_completed(futures):
            rows.extend(future.result())
    return rows


def _balance(fetched: list[dict[str, Any]]) -> list[dict[str, Any]]:
    balanced: list[dict[str, Any]] = []
    domain_counts: Counter[str] = Counter()
    for target_kind, target_count in (("primary", 5), ("secondary", 9)):
        for row in fetched:
            if row in balanced or row["kind_hint"] != target_kind:
                continue
            domain = row["domain"]
            if domain_counts[domain] >= 2:
                continue
            balanced.append(row)
            domain_counts[domain] += 1
            count = sum(item["kind_hint"] == target_kind for item in balanced)
            if count >= target_count:
                break
    for row in fetched:
        if len(balanced) >= MAX_RESEARCH_SOURCES:
            break
        if row in balanced or domain_counts[row["domain"]] >= 2:
            continue
        balanced.append(row)
        domain_counts[row["domain"]] += 1
    return balanced


def research(selection_path: str) -> int:
    ensure_work()
    selection = parse_action_json(pathlib.Path(selection_path))
    (WORK / "selection.json").write_text(
        json.dumps(selection, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if not selection.get("publish", True):
        write_output("ready", "false")
        write_output("reason", str(selection.get("reason") or "selector declined"))
        return 0

    candidates = json.loads((WORK / "candidates-full.json").read_text(encoding="utf-8"))
    by_url = {row["url"]: row for row in candidates}
    chosen_urls = [normalize_url(url) for url in selection.get("primary_urls", [])]
    chosen_urls += [normalize_url(url) for url in selection.get("secondary_urls", [])]
    chosen_urls += [
        normalize_url(url) for url in selection.get("selected_candidate_urls", [])
    ]

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(row: dict[str, Any]) -> None:
        url = normalize_url(row.get("url") or "")
        if not url or url in seen:
            return
        seen.add(url)
        item = dict(row)
        item["url"] = url
        item["kind_hint"] = primary_hint(url, item.get("kind_hint"))
        rows.append(item)

    for url in chosen_urls:
        if url:
            add(
                by_url.get(url)
                or {
                    "title": url,
                    "url": url,
                    "summary": "",
                    "source_name": host_for(url),
                }
            )

    queries = [str(selection.get("query") or selection.get("topic") or "")]
    queries.extend(str(value) for value in selection.get("search_terms", []) if value)
    queries = [query.strip() for query in queries if query.strip()][:4]
    for row in _search_rows(queries):
        add(row)

    terms = {
        token
        for token in re.findall(r"[a-z0-9]{4,}", " ".join(queries).lower())
        if token not in {"with", "from", "that", "this", "about", "latest", "news"}
    }
    scored = []
    for row in candidates:
        haystack = f"{row.get('title', '')} {row.get('summary', '')}".lower()
        score = sum(term in haystack for term in terms)
        if score:
            scored.append((score, row))
    for _, row in sorted(scored, key=lambda item: item[0], reverse=True)[:30]:
        add(row)

    fetched: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        future_map = {pool.submit(fetch_source, row): row for row in rows[:50]}
        for future in concurrent.futures.as_completed(future_map):
            row = future_map[future]
            try:
                result = future.result()
            except Exception as exc:
                result = None
                row = {**row, "fetch_error": f"{type(exc).__name__}: {exc}"}
            if result:
                fetched.append(result)
            else:
                failures.append(row)

    selected_order = {url: index for index, url in enumerate(chosen_urls) if url}
    epoch = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    fetched.sort(
        key=lambda row: (
            0 if row["url"] in selected_order else 1,
            selected_order.get(row["url"], 999),
            0 if row["kind_hint"] == "primary" else 1,
            -(parse_date(row.get("published")) or epoch).timestamp(),
        )
    )
    balanced = _balance(fetched)
    for index, row in enumerate(balanced, 1):
        row["id"] = f"SRC{index}"

    primary_count = sum(row["kind_hint"] == "primary" for row in balanced)
    secondary_count = sum(row["kind_hint"] == "secondary" for row in balanced)
    ready = len(balanced) >= 8 and primary_count >= 1 and secondary_count >= 5

    lines = [
        f"# Research pack: {selection.get('topic', '')}",
        "",
        f"Angle: {selection.get('angle', '')}",
        f"Why now: {selection.get('why_now', selection.get('reason', ''))}",
        "",
        "Use only the sources below. Kind labels are provisional but conservative: a source is primary only when it owns the underlying claim.",
        "",
    ]
    for row in balanced:
        lines.extend(
            [
                f"## {row['id']} — {row['title']}",
                f"Kind hint: {row['kind_hint']}",
                f"Publisher/domain: {row.get('source_name') or row['domain']} / {row['domain']}",
                f"URL: {row['url']}",
                f"Published: {row.get('published') or 'unknown'}",
                "",
                row["text"],
                "",
            ]
        )
    (WORK / "sources.json").write_text(
        json.dumps(balanced, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (WORK / "fetch-failures.json").write_text(
        json.dumps(failures, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (WORK / "research-pack.md").write_text("\n".join(lines), encoding="utf-8")
    write_output("ready", "true" if ready else "false")
    write_output(
        "reason",
        f"fetched {len(balanced)} usable sources ({primary_count} primary, {secondary_count} secondary)",
    )
    return 0
