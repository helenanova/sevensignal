# Clean-install QA (2026-09-09)

Verified before v0.2.0: clean-room install plus end-to-end verdict checks.

## Environment

- Python 3.10.12 (CI also runs 3.13), PyYAML 5.4.1, node v22.23.2 / npx, git 2.34.1
- Fresh `git clone` of `main` (no working-tree state)

## Install

- `npx skills add helenanova/sevensignal` -> both skills install
  (`bts-ticket-safety`, `bts-official-news`) and symlink for agent clients.
- SKILL.md frontmatter (name/description) parses cleanly for both skills.

## Checks on the clean clone

- `python3 tools/test_domain_matcher.py` - 36 tests OK
- `python3 tools/test_tools.py` - 31 tests OK
- `python3 tools/validate_data.py` - 0 errors, 0 warnings, 10 allowlist entries
- `python3 tools/eval_runner.py` - 13 deterministic cases, 0 failures

## End-to-end scenarios (matcher CLI on the clean clone)

Ticket safety (5):

| Input | Expected | Got |
|---|---|---|
| https://bts.ibighit.com/eng/tour/ | OFFICIAL | OFFICIAL (tier1_match) |
| https://www.ticketmaster.com/bts-arirang | OFFICIAL_SELLER | OFFICIAL_SELLER (tier2_confirmed_tier1) |
| https://tickets.interpark.com/goods/26000600 | OFFICIAL_SELLER | OFFICIAL_SELLER (tier2_confirmed_tier1) |
| https://world.nol.com/en/ticket/places/26000041 | OFFICIAL_SELLER | OFFICIAL_SELLER (tier2_confirmed_tier1) |
| https://interpark-tickets.com/bts (lookalike) | UNVERIFIED | UNVERIFIED (no_allowlist_match) |

Official news (5):

| Input | Expected | Got |
|---|---|---|
| https://weverse.io/bts/notice | OFFICIAL | OFFICIAL (tier1_match) |
| https://hybecorp.com/eng/news | OFFICIAL | OFFICIAL (tier1_match) |
| https://bts-official-announcements.com/tour (lookalike) | UNVERIFIED | UNVERIFIED (no_allowlist_match) |
| https://shop.weverse.io | OFFICIAL | OFFICIAL (tier1_match) |
| https://ticketmaster.com.au/bts (Tier 2, unconfirmed) | UNVERIFIED | UNVERIFIED (tier2_unconfirmed_tier1) |

10/10 scenarios produced the expected verdict - no new regression fixtures or
issues needed. `unconfirmed_tier1` sellers (ticketmaster.com.au,
ticketmaster.ph) correctly stay UNVERIFIED until a Tier 1 notice names them.
