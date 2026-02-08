```
  _____.__                _____.__                            
_/ ____\__|______   _____/ ____\  | ___.__.                   
\   __\|  \_  __ \_/ __ \   __\|  |<   |  |                   
 |  |  |  ||  | \/\  ___/|  |  |  |_\___  |                   
 |__|  |__||__|    \___  >__|  |____/ ____|                   
                       \/           \/                        
  _____                                                 __    
_/ ____\___________    _____   ______  _  _____________|  | __
\   __\\_  __ \__  \  /     \_/ __ \ \/ \/ /  _ \_  __ \  |/ /
 |  |   |  | \// __ \|  Y Y  \  ___/\     (  <_> )  | \/    < 
 |__|   |__|  (____  /__|_|  /\___  >\/\_/ \____/|__|  |__|_ \
                   \/      \/     \/                        \/
 --------------------------> Enterprise software made easy  <-
```

**Enterprise-grade reactive framework with distributed transactions, event-driven patterns, and battle-tested reliability.**

Firefly Framework is a modular Spring Boot superset spanning **40 repositories** and providing production-ready building blocks for mission-critical distributed systems. Built on Spring WebFlux and Project Reactor, every module ships as an independent artifact and follows established enterprise patterns -- CQRS, Event Sourcing, Saga/TCC, and Event-Driven Architecture.

### Highlights

- **Distributed Transactions** -- Saga and TCC orchestration with compensation and backpressure
- **Event-Driven Architecture** -- Kafka and RabbitMQ with dead-letter queues and Protobuf serialization
- **CQRS and Event Sourcing** -- Command/query separation with reactive event store and projections
- **Reactive from the ground up** -- Spring WebFlux, R2DBC, and Project Reactor throughout
- **Enterprise integrations** -- ECM, identity providers, notifications, caching, and workflow orchestration
- **Java 25** (default, Java 21+ compatible) / **Spring Boot 3.5.9** / **Spring Cloud 2025**

### Installation

The fastest way to get started is with the **[Firefly CLI](https://github.com/fireflyframework/fireflyframework-cli)** (`flywork`):

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/fireflyframework/fireflyframework-cli/main/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/fireflyframework/fireflyframework-cli/main/install.ps1 | iex
```

Then bootstrap the entire framework into your local environment:

```bash
flywork setup              # clones all repos in dependency order and installs to ~/.m2
flywork create core        # scaffold a new microservice from a built-in archetype
flywork doctor             # verify your environment (Java, Maven, Git, etc.)
```

Four project archetypes are available: **core**, **domain**, **application**, and **library**. See the [CLI documentation](https://github.com/fireflyframework/fireflyframework-cli) for full details.

### Quick Start (Maven)

```xml
<parent>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</parent>
```

Then pick the modules you need. See the [full module catalog and getting started guide](https://github.com/fireflyframework/.github/blob/main/docs/MODULE_CATALOG.md) for details.

### GenAI

Firefly Framework also provides **[fireflyframework-genai](https://github.com/fireflyframework/fireflyframework-genai)** -- a production-grade GenAI metaframework built on [Pydantic AI](https://ai.pydantic.dev/). It extends Pydantic AI with six composable layers covering agents, tools, reasoning patterns (ReAct, CoT, Plan-and-Execute, and more), DAG pipeline orchestration, observability, and REST / message-queue exposure -- so you can build, validate, and deploy intelligent agents without coupling domain logic to infrastructure.

```bash
curl -fsSL https://raw.githubusercontent.com/fireflyframework/fireflyframework-genai/main/install.sh | bash
```

### License

Apache License 2.0 -- Copyright 2024-2026 Firefly Software Solutions Inc.
