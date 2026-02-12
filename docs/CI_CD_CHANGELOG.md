# CI/CD Changelog

History of CI/CD changes, fixes, and improvements across the Firefly Framework.

---

## 26.02.04 — Centralized Observability

Released: February 2026

### New Module

**`fireflyframework-observability`** — Centralized observability foundation providing unified metrics, tracing, health indicators, structured logging, and reactive context propagation for the entire Firefly ecosystem.

### What Changed

**1. New `fireflyframework-observability` module (39th Java repo)**
Single-dependency module that replaces scattered observability code across 17 projects. Provides:
- `FireflyMetricsSupport` — abstract base for all module metrics with `firefly.{module}.{metric}` naming
- `FireflyTracingSupport` — reactive-safe tracing via Micrometer Observation API
- `FireflyHealthIndicator` — abstract base for health indicators with standard thresholds
- `FireflyObservabilityEnvironmentPostProcessor` — config-based tracing bridge selection (OTEL/BRAVE) and metrics exporter selection (PROMETHEUS/OTLP/BOTH)
- `ReactiveContextPropagationAutoConfiguration` — enables `Hooks.enableAutomaticContextPropagation()` to fix reactive/ThreadLocal context bridging
- `TracingWebClientCustomizer` — automatic trace propagation on all WebClient calls
- Shared `logback-firefly.xml` for consistent structured JSON logging
- Default Spring profile `application-firefly-observability.yml` with actuator, tracing, and metrics defaults

**2. Config-based tracing bridge selection (no POM changes needed)**
Both OpenTelemetry and Brave bridges ship on the classpath. `firefly.observability.tracing.bridge=OTEL|BRAVE` controls which is active at startup via auto-configuration exclusions.

**3. Config-based metrics exporter selection**
Both Prometheus and OTLP metrics registries ship on the classpath. `firefly.observability.metrics.exporter=PROMETHEUS|OTLP|BOTH` controls which is active. Default: Prometheus (`/actuator/prometheus`).

**4. OTLP transport selection (gRPC default, HTTP fallback)**
Both gRPC and HTTP/protobuf senders are on the classpath. Default: gRPC on port 4317. Switch via `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf` for HTTP on port 4318. Designed for open-source `otel/opentelemetry-collector-contrib`.

**5. Reactive context propagation fix**
`Hooks.enableAutomaticContextPropagation()` enabled by default via auto-configuration. This is the canonical fix for ThreadLocal/MDC values being lost across reactor thread boundaries — eliminates all manual MDC management in reactive chains.

**6. Metric naming and tag standardization**
- Fixed 5 modules with non-standard metric prefixes (`event.store.*` → `firefly.eventsourcing.*`, `webhooks.*` → `firefly.webhooks.*`, `service.client.*` → `firefly.client.*`)
- Fixed tag naming violations: `publisher_type` → `publisher.type`, `workflowId` → `workflow.id`, `error_type` → `error.type`

**7. Duplicate logback configurations replaced**
6 identical `logback-spring.xml` files across modules replaced with thin `<include resource="logback-firefly.xml"/>` wrappers.

### DAG Changes

- Added `observability` to Layer 1 (depends only on parent)
- Added edges from 17 modules to `observability`: eda, client, transactional-engine, ecm, cqrs, web, workflow, eventsourcing, application, core, domain, data, webhooks, callbacks, backoffice, and more
- **Layer shift:** eda, client, transactional-engine, ecm moved from Layer 1 → Layer 2; workflow, application, ECM impls cascaded from Layer 2 → Layer 3
- Total repos: 38 → 39 Java (41 including CLI and GenAI)
- Updated `cloner.go` repo list and 3 archetype templates

### Modules Migrated (17 repos with changes)

| Module | Key Changes |
|--------|------------|
| fireflyframework-eda | Extend `FireflyMetricsSupport`, fix `publisher_type` → `publisher.type` |
| fireflyframework-client | Extend `FireflyMetricsSupport`, fix prefix `service.client.*` → `firefly.client.*` |
| fireflyframework-transactional-engine | Extend `FireflyMetricsSupport`, replace manual span management |
| fireflyframework-cqrs | Extend base classes for metrics and health |
| fireflyframework-workflow | Extend base classes, fix `workflowId` → `workflow.id` |
| fireflyframework-eventsourcing | Delete direct OTel config, rewrite MDC context, fix prefix |
| fireflyframework-core | Move actuator configs to observability, fix WebClient trace propagation |
| fireflyframework-data | Fix ThreadLocal observation access, extend base classes |
| fireflyframework-webhooks | Rewrite tracing filter, fix prefix `webhooks.*` → `firefly.webhooks.*` |
| fireflyframework-application | Extend base classes, replace logback |
| fireflyframework-domain | Add observability dep, replace logback |
| fireflyframework-web | Add observability dep |
| fireflyframework-ecm | Add observability dep |
| fireflyframework-backoffice | Add observability dep |
| fireflyframework-callbacks | Add observability dep |
| fireflyframework-bom | Add observability to BOM |
| fireflyframework-cli | Add DAG edges, repo list, archetype updates |

### Documentation Updates

- Updated `CI_CD_GUIDE.md` — DAG layers table, repo counts (38 → 39 Java, 40 → 41 total)
- Updated `MODULE_CATALOG.md` — added observability module
- Updated `CI_STATUS.md` — added observability CI badge
- Updated `GETTING_STARTED.md` — repo count (38 → 39)
- Updated organization profile README — repo count (40 → 41)
- Created `additional-spring-configuration-metadata.json` with IDE hints for all `firefly.observability.*` properties

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
