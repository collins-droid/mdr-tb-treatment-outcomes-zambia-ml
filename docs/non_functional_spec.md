# Non-Functional Specification

This document defines target qualities for the future clinical decision-support tool. These are requirements for implementation, not claims about the current scaffold.

## Performance

- Future API predictions should return in less than 2 seconds under normal clinic-network conditions.
- Future model loading should be cached during API runtime.

## Security And Privacy

- Do not commit real patient data to the repository.
- Store secrets in environment variables, not source code.
- Use HTTPS in deployed environments.
- Apply access control before any pilot deployment.
- Maintain audit logs if predictions are stored.

## Usability

- Optimize the interface for busy clinical workflows.
- Use simple language: risk level, likely outcome, and why.
- Make required fields clear and reduce unnecessary typing.

## Explainability

- Provide patient-level explanations for every prediction where technically possible.
- Document model limitations, missing-data behavior, and known sources of bias.

## Reliability

- Fail clearly if the model artifact is missing.
- Include automated tests for preprocessing, inference, and API behavior.

## Offline And Low-Bandwidth Support

- Design the frontend so it can later support offline-first workflows.
- Keep API payloads small.
- Avoid external runtime dependencies in clinic-facing screens where possible.
