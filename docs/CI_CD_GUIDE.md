# CI/CD Configuration Guide

Everything you need to know about how Firefly Framework builds, tests, publishes, and releases its 40 repositories — and how to set it up for new ones.

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [Why Shared Workflows?](#why-shared-workflows)
3. [How Reusable Workflows Actually Work](#how-reusable-workflows-actually-work)
4. [Shared Workflow Reference](#shared-workflow-reference)
5. [DAG Orchestrator — The Cross-Repo Coordinator](#dag-orchestrator)
6. [Release Ordering and DAG Layers](#release-ordering-and-dag-layers)
7. [Setting Up CI/CD for a New Repository](#setting-up-cicd-for-a-new-repository)
8. [GitHub Packages — Why We Use It and How It Works](#github-packages)
9. [Release Process — From Code to Artifact](#release-process)
10. [Version Management — CalVer and the CLI](#version-management)
11. [Branch Strategy](#branch-strategy)
12. [Troubleshooting](#troubleshooting)
13. [CI Status Dashboard](#ci-status-dashboard)

---

## The Big Picture

Firefly Framework is not a single project — it is **40 interconnected repositories** that form a dependency graph (DAG). Some repos are foundations that many others depend on (like `parent`, `utils`, or `bom`), while others are leaves that depend on everything below them (like `notifications-firebase` or `backoffice`).

This creates a real engineering challenge: **when you change something in a foundational repo, every repo that depends on it — directly or transitively — needs to be rebuilt and re-tested to make sure nothing broke.** Doing this manually across 40 repos is not realistic.

Our CI/CD system solves this with two key ideas:

1. **Shared workflows** — All build logic lives in one place (the `.github` repo). Update it once, all 40 repos get the change.
2. **DAG-aware release ordering** — The DAG orchestrator dispatches releases **layer by layer**, ensuring parent artifacts are published before downstream repos try to resolve them.

Here is what the architecture looks like:

```
┌─────────────────────────────────────────────────────────────────────┐
│ .github repository                                                  │
│                                                                     │
│ .github/workflows/                                                  │
│ ├── java-ci.yml          Shared CI for all Java repos               │
│ ├── java-release.yml     Shared release for all Java repos          │
│ ├── go-ci.yml            Shared CI for Go repos                     │
│ ├── go-release.yml       Shared release for Go repos                │
│ ├── python-ci.yml        Shared CI for Python repos                 │
│ ├── python-release.yml   Shared release for Python repos            │
│ └── dag-orchestrator.yml Cross-repo layer-by-layer coordinator      │
└─────────────────────────────────────────────────────────────────────┘
                            ▲
                            │ workflow_call (reusable workflow)
                            │
┌─────────────────────────────────────────────────────────────────────┐
│ Each framework repository                                           │
│                                                                     │
│ .github/workflows/                                                  │
│ ├── ci.yml      → calls shared java-ci.yml (10-15 lines)           │
│ └── release.yml → calls shared release.yml (10-15 lines)           │
└─────────────────────────────────────────────────────────────────────┘
                            ▲
                            │ triggered by
                            │
┌─────────────────────────────────────────────────────────────────────┐
│ Trigger Events                                                      │
│                                                                     │
│ Push to develop/main  → ci.yml → build & test                       │
│ Pull request          → ci.yml → build & test                       │
│ Tag push (v*)         → release.yml → publish + release             │
│ workflow_dispatch      → ci.yml or release.yml (manual/DAG)         │
└─────────────────────────────────────────────────────────────────────┘
```

**Key design decisions (26.02.03):**
- **CI does not cascade.** Pushing to `develop` builds only the affected repo. Use `flywork build --affected` locally if you need to test downstream impact.
- **Releases cascade via the DAG orchestrator**, which dispatches layer by layer — waiting for each layer to complete before starting the next.
- **No duplicate workflow runs.** Tag pushes trigger `release.yml` directly. The DAG orchestrator is used for coordinated multi-repo releases, not auto-triggered from individual releases.

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
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'tutorials/**'
      - 'examples/**/README.md'
      - 'LICENSE'
      - '.gitignore'
  pull_request:
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'tutorials/**'
      - 'examples/**/README.md'
      - 'LICENSE'
      - '.gitignore'
  workflow_dispatch:
    inputs:
      triggered-by:
        description: 'Orchestrator run ID'
        required: false
        type: string
jobs:
  build:
    uses: fireflyframework/.github/.github/workflows/java-ci.yml@main
    permissions:
      packages: read
      contents: read
    with:
      java-version: '25'
    secrets: inherit
```

This file does not contain any build logic. It just says: "when there is a push, PR, or dispatch, run the `java-ci.yml` workflow from the `.github` repo."

The `workflow_dispatch` trigger with a `triggered-by` input is what allows the DAG orchestrator to trigger this repo's CI from outside. Without it, the orchestrator cannot dispatch workflows to this repo.

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

### Secrets: `GITHUB_TOKEN` vs `ORG_DISPATCH_TOKEN`

Two tokens are used in the CI/CD system:

1. **`GITHUB_TOKEN`** — Automatically provided by GitHub Actions. Used for Maven dependency resolution, artifact publishing, and creating GitHub Releases. This token is scoped to the **current repository**.

2. **`ORG_DISPATCH_TOKEN`** — An organization-level secret (Personal Access Token) with `all` repository visibility. Used exclusively for **cross-repo workflow dispatching** — when the DAG orchestrator needs to dispatch CI/release workflows in other repos.

**`secrets: inherit` is required on all Java repos** to ensure that org-level secrets like `ORG_DISPATCH_TOKEN`, `SONATYPE_USERNAME`, `SONATYPE_PASSWORD`, `GPG_PRIVATE_KEY`, and `GPG_PASSPHRASE` are properly passed through to the shared workflows. Without it, the shared release workflow cannot publish to Maven Central.

---

## Shared Workflow Reference

### `java-ci.yml` — Build, Test, and Validate

**What it does:** Compiles the Java project, runs all tests, and uploads test reports.

**Why each step exists:**

| Step | What it does | Why |
|------|-------------|-----|
| Checkout | Clones the repo | Self-explanatory — we need the source code |
| Set up JDK | Installs Temurin JDK with Maven cache | Temurin is the community OpenJDK build. Maven caching saves 30-60s per build by reusing downloaded dependencies |
| Configure GitHub Packages | Writes `~/.m2/settings.xml` | Maven needs credentials to download framework dependencies from GitHub Packages — even reading public packages requires authentication |
| Build with Maven | Runs `mvn -B -U verify` | `-B` suppresses download progress noise. `-U` forces Maven to re-check remote repositories for updated dependencies, preventing stale cache failures. `verify` compiles, tests, and checks the project without deploying |
| Upload test reports | Saves Surefire/Failsafe reports as artifacts | Even if the build fails, test reports are preserved for 7 days so you can debug failures without re-running |

**Inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `java-version` | string | `25` | JDK version (Temurin distribution) |
| `maven-goals` | string | `verify` | Maven goals to run |
| `maven-args` | string | `""` | Extra arguments passed to Maven |

**Concurrency:** CI runs use a concurrency group per repository and branch. If a new push arrives while CI is running, the in-progress run is cancelled.

**Permissions required (on caller workflow):** `packages: read` (downloading dependencies) + `contents: read` (checking out code)

### `java-release.yml` — Publish Artifacts and Create Releases

**What it does:** Deploys Maven artifacts to both GitHub Packages and Maven Central in parallel, then creates a GitHub Release.

**Key design features:**

- **Multi-module 409 handling:** For multi-module repos (detected by `<modules>` in pom.xml), the deploy is split into two phases: parent POM first (`-N`), then child modules (`-pl '!.'`). This prevents the Maven reactor ban cascade where a 409 on the parent POM kills all child deployments.
- **Maven Central pre-check:** Before deploying, checks if the version is already published on Maven Central. If so, skips the deploy entirely rather than getting a confusing error.
- **Strict error matching:** Only treats HTTP 409 and explicit "already exists/published" messages as acceptable. Other errors (including 400 Bad Request) are treated as real failures.
- **Post-release requires both targets:** The GitHub Release is only created when BOTH GitHub Packages and Maven Central succeed.
- **Concurrency control:** Each job has a concurrency group per repository and ref to prevent duplicate release runs.

**Inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `java-version` | string | `25` | JDK version |

**Permissions required (on caller workflow):** `contents: write` (creating releases/tags) + `packages: write` (publishing artifacts)

**Dual publish:** The release workflow publishes to both GitHub Packages and Maven Central in parallel jobs. Both deploy steps use `set -o pipefail` to ensure Maven failures are properly detected even when output is piped through `tee` for log capture.

### `go-ci.yml` — Go CI

**What it does:** Runs `go vet`, tests with race detection and coverage, and does a build check.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `go-version` | string | `1.25` | Go version |

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

Uses `uv` as the package manager (via `astral-sh/setup-uv@v4`) for fast dependency resolution.

**Timeouts:** The job has a `timeout-minutes: 15` limit. The `pyright` step has its own `timeout-minutes: 10`.

### `python-release.yml` — Python Release

**What it does:** Builds a Python package (wheel + sdist) using `uv build` and creates a GitHub Release with the distribution files attached.

### `dag-orchestrator.yml` — Cross-Repo Layer-by-Layer Coordinator

See the [dedicated section below](#dag-orchestrator).

---

## DAG Orchestrator

The DAG orchestrator is the "brain" of the release cascade system. It lives in the `.github` repo as `dag-orchestrator.yml` and coordinates cross-repo releases **layer by layer**.

### How It Works

1. **Checkout and build the CLI** — It checks out the `fireflyframework-cli` repo (from the `main` branch) and compiles the `flywork` binary. The CLI contains the full dependency graph definition.

2. **Compute affected repos with layers** — It runs `flywork dag affected --from <trigger-repo> --layers --json`, which returns every repo that transitively depends on the trigger repo, **grouped by dependency layer**. If `build-all` is true, it exports the entire DAG's layers instead.

3. **Dispatch layer by layer** — For each layer:
   - Dispatch all repos in the layer in parallel
   - Wait for ALL repos in the layer to complete
   - Verify all succeeded (fail fast if any repo fails)
   - Only then proceed to the next layer

This ensures that when layer 2 repos try to resolve their dependencies, all layer 1 artifacts are already published.

### Why Layer-by-Layer Matters

The 26.02.03 release failed because all 38 repos were dispatched simultaneously. Downstream repos tried to resolve parent POMs that hadn't been published yet, causing cascading build failures. Layer-by-layer dispatch eliminates this race condition.

### Permissions and Tokens

The DAG orchestrator uses `secrets.ORG_DISPATCH_TOKEN` for all cross-repo dispatches. The default `GITHUB_TOKEN` cannot dispatch workflows in other repos — it is scoped to the repo where the workflow runs.

### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `trigger-repo` | string | yes | — | The repository that changed (e.g., `fireflyframework-cache`) |
| `build-all` | boolean | no | `false` | Ignore the trigger repo and rebuild/release everything |
| `mode` | choice | no | `ci` | `ci` dispatches ci.yml on develop; `release` dispatches release.yml on main |

### Manual Usage

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

---

## Release Ordering and DAG Layers

The 38 Java repositories are organized into 6 dependency layers. Repos in the same layer can be built/released in parallel because they do not depend on each other. Repos in layer N only depend on repos in layers 0 through N-1.

| Layer | Count | Repositories |
|-------|-------|-------------|
| 0 | 1 | parent |
| 1 | 11 | bom, utils, cache, eda, ecm, idp, config-server, client, validators, plugins, transactional-engine |
| 2 | 11 | r2dbc, cqrs, web, workflow, ecm-esignature-adobe-sign, ecm-esignature-docusign, ecm-esignature-logalty, ecm-storage-aws, ecm-storage-azure, idp-aws-cognito, idp-keycloak |
| 3 | 6 | eventsourcing, application, idp-internal-db, core, domain, data |
| 4 | 5 | webhooks, callbacks, notifications, rule-engine, backoffice |
| 5 | 4 | notifications-firebase, notifications-resend, notifications-sendgrid, notifications-twilio |

**Why layers matter:** If you change `fireflyframework-utils` (layer 1), everything in layers 2-5 is potentially affected. If you change `fireflyframework-notifications` (layer 4), only layer 5 (the notification adapters) is affected.

**During a release**, the DAG orchestrator ensures:
1. Layer 0 (`parent`) is published and confirmed on GitHub Packages
2. Only then are layer 1 repos dispatched
3. Layer 1 completes → layer 2 starts
4. And so on until layer 5

This eliminates the race conditions that caused the 26.02.03 release failures.

You can always get the current DAG with:

```bash
flywork dag layers              # human-readable
flywork dag export --json       # machine-readable (used by the orchestrator)
flywork dag affected --from fireflyframework-cache --json          # flat list
flywork dag affected --from fireflyframework-cache --layers --json # layer-grouped
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
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'tutorials/**'
      - 'examples/**/README.md'
      - 'LICENSE'
      - '.gitignore'
  pull_request:
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'tutorials/**'
      - 'examples/**/README.md'
      - 'LICENSE'
      - '.gitignore'
  workflow_dispatch:
    inputs:
      triggered-by:
        description: 'Orchestrator run ID'
        required: false
        type: string
jobs:
  build:
    uses: fireflyframework/.github/.github/workflows/java-ci.yml@main
    permissions:
      packages: read
      contents: read
    with:
      java-version: '25'
    secrets: inherit
```

**Go repo:**

```yaml
name: CI
on:
  push:
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'LICENSE'
      - '.gitignore'
  pull_request:
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'LICENSE'
      - '.gitignore'
  workflow_dispatch:
    inputs:
      triggered-by:
        description: 'Orchestrator run ID'
        required: false
        type: string
jobs:
  build-and-test:
    uses: fireflyframework/.github/.github/workflows/go-ci.yml@main
    with:
      go-version: '1.25'
    secrets: inherit
```

**Python repo:**

```yaml
name: CI
on:
  push:
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'LICENSE'
      - '.gitignore'
  pull_request:
    branches: [develop, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'LICENSE'
      - '.gitignore'
  workflow_dispatch:
    inputs:
      triggered-by:
        description: 'Orchestrator run ID'
        required: false
        type: string
jobs:
  lint-and-test:
    uses: fireflyframework/.github/.github/workflows/python-ci.yml@main
    with:
      python-version: '3.13'
    secrets: inherit
```

> **Important:** All repos MUST include `secrets: inherit`. Without it, org-level secrets like `SONATYPE_USERNAME`, `GPG_PRIVATE_KEY`, and `ORG_DISPATCH_TOKEN` are not passed to the shared workflows.

### Step 3: Create the Release Workflow

Create `.github/workflows/release.yml`:

**Java repo:**

```yaml
name: Release
on:
  push:
    tags: ['v*']
  workflow_dispatch:
    inputs:
      triggered-by:
        description: 'Orchestrator run ID'
        required: false
        type: string
jobs:
  release:
    uses: fireflyframework/.github/.github/workflows/java-release.yml@main
    with:
      java-version: '25'
    permissions:
      contents: write
      packages: write
    secrets: inherit
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

### Step 6: Ensure Maven Central readiness

For the artifact to be accepted by Maven Central, its `pom.xml` must include:
- `<name>` — Human-readable project name
- `<description>` — Brief description of the module
- These are inherited from `fireflyframework-parent` for `<url>`, `<licenses>`, `<developers>`, and `<scm>`, but `<name>` and `<description>` should be unique per module.

---

## GitHub Packages

### What It Is and Why We Use It

GitHub Packages is a package registry hosted by GitHub. We publish all Maven artifacts to **both** GitHub Packages and Maven Central. GitHub Packages is the primary registry used by the framework's own CI/CD system, while Maven Central provides public availability for external consumers.

**Why both?**
- **GitHub Packages** is integrated directly with GitHub Actions — the `GITHUB_TOKEN` that every workflow already has is all you need. It is used for dependency resolution during CI and releases within the framework.
- **Maven Central** provides public, unauthenticated access for external consumers who depend on Firefly Framework modules.

**The main tradeoff:** Unlike Maven Central, GitHub Packages requires authentication even for *reading* public packages. This means every developer needs a Personal Access Token configured in their `~/.m2/settings.xml`. See the [Getting Started Guide](GETTING_STARTED.md) for how to set this up.

### How Artifacts Are Published

When the release workflow runs, it handles three cases:

**Single-module repos:**
```bash
mvn -B -U deploy -P release -DskipTests \
  -DaltDeploymentRepository=github::https://maven.pkg.github.com/fireflyframework/<repo-name>
```

**Multi-module repos (two-phase deploy):**
```bash
# Phase 1: Parent POM only (non-recursive)
mvn -B -U deploy -P release -DskipTests -N \
  -DaltDeploymentRepository=github::https://maven.pkg.github.com/fireflyframework/<repo-name>

# Phase 2: Child modules only
mvn -B -U deploy -P release -DskipTests -pl '!.' \
  -DaltDeploymentRepository=github::https://maven.pkg.github.com/fireflyframework/<repo-name>
```

The two-phase approach prevents the reactor ban cascade: if the parent POM already exists (409), the child modules can still deploy independently.

### Version Immutability

GitHub Packages does **not** allow overwriting an existing version. Once `26.02.03` is published for a given artifact, that version is permanent. Attempting to re-publish returns HTTP 409 Conflict.

**What this means in practice:**
- Every release must use a new version number
- If you need to re-publish with changes, bump the version first: `flywork fwversion bump --auto`
- The release workflow handles 409s gracefully — it logs a warning and continues
- This immutability is a good thing: it guarantees that version `26.02.03` always refers to the same bytes, everywhere

---

## Release Process

### The Standard Release Flow

The recommended way to release the entire framework:

```bash
# 1. Bump version across all repos, commit, merge to main, tag
flywork fwversion bump --auto --commit --tag --push

# 2. Use the DAG orchestrator for ordered release
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-parent \
  -f mode=release \
  -f build-all=true \
  -R fireflyframework/.github

# 3. The orchestrator dispatches repos layer by layer:
#    Layer 0: parent → wait for completion
#    Layer 1: bom, utils, cache, ... → wait for completion
#    Layer 2: r2dbc, cqrs, web, ... → wait for completion
#    ... and so on until all repos are released

# 4. Verify everything succeeded
flywork fwversion check
```

### What Happens During a Release (Step by Step)

When the DAG orchestrator dispatches `release.yml` for a repo:

1. GitHub triggers `release.yml` in the target repo
2. `release.yml` calls the shared `java-release.yml` from the `.github` repo
3. The shared workflow runs two parallel jobs:
   - **GitHub Packages:** Deploys artifacts with multi-module 409 handling
   - **Maven Central:** Checks for existing publication, then deploys with GPG signing
4. If both succeed, the post-release job:
   - Reads the version from `pom.xml`
   - Creates a GitHub Release named `v<version>` with auto-generated notes

### Manual Release Trigger

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
| `MM` | Two-digit month | `02` for February |
| `PP` | Two-digit patch | `01`, `02`, etc. |

**Why CalVer instead of SemVer?** With 38 interdependent Java modules that always release together, semantic versioning creates confusion: what counts as a "major" change when 38 repos are involved? CalVer makes it immediately clear *when* a release was made, and the patch number tracks how many releases happened that month.

### Version Commands

```bash
flywork fwversion show              # Current version status
flywork fwversion show -v           # Detailed per-repo info
flywork fwversion check             # Validate all repos are in sync
flywork fwversion bump --auto       # Bump to next CalVer
flywork fwversion bump --auto --commit --tag --push  # Full release prep
flywork fwversion bump --auto --dry-run              # Preview changes
flywork fwversion families          # View release history
```

---

## Branch Strategy

All Firefly Framework repositories follow a simple two-branch model:

| Branch | Purpose | CI behavior |
|--------|---------|-------------|
| `develop` | Active development | CI runs on every push |
| `main` | Stable releases | CI runs on push. Release workflows run here |

### Typical Workflow

1. Create a feature branch from `develop`
2. Open a PR to `develop` — CI runs (no cascade)
3. Merge the PR — CI runs on the merge commit
4. When ready to release: merge `develop` into `main`
5. Push version tags — release workflows trigger automatically
6. Use DAG orchestrator for coordinated multi-repo releases

### Why Two Branches?

- `develop` is where the latest code lives. CI validates everything here.
- `main` is the release branch. Shared workflows are referenced with `@main`, so `main` must always be stable.

**Merging to main should be a deliberate action**, not automatic. The release workflow uses `main` as its source, so only merge develop into main when you are ready to publish.

---

## Troubleshooting

### "Could not resolve artifact"

**What you see:** `Could not find artifact org.fireflyframework:fireflyframework-xyz:jar:26.02.03`

**Common causes:**

1. **Missing `settings.xml`** — Maven does not know how to authenticate with GitHub Packages.
   → Fix: Create `~/.m2/settings.xml` with your PAT. See [Getting Started Guide](GETTING_STARTED.md).

2. **Wrong token scope** — Your Personal Access Token does not have `read:packages` permission.
   → Fix: Go to GitHub Settings → Developer settings → Tokens and add `read:packages`.

3. **Artifact not published yet** — The dependency has never been deployed to GitHub Packages.
   → Fix: Check `https://github.com/fireflyframework/<repo-name>/packages`. If empty, trigger: `gh workflow run release.yml -R fireflyframework/<repo-name>`

4. **Race condition during release** — Downstream repo tried to build before upstream published.
   → Fix: Use the DAG orchestrator with layer-by-layer dispatch instead of releasing all repos simultaneously.

5. **Cached resolution failure** — Maven caches failed dependency lookups in `.lastUpdated` files.
   → Fix: Run `mvn -U verify` (the `-U` flag forces Maven to re-check remote repos) or delete the `.lastUpdated` files from `~/.m2/repository/`.

### 409 Conflict on Deploy

**What you see:** `status code: 409, reason phrase: Conflict`

**What it means:** You are trying to publish a version that already exists. GitHub Packages versions are immutable.

**What the workflow does:** The shared `java-release.yml` detects 409 errors specifically:
- **Single-module repos:** Logs a warning and continues
- **Multi-module repos:** Deploys parent POM first, then children separately. A 409 on the parent POM does not kill child deployments.

**If you need new content at the same version:** You cannot. Bump the version: `flywork fwversion bump --auto --push`

### Multi-Module 409 Cascade (Fixed in 26.02.03)

**What happened in 26.02.03:** When a multi-module repo's parent POM got a 409, Maven's reactor banned all child modules from deploying. 14 sub-modules across 4 repos failed to publish.

**How it's fixed:** The release workflow now uses a two-phase deploy strategy:
1. Deploy parent POM with `-N` (non-recursive)
2. Deploy children with `-pl '!.'` (exclude root)

This way, a 409 on the parent POM is handled independently and does not prevent child modules from deploying.

### Maven Central Validation Failures (Fixed in 26.02.03)

**What happened in 26.02.03:** The `waitUntil: uploaded` configuration in the parent POM caused the Maven Central deploy step to return success as soon as the artifact was uploaded — before Sonatype validated it. 5 artifacts failed validation and never appeared on Maven Central, but CI showed green.

**How it's fixed:** Changed `waitUntil` to `published` in both `fireflyframework-parent/pom.xml` and `fireflyframework-bom/pom.xml`. The deploy step now waits for validation to complete and fails if validation fails.

**Required pom.xml elements for Maven Central:**
- `<name>` — Required on every module
- `<description>` — Required on every module
- `<url>`, `<licenses>`, `<developers>`, `<scm>` — Inherited from parent POM

### "Permission denied" or "Resource not accessible"

**What you see:** 403 errors when trying to download packages, create releases, or dispatch workflows.

**Common causes:**

1. **Missing `secrets: inherit`** in the caller workflow — ALL Java repos must include `secrets: inherit` to pass org secrets through to the shared workflows.

2. **Missing permissions block** in the caller workflow — add the required permissions:
   ```yaml
   # For CI workflows:
   permissions:
     packages: read
     contents: read

   # For release workflows:
   permissions:
     contents: write
     packages: write
   ```

3. **`ORG_DISPATCH_TOKEN` is missing or expired** — The DAG orchestrator uses this token for cross-repo dispatch. Check the org secret at Organization Settings → Secrets and variables → Actions → `ORG_DISPATCH_TOKEN`.

### Build Order Issues (Release)

**What you see:** A downstream repo fails during release because its dependency is not in GitHub Packages yet.

**Why it happens:** The dependency was not published before the downstream repo tried to build. This is the race condition that occurs when all repos are released simultaneously.

**Fix:** Always use the DAG orchestrator for multi-repo releases. It dispatches layer by layer, waiting for each layer to complete before starting the next:

```bash
gh workflow run dag-orchestrator.yml \
  -f trigger-repo=fireflyframework-parent \
  -f mode=release \
  -f build-all=true \
  -R fireflyframework/.github
```

### Tests Pass Locally but Fail in CI

**Possible causes:**
1. **Different Java version** — CI uses Java 25 by default. Check yours with `java -version`.
2. **Missing dependencies** — CI resolves from GitHub Packages, not your local `~/.m2`. A dependency that exists locally but was never published will fail in CI.
3. **Testcontainers** — Some tests need Docker. GitHub Actions runners have Docker, but your local machine might not.
4. **Environment variables** — CI does not have the same env vars as your machine.

### Failed Builds Not Retried

**What happened before 26.02.03:** The `flywork build` command recorded the SHA even for failed builds, so `DetectChanges` would not pick them up on retry.

**How it's fixed:** `LastSHA()` now returns empty string for repos with `status: "failed"`, ensuring failed builds are always retried regardless of whether the commit SHA has changed.

---

## CI Status Dashboard

A live build status dashboard for all 40 repositories is available at:

**[CI Status Dashboard](CI_STATUS.md)**

The dashboard shows every repo grouped by category (Foundation, Core Modules, Data & Persistence, etc.) with descriptions and CI badge status. Use it to quickly check which repos are passing and which need attention.
