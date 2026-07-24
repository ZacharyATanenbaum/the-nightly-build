"""Durable production artifacts for an article PR."""

from __future__ import annotations

from typing import Any

from nb_web.common import WORK


def build_artifacts(
    draft: dict[str, Any],
    selection: dict[str, Any],
    cited_sources: list[dict[str, Any]],
    all_sources: list[dict[str, Any]],
    meta: dict[str, Any],
) -> None:
    artifact_dir = WORK / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    task = f"""# Commission: The One / {meta["slug"]}

## Subject and angle
{selection.get("topic", meta["title"])}

{selection.get("angle", "")}

## Duty
The deterministic duty oracle reported `the-one` due for {meta["date"]}. This run serves that series exactly once.

## Source policy
At least six cited sources, including at least two primary sources and two independent secondary sources. No quotations unless the exact words appear in the research pack.

## Output
`library/the-one/{meta["slug"]}.html`, article template, 1,200–2,200 words.

## The one thing this piece must do
{draft.get("thesis") or selection.get("why_now") or "Explain the mechanism and consequence without outrunning the evidence."}
"""
    process = f"""# Automated editorial record

Production: single-context, no role isolation. The GitHub Models harness used a bounded two-pass control loop: one structured draft, then at most one revision if deterministic rendering or the repository proof failed.

The renderer, not the model, owned article geometry, source ordering, metadata counts, and the permitted write path. The model could propose prose and citations only from the fetched research pack. No executable model output was run.

Final article metadata: {meta["words"]} words, {meta["sources"]} cited sources, {meta["reading_minutes"]} minutes.
"""
    voice = f"""# Voice brief: {meta["title"]}

Write for a technically fluent reader who wants the mechanism before the reaction. Specific nouns carry the prose; claims are calibrated as reported fact, estimate, or synthesis. Use one controlled long sentence only when it holds a causal chain, then land the implication plainly. Do not praise sources, narrate the writing process, or announce what the reader will learn.

## Julia Evans, “How DNS works”
Source: https://jvns.ca/blog/2022/05/12/how-dns-works/

Study the way Evans decomposes a system into concrete messages and actors without flattening the technical detail. Borrow the mechanism-first sequencing, not her conversational persona.

## Bret Victor, “Learnable Programming”
Source: https://worrydream.com/LearnableProgramming/

Study how Victor turns an abstract argument into observable operations and then states the design consequence. Use examples as evidence, not decoration.

## Vannevar Bush, “As We May Think”
Source: https://www.theatlantic.com/magazine/archive/1945/07/as-we-may-think/303881/

Study the progression from present constraint to enabling mechanism to institutional consequence. Keep the confidence proportional to what the record supports.

Article-specific emphasis: {selection.get("angle", "")}
"""

    source_notes = {
        str(row.get("source_id") or row.get("id") or "").upper(): str(
            row.get("note") or ""
        )
        for row in draft.get("source_notes", [])
        if isinstance(row, dict)
    }
    research_lines = [f"# Research log: {meta['title']}", "", "## Cited sources", ""]
    cited_urls = {row["url"] for row in cited_sources}
    for row in cited_sources:
        default_note = (
            "Owns the underlying claim."
            if row["kind_hint"] == "primary"
            else "Independent reporting or analysis used for context."
        )
        note = source_notes.get(row["id"].upper()) or default_note
        excerpt = " ".join(row["text"].split())[:700].replace("````", "```")
        research_lines.extend(
            [
                f"### {row['id']} — {row['title']}",
                f"- Kind: {row['kind_hint']}",
                f"- URL: {row['url']}",
                f"- Why used: {note}",
                f"- Record checked: {excerpt}",
                "",
            ]
        )
    research_lines.extend(["## Discarded", ""])
    discarded = [row for row in all_sources if row["url"] not in cited_urls]
    if discarded:
        for row in discarded[:12]:
            research_lines.append(
                f"- {row['title']} — {row['url']} — relevant starting material, but redundant or weaker than the cited set."
            )
    else:
        research_lines.append("None.")

    (artifact_dir / "task.md").write_text(task.replace("````", "```"), encoding="utf-8")
    (artifact_dir / "requested-changes.md").write_text(
        process.replace("````", "```"), encoding="utf-8"
    )
    (artifact_dir / "voice.md").write_text(
        voice.replace("````", "```"), encoding="utf-8"
    )
    (artifact_dir / "research.md").write_text(
        "\n".join(research_lines) + "\n", encoding="utf-8"
    )
