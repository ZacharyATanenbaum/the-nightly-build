# ty: ignore
"""Duty and broad candidate collection."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import pathlib
import re
import sys
from typing import Any

import feedparser

from nb_web.common import (
    ROOT,
    WORK,
    clean_title,
    ensure_work,
    normalize_url,
    parse_date,
    primary_hint,
    request,
    run,
    strip_markup,
    utc_now,
    write_output,
)

FEEDS: tuple[tuple[str, str, str], ...] = (
    ("OpenAI News", "https://openai.com/news/rss.xml", "primary"),
    ("Anthropic News", "https://www.anthropic.com/news/rss.xml", "primary"),
    ("Google AI", "https://blog.google/technology/ai/rss/", "primary"),
    ("Microsoft AI", "https://blogs.microsoft.com/ai/feed/", "primary"),
    (
        "NVIDIA AI",
        "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
        "primary",
    ),
    ("GitHub AI", "https://github.blog/ai-and-ml/feed/", "primary"),
    (
        "arXiv AI",
        "https://export.arxiv.org/api/query?search_query=%28cat%3Acs.AI%20OR%20cat%3Acs.LG%20OR%20cat%3Acs.CL%29&start=0&max_results=50&sortBy=submittedDate&sortOrder=descending",
        "primary",
    ),
    (
        "Federal Register AI",
        "https://www.federalregister.gov/api/v1/documents.json?conditions%5Bterm%5D=artificial%20intelligence&per_page=30&order=newest",
        "primary-json",
    ),
    ("MIT Technology Review", "https://www.technologyreview.com/feed/", "secondary"),
    (
        "Ars Technica Technology Lab",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "secondary",
    ),
    (
        "TechCrunch AI",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "secondary",
    ),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "secondary"),
    (
        "IEEE Spectrum AI",
        "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
        "secondary",
    ),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss", "secondary"),
)


def collect_feed(
    name: str, url: str, kind: str
) -> tuple[list[dict[str, Any]], str | None]:
    try:
        response = request(url)
        if kind == "primary-json":
            items = []
            for result in response.json().get("results", []):
                item_url = normalize_url(
                    result.get("html_url") or result.get("pdf_url") or ""
                )
                if not item_url:
                    continue
                items.append(
                    {
                        "title": clean_title(result.get("title", "")),
                        "url": item_url,
                        "summary": strip_markup(result.get("abstract", "")),
                        "published": result.get("publication_date"),
                        "source_name": name,
                        "kind_hint": "primary",
                    }
                )
            return items, None

        feed = feedparser.parse(response.content)
        items = []
        for entry in feed.entries:
            item_url = normalize_url(entry.get("link", ""))
            if not item_url:
                continue
            items.append(
                {
                    "title": clean_title(entry.get("title", "")),
                    "url": item_url,
                    "summary": strip_markup(
                        entry.get("summary") or entry.get("description") or ""
                    )[:1_500],
                    "published": entry.get("published") or entry.get("updated"),
                    "source_name": name,
                    "kind_hint": kind,
                }
            )
        return items, None
    except Exception as exc:
        return [], f"{name}: {type(exc).__name__}: {exc}"


def recent_library(library: pathlib.Path) -> list[dict[str, Any]]:
    base = library / "library" / "the-one"
    if not base.is_dir():
        return []
    sys.path.insert(0, str(ROOT / "engine"))
    from nb.meta import read_meta

    rows = []
    for path in sorted(base.glob("*.html"), reverse=True):
        meta = read_meta(str(path)) or {}
        rows.append(
            {
                "slug": path.stem,
                "date": meta.get("date"),
                "title": meta.get("title"),
                "dek": meta.get("dek"),
            }
        )
    return rows[:30]


def prompt_candidates(ordered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a small, source-balanced commissioning view.

    GitHub Models enforces request-size limits below several models' nominal
    context windows. The full candidate record stays on disk for targeted
    research; the commissioning model sees only enough evidence to select a
    beat and exact starting URLs.
    """
    selected: list[dict[str, Any]] = []
    for kind in ("primary", "secondary"):
        selected.extend(
            row for row in ordered if row.get("kind_hint") == kind
        )
        selected = selected[: 8 if kind == "primary" else 16]
    selected.sort(key=lambda row: row.get("published_iso") or "", reverse=True)
    return [
        {
            "title": str(row.get("title") or "")[:180],
            "url": row["url"],
            "summary": str(row.get("summary") or "")[:180],
            "published": row.get("published_iso"),
            "source_name": row.get("source_name"),
            "kind_hint": row.get("kind_hint"),
        }
        for row in selected[:16]
    ]


def prepare(library_arg: str) -> int:
    ensure_work()
    library = pathlib.Path(library_arg).resolve()
    duty_raw = run(
        "uv",
        "run",
        "engine/duty.py",
        "--repo",
        ".",
        "--library",
        str(library),
    )
    duty = json.loads(duty_raw)
    due = next(
        (entry for entry in duty.get("due", []) if entry.get("series") == "the-one"),
        None,
    )
    (WORK / "duty.json").write_text(json.dumps(duty, indent=2), encoding="utf-8")
    if due is None:
        write_output("due", "false")
        write_output("reason", "the-one is not due")
        return 0

    candidates: list[dict[str, Any]] = []
    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(collect_feed, *feed) for feed in FEEDS]
        for future in concurrent.futures.as_completed(futures):
            items, error = future.result()
            candidates.extend(items)
            if error:
                errors.append(error)

    cutoff = utc_now() - dt.timedelta(days=14)
    dedup: dict[str, dict[str, Any]] = {}
    for item in candidates:
        title = item.get("title") or ""
        url = normalize_url(item.get("url") or "")
        if not title or not url:
            continue
        published = parse_date(item.get("published"))
        if published and published < cutoff:
            continue
        item["url"] = url
        item["kind_hint"] = primary_hint(url, item.get("kind_hint"))
        item["published_iso"] = published.isoformat() if published else None
        key = re.sub(r"\W+", " ", title.lower()).strip()
        if key and key not in dedup:
            dedup[key] = item

    ordered = sorted(
        dedup.values(),
        key=lambda row: row.get("published_iso") or "",
        reverse=True,
    )[:140]
    recent = recent_library(library)
    (WORK / "candidates-full.json").write_text(
        json.dumps(ordered, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (WORK / "candidates.json").write_text(
        json.dumps(prompt_candidates(ordered), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (WORK / "recent-full.json").write_text(
        json.dumps(recent, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (WORK / "recent.json").write_text(
        json.dumps(
            [
                {
                    "slug": row.get("slug"),
                    "date": row.get("date"),
                    "title": row.get("title"),
                }
                for row in recent[:12]
            ],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (WORK / "collection-errors.txt").write_text("\n".join(errors), encoding="utf-8")

    primary = sum(item["kind_hint"] == "primary" for item in ordered)
    secondary = sum(item["kind_hint"] == "secondary" for item in ordered)
    ready = len(ordered) >= 12 and primary >= 2 and secondary >= 4
    write_output("due", "true" if ready else "false")
    write_output(
        "reason",
        f"collected {len(ordered)} candidates ({primary} primary, {secondary} secondary)",
    )
    if not ready:
        print(
            "insufficient candidate source diversity; publishing nothing",
            file=sys.stderr,
        )
    return 0
