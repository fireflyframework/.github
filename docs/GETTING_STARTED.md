# Getting Started with Firefly Framework

A step-by-step guide to configure your development environment and start building microservices with Firefly Framework.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Option A: Quick Setup with the CLI](#option-a-quick-setup-with-the-cli)
3. [Option B: Manual Maven Setup](#option-b-manual-maven-setup)
4. [Configure GitHub Packages as a Maven Repository](#configure-github-packages-as-a-maven-repository)
5. [Create Your First Microservice](#create-your-first-microservice)
6. [Add Framework Modules](#add-framework-modules)
7. [Run and Test](#run-and-test)
8. [Common Module Combinations](#common-module-combinations)
9. [Next Steps](#next-steps)
10. [FAQ](#faq)

---

## Prerequisites

Before you begin, make sure you have the following installed:

| Tool | Minimum Version | Check Command |
|------|----------------|---------------|
| **Java JDK** | 21+ (25 recommended) | `java -version` |
| **Maven** | 3.9+ | `mvn -version` |
| **Git** | 2.30+ | `git --version` |
| **GitHub Account** | -- | [github.com](https://github.com) |

You will also need a **GitHub Personal Access Token (PAT)** with `read:packages` scope. This is required because Firefly Framework artifacts are published to GitHub Packages (not Maven Central).

### Create a GitHub Personal Access Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Give it a descriptive name (e.g., `firefly-maven-read`)
4. Select the **`read:packages`** scope
5. Click **Generate token**
6. Copy the token and save it securely -- you will need it in the next steps

---

## Option A: Quick Setup with the CLI

The fastest way to get started is with the **Firefly CLI** (`flywork`). It handles cloning, building, and configuring everything for you.

### Step 1: Install the CLI

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/fireflyframework/fireflyframework-cli/main/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/fireflyframework/fireflyframework-cli/main/install.ps1 | iex
```

### Step 2: Run Setup

```bash
flywork setup
```

This command:
- Clones all 38 framework repositories in dependency order
- Installs every module to your local Maven cache (`~/.m2`)
- Takes approximately 15-20 minutes on a fast connection

### Step 3: Verify

```bash
flywork doctor
```

This checks your Java, Maven, Git, and verifies all modules are correctly installed.

### Step 4: Create a Project

```bash
flywork create core
```

Follow the interactive prompts to set your group ID, artifact ID, and package name. The CLI generates a fully configured multi-module project with all the Maven settings pre-wired.

> If you used the CLI, you can skip ahead to [Add Framework Modules](#add-framework-modules). The CLI configures GitHub Packages automatically.

---

## Option B: Manual Maven Setup

If you prefer not to use the CLI, you can configure Maven manually.

### Step 1: Configure GitHub Packages

This is the most important step. Since Firefly Framework is published to **GitHub Packages** (not Maven Central), you must tell Maven how to authenticate and where to find the artifacts.

Edit (or create) the file `~/.m2/settings.xml`:

**macOS / Linux:**

```bash
mkdir -p ~/.m2
nano ~/.m2/settings.xml
```

**Windows:**

```
notepad %USERPROFILE%\.m2\settings.xml
```

Paste the following content. Replace `YOUR_GITHUB_USERNAME` with your GitHub username and `YOUR_GITHUB_TOKEN` with the Personal Access Token you created earlier:

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
                              https://maven.apache.org/xsd/settings-1.0.0.xsd">

  <!-- Step 1: Tell Maven your GitHub credentials -->
  <servers>
    <server>
      <id>github</id>
      <username>YOUR_GITHUB_USERNAME</username>
      <password>YOUR_GITHUB_TOKEN</password>
    </server>
  </servers>

  <!-- Step 2: Tell Maven where to find Firefly artifacts -->
  <profiles>
    <profile>
      <id>github-packages</id>
      <repositories>
        <repository>
          <id>github</id>
          <url>https://maven.pkg.github.com/fireflyframework/fireflyframework-parent</url>
          <snapshots>
            <enabled>true</enabled>
          </snapshots>
          <releases>
            <enabled>true</enabled>
          </releases>
        </repository>
      </repositories>
    </profile>
  </profiles>

  <!-- Step 3: Activate the profile by default -->
  <activeProfiles>
    <activeProfile>github-packages</activeProfile>
  </activeProfiles>

</settings>
```

### Step 2: Verify the Configuration

Test that Maven can reach GitHub Packages:

```bash
mvn dependency:resolve -DgroupId=org.fireflyframework -DartifactId=fireflyframework-parent -Dversion=26.02.01 -Dpackaging=pom
```

If successful, you will see `BUILD SUCCESS`. If it fails with a 401 error, double-check your username and token in `settings.xml`.

---

## Configure GitHub Packages as a Maven Repository

This section explains what the `settings.xml` configuration does and why it is needed.

### Why GitHub Packages?

Firefly Framework publishes all Maven artifacts to [GitHub Packages](https://github.com/features/packages). This is a package registry hosted by GitHub, similar to Maven Central but private to the organization. It requires authentication even for reading public packages.

### How It Works

The `settings.xml` file has three parts:

1. **`<servers>`** -- Stores your GitHub credentials. The `<id>` must match the `<id>` in the repository definition. Maven uses these credentials when connecting to the repository.

2. **`<profiles>` / `<repositories>`** -- Tells Maven where to look for artifacts. The URL points to the `fireflyframework-parent` repository, but GitHub Packages resolves **all** artifacts published under the `fireflyframework` organization from this single URL.

3. **`<activeProfiles>`** -- Activates the profile so Maven uses the repository for every build without needing `-P github-packages` on the command line.

### Using Environment Variables (CI/CD or Shared Machines)

If you do not want to hardcode your token in `settings.xml`, you can use environment variables:

```xml
<servers>
  <server>
    <id>github</id>
    <username>${env.GITHUB_ACTOR}</username>
    <password>${env.GITHUB_TOKEN}</password>
  </server>
</servers>
```

Then set the variables before running Maven:

```bash
export GITHUB_ACTOR="your-username"
export GITHUB_TOKEN="ghp_your_token_here"
mvn clean verify
```

### IntelliJ IDEA Configuration

IntelliJ IDEA uses its own bundled Maven by default. To ensure it picks up your `settings.xml`:

1. Open **Settings** (or **Preferences** on macOS)
2. Navigate to **Build, Execution, Deployment > Build Tools > Maven**
3. Set **User settings file** to `~/.m2/settings.xml` (check the **Override** box)
4. Click **Apply** and **OK**
5. Right-click your project and select **Maven > Reload Project**

### VS Code Configuration

If you use the Java Extension Pack in VS Code:

1. Ensure `~/.m2/settings.xml` exists with the configuration above
2. Open the command palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run **Java: Clean Java Language Server Workspace**
4. Reload the window

---

## Create Your First Microservice

### Step 1: Create the Project Structure

Using the CLI:

```bash
flywork create core --group-id com.example --artifact-id my-service
```

Or manually, create a `pom.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- Inherit from the Firefly parent POM -->
    <parent>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-parent</artifactId>
        <version>26.02.01</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>my-service</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>jar</packaging>

    <dependencies>
        <!-- Reactive web framework -->
        <dependency>
            <groupId>org.fireflyframework</groupId>
            <artifactId>fireflyframework-web</artifactId>
        </dependency>

        <!-- Reactive database access -->
        <dependency>
            <groupId>org.fireflyframework</groupId>
            <artifactId>fireflyframework-r2dbc</artifactId>
        </dependency>
    </dependencies>
</project>
```

Notice that **no version tags** are needed on Firefly dependencies. The parent POM and BOM manage all versions automatically.

### Step 2: Build

```bash
mvn clean verify
```

Maven will download all Firefly dependencies from GitHub Packages, compile your code, and run tests.

### Using the BOM Instead of the Parent POM

If your project already has its own parent POM, you can import the Firefly BOM instead:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.fireflyframework</groupId>
            <artifactId>fireflyframework-bom</artifactId>
            <version>26.02.01</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

---

## Add Framework Modules

Add only the modules you need. Here are the most commonly used ones:

### Reactive Web

```xml
<dependency>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-web</artifactId>
</dependency>
```

Includes: Spring WebFlux starter, exception handling, idempotency filters, PII masking, OpenAPI support.

### Database (R2DBC)

```xml
<dependency>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-r2dbc</artifactId>
</dependency>
```

Includes: Reactive PostgreSQL support with R2DBC auto-configuration.

### Event-Driven Architecture

```xml
<dependency>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-eda</artifactId>
</dependency>
```

Includes: Kafka and RabbitMQ integration, dead-letter queues, Protobuf serialization.

### CQRS

```xml
<dependency>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-cqrs</artifactId>
</dependency>
```

Includes: Command/query bus, handler discovery, authorization, caching, and metrics.

### Caching

```xml
<dependency>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-cache</artifactId>
</dependency>
```

Includes: Caffeine, Redis, Hazelcast, and JCache adapters.

For a complete list of all modules, see the [Module Catalog](MODULE_CATALOG.md).

---

## Run and Test

### Run Locally

```bash
mvn spring-boot:run
```

Your service starts on `http://localhost:8080` by default.

### Run Tests

```bash
mvn test
```

### Build a Docker Image (if you have Spring Boot Maven Plugin configured)

```bash
mvn spring-boot:build-image
```

---

## Common Module Combinations

Here are typical setups for different types of microservices:

### REST API with Database

```xml
<dependencies>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-r2dbc</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-validators</artifactId>
    </dependency>
</dependencies>
```

### Event-Driven Microservice with CQRS

```xml
<dependencies>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-eda</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-cqrs</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-eventsourcing</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-r2dbc</artifactId>
    </dependency>
</dependencies>
```

### Domain Service with Saga Transactions

```xml
<dependencies>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-application</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-domain</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-transactional-engine</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-r2dbc</artifactId>
    </dependency>
</dependencies>
```

### Notification Service

```xml
<dependencies>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-notifications</artifactId>
    </dependency>
    <!-- Pick one or more adapters: -->
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-notifications-sendgrid</artifactId>
    </dependency>
    <dependency>
        <groupId>org.fireflyframework</groupId>
        <artifactId>fireflyframework-notifications-twilio</artifactId>
    </dependency>
</dependencies>
```

---

## Next Steps

- Browse the full [Module Catalog](MODULE_CATALOG.md) to discover all available modules
- Read the [CI/CD Configuration Guide](CI_CD_GUIDE.md) to set up automated builds and releases
- Explore the [CLI documentation](https://github.com/fireflyframework/fireflyframework-cli) for advanced build and version management commands
- Check out [fireflyframework-genai](https://github.com/fireflyframework/fireflyframework-genai) for AI/GenAI capabilities built on Pydantic AI

---

## FAQ

### Why do I need a GitHub token just to use the framework?

GitHub Packages requires authentication even for reading public packages. This is a GitHub policy, not a Firefly Framework limitation. A Personal Access Token with `read:packages` scope is the minimum requirement.

### Can I use this with Gradle?

Yes. Add the GitHub Packages repository to your `build.gradle`:

```groovy
repositories {
    mavenCentral()
    maven {
        url = uri("https://maven.pkg.github.com/fireflyframework/fireflyframework-parent")
        credentials {
            username = project.findProperty("gpr.user") ?: System.getenv("GITHUB_ACTOR")
            password = project.findProperty("gpr.key") ?: System.getenv("GITHUB_TOKEN")
        }
    }
}
```

And add dependencies:

```groovy
dependencies {
    implementation platform("org.fireflyframework:fireflyframework-bom:26.02.01")
    implementation "org.fireflyframework:fireflyframework-web"
    implementation "org.fireflyframework:fireflyframework-r2dbc"
}
```

### What Java version do I need?

Java 21 or higher. Java 25 is the default and recommended version. The parent POM is configured for Java 25, but all modules are compatible with Java 21+.

### I get a 401 Unauthorized error when building

Your `settings.xml` credentials are incorrect or missing. Verify:

1. The file exists at `~/.m2/settings.xml`
2. Your GitHub username is correct
3. Your token has `read:packages` scope
4. The `<id>` in `<server>` matches the `<id>` in `<repository>` (both should be `github`)

### I get a "Could not find artifact" error

The artifact may not be published yet, or you may be requesting a version that does not exist. Check:

1. The version exists: visit `https://github.com/fireflyframework/<module-name>/packages`
2. Your `settings.xml` is configured correctly (see above)
3. Try `mvn -U clean verify` to force Maven to re-check remote repositories

### How do I update to a newer version?

Update the parent POM version in your `pom.xml`:

```xml
<parent>
    <groupId>org.fireflyframework</groupId>
    <artifactId>fireflyframework-parent</artifactId>
    <version>26.02.01</version> <!-- new version -->
    <relativePath/>
</parent>
```

Then run `mvn -U clean verify` to pull the updated dependencies.
