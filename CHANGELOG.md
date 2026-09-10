# Changelog

All notable changes to this project are documented here. Dates are UTC.
The trust data in `skills/bts-ticket-safety/data/official-domains.yaml` carries
its own `last_verified` dates per entry.

## [Unreleased]

### Added (release clarity)
- README Status line now says exactly what the v0.1.0 tag contains
  (bts-ticket-safety) versus what is unreleased on `main`
  (bts-official-news, tools, CI), removing the released/unreleased ambiguity.
- `docs/release-checklist.md`: pre-tag checks, tag + GitHub Release steps,
  and post-publish verification.

### Added (Day 2: official-news eval hardening, closes #1)
- Expanded `bts-official-news` eval suites from 2 cases each to: 6 golden
  (incl. Weverse notice feed, HYBE corporate news, a Korean-language query,
  and read-date behavior), 7 adversarial (fake official-looking domains,
  copied/undated notices, conflicting fan-account dates, Korean screenshot
  claims, fake presale-code sites), 6 refusal (members-only scraping, session
  cookies, credential handling, lyrics reproduction, Korean redistribution
  request), and 5 freshness claim classes (undated copies, conflicting dates,
  presale windows). Closes #1.

### Added (Day 3: test the test tools)
- `tools/test_tools.py`: 31 unit tests for the maintainer tools themselves -
  `validate_data.py` (date parsing, host matching, duplicate domains,
  Tier-1-confirms-Tier-2, future dates, stale warnings, eval-fixture schema),
  `eval_runner.py` (host extraction, golden/adversarial deterministic checks,
  offline answer scoring), and `check_links.py` (fully mocked network:
  OK/WARN/FAIL classification, HEAD->GET fallback, DNS/timeout failures).
- `ci.yml`: new `tool-tests` job runs the tool tests on Python 3.10/3.13,
  plus a test-count summary step (36 matcher tests + 31 tool tests).

### Added (Day 4: easier first use)
- `docs/quickstart.md`: 5-minute quickstart with copyable prompts and expected
  verdicts for both skills, supported clients (skills CLI: Claude Code, Codex,
  Cursor), and known limits (advise-only, per-tour seller confirmation,
  30-day staleness, public pages only, English-first).
- `docs/official-news-demo.md`: static scripted demo for the official-news
  skill, alongside the ticket-safety demo GIF.
- README links the quickstart and the official-news demo next to the GIF.

### Added (Day 5: clean-install QA)
- `docs/clean-install-qa.md`: fresh-clone verification (full check suite
  green), `npx skills add` install-path check, and 10 end-to-end verdict
  scenarios (5 ticket-safety, 5 official-news) - 10/10 expected verdicts.

### Added (Day 6: contributor flow)
- CONTRIBUTING.md: table mapping each report type to the exact files to change.
- docs/example-contribution.md: one worked example from evidence to data to eval to checks.

### Added (repo polish)
- README: one-command install (`npx skills add helenanova/sevensignal`) and an
  animated demo near the top; new `docs/` folder for visual assets.
- `docs/demo.gif`: scripted terminal demo using verbatim matcher output - a
  fictional KakaoTalk deposit scam is flagged UNVERIFIED, then the official
  Korean seller is confirmed OFFICIAL_SELLER.
- `docs/social-preview.png`: repository social preview image (text and
  geometric motif only; no logos, photos, or protected artwork).

### Added (Days 15-28)
- Expanded eval coverage on `bts-ticket-safety`: 10 new adversarial cases
  (Korean-language KakaoTalk scams, Korean lookalike domains, fake Weverse
  Shop, membership resale, wallet-pass "transfers", resale-marketplace
  confusion, Instagram DM impersonation, fake support numbers, proxy
  ticketing credential theft, Korean phishing), 5 new golden cases
  (regional sellers for the current tour, www-normalization), and 3 new
  refusal cases (logged-in access, session-cookie scraping, purchase-limit
  bypass with bought accounts).
- New scam patterns in `references/scam-patterns.md`: P11 fake Weverse Shop,
  P12 membership resale, P13 messenger open-chat sale, P14 wallet-pass
  "transfer".
- `bts-ticket-safety` SKILL.md: new non-negotiable "public pages only - no
  automated logged-in access", and the Korean section expanded from a summary
  to full parity (rules, matching, verdict table, procedure, refusals).
- New skill `bts-official-news`: official tour/news tracking from public
  Tier 1 pages only, with its own golden/adversarial/refusal/freshness eval
  suites. Link-don't-quote, read dates on every item, members-only content
  out of scope.
- CONTRIBUTING.md: field-report SLA (a valid scam report becomes an
  adversarial fixture within 7 days), public-pages-only sourcing rule, and
  the documented English-only policy for maintainer-facing docs.
- MAINTAINERS.md: the weekly 15-minute maintenance loop, event-driven heavier
  sweeps, and the 60-day unmaintained policy (pinned stale warning, then
  archive - stale trust data is worse than none).

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
