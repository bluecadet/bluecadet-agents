# External Skills & Plugins Registry

Vetted external Claude Code skills/plugins the team has reviewed. Nothing here
is auto-installed for anyone — this is a "worth knowing about" shortlist, kept
current by whoever reviews something next, through the repo's normal PR
review process.

## How to add an entry

1. Sanity-check the source before trusting it: confirm install/star counts
   are real (check commit history and contributor activity, not just the
   badge — inflated numbers exist), weigh source reputation, and flag
   anything that requires routing traffic through a third-party hosted
   service as a bigger trust question, not a casual **Recommended**.
2. Add a row below with the verdict you'd actually tell a teammate to act on.
3. Date the review — this list goes stale, and a dated entry is honest about
   that instead of implying it's evergreen.

## Verdict definitions

- **Recommended** — install as-is, safe and useful.
- **Port the pattern** — don't install the dependency directly; write
  Bluecadet's own version of the idea (matches how `orchestrator` and
  `team-meeting-debrief` were generalized from their originals rather than
  imported verbatim).
- **Watch only** — interesting, not yet reviewed enough to recommend either
  way.
- **Rejected** — reviewed and passed on; reason noted.

## Registry

| Skill/Plugin | Source | Reviewed | Verdict | Use when |
|---|---|---|---|---|
| caveman-commit | github.com/JuliusBrussee/caveman | 2026-09-02 | Port the pattern | Need terse, exact Conventional Commits messages — subject ≤50 chars (hard cap 72), body only for non-obvious *why*/breaking changes/migrations/reverts |
| caveman-review | github.com/JuliusBrussee/caveman | 2026-09-02 | Watch only | One-line-per-finding code review format (location/problem/fix) — reviewed alongside caveman-commit, not yet ported anywhere |
| caveman (core terse-response mode) + Caveman Cloud proxy tier | github.com/JuliusBrussee/caveman | 2026-09-02 | Rejected | Core mode is a personal communication-style choice, not a team default. The Cloud tier routes LLM traffic through a hosted third-party gateway (BSL-1.1 licensed) to measure/optimize spend — bigger vendor-trust and data-governance call than a plugin add; worth a separate conversation if team-wide LLM cost visibility becomes a real need, not something to bundle in here. |

## Not yet reviewed

- Broader knowledge-work-plugins survey (incident-response/ADR-format/
  deploy-checklist/tech-debt-scoring templates for engineering; cross-tool
  digest for enterprise-search; runbook/status-report/vendor-review
  templates for operations; find-discussions/channel-digest/Slack
  search+messaging; `/brainstorm` + ADR template for product management) —
  candidates identified but not yet vetted against this registry's criteria.
  Source: KrakenOS `context/todos-notes/k-297.md`.
