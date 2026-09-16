---
name: git-workflow
description: Guided git workflow for non-developers (designers, PMs, anyone unfamiliar with git) doing real work in a Bluecadet repo — turns raw uncommitted changes into safe, atomic, Conventional-Commits-formatted commits with plain-English explanations at every step. Triggers on "commit this," "save this to git," "help me get this into GitHub," "make a pull request," "how do I create a branch," "I don't know git, can you help." Not for experienced developers who just want fast automation — this always explains and always asks first.
---

# Git Workflow (guided, for non-devs)

This skill is for someone who wants to safely get real work into git without necessarily understanding git. It is not a tutorial and not a speed tool — it's a careful, explain-first guide through the minimum steps needed: commit, maybe branch, maybe PR.

For pure git education (someone who wants to learn git conceptually, not just get unblocked right now), see `Use_When` below — that's a different need, covered elsewhere.

## Use_When

- The user has uncommitted changes in a real working tree and wants them saved to git / pushed / turned into a PR, and shows uncertainty about how git works.
- The user asks in plain language for help with git/GitHub without using git terminology precisely ("how do I get this online," "save my work," "send this to the team").

## Do_Not_Use_When

- The user is an experienced developer who wants fast, low-friction automation (drafting a message and moving on) — this skill's explain-and-confirm-every-step pace will feel slow to them; defer to a lighter-touch approach instead.
- The user wants to *learn* git from zero — setup, what a commit/branch/PR actually is, hands-on lessons. That's a distinct need from getting today's real work committed safely. See Step 0.

## Step 0: beginner check

If the user's request suggests they want to actually learn git — not just get unblocked on today's task — check `bluecadet-core:plugin-advisor`'s registry for the `navigating-github` entry and point them at it (`/github-learn`) instead of teaching git concepts inline here. This skill assumes "I have real changes, help me handle them safely" — not "teach me how this works."

If they just want to get their current changes committed and are fine learning as they go (the do-then-explain style), continue with the steps below.

## Steps

1. **Look at the real working tree.** Run `git status` and `git diff` to see what's actually changed. This is a single-user real repo (not a shared multi-session tree), so — unlike an internal dev-facing commit tool — trusting `git status` directly is fine here.

2. **Group changes into atomic commits.** Read the diff and identify whether it spans more than one unrelated concern (e.g. an unrelated typo fix mixed in with a real feature change). If so, say so in plain language and propose splitting into separate commits — explain *why* this matters (clean history, easier to undo one thing without undoing another) rather than just doing it silently. If everything genuinely belongs together, treat it as one commit.

3. **Draft each commit message** per `bluecadet-core:git-conventions` (type, ticket-number scope if one exists, terse subject, body only if there's a non-obvious why). Explain in plain English what's about to happen ("this saves your changes to the CSS file with a message describing what changed") before showing the exact message.

4. **Get explicit approval before any git write operation.** Show the drafted message (or the branch name, or the PR description) and wait for a clear yes before running `git add`, `git commit`, creating a branch, pushing, or opening a PR. Never chain these together on an assumption of approval — ask again at each new operation type, since this audience can't judge on their own which step is safe to skip past.

5. **Branch, if needed.** If the user is working directly on a protected branch (`main`/`master`/`develop`) and is about to commit something that should go through review, explain branches in plain terms ("a branch is a safe copy to work in without touching the main version") and offer to create one first, named per `git-conventions`' `<type>/<ticket-lowercase>-<short-description>` pattern. If they're fine committing directly (e.g. a low-stakes personal/internal repo), don't force a branch on them — ask.

6. **PR, if warranted.** If a PR makes sense (pushing a feature branch for review), draft the PR title/description per `git-conventions`' PR hygiene guidance and `gh pr create` — with the same explain-then-approve gate as commits.

7. **Confirm what happened.** After each approved action, say plainly what was done ("committed as `<hash>`: `<subject>`" / "pushed to `<branch>`" / "opened PR #`<n>`") so the user has a clear record, without dumping raw git output into the conversation.

## Guardrails

- Never `git add -A` or `git add .` — always name the exact files belonging to the atomic change being committed.
- Never commit, push, branch, or open a PR without the user's explicit approval of that specific action.
- Never amend an existing commit.
- Never force-push.
- Never skip hooks (`--no-verify`) or bypass commit signing.
- Never `git reset --hard` or any other operation that discards uncommitted work, without stopping to confirm first — this audience won't reliably know what's recoverable and what isn't.
- If the diff contains anything that looks like a secret, API key, or credential, stop and flag it instead of committing it.
- If there's nothing to commit, say so plainly rather than manufacturing a commit.

These are stricter than a dev-facing commit tool's guardrails on purpose — this audience can't judge when an override might be safe, so the default is always "ask," never "assume."

## Notes

- Built 2026-09-16 as `dev-team`'s first skill, alongside `bluecadet-core:git-conventions` (the shared Conventional Commits reference this skill drafts messages against) and a new `navigating-github` entry in `plugin-advisor`'s registry (for genuine git beginners who want to learn, not just get unblocked).
- Loosely modeled on KrakenOS's own `commit-work` skill (draft → explicit approval → commit, via a subagent, keeping raw git output out of the main conversation), but changed for this audience: works off the real working tree directly rather than session-scoped edits (no multi-session-concurrency problem here), extends the approval gate to every git write operation instead of just the commit, and adds the atomic-commit grouping step, since enforcing that split is the actual point of this skill.
