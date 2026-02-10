# CI/CD Configuration Guide

A comprehensive guide to the Firefly Framework CI/CD pipeline: how it works, how to configure it for new repositories, and how to troubleshoot common issues.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [How Shared Workflows Work](#how-shared-workflows-work)
3. [Shared Workflow Reference](#shared-workflow-reference)
4. [Setting Up CI/CD for a New Repository](#setting-up-cicd-for-a-new-repository)
5. [GitHub Packages](#github-packages)
6. [DAG Orchestrator](#dag-orchestrator)
7. [Release Process](#release-process)
8. [Version Management](#version-management)
9. [Branch Strategy](#branch-strategy)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

Firefly Framework uses a **centralized shared-workflow model**. Instead of duplicating CI/CD logic across 40 repositories, all workflow logic lives in a single place and every repo references it.

### The Three Components

```
┌──────────────────────────────────────────────────────┐
│                  .github repository                   │
│                                                       │
│   .github/workflows/                                  │
│   ├── java-ci.yml          (shared CI for Java)       │
│   ├── java-release.yml     (shared release for Java)  │
│   ├── go-ci.yml            (shared CI for Go)         │
│   ├── go-release.yml       (shared release for Go)    │
│   ├── python-ci.yml        (shared CI for Python)     │
│   ├── python-release.yml   (shared release for Python)│
│   └── dag-orchestrator.yml (cross-repo coordinator)   │
└──────────────────────────────────────────────────────┘
                          ▲
                          │ workflow_call
                          │
┌──────────────────────────────────────────────────────┐
│              Each framework repository                │
│                                                       │
│   .github/workflows/                                  │
│   ├── ci.yml       → calls shared CI workflow         │
│   └── release.yml  → calls shared release workflow    │
└──────────────────────────────────────────────────────┘
                          ▲
                          │ triggers
                          │
┌──────────────────────────────────────────────────────┐
│                   Trigger Events                      │
│                                                       │
│   • Push to develop         → ci.yml                  │
│   • Pull request            → ci.yml                  │
│   • Tag push (v*)           → release.yml             │
│   • Manual workflow_dispatch → release.yml             │
└──────────────────────────────────────────────────────┘
```

### Why This Design?

- **Single source of truth** -- Update a workflow once in `.github` and all 40 repos get the change immediately
- **Consistency** -- Every repo uses the same build steps, the same JDK version, the same Maven configuration
- **Minimal per-repo config** -- Each repo only needs two small YAML files (5-15 lines each)
- **Easy to audit** -- All CI/CD logic is in one place

---

## How Shared Workflows Work

GitHub Actions supports **reusable workflows** via the `workflow_call` trigger. Here is how it works step by step:

### Step 1: The Shared Workflow (in `.github` repo)

A shared workflow declares `workflow_call` as its trigger and defines inputs:

```yaml
# .github/workflows/java-ci.yml (in the .github repo)
name: Java CI

on:
  workflow_call:          # <-- This makes it callable from other repos
    inputs:
      java-version:
        type: string
        default: '25'
```

### Step 2: The Caller Workflow (in each repo)

Each repo has a thin workflow that references the shared one:

```yaml
# .github/workflows/ci.yml (in any Java repo)
name: CI

on:
  push:
    branches: [develop]

jobs:
  ci:
    uses: fireflyframework/.github/.github/workflows/java-ci.yml@main  # <-- References shared workflow
    secrets: inherit                                                     # <-- Passes GITHUB_TOKEN through
```

### Step 3: Execution

When a push happens on `develop`:
1. GitHub reads the repo's `ci.yml`
2. Sees the `uses:` reference to the shared workflow
3. Fetches `java-ci.yml` from the `.github` repo's `main` branch
4. Executes the shared workflow's steps in the context of the calling repo

The `@main` suffix means it always uses the latest version from the `main` branch of the `.github` repo. This is how a single workflow update propagates to all repos immediately.

### Important: `secrets: inherit`

The `secrets: inherit` line is critical. Without it, the shared workflow cannot access `GITHUB_TOKEN`, which means it cannot:
- Resolve dependencies from GitHub Packages
- Publish artifacts
- Create releases

---

## Shared Workflow Reference

### `java-ci.yml` -- Java Continuous Integration

**Purpose:** Compile, test, and validate Java code.

**Inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `java-version` | string | `25` | JDK version (Temurin distribution) |
| `maven-goals` | string | `verify` | Maven goals to run |
| `maven-args` | string | `""` | Extra Maven arguments |

**Steps (in order):**

1. **Checkout** -- Clones the repository
2. **Set up JDK** -- Installs the Temurin JDK and enables Maven dependency caching
3. **Configure GitHub Packages** -- Writes `~/.m2/settings.xml` with the `GITHUB_TOKEN` so Maven can download framework dependencies from GitHub Packages
4. **Build with Maven** -- Runs `mvn -B verify` (or the custom goals provided). The `-B` flag runs Maven in batch (non-interactive) mode
5. **Upload test reports** -- Saves Surefire and Failsafe test reports as GitHub Actions artifacts with 7-day retention. Runs even if the build fails (`if: always()`)

**Permissions required:** `packages: read` (for dependency resolution)

### `java-release.yml` -- Java Release & Publish

**Purpose:** Deploy Maven artifacts to GitHub Packages and create a GitHub Release.

**Inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `java-version` | string | `25` | JDK version (Temurin distribution) |

**Steps (in order):**

1. **Checkout** -- Clones the repository
2. **Set up JDK** -- Installs the Temurin JDK with Maven cache
3. **Configure GitHub Packages** -- Writes `~/.m2/settings.xml` with write credentials
4. **Deploy to GitHub Packages** -- Runs `mvn deploy -P release -DskipTests`. The `-DaltDeploymentRepository` flag directs artifacts to the correct per-repo package URL. If the version already exists (409 Conflict), the step logs a warning and continues without failing
5. **Extract version** -- Reads the project version from the POM using `mvn help:evaluate`
6. **Create GitHub Release** -- Uses `softprops/action-gh-release@v2` with an explicit `tag_name: v<version>`. The action creates the git tag if it does not already exist (important for `workflow_dispatch` triggers where no tag is in `GITHUB_REF`)

**Permissions required:** `contents: write` + `packages: write`

**409 Conflict handling:** GitHub Packages does not allow overwriting an existing version. When the workflow re-runs for a version that was already published, the deploy step detects the 409 error and treats it as a warning. This allows the GitHub Release creation step to still execute, which is the typical reason for re-running the workflow.

### `go-ci.yml` -- Go Continuous Integration

**Purpose:** Vet, test, and build Go code.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `go-version` | string | `1.25` | Go version |

**Steps:** `go vet ./...` → `go test -v -race -coverprofile=coverage.out ./...` → `go build -o /dev/null .`

### `go-release.yml` -- Go Release

**Purpose:** Cross-compile for 6 platforms and upload binaries as GitHub Release assets.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `go-version` | string | `1.25` | Go version |
| `binary-name` | string | (required) | Name of the binary |

**Platforms:** darwin/amd64, darwin/arm64, linux/amd64, linux/arm64, windows/amd64, windows/arm64

**Steps:** Build with ldflags (version + commit) → Package as `.tar.gz` (Unix) or `.zip` (Windows) → Upload to GitHub Release

### `python-ci.yml` -- Python Continuous Integration

**Purpose:** Lint, type-check, and test Python code.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.13` | Python version |

**Steps:** Install `uv` → Install Python → `uv sync --all-extras` → `ruff check` + `ruff format --check` → `pyright` → `pytest --cov`

### `python-release.yml` -- Python Release

**Purpose:** Build Python package and create a GitHub Release with wheel and sdist assets.

**Steps:** Install `uv` → `uv build` → Extract version → Create GitHub Release with `tag_name: v<version>` and upload `dist/*.whl` + `dist/*.tar.gz`

### `dag-orchestrator.yml` -- Cross-Repo Build Coordinator

**Purpose:** When a change in one repo affects downstream dependents, trigger their CI workflows.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `trigger-repo` | string | yes | The repo that changed |
| `build-all` | boolean | no | Build all repos regardless |

**How it works:**
1. Checks out the CLI repo and builds the `flywork` binary
2. Runs `flywork dag affected --from <trigger-repo> --json` to compute which downstream repos are affected
3. For each affected repo, dispatches its CI workflow via the GitHub API

---

## Setting Up CI/CD for a New Repository

Follow these steps to add CI/CD to a new Firefly Framework repository.

### Step 1: Create the Repository

Create the repository under the `fireflyframework` organization on GitHub. Initialize it with a `develop` branch as the default working branch.

### Step 2: Add the CI Workflow

Create `.github/workflows/ci.yml` in the new repository:

**For Java repositories:**

```yaml
name: CI

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop, main]

jobs:
  ci:
    uses: fireflyframework/.github/.github/workflows/java-ci.yml@main
    secrets: inherit
```

**For Go repositories:**

```yaml
name: CI

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop, main]

jobs:
  ci:
    uses: fireflyframework/.github/.github/workflows/go-ci.yml@main
    secrets: inherit
```

**For Python repositories:**

```yaml
name: CI

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop, main]

jobs:
  lint-and-test:
    uses: fireflyframework/.github/.github/workflows/python-ci.yml@main
    secrets: inherit
```

### Step 3: Add the Release Workflow

Create `.github/workflows/release.yml`:

**For Java repositories:**

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

**For Go repositories:**

```yaml
name: Release

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  release:
    uses: fireflyframework/.github/.github/workflows/go-release.yml@main
    secrets: inherit
    permissions:
      contents: write
    with:
      binary-name: your-binary-name
```

**For Python repositories:**

```yaml
name: Release

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  release:
    uses: fireflyframework/.github/.github/workflows/python-release.yml@main
    permissions:
      contents: write
```

### Step 4: Verify

1. Push a commit to `develop` -- the CI workflow should trigger
2. Check the Actions tab on GitHub to confirm it passes
3. To test the release workflow, either push a tag (`git tag v0.0.1 && git push --tags`) or use the **Run workflow** button in the Actions tab

### Step 5: Add to the DAG (Java repos only)

If the new repo is a Java module that other modules depend on (or that depends on other modules), update the DAG definition in the CLI:

1. Edit `internal/dag/graph.go` in the `fireflyframework-cli` repo
2. Add the new repo and its dependencies to the `FrameworkGraph()` function
3. Run `flywork dag layers` to verify the repo appears in the correct layer

---

## GitHub Packages

### What Is GitHub Packages?

GitHub Packages is a package registry hosted by GitHub. Firefly Framework publishes all Maven (Java), Go, and Python artifacts there. It works like Maven Central but is tied to the GitHub organization.

**Key difference from Maven Central:** GitHub Packages requires authentication even for reading public packages. This means every developer and every CI job needs credentials configured.

### How Maven Artifacts Are Published

When the release workflow runs, it executes:

```bash
mvn -B deploy -P release -DskipTests \
  -DaltDeploymentRepository=github::https://maven.pkg.github.com/fireflyframework/<repo-name>
```

This command:
- `-B` -- Runs Maven in batch mode (no interactive prompts)
- `deploy` -- Compiles, tests (skipped), packages, and uploads artifacts
- `-P release` -- Activates the `release` Maven profile (if defined in the POM)
- `-DskipTests` -- Skips tests since CI already validated them
- `-DaltDeploymentRepository` -- Overrides `<distributionManagement>` to point to the correct per-repo GitHub Packages URL

### How Maven Artifacts Are Consumed

All Firefly repositories inherit from `fireflyframework-parent`, which configures the GitHub Packages repository. When Maven needs a dependency like `fireflyframework-utils`, it:

1. Checks the local `~/.m2` cache
2. Checks Maven Central
3. Checks GitHub Packages at `https://maven.pkg.github.com/fireflyframework/fireflyframework-parent`

GitHub Packages resolves **all** artifacts under the `fireflyframework` organization from a single repository URL.

### Maven Settings for CI

The shared workflows automatically write `~/.m2/settings.xml` during each run:

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

The `GITHUB_TOKEN` is automatically available in every GitHub Actions workflow. The `secrets: inherit` line in caller workflows passes it to the shared workflow.

### Maven Settings for Local Development

For local builds, developers need to configure `~/.m2/settings.xml` manually with a Personal Access Token. See the [Getting Started Guide](GETTING_STARTED.md) for detailed instructions.

### Version Immutability

GitHub Packages does **not** allow overwriting an existing version. Once `26.01.01` is published, you cannot publish `26.01.01` again for the same artifact. Attempting to do so returns HTTP 409 Conflict.

This means:
- Every release must use a new version number
- If you need to re-publish, bump the version first with `flywork fwversion bump --auto`
- The release workflow handles 409s gracefully by logging a warning and continuing to the GitHub Release step

---

## DAG Orchestrator

### The Problem

Firefly Framework has 38 Java repositories with real Maven dependency relationships. When `fireflyframework-utils` changes, every repo that depends on it (directly or transitively) needs to be rebuilt. Doing this manually is impractical.

### The Solution

The `dag-orchestrator.yml` workflow automates cross-repo builds:

1. **Input** -- You tell it which repo changed (`trigger-repo`)
2. **Planning** -- It builds the CLI and runs `flywork dag affected --from <repo> --json` to compute the full transitive closure of affected repos
3. **Execution** -- For each affected repo, it dispatches that repo's CI workflow via the GitHub API

### Usage

**Trigger after a change to a specific repo:**

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-cache \
  -R fireflyframework/.github
```

**Rebuild everything (full DAG):**

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-parent \
  -f build-all=true \
  -R fireflyframework/.github
```

### DAG Layers

The framework repositories are organized into 6 dependency layers. Repos in the same layer have no dependencies on each other and can be built in parallel. Repos in layer N depend only on repos in layers 0 through N-1.

| Layer | Count | Repositories |
|-------|-------|-------------|
| 0 | 1 | parent |
| 1 | 11 | bom, utils, cache, eda, ecm, idp, config-server, client, validators, plugins, transactional-engine |
| 2 | 11 | r2dbc, cqrs, web, workflow, ecm-esignature-adobe-sign, ecm-esignature-docusign, ecm-esignature-logalty, ecm-storage-aws, ecm-storage-azure, idp-aws-cognito, idp-keycloak |
| 3 | 6 | eventsourcing, application, idp-internal-db, core, domain, data |
| 4 | 5 | webhooks, callbacks, notifications, rule-engine, backoffice |
| 5 | 4 | notifications-firebase, notifications-resend, notifications-sendgrid, notifications-twilio |

You can always get the latest DAG layout with:

```bash
flywork dag layers
```

---

## Release Process

### Automated Release (Recommended)

The standard release workflow:

```bash
# 1. Bump version across all repos, commit, tag, and push
flywork fwversion bump --auto --commit --tag --push

# 2. Tag pushes automatically trigger release.yml in each repo
#    This publishes Maven artifacts and creates GitHub Releases

# 3. Verify everything succeeded
flywork fwversion check
```

### What Happens During a Release

For each Java repository:

1. The tag push (e.g., `v26.02.01`) triggers the repo's `release.yml`
2. The repo's `release.yml` calls the shared `java-release.yml`
3. The shared workflow:
   - Checks out the code at the tagged commit
   - Sets up the JDK and configures Maven
   - Runs `mvn deploy` to publish the artifact to GitHub Packages
   - Extracts the version from the POM
   - Creates a GitHub Release with auto-generated release notes

### Manual Release Trigger

If you need to re-run releases (e.g., after fixing a workflow issue), you can trigger them manually:

**Single repo:**

```bash
gh workflow run release.yml -R fireflyframework/fireflyframework-utils
```

**All repos (layer by layer):**

```bash
# Layer 0
gh workflow run release.yml -R fireflyframework/fireflyframework-parent

# Wait for it to complete, then Layer 1
gh workflow run release.yml -R fireflyframework/fireflyframework-bom
gh workflow run release.yml -R fireflyframework/fireflyframework-utils
# ... etc.
```

Or use the CLI to publish all locally:

```bash
export GITHUB_TOKEN=ghp_your_token
flywork publish --all
```

### Checking Release Status

**Check if a repo has a GitHub Release:**

```bash
gh release list -R fireflyframework/fireflyframework-utils -L 1
```

**Check the latest release workflow run:**

```bash
gh run list -R fireflyframework/fireflyframework-utils -w release.yml -L 1
```

**Check all repos at once:**

```bash
for repo in fireflyframework-parent fireflyframework-bom fireflyframework-utils; do
  echo -n "$repo: "
  gh release list -R "fireflyframework/$repo" -L 1 --json tagName -q '.[0].tagName' 2>/dev/null || echo "none"
done
```

---

## Version Management

### CalVer Scheme

Firefly Framework uses **Calendar Versioning** (CalVer) with the format `YY.MM.PP`:

| Component | Meaning | Example |
|-----------|---------|---------|
| `YY` | Two-digit year | `26` for 2026 |
| `MM` | Two-digit month | `01` for January |
| `PP` | Two-digit patch | `01`, `02`, etc. |

**Version progression examples:**
- First release in January 2026: `26.01.01`
- Second release in January 2026: `26.01.02`
- First release in February 2026: `26.02.01`

### Version Commands

The CLI provides comprehensive version management:

```bash
# Show current version status across all repos
flywork fwversion show

# Show detailed per-repo status
flywork fwversion show -v

# Validate version consistency (are all repos on the same version?)
flywork fwversion check

# Bump to next CalVer (auto-computed)
flywork fwversion bump --auto

# Bump, commit, tag, and push in one command
flywork fwversion bump --auto --commit --tag --push

# Preview what would change (no modifications)
flywork fwversion bump --auto --dry-run

# Bump and also run mvn install after
flywork fwversion bump --auto --install

# View release history
flywork fwversion families
```

### How Version Bumping Works

When you run `flywork fwversion bump --auto --commit --tag --push`:

1. **Detect current version** -- Reads the version from the parent POM
2. **Compute next version** -- Increments the patch number, or rolls to the next month if the current month has changed
3. **Update all POMs** -- Finds every `pom.xml` across all 38 repos and updates the parent version and any cross-module dependency versions
4. **Commit** -- Creates a git commit in each repo with the message `chore: bump version to <new-version>`
5. **Tag** -- Creates a `v<new-version>` tag in each repo
6. **Push** -- Pushes commits and tags to the remote
7. **Record family** -- Saves a snapshot of all module SHAs for this version

---

## Branch Strategy

All Firefly Framework repositories follow a two-branch model:

| Branch | Purpose |
|--------|---------|
| `develop` | Active development. CI runs on every push. |
| `main` | Stable releases. Updated by merging `develop` or force-push. |

### Workflow

1. All development happens on `develop` (or feature branches merged into `develop`)
2. CI runs automatically on every push to `develop`
3. When ready to release:
   - Merge `develop` into `main` (or force `main` to match `develop`)
   - Push tags for the release
   - Release workflows trigger automatically

### Tag Naming

Tags follow the pattern `v<version>`, e.g., `v26.01.01`. The release workflow uses this tag to:
- Identify which commit to build
- Name the GitHub Release
- Set the `tag_name` for the GitHub Release

---

## Troubleshooting

### Problem: "Could not resolve artifact"

**Symptom:** Maven fails with `Could not find artifact org.fireflyframework:fireflyframework-xyz:jar:26.01.01`

**Causes and fixes:**

1. **Missing `settings.xml`** -- Maven does not know how to authenticate with GitHub Packages
   - Fix: Create or update `~/.m2/settings.xml` (see [Getting Started Guide](GETTING_STARTED.md))

2. **Wrong token scope** -- Your PAT does not have `read:packages`
   - Fix: Go to GitHub Settings > Tokens and add the `read:packages` scope

3. **Artifact not published yet** -- The dependency was never deployed to GitHub Packages
   - Fix: Check if the package exists at `https://github.com/fireflyframework/<repo-name>/packages`
   - Fix: Trigger the release workflow: `gh workflow run release.yml -R fireflyframework/<repo-name>`

4. **Wrong version** -- You are requesting a version that does not exist
   - Fix: Check available versions in the package registry
   - Fix: Use `mvn -U` to force Maven to re-check remote repositories

### Problem: 409 Conflict on Deploy

**Symptom:** `status code: 409, reason phrase: Conflict`

**Cause:** GitHub Packages does not allow overwriting existing versions. The artifact was already published.

**What the workflow does:** The shared `java-release.yml` detects 409 errors and treats them as warnings. The workflow continues to the GitHub Release creation step, which is typically the reason for re-running.

**If you need to publish new content at the same version:** This is not possible with GitHub Packages. You must bump the version: `flywork fwversion bump --auto --push`

### Problem: "GitHub Releases requires a tag"

**Symptom:** The `softprops/action-gh-release` step fails with this error.

**Cause:** This happens when the release workflow is triggered via `workflow_dispatch` and the `tag_name` input is missing. Without a tag in `GITHUB_REF` and no explicit `tag_name`, the action does not know what tag to use.

**Fix:** The shared `java-release.yml` and `python-release.yml` both set `tag_name: v${{ steps.version.outputs.version }}` explicitly. If you see this error, make sure your repo's `release.yml` references the shared workflow from `@main` (not an older commit).

### Problem: CI Fails with "Permission denied" or "Resource not accessible"

**Symptom:** The workflow cannot access packages, create releases, or push tags.

**Causes and fixes:**

1. **Missing `secrets: inherit`** in the caller workflow
   - Fix: Add `secrets: inherit` to the job that calls the shared workflow

2. **Missing permissions** in the caller workflow
   - Fix: Add the required permissions block:
     ```yaml
     permissions:
       contents: write    # for creating releases and tags
       packages: write    # for publishing artifacts
     ```

3. **Organization-level restrictions** -- The org may restrict workflow permissions
   - Fix: Go to Organization Settings > Actions > General > Workflow permissions and ensure "Read and write permissions" is selected

### Problem: Build Order Issues

**Symptom:** A downstream repo fails because its dependency is not in `.m2` or GitHub Packages.

**Cause:** The dependency was not built/published before the downstream repo.

**Fixes:**

1. **Check the DAG layer**: `flywork dag layers` -- the dependency must be in an earlier layer
2. **For local builds**: `flywork build --all` rebuilds everything in correct order
3. **For CI**: Trigger the DAG orchestrator with `build-all=true`
4. **For releases**: Trigger repos layer by layer (0, then 1, then 2, etc.)

### Problem: GenAI CI Fails with Lint Errors

**Symptom:** The `ruff check` or `ruff format --check` step fails.

**Fix:** Run the auto-fixer locally:

```bash
cd fireflyframework-genai
uv run ruff check . --fix
uv run ruff format .
```

Then commit and push the fixes.

### Problem: Tests Pass Locally but Fail in CI

**Possible causes:**

1. **Different Java version** -- CI uses Java 25 by default. Check with `java -version`
2. **Missing test dependencies** -- CI resolves from GitHub Packages, not your local `.m2`
3. **Testcontainers** -- Some tests require Docker. Verify Docker is available in the CI runner
4. **Environment variables** -- CI may not have the same env vars as your local machine

### Problem: Release Workflow Succeeds but No GitHub Release Appears

**Possible causes:**

1. The `permissions: contents: write` block is missing from the caller workflow
2. The release was created but marked as "draft" -- check the Releases page on GitHub
3. The workflow completed but the gh-release step was skipped due to a prior step failure

**Debug:** Check the workflow run logs in the Actions tab. Look at each step's output.
