# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| `v0.2.x` (main) | Yes — best effort for v0 |
| Older local trees | No guarantees |

## Reporting a vulnerability

Please **do not** open a public issue for security-sensitive reports.

1. Contact the maintainer via GitHub: [@BrianV1981](https://github.com/BrianV1981)  
2. Include reproduction steps, impact, and environment details  
3. Allow reasonable time for a fix before public disclosure  

## Hard rules for this project

- **Never commit** API keys, OAuth tokens, or `.aim_core/CONFIG.json`
- **Never commit** live `memory_lance/` databases (may contain private session data)
- Treat `memory-wiki/` and session archives as potentially sensitive before publishing forks
- Installer scripts modify shell RC files — review before running on shared machines

## Dependencies

Report supply-chain issues (malicious packages, compromised actions) the same way as vulnerabilities.
