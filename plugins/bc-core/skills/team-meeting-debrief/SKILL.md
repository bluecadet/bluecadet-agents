---
name: team-meeting-debrief
description: Debrief a Granola or Zoom meeting for a Bluecadet project — pulls the transcript, summarizes it, saves the summary into the project's shared Drive folder, optionally logs a decision, keeps client-side attendees' People docs current, and drafts a Slack post for the user to review before sending.
---

# Team Meeting Debrief

Triggered by: "debrief my meeting", "debrief [meeting name]", "summarize my meeting with [X]"

This skill runs inside a claude.ai Project, using the Granola connector, the Zoom for Claude connector, the Google Drive connector, and (at the final step) the Slack connector. It is meant to work across any Bluecadet project that has adopted the `80_agents` folder convention — it is not specific to one project.

---

## Step 1: Identify the meeting

Granola and Zoom cover different, overlapping ground — some meetings only exist in one. Check both rather than assuming Granola is the only source.

- If the user explicitly asks for Zoom (names Zoom directly, asks for "the Zoom recording," "the Zoom transcript," etc.), search Zoom directly for that meeting — don't detour through Granola first just because it's the usual default. The Granola-first order below is a default search strategy, not a rule that overrides what the user actually asked for.
- Otherwise, if the user named a specific meeting, search Granola for it by name/date first — it's the primary source (Granola notes are pre-summarized and cheaper to process). If nothing turns up there, search Zoom (`mcp__claude_ai_Zoom_for_Claude__search` or `search_meetings`) by the same name/date before concluding the meeting can't be found.
- If no meeting was named at all, ask which meeting, or offer a short list of recent unprocessed meetings to choose from — pulled from whichever source(s) are relevant.
- When doing a backfill/gap sweep across a date range (not a single named meeting): search Zoom by keyword/date range for meetings that never made it into Granola at all — this is how gaps get found, not by assuming Granola is complete.

**Pulling the content, per source:**

- **Granola:** pull the full notes/transcript via the Granola tools as before.
- **Zoom:** call `get_meeting_assets` for the chosen meeting. It can return `meeting_summary`, `my_notes`, `recording`, and `meeting_transcript` — any of these may be `null` if unavailable.
  - If `meeting_summary` exists, use it as the primary source — it's Zoom's own AI summary and is fast to work from.
  - If there's no summary but `meeting_transcript` exists, fall back to the raw transcript and synthesize the Step 3 summary manually from it. Large transcripts (multi-thousand-line) commonly exceed tool/read token limits — when that happens, extract just the transcript's text fields (not the full JSON with timestamps/speaker metadata) to a plain-text file in the scratchpad directory, then read it in ~1000-line chunks rather than trying to pull the whole thing in one call.
  - If neither a summary nor a transcript exists for a Zoom meeting (e.g. no one recorded, or Zoom never generated one), treat it the same as "no transcript" below — note it has nothing to debrief and move on, don't guess at content.
- If neither Granola nor Zoom has usable content for the meeting, say so and stop — don't guess at content.

**Provenance:** when a debrief is sourced from Zoom rather than Granola, add a line to the Step 3 metadata block noting that — e.g. `Source: Zoom transcript (no Granola note exists for this meeting)` or `Source: Zoom meeting summary`. Granola-sourced debriefs don't need this line (it's the default, expected path); flag it only when the pipeline differs, so anyone reading the doc later understands why formatting or extraction quality might differ from the usual Granola-based debriefs.

## Step 2: Identify the project and its Drive folder

- If the project isn't obvious from the meeting title, ask which project this belongs to.
- **Check `claude_index` first, if it's loaded as Project context and lists folder IDs next to folder names** — use the documented ID directly rather than searching Drive. Only fall back to a live search (by name) if `claude_index` doesn't have the ID, doesn't exist, or the documented ID turns out to be wrong (a write fails against it). This is the canonical reference, not a session-scoped cache — no need to re-verify it "just in case" on every run.
- If no usable ID came from `claude_index`, search Google Drive for that project's folder by name.

**If that live search resolves an ID `claude_index` didn't have, or corrects one that was wrong, offer to update `claude_index` with it** — show the user the specific line you'd add/correct (matching the `claude_index — Template`'s `name (id: ...)` format, in the `80_agents — Claude/Agent Working Files` section or wherever the folder in question belongs) and get a yes before writing. Same confirmation bar as the Slack draft in Step 6 — this is shared team content, not a silent side effect of debriefing a meeting. Skip the offer if the project has no `claude_index` yet; don't create one as part of this step.

- Look for an `80_agents` subfolder inside it.
  - **If `80_agents` doesn't exist:** stop and tell the user this project hasn't been set up for this workflow yet (no defined place to save the summary). Don't invent a folder structure or guess where to put it.
  - **If it exists but there's no `Meeting Notes` subfolder inside it:** same — stop and say so, rather than creating one unasked.

## Step 3: Generate the summary

**Scope the summary to the identified project only.** A single meeting often covers other projects, general team business, or tangential conversation that has nothing to do with the project this debrief is for (identified in Step 2). Only summarize, and only pull Action Items and Decisions from, the portion of the meeting actually about that project — leave it out of the written doc entirely, don't summarize it briefly "for context." This debrief is a project-specific record, not a transcript of the whole meeting.

**Do mention what got excluded, but only in the chat, never in the doc itself.** When showing the drafted summary for confirmation (below), add a short note naming what was left out and why (e.g. "Also excluded: 15 minutes on Q3 resourcing policy, unrelated to this project"). This keeps the written record clean per the rule above while still giving the user visibility into what the exclusion decision actually was, rather than a silent judgment call they can't see or correct.

**Project name:** use the project's README title line verbatim (see Step 2) rather than inventing a name or abbreviation — different docs in the same project folder are often inconsistent about this (e.g. a project referred to as both "NWWII" and "NWWIIM" across different docs), and picking one authoritative source keeps every debrief consistent instead of each one choosing independently.

**Debriefed by:** if the user's full name isn't obviously available (e.g. the meeting's own attendee list only has a first name), ask the user for it once — don't guess or cross-reference an unrelated document's attendee list to infer it. Remember the answer for the rest of this session so it isn't asked again on a later debrief in the same conversation.

Content structure (plain text, no markdown syntax like `#`/`*`/`-`/`[]` in the text itself — write it out, formatting gets applied separately in Step 4):

```
[Meeting Title]
Date: [date]
Attendees: [list]
Project: [project name]
Debriefed by: [the user's full name]

Summary
[2-4 sentence narrative of what the meeting covered and what was resolved]

Action Items
[Name]: [action item]
[Name]: [action item]

Decisions Made
[Only include this section if a real decision was made]
[decision] — reasoning: [why]
```

If a section has nothing to put in it, omit that section entirely.

**Confirm Action Items and Decisions Made with the user before writing anything to Drive.** These two sections create durable claims — that someone owes a specific task, or that something was officially decided — in a way the Summary narrative doesn't. A misheard name or a misread nuance from the transcript becoming a silent written record is a real failure mode, not a hypothetical one. Show the drafted Action Items and Decisions Made sections, along with the excluded-content note from above, and get an explicit confirm-or-correct from the user before proceeding to Step 4. The Summary narrative alone doesn't need this same confirm-or-correct gate.

**When showing this confirmation, number each Action Item and each Decision** (1, 2, 3...) so the user can reference one directly ("remove #2", "fix the name on #1") instead of describing it in prose. This numbering is for the chat confirmation only — the actual Google Doc still uses real bulleted lists per Step 4, not numbers.

Multiple team members can each debrief the same meeting from their own perspective — this produces one doc per person per meeting, not one shared/merged doc. `Debriefed by` is what distinguishes them; don't try to merge or dedupe against another person's existing debrief of the same meeting.

## Step 4: Save to Drive

Create a new Doc inside `[project]/80_agents/Meeting Notes`, named `YYYY-MM-DD-kebab-case-meeting-title--lastname` (double dash before the debriefer's last name — keeps multiple people's debriefs of the same meeting from colliding on filename, and visually separates the name tag from the title).

If two meetings share the same date and title (e.g. two same-day syncs both titled "Review NWWIIM Dev Estimates"), insert a 24-hour HHMM time right after the date to disambiguate: `YYYY-MM-DD-HHMM-kebab-case-meeting-title--lastname`. Only add the time when there's an actual collision — don't add it by default.

At the very top of the doc, above the Meeting Title line, add a one-line banner: `AI Generated - DO NOT EDIT`, bold and italic, normal text size (not a heading — it's a flag, not a section, so it shouldn't take up much vertical space). Leave one blank line between the banner and the Meeting Title line so it doesn't visually run into the front matter.

**Apply real formatting, don't leave it as flat text.** Preference order for which Docs-writing tool to use, since more than one may be available depending on the environment:

1. **`mcp-drive`'s Docs tools** (`create_doc`, `batch_update_doc`, `update_paragraph_style`, `insert_doc_elements`) — use these first if the `mcp-drive` connector is enabled in this Project. It gives real Docs-API-level formatting from inside a claude.ai Project, closing the gap the plain native connector has always had here.
2. **`google-workspace-bc`'s tools of the same names** — the path this skill has always had when run outside a claude.ai Project (i.e. in Claude Code).
3. **The plain native Google Drive connector's upload path** — last resort, only when neither of the above is available. That connector renders literal markdown characters as escaped text rather than real formatting, so fall back to the plain-labeled-paragraph text structure from Step 3 instead of the formatted version below.

With either #1 or #2, apply real Docs-API-level formatting via whatever tool the connector actually exposes for each outcome below — exact tool/function names vary by environment (e.g. mcp-drive's `insert_doc_elements` takes an `asBullets` flag rather than a separate bullet-list tool; google-workspace-bc applies `createParagraphBullets` through its `batch_update_doc` escape hatch) — fall back to a raw `batch_update_doc` request for anything the friendly wrapper doesn't expose directly, rather than assuming a specific named tool exists:

- Meeting Title line: heading style (e.g. `HEADING_1` or bold + larger size), not a plain paragraph.
- Section labels (`Summary`, `Action Items`, `Decisions Made`) — bold, so they read as headers, not just another line of text.
- `Action Items` and `Decisions Made` entries — real bulleted lists, not plain paragraphs.
- The metadata block (Date/Attendees/Project/Debriefed by) can stay plain text.

## Step 5: Log decisions (if any)

If Step 3 surfaced a real decision, also add a one-line entry to `[project]/80_agents/Decisions Log` (create this doc if it doesn't exist yet, with a short header explaining its purpose and a `Last updated: [YYYY-MM-DD]` front matter line).

```
[YYYY-MM-DD] DECISION: [what was decided] | REASONING: [why] | CONTEXT: Source — [meeting title, link to the summary doc]
```

**The log is newest-first, chronological order** — insert each new entry at the top (right after the doc's front matter/intro), never appended to the bottom. Insert the entry text with two trailing newlines already included in a single write — don't insert the entry first and then go back with a second write to fix a missing blank-line separator; get the spacing right in the one insertion.

**Bold ONLY the `[YYYY-MM-DD] DECISION:` prefix — not the REASONING or CONTEXT text, and not the whole entry.** When applying this via the Docs API, compute the exact character range covering just that prefix substring; don't bold the full inserted line just because it's the simpler range to compute. Leave a blank line between entries.

**Update the doc's own `Last updated:` front matter line to today's date every time a new entry is added.** This is easy to forget since it's a small edit separate from the entry insertion itself — treat it as part of the same write, not an optional afterthought.

Inserting at a specific position inside an existing doc requires real Docs API access — `mcp-drive` or `google-workspace-bc`'s `batch_update_doc` (same preference order as Step 4). **The plain native Drive connector cannot do this step at all** — it can create new files but can't edit an existing one's content. If neither `mcp-drive` nor `google-workspace-bc` is available, say so and skip this step rather than attempting a workaround (e.g. appending to the bottom, which breaks the newest-first convention).

This step is a candidate for removal/adjustment during fine-tuning — it's here because scattered per-meeting files make "why was X decided" hard to answer later, but it's a judgment call whether every project wants a running decisions doc. Open idea (not yet decided, 2026-09-17): decision logging might warrant becoming its own standalone skill rather than a step here, since it has its own real complexity (positional insertion, front-matter maintenance, formatting precision) distinct from the rest of a meeting debrief.

## Step 6: Draft a Slack message and ask before posting

Never post to Slack without explicit confirmation. Draft the message, show it to the user, and ask "Post this to [channel]?"

**"Show it to the user" means literally as plain text in this conversation — never via any Slack tool**, including a "send yourself a draft" or self-DM style preview. Calling any Slack tool before the user has explicitly confirmed defeats the confirmation gate, even when the target is the user's own DM rather than the real channel — it's still an unconfirmed Slack action, and it's easy for the user to miss it landing somewhere in Slack instead of in the conversation they're already reading.

```
📝 Meeting debrief: [Meeting Title]
🗓️ [Date]
🔗 [Link to the summary doc]

Quick recap: [1-sentence summary]

Potential todos:
- [todo 1]
- [todo 2]

Post this to [#channel]?
```

**Always check `[project]/80_agents/README`'s Metadata section for a listed Slack channel before drafting the message — don't ask first.** Only ask the user directly if no channel is listed there. This is easy to skip on a quick pass since it previously read as a soft fallback; treat it as a required first step, not something to remember only if it happens to come to mind.

## Step 7: Check attendees — and named externals — against the People folder

Client-side people only, Bluecadet's own team is already covered by local `people/` (see the `people-capture` rule) — don't create People docs for internal teammates here.

**Client-side = anyone (attendee or not) whose email domain isn't `@bluecadet.com`, or who's clearly external from context when no email is available.** That's the actual rule, stated explicitly rather than left as an inferred judgment call.

**This step covers two categories, not just attendees: actual meeting attendees, and any other external person named with identifying context during the meeting** — a role, an org, a reason they came up (e.g. "their new IT director starts next month, Jane Smith"). A bare name mentioned once with nothing else attached doesn't count — don't surface someone from a passing name-drop with no context to actually put in a People doc.

**Always say something for this step, even when it's a no-op.** If every attendee is internal and nothing else external was substantively named, say so in one line (e.g. "No client-side attendees or named externals — skipping People folder check") rather than silently skipping the step without mentioning it. A silent skip looks identical to a forgotten step; an explicit one-line no-op is auditable.

- Look for an `80_agents/People/` folder inside the project's Drive folder (same folder found in Step 2). Create it if `80_agents` exists but `People` doesn't yet.
- For each client-side attendee, and each named-with-context external mention, check whether a doc already exists for them (search by name).
  - **Doesn't exist:** offer to create one using the People — Template structure (`Identity`: Role, Company/Org, Relationship [client/vendor], Projects; `Contact`: Email, Phone, LinkedIn; `Notes`; `History`). Only fill in what's actually known from this meeting, leave the rest blank rather than guessing. Don't offer to create a doc for a bare-name mention with no context — that's the passing-mention case this step intentionally skips.
  - **Exists, and this meeting surfaced new/changed info** (a title change, new contact info, a role clarification): offer to update it — append to `Notes` or `History`, don't silently overwrite what's already there. Creating a new doc here would just produce a duplicate; use the Docs API directly (`mcp-drive`'s or `google-workspace-bc`'s `batch_update_doc`/`insert_doc_elements`, whichever is available — same preference order as Step 4) to append to the existing one instead.
  - **Exists, nothing new:** leave it alone, don't touch a doc just because the person showed up again.
- Front matter on a new doc: `Last updated: [YYYY-MM-DD] · Status: current`, matching the format already used in existing People docs (e.g. NWWII's).
- Cite the source (e.g. "Source: [meeting title] debrief, [date]"), same pattern the existing People docs already use.
- Always ask before creating or updating, same confirmation bar as the Slack draft in Step 6, this is shared team content, not a silent side effect of debriefing a meeting.

## Step 8: Log friction (if any)

Track real friction as it happens through Steps 1-7 — not every imperfection, only things with a plausible fix (same principle as the team's own internal friction log: "this wouldn't have happened if the system were better set up"). At the end of the run, if anything qualifies, write it to `[project]/80_agents/Friction Log` (create this doc if it doesn't exist yet, using the Friction Log — Template structure from the Global_Agents Drive folder, front matter `Last updated: [YYYY-MM-DD] · Status: current`).

**Categories:**
- `wrong-guess` — a tool/format/behavior assumption that turned out wrong
- `missing-context` — had to ask the user for something the docs should already have had
- `retry` — a tool call failed and needed a workaround
- `ambiguous-instruction` — this skill's own instructions were unclear about what to do

**Entry format**, appended to the bottom of the doc (chronological, oldest to newest — not the Decisions Log's newest-first convention):

```
[YYYY-MM-DD] [category] Description | potential fix
```

If the friction is really about this skill's own instructions rather than something specific to this project, add a `scope: skill` tag so it's identifiable later even though it's filed under one project's log:

```
[YYYY-MM-DD] [category] [scope: skill] Description | potential fix
```

**No confirmation gate for this write** — unlike every other write in this skill, friction entries are Claude's own process observations, not claims about what someone said or decided, so they don't need the same show-and-confirm bar. Just tell the user at the end of the run how many were logged (e.g. "Logged 2 friction items") — same one-line acknowledgment pattern as Step 7's no-op case, never silent. If nothing qualified this run, say so in one line rather than skipping the mention entirely (e.g. "No friction to log this run").

---

## Notes

- Never include specific dollar figures, margins, or anything marked "INTERNAL ONLY" / "NEVER TO BE SHARED WITH THE CLIENT" in the Slack message text — those stay in the Drive doc only, and only if the project's own instructions treat that Drive folder as internal-only.
- If a project's Drive folder structure doesn't match what this skill expects (no `80_agents`, no `Meeting Notes`), stop and say so rather than adapting silently — that's a sign the project needs onboarding to this pattern first, not a reason to improvise a different location.
- Keep summaries factual and concise — they're for someone re-orienting to the project, not a full transcript replay.
