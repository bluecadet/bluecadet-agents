# Bluecadet Conventional Commits

How to update this: when a new git-convention decision gets made (Slack, a PR thread, wherever), edit this file on the spot and add a dated line to the Provenance section below — don't let a real decision go undocumented again.

## Commit message format

```
<type>(<ticket>): <subject>

[optional body]

[optional footer(s)]
```

Keep it terse:

- Subject line: 50 characters or less, hard cap at 72. Imperative mood ("add", not "added" or "adds").
- Body: only when there's a non-obvious *why* — a breaking change, a migration, a revert, a workaround for something not evident from the diff itself. If the subject line says everything worth knowing, skip the body.

### Types

| Type | Meaning |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Build tasks, package manager configs, etc. — no production code change |
| `perf` | Measurable performance improvement |
| `docs` | Documentation changes |
| `revert` | Roll back a previous commit |
| `style` | Formatting, missing semicolons, etc. — no code change |
| `refactor` | Refactoring production code |
| `ci` | CI/CD configuration or workflow changes |
| `test` | Adding or refactoring tests — no production code change |
| `wip` | Work in progress — code is potentially unstable. BC-added, non-standard. Use at end of day for unfinished work, not as a substitute for atomic commits. |

`oops` (admitting/fixing a mistake without rewriting history) was proposed once but never formally confirmed — don't use it as an official type unless it gets decided for real.

### Scope = ticket number

Unlike the vanilla Conventional Commits spec (which suggests area names like `parser`/`api`), Bluecadet uses the Jira/GitHub ticket number as the scope:

```
feat(NGA-123): add new config
fix(ACMW-556): correct Stripe capture rounding
```

If there's no ticket, omit the scope entirely (`feat: add new config`) rather than inventing one.

### Breaking changes

A footer `BREAKING CHANGE: <description>`, or a `!` appended after the type/scope (`feat(ML-42)!: ...`), marks a breaking change.

### Atomic commits

One logical change per commit. If a set of changes touches more than one unrelated concern, split it into separate commits rather than bundling — this makes history legible and reviewable, and is the whole point of drafting commits carefully instead of committing everything in one shot at the end of a session.

## Branch naming

```
<type>/<ticket-lowercase>-<short-description>
```

Short type prefix (matches the commit type), all lowercase, ticket number lowercased, brief hyphenated description, no unusual characters.

```
feat/ml-123-add-config
fix/acmw-556-stripe-rounding
```

## PR hygiene (secondary, for context)

- Keep PRs under roughly 10 files where practical — a reviewer should be able to get through one in 10-15 minutes. Known exceptions: Drupal config exports, CSS spread across many files, or a genuinely large feature communicated to the team in advance.
- PR description explains *why* and *how*, not just *what* — don't just restate the linked ticket.
- Link the issue(s) being addressed.

## Provenance

Reconciled 2026-09-16 from three real Bluecadet decisions, found via Slack/Drive search after the docs behind them got lost track of:

- **Types + scope taxonomy baseline**: `bc-base-drupal` README ("Bluecadet Base Drupal Site" Google Doc), "Commit Guidelines" section — types list and `wip` addition came from here. Its scope guidance ("don't use issue identifiers as scope") was superseded by the item below.
- **Scope = ticket number**: #dev-talk Slack thread, 2025-10-23 (Pete, Clay Tercek, Katie Han) — explicit agreement that the ticket number is the scope, e.g. `feat(NGA-123): Add new config`.
- **Branch prefix `<type>/<ticket>-<description>`**: #mars-landing--dev Slack thread, 2026-05-04 (Pete, Amit Asaravala) — settled on short, all-lowercase `feat/ml-123-description` over the doc's longer `feature/[ticket#]-[label]` form.
- **Atomic commits + PR hygiene**: #nga-dev-team Slack canvas "PRs & Code Review (Drupal)", 2025-01-07 — "individual commits should be small," PR file-count guidance, why/how-not-just-what description guidance.

Known drift: the `bc-base-drupal` README itself still has the older, unreconciled scope/branch text. Not updated as part of this — tracked as a separate follow-up.
