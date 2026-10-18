# Getting started with Jafly

[Jafly](https://github.com/fireflyframework/fireflyframework-jafly) is the Java implementation of the Firefly Framework. Its modules share one repository, one Maven reactor, and one parent/BOM release train. Other language frameworks retain their own monorepos.

## Prerequisites

Use JDK 25, Git, and Docker for the integration tests. The repository includes a Maven wrapper; an existing Maven 3.9+ installation is also supported. Source builds resolve internal modules within the reactor without a GitHub Packages token.

## Build from source

```sh
git clone https://github.com/fireflyframework/fireflyframework-jafly.git
cd fireflyframework-jafly
./mvnw -B -ntp clean install
```

This compiles the framework, runs the configured tests, and installs the parent, BOM, and libraries to your local Maven cache. The current development version is `26.10.17-SNAPSHOT`. See the [installation guide](https://fireflyframework.github.io/fireflyframework-jafly/installation/) for prerequisites and registry configuration, then build the [onboarding service](https://fireflyframework.github.io/fireflyframework-jafly/getting-started/).

## Set up with the CLI

Install `flywork` from the [CLI releases](https://github.com/fireflyframework/fireflyframework-cli/releases) using the [documented installer](https://github.com/fireflyframework/fireflyframework-cli#install), then run:

```sh
flywork setup
flywork doctor
flywork create core
```

The current CLI clones Jafly once and builds its full reactor. Existing legacy checkout directories are preserved. A successful setup saves the installed parent version for subsequent project scaffolding. Use the CLI's `FLYWORK_HOME` setting to isolate configuration and setup state when qualifying a new environment.

## Use the parent or BOM

After installing the source train locally, a new application can inherit:

```xml
<parent>
  <groupId>org.fireflyframework</groupId>
  <artifactId>fireflyframework-parent</artifactId>
  <version>26.10.17-SNAPSHOT</version>
  <relativePath/>
</parent>
```

Keep your application's own version independent. If it already inherits another parent, import `org.fireflyframework:fireflyframework-bom:26.10.17-SNAPSHOT` with `type=pom` and `scope=import` in dependency management instead. The [Maven guide](https://fireflyframework.github.io/fireflyframework-jafly/maven/) explains the full configuration and versioning contract.

Add only the modules you need, using their existing `org.fireflyframework` artifact IDs without individual versions when managed by the parent/BOM. The [module catalog](https://fireflyframework.github.io/fireflyframework-jafly/modules/) links every component's guide and source.

## Published artifacts

For final versions, consult [Jafly releases](https://github.com/fireflyframework/fireflyframework-jafly/releases) and their verified publication manifests. Authentication is necessary when resolving private or authenticated GitHub Packages artifacts. Reference environment variables in Maven settings to keep credentials out of source control. A local source installation needs no package token.

Original repository releases and pinned book examples remain historical records. Do not rewrite an existing release or assume its examples have been qualified on the new Boot 4 train.

## Continue

- [Framework documentation](https://fireflyframework.github.io/fireflyframework-jafly/)
- [Module catalog](MODULE_CATALOG.md)
- [CI/CD and releases](CI_CD_GUIDE.md)
- [Contribution guidelines](../CONTRIBUTING.md)
