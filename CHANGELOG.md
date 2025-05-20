# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 - 2025-05-08

**Note:**

This is the first official release of the Ditti Research Dashboard. While the project has been in development for several years, this changelog focuses on the current feature set and functionality. Future releases will document changes from this point forward.

**Added:**

- Initial release of the Ditti Research Dashboard
- Frontend Features:
  - Admin Dashboard for managing researcher/coordinator accounts, studies, and permissions.
  - Ditti Dashboard for enrolling participants and viewing data collected from the Penn Ditti Mobile App.
  - Wearable Dashboard for enrolling participants and viewing data collected from Fitbit devices.
  - Participant Dashboard for participants to authorize Fitbit API access or request data deletion.
- Backend Features:
  - RESTful Flask API routes for creating, reading, updating, and deleting data.
  - OAuth2.0 authentication flows via Amazon Cognito for researchers/coordinators and participants.
  - PostgreSQL database schema for managing permissions and Fitbit data.
  - Testing suite using `pytest`
- Miscellaneous:
  - Installation framework and CloudFormation template for bootstrapping local development environments.
  - Lambda function handler for automatically pulling participant Fitbit data.
  - `rds_stopper` function for temporarily stopping idle database instances.
  - Sample VSCode `settings.json` and recommended extensions.
  - Linting and formatting with ESLint/Prettier (frontend) and Ruff (backend).
- Documentation:
  - [Apache 2.0 license](./COPYING).
  - [Contribution Guide](./docs/CONTRIBUTING.md).
  - [Dev Installation Guide](./docs/INSTALL-dev.md).
  - [Code of Conduct](./docs/CODE-OF-CONDUCT.md).
  - [Readme](./README.md).
  - PR and issue templates.
- CI/CD:
  - Status check workflows using GitHub Actions.
  - Shell scripts for manual deployment to staging and production environments.
- Infrastructure:
  - Serverless deployment using Zappa.

**Security:**

- Secure session management with OAuth2.0 via Amazon Cognito.
- No collection of PHI.
- API Keys and credentials are encrypted at rest with AWS Secrets Manager.
- Use of SameSite=Strict and HTTP-only cookies.
- Fine-grained Role-Based Access Control (RBAC) for researchers/coordinators.
- Data is transmitted securely with HTTP/TLS.
- Requests between backend services hosted on AWS implement SigV4 authentication via `boto3`.
