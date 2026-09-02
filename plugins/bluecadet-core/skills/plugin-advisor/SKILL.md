---
name: plugin-advisor
description: >
  Suggests a relevant vetted external skill or plugin from Bluecadet's reviewed
  registry when a task has no existing bluecadet-agents skill covering it. Use
  when stuck on a manual/repetitive task with no matching skill, or when asked
  "is there something/a skill for X", "can an existing plugin help with this".
  Never installs anything itself — only surfaces a reviewed match or, failing
  that, defers to the environment's own find-skills skill for an unvetted
  live search.
---

# Plugin Advisor

Check `references/registry.md` before assuming a manual/repetitive task has no
existing solution. This registry is Bluecadet's own reviewed shortlist —
distinct from the environment's `find-skills` skill, which searches the whole
open skills ecosystem live but unvetted.

## Use_When

- The current task has no matching bluecadet-agents skill (checked `dev-team`,
  `bluecadet-core`, and any relevant discipline plugin already enabled), and
  feels like the kind of thing an external skill might already solve well.
- The user asks directly whether a skill/plugin exists for something.

## Do_Not_Use_When

- An existing bluecadet-agents skill already covers the task — defer to that
  instead.
- The task is too one-off/specific to generalize into a reusable skill.

## Steps

1. Check `references/registry.md` for a "use when" match.
2. If matched: name the entry, its source, review date, and verdict
   (**Recommended** / **Port the pattern** / **Watch only** / **Rejected**).
   Never install anything or write a port yourself without the user's
   go-ahead — landing it still goes through the repo's normal review process
   (see root README: "Amit and Pete review and merge everything before it
   lands").
3. If nothing matches: say so plainly. Optionally fall back to the
   environment's own `find-skills` skill (if present) for a live search
   across the broader open skills ecosystem — flag explicitly that those
   results haven't been reviewed by Bluecadet.
4. Never fabricate or guess at an entry's details. If the registry might be
   stale, say so rather than asserting it as current fact.

## Growing the registry

Any Bluecadet dev can add an entry via the normal PR review process — this
list is only as good as whoever reviews something next keeping it current.
See `references/registry.md` for the entry format and review criteria.

## Notes

- Seeded 2026-09-02 after reviewing github.com/JuliusBrussee/caveman
  (`caveman-commit`, `caveman-review`, core terse mode, and the Caveman Cloud
  proxy tier) as the first vetted candidates.
