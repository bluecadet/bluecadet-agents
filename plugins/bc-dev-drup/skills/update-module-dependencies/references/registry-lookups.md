# Registry lookup patterns

Three different dependency sources show up in a Bluecadet Drupal module's `composer.json`/`package.json`. Each needs a different API to find the latest version — Packagist does not carry Drupal.org contrib releases.

## Drupal.org (core + contrib)

Applies to `drupal/core` and any `drupal/<name>` package.

- Release history (XML): `https://updates.drupal.org/release-history/<project>/current`
  Example: `https://updates.drupal.org/release-history/views_ajax_history/current` — verified working 2026-09-15, returns a `<releases>` list, each `<release>` carrying `<version>` in Drupal's native tag format (e.g. `8.x-1.8`).
  Take the newest `<release>` with `<status>published</status>` and no `-dev`/`-alpha`/`-beta`/`-rc` suffix, unless the module already tracks a pre-release.

  Do **not** use `packages.drupal.org/8/packages/<project>.json` — that per-project path 404s (confirmed 2026-09-15, redirects to a dead drupal.org URL). If a Composer-normalized version number is needed (e.g. to compare against a `composer.json` constraint like `^1.8`), convert the Drupal tag yourself: `8.x-1.8` → `1.8.0`. This matches what these modules' composer.json constraints already assume.

Cross-check <https://www.drupal.org/security> for the same project name if a release looks like a security fix — the release notes usually say so directly ("Security update").

## Packagist (non-Drupal.org packages)

Applies to `vendor/package` names that aren't `drupal/*` — e.g. `bluecadet/bc_drupal_package_manager`.

- `https://repo.packagist.org/p2/<vendor>/<package>.json`

The response's `packages.<vendor>/<package>` array is newest-first; take the first non-dev entry.

## npm

Applies to everything in `package.json` — e.g. `@bluecadet/bldr`, `@bluecadet/drops`.

- `https://registry.npmjs.org/<package>` (URL-encode the `/` in scoped names as `%2f`, or just fetch `https://registry.npmjs.org/@bluecadet/bldr` directly — npm's registry accepts the unescaped form too)

The `dist-tags.latest` field is the current stable release. Check `npm audit` output (or the GitHub Security Advisory database for the package) if a bump looks security-motivated.
