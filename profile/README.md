# Firefly Framework

**Enterprise-grade reactive framework with distributed transactions, event-driven patterns, and battle-tested reliability. Built for mission-critical systems that power the world's most demanding applications -- from fintech to healthcare to large-scale SaaS platforms.**

---

## About

Firefly Framework is a modular Spring Boot superset that provides production-ready building blocks for designing, developing, and operating mission-critical distributed systems. Every module is built on reactive foundations (Spring WebFlux, Project Reactor) and follows established enterprise patterns including CQRS, Event Sourcing, Saga/TCC, and Event-Driven Architecture.

The framework is designed around a clear separation of concerns: each module addresses a single responsibility, ships as an independent artifact, and integrates seamlessly with the rest of the ecosystem through the parent POM and BOM.

## Module Overview

### Build Infrastructure

| Repository | Purpose |
|---|---|
| **fireflyframework-parent** | Parent POM managing Spring Boot 3.5, Spring Cloud 2025, Java 21, and all shared plugin/dependency configuration |
| **fireflyframework-bom** | Bill of Materials for conflict-free version alignment across all framework modules |

### Core Framework

| Repository | Purpose |
|---|---|
| **fireflyframework-core** | Actuator configuration, health indicators, service registry, web client resilience, and observability foundations |
| **fireflyframework-domain** | Domain-Driven Design primitives: base entities, value objects, aggregate roots, and domain event publishing |
| **fireflyframework-utils** | Shared utilities, template rendering, and common helper functions |
| **fireflyframework-validators** | Annotation-based validators for financial, identity, and general-purpose data formats |
| **fireflyframework-plugins** | Lightweight plugin system with annotation-based discovery and hot-loadable JAR/Spring Bean loaders |

### Reactive Infrastructure

| Repository | Purpose |
|---|---|
| **fireflyframework-cache** | Unified caching abstraction with Caffeine, Redis, Hazelcast, and JCache adapters |
| **fireflyframework-r2dbc** | Reactive database support with R2DBC auto-configuration and PostgreSQL integration |
| **fireflyframework-web** | Spring WebFlux starter with exception handling, idempotency, PII masking, and OpenAPI support |
| **fireflyframework-client** | Reactive service client for REST, SOAP, and gRPC with circuit breakers and load balancing |

### Distributed Patterns

| Repository | Purpose |
|---|---|
| **fireflyframework-eda** | Event-Driven Architecture with Kafka/RabbitMQ, dead-letter queues, and Protobuf serialization |
| **fireflyframework-cqrs** | CQRS implementation with command/query bus, authorization, caching, and metrics |
| **fireflyframework-eventsourcing** | Event Sourcing with reactive event store, snapshots, projections, and outbox pattern |
| **fireflyframework-transactional-engine** | Distributed transactions via Saga and TCC with compensation, backpressure, and persistence |
| **fireflyframework-workflow** | Workflow orchestration with AOP-based definitions, state persistence, and scheduling |
| **fireflyframework-data** | Data processing with job orchestration, enrichment pipelines, and batch/async workloads |

### Enterprise Content Management

| Repository | Purpose |
|---|---|
| **fireflyframework-ecm** | Document storage, versioning, permissions, and search abstractions |
| **fireflyframework-ecm-storage-aws** | Amazon S3 storage adapter |
| **fireflyframework-ecm-storage-azure** | Azure Blob Storage adapter |
| **fireflyframework-ecm-esignature-adobe-sign** | Adobe Sign eSignature adapter |
| **fireflyframework-ecm-esignature-docusign** | DocuSign eSignature adapter |
| **fireflyframework-ecm-esignature-logalty** | Logalty certified eSignature adapter |

### Identity Provider

| Repository | Purpose |
|---|---|
| **fireflyframework-idp** | IDP abstraction layer with ports and DTOs for authentication and authorization |
| **fireflyframework-idp-aws-cognito** | AWS Cognito adapter |
| **fireflyframework-idp-internal-db** | Database-backed IDP with R2DBC, JWT tokens, and Flyway migrations |
| **fireflyframework-idp-keycloak** | Keycloak Admin API adapter |

### Notifications

| Repository | Purpose |
|---|---|
| **fireflyframework-notifications** | Notification abstractions for email, SMS, and push delivery |
| **fireflyframework-notifications-firebase** | Firebase Cloud Messaging push adapter |
| **fireflyframework-notifications-resend** | Resend email adapter |
| **fireflyframework-notifications-sendgrid** | SendGrid email adapter |
| **fireflyframework-notifications-twilio** | Twilio SMS adapter |

## Getting Started

Add the parent POM to your project:

```xml
<parent>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</parent>
```

Or import the BOM for version management only:

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

Then add the modules you need:

```xml
<dependency>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-eda</artifactId>
</dependency>
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

## License

All Firefly Framework modules are released under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

Copyright 2024-2026 Firefly Software Solutions Inc.
