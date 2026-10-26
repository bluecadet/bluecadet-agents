---
name: create-drive-project
description: Create a new Bluecadet project folder in Google Drive from one of the project folder-structure templates (copies the template, fills in the project name and year). Use when someone wants a new Drive project folder, project directory, or "project structure" set up. Not for Jira projects (see jira-project-provisioning).
---

# Create Drive Project

Triggered by: "create a new project folder", "set up a Drive project for [name]", "new project directory", "copy the project template"

This is about the **Google Drive project folder**, not Jira. For a Jira project use `jira-project-provisioning`.

This skill needs the **mcp-drive** connector (Bluecadet's internal remote MCP server, `mcp-drive.netlify.app`), specifically its `copy_drive_folder` tool. It runs as the connected user's own Google identity. If the connector or that tool isn't available, say so and stop. Don't fall back to copying folders by hand with other Drive tools.

All Drive IDs live in `scripts/drive_project.py`. Never type an ID from memory. Take the templates folder, the destination and the placeholder values only from that script's output.

---

## Step 1: Gather the basics

Ask for whatever isn't already given:

- **Project name.** Used as the new folder's name and in file names, so confirm the exact spelling.
- **Template.** Don't ask until you've listed them (Step 2).

New projects go in the live projects folder. Only use test mode if the user says it's a trial or test run.

## Step 2: List and pick a template

Run:

```bash
python3 scripts/drive_project.py templates
```

Make the `search_drive_files` call it prints. Show the user the template names and ask which one to use. Don't guess from the project name. Take the chosen folder's ID from the search result.

## Step 3: Confirm, then plan

Tell the user what will happen in one or two lines: the template, the new folder name, and the destination (live projects folder or test folder). Wait for a yes.

Then run:

```bash
python3 scripts/drive_project.py plan --name "<project name>" --template-id "<template folder id>" --mode live
```

Use `--mode test` for a trial run. If the script prints an error (for example the name has a character Drive doesn't allow), show it and ask for a different name. Don't edit the name yourself.

## Step 4: Copy

Call `copy_drive_folder` with exactly the `arguments` the script printed, changing nothing.

The tool does a bounded amount of work per call. If the result has `done: false`, call it again with the **same arguments plus the `cursor` from the result**, and repeat until `done: true`. Pass the cursor back untouched.

If a call fails partway through, say what failed and stop. Don't restart from scratch: a fresh start with the same name is refused because the folder already exists, and a retry could copy some files twice. Ask the user how they want to proceed.

## Step 5: Report

When `done: true`, give the user:

- The link to the new folder (`rootFolderUrl`)
- How many folders and files were created
- Any `warnings`, in plain words. A warning that a shortcut points outside the template means that shortcut still points at the original target. A warning that placeholders couldn't be filled inside a Doc or Sheet means that file was copied with its `[ProjectName]`-style text unchanged.

## What gets filled in

`[ProjectName]` and `[Year]` are replaced in file and folder names, and inside the text of copied Google Docs and Sheets. Slides decks are copied as-is. To support another placeholder, add it to `build_replacements()` in `scripts/drive_project.py`.

## Not included (yet)

The `80_agents` folder isn't part of any template and this skill doesn't add it. It's meant as an optional add-on later.

## For a future dev

- The copy logic is the `copy_drive_folder` tool in [bluecadet/mcp-workspace-tools](https://github.com/bluecadet/mcp-workspace-tools), `mcp-drive/src/copy-folder.ts`. It replaced the old Apps Script web app ("BC GDrive Add-on / WebApp").
- If the templates folder or the projects folder moves, change the constants at the top of `scripts/drive_project.py`.
- The tool works in short steps because it runs as a Netlify function with a request time limit. That's why the cursor loop exists.
