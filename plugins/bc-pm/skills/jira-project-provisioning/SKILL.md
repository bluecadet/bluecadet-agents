---
name: jira-project-provisioning
description: Provision a new Jira Cloud project at Bluecadet — clones a base project's (WEBBASE/EXPBASE/SAOBASE) schemes, adds roles, and creates a board/sprint — using the mcp-jira connector. Runs as the calling user's own Jira identity, so it only succeeds for someone who actually has Jira admin rights.
---

# Jira Project Provisioning

Triggered by: "create a new Jira project", "set up Jira for [project]", "provision a Jira project called [name]"

This skill requires the **mcp-jira** connector (Bluecadet's internal remote MCP server, `mcp-jira.netlify.app`). It calls the Jira Cloud REST API as the connected user's own OAuth identity — there is no shared service account. A new project's "Created by" reflects the real person who ran this, and Jira's own admin-permission checks are the actual gate on whether it succeeds: if the calling user isn't a Jira admin, the create-project call will fail with a 403, same as it would in the Jira UI. If the `mcp-jira` connector isn't available in this environment, say so and stop — don't fall back to any local script or personal credential.

---

## Step 1: Gather the basics

Ask for whatever isn't already given:

- **Project name** — e.g. "Ridgeline Cafe"
- **Project key** — 2-10 uppercase letters/digits, starting with a letter (e.g. `RCC`). If the user hasn't picked one, suggest a short one derived from the name and confirm it with them rather than guessing silently.
- **Base project to clone from** — one of:
  - `WEBBASE` — category Web (website/client delivery work)
  - `EXPBASE` — category Experiential
  - `SAOBASE` — category Strategy & Ops
  
  If it's not obvious which category the new project belongs to, ask rather than assuming.

## Step 2: Resolve the lead's account ID

Use `search_jira_users` with the lead's name or email to get their Jira account ID. Always resolve this explicitly — never assume the calling user is the lead just because they're the one running this.

Decide initial admins (normally just the lead) and any initial members. Additional people can always be added later via Step 7 — default to a minimal initial set rather than adding everyone who might eventually need access.

## Step 3: Decide board type and scope

If a board is wanted at all, ask **Scrum or Kanban** first — this isn't a minor detail, it changes what's possible next:

- **Kanban boards don't support sprints at all.** This is a Jira Agile API constraint, not a preference — `provision_jira_project` ignores `skipSprint` entirely and never creates a sprint when `boardType: "kanban"`. Don't offer sprint-related scope choices if the user picks Kanban.
- **Scrum boards** support the full scope choice below.

Then decide scope:

- **Project only** (`skipBoard: true`) — nothing's ready yet, no board/filter/sprint
- **Project + board, no sprint** (`skipSprint: true`, scrum only) — the normal choice when the board should exist ahead of real issues but there's nothing to sprint-plan into yet
- **Project + board + first sprint** (scrum only, no flags) — only once there's real work to put into it immediately
- **Project + Kanban board** (`boardType: "kanban"`) — sprint scope choices don't apply here at all

## Step 4: Discover the base project (read-only)

Call `discover_base_project` with the chosen source key. This makes zero write calls — it just pulls the real scheme/category/role IDs that will get cloned. Show the user a short summary (category, workflow, permission scheme) before moving on, so they can catch a wrong base project choice before anything is created.

## Step 5: Plan, confirm, then execute

Call `provision_jira_project` with `dryRun: true` (the default) — this returns the exact plan (every call it would make) with zero writes, same as Step 4 but for the full provisioning sequence including roles and board/sprint. Show this plan to the user.

**Get an explicit confirmation before calling it again with `dryRun: false`.** Creating a real Jira project isn't cleanly reversible (deleting a project doesn't cleanly undo everything downstream — dashboards, filters, links), so this needs the same confirm-before-acting bar as any other shared, hard-to-reverse action — don't treat the dry-run plan as implicit approval to proceed.

Once confirmed, call `provision_jira_project` again with `dryRun: false`. Report back exactly what was created (project key/id, roles added, board id, sprint if any) — pull this straight from the tool's own response, don't paraphrase or guess at IDs.

## Step 6: Manual checklist (no API for these)

Tell the user these still need to happen by hand in the Jira UI — `provision_jira_project`'s own response includes this same reminder, but restate it plainly:

- Board column layout, card colors by priority, swimlanes by assignee, JQL quick filters — see the reference column models below, which one applies depends on the base project used in Step 1
- Add the project to the "Default Description Fields 2.0" automation rule (Jira Automation admin UI)
- Link the GitHub repo to the dev panel, once one exists for the actual build
- Client user group creation/invites — deliberately manual, not an API limitation (paid seats)

**Also flag this one explicitly:** Jira Cloud can auto-populate a project role (commonly "Client") with org-configured default members on every new project. If the user mentions anything looking wrong in a role they didn't touch, that's the likely cause — point them at Jira Settings → System → Project roles → [role] → Default Members, or have them remove the unwanted actor directly on the new project.

**Reference column models — these are suggestions, not requirements, and how strongly to hold to them varies by base project:**

**Web (`WEBBASE`)** — ACMW's real, tuned board, a strong suggestion (proven across a live production project, not a starting guess):

| Column | Statuses |
|--------|----------|
| Needs Refinement | Needs Refinement, Reopened |
| Blocked | Blocked |
| Ready | To Do, Ready for Implementation |
| In Progress | In Progress, Design In Progress |
| Review/UAT | Code/PR Review, Team Review, Design Review, INT QA, CLIENT UAT |
| Waiting to Push | Merged, Deployable |
| Done | Done |

**Experiential (`EXPBASE`)** and **Strategy & Ops (`SAOBASE`)** — a simpler 5-column model:

| Column |
|--------|
| To Do |
| In Progress |
| Review |
| Blocked |
| Done |

Treat this one as slightly loose for Experiential projects and very loose for Strategy & Ops — offer it as the starting point, but don't push back if the project lead wants to deviate from it the way you might for the Web model.

## Step 7: Adding people or a sprint later

Don't re-run the full provisioning flow for follow-up changes to an existing project:

- **Add someone to a role:** resolve their account ID with `search_jira_users`, then `add_project_role_member` with the project key, role ID (from Step 4's discovery output), and account ID.
- **Create a sprint once there's real work to plan:** `create_project_sprint` with the board ID and a sprint name.

---

## Notes

- This skill only provisions the project itself. It does not scope, estimate, or plan the actual work that will live in the new project — that's a separate conversation.
- If `provision_jira_project` fails on the real (non-dry-run) call, report the actual error message back to the user rather than a generic "something went wrong" — Jira's own error text (e.g. a 403 on create, or a 400 on the filter step if it runs immediately after project creation and Jira's search index hasn't caught up yet) is usually specific enough to act on directly.
- Full technical history and known gotchas for this provisioning logic live in Bluecadet's `mcp-workspace-tools` repo (`mcp-jira/`) and in KrakenOS's `references/sops/jira-project-creation.md` — don't re-derive that history here if something looks off, check there first.
