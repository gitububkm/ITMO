# Opengrep rules

Rules used by the `sast` job in `.gitlab-ci.yml`. They are stored in the repository
so that every pipeline run analyses the code with exactly the same rule set.

| Directory | Source | Why |
|---|---|---|
| `rules/opengrep-rules/python/lang/security` | [opengrep-rules](https://github.com/opengrep/opengrep-rules) @ `f1d2b56` | Python: injections, deserialization, subprocess, XML |
| `rules/opengrep-rules/python/django/security` | same | Django: raw SQL, CSRF, XSS, cookies |
| `rules/opengrep-rules/python/jwt/security` | same | PyJWT |
| `rules/opengrep-rules/python/cryptography/security` | same | cryptography, hashlib |
| `rules/opengrep-rules/python/requests/security` | same | requests (SSRF, TLS) |
| `rules/opengrep-rules/dockerfile/security` | same | Dockerfile |
| `rules/opengrep-rules/generic/secrets` | same | Hardcoded keys and tokens |
| `rules/custom` | this project | Django settings: `DEBUG = True`, hardcoded `SECRET_KEY` |

Only the rule files (`*.yaml`) are copied; the test fixtures from the upstream
repository are left out. Upstream rules are licensed under `rules/opengrep-rules/LICENSE`.

Scan scope: the whole repository except `Solutions/` (lab solutions), `docs/`,
`tests/` (CI smoke tests) and `.opengrep/` itself.
