---
name: team-slack-sync
description: Sync a Bluecadet project's Slack channel(s) for decisions and action items that never made it into a meeting debrief — pulls new messages since the last sync, confirms real decisions with the user, logs them via the Sourcing & Decision Standards rule, and surfaces action items directly in chat.
---

# Team Slack Sync

Triggered by: "sync [project]'s Slack", "check [project]'s Slack channel for decisions", "pull Slack activity for [project]"

This skill runs inside a claude.ai Project, using the Slack connector and the Google Drive connector. It is `team-meeting-debrief`'s sister skill — same project/Drive conventions, same Sourcing & Decision Standards and Friction Logging rules, but the source is a project's Slack channel(s) instead of a meeting transcript. Real decisions get made async in Slack (budget tweaks, scope calls) that nobody was in a meeting to debrief — this skill is how those get captured instead of quietly living only in Slack's own history.

---

## Step 1: Identify the project and its Slack channel(s)

- If the project isn't obvious from context, ask which project this is for.
- Check `claude_index` first, same as `team-meeting-debrief`'s Step 2 — use the project's Drive folder ID and README ID directly rather than searching.
- Read the project's README Metadata section for its Slack channel(s):
  - Single channel: `Slack channel: #channel-name (id: C0XXXXXXX)`
  - Multiple channels: a `Slack channels:` list, one `#channel-name (id: C0XXXXXXX)` per line.
- **Cache each channel's Slack ID next to its name in README**, the same ID-caching convention `claude_index` already uses for Drive folders. If README only has a name and no ID, resolve it once via `slack_search_channels`, then offer to add the ID back to README — same confirm-before-write bar Step 2 of `team-meeting-debrief` uses for `claude_index` corrections.
- **If more than one channel is listed, ask which to sync** — don't silently run through all of them. If only one is listed, use it without asking.
- If README lists no Slack channel at all, stop and say so — same "this project hasn't been set up for this workflow yet" bar `team-meeting-debrief`'s Step 2 uses for a missing `80_agents` folder. Don't guess at a channel name.

**Check the canonical rules — always, not conditionally**, same as `team-meeting-debrief`'s Step 2. `Sourcing & Decision Standards` (governs Step 4) and `Friction Logging` (governs Step 6) live once in `Global_Agents/Rules/` and apply to every project; they're never copied into a project's own folder, so an empty or missing project `Rules/` folder doesn't mean skip them. Fetch them via `claude_index`'s standing `Global_Agents` link if not already loaded. Then check `claude_index`'s `Rules/` listing for a project-specific override doc (e.g. `Sourcing & Decision Standards — Project Additions`, most commonly this project's tag vocabulary) and follow it too, if one exists.

## Step 2: Resolve the sync window

Each tracked channel has its own cursor in `[project]/80_agents/Slack Sync` (create this doc if it doesn't exist yet — front matter only, one line per channel):

```
Slack Sync

Last updated: [YYYY-MM-DD] · Status: current

#channel-name: synced through [Slack ts], [YYYY-MM-DD HH:MM EST]
```

- **Channel already has a cursor:** pull messages from just after that timestamp through now.
- **First sync for this channel:** unlike a meeting, a channel has no natural start boundary. Don't default to the channel's entire history. Suggest a reasonable window (e.g. the last 30 days) and confirm with the user before pulling, or let them specify a different start date.

Use `slack_read_channel` directly against the known channel ID for the pull — this skill always knows its target channel in advance (from README), so there's no need for `slack_search`-style queries or their query-syntax gotchas.

**After a successful run, update this channel's cursor line to the timestamp of the last message processed, and bump the doc's own `Last updated` front matter** — treat both as part of the same write, not an optional afterthought (same discipline the Decisions Log's own maintenance already requires).

## Step 3: Scan for decisions and action items

**Hard-skip any message posted by a debrief bot** — identifiable by the `Sent using Claude` signature, or the posting app/bot user if identifiable directly. These are `team-meeting-debrief`'s own recap posts, already logged once; re-processing them risks logging the same decision a second time.

Read the remaining messages (and their threads) in the window. Apply judgment for what counts as a real decision or action item — the same bar `team-meeting-debrief`'s Step 3 already uses ("only real decisions... not every choice"). Most channel traffic is logistics and scheduling chatter ("is this meeting happening?", "time check") — skip it, don't force it into a category.

For each candidate decision or action item found, note the specific message(s) it came from (permalink, author, timestamp) — that message is the entry's source. There's no intermediate summary doc the way `team-meeting-debrief` has one.

**Confirm with the user before doing anything else.** Show the drafted decisions and action items — numbered, same format as `team-meeting-debrief`'s Step 3 confirmation — and get an explicit confirm-or-correct. Nothing gets logged until this is confirmed.

## Step 4: Log confirmed decisions

For each confirmed decision, apply the `Sourcing & Decision Standards` rule (found in Step 1) exactly as `team-meeting-debrief`'s Step 5 does — same entry format (stable ID, `OWNER` with its client-approved/internal-call/not-specified distinction, `STAKEHOLDERS` when named client people are involved, this project's tag if one applies), same confirmation-gate language, same insertion mechanics. `CONTEXT` cites the Slack message directly (permalink), not a summary doc.

**If this Slack thread revisits a decision already in the Decisions Log**, don't write a fresh unrelated entry — append the appropriate dated sub-line to the original per the rule (`SUPERSEDED BY`, `⚠️ NEEDS REVIEW`, or a dismissed-review line).

If `Global_Agents` isn't reachable at all, skip decision-logging entirely and say so, rather than inventing a format.

## Step 5: Surface action items

List confirmed action items directly in this conversation — there's no persistent action-item log to write to here. The user decides what to do with each one (add to their own tracking, ping someone, ignore).

## Step 6: Log friction (if any)

Same as `team-meeting-debrief`'s Step 8 — apply the `Friction Logging` rule (always applies, per Step 1), then say how many were logged (or that none were). Skip silently only if `Global_Agents` isn't reachable at all.

## Step 7: Check named externals against the People folder

Same as `team-meeting-debrief`'s Step 7 — client-side people (non-`@bluecadet.com`, or clearly external from context) named with real identifying context in a scanned message. There's no attendee list here, just message authors and named third parties, but the same rule applies: a bare name mentioned once with nothing else attached doesn't count. Same confirm-before-write bar as Step 4.

---

## Notes

- No Slack recap gets posted back to the source channel. The channel already receives `team-meeting-debrief`'s recaps, and posting a summary of Slack activity back into that same Slack channel would be circular — it's also the reason Step 3 has to hard-skip those bot posts in the first place.
- No standalone digest doc is saved. The Slack messages themselves are the durable record; only confirmed decisions get written anywhere durable (the Decisions Log), cited by their own permalink.
- Keep summaries and confirmations factual and concise — same bar `team-meeting-debrief` holds itself to.
