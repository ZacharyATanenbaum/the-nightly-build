from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"marker not found in {path}: {old[:180]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


article = Path("scripts/nb_web/article.py")
replace_once(
    article,
    '''def _sentence_html(text: str, source_map: dict[str, int]) -> str:\n    markers: list[str] = []\n\n    def stash(match):\n        markers.append(match.group(1).upper())\n        return f"@@CITE{len(markers) - 1}@@"\n\n    escaped = html.escape(CITATION_RE.sub(stash, text), quote=False)\n    for index, marker in enumerate(markers):\n        number = source_map[marker]\n        citation = f'<sup class="nb-cite"><a href="#s{number}">{number}</a></sup>'\n        escaped = escaped.replace(f"@@CITE{index}@@", citation)\n    return escaped\n''',
    '''def _paragraph_text(paragraph: object) -> str:\n    if isinstance(paragraph, dict):\n        return str(paragraph.get("text") or "")\n    return str(paragraph)\n\n\ndef _paragraph_sources(paragraph: object) -> list[str]:\n    if isinstance(paragraph, dict):\n        raw = paragraph.get("source_ids")\n        if not isinstance(raw, list):\n            return []\n        markers: list[str] = []\n        for value in raw:\n            marker = str(value).strip().upper()\n            if marker and marker not in markers:\n                markers.append(marker)\n        return markers\n    return [marker.upper() for marker in CITATION_RE.findall(str(paragraph))]\n\n\ndef _sentence_html(text: str, source_map: dict[str, int]) -> str:\n    markers: list[str] = []\n\n    def stash(match):\n        markers.append(match.group(1).upper())\n        return f"@@CITE{len(markers) - 1}@@"\n\n    escaped = html.escape(CITATION_RE.sub(stash, text), quote=False)\n    for index, marker in enumerate(markers):\n        number = source_map[marker]\n        citation = f'<sup class="nb-cite"><a href="#s{number}">{number}</a></sup>'\n        escaped = escaped.replace(f"@@CITE{index}@@", citation)\n    return escaped\n\n\ndef _paragraph_html(paragraph: object, source_map: dict[str, int]) -> str:\n    if not isinstance(paragraph, dict):\n        return _sentence_html(str(paragraph), source_map)\n    escaped = html.escape(_paragraph_text(paragraph), quote=False)\n    citations = "".join(\n        f'<sup class="nb-cite"><a href="#s{source_map[marker]}">'\n        f"{source_map[marker]}</a></sup>"\n        for marker in _paragraph_sources(paragraph)\n    )\n    return escaped + citations\n''',
)

replace_once(
    article,
    '''        section_cites = []\n        for paragraph in paragraphs:\n            section_cites.extend(\n                marker.upper() for marker in CITATION_RE.findall(str(paragraph))\n            )\n        if not section_cites:\n            errors.append(f"section {section.get('id')} has no citations")\n        cited.extend(section_cites)\n''',
    '''        section_cites: list[str] = []\n        for paragraph_index, paragraph in enumerate(paragraphs, 1):\n            if isinstance(paragraph, dict) and not _paragraph_text(paragraph).strip():\n                errors.append(\n                    f"section {section.get('id')} paragraph {paragraph_index} has no text"\n                )\n            paragraph_cites = _paragraph_sources(paragraph)\n            if isinstance(paragraph, dict) and not paragraph_cites:\n                errors.append(\n                    f"section {section.get('id')} paragraph {paragraph_index} has no source_ids"\n                )\n            section_cites.extend(paragraph_cites)\n        if not section_cites:\n            errors.append(f"section {section.get('id')} has no citations")\n        cited.extend(section_cites)\n''',
)

replace_once(
    article,
    '''    for section in draft["sections"]:\n        for paragraph in section["paragraphs"]:\n            for marker in CITATION_RE.findall(str(paragraph)):\n                marker = marker.upper()\n                if marker not in cited_order:\n                    cited_order.append(marker)\n''',
    '''    for section in draft["sections"]:\n        for paragraph in section["paragraphs"]:\n            for marker in _paragraph_sources(paragraph):\n                if marker not in cited_order:\n                    cited_order.append(marker)\n''',
)

replace_once(
    article,
    '''        paragraphs = "\\n".join(\n            f"        <p>{_sentence_html(str(paragraph), source_map)}</p>"\n            for paragraph in section["paragraphs"]\n        )\n''',
    '''        paragraphs = "\\n".join(\n            f"        <p>{_paragraph_html(paragraph, source_map)}</p>"\n            for paragraph in section["paragraphs"]\n        )\n''',
)

paragraph_schema = '''              "paragraphs": {\n                "type": "array",\n                "minItems": 2,\n                "maxItems": 6,\n                "items": {"type": "string"}\n              }'''
structured_schema = '''              "paragraphs": {\n                "type": "array",\n                "minItems": 2,\n                "maxItems": 6,\n                "items": {\n                  "type": "object",\n                  "properties": {\n                    "text": {"type": "string"},\n                    "source_ids": {\n                      "type": "array",\n                      "items": {"type": "string"},\n                      "minItems": 1,\n                      "maxItems": 4,\n                      "uniqueItems": true\n                    }\n                  },\n                  "required": ["text", "source_ids"],\n                  "additionalProperties": false\n                }\n              }'''

write_prompt = Path(".github/prompts/nightly-write.prompt.yml")
replace_once(
    write_prompt,
    "Every section must contain citations. Cite with exact markers such as [[SRC1]] immediately after the supported claim. Use at least six distinct sources, at least one marked primary and at least three marked secondary.",
    "Every paragraph is an object with plain `text` and a nonempty `source_ids` array. Use exact IDs from the research pack such as SRC1; the renderer, not you, inserts citation links. Across the article use at least six distinct sources, at least one marked primary and at least three marked secondary.",
)
replace_once(
    write_prompt,
    "Avoid markdown and HTML in paragraph text; citation markers are the only special syntax.",
    "Avoid markdown, HTML, or citation syntax in paragraph text. Put evidence IDs only in `source_ids`.",
)
replace_once(write_prompt, paragraph_schema, structured_schema)

revise_prompt = Path(".github/prompts/nightly-revise.prompt.yml")
replace_once(
    revise_prompt,
    "Return a complete replacement object under the same contract. Use 1,350-1,850 prose words, four or five sections beginning with orientation, citations in every section, six or more distinct sources, one or more primary and three or more secondary.",
    "Return a complete replacement object under the same contract. Every paragraph must have plain text and a nonempty `source_ids` array using exact IDs from the research pack. Use 1,350-1,850 prose words, four or five sections beginning with orientation, six or more distinct sources overall, one or more primary and three or more secondary.",
)
replace_once(revise_prompt, paragraph_schema, structured_schema)

Path("tests/test_web_structured_citations.py").write_text(
    '''from nb_web.article import _draft_errors, _render_article\n\n\ndef _sources():\n    return [\n        {\n            "id": f"SRC{index}",\n            "kind_hint": "primary" if index == 1 else "secondary",\n            "source_name": f"Publisher {index}",\n            "domain": f"source{index}.example",\n            "title": f"Source {index}",\n            "url": f"https://source{index}.example/record",\n        }\n        for index in range(1, 7)\n    ]\n\n\ndef _draft():\n    return {\n        "publish": True,\n        "slug": "structured-citations",\n        "title": "The renderer owns citation syntax",\n        "dek": "Models select evidence IDs; deterministic code emits the links.",\n        "thesis": "Citation geometry should be machine-owned.",\n        "tags": ["evidence"],\n        "sections": [\n            {\n                "id": "orientation",\n                "heading": "The evidence boundary",\n                "paragraphs": [\n                    {"text": "The primary record defines the change.", "source_ids": ["SRC1"]},\n                    {"text": "Independent reporting supplies context.", "source_ids": ["SRC2", "SRC3"]},\n                ],\n            },\n            {\n                "id": "mechanism",\n                "heading": "The renderer inserts links",\n                "paragraphs": [\n                    {"text": "The model returns identifiers rather than markup.", "source_ids": ["SRC4"]},\n                    {"text": "First-cite order remains deterministic.", "source_ids": ["SRC2", "SRC5"]},\n                ],\n            },\n            {\n                "id": "consequence",\n                "heading": "A syntax failure cannot erase evidence",\n                "paragraphs": [\n                    {"text": "Every paragraph carries explicit evidence.", "source_ids": ["SRC6"]},\n                    {"text": "The article still cites six distinct sources.", "source_ids": ["SRC1", "SRC3"]},\n                ],\n            },\n        ],\n        "source_notes": [\n            {"source_id": f"SRC{index}", "note": "Supports a test claim."}\n            for index in range(1, 7)\n        ],\n        "editor_note": "Test fixture.",\n    }\n\n\ndef test_structured_source_ids_render_as_links_in_first_cite_order():\n    draft = _draft()\n    sources = _sources()\n\n    assert _draft_errors(draft, sources) == []\n    rendered, meta, cited = _render_article(draft, sources)\n\n    assert [row["id"] for row in cited] == [\n        "SRC1",\n        "SRC2",\n        "SRC3",\n        "SRC4",\n        "SRC5",\n        "SRC6",\n    ]\n    assert rendered.count('class="nb-cite"') == 9\n    assert 'href="#s1"' in rendered\n    assert 'href="#s6"' in rendered\n    assert "[[SRC" not in rendered\n    assert meta["sources"] == 6\n\n\ndef test_structured_paragraph_without_source_ids_is_rejected():\n    draft = _draft()\n    draft["sections"][0]["paragraphs"][0]["source_ids"] = []\n\n    errors = _draft_errors(draft, _sources())\n\n    assert any("paragraph 1 has no source_ids" in error for error in errors)\n''',
    encoding="utf-8",
)

Path(__file__).unlink()
