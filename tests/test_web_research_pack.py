from nb_web.research import (
    MAX_PROMPT_SOURCE_TEXT,
    MAX_PROMPT_SOURCES,
    MAX_RESEARCH_PACK_CHARS,
    build_research_pack,
)


def _rows(count: int = 14):
    return [
        {
            "id": f"SRC{index}",
            "title": f"Source {index}",
            "kind_hint": "primary" if index == 1 else "secondary",
            "source_name": f"Publisher {index}",
            "domain": f"source{index}.example",
            "url": f"https://source{index}.example/record",
            "published": "2026-07-24",
            "text": (f"Evidence owned by source {index}. " * 500).strip(),
        }
        for index in range(1, count + 1)
    ]


def test_model_pack_is_bounded_without_erasing_full_record():
    selection = {
        "topic": "A testable mechanism",
        "angle": "Explain the boundary.",
        "why_now": "A documented change occurred.",
    }
    rows = _rows()

    prompt_pack = build_research_pack(
        selection,
        rows,
        text_limit=MAX_PROMPT_SOURCE_TEXT,
        source_limit=MAX_PROMPT_SOURCES,
    )
    full_pack = build_research_pack(selection, rows)

    assert len(prompt_pack) <= MAX_RESEARCH_PACK_CHARS
    assert "## SRC10" in prompt_pack
    assert "## SRC11" not in prompt_pack
    assert "Excerpt truncated for model context" in prompt_pack
    assert "## SRC14" in full_pack
    assert len(full_pack) > len(prompt_pack)
