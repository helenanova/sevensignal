# Worked example: confirming a new official seller

This walks one complete contribution from evidence to merged change, using a
realistic example: a Tier 1 Weverse notice names a new ticketing partner for a
tour leg.

## 1. Gather the evidence

Find the Tier 1 notice that names the seller. Save the exact URL and the date
you read it. Example: a Weverse notice says the Japan leg sells through
`ticket.jp-example.com`.

Evidence standard (see CONTRIBUTING.md): the source URL must itself be on an
already-listed Tier 1 domain. A screenshot, a fan blog, or the seller's own
homepage is not evidence.

## 2. Make the data change

Edit `skills/bts-ticket-safety/data/official-domains.yaml`, adding to
`tier_2_ticketing_partners`:

```yaml
    - domain: ticket.jp-example.com
      role: Ticketing partner (Japan, per tour)
      regions: [JP]
      confirmation: confirmed_tier1
      verified_source: https://weverse.io/bts/notice/99999
      notes: Weverse notice for the Japan leg names this seller and links its
        purchase pages.
      last_verified: 2026-09-15
```

Rules to respect: lowercase registrable domain, no `www.`, no duplicates, no
overlap with Tier 1, `last_verified` not in the future.

## 3. Add the eval case

New legitimate flow -> golden case (CONTRIBUTING rule). Add to
`skills/bts-ticket-safety/evals/golden.yaml`:

```yaml
  - id: golden-11
    input: |
      Fan: "The Weverse notice for the Japan leg links to
      https://ticket.jp-example.com/on sale - can I buy there?"
    expected:
      verdict: OFFICIAL_SELLER
      must_mention: ["ticket.jp-example.com"]
    rationale: Tier 2 domain confirmed by a Tier 1 notice for this tour.
```

If the change were a new scam pattern instead, you would add adversarial
cases to `adversarial.yaml` plus the pattern in `references/scam-patterns.md`.

## 4. Run the checks

```bash
python3 tools/test_domain_matcher.py
python3 tools/test_tools.py
python3 tools/validate_data.py
python3 tools/eval_runner.py
python3 tools/check_links.py   # needs network
```

All must pass. CI runs the first three on every pull request; a red CI means
the change does not merge.

## 5. Open the pull request

Use the PR template. Include: the evidence URL, the date you read it, the
eval case id you added, and the check output. A maintainer confirms the
evidence against the Tier 1 source before merging - allowlist diffs are
security review, not normal edits (SECURITY.md).
