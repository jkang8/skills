# Sources

All general knowledge, not re-read for this version. Each line says what the skill takes from the source.

- [OWASP Top 10 (2021)](https://owasp.org/Top10/) and [ASVS](https://owasp.org/www-project-application-security-verification-standard/): input validation, injection, access control per object, session cookies, security logging.
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/): prompt injection, insecure output handling, excessive agency.
- [GitHub Actions security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions): pin third-party actions to a SHA, least-privilege `permissions:`, no `pull_request_target` with PR checkout.
- [NIST SSDF (SP 800-218)](https://csrc.nist.gov/projects/ssdf): dependency hygiene and secure development practices.
