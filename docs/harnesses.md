# Harnesses

Most night-shift runtimes need a repository checkout, web access, and permission
to open pull requests. [Scheduling](scheduling.md) defines that contract. The
ChatGPT Scheduled Task route is the connector-only exception: ChatGPT reads and
writes GitHub through the connected app while GitHub Actions supply executable
validation, protected merge, and publishing.

Provider features and prices move quickly. The links below are the source of
truth. A documented entrypoint means the integration is possible; it does not
mean this project has stress-tested that harness end to end.

## Current paths

| Agent                                                                                             | Laptop-off schedule                            | Unattended entrypoint              | Billing                                                             |
| ------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------- |
| [ChatGPT](https://help.openai.com/en/articles/10291617-tasks-in-chatgpt)                          | Scheduled Tasks                                | Hosted task + connected GitHub app | ChatGPT plan usage; no GitHub Models or model API key in this route |
| [Claude Code](https://code.claude.com/docs/en/routines)                                           | Routines                                       | `anthropics/claude-code-action`    | Routines use plan allowance; the Actions path uses API billing      |
| [Jules](https://jules.google/docs/scheduled-tasks/)                                               | Scheduled Tasks                                | Hosted task                        | Daily task quota for the plan                                       |
| [Codex](https://learn.chatgpt.com/docs/automations)                                               | Cloud scheduled tasks                          | `openai/codex-action@v1`           | Cloud tasks use plan allowance; the Action uses API billing         |
| [Cursor](https://docs.cursor.com/en/cli/headless)                                                 | Cloud Agents and Automations, plan-dependent   | `cursor-agent -p --force`          | Included usage, then on-demand usage where enabled                  |
| [OpenCode](https://dev.opencode.ai/docs/github/)                                                  | GitHub Action on cron                          | `opencode run`                     | The model provider you connect                                      |
| [Devin](https://docs.devin.ai/product-guides/scheduled-sessions)                                  | Automations                                    | API or CLI                         | Devin plan usage                                                    |
| [GitHub Copilot](https://docs.github.com/en/copilot/how-tos/github-copilot-app/using-automations) | Automations                                    | Hosted coding agent                | Included premium requests, then usage-based billing if enabled      |
| [Antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity)          | Local schedules; laptop-off is not established | CLI                                | Plan-dependent                                                      |
| [Pi](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)               | No hosted scheduler                            | `pi -p`                            | The model provider you connect                                      |

## Hosted schedulers

Use a hosted scheduler when it can browse the web, create branches and pull
requests in the fork, inspect Actions state, and rerun failed jobs. Run one task
for the whole paper.

- **ChatGPT:** connect the fork through the GitHub app, add `WEB_TASK.md`, and
  create one daily Scheduled Task with the exact prompt in
  [Scheduling](scheduling.md#chatgpt-scheduled-tasks). The ChatGPT task performs
  all topic selection, research, verification, writing, revision, PR
  preparation, failed-PR repair, and pipeline closure. GitHub Actions only
  validate, auto-merge, report status, and publish. The task must wait for the
  current head's check, merge, publisher, and exact published article before it
  reports success. Do not install a GitHub Models generation workflow, a second
  GitHub cron, or a duplicate publisher.
- **Claude Code:** create a Routine and enable full, or suitably scoped,
  network access. It runs in Anthropic's cloud and consumes your plan usage.
- **Jules:** install its GitHub app, create a Scheduled Task, and select the
  fork. Runs count against the plan's daily task quota.
- **Codex:** choose a cloud environment for the scheduled task. Local tasks
  need the computer; cloud tasks continue without it.
- **Cursor, Devin, and Copilot:** use their hosted automation surface when
  your plan includes it. Confirm repository permissions and usage limits in
  the provider before scheduling.

## GitHub Actions

The universal workflow in [Scheduling](scheduling.md) works with an agent that
has a non-interactive command or Action. Typical invoke steps are:

- Codex: `openai/codex-action@v1` with `OPENAI_API_KEY`.
- Claude Code: `anthropics/claude-code-action` with `ANTHROPIC_API_KEY`.
- Cursor: `cursor-agent -p --force "<prompt>"` with `CURSOR_API_KEY`.
- OpenCode: `opencode run "<prompt>"` with the chosen model credentials.
- Pi: `pi -p "<prompt>"` with the chosen model credentials.

This universal Actions path is separate from the ChatGPT connector-only route.
In the ChatGPT route, no GitHub workflow invokes a model or repairs prose. Keep
one repository article check, protected auto-merge, durable reporting, and one
static publisher, but do not use `actions/ai-inference`, GitHub Models, or a
GitHub generation schedule.

The browser probe is part of the deterministic gate. It should serve the built
site over loopback, prove that Chrome reached the exact article, check stable DOM
and computed-style invariants, and fail closed if the browser, navigation, page
structure, or stylesheet evidence is unavailable.

Use each provider's current documentation for installation and Action inputs.
Give the runtime web access, keep credentials in repository secrets, and say
plainly whether the run consumes a subscription allowance or a metered API.

## Role coordination

The protocol does not assume that every harness exposes the same subagent API.
The scheduled correspondent detects three useful levels at runtime:

1. **Peer:** isolated, named children can address one another. The
   correspondent still launches every role and owns phase transitions; peers
   use direct messages only for narrow blocking questions.
2. **Parent relay:** isolated children exist, but their messages return to the
   correspondent. It relays paths and requests without copying artifact
   contents into its context.
3. **Single context:** no isolated child is available. The same role sequence
   runs, but the PR records the loss of isolation explicitly.

The ordinary ChatGPT Scheduled Task route should assume single-context
production unless the active ChatGPT runtime exposes isolated workers. It must
record that honestly in the production record rather than pretending that
separate roles ran.

Nested spawning and provider-specific agent teams are never required. Each
article has one worktree and five direct role launches when the harness supports
them: writing coach and researcher in parallel, then writer, editor, and
publisher as their inputs become ready. Files under `.nb-work/` are
authoritative, so a checkout-based harness can resume a role or launch a fresh
instance without restarting the article.

Model names are equally harness-specific. `press/production.yaml` therefore
uses portable tiers (`efficient`, `capable`, `premium`, or `inherit`) unless a
user pins an exact provider ID. A managed Scheduled Task may record
`harness-managed` when the product does not expose the selected model; see
[Production cost and role models](production.md).
