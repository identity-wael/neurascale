# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability within NeuraScale, please send an email to security@neurascale.io. All security vulnerabilities will be promptly addressed.

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

## Preferred Languages

We prefer all communications to be in English.

## Security Measures

This project implements several security measures:

1. **Dependency Scanning**: Automated dependency updates via Dependabot
2. **Secret Scanning**: GitHub secret scanning enabled to prevent credential leaks
3. **Security Headers**: Implemented via Vercel configuration
4. **Environment Variables**: Sensitive data stored in environment variables, never in code
5. **Access Control**: Proper authentication and authorization mechanisms

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any potential similar problems
3. Prepare fixes for all supported versions
4. Release new versions as soon as possible

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a pull request.