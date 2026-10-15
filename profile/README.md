<a href="https://fireflyframework.org/">
<picture>
  <source media="(max-width: 640px) and (prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/banner-narrow-dark.svg">
  <source media="(max-width: 640px)" srcset="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/banner-narrow-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/banner-dark.svg">
  <img src="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/banner-light.svg" alt="Framework by Firefly. One architecture. Five languages: Java, Python, PHP, Rust, and .NET." width="100%">
</picture>
</a>

# Firefly Framework

Build services in Java, Python, PHP, Rust, or .NET with a shared approach to application architecture. Each framework follows its language's conventions and builds on a native stack your team can keep using.

The frameworks handle composition, command and query dispatch, persistence, messaging, and multi-step operations around your business code. Your team writes the domain rules and chooses its infrastructure. Capabilities and release maturity differ by framework; each project's documentation defines what it supports.

[Website](https://fireflyframework.org/) · [Choose a framework](https://fireflyframework.org/#frameworks) · [Architecture](https://fireflyframework.org/#architecture) · [Books](https://fireflyframework.org/#books)

## Choose your language

| Framework | Native foundation | Explore |
| --- | --- | --- |
| <a href="https://fireflyframework.org/frameworks/java/"><picture><source media="(prefers-color-scheme: dark)" srcset="https://fireflyframework.org/brand/frameworks/java-dark.svg"><img src="https://fireflyframework.org/brand/frameworks/java-light.svg" alt="jafly by Firefly" width="130"></picture></a> | Java · Spring Boot and WebFlux | [Guide](https://fireflyframework.org/frameworks/java/) · [Modules](https://github.com/fireflyframework/.github/blob/main/docs/MODULE_CATALOG.md) |
| <a href="https://fireflyframework.org/frameworks/python/"><picture><source media="(prefers-color-scheme: dark)" srcset="https://fireflyframework.org/brand/frameworks/python-dark.svg"><img src="https://fireflyframework.org/brand/frameworks/python-light.svg" alt="pyfly by Firefly" width="130"></picture></a> | Python · Starlette or FastAPI | [Guide](https://fireflyframework.org/frameworks/python/) · [Source](https://github.com/fireflyframework/fireflyframework-pyfly) |
| <a href="https://fireflyframework.org/frameworks/php/"><picture><source media="(prefers-color-scheme: dark)" srcset="https://fireflyframework.org/brand/frameworks/php-dark.svg"><img src="https://fireflyframework.org/brand/frameworks/php-light.svg" alt="larafly by Firefly" width="130"></picture></a> | PHP · Laravel | [Guide](https://fireflyframework.org/frameworks/php/) · [Source](https://github.com/fireflyframework/fireflyframework-php) |
| <a href="https://fireflyframework.org/frameworks/rust/"><picture><source media="(prefers-color-scheme: dark)" srcset="https://fireflyframework.org/brand/frameworks/rust-dark.svg"><img src="https://fireflyframework.org/brand/frameworks/rust-light.svg" alt="rsfly by Firefly" width="130"></picture></a> | Rust · Tokio and Axum | [Guide](https://fireflyframework.org/frameworks/rust/) · [Source](https://github.com/fireflyframework/fireflyframework-rust) |
| <a href="https://fireflyframework.org/frameworks/dotnet/"><picture><source media="(prefers-color-scheme: dark)" srcset="https://fireflyframework.org/brand/frameworks/dotnet-dark.svg"><img src="https://fireflyframework.org/brand/frameworks/dotnet-light.svg" alt="netfly by Firefly" width="130"></picture></a> | C# · ASP.NET Core | [Guide](https://fireflyframework.org/frameworks/dotnet/) · [Source](https://github.com/fireflyframework/fireflyframework-dotnet) |

jafly spans the modular Java repositories. Start with its [setup guide](https://github.com/fireflyframework/.github/blob/main/docs/GETTING_STARTED.md), [parent project](https://github.com/fireflyframework/fireflyframework-parent), and [CLI](https://github.com/fireflyframework/fireflyframework-cli). The other language implementations each have their own repository and installation guide. pyfly distributes through [GitHub Releases](https://github.com/fireflyframework/fireflyframework-pyfly/releases).

## How a service fits together

<picture>
  <source media="(max-width: 640px) and (prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/architecture-narrow-dark.svg">
  <source media="(max-width: 640px)" srcset="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/architecture-narrow-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/architecture-dark.svg">
  <img src="https://raw.githubusercontent.com/fireflyframework/.github/main/profile/assets/architecture-light.svg" alt="Conceptual application architecture: delivery boundaries reach application capabilities and domain rules; adapters connect providers and persistence. Each framework has its own modules." width="100%">
</picture>

*Conceptual architecture shared by the family. Each implementation supplies its own modules and integrations.*

Domain logic stays separate from transport and provider code. The native libraries still route requests and run database transactions. For operations that span services, the frameworks provide compensating sagas; your application defines the compensating actions.

## Build, run agents, and coordinate processes

| Project | What it does | Explore |
| --- | --- | --- |
| Firefly Forge | A software factory for pyfly and larafly. Give a coding agent a bounded task, run the project's checks, and review the recorded change before delivery. | [Guide](https://fireflyframework.org/forge/) · [Source](https://github.com/fireflyframework/firefly-forge) |
| Firefly Agentic | A Python library on Pydantic AI for agents with tools, memory, and retrieval. Your application collects approvals for tools that need them. | [Guide](https://fireflyframework.org/agentic/) · [Source](https://github.com/fireflyframework/fireflyframework-agentic) |
| Firefly Weave | Business processes across systems and people. Author workflows in Studio, YAML, JSON, or Python; runs retain their history while waiting for events and human tasks. | [Guide](https://fireflyframework.org/weave/) · [Source](https://github.com/fireflyframework/firefly-weave) |

[Firefly Agent Bridge](https://github.com/fireflyframework/firefly-agent-bridge) connects applications and Forge to a developer's signed-in coding CLI. The [Java Agentic Bridge](https://github.com/fireflyframework/fireflyframework-agentic-bridge) connects Java services to an HTTP agent service.

## Learn by building

<p>
  <a href="https://fireflyframework.org/frameworks/java/#book"><img src="https://fireflyframework.org/assets/books/java.png" alt="jafly by example: Java and Spring Boot" width="23%"></a>
  <a href="https://fireflyframework.org/frameworks/python/#book"><img src="https://fireflyframework.org/assets/books/python.png" alt="pyfly by example: Python" width="23%"></a>
  <a href="https://fireflyframework.org/frameworks/php/#book"><img src="https://fireflyframework.org/assets/books/php.png" alt="larafly by example: PHP and Laravel" width="23%"></a>
  <a href="https://fireflyframework.org/frameworks/rust/#book"><img src="https://fireflyframework.org/assets/books/rust.png" alt="rsfly by example: Rust" width="23%"></a>
</p>

Four *by example* books are available in English and Spanish, in PDF and EPUB. jafly follows a lending service; pyfly and larafly build a wallet and ledger; rsfly builds a ledger on Tokio, Axum, and SQLx. Each framework's book page links to its editions and companion sample.

Choose a language, follow its installation guide, and run one sample service. Then add the modules your application needs. The [framework pages](https://fireflyframework.org/#frameworks) link to documentation, source examples, and release information.

## Contribute and follow the work

Open issues and pull requests in the project you use. Read the [contribution guide](https://github.com/fireflyframework/.github/blob/main/CONTRIBUTING.md), follow the [code of conduct](https://github.com/fireflyframework/.github/blob/main/CODE_OF_CONDUCT.md), and use the [security policy](https://github.com/fireflyframework/.github/blob/main/SECURITY.md) to report vulnerabilities privately.

The Firefly Software Foundation maintains the frameworks. [Firefly Software](https://fireflysoftware.io/) builds its banking and insurance services on them, with business modules in [Firefly OpenPlatform](https://github.com/firefly-oss). Read [how the project began](https://fireflyframework.org/about/).

<sub>Each project defines its own license. The Firefly and Framework visual identities remain proprietary to Firefly Software Solutions Inc.</sub>
