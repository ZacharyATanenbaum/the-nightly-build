# Web night shift

This is the connector-only runtime contract for a ChatGPT Web Scheduled Task. It adapts `PROTOCOL.md` to a stateless environment that can read and write GitHub but cannot retain a checkout or run repository code. The repository proof and GitHub Actions are the publishing authority.

## Philosophy

- Git is the memory and the protocol. Reconstruct state from `main`, `library`, pull requests, and CI on every run.
- Model output is a proposal. A successful `nightly-build-check` run and a merged PR are machine evidence.
- Never weaken a gate because the web runtime cannot execute it. CI exists to supply the missing execution boundary.
- One strong article or no article. A skipped night is preferable to unsupported research.

## Fixed scope

- Repository: `ZacharyATanenbaum/the-nightly-build`.
- Serve only series `the-one` until this file is changed on `main`.
- Use the current UTC date for duty and metadata.
- Never modify `main`, `library`, `.github/`, `press/`, templates, engine files, or site assets.
- Never push directly to `library`, never merge, and never create more than one article PR in a run.

## Control loop

1. Read this file, `PROTOCOL.md`, `spec/editorial.md`, `spec/headlines.md`, `press/editorial.md`, `press/series/the-one/series.yaml`, `press/series/the-one/prompt.md`, and the effective `templates/article/` package.
2. Inspect open and recently merged PRs whose title begins `nb: the-one/`.
   - An open PR exists: repair that PR first; do not commission another article.
   - A merged PR has `nb-meta.date` equal to today: stop; today is already published.
3. For an open failed PR, read the latest `## The editor` bot comment and update the existing branch, article, and PR body. Make at most two repair commits in one run. If it remains red, leave it open and report the unresolved findings.
4. Otherwise choose one fresh subject within the series beat. Read recent article PR titles and metadata first so the subject and angle do not repeat the catalog.
5. Research before drafting. Meet the configured source floor and source-kind bands. Open every cited source, prefer the record that owns each claim, and use independent reporting for context. Treat “no data found” as unproven until primary-source, parser/access, and alternate-query diligence is recorded.
6. Render exactly one file at `library/the-one/<slug>.html` from the article template. Use a lowercase hyphenated slug. Do not add any other file or asset.
7. Create branch `nb/the-one-<slug>` from the current `library` head, commit the article, and open a ready-for-review PR targeting `library` titled `nb: the-one/<slug> - <Title>`.
8. Build the PR body in the order required by `PROTOCOL.md`: matching `nb-meta`, Task, Process, Voice brief, Research, and Also consulted. The voice brief must study and cite at least three real writers or pieces with `Source:` lines.
9. Stop after opening or repairing the PR. Do not claim publication. The next run determines success from CI and merge state.

## Hard gates before opening a PR

- The article path is the only changed path.
- Metadata, rendered dek, source count, and approximate word count agree with the article.
- Every flex section has at least one citation; source entries appear in first-cite order.
- At least six sources are cited, including at least two declared primary and two declared secondary sources.
- No executable scripts except the shipped `../../assets/nb.js`; no external images, iframes, event handlers, or invented quotations.
- The PR body contains the complete production record and accurately distinguishes verified facts, estimates, and synthesis.

## Scheduler prompt

The Web Scheduled Task prompt should contain only this:

> Run the web night shift for `ZacharyATanenbaum/the-nightly-build`. Read `WEB_TASK.md` from `main` and follow it exactly. GitHub and the public web are your working state; the repository proof and CI are the publication authority.
