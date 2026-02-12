# CI Status

Live build status for every repository in the Firefly Framework organization.

## Foundation

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-parent](https://github.com/fireflyframework/fireflyframework-parent) | Parent POM managing Spring Boot 3.5, Spring Cloud 2025, Java 21+ versions, plugin configuration, and dependency alignment | [![CI](https://github.com/fireflyframework/fireflyframework-parent/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-parent/actions/workflows/ci.yml) |
| [fireflyframework-bom](https://github.com/fireflyframework/fireflyframework-bom) | Bill of Materials (BOM) for conflict-free versioning across all modules | [![CI](https://github.com/fireflyframework/fireflyframework-bom/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-bom/actions/workflows/ci.yml) |
| [fireflyframework-utils](https://github.com/fireflyframework/fireflyframework-utils) | Shared utility library with template rendering, filtering annotations, and common helpers | [![CI](https://github.com/fireflyframework/fireflyframework-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-utils/actions/workflows/ci.yml) |
| [fireflyframework-validators](https://github.com/fireflyframework/fireflyframework-validators) | Annotation-based validators for financial, identity, and general-purpose data formats | [![CI](https://github.com/fireflyframework/fireflyframework-validators/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-validators/actions/workflows/ci.yml) |
| [fireflyframework-plugins](https://github.com/fireflyframework/fireflyframework-plugins) | Annotation-based plugin discovery, dependency resolution, and hot-loadable JAR/Spring Bean loaders | [![CI](https://github.com/fireflyframework/fireflyframework-plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-plugins/actions/workflows/ci.yml) |

## Observability

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-observability](https://github.com/fireflyframework/fireflyframework-observability) | Centralized metrics, tracing, health indicators, structured logging, and reactive context propagation with config-based OTel/Brave bridge and Prometheus/OTLP exporter selection | [![CI](https://github.com/fireflyframework/fireflyframework-observability/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-observability/actions/workflows/ci.yml) |

## Core Modules

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-core](https://github.com/fireflyframework/fireflyframework-core) | Actuator configuration, health indicators, service registry, web client resilience, and observability | [![CI](https://github.com/fireflyframework/fireflyframework-core/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-core/actions/workflows/ci.yml) |
| [fireflyframework-domain](https://github.com/fireflyframework/fireflyframework-domain) | DDD foundation with base entities, value objects, aggregate roots, and reactive domain event publishing | [![CI](https://github.com/fireflyframework/fireflyframework-domain/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-domain/actions/workflows/ci.yml) |
| [fireflyframework-data](https://github.com/fireflyframework/fireflyframework-data) | Job orchestration, enrichment pipelines, CQRS integration, and observability for batch/async workloads | [![CI](https://github.com/fireflyframework/fireflyframework-data/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-data/actions/workflows/ci.yml) |
| [fireflyframework-application](https://github.com/fireflyframework/fireflyframework-application) | Application layer for business process-oriented microservices with plugin architecture and security aspects | [![CI](https://github.com/fireflyframework/fireflyframework-application/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-application/actions/workflows/ci.yml) |
| [fireflyframework-backoffice](https://github.com/fireflyframework/fireflyframework-backoffice) | Backoffice and internal portal extension with context resolution and resource controller abstractions | [![CI](https://github.com/fireflyframework/fireflyframework-backoffice/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-backoffice/actions/workflows/ci.yml) |

## Data & Persistence

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-r2dbc](https://github.com/fireflyframework/fireflyframework-r2dbc) | Reactive R2DBC auto-configuration with connection pooling and PostgreSQL integration | [![CI](https://github.com/fireflyframework/fireflyframework-r2dbc/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-r2dbc/actions/workflows/ci.yml) |
| [fireflyframework-cache](https://github.com/fireflyframework/fireflyframework-cache) | Pluggable Caffeine, Redis, Hazelcast, and JCache adapters with multi-tier cache strategies | [![CI](https://github.com/fireflyframework/fireflyframework-cache/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-cache/actions/workflows/ci.yml) |
| [fireflyframework-cqrs](https://github.com/fireflyframework/fireflyframework-cqrs) | Command/query bus with handler registry, authorization, caching, and metrics instrumentation | [![CI](https://github.com/fireflyframework/fireflyframework-cqrs/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-cqrs/actions/workflows/ci.yml) |
| [fireflyframework-eventsourcing](https://github.com/fireflyframework/fireflyframework-eventsourcing) | Reactive event store with snapshots, projections, outbox pattern, and multi-tenancy over R2DBC | [![CI](https://github.com/fireflyframework/fireflyframework-eventsourcing/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-eventsourcing/actions/workflows/ci.yml) |
| [fireflyframework-transactional-engine](https://github.com/fireflyframework/fireflyframework-transactional-engine) | Saga and TCC distributed transactions with reactive orchestration, compensation, and backpressure | [![CI](https://github.com/fireflyframework/fireflyframework-transactional-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-transactional-engine/actions/workflows/ci.yml) |

## Web & Messaging

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-web](https://github.com/fireflyframework/fireflyframework-web) | Spring WebFlux starter with RFC 7807, request idempotency, PII masking, and OpenAPI auto-configuration | [![CI](https://github.com/fireflyframework/fireflyframework-web/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-web/actions/workflows/ci.yml) |
| [fireflyframework-eda](https://github.com/fireflyframework/fireflyframework-eda) | Kafka and RabbitMQ publishers/consumers with dead-letter queues, event filtering, and Protobuf serialization | [![CI](https://github.com/fireflyframework/fireflyframework-eda/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-eda/actions/workflows/ci.yml) |
| [fireflyframework-client](https://github.com/fireflyframework/fireflyframework-client) | Reactive REST, SOAP, and gRPC client with circuit breakers, load balancing, and chaos engineering | [![CI](https://github.com/fireflyframework/fireflyframework-client/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-client/actions/workflows/ci.yml) |
| [fireflyframework-config-server](https://github.com/fireflyframework/fireflyframework-config-server) | Spring Cloud Config Server for centralized configuration with hierarchical native profiles | [![CI](https://github.com/fireflyframework/fireflyframework-config-server/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-config-server/actions/workflows/ci.yml) |
| [fireflyframework-workflow](https://github.com/fireflyframework/fireflyframework-workflow) | Event-driven workflow orchestration with AOP definitions, state persistence, and distributed tracing | [![CI](https://github.com/fireflyframework/fireflyframework-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-workflow/actions/workflows/ci.yml) |

## ECM & Document Management

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-ecm](https://github.com/fireflyframework/fireflyframework-ecm) | Document storage, versioning, permissions, and search abstractions using hexagonal architecture | [![CI](https://github.com/fireflyframework/fireflyframework-ecm/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-ecm/actions/workflows/ci.yml) |
| [fireflyframework-ecm-esignature-adobe-sign](https://github.com/fireflyframework/fireflyframework-ecm-esignature-adobe-sign) | Adobe Sign eSignature adapter for digital signature workflows | [![CI](https://github.com/fireflyframework/fireflyframework-ecm-esignature-adobe-sign/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-ecm-esignature-adobe-sign/actions/workflows/ci.yml) |
| [fireflyframework-ecm-esignature-docusign](https://github.com/fireflyframework/fireflyframework-ecm-esignature-docusign) | DocuSign eSignature adapter for digital signature workflows | [![CI](https://github.com/fireflyframework/fireflyframework-ecm-esignature-docusign/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-ecm-esignature-docusign/actions/workflows/ci.yml) |
| [fireflyframework-ecm-esignature-logalty](https://github.com/fireflyframework/fireflyframework-ecm-esignature-logalty) | Logalty certified digital signature adapter | [![CI](https://github.com/fireflyframework/fireflyframework-ecm-esignature-logalty/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-ecm-esignature-logalty/actions/workflows/ci.yml) |
| [fireflyframework-ecm-storage-aws](https://github.com/fireflyframework/fireflyframework-ecm-storage-aws) | Amazon S3 storage adapter for document lifecycle management | [![CI](https://github.com/fireflyframework/fireflyframework-ecm-storage-aws/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-ecm-storage-aws/actions/workflows/ci.yml) |
| [fireflyframework-ecm-storage-azure](https://github.com/fireflyframework/fireflyframework-ecm-storage-azure) | Azure Blob Storage adapter for document lifecycle management | [![CI](https://github.com/fireflyframework/fireflyframework-ecm-storage-azure/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-ecm-storage-azure/actions/workflows/ci.yml) |

## Identity Providers

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-idp](https://github.com/fireflyframework/fireflyframework-idp) | IDP abstraction layer with ports and DTOs for authentication, authorization, and token operations | [![CI](https://github.com/fireflyframework/fireflyframework-idp/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-idp/actions/workflows/ci.yml) |
| [fireflyframework-idp-aws-cognito](https://github.com/fireflyframework/fireflyframework-idp-aws-cognito) | AWS Cognito adapter for authentication, user management, and token operations | [![CI](https://github.com/fireflyframework/fireflyframework-idp-aws-cognito/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-idp-aws-cognito/actions/workflows/ci.yml) |
| [fireflyframework-idp-internal-db](https://github.com/fireflyframework/fireflyframework-idp-internal-db) | Database-backed IDP with JWT tokens, role management, and Flyway migrations over R2DBC/PostgreSQL | [![CI](https://github.com/fireflyframework/fireflyframework-idp-internal-db/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-idp-internal-db/actions/workflows/ci.yml) |
| [fireflyframework-idp-keycloak](https://github.com/fireflyframework/fireflyframework-idp-keycloak) | Keycloak adapter for authentication, user management, and token operations via the Admin API | [![CI](https://github.com/fireflyframework/fireflyframework-idp-keycloak/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-idp-keycloak/actions/workflows/ci.yml) |

## Notifications

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-notifications](https://github.com/fireflyframework/fireflyframework-notifications) | Notification abstractions with ports and DTOs for email, SMS, and push delivery | [![CI](https://github.com/fireflyframework/fireflyframework-notifications/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-notifications/actions/workflows/ci.yml) |
| [fireflyframework-notifications-firebase](https://github.com/fireflyframework/fireflyframework-notifications-firebase) | Firebase Cloud Messaging (FCM) push notification adapter | [![CI](https://github.com/fireflyframework/fireflyframework-notifications-firebase/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-notifications-firebase/actions/workflows/ci.yml) |
| [fireflyframework-notifications-resend](https://github.com/fireflyframework/fireflyframework-notifications-resend) | Resend email delivery adapter | [![CI](https://github.com/fireflyframework/fireflyframework-notifications-resend/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-notifications-resend/actions/workflows/ci.yml) |
| [fireflyframework-notifications-sendgrid](https://github.com/fireflyframework/fireflyframework-notifications-sendgrid) | SendGrid email delivery adapter | [![CI](https://github.com/fireflyframework/fireflyframework-notifications-sendgrid/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-notifications-sendgrid/actions/workflows/ci.yml) |
| [fireflyframework-notifications-twilio](https://github.com/fireflyframework/fireflyframework-notifications-twilio) | Twilio SMS delivery adapter | [![CI](https://github.com/fireflyframework/fireflyframework-notifications-twilio/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-notifications-twilio/actions/workflows/ci.yml) |

## Business Logic

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-rule-engine](https://github.com/fireflyframework/fireflyframework-rule-engine) | YAML DSL-based rule engine with AST processing, Python compilation, and reactive APIs | [![CI](https://github.com/fireflyframework/fireflyframework-rule-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-rule-engine/actions/workflows/ci.yml) |
| [fireflyframework-webhooks](https://github.com/fireflyframework/fireflyframework-webhooks) | Reactive webhook ingestion with provider-agnostic routing, rate limiting, and observability | [![CI](https://github.com/fireflyframework/fireflyframework-webhooks/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-webhooks/actions/workflows/ci.yml) |
| [fireflyframework-callbacks](https://github.com/fireflyframework/fireflyframework-callbacks) | Outbound webhook dispatch with circuit breakers, retry logic, and domain authorization | [![CI](https://github.com/fireflyframework/fireflyframework-callbacks/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-callbacks/actions/workflows/ci.yml) |

## Tooling

| Repository | Description | CI |
|:---|:---|:---|
| [fireflyframework-cli](https://github.com/fireflyframework/fireflyframework-cli) | Cross-platform CLI (`flywork`) for environment setup, DAG builds, project scaffolding, and releases | [![CI](https://github.com/fireflyframework/fireflyframework-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-cli/actions/workflows/ci.yml) |
| [fireflyframework-genai](https://github.com/fireflyframework/fireflyframework-genai) | GenAI metaframework on Pydantic AI with agents, reasoning patterns, observability, and REST/queue exposure | [![CI](https://github.com/fireflyframework/fireflyframework-genai/actions/workflows/ci.yml/badge.svg)](https://github.com/fireflyframework/fireflyframework-genai/actions/workflows/ci.yml) |
