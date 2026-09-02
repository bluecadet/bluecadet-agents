# bluecadet-agents

Shared Claude Code plugins for the Bluecadet team, one plugin per discipline. Synced into Claude Teams so plugins can be enabled org-wide.

Decided in the 2026-08-27 Amit/Pete 1:1.

## Structure

One plugin per discipline under `plugins/`, plus a shared `bluecadet-core` plugin at the top that every discipline plugin depends on. Skills inside a plugin are invoked as `/<plugin-name>:<skill-name>`.

```
bluecadet-core          (defaultEnabled: true — everyone gets this)
├── dev-team            (depends on bluecadet-core, defaultEnabled: true)
│   ├── drupal-dev       (depends on dev-team, defaultEnabled: false)
│   └── wordpress-dev    (depends on dev-team, defaultEnabled: false)
└── pm                  (depends on bluecadet-core, defaultEnabled: true)
```

`bluecadet-core` holds skills that aren't discipline-specific — e.g. `team-meeting-debrief`, `bc-pdf-reading`. As PM/Design/Biz Dev plugins get built, they should depend on `bluecadet-core` directly too (not on `dev-team`).

## Rollout order

1. **Dev Team** — in progress, plus stack-specific sub-plugins that depend on it:
   - **Drupal Dev** — depends on `dev-team`
   - **WordPress Dev** — depends on `dev-team`
2. **PM** — in progress, ahead of its rollout turn (2026-09-02: started with quote-source-verification before Dev Team's own skills were built out)
3. Design
4. Biz Dev

Each plugin gets built out when its rollout turn comes — not stubbed out empty ahead of time.

## Contribution model

Open-submit, but Amit and Pete review and merge everything before it lands. A bad skill landing unreviewed could cause real problems if someone hits it unknowingly.

## Dev Team plugin — status

- [ ] Granola-to-Slack skill (referenced as "drafted ~2026-08-24" but no draft found — needs to actually be written)

## Bluecadet Core plugin — status

- [x] `team-meeting-debrief` — pulled in as-is from KrakenOS's `claude-skills/team-meeting-debrief/`, already written generically (2026-09-01)
- [x] `bc-pdf-reading` — Pete's Claude-online-drafted PDF triage/extraction skill (2026-09-02), renamed from `pdf-reading` to avoid colliding with any first-party PDF skill an environment might already have installed (e.g. claude.ai's built-in `pdf` skill); intended as a fallback for environments that don't already have one. Original frontmatter had a non-standard `when_to_use` field, folded into `description` on import.
- [x] `orchestrator` — generalized from Pete's KrakenOS-local `.claude/skills/orchestrator/SKILL.md` (2026-09-02), itself adapted from Clay Tercek's original. Resolves an open question from Pete's personal todo tracking (graduate the local skill to his own global CLAUDE.md, or into this shared repo) in favor of the shared repo. KrakenOS-specific references (its own skill roster, its own todo/friction-log paths, "Pete" by name) replaced with project-agnostic equivalents. Invokes as `/bluecadet-core:orchestrator` — does not collide with any project-local `/orchestrator` skill, since plugin skills are always namespaced by plugin name.
- [x] `plugin-advisor` (2026-09-02) — suggests a relevant external skill/plugin from a curated `references/registry.md` when a task has no matching bluecadet-agents skill; never installs anything itself. Distinct from the environment's own `find-skills` skill, which does a live but unvetted search across the whole open skills ecosystem. Seeded from reviewing github.com/JuliusBrussee/caveman (caveman-commit ported as a pattern candidate, the Cloud/proxy tier rejected — see the registry for reasoning). Devs own keeping the registry current via the normal PR review process.

## PM plugin — status

- [x] `quote-source-verification` — generalized from Kristina's Truman-specific Google Doc draft (2026-09-02). Truman's specific source set and coverage gaps live in `skills/quote-source-verification/references/known-figures.md` as the worked example; the skill itself is figure-agnostic. Points to `bc-pdf-reading` (bluecadet-core) for text-layer PDFs and OCR guidance.
