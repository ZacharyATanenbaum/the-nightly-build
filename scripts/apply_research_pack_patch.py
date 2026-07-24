from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"marker not found in {path}: {old[:160]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


research = Path("scripts/nb_web/research.py")
replace_once(
    research,
    "MAX_SOURCE_TEXT = 7_500\nMAX_RESEARCH_SOURCES = 14\n",
    "MAX_SOURCE_TEXT = 7_500\nMAX_RESEARCH_SOURCES = 14\nMAX_PROMPT_SOURCES = 10\nMAX_PROMPT_SOURCE_TEXT = 700\nMAX_RESEARCH_PACK_CHARS = 18_000\n",
)

replace_once(
    research,
    '''    return balanced\n\n\ndef research(selection_path: str) -> int:\n''',
    '''    return balanced\n\n\ndef build_research_pack(\n    selection: dict[str, Any],\n    rows: list[dict[str, Any]],\n    *,\n    text_limit: int | None = None,\n    source_limit: int | None = None,\n) -> str:\n    """Serialize evidence for either the model or the durable audit record.\n\n    The model-facing pack is deliberately bounded below GitHub Models' request\n    limit. The complete fetched text remains in ``sources.json`` and in the\n    separate durable research record, so reducing prompt size never erases the\n    machine-auditable evidence.\n    """\n    lines = [\n        f"# Research pack: {selection.get('topic', '')}",\n        "",\n        f"Angle: {selection.get('angle', '')}",\n        f"Why now: {selection.get('why_now', selection.get('reason', ''))}",\n        "",\n        "Use only the sources below. Kind labels are provisional but conservative: a source is primary only when it owns the underlying claim.",\n        "",\n    ]\n    selected = rows if source_limit is None else rows[:source_limit]\n    for row in selected:\n        text = str(row["text"])\n        if text_limit is not None and len(text) > text_limit:\n            excerpt = text[:text_limit].rsplit(" ", 1)[0].rstrip()\n            text = excerpt + "\\n[Excerpt truncated for model context; do not infer omitted content.]"\n        lines.extend(\n            [\n                f"## {row['id']} — {row['title']}",\n                f"Kind hint: {row['kind_hint']}",\n                f"Publisher/domain: {row.get('source_name') or row['domain']} / {row['domain']}",\n                f"URL: {row['url']}",\n                f"Published: {row.get('published') or 'unknown'}",\n                "",\n                text,\n                "",\n            ]\n        )\n    return "\\n".join(lines)\n\n\ndef research(selection_path: str) -> int:\n''',
)

old = '''    lines = [\n        f"# Research pack: {selection.get('topic', '')}",\n        "",\n        f"Angle: {selection.get('angle', '')}",\n        f"Why now: {selection.get('why_now', selection.get('reason', ''))}",\n        "",\n        "Use only the sources below. Kind labels are provisional but conservative: a source is primary only when it owns the underlying claim.",\n        "",\n    ]\n    for row in balanced:\n        lines.extend(\n            [\n                f"## {row['id']} — {row['title']}",\n                f"Kind hint: {row['kind_hint']}",\n                f"Publisher/domain: {row.get('source_name') or row['domain']} / {row['domain']}",\n                f"URL: {row['url']}",\n                f"Published: {row.get('published') or 'unknown'}",\n                "",\n                row["text"],\n                "",\n            ]\n        )\n    (WORK / "sources.json").write_text(\n        json.dumps(balanced, indent=2, ensure_ascii=False), encoding="utf-8"\n    )\n    (WORK / "fetch-failures.json").write_text(\n        json.dumps(failures, indent=2, ensure_ascii=False), encoding="utf-8"\n    )\n    (WORK / "research-pack.md").write_text("\\n".join(lines), encoding="utf-8")\n'''
new = '''    full_pack = build_research_pack(selection, balanced)\n    prompt_pack = build_research_pack(\n        selection,\n        balanced,\n        text_limit=MAX_PROMPT_SOURCE_TEXT,\n        source_limit=MAX_PROMPT_SOURCES,\n    )\n    if len(prompt_pack) > MAX_RESEARCH_PACK_CHARS:\n        raise ValueError(\n            f"model research pack is {len(prompt_pack)} characters; "\n            f"limit is {MAX_RESEARCH_PACK_CHARS}"\n        )\n\n    (WORK / "sources.json").write_text(\n        json.dumps(balanced, indent=2, ensure_ascii=False), encoding="utf-8"\n    )\n    (WORK / "fetch-failures.json").write_text(\n        json.dumps(failures, indent=2, ensure_ascii=False), encoding="utf-8"\n    )\n    (WORK / "research-record.md").write_text(full_pack, encoding="utf-8")\n    (WORK / "research-pack.md").write_text(prompt_pack, encoding="utf-8")\n'''
replace_once(research, old, new)

Path("tests/test_web_research_pack.py").write_text(
    '''from nb_web.research import (\n    MAX_PROMPT_SOURCE_TEXT,\n    MAX_PROMPT_SOURCES,\n    MAX_RESEARCH_PACK_CHARS,\n    build_research_pack,\n)\n\n\ndef _rows(count: int = 14):\n    return [\n        {\n            "id": f"SRC{index}",\n            "title": f"Source {index}",\n            "kind_hint": "primary" if index == 1 else "secondary",\n            "source_name": f"Publisher {index}",\n            "domain": f"source{index}.example",\n            "url": f"https://source{index}.example/record",\n            "published": "2026-07-24",\n            "text": (f"Evidence owned by source {index}. " * 500).strip(),\n        }\n        for index in range(1, count + 1)\n    ]\n\n\ndef test_model_pack_is_bounded_without_erasing_full_record():\n    selection = {\n        "topic": "A testable mechanism",\n        "angle": "Explain the boundary.",\n        "why_now": "A documented change occurred.",\n    }\n    rows = _rows()\n\n    prompt_pack = build_research_pack(\n        selection,\n        rows,\n        text_limit=MAX_PROMPT_SOURCE_TEXT,\n        source_limit=MAX_PROMPT_SOURCES,\n    )\n    full_pack = build_research_pack(selection, rows)\n\n    assert len(prompt_pack) <= MAX_RESEARCH_PACK_CHARS\n    assert "## SRC10" in prompt_pack\n    assert "## SRC11" not in prompt_pack\n    assert "Excerpt truncated for model context" in prompt_pack\n    assert "## SRC14" in full_pack\n    assert len(full_pack) > len(prompt_pack)\n''',
    encoding="utf-8",
)

Path(__file__).unlink()
