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
```

**Enterprise-grade reactive framework with distributed transactions, event-driven patterns, and battle-tested reliability.**

Firefly Framework is a modular Spring Boot superset providing production-ready building blocks for mission-critical distributed systems. Built on Spring WebFlux and Project Reactor, every module ships as an independent artifact and follows established enterprise patterns -- CQRS, Event Sourcing, Saga/TCC, and Event-Driven Architecture.

### Highlights

- **Distributed Transactions** -- Saga and TCC orchestration with compensation and backpressure
- **Event-Driven Architecture** -- Kafka and RabbitMQ with dead-letter queues and Protobuf serialization
- **CQRS and Event Sourcing** -- Command/query separation with reactive event store and projections
- **Reactive from the ground up** -- Spring WebFlux, R2DBC, and Project Reactor throughout
- **Enterprise integrations** -- ECM, identity providers, notifications, caching, and workflow orchestration
- **Java 21** / **Spring Boot 3.5** / **Spring Cloud 2025**

### Quick Start

```xml
<parent>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</parent>
```

Then pick the modules you need. See the [full module catalog and getting started guide](https://github.com/fireflyframework/.github/blob/main/docs/MODULE_CATALOG.md) for details.

### License

Apache License 2.0 -- Copyright 2024-2026 Firefly Software Solutions Inc.
