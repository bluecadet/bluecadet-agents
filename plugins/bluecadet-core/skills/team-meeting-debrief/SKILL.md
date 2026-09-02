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

- If the user named a specific meeting, search Granola for it by name/date first — it's the primary source (Granola notes are pre-summarized and cheaper to process). If nothing turns up there, search Zoom (`mcp__claude_ai_Zoom_for_Claude__search` or `search_meetings`) by the same name/date before concluding the meeting can't be found.
- If not, ask which meeting, or offer a short list of recent unprocessed meetings to choose from — pulled from whichever source(s) are relevant.
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
- Search Google Drive for that project's folder by name.
- Look for an `80_agents` subfolder inside it.
  - **If `80_agents` doesn't exist:** stop and tell the user this project hasn't been set up for this workflow yet (no defined place to save the summary). Don't invent a folder structure or guess where to put it.
  - **If it exists but there's no `Meeting Notes` subfolder inside it:** same — stop and say so, rather than creating one unasked.

## Step 3: Generate the summary

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

Multiple team members can each debrief the same meeting from their own perspective — this produces one doc per person per meeting, not one shared/merged doc. `Debriefed by` is what distinguishes them; don't try to merge or dedupe against another person's existing debrief of the same meeting.

## Step 4: Save to Drive

Create a new Doc inside `[project]/80_agents/Meeting Notes`, named `YYYY-MM-DD-kebab-case-meeting-title--lastname` (double dash before the debriefer's last name — keeps multiple people's debriefs of the same meeting from colliding on filename, and visually separates the name tag from the title).

If two meetings share the same date and title (e.g. two same-day syncs both titled "Review NWWIIM Dev Estimates"), insert a 24-hour HHMM time right after the date to disambiguate: `YYYY-MM-DD-HHMM-kebab-case-meeting-title--lastname`. Only add the time when there's an actual collision — don't add it by default.

At the very top of the doc, above the Meeting Title line, add a one-line banner: `AI Generated - DO NOT EDIT`, bold and italic, normal text size (not a heading — it's a flag, not a section, so it shouldn't take up much vertical space). Leave one blank line between the banner and the Meeting Title line so it doesn't visually run into the front matter.

**Apply real formatting, don't leave it as flat text** (when created via the Docs API — `create_doc` + `batch_update_doc`/`update_paragraph_style`, which this skill has direct access to when run outside a claude.ai Project; if only the plain Drive-connector upload path is available, fall back to the plain-labeled-paragraph text above, since that connector renders literal markdown characters as escaped text rather than real formatting):

- Meeting Title line: heading style (e.g. `HEADING_1` or bold + larger size), not a plain paragraph.
- Section labels (`Summary`, `Action Items`, `Decisions Made`) — bold, so they read as headers, not just another line of text.
- `Action Items` and `Decisions Made` entries — real bulleted lists (`create_bullet_list`), not plain paragraphs.
- The metadata block (Date/Attendees/Project/Debriefed by) can stay plain text.

## Step 5: Log decisions (if any)

If Step 3 surfaced a real decision, also add a one-line entry to `[project]/80_agents/Decisions Log` (create this doc if it doesn't exist yet, with a short header explaining its purpose):

```
[YYYY-MM-DD] DECISION: [what was decided] | REASONING: [why] | CONTEXT: Source — [meeting title, link to the summary doc]
```

**The log is newest-first, chronological order** — insert each new entry at the top (right after the doc's front matter/intro), never appended to the bottom. Bold the `[YYYY-MM-DD] DECISION:` prefix, and leave a blank line between entries.

This step is a candidate for removal/adjustment during fine-tuning — it's here because scattered per-meeting files make "why was X decided" hard to answer later, but it's a judgment call whether every project wants a running decisions doc.

## Step 6: Draft a Slack message and ask before posting

Never post to Slack without explicit confirmation. Draft the message, show it to the user, and ask "Post this to [channel]?"

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

Determine the channel from the project's own README/metadata if available; otherwise ask.

## Step 7: Check attendees against the People folder

Client-side attendees only, Bluecadet's own team is already covered by local `people/` (see the `people-capture` rule) — don't create People docs for internal teammates here.

- Look for an `80_agents/People/` folder inside the project's Drive folder (same folder found in Step 2). Create it if `80_agents` exists but `People` doesn't yet.
- For each client-side attendee, check whether a doc already exists for them (search by name).
  - **Doesn't exist:** offer to create one using the People — Template structure (`Identity`: Role, Company/Org, Relationship [client/vendor], Projects; `Contact`: Email, Phone, LinkedIn; `Notes`; `History`). Only fill in what's actually known from this meeting, leave the rest blank rather than guessing. Don't bulk-create docs for people who were only mentioned in passing, not actual attendees.
  - **Exists, and this meeting surfaced new/changed info** (a title change, new contact info, a role clarification): offer to update it — append to `Notes` or `History`, don't silently overwrite what's already there. Creating a new doc here would just produce a duplicate; use the Docs API directly (`batch_update_doc`/`insert_doc_elements`) to append to the existing one instead.
  - **Exists, nothing new:** leave it alone, don't touch a doc just because the person showed up again.
- Front matter on a new doc: `Last updated: [YYYY-MM-DD] · Status: current`, matching the format already used in existing People docs (e.g. NWWII's).
- Cite the source (e.g. "Source: [meeting title] debrief, [date]"), same pattern the existing People docs already use.
- Always ask before creating or updating, same confirmation bar as the Slack draft in Step 6, this is shared team content, not a silent side effect of debriefing a meeting.

---

## Notes

- Never include specific dollar figures, margins, or anything marked "INTERNAL ONLY" / "NEVER TO BE SHARED WITH THE CLIENT" in the Slack message text — those stay in the Drive doc only, and only if the project's own instructions treat that Drive folder as internal-only.
- If a project's Drive folder structure doesn't match what this skill expects (no `80_agents`, no `Meeting Notes`), stop and say so rather than adapting silently — that's a sign the project needs onboarding to this pattern first, not a reason to improvise a different location.
- Keep summaries factual and concise — they're for someone re-orienting to the project, not a full transcript replay.
