"""Build source-diverse story clusters for nightly commissioning."""

from __future__ import annotations

import math
import re
import urllib.parse
from collections import Counter
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.+-]{2,}")
STOPWORDS = frozenset(
    [
        "about",
        "after",
        "again",
        "against",
        "all",
        "also",
        "amid",
        "among",
        "and",
        "announces",
        "announcement",
        "are",
        "artificial",
        "as",
        "at",
        "before",
        "being",
        "between",
        "both",
        "but",
        "by",
        "can",
        "company",
        "companies",
        "could",
        "data",
        "from",
        "for",
        "has",
        "have",
        "how",
        "into",
        "intelligence",
        "its",
        "launch",
        "launches",
        "made",
        "make",
        "makes",
        "making",
        "model",
        "models",
        "more",
        "most",
        "new",
        "news",
        "not",
        "now",
        "of",
        "on",
        "one",
        "or",
        "our",
        "over",
        "paper",
        "platform",
        "platforms",
        "release",
        "releases",
        "research",
        "says",
        "software",
        "system",
        "systems",
        "than",
        "that",
        "the",
        "their",
        "them",
        "there",
        "these",
        "they",
        "this",
        "through",
        "to",
        "tool",
        "tools",
        "under",
        "up",
        "update",
        "updates",
        "use",
        "uses",
        "using",
        "via",
        "was",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
        "would",
    ]
)


def _domain(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower().removeprefix("www.")


def _terms(row: dict[str, Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    title = str(row.get("title") or "").lower()
    summary = str(row.get("summary") or "")[:600].lower()
    for token in TOKEN_RE.findall(title):
        if token not in STOPWORDS:
            counts[token] += 3
    for token in TOKEN_RE.findall(summary):
        if token not in STOPWORDS:
            counts[token] += 1
    return counts


def _weighted_vectors(rows: list[dict[str, Any]]) -> list[dict[str, float]]:
    term_counts = [_terms(row) for row in rows]
    document_frequency: Counter[str] = Counter()
    for counts in term_counts:
        document_frequency.update(counts.keys())
    total = max(1, len(rows))
    vectors: list[dict[str, float]] = []
    for counts in term_counts:
        vector = {
            term: count * (math.log((total + 1) / (document_frequency[term] + 1)) + 1)
            for term, count in counts.items()
        }
        vectors.append(vector)
    return vectors


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    shared = left.keys() & right.keys()
    if not shared:
        return 0.0
    numerator = sum(left[term] * right[term] for term in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def _match(seed: dict[str, float], candidate: dict[str, float], *, kind: str) -> float:
    similarity = _cosine(seed, candidate)
    shared = seed.keys() & candidate.keys()
    rare_anchor = any(
        len(term) >= 5 and ("-" in term or any(ch.isdigit() for ch in term))
        for term in shared
    )
    threshold = 0.13 if kind == "secondary" else 0.16
    if similarity >= threshold or (rare_anchor and similarity >= 0.07):
        return similarity
    return 0.0


def _overlap(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def build_commissioning_clusters(
    rows: list[dict[str, Any]], *, limit: int = 6
) -> list[dict[str, Any]]:
    """Return recent clusters with one primary and two independent secondaries.

    The commissioning model does not receive isolated feed items. Each option is
    anchored by a record that owns the claim and is accompanied by independent
    coverage from at least two domains. Targeted research may add more owner-
    authored records, but it never invents a second primary merely to satisfy a count.
    """
    if not rows:
        return []
    vectors = _weighted_vectors(rows)
    candidates: list[tuple[float, list[tuple[int, float]]]] = []

    for seed_index, seed_row in enumerate(rows):
        if seed_row.get("kind_hint") != "primary":
            continue
        matches: list[tuple[int, float]] = []
        for index, row in enumerate(rows):
            if index == seed_index:
                continue
            score = _match(
                vectors[seed_index],
                vectors[index],
                kind=str(row.get("kind_hint") or ""),
            )
            if score:
                matches.append((index, score))
        matches.sort(key=lambda item: item[1], reverse=True)

        chosen: list[tuple[int, float]] = [(seed_index, 1.0)]
        domain_counts: Counter[str] = Counter({_domain(str(seed_row["url"])): 1})
        for wanted_kind, cap in (("primary", 2), ("secondary", 4)):
            for index, score in matches:
                row = rows[index]
                if row.get("kind_hint") != wanted_kind:
                    continue
                domain = _domain(str(row["url"]))
                if not domain or domain_counts[domain] >= 1:
                    continue
                chosen.append((index, score))
                domain_counts[domain] += 1
                if (
                    sum(
                        rows[item[0]].get("kind_hint") == wanted_kind for item in chosen
                    )
                    >= cap
                ):
                    break

        primary_count = sum(
            rows[index].get("kind_hint") == "primary" for index, _ in chosen
        )
        secondary_count = sum(
            rows[index].get("kind_hint") == "secondary" for index, _ in chosen
        )
        if primary_count < 1 or secondary_count < 2:
            continue
        distinct_domains = len(
            {_domain(str(rows[index]["url"])) for index, _ in chosen}
        )
        average_match = sum(score for _, score in chosen[1:]) / max(1, len(chosen) - 1)
        cluster_score = (
            min(primary_count, 2) * 10
            + min(secondary_count, 4) * 7
            + distinct_domains * 2
            + average_match * 20
        )
        candidates.append((cluster_score, chosen))

    candidates.sort(key=lambda item: item[0], reverse=True)
    clusters: list[dict[str, Any]] = []
    signatures: list[set[str]] = []
    for score, chosen in candidates:
        urls = {str(rows[index]["url"]) for index, _ in chosen}
        if any(_overlap(urls, signature) >= 0.6 for signature in signatures):
            continue
        signatures.append(urls)
        sources = []
        for index, match_score in chosen:
            row = rows[index]
            sources.append(
                {
                    "title": str(row.get("title") or "")[:180],
                    "url": row["url"],
                    "summary": str(row.get("summary") or "")[:160],
                    "published": row.get("published_iso"),
                    "source_name": row.get("source_name"),
                    "kind_hint": row.get("kind_hint"),
                    "match_score": round(match_score, 3),
                }
            )
        clusters.append(
            {
                "cluster_id": f"cluster-{len(clusters) + 1}",
                "topic_anchor": sources[0]["title"],
                "primary_count": sum(
                    source["kind_hint"] == "primary" for source in sources
                ),
                "secondary_count": sum(
                    source["kind_hint"] == "secondary" for source in sources
                ),
                "distinct_domains": len(
                    {_domain(str(source["url"])) for source in sources}
                ),
                "cluster_score": round(score, 2),
                "sources": sources,
            }
        )
        if len(clusters) >= limit:
            break
    return clusters
