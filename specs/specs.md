# Ditti Research Dashboard Specifications

This document is a single source of truth for design patterns, testing patterns, deployment patterns, coding style, etc.

## Functions Specifications

- [**Source Code and Infrastructure**](./functions/source_code.md): Defines the standard file structure, configuration handling, agent patterns, and utility organization for Lambda functions.
- [**Dockerfiles**](./functions/dockerfiles.md): Specifies multi-stage Docker build patterns for Lambda functions including extension layers, function layers, and development/production configurations with proper AWS credential handling.
- [**Local Development**](./functions/local_development.md): Outlines local development workflows using Docker containers with mocked AWS services, standardized bash scripts, and Moto for AWS service simulation.
- [**Testing**](./functions/testing.md): Establishes comprehensive testing frameworks using pytest with container-based testing, extensive mocking strategies, and standardized test file organization patterns.
- [**Deployment**](./functions/deployment.md): Defines CloudFormation-based deployment patterns with separate IAM and function stacks, proper role management, and environment-specific configurations for staging and production.
