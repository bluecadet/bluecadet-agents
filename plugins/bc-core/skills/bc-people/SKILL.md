---
name: bc-people
description: Consult this whenever you need a Bluecadet colleague's Slack ID, Jira account ID, GitHub handle, or Workfront/Signal display name. Checks the shared BC People roster in the Global_Agents Drive folder before doing a live lookup, and writes the result back so nobody on the team repeats it. Not for client/vendor contacts — those live in each project's own 80_agents/People/ folder.
---

# BC People

Triggered by needing a colleague's Slack ID, Jira account ID, GitHub handle, or Workfront/Signal display name — assigning a Jira ticket, drafting a Slack message, requesting a PR review, resolving a name for `get_utilization`, etc. Not triggered by questions about clients or vendors — that's each project's own `80_agents/People/` folder, a different thing with a different template.

This skill requires the Google Workspace connector (Drive + Sheets) already used across Bluecadet's Claude tooling. If it's not available, say so and stop — don't guess at an ID instead.

## The roster

**BC People — Staff Identity Roster**, in the Global_Agents Drive folder.

- Spreadsheet ID: `1o3ZXzSuPb4gPU6QW-j4ZxMoWSPIfaOzSqJFuj37qyWw`
- Link: https://docs.google.com/spreadsheets/d/1o3ZXzSuPb4gPU6QW-j4ZxMoWSPIfaOzSqJFuj37qyWw/edit
- `Roster` tab columns: Name | Slack ID | Jira Account ID | GitHub Handle | Workfront / Signal Name | Email | Notes | Last Updated
- `About` tab explains scope — read it once if this is your first time touching the sheet.

Same editing convention as the rest of Global_Agents: Claude-maintained, not hand-edited. Read it freely; if it needs a correction, make the edit yourself as part of this skill rather than telling the person to go fix it.

## Step 1: Check the roster first

Read the `Roster` tab and look for the person by name — case-insensitive, tolerant of a nickname or partial name the way you'd recognize it in conversation. If the field you actually need is already populated, use it. Done — no live lookup.

## Step 2: Live lookup on a miss

Resolve whichever field is missing the normal way:

- **Slack ID** — search Slack for the person (e.g. `slack_search_users`).
- **Jira account ID** — `lookupJiraAccountId` / `search_jira_users`.
- **GitHub handle** — for the person running the skill, `gh api user --jq '.login'` reads their own authenticated handle directly, no guessing. For someone else, there's no reliable search — ask rather than guessing at a username from their name.
- **Workfront/Signal display name** — there's no lookup tool for this one (Workfront/Signal has no email-keyed identity endpoint). Ask the person directly if it's not already clear from context.

If a live lookup comes back ambiguous (more than one plausible match) or empty, say so and ask rather than guessing and writing a wrong ID into a shared sheet — a bad row here is worse than no row, since the next lookup will trust it without re-checking.

## Step 3: Write it back, same turn

- **New person**: append a row with whatever field(s) you actually resolved. Leave the rest blank rather than guessing just to fill the row — a blank is an honest "unknown," a guess is a landmine for whoever reads it next.
- **Existing person, new field**: update just that cell, and bump Last Updated to today.
- Do this immediately after a successful lookup, not as a follow-up — deferred writes are how this cache stops being worth checking.

## What doesn't belong here

Client/vendor contacts, relationship notes, meeting history — that's each project's own `80_agents/People/` folder. This roster is internal Bluecadet staff identity lookups only, nothing narrative.
