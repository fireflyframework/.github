# CI/CD Configuration Guide

This guide covers the CI/CD architecture for the Firefly Framework, including shared workflows, per-repo configuration, GitHub Packages, the DAG orchestrator, and version management.

---

## Architecture Overview

Firefly Framework uses a **centralized shared-workflow model**:

- **Shared workflows** live in the `.github` repository under `.github/workflows/`
- **Per-repo caller workflows** in each repository reference the shared workflows via `workflow_call`
- **DAG orchestrator** coordinates cross-repo builds when a dependency changes
- **CLI tooling** (`flywork`) provides local build/publish/version commands that mirror CI behavior

```
.github repo (shared workflows)
├── java-ci.yml          ← called by all Java repos
├── java-release.yml     ← called by all Java repos on tag push
├── go-ci.yml            ← called by Go repos (CLI)
├── go-release.yml       ← called by Go repos (CLI)
├── python-ci.yml        ← called by Python repos (GenAI)
├── python-release.yml   ← called by Python repos (GenAI)
└── dag-orchestrator.yml ← coordinates cross-repo builds
```

Each framework repository contains two thin caller workflows:
- `ci.yml` — triggers on push/PR to `develop`, calls the shared CI workflow
- `release.yml` — triggers on tag push or `workflow_dispatch` on `main`, calls the shared release workflow

---

## Shared Workflows

### `java-ci.yml`

Runs `mvn verify` (or custom goals) with GitHub Packages configured for dependency resolution.

**Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `java-version` | `25` | JDK version to use |
| `maven-goals` | `verify` | Maven goals to execute |
| `maven-args` | `""` | Additional Maven arguments |

**What it does:**

1. Checks out the repository
2. Sets up the JDK with Temurin distribution and Maven cache
3. Writes `~/.m2/settings.xml` with GitHub Packages server credentials
4. Runs Maven with the specified goals
5. Uploads Surefire/Failsafe test reports as artifacts (7-day retention)

### `java-release.yml`

Deploys Maven artifacts to GitHub Packages and creates a GitHub Release.

**Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `java-version` | `25` | JDK version to use |

**What it does:**

1. Checks out the repository
2. Sets up the JDK and configures GitHub Packages credentials
3. Runs `mvn deploy -P release -DskipTests` to publish artifacts
4. Extracts the project version from the POM
5. Creates a GitHub Release tagged `v<version>` with auto-generated release notes

### `go-ci.yml`

Runs `go vet`, tests with race detection and coverage, and a build check.

**Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `go-version` | `1.25` | Go version to use |

### `go-release.yml`

Cross-compiles for 6 platforms (darwin/linux/windows x amd64/arm64) and uploads release assets.

**Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `go-version` | `1.25` | Go version to use |
| `binary-name` | (required) | Name of the binary to build |

### `python-ci.yml`

Runs ruff linting, pyright type checking, and pytest with coverage.

**Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `python-version` | `3.13` | Python version to use |

### `python-release.yml`

Builds the Python package with `uv build` and creates a GitHub Release with wheel and sdist assets.

---

## Per-Repo Workflow Setup

Each Java repository needs two workflow files in `.github/workflows/`:

### `ci.yml`

```yaml
name: CI

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop]

jobs:
  ci:
    uses: fireflyframework/.github/.github/workflows/java-ci.yml@main
    secrets: inherit
```

### `release.yml`

```yaml
name: Release

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  release:
    uses: fireflyframework/.github/.github/workflows/java-release.yml@main
    secrets: inherit
    permissions:
      contents: write
      packages: write
```

For Go repositories, replace `java-ci.yml` / `java-release.yml` with `go-ci.yml` / `go-release.yml` and add the `binary-name` input to the release workflow.

For Python repositories, use `python-ci.yml` / `python-release.yml`.

---

## GitHub Packages

### How It Works

All Java artifacts are published to GitHub Packages under the `fireflyframework` organization. Each repository publishes to its own package namespace:

```
https://maven.pkg.github.com/fireflyframework/<repo-name>
```

### Maven Settings

Both CI and local builds need a `~/.m2/settings.xml` with the GitHub Packages server:

```xml
<settings>
  <servers>
    <server>
      <id>github</id>
      <username>${env.GITHUB_ACTOR}</username>
      <password>${env.GITHUB_TOKEN}</password>
    </server>
  </servers>
  <profiles>
    <profile>
      <id>github-packages</id>
      <repositories>
        <repository>
          <id>github</id>
          <url>https://maven.pkg.github.com/fireflyframework/fireflyframework-parent</url>
          <snapshots><enabled>true</enabled></snapshots>
          <releases><enabled>true</enabled></releases>
        </repository>
      </repositories>
    </profile>
  </profiles>
  <activeProfiles>
    <activeProfile>github-packages</activeProfile>
  </activeProfiles>
</settings>
```

In CI, the shared workflows write this automatically using `GITHUB_TOKEN`. Locally, the `flywork publish` command manages it via `publish.EnsureSettingsXML()`.

### Publishing

Artifacts are deployed with:

```bash
mvn deploy -P release -DskipTests \
  -DaltDeploymentRepository=github::https://maven.pkg.github.com/fireflyframework/<repo-name>
```

The `-DaltDeploymentRepository` flag overrides the `<distributionManagement>` in the POM to point to the correct per-repo package URL.

### Consuming Dependencies

All repositories inherit from `fireflyframework-parent`, which includes the GitHub Packages repository in its `<repositories>` section. As long as `~/.m2/settings.xml` has the server credentials, Maven will resolve dependencies from GitHub Packages automatically.

---

## DAG Orchestrator

The `dag-orchestrator.yml` workflow coordinates cross-repo builds when a change in one repository affects downstream dependents.

### How It Works

1. **Trigger** — A repo's CI workflow (or manual dispatch) triggers the orchestrator with `trigger-repo` input
2. **Plan** — The orchestrator checks out the CLI, builds it, and runs `flywork dag affected --from <repo> --json` to compute the transitive closure of affected repos
3. **Build** — For each affected repo, it dispatches that repo's CI workflow via the GitHub API

### Manual Trigger

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-cache \
  -R fireflyframework/.github
```

To rebuild everything:

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-parent \
  -f build-all=true \
  -R fireflyframework/.github
```

---

## Version Management

### CalVer Scheme

Firefly Framework uses **Calendar Versioning** with the format `YY.MM.PP`:

- `YY` — Two-digit year (e.g., `26` for 2026)
- `MM` — Two-digit month (e.g., `01` for January)
- `PP` — Two-digit patch number, starting at `01` and incrementing within a month

Example progression: `26.01.01` → `26.01.02` → `26.02.01`

### Version Commands

```bash
flywork fwversion show        # show current versions across all repos
flywork fwversion bump --auto # auto-compute next CalVer and update all POMs
flywork fwversion check       # validate consistency
flywork fwversion families    # show release history
```

### Release Workflow

A typical release cycle:

1. **Bump versions** — `flywork fwversion bump --auto --push`
   - Updates all `pom.xml` files across every repo
   - Commits and tags each repo with `v<version>`
   - Pushes commits and tags to remote
2. **CI triggers** — Tag push triggers `release.yml` in each repo
3. **Artifacts published** — Maven deploy to GitHub Packages
4. **GitHub Releases created** — With auto-generated release notes
5. **Family recorded** — Version family snapshot saved with module SHAs

### Manual Release Trigger

If tag-triggered releases need re-running (e.g., after a workflow fix):

```bash
# Single repo
gh workflow run release.yml -R fireflyframework/fireflyframework-utils

# All repos (use the CLI or script)
flywork publish --all
```

---

## Troubleshooting

### Missing Dependencies (Could not resolve artifact)

Maven cannot find a dependency in GitHub Packages. Causes:

- The dependency repo has not been published yet — check the DAG layer order and publish upstream repos first
- `~/.m2/settings.xml` is missing or has wrong credentials — re-run `flywork publish` to auto-fix, or manually update
- The `GITHUB_TOKEN` lacks `read:packages` scope

### 409 Conflict on Deploy

GitHub Packages returns HTTP 409 when you try to publish a version that already exists. Solutions:

- Bump the version with `flywork fwversion bump --auto` before publishing
- Use `-DskipExisting=true` (Maven 4+) or catch the error in the workflow

### Tag Issues (Release Step Fails)

The `softprops/action-gh-release` action requires a tag. When triggered via `workflow_dispatch`, there is no tag in `GITHUB_REF`. The shared `java-release.yml` provides an explicit `tag_name: v${{ steps.version.outputs.version }}` — the action creates the tag if it does not exist.

If releases are missing, re-trigger via:

```bash
gh workflow run release.yml -R fireflyframework/<repo-name>
```

### Build Order Issues

If a downstream repo fails because a dependency is not in `.m2`:

1. Check the DAG layer: `flywork dag layers`
2. Ensure all upstream repos in earlier layers are built first
3. For local builds: `flywork build --all` rebuilds everything in correct order
4. For CI: trigger the DAG orchestrator with `build-all=true`

### CI Permissions

Shared workflows require these permissions in the caller workflow:

- **CI**: `packages: read` (to resolve dependencies from GitHub Packages)
- **Release**: `contents: write` (to create tags and releases) + `packages: write` (to publish artifacts)

Ensure `secrets: inherit` is set in the caller workflow so the shared workflow receives `GITHUB_TOKEN`.
