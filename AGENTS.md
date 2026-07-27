# The Nightly Build

This repository is The Nightly Build: scheduled AI agents research topics and
publish cited HTML articles to a GitHub Pages library, gated by CI.

- If you were invoked by a **ChatGPT Scheduled Task or another connector-only
  hosted schedule without a checkout or shell**: read `WEB_TASK.md` first. It
  adapts `PROTOCOL.md` to that runtime. The task performs research, writing,
  article repair, and completion checks; GitHub Actions only validate,
  auto-merge, report status, and publish.
- If you were invoked by a **schedule with a checkout and shell to produce an
  article**: load `skills/correspondent/SKILL.md`. If you cannot, follow
  `PROTOCOL.md`; it is self-sufficient.
- If a **human is asking for setup, series configuration, or curation help**:
  load `skills/librarian/SKILL.md`.
- Never push to the `library` branch directly. Never edit files under `library/`
  in place. All content lands via article pull requests and the protected
  repository check.
- A connector-only runtime does not claim it ran `engine/check.py`; CI owns the
  executable proof and browser render probe.
- Opening a PR is not completion. The connector route reports success only after
  the current head passes, merges, the sole publisher succeeds, and the exact
  article appears at the published endpoint. Exhausted bounded retries preserve
  the PR and report `BLOCKED` so the next run resumes it before new work.
