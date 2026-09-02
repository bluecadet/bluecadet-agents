---
name: house-glossary
description: Consult this whenever a Bluecadet-specific term, acronym, internal tool name, project codename, or workflow shorthand comes up and its meaning isn't already clear from context — e.g. someone mentions "the BLR," "Basecadet," "80_agents," a Jira project prefix, or any other house term. Check references/glossary.md before asking the user what something means or guessing at its expansion.
---

# House Glossary

Bluecadet, like any agency with enough history, has accumulated shorthand: internal project codenames that don't match their public-facing name, acronyms for recurring meeting types, folder/file conventions repeated across projects, and tool names that only make sense with context. None of this is written down in one place today — this skill and its reference file are that place.

## When a term comes up

1. Check `references/glossary.md` first.
2. If it's there, use the definition and move on, no need to ask the user to confirm something already documented.
3. If it's not there, and the term seems like real recurring Bluecadet shorthand rather than a one-off, ask the user what it means. Don't guess at an expansion or definition, a wrong guess presented confidently is worse than asking.
4. Once confirmed, add it to `references/glossary.md` in the same format as existing entries, so the next person (or the next session) doesn't have to ask again.

## What belongs in the glossary vs. what doesn't

**Belongs here:** org-wide shorthand any Bluecadet dev might run into, regardless of which client project they're on: internal codenames for internal deliverables (e.g. an internal template project with a different name than its public one), recurring internal meeting-type acronyms, Drive/repo folder conventions used across multiple projects, internal tool names.

**Doesn't belong here:** a single client project's own Jira ticket prefix, codenames, or internal jargon that only makes sense within that one project, that's project-specific context, not house-wide. (Individual devs' own project trackers are the right place for that.)

## Notes

- Seeded 2026-09-02 from Clay Tercek's Slack suggestion and a light pass over available project context. Several real, recurring terms (e.g. "BLR," used across at least two unrelated projects) have no confirmed expansion anywhere accessible, marked as "needs definition" in the glossary rather than guessed at, don't remove those entries, fill them in once someone who knows confirms.
- This is a living document. Nobody owns keeping it current except whoever notices a gap, add on the spot rather than filing it away for later.
