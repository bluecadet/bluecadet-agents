---
name: team-meeting-debrief
description: Debrief a Granola meeting for a Bluecadet project — pulls the transcript, summarizes it, saves the summary into the project's shared Drive folder, optionally logs a decision, and drafts a Slack post for the user to review before sending.
---

# Team Meeting Debrief

Triggered by: "debrief my meeting", "debrief [meeting name]", "summarize my meeting with [X]"

This skill runs inside a claude.ai Project, using the Granola connector, the Google Drive connector, and (at the final step) the Slack connector. It is meant to work across any Bluecadet project that has adopted the `80_agents` folder convention — it is not specific to one project.

---

## Step 1: Identify the meeting

- If the user named a specific meeting, search Granola for it by name/date.
- If not, ask which meeting, or offer a short list of their recent unprocessed meetings to choose from.
- Pull the full notes/transcript for the chosen meeting.
- If Granola has no transcript for it, say so and stop — don't guess at content.

## Step 2: Identify the project and its Drive folder

- If the project isn't obvious from the meeting title, ask which project this belongs to.
- Search Google Drive for that project's folder by name.
- Look for an `80_agents` subfolder inside it.
  - **If `80_agents` doesn't exist:** stop and tell the user this project hasn't been set up for this workflow yet (no defined place to save the summary). Don't invent a folder structure or guess where to put it.
  - **If it exists but there's no `Meeting Notes` subfolder inside it:** same — stop and say so, rather than creating one unasked.

## Step 3: Generate the summary

Write the summary as plain prose with labeled sections on their own line — no markdown syntax (`#`, `*`, `-`, `[]`) in the text itself. (Docs created through the Drive connector render literal markdown characters as escaped text rather than real formatting — plain labeled paragraphs avoid that problem entirely.)

```
[Meeting Title]
Date: [date]
Attendees: [list]
Project: [project name]

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

## Step 4: Save to Drive

Create a new Doc inside `[project]/80_agents/Meeting Notes`, named `YYYY-MM-DD-kebab-case-meeting-title`.

## Step 5: Log decisions (if any)

If Step 3 surfaced a real decision, also append a one-line entry to `[project]/80_agents/Decisions Log` (create this doc if it doesn't exist yet, with a short header explaining its purpose):

```
[YYYY-MM-DD] DECISION: [what was decided] — REASONING: [why] — SOURCE: [meeting title, link to the summary doc]
```

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

---

## Notes

- Never include specific dollar figures, margins, or anything marked "INTERNAL ONLY" / "NEVER TO BE SHARED WITH THE CLIENT" in the Slack message text — those stay in the Drive doc only, and only if the project's own instructions treat that Drive folder as internal-only.
- If a project's Drive folder structure doesn't match what this skill expects (no `80_agents`, no `Meeting Notes`), stop and say so rather than adapting silently — that's a sign the project needs onboarding to this pattern first, not a reason to improvise a different location.
- Keep summaries factual and concise — they're for someone re-orienting to the project, not a full transcript replay.
