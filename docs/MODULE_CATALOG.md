# Firefly Framework -- Module Catalog

Complete reference of all framework modules, organized by capability.

## Build Infrastructure

| Repository | Purpose |
|---|---|
| [fireflyframework-parent](https://github.com/fireflyframework/fireflyframework-parent) | Parent POM managing Spring Boot 3.5, Spring Cloud 2025, Java 21, and all shared plugin/dependency configuration |
| [fireflyframework-bom](https://github.com/fireflyframework/fireflyframework-bom) | Bill of Materials for conflict-free version alignment across all framework modules |

## Runtime Infrastructure

| Repository | Purpose |
|---|---|
| [fireflyframework-config-server](https://github.com/fireflyframework/fireflyframework-config-server) | Spring Cloud Config Server for centralized configuration management across microservices with hierarchical native profiles |

## Core Framework

| Repository | Purpose |
|---|---|
| [fireflyframework-core](https://github.com/fireflyframework/fireflyframework-core) | Actuator configuration, health indicators, service registry, web client resilience, and observability foundations |
| [fireflyframework-domain](https://github.com/fireflyframework/fireflyframework-domain) | Domain-Driven Design primitives: base entities, value objects, aggregate roots, and domain event publishing |
| [fireflyframework-utils](https://github.com/fireflyframework/fireflyframework-utils) | Shared utilities, template rendering, and common helper functions |
| [fireflyframework-validators](https://github.com/fireflyframework/fireflyframework-validators) | Annotation-based validators for financial, identity, and general-purpose data formats |
| [fireflyframework-plugins](https://github.com/fireflyframework/fireflyframework-plugins) | Lightweight plugin system with annotation-based discovery and hot-loadable JAR/Spring Bean loaders |

## Application Layer

| Repository | Purpose |
|---|---|
| [fireflyframework-application](https://github.com/fireflyframework/fireflyframework-application) | Application layer library enabling business process-oriented microservices with plugin architecture, security aspects, and configuration resolution |
| [fireflyframework-backoffice](https://github.com/fireflyframework/fireflyframework-backoffice) | Backoffice and internal portal extension with context resolution and resource controller abstractions |

## Reactive Infrastructure

| Repository | Purpose |
|---|---|
| [fireflyframework-cache](https://github.com/fireflyframework/fireflyframework-cache) | Unified caching abstraction with Caffeine, Redis, Hazelcast, and JCache adapters |
| [fireflyframework-r2dbc](https://github.com/fireflyframework/fireflyframework-r2dbc) | Reactive database support with R2DBC auto-configuration and PostgreSQL integration |
| [fireflyframework-web](https://github.com/fireflyframework/fireflyframework-web) | Spring WebFlux starter with exception handling, idempotency, PII masking, and OpenAPI support |
| [fireflyframework-client](https://github.com/fireflyframework/fireflyframework-client) | Reactive service client for REST, SOAP, and gRPC with circuit breakers and load balancing |

## Distributed Patterns

| Repository | Purpose |
|---|---|
| [fireflyframework-eda](https://github.com/fireflyframework/fireflyframework-eda) | Event-Driven Architecture with Kafka/RabbitMQ, dead-letter queues, and Protobuf serialization |
| [fireflyframework-cqrs](https://github.com/fireflyframework/fireflyframework-cqrs) | CQRS implementation with command/query bus, authorization, caching, and metrics |
| [fireflyframework-eventsourcing](https://github.com/fireflyframework/fireflyframework-eventsourcing) | Event Sourcing with reactive event store, snapshots, projections, and outbox pattern |
| [fireflyframework-transactional-engine](https://github.com/fireflyframework/fireflyframework-transactional-engine) | Distributed transactions via Saga and TCC with compensation, backpressure, and persistence |
| [fireflyframework-workflow](https://github.com/fireflyframework/fireflyframework-workflow) | Workflow orchestration with AOP-based definitions, state persistence, and scheduling |
| [fireflyframework-data](https://github.com/fireflyframework/fireflyframework-data) | Data processing with job orchestration, enrichment pipelines, and batch/async workloads |

## Business Rules

| Repository | Purpose |
|---|---|
| [fireflyframework-rule-engine](https://github.com/fireflyframework/fireflyframework-rule-engine) | YAML DSL-based rule engine with AST processing, Python compilation, audit trails, and reactive APIs for dynamic business rule evaluation |

## Enterprise Content Management

| Repository | Purpose |
|---|---|
| [fireflyframework-ecm](https://github.com/fireflyframework/fireflyframework-ecm) | Document storage, versioning, permissions, and search abstractions |
| [fireflyframework-ecm-storage-aws](https://github.com/fireflyframework/fireflyframework-ecm-storage-aws) | Amazon S3 storage adapter |
| [fireflyframework-ecm-storage-azure](https://github.com/fireflyframework/fireflyframework-ecm-storage-azure) | Azure Blob Storage adapter |
| [fireflyframework-ecm-esignature-adobe-sign](https://github.com/fireflyframework/fireflyframework-ecm-esignature-adobe-sign) | Adobe Sign eSignature adapter |
| [fireflyframework-ecm-esignature-docusign](https://github.com/fireflyframework/fireflyframework-ecm-esignature-docusign) | DocuSign eSignature adapter |
| [fireflyframework-ecm-esignature-logalty](https://github.com/fireflyframework/fireflyframework-ecm-esignature-logalty) | Logalty certified eSignature adapter |

## Identity Provider

| Repository | Purpose |
|---|---|
| [fireflyframework-idp](https://github.com/fireflyframework/fireflyframework-idp) | IDP abstraction layer with ports and DTOs for authentication and authorization |
| [fireflyframework-idp-aws-cognito](https://github.com/fireflyframework/fireflyframework-idp-aws-cognito) | AWS Cognito adapter |
| [fireflyframework-idp-internal-db](https://github.com/fireflyframework/fireflyframework-idp-internal-db) | Database-backed IDP with R2DBC, JWT tokens, and Flyway migrations |
| [fireflyframework-idp-keycloak](https://github.com/fireflyframework/fireflyframework-idp-keycloak) | Keycloak Admin API adapter |

## Notifications

| Repository | Purpose |
|---|---|
| [fireflyframework-notifications](https://github.com/fireflyframework/fireflyframework-notifications) | Notification abstractions for email, SMS, and push delivery |
| [fireflyframework-notifications-firebase](https://github.com/fireflyframework/fireflyframework-notifications-firebase) | Firebase Cloud Messaging push adapter |
| [fireflyframework-notifications-resend](https://github.com/fireflyframework/fireflyframework-notifications-resend) | Resend email adapter |
| [fireflyframework-notifications-sendgrid](https://github.com/fireflyframework/fireflyframework-notifications-sendgrid) | SendGrid email adapter |
| [fireflyframework-notifications-twilio](https://github.com/fireflyframework/fireflyframework-notifications-twilio) | Twilio SMS adapter |

## Integration

| Repository | Purpose |
|---|---|
| [fireflyframework-webhooks](https://github.com/fireflyframework/fireflyframework-webhooks) | Reactive webhook ingestion with provider-agnostic routing, message queue integration, rate limiting, and comprehensive observability |
| [fireflyframework-callbacks](https://github.com/fireflyframework/fireflyframework-callbacks) | Outbound webhook management for dispatching events to external systems with circuit breakers, retry logic, and domain authorization |

## Tooling & Automation

| Repository | Purpose |
|---|---|
| [fireflyframework-cli](https://github.com/fireflyframework/fireflyframework-cli) | Go-based CLI for scaffolding, building, and managing Firefly Framework projects with dependency-aware build orchestration |
| [.github](https://github.com/fireflyframework/.github) | Organization profile, documentation, and community health files |

## Getting Started

### Option 1: Inherit the Parent POM (recommended)

```xml
<parent>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <relativePath/>
</parent>
```

This gives your project all managed dependency versions, plugin configurations, and annotation processor wiring.

### Option 2: Import the BOM only

If your project already has its own parent POM:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.fireflyframework</groupId>
            <artifactId>fireflyframework-bom</artifactId>
            <version>1.0.0-SNAPSHOT</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### Add modules

Then declare only the modules you need -- no version tags required:

```xml
<dependencies>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-eda</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-cqrs</artifactId>
    </dependency>
</dependencies>
```

## Technology Stack

- **Java 21** with virtual threads support
- **Spring Boot 3.5.9** / **Spring Cloud 2025.0.1**
- **Spring WebFlux** and **Project Reactor** for reactive programming
- **R2DBC** for non-blocking database access
- **Kafka** and **RabbitMQ** for event-driven messaging
- **Redis**, **Caffeine**, **Hazelcast** for caching
- **Resilience4j** for circuit breakers and fault tolerance
- **Testcontainers** for integration testing
- **gRPC** and **Protobuf** for high-performance service communication
