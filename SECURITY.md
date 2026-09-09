# Security Policy

## Scope

The security-sensitive surface of this project is trust data, not code:

- `official-domains.yaml` - a wrong entry here can send fans to a scam site.
- Eval fixtures - weakened fixtures let bad behavior ship.

Treat any proposed change to those files as security review, not a normal edit.

## Reporting a problem

- **Wrong or suspicious domain in the allowlist:** report immediately through
  GitHub private vulnerability reporting:
  https://github.com/helenanova/sevensignal/security/advisories/new
  If that link is unavailable, open a minimal public issue that says a trust-data
  problem exists without describing the exploit path, and the owner will follow up.
- **A scam the skill fails to catch:** report with the scam text (remove any
  personal information first) so it can become an adversarial fixture.

## Rules for everyone

- Never commit credentials, session cookies, account data, or real victim personal
  information. Fixtures use fictional examples only.
- Never add a domain to the allowlist without a source URL on an already-listed
  official domain pointing to it, plus a `last_verified` date.
- The project never asks users for passwords, payment details, or verification
  codes. Any copy of it that does is not this project.
