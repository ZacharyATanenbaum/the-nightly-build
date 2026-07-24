from nb_web.cluster import build_commissioning_clusters


def _row(title, url, kind, summary=""):
    return {
        "title": title,
        "url": url,
        "kind_hint": kind,
        "summary": summary,
        "source_name": url.split("/")[2],
        "published_iso": "2026-07-24T00:00:00+00:00",
    }


def test_commissioning_clusters_require_independent_coverage():
    rows = [
        _row(
            "OpenAI releases Atlas-2 coding model",
            "https://openai.com/atlas-2",
            "primary",
            "Atlas-2 is a coding agent model with a new evaluation record.",
        ),
        _row(
            "Atlas-2 system card and evaluation data",
            "https://github.com/openai/atlas-2-evals",
            "primary",
            "Evaluation data and system-card measurements for Atlas-2.",
        ),
        _row(
            "OpenAI's Atlas-2 changes coding-agent workflows",
            "https://example-news.com/atlas-2",
            "secondary",
            "Independent testing of the Atlas-2 coding agent release.",
        ),
        _row(
            "Atlas-2 brings longer context to software agents",
            "https://another-news.example/atlas-2-context",
            "secondary",
            "Analysis of Atlas-2 and its effect on agent workflows.",
        ),
        _row(
            "A Petri-net method for Rust API tests",
            "https://arxiv.org/abs/2607.00001",
            "primary",
            "A standalone research paper with no independent coverage.",
        ),
    ]

    clusters = build_commissioning_clusters(rows)

    assert clusters
    assert clusters[0]["primary_count"] >= 1
    assert clusters[0]["secondary_count"] >= 2
    assert clusters[0]["distinct_domains"] >= 3
    assert "Atlas-2" in clusters[0]["topic_anchor"]


def test_lone_primary_is_not_commissioned():
    rows = [
        _row(
            "A Petri-net method for Rust API tests",
            "https://arxiv.org/abs/2607.00001",
            "primary",
        )
    ]

    assert build_commissioning_clusters(rows) == []
