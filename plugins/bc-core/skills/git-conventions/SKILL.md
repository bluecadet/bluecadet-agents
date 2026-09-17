---
name: git-conventions
description: Consult this whenever a commit message, branch name, or PR title/description needs to be drafted for a Bluecadet repo — any skill in any plugin (git-workflow, a future dev-facing commit skill, or ad hoc work) should check references/conventional-commits.md before guessing at the format. Triggers on drafting a commit message, naming a branch, writing a PR title, or being asked "what's our commit convention" / "how do we name branches here."
---

# Git Conventions

Bluecadet's Conventional Commits format, scope convention, and branch naming pattern, in one place so every skill that touches git uses the same rules instead of each guessing independently.

## When this applies

Any time you're about to:

- Draft a commit message for a Bluecadet repo
- Name a new branch
- Write a PR title or description

Read `references/conventional-commits.md` first. Don't invent a format from general Conventional Commits knowledge — Bluecadet has specific, decided variations (ticket-as-scope, a particular branch prefix style) that differ from the vanilla spec in ways that matter.

## Notes

- Seeded 2026-09-16 after Pete asked where Bluecadet's actual Conventional Commits decisions live — they'd been made in Slack over the past year but the docs were lost track of. Reconciled from three real sources (see the reference file's provenance note) rather than invented fresh.
- The checked-in `bc-base-drupal` README ("Commit Guidelines" section) still has an older, unreconciled version of this spec (area-name scopes instead of ticket numbers, a longer branch-prefix form). This file intentionally encodes the more recent decision instead — flagged as a known drift, follow-up tracked separately, not a discrepancy to "fix" by matching the stale doc.
- This is a living document, same as `house-glossary` — if a new git-convention decision gets made (in Slack, in a PR discussion, wherever), update `references/conventional-commits.md` on the spot rather than letting it drift again.
