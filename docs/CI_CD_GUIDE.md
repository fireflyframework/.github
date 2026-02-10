# CI/CD Configuration Guide

Everything you need to know about how Firefly Framework builds, tests, publishes, and releases its 40 repositories — and how to set it up for new ones.

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [Why Shared Workflows?](#why-shared-workflows)
3. [How Reusable Workflows Actually Work](#how-reusable-workflows-actually-work)
4. [Shared Workflow Reference](#shared-workflow-reference)
5. [The Automatic Cascade — How a Single Commit Rebuilds the World](#the-automatic-cascade)
6. [DAG Orchestrator — The Cross-Repo Coordinator](#dag-orchestrator)
7. [Setting Up CI/CD for a New Repository](#setting-up-cicd-for-a-new-repository)
8. [GitHub Packages — Why We Use It and How It Works](#github-packages)
9. [Release Process — From Code to Artifact](#release-process)
10. [Version Management — CalVer and the CLI](#version-management)
11. [Branch Strategy](#branch-strategy)
12. [Troubleshooting](#troubleshooting)

---

## The Big Picture

Firefly Framework is not a single project — it is **40 interconnected repositories** that form a dependency graph (DAG). Some repos are foundations that many others depend on (like `parent`, `utils`, or `bom`), while others are leaves that depend on everything below them (like `notifications-firebase` or `backoffice`).

This creates a real engineering challenge: **when you change something in a foundational repo, every repo that depends on it — directly or transitively — needs to be rebuilt and re-tested to make sure nothing broke.** Doing this manually across 40 repos is not realistic.

Our CI/CD system solves this with three key ideas:

1. **Shared workflows** — All build logic lives in one place (the `.github` repo). Update it once, all 40 repos get the change.
2. **Automatic cascade** — When a repo's CI passes on `develop`, it automatically tells the DAG orchestrator to rebuild all downstream dependents. When a release succeeds, it automatically triggers releases for downstream repos.
3. **DAG-aware ordering** — The system understands which repos depend on which, so it rebuilds them in the right order and never tries to build something before its dependencies are ready.

Here is what the architecture looks like:

```
┌──────────────────────────────────────────────────────────────────────┐
│                        .github repository                            │
│                                                                      │
│   .github/workflows/                                                 │
│   ├── java-ci.yml            Shared CI for all Java repos            │
│   ├── java-release.yml       Shared release for all Java repos       │
│   ├── go-ci.yml              Shared CI for Go repos                  │
│   ├── go-release.yml         Shared release for Go repos             │
│   ├── python-ci.yml          Shared CI for Python repos              │
│   ├── python-release.yml     Shared release for Python repos         │
│   └── dag-orchestrator.yml   Cross-repo cascade coordinator          │
└──────────────────────────────────────────────────────────────────────┘
                            ▲
                            │  workflow_call (reusable workflow)
                            │
┌──────────────────────────────────────────────────────────────────────┐
│                    Each framework repository                         │
│                                                                      │
│   .github/workflows/                                                 │
│   ├── ci.yml       → 5-10 line file that calls shared java-ci.yml   │
│   └── release.yml  → 5-10 line file that calls shared release.yml   │
└──────────────────────────────────────────────────────────────────────┘
                            ▲
                            │  triggered by
                            │
┌──────────────────────────────────────────────────────────────────────┐
│                        Trigger Events                                │
│                                                                      │
│   Push to develop         → ci.yml   → build & test → cascade CI     │
│   Pull request            → ci.yml   → build & test (no cascade)     │
│   Tag push (v*)           → release.yml → publish + release          │
│   Manual workflow_dispatch → release.yml → publish + release          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Why Shared Workflows?

Imagine you need to upgrade from Java 25 to Java 26 across all repositories. Without shared workflows, you would need to:

1. Open 38 separate repos
2. Edit each repo's CI workflow to change the Java version
3. Create 38 pull requests
4. Review and merge all of them

With shared workflows, you:

1. Open the `.github` repo
2. Change `default: '25'` to `default: '26'` in `java-ci.yml` and `java-release.yml`
3. Push one commit

That is it. Every repo picks up the change on its next build because they all reference the shared workflow from the `.github` repo's `main` branch.

**The same applies to any CI/CD change:** adding a new build step, fixing a Maven configuration issue, changing the test report retention period, updating the artifact upload action — all of these are one-commit changes that propagate everywhere.

### The tradeoff

The downside is that a broken shared workflow breaks *all* repos at once. This is why changes to the `.github` repo should always be tested carefully. But in practice, the benefit of consistency far outweighs this risk — and a single fix also repairs all repos at once.

---

## How Reusable Workflows Actually Work

GitHub Actions has a feature called **reusable workflows** (`workflow_call` trigger). Here is the step-by-step of what happens when you push to `develop` on any Java repo:

### Step 1: GitHub reads the repo's `ci.yml`

Each repo has a tiny file like this:

```yaml
# .github/workflows/ci.yml (in fireflyframework-utils, for example)
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

This file does not contain any build logic. It just says: "when there is a push or PR, run the `java-ci.yml` workflow from the `.github` repo."

### Step 2: GitHub fetches the shared workflow

The `uses: fireflyframework/.github/.github/workflows/java-ci.yml@main` line tells GitHub to:
- Go to the `fireflyframework/.github` repository
- Look in `.github/workflows/java-ci.yml`
- Use the version from the `main` branch

The `@main` suffix is important: it means every repo always uses the **latest** version of the shared workflow. There is no version pinning to worry about.

### Step 3: The shared workflow runs in the calling repo's context

Even though the workflow YAML comes from the `.github` repo, it runs **in the context of the calling repo**. This means:
- `actions/checkout@v4` clones the calling repo (e.g., `fireflyframework-utils`), not the `.github` repo
- `${{ github.repository }}` resolves to `fireflyframework/fireflyframework-utils`
- `${{ secrets.GITHUB_TOKEN }}` is the token for the calling repo

This is what makes the pattern so powerful — one workflow definition, 40 different execution contexts.

### Why `secrets: inherit` is critical

The `secrets: inherit` line passes all of the calling repo's secrets (including `GITHUB_TOKEN`) to the shared workflow. Without it:
- Maven cannot authenticate with GitHub Packages to download dependencies
- The workflow cannot publish artifacts
- The workflow cannot create GitHub Releases

If you forget this line, every build step that needs authentication will fail with "401 Unauthorized" or "Permission denied."

---

## Shared Workflow Reference

### `java-ci.yml` — Build, Test, and Validate

**What it does:** Compiles the Java project, runs all tests, and uploads test reports. If the build succeeds and was triggered by a push (not a PR), it automatically notifies the DAG orchestrator to rebuild downstream repos.

**Why each step exists:**

| Step | What it does | Why |
|------|-------------|-----|
| Checkout | Clones the repo | Self-explanatory — we need the source code |
| Set up JDK | Installs Temurin JDK with Maven cache | Temurin is the community OpenJDK build. Maven caching saves 30-60s per build by reusing downloaded dependencies |
| Configure GitHub Packages | Writes `~/.m2/settings.xml` | Maven needs credentials to download framework dependencies from GitHub Packages — even reading public packages requires authentication |
| Build with Maven | Runs `mvn -B verify` | The `-B` flag suppresses download progress noise. `verify` compiles, tests, and checks the project without deploying |
| Upload test reports | Saves Surefire/Failsafe reports as artifacts | Even if the build fails, test reports are preserved for 7 days so you can debug failures without re-running |
| Trigger downstream CI | Dispatches the DAG orchestrator | **This is the cascade trigger.** After a successful push build, the system automatically rebuilds all repos that depend on this one |

**Inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `java-version` | string | `25` | JDK version (Temurin distribution) |
| `maven-goals` | string | `verify` | Maven goals to run |
| `maven-args` | string | `""` | Extra arguments passed to Maven |
| `trigger-downstream` | boolean | `true` | Whether to trigger the DAG cascade after success |

**Permissions required:** `packages: read` (dependency resolution) + `actions: write` (dispatching DAG orchestrator)

> **Note:** The cascade only triggers on `push` events (merges to develop), not on pull requests. This is intentional — PRs should validate the current repo only. The full cascade happens after the PR is merged.

### `java-release.yml` — Publish Artifacts and Create Releases

**What it does:** Deploys Maven artifacts to GitHub Packages, creates a GitHub Release with auto-generated release notes, and triggers release cascading to downstream repos.

**Why each step exists:**

| Step | What it does | Why |
|------|-------------|-----|
| Checkout | Clones the repo | Need source code to build the artifact |
| Set up JDK | Installs Temurin JDK | Same as CI |
| Configure GitHub Packages | Writes `~/.m2/settings.xml` | Needs write credentials to publish artifacts |
| Deploy to GitHub Packages | Runs `mvn deploy` | Compiles, packages, and uploads the JAR/POM to the GitHub Packages Maven registry. Tests are skipped because CI already validated them |
| Extract version | Reads version from POM | The `softprops/action-gh-release` action needs to know the version to create the tag and name the release |
| Create GitHub Release | Uses `softprops/action-gh-release@v2` | Creates a tagged release on GitHub with auto-generated release notes. The `tag_name` is set explicitly because when triggered via `workflow_dispatch` there is no tag in `GITHUB_REF` |
| Trigger downstream releases | Dispatches DAG orchestrator in release mode | **After this repo is released, all its downstream dependents are also released.** This is how a single release cascades through the entire dependency graph |

**Inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `java-version` | string | `25` | JDK version |
| `trigger-downstream` | boolean | `true` | Whether to cascade releases to downstream repos |

**Permissions required:** `contents: write` (creating releases/tags) + `packages: write` (publishing artifacts) + `actions: write` (dispatching DAG orchestrator)

**409 Conflict handling:** GitHub Packages does not allow overwriting existing versions. When you re-run a release for a version that was already published, the deploy step will get a 409 error. The workflow detects this specifically — if the error is a 409, it logs a warning and continues to the GitHub Release step (which is usually why you are re-running). If the error is anything else, the workflow fails.

### `go-ci.yml` — Go CI

**What it does:** Runs `go vet`, tests with race detection and coverage, and does a build check.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `go-version` | string | `1.25` | Go version |

**Steps:** `go vet ./...` → `go test -v -race -coverprofile=coverage.out ./...` → `go build -o /dev/null .`

### `go-release.yml` — Go Release

**What it does:** Cross-compiles for 6 platforms and uploads binaries to a GitHub Release.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `go-version` | string | `1.25` | Go version |
| `binary-name` | string | (required) | Name of the compiled binary |

**Platforms:** darwin/amd64, darwin/arm64, linux/amd64, linux/arm64, windows/amd64, windows/arm64

### `python-ci.yml` — Python CI

**What it does:** Lints (`ruff check` + `ruff format --check`), type-checks (`pyright`), and runs tests (`pytest --cov`).

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.13` | Python version |

Uses `uv` as the package manager for fast dependency resolution.

### `python-release.yml` — Python Release

**What it does:** Builds a Python package (wheel + sdist) and creates a GitHub Release with the distribution files attached.

### `dag-orchestrator.yml` — Cross-Repo Cascade Coordinator

See the [dedicated section below](#dag-orchestrator).

---

## The Automatic Cascade

This is the most important concept in the Firefly CI/CD system. Here is the problem it solves and exactly how it works.

### The Problem

Suppose you fix a bug in `fireflyframework-utils`. That repo has 30+ downstream dependents (directly and transitively). Those dependents were all compiled and tested against the *old* version of utils. The fix might:
- Change a method signature that breaks callers
- Fix a behavior that other repos accidentally depended on
- Introduce a new transitive dependency conflict

**You need to know immediately if anything downstream broke.** Not tomorrow, not when someone manually notices — right now, as part of the same push.

### How the Cascade Works — CI Mode

Here is the exact sequence of events when you push a commit to `develop` on `fireflyframework-utils`:

```
1. Push to develop on fireflyframework-utils
   │
2. GitHub triggers ci.yml in fireflyframework-utils
   │
3. ci.yml calls shared java-ci.yml from .github repo
   │
4. java-ci.yml runs: checkout → setup JDK → configure packages → mvn verify
   │
5. Build succeeds ✓
   │
6. java-ci.yml's last step: "Trigger downstream CI via DAG orchestrator"
   │  Dispatches: dag-orchestrator.yml with mode=ci, trigger-repo=fireflyframework-utils
   │
7. DAG orchestrator builds the flywork CLI and runs:
   │  flywork dag affected --from fireflyframework-utils --json
   │  → Returns all downstream repos (e.g., r2dbc, cqrs, web, core, domain, ...)
   │
8. For each affected repo, dispatches ci.yml on develop
   │  → fireflyframework-r2dbc/ci.yml
   │  → fireflyframework-cqrs/ci.yml
   │  → fireflyframework-web/ci.yml
   │  → ... (all downstream repos in parallel)
   │
9. Each downstream repo builds and tests against the NEW version of utils
   │
10. If any downstream repo fails → you see it in the Actions tab immediately
```

**Key design decisions:**

- **The cascade only triggers on `push` events**, not on pull requests. This is intentional. PRs should validate the current repo quickly. The full cascade runs after the PR is merged to develop.
- **The cascade is triggered by the CI workflow itself**, not by a separate cron job or webhook. This means it happens automatically — no human intervention needed.
- **The DAG orchestrator dispatches all affected repos in parallel** (using a GitHub Actions matrix). It does not wait for layer 2 to finish before starting layer 3, because each repo resolves its dependencies from GitHub Packages (the latest published version), not from the local build.

### How the Cascade Works — Release Mode

When you release a repo, the cascade works the same way but triggers `release.yml` instead of `ci.yml`:

```
1. Release succeeds on fireflyframework-utils (artifacts published, GitHub Release created)
   │
2. java-release.yml's last step: "Trigger downstream releases via DAG orchestrator"
   │  Dispatches: dag-orchestrator.yml with mode=release, trigger-repo=fireflyframework-utils
   │
3. DAG orchestrator computes affected repos and dispatches release.yml on main for each
   │
4. Each downstream repo publishes its artifact and creates a GitHub Release
   │
5. Each downstream repo's release, in turn, triggers the cascade again for ITS dependents
   │
6. The cascade ripples through the entire graph until all leaf repos are released
```

**This means releasing the parent repo with `trigger-downstream: true` will eventually release the entire framework.** Each layer cascades to the next, and the chain continues until there are no more dependents.

### When to Disable the Cascade

Set `trigger-downstream: false` when:
- You are doing a **targeted release** of a single repo that you know has not changed its public API
- You are **testing the release workflow** and do not want to trigger 30+ downstream builds
- You are re-running a release to **fix the GitHub Release** (e.g., after a workflow fix) and the artifacts are already published

In per-repo caller workflows, you can pass this input:

```yaml
jobs:
  release:
    uses: fireflyframework/.github/.github/workflows/java-release.yml@main
    secrets: inherit
    with:
      trigger-downstream: false  # do not cascade
```

---

## DAG Orchestrator

The DAG orchestrator is the "brain" of the cascade system. It lives in the `.github` repo as `dag-orchestrator.yml` and coordinates cross-repo builds and releases.

### How It Works

1. **Checkout and build the CLI** — It checks out the `fireflyframework-cli` repo and compiles the `flywork` binary. The CLI contains the full dependency graph definition.

2. **Compute affected repos** — It runs `flywork dag affected --from <trigger-repo> --json`, which returns every repo that transitively depends on the trigger repo. For example, if `fireflyframework-utils` is the trigger, the affected set includes everything from layer 2 through layer 5.

3. **Dispatch workflows** — For each affected repo, it dispatches either `ci.yml` (on develop) or `release.yml` (on main), depending on the `mode` input.

### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `trigger-repo` | string | yes | — | The repository that changed (e.g., `fireflyframework-cache`) |
| `build-all` | boolean | no | `false` | Ignore the trigger repo and rebuild everything |
| `mode` | choice | no | `ci` | `ci` dispatches ci.yml on develop; `release` dispatches release.yml on main |

### Manual Usage

**Trigger CI for all repos affected by a change to cache:**

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-cache \
  -R fireflyframework/.github
```

**Trigger release cascade from parent:**

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-parent \
  -f mode=release \
  -R fireflyframework/.github
```

**Rebuild everything (useful after major dependency changes):**

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-parent \
  -f build-all=true \
  -R fireflyframework/.github
```

### The Dependency Graph (DAG Layers)

The 38 Java repositories are organized into 6 dependency layers. Repos in the same layer can be built in parallel because they do not depend on each other. Repos in layer N only depend on repos in layers 0 through N-1.

| Layer | Count | Repositories |
|-------|-------|-------------|
| 0 | 1 | parent |
| 1 | 11 | bom, utils, cache, eda, ecm, idp, config-server, client, validators, plugins, transactional-engine |
| 2 | 11 | r2dbc, cqrs, web, workflow, ecm-esignature-adobe-sign, ecm-esignature-docusign, ecm-esignature-logalty, ecm-storage-aws, ecm-storage-azure, idp-aws-cognito, idp-keycloak |
| 3 | 6 | eventsourcing, application, idp-internal-db, core, domain, data |
| 4 | 5 | webhooks, callbacks, notifications, rule-engine, backoffice |
| 5 | 4 | notifications-firebase, notifications-resend, notifications-sendgrid, notifications-twilio |

**Why layers matter:** If you change `fireflyframework-utils` (layer 1), everything in layers 2-5 is potentially affected. If you change `fireflyframework-notifications` (layer 4), only layer 5 (the notification adapters) is affected.

You can always get the current DAG with:

```bash
flywork dag layers           # human-readable
flywork dag export --json    # machine-readable (used by the orchestrator)
flywork dag affected --from fireflyframework-cache --json  # show what a change affects
```

---

## Setting Up CI/CD for a New Repository

Adding CI/CD to a new Firefly Framework repo takes about 5 minutes. Here is the step-by-step.

### Step 1: Create the Repository

Create the repo under the `fireflyframework` organization. Set `develop` as the default branch.

### Step 2: Create the CI Workflow

Create `.github/workflows/ci.yml` in the new repo.

**Java repo:**

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

**Go repo:**

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

**Python repo:**

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

That is the entire file. All build logic is in the shared workflow.

### Step 3: Create the Release Workflow

Create `.github/workflows/release.yml`:

**Java repo:**

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
      actions: write
```

**Go repo:**

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

**Python repo:**

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

1. Push a commit to `develop` — the CI workflow should trigger and pass
2. Check the Actions tab on GitHub to confirm
3. To test the release workflow, either push a tag (`git tag v0.0.1 && git push --tags`) or use the "Run workflow" button in the Actions tab

### Step 5: Add to the DAG (Java repos only)

If the new repo depends on other framework modules (or other modules depend on it), you need to register it in the DAG:

1. Edit `internal/dag/graph.go` in the `fireflyframework-cli` repo
2. Add the repo and its dependencies to the `FrameworkGraph()` function
3. Run `flywork dag layers` to verify the repo appears in the correct layer
4. Commit and push the CLI change

**Why this matters:** Without a DAG entry, the cascade system does not know the repo exists. It will not be rebuilt when its dependencies change, and it will not trigger rebuilds of its own dependents.

---

## GitHub Packages

### What It Is and Why We Use It

GitHub Packages is a package registry hosted by GitHub. We publish all Maven artifacts there instead of Maven Central.

**Why not Maven Central?**
- Maven Central requires a complex publishing process (GPG signing, Sonatype staging, manual review for first-time publishers)
- GitHub Packages is integrated directly with GitHub Actions — the `GITHUB_TOKEN` that every workflow already has is all you need
- Package visibility is tied to repository visibility, so organization-level access control is automatic

**The main tradeoff:** Unlike Maven Central, GitHub Packages requires authentication even for *reading* public packages. This means every developer needs a Personal Access Token configured in their `~/.m2/settings.xml`. See the [Getting Started Guide](GETTING_STARTED.md) for how to set this up.

### How Artifacts Are Published

When the release workflow runs, it executes:

```bash
mvn -B deploy -P release -DskipTests \
  -DaltDeploymentRepository=github::https://maven.pkg.github.com/fireflyframework/<repo-name>
```

Breaking this down:
- `-B` — Batch mode, no interactive prompts or download progress bars
- `deploy` — The full Maven lifecycle: compile → test (skipped) → package → install → deploy
- `-P release` — Activates the `release` Maven profile if defined in the POM
- `-DskipTests` — Tests are skipped because CI already validated them on `develop`
- `-DaltDeploymentRepository` — Overrides `<distributionManagement>` in the POM to point to the correct per-repo GitHub Packages URL

### How Artifacts Are Consumed

All framework repos inherit from `fireflyframework-parent`, which configures GitHub Packages as a Maven repository. When Maven resolves a dependency like `fireflyframework-utils`:

1. Checks the local `~/.m2` cache
2. Checks Maven Central
3. Checks GitHub Packages at `https://maven.pkg.github.com/fireflyframework/fireflyframework-parent`

**Important:** GitHub Packages resolves **all** artifacts under the `fireflyframework` organization from a single repository URL. You do not need a separate repository entry for each module.

### Version Immutability

GitHub Packages does **not** allow overwriting an existing version. Once `26.01.01` is published for a given artifact, that version is permanent. Attempting to re-publish returns HTTP 409 Conflict.

**What this means in practice:**
- Every release must use a new version number
- If you need to re-publish with changes, bump the version first: `flywork fwversion bump --auto`
- The release workflow handles 409s gracefully — it logs a warning and continues to the GitHub Release creation step
- This immutability is actually a good thing: it guarantees that version `26.01.01` always refers to the same bytes, everywhere

### CI Authentication

The shared workflows automatically write `~/.m2/settings.xml` with the `GITHUB_TOKEN` during each run. You do not need to configure anything for CI — it is handled by the shared workflow.

### Local Development Authentication

For local builds, you need to create a `~/.m2/settings.xml` with a Personal Access Token. See the [Getting Started Guide](GETTING_STARTED.md) for detailed instructions.

---

## Release Process

### The Standard Release Flow

The recommended way to release the entire framework:

```bash
# 1. Bump version across all 38 repos, commit, tag, and push
flywork fwversion bump --auto --commit --tag --push

# 2. Tag pushes automatically trigger release.yml in each repo
#    → Maven artifacts are published to GitHub Packages
#    → GitHub Releases are created with auto-generated release notes
#    → Each release cascades to downstream repos (if trigger-downstream is true)

# 3. Verify everything succeeded
flywork fwversion check
```

### What Happens During a Release (Step by Step)

When a tag like `v26.02.01` is pushed to `fireflyframework-utils`:

1. GitHub sees the tag push and triggers `release.yml` in `fireflyframework-utils`
2. `release.yml` calls the shared `java-release.yml` from the `.github` repo
3. The shared workflow:
   - Checks out the code at the tagged commit
   - Sets up the JDK and writes `~/.m2/settings.xml`
   - Runs `mvn deploy` to publish the JAR and POM to GitHub Packages
   - Reads the version from `pom.xml` (e.g., `26.02.01`)
   - Creates a GitHub Release named `v26.02.01` with auto-generated notes
   - Dispatches the DAG orchestrator with `mode=release` to cascade to downstream repos
4. The DAG orchestrator computes affected repos and dispatches `release.yml` on `main` for each
5. Each downstream repo repeats steps 1-4, cascading further until leaf repos are reached

### Manual Release Trigger

If you need to re-run a release (for example, after fixing a workflow issue), you can trigger it manually:

**Single repo:**

```bash
gh workflow run release.yml -R fireflyframework/fireflyframework-utils
```

**Via DAG orchestrator (full cascade from a starting point):**

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-parent \
  -f mode=release \
  -R fireflyframework/.github
```

**Using the CLI to publish locally:**

```bash
export GITHUB_TOKEN=ghp_your_token
flywork publish --all
```

### Checking Release Status

```bash
# Check a single repo's latest release
gh release list -R fireflyframework/fireflyframework-utils -L 1

# Check the latest release workflow run
gh run list -R fireflyframework/fireflyframework-utils -w release.yml -L 1

# Check all repos at once
for repo in fireflyframework-parent fireflyframework-bom fireflyframework-utils; do
  echo -n "$repo: "
  gh release list -R "fireflyframework/$repo" -L 1 --json tagName -q '.[0].tagName' 2>/dev/null || echo "none"
done
```

---

## Version Management

### Why CalVer?

Firefly Framework uses **Calendar Versioning** (CalVer) with the format `YY.MM.PP`:

| Component | Meaning | Example |
|-----------|---------|---------|
| `YY` | Two-digit year | `26` for 2026 |
| `MM` | Two-digit month | `01` for January |
| `PP` | Two-digit patch | `01`, `02`, etc. |

**Why CalVer instead of SemVer?** With 38 interdependent Java modules that always release together, semantic versioning (major.minor.patch) creates confusion: what counts as a "major" change when 38 repos are involved? CalVer makes it immediately clear *when* a release was made, and the patch number tracks how many releases happened that month. All 38 repos share the same version number, which makes dependency management simple.

**Examples:**
- First release in January 2026: `26.01.01`
- Second release in January 2026: `26.01.02`
- First release in February 2026: `26.02.01`

### Version Commands

```bash
# Show current version status across all repos
flywork fwversion show

# Show detailed per-repo version info
flywork fwversion show -v

# Validate all repos are on the same version
flywork fwversion check

# Bump to next CalVer (auto-computed based on current date)
flywork fwversion bump --auto

# Bump, commit, tag, and push — the full release prep
flywork fwversion bump --auto --commit --tag --push

# Preview what would change without modifying anything
flywork fwversion bump --auto --dry-run

# Bump and also run mvn install to update local .m2
flywork fwversion bump --auto --install

# View release history
flywork fwversion families
```

### How Version Bumping Works

When you run `flywork fwversion bump --auto --commit --tag --push`, the CLI:

1. **Reads the current version** from the parent POM
2. **Computes the next version** — increments the patch number, or rolls to the next month if the calendar month has changed
3. **Updates all POMs** — finds every `pom.xml` across all 38 repos and updates the parent version reference and any cross-module dependency versions
4. **Commits** — creates a git commit in each repo
5. **Tags** — creates a `v<new-version>` tag in each repo
6. **Pushes** — pushes commits and tags to the remote
7. **Records the release family** — saves a snapshot of all module SHAs for this version

---

## Branch Strategy

All Firefly Framework repositories follow a simple two-branch model:

| Branch | Purpose | CI behavior |
|--------|---------|-------------|
| `develop` | Active development | CI runs on every push. Successful builds cascade downstream. |
| `main` | Stable releases | Updated by merging develop. Release workflows run here. |

### Typical Workflow

1. Create a feature branch from `develop`
2. Open a PR to `develop` — CI runs (no cascade)
3. Merge the PR — CI runs on the merge commit and cascades to downstream repos
4. When ready to release: merge `develop` into `main` (or force-push `main` to match `develop`)
5. Push version tags — release workflows trigger automatically
6. Release cascades through the DAG

### Why Two Branches?

- `develop` is where the latest code lives. CI validates everything here, and the cascade ensures downstream compatibility.
- `main` is the release branch. Shared workflows are referenced with `@main`, so `main` must always be stable.

**Merging to main should be a deliberate action**, not automatic. The release workflow uses `main` as its source, so only merge develop into main when you are ready to publish.

---

## Troubleshooting

### "Could not resolve artifact"

**What you see:** `Could not find artifact org.fireflyframework:fireflyframework-xyz:jar:26.01.01`

**What it means:** Maven cannot find a framework dependency. This can happen for several reasons:

1. **Missing `settings.xml`** — Maven does not know how to authenticate with GitHub Packages.
   → Fix: Create `~/.m2/settings.xml` with your PAT. See [Getting Started Guide](GETTING_STARTED.md).

2. **Wrong token scope** — Your Personal Access Token does not have `read:packages` permission.
   → Fix: Go to GitHub Settings → Developer settings → Tokens and add `read:packages`.

3. **Artifact not published yet** — The dependency has never been deployed to GitHub Packages.
   → Fix: Check `https://github.com/fireflyframework/<repo-name>/packages`. If empty, trigger: `gh workflow run release.yml -R fireflyframework/<repo-name>`

4. **Wrong version** — The POM references a version that does not exist in the registry.
   → Fix: Run `mvn -U verify` to force Maven to re-check remote repos.

### 409 Conflict on Deploy

**What you see:** `status code: 409, reason phrase: Conflict`

**What it means:** You are trying to publish a version that already exists. GitHub Packages versions are immutable.

**What the workflow does:** The shared `java-release.yml` detects 409 errors specifically. It logs a warning and continues to the GitHub Release step. This way, re-running the release workflow for a version that was already published still creates the GitHub Release.

**If you need new content at the same version:** You cannot. Bump the version: `flywork fwversion bump --auto --push`

### "GitHub Releases requires a tag"

**What you see:** The `softprops/action-gh-release` step fails with this error.

**Why it happens:** When triggered via `workflow_dispatch`, `GITHUB_REF` is `refs/heads/main` (a branch), not a tag. The gh-release action does not know what tag to use.

**The fix is already in place:** The shared workflows set `tag_name: v${{ steps.version.outputs.version }}` explicitly. If you still see this error, your repo's `release.yml` might be referencing an old version of the shared workflow. Make sure it uses `@main`.

### "Permission denied" or "Resource not accessible"

**What you see:** 403 errors when trying to download packages, create releases, or dispatch workflows.

**Common causes:**

1. **Missing `secrets: inherit`** in the caller workflow — the shared workflow cannot access `GITHUB_TOKEN`.
2. **Missing permissions block** in the caller workflow — add the required permissions:
   ```yaml
   permissions:
     contents: write    # creating releases and tags
     packages: write    # publishing artifacts
     actions: write     # dispatching DAG orchestrator
   ```
3. **Organization-level restrictions** — Go to Organization Settings → Actions → General → Workflow permissions and select "Read and write permissions."
4. **Cross-repo dispatch** — The DAG orchestrator dispatches workflows in other repos. This requires the `GITHUB_TOKEN` to have `actions: write` permission and the organization to allow cross-repo workflow dispatch. If using a fine-grained PAT instead of `GITHUB_TOKEN`, it needs explicit repo access.

### Build Order Issues

**What you see:** A downstream repo fails because its dependency is not in GitHub Packages.

**Why it happens:** The dependency was not published before the downstream repo tried to build.

**Fixes:**
1. Check the DAG: `flywork dag layers` — the dependency must be in an earlier layer
2. For local builds: `flywork build --all` rebuilds everything in correct DAG order
3. For CI: Trigger the DAG orchestrator with `build-all=true`
4. For releases: Release repos layer by layer (0, then 1, then 2, etc.) or let the cascade handle it

### GenAI CI Fails with Lint Errors

**What you see:** `ruff check` or `ruff format --check` step fails.

**Fix:** Run the auto-fixer locally:

```bash
cd fireflyframework-genai
uv run ruff check . --fix
uv run ruff format .
```

Commit and push the fixes.

### Tests Pass Locally but Fail in CI

**Possible causes:**
1. **Different Java version** — CI uses Java 25 by default. Check yours with `java -version`.
2. **Missing dependencies** — CI resolves from GitHub Packages, not your local `~/.m2`. A dependency that exists locally but was never published will fail in CI.
3. **Testcontainers** — Some tests need Docker. GitHub Actions runners have Docker, but your local machine might not.
4. **Environment variables** — CI does not have the same env vars as your machine.

### Release Succeeds but No GitHub Release Appears

**Possible causes:**
1. Missing `permissions: contents: write` in the caller workflow
2. The release was created as "draft" — check the Releases page
3. The gh-release step was skipped because a prior step failed

**Debug:** Check the workflow run in the Actions tab. Expand each step to see its output. The "Create GitHub Release" step will show whether the tag was created and the release was published.

### The Cascade Did Not Trigger

**What you see:** You pushed to develop and the current repo's CI passed, but downstream repos were not rebuilt.

**Possible causes:**
1. **It was a PR, not a push** — The cascade only triggers on `push` events (merges to develop), not on pull requests.
2. **`trigger-downstream` is set to `false`** — Check the caller workflow's `with:` block.
3. **Missing `actions: write` permission** — The workflow needs permission to dispatch the DAG orchestrator.
4. **The repo is not in the DAG** — Run `flywork dag affected --from <repo-name>` to check if it has any downstream dependents. If the repo is not registered in `internal/dag/graph.go`, the DAG does not know about it.
5. **Cross-repo dispatch failed** — The `GITHUB_TOKEN` may not have permission to trigger workflows in the `.github` repo. Check the workflow logs for a warning message.
