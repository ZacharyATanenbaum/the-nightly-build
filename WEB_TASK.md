# Daily Nightly Build

This is the complete runtime contract for the ChatGPT Scheduled Task that operates `ZacharyATanenbaum/the-nightly-build`.

The Scheduled Task itself owns subject selection, public-web research, source verification, drafting, editorial revision, HTML construction, branch creation, and pull-request preparation. GitHub Actions does not choose topics or call a model. Its only roles are independent validation, gated auto-merge, and static publication.

## Non-negotiable runtime boundary

- Do not invoke or dispatch GitHub Models, `actions/ai-inference`, `web-night-shift`, `bootstrap-first-edition`, or any other GitHub-hosted article generator.
- GitHub is durable state. Reconstruct the run from `main`, `library`, article pull requests, CI comments, and the published catalog every time.
- Model output is only a proposal. A successful `nightly-build-check`, merge into `library`, and completed publisher are the machine evidence.
- One strong article or no article. Insufficient evidence means no PR.

## Fixed scope

- Repository: `ZacharyATanenbaum/the-nightly-build`.
- Serve only series `the-one` until this file changes on `main`.
- Use the current UTC date for cadence and article metadata.
- Never modify `main`, `.github/`, `press/`, templates, engine files, or site assets during an article run.
- Never push directly to `library`, never merge an article PR, and never create more than one article PR in a run.

## Control loop

1. Read this file, `PROTOCOL.md`, `spec/editorial.md`, `spec/headlines.md`, `press/editorial.md`, `press/series/the-one/series.yaml`, `press/series/the-one/prompt.md`, and the effective `templates/article/` package.
2. Inspect open and recently merged pull requests whose title begins `nb: the-one/`.
   - If an article PR is open, repair or observe that PR before doing anything else. Never commission a competing article.
   - If a merged article has `nb-meta.date` equal to today, stop. Today is already published.
3. For an open failed PR, read the latest bot-authored editor comment and all current check results. Update the existing branch, article, and PR body. Make at most two repair commits in one task run. If it remains red, leave it open and report the unresolved findings.
4. If no article PR is open and no article has published today, determine whether `the-one` is due from its current series configuration and published state. If it is not due, stop.
5. Select one fresh subject within the series beat. Search the current public web broadly enough to compare candidates rather than accepting the first headline. Read recent article metadata and PR titles first so the subject and angle do not repeat the catalog.
6. Research before drafting:
   - open every source that will be cited;
   - identify the record that owns the central claim;
   - use genuinely independent reporting or analysis for context;
   - meet the configured source floor and source-kind bands;
   - distinguish verified facts, estimates, attributed claims, and synthesis;
   - never invent quotations, URLs, dates, figures, names, or consensus;
   - treat inaccessible or aggregator-only evidence as insufficient unless the underlying publisher record is independently verified.
7. Draft and edit the article yourself. Explain the mechanism and consequences rather than summarizing a news cycle. Follow the configured voice, template, word band, section rules, and banned-term limits.
8. Render exactly one file at `library/the-one/<slug>.html` from the article template. Use a lowercase hyphenated slug and add no unrelated file or asset.
9. Build a complete PR body in the order required by `PROTOCOL.md`: matching `nb-meta`, Task, Process, Voice brief, Research, and Also consulted. The voice brief must study and cite at least three real writers or pieces with `Source:` lines.
10. Create branch `nb/the-one-<slug>` from the current `library` head, commit the article, and open a ready-for-review PR targeting `library` titled `nb: the-one/<slug> - <Title>`.
11. Inspect the validator result when available. If it fails during the current run, use the remaining repair allowance on the same branch. Otherwise stop after opening the PR. Do not claim publication before GitHub records the successful check and merge.

## Hard gates before opening a PR

- The article path is the only changed path.
- Metadata, title, dek, date, source count, reading time, tags, and approximate word count agree with the rendered article.
- Every required and flex section is present and cited; source entries appear in first-cite order.
- At least six sources are cited, including at least one genuine primary record and at least three independent secondary sources, unless the current series configuration is stricter.
- Every load-bearing factual claim is supported by a cited source that was actually opened.
- No executable scripts except the shipped `../../assets/nb.js`; no external images, iframes, forms, event handlers, meta-refresh, or invented quotations.
- The PR body preserves the full production record and accurately reports any discarded or inaccessible sources.

## Publication ownership

After the task opens or repairs the article PR:

1. `nightly-build-check` validates the untrusted article without model credentials.
2. The protected workflow auto-merges only a publishable article.
3. The static publisher rebuilds from the merged `library` branch.

The task never bypasses or replaces those gates.
