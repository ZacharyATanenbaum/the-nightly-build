from nb_web import research
from nb_web.article import _draft_errors
from nb_web.common import primary_hint
from nb_web.research import official_feed_record


def _official_row(summary: str = "A" * 180):
    return {
        "title": "Launching Health in ChatGPT",
        "url": "https://openai.com/index/health-in-chatgpt",
        "summary": summary,
        "published": "2026-07-23T00:00:00+00:00",
        "source_name": "OpenAI News",
        "kind_hint": "primary",
    }


def test_aggregators_never_own_the_claim_even_with_a_stale_hint():
    assert (
        primary_hint("https://news.google.com/rss/articles/example", "primary")
        == "secondary"
    )
    assert (
        primary_hint("https://www.google.com/search?q=example", "primary")
        == "secondary"
    )
    assert primary_hint("https://blog.google/technology/ai/example") == "primary"
    assert primary_hint("https://openai.com/index/example", "primary") == "primary"


def test_official_feed_record_preserves_substantive_primary_evidence():
    record = official_feed_record(_official_row(), reason="HTTPError: 403")

    assert record is not None
    assert record["kind_hint"] == "primary"
    assert record["retrieval"] == "official-feed-record"
    assert "Official feed record from OpenAI News" in record["text"]
    assert record["fetch_error"] == "HTTPError: 403"


def test_official_feed_record_refuses_aggregators_and_thin_snippets():
    aggregator = _official_row()
    aggregator["url"] = "https://news.google.com/rss/articles/example"
    assert official_feed_record(aggregator) is None
    assert official_feed_record(_official_row("too short")) is None


def test_fetch_source_falls_back_only_to_owner_authored_feed_text(monkeypatch):
    def blocked(_url):
        raise RuntimeError("blocked")

    monkeypatch.setattr(research, "request", blocked)
    monkeypatch.setattr(research, "jina_fallback", lambda _url: "")

    record = research.fetch_source(_official_row())

    assert record is not None
    assert record["kind_hint"] == "primary"
    assert record["retrieval"] == "official-feed-record"


def test_article_gate_accepts_one_primary_and_five_independent_secondaries():
    sources = [
        {"id": "SRC1", "kind_hint": "primary"},
        *[{"id": f"SRC{index}", "kind_hint": "secondary"} for index in range(2, 7)],
    ]
    draft = {
        "publish": True,
        "title": "A concrete mechanism",
        "dek": "The consequence arrives through a specific system boundary.",
        "sections": [
            {
                "id": "orientation",
                "heading": "The record",
                "paragraphs": ["Claim [[SRC1]] and context [[SRC2]]."],
            },
            {
                "id": "mechanism",
                "heading": "Where the mechanism sits",
                "paragraphs": ["Mechanism [[SRC3]] with corroboration [[SRC4]]."],
            },
            {
                "id": "consequence",
                "heading": "What changes",
                "paragraphs": ["Consequence [[SRC5]] and limit [[SRC6]]."],
            },
        ],
    }

    assert _draft_errors(draft, sources) == []
