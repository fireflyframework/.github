# Security Policy

The Firefly Framework team takes security seriously. We appreciate your efforts to responsibly disclose vulnerabilities and will make every effort to acknowledge your contributions.

---

## Supported Versions

| Version | Supported |
|-----------|--------------------|
| 26.02.x | :white_check_mark: |
| < 26.02.0 | :x: |

Only the latest CalVer release line receives security patches. If you are running an older version, please upgrade before reporting.

---

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, send an email to:

> **security@fireflyframework.org**

Include the following information in your report:

1. **Description** -- A clear description of the vulnerability.
2. **Affected component** -- The module, class, or endpoint involved.
3. **Reproduction steps** -- Detailed steps to reproduce the issue.
4. **Impact assessment** -- Your understanding of the potential impact (e.g., data exposure, denial of service, remote code execution).
5. **Proof of concept** -- Code, screenshots, or logs that demonstrate the vulnerability (if available).
6. **Your environment** -- Firefly version, Java version, operating system, and any relevant configuration.

Please encrypt sensitive reports using our PGP key if available (contact us for the key).

---

## Response Timeline

| Stage | Timeframe |
|------------------------|----------------------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix for critical issues | Within 7 days |

For non-critical issues, fixes will be included in the next scheduled release. We will keep you informed of our progress throughout the process.

---

## Coordinated Disclosure

We follow a **coordinated disclosure** policy:

1. **Reporter submits** the vulnerability via email.
2. **We acknowledge** receipt and begin our assessment.
3. **We develop and test** a fix in a private branch.
4. **We release the patch** and publish a security advisory on GitHub.
5. **Public disclosure** occurs after the patch is available, typically within 90 days of the initial report. We will coordinate the disclosure timeline with you.

We ask that you:

- **Do not** disclose the vulnerability publicly until a fix has been released and users have had reasonable time to update.
- **Do not** exploit the vulnerability beyond what is necessary to demonstrate the issue.
- **Do not** access, modify, or delete data belonging to other users.

---

## Credit

We believe in recognizing the security community's contributions. With your permission, we will:

- Credit you by name (or alias) in the security advisory.
- Include your name in our release notes for the patched version.
- Add you to our Security Hall of Fame (if established).

If you prefer to remain anonymous, we will respect that preference.

---

Thank you for helping keep Firefly Framework and its users safe.
