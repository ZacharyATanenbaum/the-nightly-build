# Daily Nightly Build

This is the complete runtime contract for the ChatGPT Scheduled Task that operates `ZacharyATanenbaum/the-nightly-build`.

The Scheduled Task owns subject selection, public-web research, source verification, drafting, editorial revision, HTML construction, branch creation, pull-request preparation, and closure of the article pipeline. GitHub Actions independently validates, auto-merges, and publishes.

## Non-negotiable runtime boundary

- Do not invoke or dispatch GitHub Models, `actions/ai-inference`, `web-night-shift`, `bootstrap-first-edition`, or any other GitHub-hosted article generator.
- GitHub is durable state. Reconstruct every run from `main`, `library`, article pull requests, current check runs, bot comments, `automation-status`, `gh-pages`, and the published catalog.
- Model output is only a proposal. A successful validator, merge into `library`, successful `web-publish`, and the exact article on `gh-pages` are the machine evidence.
- One strong article or no article. Insufficient evidence means no PR.
- Opening a PR is not completion.

## Fixed scope

- Repository: `ZacharyATanenbaum/the-nightly-build`.
- Serve only series `the-one` until this file changes on `main`.
- Use the current UTC date for cadence and article metadata.
- Never push directly to `library` or `main` during an article run.
- Never modify `.github/`, `press/`, templates, engine files, or site assets from an article branch.
- Never merge an article PR unless the current head SHA has a successful `nightly-build-check`.
- Never create more than one article PR in a run or commission a competing article while any `nb: the-one/` PR is open.

## Completion gate

A normal task run has exactly one successful exit. All of the following must be true for the current article:

1. `nightly-build-check` completed successfully for the PR's current head SHA.
2. That validated head was merged into `library`.
3. The subsequent `web-publish` run completed successfully.
4. `gh-pages` advanced and contains `library/the-one/<slug>.html` with matching slug and date metadata.

Do not report success, publication, or a finished run before all four facts are observed.

## Control loop

1. Read this file, `PROTOCOL.md`, `spec/editorial.md`, `spec/headlines.md`, `press/editorial.md`, `press/series/the-one/series.yaml`, `press/series/the-one/prompt.md`, and the effective `templates/article/` package.
2. Inspect open and recently merged pull requests whose title begins `nb: the-one/`.
   - If an article PR is open, enter the closure loop for that PR before doing anything else.
   - If a merged article has `nb-meta.date` equal to today and the completion gate is proven, stop. Today is already published.
   - If today's article merged but publication is unproven or failed, resume publication recovery rather than commissioning another article.
3. If no article PR is open and no completed article exists for today, determine whether `the-one` is due from its current series configuration and published state. If it is not due, stop.
4. Select one fresh subject within the series beat. Search the current public web broadly enough to compare candidates rather than accepting the first headline. Read recent article metadata and PR titles first so the subject and angle do not repeat the catalog.
5. Research before drafting:
   - open every source that will be cited;
   - identify the record that owns the central claim;
   - use genuinely independent reporting or analysis for context;
   - meet the configured source floor and source-kind bands;
   - distinguish verified facts, estimates, attributed claims, and synthesis;
   - never invent quotations, URLs, dates, figures, names, or consensus;
   - treat inaccessible or aggregator-only evidence as insufficient unless the underlying publisher record is independently verified.
6. Draft and edit the article yourself. Explain the mechanism and consequences rather than summarizing a news cycle. Follow the configured voice, template, word band, section rules, and banned-term limits.
7. Render exactly one file at `library/the-one/<slug>.html` from the article template. Use a lowercase hyphenated slug and add no unrelated file or asset.
8. Build a complete PR body in the order required by `PROTOCOL.md`: matching `nb-meta`, Task, Process, Voice brief, Research, and Also consulted. The voice brief must study and cite at least three real writers or pieces with `Source:` lines.
9. Create branch `nb/the-one-<slug>` from the current `library` head, commit the article, and open a ready-for-review PR targeting `library` titled `nb: the-one/<slug> - <Title>`.
10. Record the PR number, current head SHA, article path, and the pre-publication `gh-pages` head, then enter the closure loop. Do not stop after opening the PR.

## Closure and repair loop

1. Poll the PR and its GitHub Actions runs until the current `nightly-build-check` attempt completes. Treat queued and in-progress checks as unfinished, not as success or failure.
2. If validation fails, read the latest bot-authored `## The editor` comment and the failed job logs. Repair only the cited blockers on the same article branch, keep the PR body consistent, push the repair, and wait for the new head's check.
3. Make at most three article repair commits for one UTC edition. Each repair must map to an observed blocker; do not rewrite unrelated sections or weaken a gate.
4. If a job is cancelled, timed out, or fails from a runner, network, checkout, cache, or GitHub API error without an article blocker, rerun the failed job. Make at most two infrastructure reruns per workflow attempt.
5. After validation succeeds, wait for the PR to merge. If only the automerge job failed transiently, rerun that job. Never manually merge a head whose successful validation cannot be tied to the same SHA.
6. After merge, wait for `web-publish`. If it fails transiently, inspect its failed job log and rerun the failed job within the same two-rerun bound.
7. Verify publication independently: the `gh-pages` head must differ from the recorded pre-publication head and the exact article path must exist there with matching metadata. A green publisher without the article is a failure.
8. If the bounded repair or rerun allowance is exhausted, leave the existing PR and branch intact, report `BLOCKED` with the exact run URL and unresolved machine evidence, and let the next scheduled run resume that same state first. This is a failed run, never a successful completion.

## Hard gates before opening a PR

- The article path is the only changed path.
- Metadata, title, dek, date, source count, reading time, tags, and approximate word count agree with the rendered article.
- Every required and flex section is present and cited; source entries appear in first-cite order.
- At least six sources are cited, including at least one genuine primary record and at least three independent secondary sources, unless the current series configuration is stricter.
- Every load-bearing factual claim is supported by a cited source that was actually opened.
- No executable scripts except the shipped `../../assets/nb.js`; no external images, iframes, forms, event handlers, meta-refresh, or invented quotations.
- The PR body preserves the full production record and accurately reports any discarded or inaccessible sources.

## Publication ownership

1. `nightly-build-check` validates the untrusted article without model credentials.
2. Its protected automerge job merges only the validated head into `library`.
3. `web-publish` is the sole publisher and rebuilds the immutable `gh-pages` branch.
4. The Scheduled Task observes and repairs this pipeline; it never bypasses or replaces a gate.

## Canonical scheduler prompt

> Run the Daily Nightly Build for `ZacharyATanenbaum/the-nightly-build`. Read `WEB_TASK.md` from `main` and follow it exactly. GitHub and the public web are the working state. Do not finish after opening a pull request: wait for validation, repair observed failures on the same PR, verify merge and `web-publish`, and report success only after the exact article exists on `gh-pages`.
