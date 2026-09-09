# Changelog

All notable changes to this project are documented here. Dates are UTC.
The trust data in `skills/bts-ticket-safety/data/official-domains.yaml` carries
its own `last_verified` dates per entry.

## [0.1.0] - 2026-09-08

First public release (M0).

### Added
- Skill `bts-ticket-safety`: deterministic domain allowlist, verdict taxonomy,
  scam-pattern catalog, official-channel guide, and four eval suites
  (golden, adversarial, refusal, freshness).
- Project docs: README, LICENSE (MIT), DISCLAIMER, SECURITY, CONTRIBUTING.
- Repository infrastructure: issue forms (allowlist change, scam report, bug
  report), pull request template, CODE_OF_CONDUCT, this CHANGELOG.

### Trust-data verification (2026-09-08, against Tier 1 Weverse notices)
- Confirmed `ticketmaster.com` for BTS WORLD TOUR 'ARIRANG' (NA & Europe
  presale) via weverse.io/bts/notice/33091.
- Confirmed `ticketmaster.co.uk` for the UK leg via the same notice (regional
  storefront of Ticketmaster; confirm per-show links from the tour notice).
- Corrected the Korea seller entry: the official Korean purchase page is
  `tickets.interpark.com` (NOL Ticket), linked from weverse.io/bts/notice/33269.
  The previous entry `ticket.interpark.com` (no 's') did not match the page the
  notice links and was removed.
- Corrected the Korea global entry: the official global purchase page is
  `world.nol.com` (NOL World), linked from the same notice.
  `ticket.globalinterpark.com` did not load at verification time (HTTP 403) and
  was removed; the Interpark Global flow moved to NOL World.
- Marked `ticketmaster.com.au` and `ticketmaster.ph` as `unconfirmed_tier1`:
  the Asia & Australia notice (weverse.io/bts/notice/36080) names no sellers
  inline, so these stay UNVERIFIED until a Tier 1 notice confirms them.
- Updated eval fixtures golden-04 and adversarial-01 to match the corrected
  Korea entries.
