# Contributing

Welcome. These rules keep the project safe for fans.

## Content rules

1. **No copyrighted material.** No lyrics, photos, album art, video embeds, or
   reproduced official notice text. Facts (dates, domains, rules) are fine.
2. **Evidence standard.** Every factual claim about sellers, presales, or process
   must cite an official source URL and a `last_verified` date. Fan blogs and
   forums can inform research but are never citations.
3. **English-first, Korean summaries.** Write the canonical text in English. Add a
   Korean summary (한국어 요약) to any user-facing section.
4. **Plain words.** Short sentences. No hype, no fandom jargon in safety-critical
   instructions.

## Changing the allowlist

A domain enters `official-domains.yaml` only when an already-listed official
domain links to it or names it in a notice. Include:

- the exact registrable domain
- its role and regions
- the official source URL where you confirmed it
- the date you confirmed it

## Run the checks

Before opening a pull request, run:

```bash
python3 tools/test_domain_matcher.py   # matcher unit tests (no dependencies)
python3 tools/validate_data.py         # schema + 30-day staleness check
python3 tools/eval_runner.py           # deterministic eval assertions
python3 tools/check_links.py           # live source-link check (network)
```

CI runs the first three on every push and pull request. A weekly workflow
re-checks staleness and source links and opens one `stale-data` issue when
allowlist data is older than 30 days or a cited source stops responding.
Treat that issue as a re-verification task: confirm against a Tier 1 notice,
update `last_verified`, then close it.

## Changing skill behavior

Any change to verdicts, procedures, or refusals must ship with eval fixtures:

- new scam pattern -> add adversarial cases
- new legitimate flow -> add golden cases
- changed refusal scope -> add refusal cases
- time-sensitive claims -> add or update freshness entries

Run all four suites before proposing the change. A change that breaks existing
fixtures needs a written reason in the pull request.
