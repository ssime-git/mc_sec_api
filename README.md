# API Security Masterclass Repository

This repository contains demonstration materials for the API Security Masterclass. It includes practical examples of secure API implementation, GDPR compliance, and OAuth2 authentication.

## Repository Structure

This repository is organized into two main components:

1. **[GDPR-Compliant API System](/securing_api)** - A comprehensive example of a secure, GDPR-compliant ML API system
2. **OAuth2 Demo** - Demonstration of OAuth2 authentication flows

## Resources

* [Masterclass Slides](https://docs.google.com/presentation/d/1LmQAB2wKJdoj7cNDC6G40Jfd6m3r5xt_/edit#slide=id.g2e34f6b7219_0_189)
* [API Security Best Practices](https://github.com/OWASP/API-Security/blob/master/2019/en/dist/owasp-api-security-top-10.pdf) (OWASP API Security Top 10)

## Setup Instructions

We recommend using `uv` to create the virtual environment. For more details about `uv`, check the [documentation](https://docs.astral.sh/uv/getting-started/installation/).

## GDPR-Compliant API System

The [securing_api](/securing_api) directory contains a complete implementation of a GDPR-compliant machine learning API system with the following features:

- Two-API architecture separating security from prediction functionality
- User authentication with JWT tokens
- Consent management for GDPR compliance
- Data pseudonymization
- Streamlit dashboard for user interaction

See the [securing_api README](/securing_api/README.md) for detailed documentation.

## OAuth2 Demo

The OAuth2 demo illustrates different OAuth2 flows including:

- Authorization Code Flow
- Client Credentials Flow
- Implicit Flow
- Resource Owner Password Credentials Flow

This demonstrates how OAuth2 can be used for more robust service-to-service authentication compared to static API keys.

## Important Notes

* **JWT Libraries**: Never install both `jwt` and `PyJWT` packages at the same time. This can cause conflicts. See [this StackOverflow thread](https://stackoverflow.com/questions/33198428/jwt-module-object-has-no-attribute-encode) for details.
* **Environment Variables**: Both demos use environment variables for configuration. See the respective `.env.example` files for required variables.

## Getting Started

### GDPR-Compliant API System

To run the GDPR-compliant API system:

```sh
# Navigate to the securing_api directory
cd securing_api

# Start all services using Docker Compose
docker compose up --build

# Or use the Makefile
make up
```

Once running, you can access:
- Streamlit Dashboard: http://localhost:8502
- Security API: http://localhost:8000
- Prediction API: http://localhost:8001 (internal only)

Default login credentials:
- Username: `apitest` or `apitest2`
- Password: `Test123!`

### Documentation

For detailed documentation on each component:

- [GDPR-Compliant API System Documentation](/securing_api/README.md) - Complete documentation of the architecture, API endpoints, and GDPR compliance features

- [OAuth2 Demo Documentation](/oauth2_demo/README.md) - Explains different OAuth2 flows and how to use them

## Contributing

Contributions to improve the demonstrations or add new security features are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- OWASP API Security Project for best practices
- FastAPI for the API framework
- Streamlit for the dashboard interface
