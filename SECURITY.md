# Security

## Reporting a vulnerability

Do not publish credentials, tokens, private personal data, or exploitable vulnerability details in public issues.

For private repositories, report suspected security issues directly to the repository owner through GitHub's private contact mechanisms. For the public repository, avoid disclosing sensitive details publicly until a fix or mitigation is available.

## Secrets

- Never commit credentials, API keys, session files, or production secrets.
- Use GitHub Actions secrets or an appropriate external secret store.
- Do not print secrets in CI logs.
