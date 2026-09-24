---
name: allocation
description: Look up your own or a colleague's planned Workfront hours for any timeframe (defaults to this week), via the bc-dashboard MCP connector's get_utilization tool. Resolves your own identity through the bc-people roster so you're not asked "what's your name" every session.
---

# Allocation

Triggered by: "/allocation", "what's my allocation this week", "what am I planned for [timeframe]", "what's [person]'s allocation", "how many hours am I planned for".

This skill requires the **bc-dashboard** connector (Bluecadet's Signal dashboard, `signal.bluecadet.com/mcp`) authenticated for this session. If its tools aren't loaded, tell the person it needs authorizing (claude.ai connector settings, or `/mcp` in an interactive session) and stop — don't fall back to guessing or to any other data source.

`get_utilization` is role-gated by Signal's own Netlify Identity roles (`admin`/`pm` today). If the tool call fails or comes back empty for a real person, that's most likely an access problem, not a data problem — say so plainly rather than presenting an empty result as "no planned hours."

---

## Step 1: Resolve who this is for

- If a person's name was given, use it as-is — pass it straight to `get_utilization`'s `person` param, no need to resolve an exact match yourself (the tool does substring matching).
- Otherwise, this is the caller asking about themselves. Resolve their Workfront/Signal display name via the **bc-people** skill: check the roster first; if it's not there, ask them once ("what's your name in Workfront/Signal — usually just your full name") and write it back through bc-people so this doesn't get asked again next session.

## Step 2: Resolve the timeframe

Default to **this week** if nothing else is given — Monday through Sunday of the current calendar week, `granularity: week`. For "this month" or a named month, use `granularity: month`. For an explicit date range, pass `start`/`end` directly and pick whichever granularity reads more naturally for the range's length.

## Step 3: Call the tool

`get_utilization(person, granularity, start, end)`. Don't set `includeNonBillable` unless asked.

## Step 4: Present it

Show avl (available), planned, and actual (billable/internal/nonbill) hours per bucket in the window, plus a one-line takeaway. If planned is noticeably over or under avl for the current/nearest week, call that out — that's usually the thing someone actually wants to know, not just the raw numbers.

Always include this caveat once, briefly: planned hours are Workfront's *current* live assignment state — if something was reassigned today, that shows up as it stands now, not as it looked at any earlier point.

## Notes

- This is a forecast/planning view (what Workfront's scheduling data says), not a timesheet — don't present it as logged/actual time worked.
- Depends on `bluecadet/int-signal-dashboard`'s `get_utilization` tool; see that repo's `docs/mcp.md` for the full tool contract if something here seems out of date.
