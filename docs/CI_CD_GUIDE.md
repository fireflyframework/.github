# Framework CI/CD guide

Java development is consolidated in [Jafly](https://github.com/fireflyframework/fireflyframework-jafly). Maven resolves module ordering inside one checkout; there is one Java release train. Other framework families keep their own repositories and language-specific workflows.

## Java build and documentation

[Jafly CI](https://github.com/fireflyframework/fireflyframework-jafly/actions/workflows/ci.yml) validates every reactor project on Java 25. It checks the parent/BOM catalog, versions, preserved source history, and release tooling, then runs the full Maven build and configured tests. Docker is required for container-backed integration tests. Module changes are tested together; there is no per-repository Java release fanout.

```sh
git clone https://github.com/fireflyframework/fireflyframework-jafly.git
cd fireflyframework-jafly
./mvnw -B -ntp clean verify
```

The [Jafly documentation](https://fireflyframework.github.io/fireflyframework-jafly/) covers installation, the onboarding tutorial, architecture, and module guides. Its workflow checks and builds the documentation before deploying it to GitHub Pages.

## Repository and artifact layout

| Path | Responsibility |
| --- | --- |
| `pom.xml` | Aggregates the complete Java reactor; not a published consumer artifact |
| `build/parent/pom.xml` | Standalone `org.fireflyframework:fireflyframework-parent` with shared build and dependency management |
| `build/bom/pom.xml` | Standalone `org.fireflyframework:fireflyframework-bom` for consumers that keep another parent |
| `modules/` | Existing module coordinates and Java packages, including nested subprojects |
| `.github/workflows/` | Java CI, snapshot publication, final releases, and documentation |

All Jafly artifacts use one concrete CalVer train. Application versions remain independent. Use the parent or import the BOM; do not inherit the root aggregator. Existing published versions and original repository tags remain available.

## Final Java releases

The [release workflow](https://github.com/fireflyframework/fireflyframework-jafly/blob/main/.github/workflows/release.yml) runs for a final `vYY.MM.PP` tag or a manual dispatch naming an existing immutable final tag. It verifies that the tag, commit, and every project version agree before publication.

The workflow verifies the full reactor, deploys to GitHub Packages, checks the expected artifact inventory, publishes to Maven Central, waits for publication, verifies Central artifact bytes, and only then creates the GitHub Release and its evidence assets. Keep published versions immutable. If one registry succeeds and another fails, inspect the retained evidence before retrying; see [release recovery](https://fireflyframework.github.io/fireflyframework-jafly/releases/#failure-and-retry).

Required secrets, supplied through GitHub Actions, are `SONATYPE_USERNAME`, `SONATYPE_PASSWORD`, `GPG_PRIVATE_KEY` (base64-encoded armored key), and `GPG_PASSPHRASE`. GitHub provides `GITHUB_TOKEN` for the destination repository. Keep credential values out of source, logs, and documentation. Organization secrets limited to selected repositories must include Jafly. Check the actual publication run and downloads before using a release.

## Development snapshots

The [snapshot workflow](https://github.com/fireflyframework/fireflyframework-jafly/blob/main/.github/workflows/snapshots.yml) is dispatched on `main` or `develop`. It verifies the entire snapshot train before deploying to the destination GitHub Packages repository. Snapshot artifacts are mutable development builds; final Central releases are separate.

Build and install `26.10.17-SNAPSHOT` locally from source, or check the snapshot publication workflow and registry before relying on a remote download. The CI workflow does not publish artifacts.

## Compatibility dispatcher

This repository retains `.github/workflows/dag-orchestrator.yml` for existing callers. It accepts Jafly or an allowlisted former Java source name, then dispatches one Jafly workflow. CI uses `develop`; release mode requires an explicit existing final tag. `ORG_DISPATCH_TOKEN` must authorize Actions dispatch in Jafly.

The dispatcher reports dispatch acceptance. Follow the destination workflow at its exact ref and commit for build/publication status. It does not treat the latest unrelated green run as proof of completion. Former Java source repositories retain their history and release records; their publication workflows are retired at cutover.

## Other framework families

PyFly, LaraFly/PHP, Go, Rust, .NET, Agentic, and other independent products retain their own build/release policies. Reusable language workflows in this repository remain available for their existing callers. Do not apply Java CalVer, artifact conventions, or Maven settings to other frameworks automatically.

## Troubleshooting

- **Missing module or version drift:** run Jafly's release-tool checks and the full reactor from the repository root. Keep parent, BOM, and internal module versions aligned.
- **Container tests fail:** verify the Docker engine and the host/socket settings documented in Jafly's development guide; do not disable failing tests to qualify a release.
- **Publishing credentials unavailable:** check secret visibility for the destination repository using secret names only. CI does not require Central signing credentials.
- **Partial registry publication:** preserve existing immutable versions and examine the exact release manifest and workflow logs before recovery.
- **Old CLI still clones many repositories:** install the current CLI release; source changes on `main` alone do not replace an installed binary. Existing old checkout directories are preserved.

See [CI status](CI_STATUS.md), [module catalog](MODULE_CATALOG.md), and the [historical changelog](CI_CD_CHANGELOG.md).
