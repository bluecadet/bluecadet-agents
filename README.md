# bluecadet-agents

Shared Claude Code plugins for the Bluecadet team, one plugin per discipline. Synced into Claude Teams so plugins can be enabled org-wide.

Decided in the 2026-08-27 Amit/Pete 1:1.

## Structure

One plugin per discipline under `plugins/`, plus a shared `bc-core` plugin at the top that every discipline plugin depends on. Skills inside a plugin are invoked as `/<plugin-name>:<skill-name>`.

Plugin names use a `bc-` prefix (not the full "bluecadet-") to keep skill invocations short while still avoiding collisions with other marketplaces' generically-named plugins — see the naming-standardization pass, 2026-09-17.

```
bc-core                 (defaultEnabled: true — everyone gets this)
├── bc-dev              (depends on bc-core, defaultEnabled: true)
│   ├── bc-dev-drup      (depends on bc-dev, defaultEnabled: false)
│   └── bc-dev-wp        (depends on bc-dev, defaultEnabled: false)
├── bc-pm               (depends on bc-core, defaultEnabled: true)
└── bc-content          (depends on bc-core, defaultEnabled: true)
```

`bc-core` holds skills that aren't discipline-specific — e.g. `team-meeting-debrief`, `bc-pdf-reading`. As Design/Biz Dev plugins get built, they should depend on `bc-core` directly too (not on `bc-dev`).

## Rollout order

1. **Dev Team** — in progress, plus stack-specific sub-plugins that depend on it:
   - **Drupal Dev** — depends on `bc-dev`
   - **WordPress Dev** — depends on `bc-dev`
2. **PM** — in progress, ahead of its rollout turn (2026-09-02: started, but its only skill was misplaced and later moved to Content Team, see below)
3. **Content Team** — in progress, ahead of its rollout turn. Not one of the four disciplines from the original 2026-08-27 Amit/Pete 1:1 (Biz Dev, Dev Team, Design Team, PM) — added 2026-09-02 once `quote-verification` (originally `quote-source-verification`) turned out to belong here, not in PM. Where it slots into the rollout order long-term hasn't been decided.
4. Design
5. Biz Dev

Each plugin gets built out when its rollout turn comes — not stubbed out empty ahead of time.

**Exception, 2026-09-17:** `bc-dev`, `bc-dev-drup`, `bc-dev-wp`, and `bc-pm` each carry a `hello-world` placeholder skill even though none of them have a real skill yet. `claude plugin validate` fails the *entire* marketplace sync if any one plugin's `skills/` directory doesn't exist — an empty plugin isn't just inert, it's load-bearing broken. Remove each placeholder the same PR that adds that plugin's first real skill.

## Contribution model

Open-submit, but Amit and Pete review and merge everything before it lands. A bad skill landing unreviewed could cause real problems if someone hits it unknowingly.

## Dev Team (`bc-dev`) plugin — status

- [ ] Granola-to-Slack skill (referenced as "drafted ~2026-08-24" but no draft found — needs to actually be written)

## Bluecadet Core (`bc-core`) plugin — status

- [x] `team-meeting-debrief` — pulled in as-is from KrakenOS's `claude-skills/team-meeting-debrief/`, already written generically (2026-09-01). Zoom support + per-person attribution added 2026-09-02. Also now keeps client-side attendees' `80_agents/People/` docs current (create or update, always asks first, Bluecadet-internal people excluded, they're covered by local `people/` instead), added 2026-09-02.
- [x] `bc-pdf-reading` — Pete's Claude-online-drafted PDF triage/extraction skill (2026-09-02), renamed from `pdf-reading` to avoid colliding with any first-party PDF skill an environment might already have installed (e.g. claude.ai's built-in `pdf` skill); intended as a fallback for environments that don't already have one. Original frontmatter had a non-standard `when_to_use` field, folded into `description` on import.
- [x] `orchestrator` — generalized from Pete's KrakenOS-local `.claude/skills/orchestrator/SKILL.md` (2026-09-02), itself adapted from Clay Tercek's original. Resolves an open question from Pete's personal todo tracking (graduate the local skill to his own global CLAUDE.md, or into this shared repo) in favor of the shared repo. KrakenOS-specific references (its own skill roster, its own todo/friction-log paths, "Pete" by name) replaced with project-agnostic equivalents. Invokes as `/bc-core:orchestrator` — does not collide with any project-local `/orchestrator` skill, since plugin skills are always namespaced by plugin name.
- [x] `plugin-advisor` (2026-09-02) — suggests a relevant external skill/plugin from a curated `references/registry.md` when a task has no matching bluecadet-agents skill; never installs anything itself. Distinct from the environment's own `find-skills` skill, which does a live but unvetted search across the whole open skills ecosystem. Seeded from reviewing github.com/JuliusBrussee/caveman (caveman-commit ported as a pattern candidate, the Cloud/proxy tier rejected — see the registry for reasoning). Devs own keeping the registry current via the normal PR review process.
- [x] `house-glossary` (2026-09-02) — from Clay's wishlist item, above. Reference skill: consult `references/glossary.md` for Bluecadet-specific shorthand instead of guessing, add newly-confirmed terms as they come up. Seeded with only what could be confirmed from available project context; real recurring terms with no confirmed definition (e.g. "BLR") are listed under a "Needs definition" section rather than guessed at. Also flags an unconfirmed naming question worth Pete's attention: Clay referred to a "narrative team" that might not want a brand-voice skill, unclear if that's the same team as this repo's `bc-content` plugin under a different name.
- [/] `team-session-notes` (added 2026-09-02, pulled 2026-09-17, back in rework as of the same day) — bridges a local Claude Code session to a project's `80_agents` Drive folder, the gap `team-meeting-debrief` doesn't cover since that one only runs from inside a claude.ai Project. Part of the larger `projects/team-knowledge-base` initiative in KrakenOS (architecture, front-matter conventions, and the confirmed-working Markdown→DOCX→Drive pipeline all decided there, not invented here). Currently restored to its pre-rework state on a draft PR while the rework itself is scoped — not yet changed.

## PM (`bc-pm`) plugin — status

No skills yet. `quote-verification` (originally built and named `quote-source-verification`) was originally built here 2026-09-02, then moved to Content Team the same day once Pete caught that it was misplaced.

## Content Team (`bc-content`) plugin — status

- [x] `quote-verification` (originally `quote-source-verification`, shortened 2026-09-17) — generalized from Kristina's Truman-specific Google Doc draft (2026-09-02), moved here from PM the same day. Truman's specific source set and coverage gaps live in `skills/quote-verification/references/known-figures.md` as the worked example; the skill itself is figure-agnostic. Points to `bc-pdf-reading` (bc-core) for text-layer PDFs and OCR guidance.

## Wishlist / backlog

Not built yet, not assigned to a plugin. From Clay Tercek's reply in Slack DM, 2026-09-02, to Pete asking what should be included:

- **Netlify Deploy MCP as a bundled `.mcp.json`** — fold the existing free-floating Netlify Deploy connector into a plugin instead, plus skills built around it (bc-dev, probably)
- **Client context skill** — pulled from Drive (plugin TBD)
- **Brand voice / writing style skill** — bc-content candidate; Clay flagged himself that the narrative team might not want this
- **Accessibility review against SOW commitments** — bc-dev candidate
- **PR review guidelines and commit conventions** — bc-dev candidate

Also open: Clay asked whether the intent is "a bucket of skills" or something that connects out to other services (Jira, Docs, etc.) — worth answering back to him directly, that's a real design-direction question, not a backlog item.
