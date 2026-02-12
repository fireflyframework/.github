# CI/CD Changelog

History of CI/CD changes, fixes, and improvements across the Firefly Framework.

---

## 26.02.03 — CI/CD Overhaul

Released: February 2026

### Issues Fixed (from 26.02.02 release)

**1. Race conditions — simultaneous repo releases**
All 38 repos were dispatched simultaneously by the DAG orchestrator. Downstream repos tried to resolve parent POMs that hadn't been published yet, causing cascading build failures.
- **Fix:** Redesigned `dag-orchestrator.yml` for layer-by-layer dispatch. Each layer waits for GitHub Packages to publish before the next layer starts.

**2. Multi-module 409 cascade**
When a multi-module repo's parent POM got a 409 (Conflict), Maven's reactor banned all child modules from deploying. 14 sub-modules across 4 repos failed to publish.
- **Fix:** Two-phase deploy strategy in `java-release.yml` — parent POM first (`-N`), then child modules (`-pl '!.'`).

**3. Duplicate workflow runs**
Both tag-push events and the DAG orchestrator triggered `release.yml`, creating redundant runs.
- **Fix:** Removed DAG dispatch from `java-release.yml` and `java-ci.yml`. CI cascade removed entirely — only releases cascade via the DAG orchestrator.

**4. Maven Central silent failures**
`waitUntil: uploaded` in the parent POM caused the deploy step to return success before Sonatype validation completed. 5 artifacts failed validation and never appeared on Maven Central, but CI showed green.
- **Fix:** Changed `waitUntil` to `published` in both `fireflyframework-parent/pom.xml` and `fireflyframework-bom/pom.xml`.

**5. Broken CI cascade — missing `secrets: inherit`**
35 of 38 Java repos lacked `secrets: inherit` in their `ci.yml`, so `ORG_DISPATCH_TOKEN` and other org secrets were not passed through to shared workflows.
- **Fix:** Added `secrets: inherit` and `permissions` block to all 38 Java repo `ci.yml` files.

**6. Failed builds not retried by CLI**
The `flywork build` command recorded the SHA even for failed builds, so `DetectChanges` would not pick them up on retry.
- **Fix:** `LastSHA()` now returns empty string for repos with `status: "failed"`.

### Improvements

- Added concurrency groups to both `java-ci.yml` and `java-release.yml` to prevent duplicate runs
- Added `main` to CI push branches on all repos (previously only `develop` was monitored)
- Added `paths-ignore` for docs/markdown files to avoid unnecessary CI runs
- Added Maven Central pre-check to skip deploy if version is already published
- Strict error matching in deploy steps — only 409 and explicit "already exists" messages are acceptable
- Post-release now requires BOTH GitHub Packages and Maven Central to succeed
- Added `--layers` flag to CLI `dag affected` command for layer-grouped output
- Added `<name>` and `<description>` to 12 pom.xml files for Maven Central compliance
- Removed `continue-on-error: true` from pyright step in `python-ci.yml`
- Created CI workflow for `flyfront` (Angular/NX)
