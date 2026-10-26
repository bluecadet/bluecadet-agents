#!/usr/bin/env python3
"""Builds the exact `copy_drive_folder` arguments for a new Bluecadet Drive project.

This is the single place the Drive IDs live. The copy itself runs server-side in
the mcp-drive connector (bluecadet/mcp-workspace-tools, tool `copy_drive_folder`);
this script only validates input and prints the arguments, so every run uses the
same constants and the same name rules instead of whatever the model typed.

FOR A FUTURE DEV: if the Drive structure moves, edit the constants below and
nothing else. They are Google Drive folder IDs (the long string in a folder's
URL after /folders/).
"""

import argparse
import json
import re
import sys
from datetime import date

# Folder holding the project templates. Each subfolder (named
# _Template_FolderStructure_*) is one template a user can pick.
TEMPLATES_FOLDER_ID = "1dxM3J5BTBWhcBHIndwY_vNXQ4SsvZ8M3"

# Where every real new project is created.
LIVE_DEST_FOLDER_ID = "0ALLtRdYfLDX8Uk9PVA"

# Where trial runs go. Safe to fill with junk; clean it out by hand.
TEST_DEST_FOLDER_ID = "0ACcqZ8M0I-NbUk9PVA"

# Substring that matches every template folder's name, used to list them.
TEMPLATE_NAME_SEARCH = "_Template"

DESTINATIONS = {"live": LIVE_DEST_FOLDER_ID, "test": TEST_DEST_FOLDER_ID}

# Characters Drive allows, minus ones that cause trouble in folder names.
_BAD_NAME = re.compile(r'[/\\:*?"<>|\[\]]')


def validate_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("Project name is empty.")
    if len(name) > 100:
        raise ValueError("Project name is longer than 100 characters.")
    if _BAD_NAME.search(name):
        raise ValueError(
            'Project name contains a character that is not allowed: / \\ : * ? " < > | [ ]'
        )
    return name


def build_replacements(name: str) -> dict:
    # Placeholders written as [Key] in template file and folder names, and
    # inside Docs and Sheets. To support a new one, add its key here.
    return {"ProjectName": name, "Year": str(date.today().year)}


def cmd_templates(_args) -> int:
    print(
        json.dumps(
            {
                "tool": "search_drive_files",
                "arguments": {
                    "name": TEMPLATE_NAME_SEARCH,
                    "parentId": TEMPLATES_FOLDER_ID,
                    "fileType": "folder",
                    "pageSize": 100,
                },
            },
            indent=2,
        )
    )
    return 0


def cmd_plan(args) -> int:
    try:
        name = validate_name(args.name)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "mode": args.mode,
                "destination_folder_id": DESTINATIONS[args.mode],
                "tool": "copy_drive_folder",
                "arguments": {
                    "sourceFolderId": args.template_id,
                    "destParentId": DESTINATIONS[args.mode],
                    "newName": name,
                    "replacements": build_replacements(name),
                },
                "note": "Add the returned `cursor` to these same arguments and call again until done is true.",
            },
            indent=2,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("templates", help="print the call that lists the available templates").set_defaults(
        func=cmd_templates
    )

    plan = sub.add_parser("plan", help="print the copy_drive_folder arguments for a new project")
    plan.add_argument("--name", required=True, help="new project folder name")
    plan.add_argument("--template-id", required=True, help="Drive ID of the chosen template folder")
    plan.add_argument(
        "--mode",
        choices=sorted(DESTINATIONS),
        default="test",
        help="test (default) or live. Live is the real projects folder.",
    )
    plan.set_defaults(func=cmd_plan)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
