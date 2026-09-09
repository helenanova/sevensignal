## What changed and why

<!-- One short paragraph. Link the issue if there is one. -->

## Checklist

Trust-data and behavior changes are security-sensitive (see SECURITY.md).

- [ ] Every new or changed factual claim cites an official source URL and a
      `last_verified` date (CONTRIBUTING.md evidence standard).
- [ ] For `official-domains.yaml` changes: the source URL is on an
      already-listed Tier 1 domain.
- [ ] Eval fixtures updated in the same change (new scam pattern -> adversarial
      cases; new legitimate flow -> golden cases; changed refusals -> refusal
      cases; expiring claims -> freshness entries).
- [ ] I ran all four eval suites before proposing this change.
- [ ] No copyrighted material (no lyrics, photos, album art, or reproduced
      notice text).
- [ ] No credentials, session data, or real personal information.
- [ ] User-facing sections carry an English canonical text and a Korean summary
      (한국어 요약).
- [ ] CHANGELOG.md updated for user-visible changes.
