---
name: project-allocation
description: Show a project's full team planned-hours breakdown for a timeframe (defaults to this week), via bc-dashboard's project-scoped get_utilization, and optionally draft a Slack summary in the project channel for review before sending.
---

# Project Allocation

Triggered by: "/project-allocation [project] [timeframe]", "what's the team's allocation on [project] this week", "who's working on [project] and for how many hours".

This skill requires the **bc-dashboard** connector, same as the `allocation` skill in `bc-core` — if it's not authenticated, say so and stop.

## Step 0: Confirm the project filter is actually live

This skill depends on `get_utilization`'s `project` parameter, added in `bluecadet/int-signal-dashboard` PR #10. Before relying on it, check the tool's current input schema (e.g. via a fresh `ToolSearch` for `get_utilization`, or just note whether `project` appears as an accepted argument). If `project` isn't there yet, the PR hasn't merged/deployed — tell the person plainly that project-scoped allocation isn't live yet and stop. **Do not** call `get_utilization` without a working `project` filter and present the result as if it were project-scoped — an unfiltered call returns each person's *total* hours across every project, which would silently misrepresent the data as smaller/project-specific when it isn't.

## Step 1: Resolve the project

Ask for the project name if it wasn't given. Pass it as-is to `get_utilization`'s `project` param (substring match against Signal's project table) — don't try to guess a canonical name first.

## Step 2: Resolve the timeframe

Same default as `allocation`: this week (Monday–Sunday), `granularity: week`, unless a different range is given.

## Step 3: Call the tool

`get_utilization(project, granularity, start, end)`. This already returns only people with actual hours on the project in the window — no need to cross-reference `get_staff_projects` separately.

## Step 4: Present it

A table: person, discipline, planned hours in the window, plus a team total row. If the result is empty, say plainly that nobody has planned hours on that project name in that window — could be a naming mismatch (try a broader substring) or genuinely nothing scheduled, don't guess which.

## Step 5: Offer a Slack draft

Ask if they want this drafted to Slack, and which channel. Then:

1. Resolve each person's Slack ID via the **bc-people** roster (one read covers everyone) so the message can `@mention` them instead of just listing plain names. Anyone not in the roster yet: use their plain name and don't block on it — this isn't the moment to run a full `bc-people` lookup pass on people who aren't the point of the message.
2. Build the message — the table plus room for the PM's own commentary, ask if they want to add anything before it goes out.
3. Create it with `slack_send_message_draft` (channel + message). This lands as a real draft in the PM's own Slack "Drafts & Sent," not a sent message.
4. Hand back the `channel_link` from the result and stop there. **Do not call `slack_send_message`** — the PM reviews and sends it themselves, directly in Slack. This skill's job ends at a reviewable draft, not a sent message.

## Notes

- Same forecast-not-timesheet caveat as `allocation` — Workfront's current live assignment state, not logged actuals.
- If `bc-dashboard`'s deployed schema changes (e.g. `project` moves to a dedicated tool instead of a param), update Step 0/3 to match — this skill was written against PR #10's shape specifically.
