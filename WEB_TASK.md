# ChatGPT Scheduled Task night shift

This file is the execution contract for a ChatGPT Scheduled Task that has access
to the public web and a connected GitHub app, but does not retain a repository
checkout or run shell commands. `PROTOCOL.md` remains the editorial authority;
this file adapts that protocol to a stateless, connector-only runtime.

## Execution boundary

- The ChatGPT Scheduled Task is both the scheduler and the authoring runtime. It
  performs subject selection, public-web research, source verification, article
  drafting, bounded revision, HTML assembly, pull-request preparation, and
  closure of the article pipeline.
- Do not invoke GitHub Models, `actions/ai-inference`, or any GitHub-hosted
  article-generation cron or workflow. GitHub Actions do not author or repair
  content.
- GitHub Actions are deterministic infrastructure only: independent proof,
  browser render validation, protected auto-merge, and GitHub Pages publishing.
- Git is durable memory. Reconstruct state from `main`, `library`, article PRs,
  bot comments, check runs, publisher runs, the Pages API, and the canonical
  GitHub Pages site every time.
- Never claim to have run `uv`, Python, `engine/check.py`, or any other shell
  command. GitHub Actions supply that machine evidence.
- Never push directly to `main` or `library`, never bypass a required check, and
  never modify engine, workflow, template, press, or site-asset files during an
  article run.
- Opening or updating a PR is not completion.

## Canonical publication endpoint

The authoritative public endpoint is the repository's GitHub Pages site, normally
`https://<owner>.github.io/<repo>/`. Resolve it from the Pages API or the
publisher's deployment output when possible.

Do not use RawGitHack, `raw.githubusercontent.com`, a `gh-pages` branch URL, an
Actions artifact URL, or a workflow summary link as the production endpoint.
Those may be useful diagnostics, but they do not prove that readers can reach the
GitHub Pages site.

## Completion gate

A normal task run may report success only after all of these facts are observed
for the same article:

1. The current PR head SHA has a successful required article check.
2. That validated head has merged into `library`.
3. The repository's sole configured GitHub Pages publisher has completed
   successfully after the merge.
4. The Pages API resolves the repository site as a workflow deployment.
5. The canonical homepage returns HTTP 200.
6. The exact canonical article URL returns HTTP 200 and contains matching series,
   slug, title, and date metadata.

A green model claim, a PR URL, a successful validator without a merge, a green
publisher without the expected article, or any public 404 is not completion.

## Run loop

1. Resolve the repository named by the Scheduled Task. Read this file,
   `AGENTS.md`, `PROTOCOL.md`, the house editorial and headline specifications,
   `press/`, the configured series, and each effective template needed tonight.
2. Inspect open and recently merged article PRs before commissioning work.
   - Enter the closure and repair loop for an existing open PR before creating
     another for the same series.
   - If today's article merged but publication is absent or failed, recover that
     publication before commissioning another article.
   - Treat the latest check runs, job logs, bot-authored editor findings, Pages
     state, and public HTTP responses as machine evidence.
3. Determine due work conservatively from the series configuration and the
   published `library` state. At most one article per due series may be proposed.
   When the stateless runtime cannot establish that an article is due, skip it.
4. For new work, read recent article titles and metadata to avoid repetition.
   Select a subject inside the series beat because the evidence changed, the
   mechanism matters, and the consequences justify a complete article.
5. Research before drafting. Open every cited source. Prefer the record that owns
   each load-bearing claim and use genuinely independent reporting or analysis
   for context. Meet the configured source floor and source-kind bands. A skipped
   article is preferable to unsupported synthesis.
6. Build exactly the article bundle permitted by `PROTOCOL.md`, normally one HTML
   file at `library/<series>/<slug>.html`. Follow the effective template,
   metadata, source-order, citation, active-content, word-band, and production
   record rules. The Scheduled Task owns all prose and reasoning; GitHub does not.
7. Create a branch from the current `library` head, commit only the article bundle,
   and open one ready-for-review PR targeting `library`. Use the required title
   and PR-body structure: matching `nb-meta`, Task, Process, Voice brief,
   Research, and Also consulted.
8. Record the PR number, current head SHA, article path, canonical Pages base URL,
   and current published state, then enter the closure and repair loop. Do not
   stop after opening the PR.

## Closure and repair loop

1. Poll the PR and its required check until the current head's run completes.
   Queued and in-progress runs are unfinished, not successful.
2. If article validation fails, read the latest editor comment and failed job
   logs. Repair only the observed blockers on the same branch, keep the PR body
   consistent with the article, and wait for the new head's check.
3. Make at most three article-repair commits for one edition. Every repair must
   map to machine evidence; do not rewrite unrelated sections or weaken a gate.
4. If a job is cancelled, times out, or fails because of a runner, network,
   checkout, cache, or GitHub API fault without an article blocker, rerun the
   failed job. Make at most two infrastructure reruns per workflow attempt.
5. After validation succeeds, wait for the validated head to merge. If only the
   auto-merge job failed transiently, rerun that job. Never manually merge a head
   whose successful validation cannot be tied to the same SHA.
6. After merge, wait for the sole configured GitHub Pages publisher. Inspect and
   rerun a transient publisher failure within the same two-rerun bound.
7. Verify publication independently. Require the Pages API to resolve the site,
   then fetch the canonical homepage and exact article URL. Both must return HTTP
   200, and the article must contain matching series, slug, title, and date
   metadata. A successful workflow with a 404 page is a failure.
8. If Pages is not configured, report `BLOCKED` with the repository Pages settings
   URL. A connector-only ChatGPT task cannot assume it can create the initial
   Pages site through the GitHub app or `GITHUB_TOKEN`.
9. If the bounded repair or rerun allowance is exhausted, preserve the existing
   branch and PR, report `BLOCKED` with the exact run URL and unresolved evidence,
   and let the next Scheduled Task run resume that state before new work. This is
   a failed run, never a successful completion.

## Hard gates before opening a PR

- The branch is based on the current `library` head and changes only the permitted
  article bundle.
- Metadata, title, dek, source count, word count, date, and rendered content agree.
- Every required and flex section is present and cited as the template requires.
- Sources appear in first-cite order and satisfy the configured primary and
  independent-secondary composition.
- Every factual claim is supported by a source actually opened during this run;
  quotations, numbers, dates, names, and URLs are never invented.
- The HTML contains no executable content beyond the shipped engine runtime and
  no external images, iframes, forms, event handlers, or unsafe URLs.
- The PR body preserves a complete, honest production record and states when the
  runtime used a single context rather than isolated roles.

## Setup-agent obligations

A setup agent using this route must:

1. Bootstrap the fork with `scripts/setup.sh` from an authenticated checkout. That
   script creates `library`, installs the protected checks and publisher, enables
   GitHub Pages through the repository API when permitted, and prints the manual
   fallback when it is not.
2. If Pages could not be enabled automatically, have a repository administrator
   set **Settings → Pages → Build and deployment → Source → GitHub Actions**.
   `actions/configure-pages` with `enablement: true` is not sufficient when
   GitHub rejects one-time site creation from the workflow token.
3. Confirm the Pages API returns HTTP 200 with `build_type: workflow`, run the
   official publisher, and require both the canonical homepage and a known
   article URL to return HTTP 200. Do not declare setup complete from workflow
   success alone.
4. Confirm the fork is connected to ChatGPT's GitHub app with permission to read
   repository and Actions state, create branches and commits, open or update PRs,
   and rerun failed workflow jobs.
5. Prove that exact write surface with a disposable branch and draft PR, then
   close the PR and remove or reset the disposable branch.
6. Create one daily ChatGPT Scheduled Task for the whole paper using the prompt
   below. Do not create a second GitHub generation schedule.
7. Remove any previously installed GitHub Models generation workflow or cron.
   Keep deterministic CI, protected auto-merge, durable status reporting, and
   exactly one GitHub Pages publisher.
8. Test the route with a disposable or historical article on an isolated base:
   require validator success, a real browser-render pass, auto-merge, publisher
   success, Pages API success, and canonical HTTP 200 responses before declaring
   setup complete.
9. Run the real task once when the product exposes that control and verify the
   same completion gate rather than merely asserting success.

## Scheduled Task prompt

Replace `<repo>` with the fork's `owner/name` value and use this as the complete
Scheduled Task instruction:

> Run the Daily Nightly Build for `<repo>`. Perform all subject selection,
> public-web research, source verification, article drafting, bounded revision,
> pull-request preparation, and failed-article repair yourself using the
> connected GitHub app and the public web. Read `WEB_TASK.md` from `main` and
> follow it exactly. Do not dispatch, invoke, or rely on GitHub Models,
> `actions/ai-inference`, or any GitHub-hosted article-generation workflow.
> GitHub Actions are only deterministic validation, protected auto-merge, and
> GitHub Pages publishing. Do not finish after opening a pull request: wait for
> the current head's check, repair observed blockers on the same PR, verify merge
> and publisher success, and report success only after the canonical GitHub Pages
> homepage and exact article URL both return HTTP 200 with matching metadata. If
> no article is due or the evidence is insufficient, publish nothing.
