---
name: update-module-dependencies
description: Use this skill when a developer wants to do a routine dependency-maintenance pass on a Bluecadet-owned Drupal module — checking for newer versions of its composer.json/package.json dependencies, deciding whether/how that should bump the module's own release version (major/minor/patch), and writing the changelog entry correctly. Trigger on requests like "check for dependency updates on this module," "is this module's composer.json out of date," "what version bump does this need," or "update the changelog for this release." This is a narrow, routine-maintenance skill — it does not do a full CI-modernization/PHPStan/README-rewrite pass (that's a separate, bigger effort) and it does not cut the actual git tag or GitHub release; it prepares the edits and hands off to a human-reviewed PR.
---

# Update Module Dependencies

Bring a Bluecadet-owned Drupal module's dependencies up to date, decide the resulting version bump for the module itself, and write the changelog entry — as a PR a human reviews, not an autonomous release.

---

## When this applies vs. when it doesn't

**Use this skill when:**

- A dev wants to check whether a module's dependencies (Drupal core, Drupal.org contrib modules, Packagist packages, npm packages) have newer versions available.
- A dev has already made changes on a branch (dependency bumps, a bug fix, etc.) and needs to figure out the right version bump and changelog entry before opening/merging a PR.

**Don't use this for:**

- A full module modernization pass (CI centralization onto `bluecadet/web-gh-actions`, PHPCS/PHPStan cleanup, README rewrite, adding test coverage). That's a much bigger, more judgment-heavy effort — see the `module-ops` project conventions if one exists in the target repo's tracking, and treat this skill's output as one small piece of it, not a replacement.
- Actually creating the git tag or GitHub release. This skill stops at "PR ready for review" — cutting the release is a separate, human decision.

## Step 1 — Inventory the module's dependencies

Read `composer.json` (`require` and `require-dev`) and `package.json` (`dependencies` and `devDependencies`) in the module's repo root (and any `modules/<submodule>/` composer.json, if present).

Classify each dependency into exactly one registry — the lookup mechanism differs per registry, see `references/registry-lookups.md`:

- **Drupal.org** — `drupal/core` and any `drupal/*` contrib package.
- **Packagist (non-Drupal.org)** — e.g. `bluecadet/bc_drupal_package_manager`, or any other `vendor/package` that isn't a `drupal/*` name.
- **npm** — everything in `package.json` (e.g. `@bluecadet/bldr`, `@bluecadet/drops`).

## Step 2 — Check latest available versions

For each dependency, fetch its latest available version using the matching pattern in `references/registry-lookups.md`. Note the current constraint (e.g. `^1.0`), the latest available version, and whether that latest version is a security release (Drupal SA, GitHub Security Advisory, or an npm audit advisory) — flag security releases explicitly, since they change urgency even when they wouldn't otherwise change the proposed version bump size.

Skip any dependency already at (or already permitting) the latest available version.

## Step 3 — Propose constraint updates

For each dependency with a real update available, propose the new constraint (e.g. `drupal/views_ajax_history: ^1.0` → `^1.8`). Keep the module's existing range style (caret vs. explicit range) rather than inventing a new one. Don't propose widening a range further than the confirmed-available version justifies, and don't touch the module's own `drupal/core`/PHP support statement unless the dev is actually asking to extend platform support — that's a bigger decision than a routine dependency bump.

Show the dev the full proposed diff before touching any file.

## Step 4 — Confirm with the dev

Ask which of the proposed updates to actually apply. Don't silently apply every available bump — some may be intentionally deferred (e.g. a major version needing its own migration work). This mirrors the module-ops precedent of treating dependency bumps as a reviewed decision, not a mechanical `composer update --with-all-dependencies`.

## Step 5 — Decide the module's version bump

The module's current version is **not** in `composer.json` (these modules don't declare a `version` key) — it's the latest git tag. Confirm it with `git tag --sort=-v:refname | head -1` (or `gh release list` if tags aren't reliably pushed).

Classify the accumulated changes since that tag — the dependency updates just confirmed, plus anything else already on the branch — using these rules:

- **MAJOR** — dropped support for a Drupal core version or PHP version the module previously supported; removed or renamed a public API, hook, or service; a breaking config schema change.
- **MINOR** — added support (new Drupal core version, widened a dependency range that unlocks new compatibility), a new feature or hook, anything backward-compatible.
- **PATCH** — a bug fix, a dependency patch-level bump, or a doc/README/CI-only change.

If the classification is genuinely ambiguous (e.g. a dependency bump that's technically a new minor upstream version but the module's own behavior is unaffected), ask the dev rather than guessing — don't silently pick the smaller or larger bump.

## Step 6 — Write the changelog entry

Append a new version-headed section to the module's README `## Changelog`, matching the existing template format exactly:

```markdown
### [X.Y.Z]

- [What changed, in past tense]
```

Flat bullets, past tense, no Keep-a-Changelog categories (Added/Fixed/Changed) — that's not this template's convention. **Never edit or "clean up" older changelog entries**, even ones that don't follow the current convention (legacy `8.x-N.x` headers, placeholder-looking headings like `2.1.x`) — only ever append.

## Step 7 — Make the edits and hand off for review

Commit the `composer.json`/`package.json` changes and the changelog entry on the current (or a new) branch. Open or update a PR whose description states the old → new version and why for each dependency bump, and the resulting module version bump and its classification (major/minor/patch) with a one-line reason. Do not create the git tag or GitHub release — leave that for the reviewer once the PR merges.
