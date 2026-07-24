from nb_web.article import _draft_errors, _render_article


def _sources():
    return [
        {
            "id": f"SRC{index}",
            "kind_hint": "primary" if index == 1 else "secondary",
            "source_name": f"Publisher {index}",
            "domain": f"source{index}.example",
            "title": f"Source {index}",
            "url": f"https://source{index}.example/record",
        }
        for index in range(1, 7)
    ]


def _draft():
    return {
        "publish": True,
        "slug": "structured-citations",
        "title": "The renderer owns citation syntax",
        "dek": "Models select evidence IDs; deterministic code emits the links.",
        "thesis": "Citation geometry should be machine-owned.",
        "tags": ["evidence"],
        "sections": [
            {
                "id": "orientation",
                "heading": "The evidence boundary",
                "paragraphs": [
                    {
                        "text": "The primary record defines the change.",
                        "source_ids": ["SRC1"],
                    },
                    {
                        "text": "Independent reporting supplies context.",
                        "source_ids": ["SRC2", "SRC3"],
                    },
                ],
            },
            {
                "id": "mechanism",
                "heading": "The renderer inserts links",
                "paragraphs": [
                    {
                        "text": "The model returns identifiers rather than markup.",
                        "source_ids": ["SRC4"],
                    },
                    {
                        "text": "First-cite order remains deterministic.",
                        "source_ids": ["SRC2", "SRC5"],
                    },
                ],
            },
            {
                "id": "consequence",
                "heading": "A syntax failure cannot erase evidence",
                "paragraphs": [
                    {
                        "text": "Every paragraph carries explicit evidence.",
                        "source_ids": ["SRC6"],
                    },
                    {
                        "text": "The article still cites six distinct sources.",
                        "source_ids": ["SRC1", "SRC3"],
                    },
                ],
            },
        ],
        "source_notes": [
            {"source_id": f"SRC{index}", "note": "Supports a test claim."}
            for index in range(1, 7)
        ],
        "editor_note": "Test fixture.",
    }


def test_structured_source_ids_render_as_links_in_first_cite_order():
    draft = _draft()
    sources = _sources()

    assert _draft_errors(draft, sources) == []
    rendered, meta, cited = _render_article(draft, sources)

    assert [row["id"] for row in cited] == [
        "SRC1",
        "SRC2",
        "SRC3",
        "SRC4",
        "SRC5",
        "SRC6",
    ]
    assert rendered.count('class="nb-cite"') == 9
    assert 'href="#s1"' in rendered
    assert 'href="#s6"' in rendered
    assert "[[SRC" not in rendered
    assert meta["sources"] == 6


def test_structured_paragraph_without_source_ids_is_rejected():
    draft = _draft()
    draft["sections"][0]["paragraphs"][0]["source_ids"] = []

    errors = _draft_errors(draft, _sources())

    assert any("paragraph 1 has no source_ids" in error for error in errors)
