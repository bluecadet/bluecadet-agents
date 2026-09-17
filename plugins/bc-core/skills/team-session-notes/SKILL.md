---
name: team-session-notes
description: Use this when working in a local Claude Code session on a Bluecadet project and something comes up that the whole team should know about, not just this session, a technical finding, a workflow gotcha, a decision, new or changed info about a client-side contact, anything worth the team's shared project knowledge. Proactively flag candidates as they come up mid-session and ask before writing anything. Not for meeting content, that's team-meeting-debrief's job.
---

# Team Session Notes

Bridges a local Claude Code session to a project's shared `80_agents` Google Drive folder, the same shared-knowledge destination `team-meeting-debrief` writes to from inside a claude.ai Project. This skill covers the gap that leaves: things that surface during hands-on local work, not during a meeting.

**Environment note:** unlike `team-meeting-debrief` (runs inside a claude.ai Project, using its native connectors), this skill runs in a local Claude Code session. It needs `pandoc` installed and a working Google Workspace MCP connection for whoever's running it. If either isn't available, say so and stop rather than attempting a broken write.

---

## Step 1: Notice, don't assume

Mid-session, if something comes up that other people on this project (or the wider team) would benefit from knowing, flag it: "This seems worth sharing to the team, want me to add it to \[project\]'s `80_agents` folder?"

Don't write anything without an explicit yes. This is different from `team-meeting-debrief`, which the user invokes directly, here Claude is the one noticing, so the bar for confirming first is higher, not lower.

**What's worth flagging:** a technical finding future work will need (root cause of a bug, a constraint discovered the hard way), a workflow gotcha (an API that silently fails a certain way, a tool limitation), a decision made during the session with real reasoning behind it, new or changed information about a client-side contact, anything that would otherwise only live in this one local session's transcript and nowhere else.

**What's not:** routine progress, anything already going into a Jira ticket or commit message where the team will see it anyway, anything so project-specific-to-right-now that it won't matter in a week.

## Step 2: Classify — decision, people update, or note?

- **A real decision was made, with reasoning** → Step 3 (route to the existing Decisions Log).
- **New or changed info about a client-side contact** → Step 4 (People folder).
- **Everything else worth sharing** → Step 5 (new Session Notes doc).

## Step 3: Decisions go to the existing Decisions Log

Don't reinvent this. Find the project's `80_agents/Decisions Log` doc (same folder-discovery approach as `team-meeting-debrief`'s Step 2: search Drive for the project folder, look for `80_agents`, stop and say so if it doesn't exist) and append using the exact same format and conventions `team-meeting-debrief` already uses for its own decision-logging step in this plugin: newest-first (insert at the top, never appended to the bottom), bold the `[YYYY-MM-DD] DECISION:` prefix, blank line between entries:

```
[YYYY-MM-DD] DECISION: [what was decided] | REASONING: [why] | CONTEXT: Source — [one-line description of the session/work, not a meeting]
```

Stop here, don't also create a Session Notes doc for the same thing.

## Step 4: Client contact info goes to the People folder

Client-side only, Bluecadet's own team is already covered by local `people/` (see the `people-capture` rule) — don't create People docs for internal teammates here.

- Look for an `80_agents/People/` folder inside the project's Drive folder. Create it if `80_agents` exists but `People` doesn't yet; if `80_agents` itself doesn't exist, stop and say so, don't invent the whole structure.
- Check whether a doc already exists for this person (search by name).
  - **Doesn't exist:** offer to create one using the People — Template structure (`Identity`: Role, Company/Org, Relationship [client/vendor], Projects; `Contact`: Email, Phone, LinkedIn; `Notes`; `History`). Only fill in what's actually known from this session, leave the rest blank rather than guessing.
  - **Exists, and this session surfaced new/changed info:** offer to update it — append to `Notes` or `History`, don't silently overwrite what's already there.
  - **Exists, nothing new:** leave it alone.
- Front matter: `Last updated: [YYYY-MM-DD] · Status: current`, matching the format already used in existing People docs (e.g. NWWII's).
- Cite the source in `Notes` or `History` (e.g. "Source: [one-line session description], [date]"), same pattern the existing People docs already use.
- Always ask before creating or updating, same bar as everything else this skill writes.

## Step 5: Non-decision, non-people findings get a Session Notes doc

Look for an `80_agents/Session Notes` subfolder inside the project's Drive folder. Create it if `80_agents` exists but `Session Notes` doesn't yet, this is a new convention this skill introduces. If `80_agents` itself doesn't exist, stop and say so, same as `team-meeting-debrief` does, don't invent the whole structure.

**Content** (plain prose, no markdown syntax in the body text, formatting gets applied by the DOCX conversion in Step 6, not written by hand):

```
[Title]
Date: [date]
Project: [project name]
Noted by: [the user's full name]

[2-4 sentence narrative: what was found, why it matters to the team, what someone should do with this knowledge]
```

**Front matter**, required on every `80_agents` doc per the team-knowledge-base convention:

```
Last updated: [YYYY-MM-DD]
Status: current
Owner: [only if someone is actually accountable for keeping this fresh — most session notes won't have one]
```

**Filename:** `YYYY-MM-DD-kebab-case-title--lastname` (same convention as `team-meeting-debrief`'s Meeting Notes, double-dash before the noter's last name).

## Step 6: Build the doc via the confirmed-working pipeline

Applies to both the Session Notes path (Step 5) and new/updated People docs (Step 4). Do not write directly through a plain Drive-connector text upload, that path has a known markdown-escaping bug (literal `#`/`*`/`-` come out escaped instead of rendering as real formatting). Use the pipeline validated 2026-09-01 for `80_agents` docs:

1. Write the front matter + content to a local Markdown file in the scratchpad directory.
2. Convert it: `pandoc input.md -o output.docx`
3. Upload with Drive's own conversion: `import_to_google_doc` with `file_path` pointing at the `.docx`, `source_format: "docx"`, `folder_id` set to the destination folder's ID (`Session Notes` or `People`), `file_name` set accordingly (the person's name for a People doc, the Step 5 filename for a session note).

For a People doc *update* rather than a fresh create, this pipeline doesn't apply as-is since it always produces a new file, use the Docs API directly (`batch_update_doc`/`insert_doc_elements`) to append to the existing doc's `Notes`/`History` sections instead of recreating it.

Confirm the doc landed with real formatting (headings/bold, not escaped literal characters) before telling the user it's done.

## Step 7: Tell the user, don't just report success silently

Give a one-line summary and a link to the doc. Unlike `team-meeting-debrief`, this skill has no Slack-drafting step, if that's ever wanted, it should be layered on deliberately, not assumed.

## Notes

- The `80_agents` folder is Claude-maintained, not hand-edited by teammates, a stated team-knowledge-base convention, not a Drive permission lock. Don't undermine it by suggesting the user edit a doc directly instead of going through this skill.
- Never include specific dollar figures, margins, or anything marked "INTERNAL ONLY" in a Session Notes or People doc unless the project's own instructions already treat `80_agents` as strictly internal, same caution `team-meeting-debrief` applies to its Slack drafts.
- This skill does not touch the project's existing human-maintained running notes doc, `80_agents` doesn't reinvent that as a second activity log.
