"""Structured model output to proof-compatible article HTML."""

from __future__ import annotations

import html
import json
import math
import pathlib
import sys
from collections import Counter
from typing import Any

from nb_web.artifacts import build_artifacts
from nb_web.common import CITATION_RE, ROOT, WORK, parse_action_json, slugify, utc_now


def _sentence_html(text: str, source_map: dict[str, int]) -> str:
    markers: list[str] = []

    def stash(match):
        markers.append(match.group(1).upper())
        return f"@@CITE{len(markers) - 1}@@"

    escaped = html.escape(CITATION_RE.sub(stash, text), quote=False)
    for index, marker in enumerate(markers):
        number = source_map[marker]
        citation = f'<sup class="nb-cite"><a href="#s{number}">{number}</a></sup>'
        escaped = escaped.replace(f"@@CITE{index}@@", citation)
    return escaped


def _draft_errors(draft: dict[str, Any], sources: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not draft.get("publish", True):
        errors.append("draft declined publication")
    if not str(draft.get("title") or "").strip():
        errors.append("missing title")
    if not str(draft.get("dek") or "").strip():
        errors.append("missing dek")
    sections = draft.get("sections")
    if not isinstance(sections, list):
        return errors + ["sections must be a list"]
    if not 3 <= len(sections) <= 7:
        errors.append("article requires orientation plus 2-6 flex sections")
    ids = [
        slugify(str(section.get("id") or ""))
        for section in sections
        if isinstance(section, dict)
    ]
    if not ids or ids[0] != "orientation":
        errors.append("first section id must be orientation")
    if len(ids) != len(set(ids)):
        errors.append("section ids must be unique")

    known = {row["id"].upper(): row for row in sources}
    cited: list[str] = []
    for section in sections:
        if not isinstance(section, dict):
            errors.append("each section must be an object")
            continue
        paragraphs = section.get("paragraphs")
        if not isinstance(paragraphs, list) or not paragraphs:
            errors.append(f"section {section.get('id')} has no paragraphs")
            continue
        section_cites = []
        for paragraph in paragraphs:
            section_cites.extend(
                marker.upper() for marker in CITATION_RE.findall(str(paragraph))
            )
        if not section_cites:
            errors.append(f"section {section.get('id')} has no citations")
        cited.extend(section_cites)

    unknown = sorted(set(cited) - set(known))
    if unknown:
        errors.append(f"unknown source ids cited: {unknown}")
    unique = []
    for marker in cited:
        if marker in known and marker not in unique:
            unique.append(marker)
    kinds = Counter(known[marker]["kind_hint"] for marker in unique)
    if len(unique) < 6:
        errors.append(f"only {len(unique)} distinct sources cited; need 6")
    if kinds["primary"] < 2:
        errors.append(f"only {kinds['primary']} primary sources cited; need 2")
    if kinds["secondary"] < 2:
        errors.append(f"only {kinds['secondary']} secondary sources cited; need 2")
    return errors


def _render_article(
    draft: dict[str, Any], sources: list[dict[str, Any]]
) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    errors = _draft_errors(draft, sources)
    if errors:
        raise ValueError("\n".join(errors))

    source_by_id = {row["id"].upper(): row for row in sources}
    cited_order: list[str] = []
    for section in draft["sections"]:
        for paragraph in section["paragraphs"]:
            for marker in CITATION_RE.findall(str(paragraph)):
                marker = marker.upper()
                if marker not in cited_order:
                    cited_order.append(marker)
    source_map = {marker: index for index, marker in enumerate(cited_order, 1)}
    cited_sources = [source_by_id[marker] for marker in cited_order]

    title = " ".join(str(draft["title"]).split())
    dek = " ".join(str(draft["dek"]).split())
    slug = slugify(str(draft.get("slug") or title))
    date = utc_now().date().isoformat()
    tags = [slugify(str(tag)) for tag in draft.get("tags", []) if slugify(str(tag))][:8]

    section_html = []
    for section in draft["sections"]:
        section_id = slugify(str(section["id"]))
        heading = html.escape(" ".join(str(section["heading"]).split()))
        paragraphs = "\n".join(
            f"        <p>{_sentence_html(str(paragraph), source_map)}</p>"
            for paragraph in section["paragraphs"]
        )
        section_html.append(
            f'      <section data-nb-section="{section_id}" id="{section_id}">\n'
            f"        <h2>{heading}</h2>\n{paragraphs}\n      </section>"
        )

    source_items = []
    for number, row in enumerate(cited_sources, 1):
        label = html.escape(
            f"{row.get('source_name') or row['domain']} · {row['title']}"
        )
        url = html.escape(row["url"], quote=True)
        source_items.append(
            f'          <li id="s{number}"><a data-nb-source '
            f'data-nb-kind="{row["kind_hint"]}" href="{url}">{label}</a></li>'
        )

    meta = {
        "protocol": "1.1",
        "series": "the-one",
        "slug": slug,
        "template": "article",
        "title": title,
        "mode": "open",
        "order": None,
        "date": date,
        "tags": tags,
        "sources": len(cited_sources),
        "words": 0,
        "reading_minutes": 0,
        "dek": dek,
        "harness": "github-models-action",
        "model": "openai/gpt-4.1",
    }

    def build(meta_value: dict[str, Any]) -> str:
        serialized = json.dumps(meta_value, indent=2, ensure_ascii=False)
        serialized = (
            serialized.replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
        )
        meta_json = "\n".join("      " + line for line in serialized.splitlines())
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{html.escape(title)} · The One</title>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../assets/theme.css" />
    <link rel="stylesheet" href="../../assets/nb.css" />
    <script defer src="../../assets/nb.js"></script>
    <script type="application/json" id="nb-meta">
{meta_json}
    </script>
  </head>
  <body class="nb-article">
    <article class="nb-reading">
      <header>
        <div class="nb-eyebrow">The One · Tonight's Read</div>
        <h1 class="nb-title">{html.escape(title)}</h1>
        <p class="nb-dekline">{html.escape(dek)}</p>
        <div class="nb-byline"><span>{meta_value["reading_minutes"]} min read</span><span>{date}</span></div>
      </header>

{chr(10).join(section_html)}

      <section class="nb-sources" data-nb-section="sources" id="sources">
        <h2>Sources</h2>
        <ol>
{chr(10).join(source_items)}
        </ol>
      </section>
    </article>
  </body>
</html>
"""

    sys.path.insert(0, str(ROOT / "engine"))
    from nb.article import Article

    first = build(meta)
    parsed = Article()
    parsed.feed(first)
    meta["words"] = parsed.word_count
    meta["reading_minutes"] = max(1, math.ceil(parsed.word_count / 220))
    return build(meta), meta, cited_sources


def render(draft_path: str) -> int:
    try:
        draft = parse_action_json(pathlib.Path(draft_path))
        (WORK / "draft.json").write_text(
            json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        sources = json.loads((WORK / "sources.json").read_text(encoding="utf-8"))
        selection = json.loads((WORK / "selection.json").read_text(encoding="utf-8"))
        article, meta, cited_sources = _render_article(draft, sources)
        if not 1_200 <= int(meta["words"]) <= 2_200:
            raise ValueError(
                f"rendered article has {meta['words']} words; target is 1200-2200"
            )
        (WORK / "article.html").write_text(article, encoding="utf-8")
        (WORK / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (WORK / "slug.txt").write_text(str(meta["slug"]), encoding="utf-8")
        (WORK / "title.txt").write_text(str(meta["title"]), encoding="utf-8")
        build_artifacts(draft, selection, cited_sources, sources, meta)
        (WORK / "render-errors.txt").write_text("", encoding="utf-8")
        return 0
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        (WORK / "render-errors.txt").write_text(message + "\n", encoding="utf-8")
        print(message, file=sys.stderr)
        return 1
