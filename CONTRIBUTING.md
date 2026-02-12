# Contributing to Firefly Framework

Thank you for your interest in contributing to Firefly Framework! This guide covers everything you need to get started, from setting up your environment to submitting a pull request.

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Setup](#quick-setup)
- [Branching Model](#branching-model)
- [Pull Request Process](#pull-request-process)
- [Versioning (CalVer)](#versioning-calver)
- [Code Standards](#code-standards)
- [Commit Conventions](#commit-conventions)

---

## Prerequisites

Ensure the following tools are installed and available on your `PATH`:

| Tool | Required Version | Notes |
|--------|------------------|--------------------------------|
| Java | 25 (21+ compatible) | Default is Java 25; builds must pass on 21+ |
| Maven | 3.9+ | Used for all Java module builds |
| Go | 1.25+ | Required for the CLI (`flywork`) |
| Python | 3.13+ | Required for GenAI modules and tooling |
| Git | 2.30+ | Required for branching workflows |

## Quick Setup

The fastest way to bootstrap your development environment is with the Firefly CLI:

```bash
flywork setup # clones all repos in dependency order and installs to ~/.m2
flywork doctor # verifies your environment (Java, Maven, Go, Python, Git, etc.)
```

`flywork doctor` will check every prerequisite listed above and report any issues.

---

## Branching Model

Firefly Framework follows a **Gitflow** branching model across all repositories.

```
  main ─────────●────────────────●──────────────── production releases
                 \ / \
  hotfix/fix-x `───●───●───' \
                                   \
  release/26.02 ──────●─────●──────●──────────────
                     / |
  develop ──●──●──●──●──●──●──●──●──●──●──●────── integration branch
              \ / \ /
  feature/a `──●─' \ /
                               \ /
  feature/b `●'
```

### Branch Purposes

| Branch | Created From | Merges Into | Purpose |
|-------------------|--------------|--------------------|--------------------------------|
| `main` | -- | -- | Production releases only |
| `develop` | `main` | -- | Integration branch for all work |
| `feature/<name>` | `develop` | `develop` | New features and enhancements |
| `release/YY.MM` | `develop` | `main` + `develop` | Release stabilization and prep |
| `hotfix/<name>` | `main` | `main` + `develop` | Emergency production fixes |

### Rules

- **Never** push directly to `main` or `develop`.
- Feature branches must be up to date with `develop` before merging.
- Release branches receive only bug fixes -- no new features.
- Hotfix branches are reserved for critical production issues and must include a regression test.

---

## Pull Request Process

1. **Branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```

2. **Implement** your changes, following the code standards below.

3. **Verify** locally:
   ```bash
   mvn verify
   ```
   All tests must pass and no new warnings should be introduced.

4. **Open a PR** targeting `develop`. Fill out the PR template completely.

5. **Get a review.** At least one maintainer approval is required.

6. **Merge.** Once approved and CI is green, a maintainer will merge via squash-merge or merge commit depending on the scope of the change.

---

## Versioning (CalVer)

Firefly Framework uses **Calendar Versioning** in `YY.MM.PATCH` format:

| Segment | Meaning | Example |
|---------|--------------------------------|----------|
| `YY` | Two-digit year of the release | `26` |
| `MM` | Two-digit month of the release | `01` |
| `PATCH` | Incremental patch number | `01` |

A full version looks like **`26.02.03`** (January 2026, first patch).

- The `develop` branch always carries a `-SNAPSHOT` suffix (e.g., `26.02.00-SNAPSHOT`).
- Release branches drop the `-SNAPSHOT` suffix when they are finalized.
- Hotfix patches increment only the `PATCH` segment.

---

## Code Standards

### Java

- **Reactive first.** All I/O-bound code must return `Mono<T>` or `Flux<T>` (Project Reactor). Blocking calls are not permitted in reactive chains.
- **Lombok annotations.** Use `@Data`, `@Builder`, `@Value`, `@Slf4j`, and related annotations to reduce boilerplate. Do not write manual getters/setters when Lombok can generate them.
- **Javadoc on public API.** Every public class and public method must have a Javadoc comment explaining its purpose, parameters, and return value.
- **Apache 2.0 license header.** Every new Java source file must include the standard Apache 2.0 header at the top:
  ```java
  /*
   * Copyright 2024-2026 Firefly Software Solutions Inc.
   *
   * Licensed under the Apache License, Version 2.0 (the "License");
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   * http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an "AS IS" BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   */
  ```

### Python

- **Ruff** for linting and formatting. Run `ruff check .` and `ruff format .` before committing.
- **Pyright** for static type checking. All public functions must have complete type annotations, and `pyright` must report zero errors.

### Go

- **`go vet`** must pass with no findings.
- **Cobra** is the standard library for CLI command structure. All new CLI commands must be implemented as Cobra commands.

---

## Commit Conventions

All commits must follow the format:

```
<type>: <summary>
```

Where `<type>` is one of:

| Type | When to Use |
|------------|------------------------------------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation-only changes |
| `refactor` | Code restructuring with no behavior change |
| `test` | Adding or updating tests |
| `ci` | CI/CD pipeline changes |
| `chore` | Maintenance tasks (dependency bumps, etc.) |

### Examples

```
feat: add retry policy to transactional engine
fix: resolve NPE in R2DBC connection pool cleanup
docs: update module catalog with new webhooks module
refactor: extract saga step builder into shared utility
test: add integration tests for event sourcing projections
ci: add Java 25 to build matrix
chore: bump Spring Boot to 3.5.10
```

The summary should be lowercase, imperative mood, and no longer than 72 characters.

---

Thank you for contributing to Firefly Framework! If you have questions, open a thread in [GitHub Discussions](https://github.com/orgs/fireflyframework/discussions).
