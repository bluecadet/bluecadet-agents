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

## Step 3: Decide board type, name, and scope

If a board is wanted at all, confirm its **name** explicitly rather than silently defaulting it to the project's name. This matters more than it looks: Jira Cloud's REST API has no endpoint to rename a board once created — confirmed 2026-09-23, it's a long-standing Atlassian feature request that's still unshipped. A wrong board name via this skill can only be fixed by a human renaming it directly in the Jira UI afterward, not by anything this skill or `mcp-jira` can do. Ask "what should the board be called?" and offer the project name as the default, rather than assuming it.

Then ask **Scrum or Kanban** — this isn't a minor detail, it changes what's possible next:

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

## Step 8: Recovering from a partially-failed run

`provision_jira_project` can fail partway through — a real HGSE run (2026-09-22) got a project and its roles created successfully, then hit an error before the board/filter step, leaving the project real but incomplete. As of the 2026-09-22 fix, the tool's own error response now includes everything it actually completed before the failure (not just a bare error) — read that output carefully rather than assuming a failure means nothing happened.

If a run fails or you're picking up a project someone else started, don't blindly re-run `provision_jira_project` — a retry will 400 on "project already exists" once the project itself was created. Instead:

1. **Call `get_project_status`** with the project key — read-only, reports the project's current permission scheme, any boards it already has, and each scrum board's existing sprints (name + state). This tells you exactly what's left to do instead of reasoning it out from the original failure message.
2. **If the permission scheme is wrong:** call `discover_base_project` on the intended source (to get the correct scheme ID), then `update_project_permission_scheme` with the project key and that scheme ID. This touches only the permission scheme, nothing else already set up on the project.
3. **If there's no board yet:** call `create_project_board` with the project key, a name, and the board type — this does filter-then-board together, the same order `provision_jira_project` uses. It's not fully atomic (a previous attempt could have created the filter but not the board), so it checks for an existing filter by its generated name first and reuses it rather than creating a duplicate — you don't need to do anything extra for that case.
4. **If a scrum board has no sprint yet** (per `get_project_status`'s sprint list): `create_project_sprint` as in Step 7. Always check the sprint list first — creating one without checking can leave a project with a duplicate sprint if someone else's partial work already added one.

Skip any step `get_project_status` shows as already done — don't recreate a board, reassign a scheme, or add a sprint that's already correct.

---

## Notes

- This skill only provisions the project itself. It does not scope, estimate, or plan the actual work that will live in the new project — that's a separate conversation.
- If `provision_jira_project` fails on the real (non-dry-run) call, report the actual error message *and* whatever progress it lists back to the user rather than a generic "something went wrong" — Jira's own error text (e.g. a 403 on create, or a 400 on the filter step if it runs immediately after project creation and Jira's search index hasn't caught up yet) is usually specific enough to act on directly, and see Step 8 for how to finish a partial run rather than blindly retrying.
- **Fully root-caused 2026-09-22-23** (took several rounds — the full trail is worth knowing since it wasn't a single fix): classic OAuth scopes never covered the Jira Agile REST API at all — board/sprint/epic only exist as granular scopes under the "Jira Software" product (Atlassian does allow mixing classic scopes with granular ones across different products on the same app). Adding those granular scopes fixed board *creation* (`write:board-scope:jira-software` — one scope) but board *reads* (`get_project_status`, `get_board_by_id`) kept 401ing with a bodyless error even after a full connector disconnect/reconnect that appeared to confirm the right scopes were granted. Surfacing the `WWW-Authenticate`/error-body detail (rather than a bare status code) showed Atlassian's real reason: `"scope does not match"`. Checking Atlassian's own API docs directly showed board *read* endpoints require **two** scopes together — `read:board-scope:jira-software` **and** `read:project:jira` — plus `read:issue-details:jira` since board contents are issues. Even after adding both to the app and doing another confirmed fresh reconnect, the exact same error persisted — the final answer only came from `debug_token_scopes`, which decodes the live access token's own JWT `scope` claim directly: it showed `read:project:jira` genuinely wasn't in the token despite the app being configured for it and the reconnect having "worked." One more reconnect after that resolved it. **The lesson: neither the Atlassian consent screen nor a "successful" reconnect is proof a scope actually landed in the live token — `debug_token_scopes` is the only tool here that reads ground truth instead of inferring it, and is the right first move the next time a scope-shaped 401 doesn't resolve after a reconnect that should have fixed it.**
- Full technical history and known gotchas for this provisioning logic live in Bluecadet's `mcp-workspace-tools` repo (`mcp-jira/`) and in KrakenOS's `references/sops/jira-project-creation.md` — don't re-derive that history here if something looks off, check there first.
