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
├── pm                  (depends on bluecadet-core, defaultEnabled: true)
├── content-team        (depends on bluecadet-core, defaultEnabled: true)
└── design              (depends on bluecadet-core, defaultEnabled: true)
```

`bluecadet-core` holds skills that aren't discipline-specific — e.g. `team-meeting-debrief`, `bc-pdf-reading`. As Design/Biz Dev plugins get built, they should depend on `bluecadet-core` directly too (not on `dev-team`).

## Rollout order

1. **Dev Team** — in progress, plus stack-specific sub-plugins that depend on it:
   - **Drupal Dev** — depends on `dev-team`
   - **WordPress Dev** — depends on `dev-team`
2. **PM** — in progress, ahead of its rollout turn (2026-09-02: started, but its only skill was misplaced and later moved to Content Team, see below)
3. **Content Team** — in progress, ahead of its rollout turn. Not one of the four disciplines from the original 2026-08-27 Amit/Pete 1:1 (Biz Dev, Dev Team, Design Team, PM) — added 2026-09-02 once `quote-source-verification` turned out to belong here, not in PM. Where it slots into the rollout order long-term hasn't been decided.
4. **Design** — in progress, ahead of its rollout turn (2026-09-16: started once `prototype-change-manifest` had a real skill to land, same pattern as Content Team)
5. Biz Dev

Each plugin gets built out when its rollout turn comes — not stubbed out empty ahead of time.

## Contribution model

Open-submit, but Amit and Pete review and merge everything before it lands. A bad skill landing unreviewed could cause real problems if someone hits it unknowingly.

## Dev Team plugin — status

- [ ] Granola-to-Slack skill (referenced as "drafted ~2026-08-24" but no draft found — needs to actually be written)

## Bluecadet Core plugin — status

- [x] `team-meeting-debrief` — pulled in as-is from KrakenOS's `claude-skills/team-meeting-debrief/`, already written generically (2026-09-01). Zoom support + per-person attribution added 2026-09-02. Also now keeps client-side attendees' `80_agents/People/` docs current (create or update, always asks first, Bluecadet-internal people excluded, they're covered by local `people/` instead), added 2026-09-02.
- [x] `bc-pdf-reading` — Pete's Claude-online-drafted PDF triage/extraction skill (2026-09-02), renamed from `pdf-reading` to avoid colliding with any first-party PDF skill an environment might already have installed (e.g. claude.ai's built-in `pdf` skill); intended as a fallback for environments that don't already have one. Original frontmatter had a non-standard `when_to_use` field, folded into `description` on import.
- [x] `orchestrator` — generalized from Pete's KrakenOS-local `.claude/skills/orchestrator/SKILL.md` (2026-09-02), itself adapted from Clay Tercek's original. Resolves an open question from Pete's personal todo tracking (graduate the local skill to his own global CLAUDE.md, or into this shared repo) in favor of the shared repo. KrakenOS-specific references (its own skill roster, its own todo/friction-log paths, "Pete" by name) replaced with project-agnostic equivalents. Invokes as `/bluecadet-core:orchestrator` — does not collide with any project-local `/orchestrator` skill, since plugin skills are always namespaced by plugin name.
- [x] `plugin-advisor` (2026-09-02) — suggests a relevant external skill/plugin from a curated `references/registry.md` when a task has no matching bluecadet-agents skill; never installs anything itself. Distinct from the environment's own `find-skills` skill, which does a live but unvetted search across the whole open skills ecosystem. Seeded from reviewing github.com/JuliusBrussee/caveman (caveman-commit ported as a pattern candidate, the Cloud/proxy tier rejected — see the registry for reasoning). Devs own keeping the registry current via the normal PR review process.
- [x] `house-glossary` (2026-09-02) — from Clay's wishlist item, above. Reference skill: consult `references/glossary.md` for Bluecadet-specific shorthand instead of guessing, add newly-confirmed terms as they come up. Seeded with only what could be confirmed from available project context; real recurring terms with no confirmed definition (e.g. "BLR") are listed under a "Needs definition" section rather than guessed at. Also flags an unconfirmed naming question worth Pete's attention: Clay referred to a "narrative team" that might not want a brand-voice skill, unclear if that's the same team as this repo's `content-team` plugin under a different name.
- [x] `team-session-notes` (2026-09-02) — bridges a local Claude Code session to a project's `80_agents` Drive folder, the gap `team-meeting-debrief` doesn't cover since that one only runs from inside a claude.ai Project. Part of the larger `projects/team-knowledge-base` initiative in KrakenOS (architecture, front-matter conventions, and the confirmed-working Markdown→DOCX→Drive pipeline all decided there, not invented here). Claude proactively flags candidates and asks before writing; decisions route to the existing Decisions Log, client-contact info routes to `80_agents/People/` (same logic as `team-meeting-debrief`'s People step, added the same day), everything else gets a new `80_agents/Session Notes/` subfolder. Needs `pandoc` and a configured Google Workspace MCP connection to actually run, unlike anything else in this plugin so far.

## PM plugin — status

No skills yet. `quote-source-verification` was originally built here 2026-09-02, then moved to Content Team the same day once Pete caught that it was misplaced.

## Content Team plugin — status

- [x] `quote-source-verification` — generalized from Kristina's Truman-specific Google Doc draft (2026-09-02), moved here from PM the same day. Truman's specific source set and coverage gaps live in `skills/quote-source-verification/references/known-figures.md` as the worked example; the skill itself is figure-agnostic. Points to `bc-pdf-reading` (bluecadet-core) for text-layer PDFs and OCR guidance.

## Design plugin — status

- [x] `prototype-change-manifest` (2026-09-16) — design's first skill, brought in as-is from Clay Tercek's Slack proposal (#dev-talk, 2026-09-14: [thread](https://bluecadet.slack.com/archives/C03N0USCX/p1789394879056959)) for formalizing the designer+agent code handoff. Writes a `CHANGES.md` change manifest (template at `assets/CHANGES.template.md`) alongside a designer's AI-built prototype, spec'd entirely in design language so a developer can implement it without reverse-engineering the prototype's markup. Per that thread, this and the prototype itself are meant as *supplemental* handoff material, not a replacement for Figma-as-source-of-truth or the ticket itself — Amy Frear's follow-up ask (link Figma references in the manifest) is already covered by the template's `Intent source` field and `Assets` section, no changes needed for that. Not yet run end-to-end against a real prototype.

## Wishlist / backlog

Not built yet, not assigned to a plugin. From Clay Tercek's reply in Slack DM, 2026-09-02, to Pete asking what should be included:

- **Netlify Deploy MCP as a bundled `.mcp.json`** — fold the existing free-floating Netlify Deploy connector into a plugin instead, plus skills built around it (dev-team, probably)
- **Client context skill** — pulled from Drive (plugin TBD)
- **Brand voice / writing style skill** — content-team candidate; Clay flagged himself that the narrative team might not want this
- **Accessibility review against SOW commitments** — dev-team candidate
- **PR review guidelines and commit conventions** — dev-team candidate

Also open: Clay asked whether the intent is "a bucket of skills" or something that connects out to other services (Jira, Docs, etc.) — worth answering back to him directly, that's a real design-direction question, not a backlog item.
