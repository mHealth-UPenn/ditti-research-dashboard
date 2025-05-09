# Ditti Research Dashboard

The Ditti Research Dashboard is a centralized platform for managing and visualizing data collected from the [Penn Ditti Mobile App](https://www.med.upenn.edu/DittiApp/). Researchers and clinicians can quickly enroll new participants and monitor their adherence to behavioral sleep interventions with ease.

![Screenshot](./images/readme-image.webp)

🔬 **Manage Research and Clinical Data:** The Ditti Research Dashboard allows researchers and clinicians to manage and visualize anonymized study data from the Penn Ditti app for monitoring behavioral sleep intervention adherence.

🔐 **Control Data Access with Fine-grained Roles and Permissions:** The Admin Dashboard provides granular controls for research researcher roles, enabling specific access management across studies and app-wide permissions.

☁️ **Leverage Secure, HIPAA-compliant Infrastructure:** Built on AWS with TypeScript, React.js, and Python, the app integrates participant data from DynamoDB and a Fitbit Dashboard for visualizing participant sleep data.

**Key Features:**

- Visualizations of participant interactions with the Penn Ditti Mobile App
- Interfaces for managing study-related data and enrolling study participants
- Tools for labeling and uploading audio files for the Penn Ditti Mobile App
- Administrative controls for managing researcher-level and study-level permissions
- Serverless architecture for controlling costs on-demand
- Integrations with Fitbit for visualizing sleep research data

## Getting Started

### Development Setup

Follow our [Development Setup Guide](docs/INSTALL-dev.md) to set up your local environment

### Production Setup

🚧 **Under Construction** 🚧

We are working hard at creating a straightforward process for installing and hosting your own version of the Ditti Research Dashboard. A future version will include a step-by-step installation for free, self-hosted options.

## Contributing

The Ditti Research Dashboard is **100% free** and **open source**. We encourage any users to contribute through open discussions, feature requests, bug reports, and contributions.

Looking to get involved? Our [Contribution Guide](docs/CONTRIBUTING.md) outlines how to get started with opening discussions.

Interested in contributing? Visit our [Development Setup Guide](docs/INSTALL-dev.md) to begin.

## Built With

- **[Flask](https://flask.palletsprojects.com/en/stable/)**: Our backend is a Python Flask app that responds RESTfully in JSON.
- **[React.js](https://react.dev/)**: Our frontend is a React.js app built with TypeScript that communicates with the Flask API.
- **[Tailwind CSS](https://tailwindcss.com/)**: Our frontend is styled using Tailwind CSS.
- **[PostgreSQL](https://www.postgresql.org/)**: Our database leverages PostgreSQL for secure data storage.
- **[Amazon Web Services](https://aws.amazon.com/)**: Our stack is deployed on AWS and uses managed services like [Cognito](https://aws.amazon.com/cognito/) to lock-in scalability and security.

## Security

The Ditti Research Dashboard is built with security and HIPAA compliance in mind:

- **Data Encryption**: All data is encrypted at rest and in transit
- **Access Control**: Role-based access control (RBAC) for all researchers and clinicians
- **Audit Logging**: Comprehensive logging of all system activities
- **Secure Authentication**: AWS Cognito for secure authentication
- **Data Privacy**: Strict adherence to HIPAA guidelines for PHI handling

## Copyright/License

Copyright (C) 2025 the Trustees of the University of Pennsylvania.

[Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0). The Ditti Research Dashboard is free for both commercial and non-commercial use.
