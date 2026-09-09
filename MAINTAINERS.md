# Maintainer loop

This project is safety data with code around it. The data decays; the loop
below is what keeps decay visible. Maintainer-facing doc: English-only.

## Weekly loop (about 15 minutes)

1. Run the checks:
   ```bash
   python3 tools/validate_data.py --fail-on-stale
   python3 tools/check_links.py
   ```
   The scheduled `freshness.yml` workflow already runs these weekly and opens
   one `stale-data` issue on findings - the loop above is the same check done
   by a human who can act on it.
2. If anything is stale or dead: re-verify against a current Tier 1 notice
   (bts.ibighit.com or weverse.io/bts/notice, public pages only), update
   `last_verified`, and close the `stale-data` issue.
3. Skim the current tour's Tier 1 notices for seller or schedule changes.
4. Triage open `scam-report` issues against the field-report SLA in
   CONTRIBUTING.md (valid report -> adversarial fixture within 7 days).
5. Check any `unconfirmed_tier1` allowlist entries - has a Tier 1 notice
   confirmed or replaced them yet?

## Heavier sweep (1-2 hours, event-driven)

Run when a tour is announced, an onsale day lands, or a seller changes:

- Re-verify every Tier 2 entry against the new tour's notices.
- Update eval fixtures that reference specific tours or sellers.
- Re-check golden fixtures still reflect the real purchase flow.

## If the project goes unmaintained

Stale trust data is worse than no data. If no maintainer can run the loop:

- **After 60 days without a verification pass:** open a pinned issue titled
  "This project's trust data is unmaintained" saying the allowlist may be
  stale, pointing at the last `last_verified` dates, and telling readers to
  verify everything against Tier 1 notices themselves. Add the same warning
  to the top of README.md.
- **Longer term:** archive the repository. An archived repo with an honest
  warning protects fans; a quiet one with rotting data does not.
- The weekly freshness workflow keeps flagging staleness meanwhile - that is
  its job - but an alarm no one reads is not maintenance.

## Rules that do not bend

- Allowlist diffs are security review, not normal edits (SECURITY.md).
- Verification uses public pages only. Never use logged-in, members-only,
  or paid content as a source (CONTRIBUTING.md rule 5).
- If a second maintainer joins, allowlist changes need two-person review:
  one proposes, the other confirms against the Tier 1 source.
