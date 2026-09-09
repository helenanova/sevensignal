# Maintainer tools

Executable safety checks for the project. Every tool runs locally with
`python3` and in CI (`.github/workflows/`).

| Tool | What it does | Dependencies |
|---|---|---|
| `domain_matcher.py` | Reference implementation of the documented domain-matching rules, with a CLI | none (stdlib only) |
| `test_domain_matcher.py` | Unit tests: exact/subdomain/case matches, verdict mapping, adversarial lookalikes | none (stdlib only) |
| `validate_data.py` | Schema validation for the allowlist and eval fixtures; 30-day staleness fail-safe | PyYAML |
| `eval_runner.py` | Runs the deterministic eval assertions; separates LLM-judged cases | PyYAML |
| `check_links.py` | Liveness check for every official source URL the data cites | none (stdlib only) |

## Quick start

```bash
python3 tools/test_domain_matcher.py      # unit tests, no dependencies
pip install -r requirements-dev.txt       # one-time, for the PyYAML tools
python3 tools/validate_data.py            # schema + staleness report
python3 tools/eval_runner.py              # deterministic eval assertions
python3 tools/check_links.py              # live source-link check (network)
```

## domain_matcher.py

Implements the "Deterministic domain matching" rules from
`skills/bts-ticket-safety/SKILL.md` exactly: lowercase, strip one leading
`www.`, then match on equality or `.`-suffix, longest listed domain wins.

```bash
$ python3 tools/domain_matcher.py https://bts.ibighit.com/eng/tour/ interpark-tickets.com
https://bts.ibighit.com/eng/tour/  ->  host=bts.ibighit.com  match=ibighit.com  verdict=OFFICIAL  (tier1_match)
interpark-tickets.com  ->  host=interpark-tickets.com  match=-  verdict=UNVERIFIED  (no_allowlist_match)
```

Verdict mapping: Tier 1 match -> OFFICIAL; Tier 2 with `confirmed_tier1` ->
OFFICIAL_SELLER; Tier 2 with `unconfirmed_tier1` -> UNVERIFIED; no match ->
UNVERIFIED. The matcher never emits SCAM_INDICATORS or OUT_OF_SCOPE: those
come from scam-pattern screening and refusal rules, which are agent judgment,
not string logic.

Deliberate strictness, all fail closed:

- A trailing dot (`weverse.io.`) is NOT normalized away. The documented rules
  do not normalize it, so it does not match.
- Hosts with empty labels (`.weverse.io`, `weverse..io`) are not valid
  hostnames and never match.
- Unicode lookalikes (e.g. Cyrillic 'e') and punycode never match: matching is
  exact on the normalized string.
- `https://weverse.io@evil.com/` resolves to host `evil.com`. The part before
  `@` is userinfo, not the host.

The CLI loads the allowlist with a small line parser that understands only the
documented layout of `official-domains.yaml`; it is a convenience so the
matcher stays dependency-free, not a YAML parser. `validate_data.py` performs
the authoritative schema validation with PyYAML.

## validate_data.py

Checks `official-domains.yaml` against the CONTRIBUTING evidence rules as
executable constraints:

- every entry has domain, role, regions, verified_source (https), last_verified
- a Tier 2 entry's verified_source must be on a Tier 1 domain ("Tier 1 confirms
  Tier 2", made executable)
- no duplicates, no Tier 1/Tier 2 overlap, no future dates
- eval fixtures follow the schema in `evals/README.md` (unique ids, suite
  prefixes, valid verdicts, Tier 1 recheck targets)
- every other YAML file in the repo at least parses

Staleness fail-safe: any `last_verified` (or the file-level `last_reviewed`)
older than `--max-age-days` (default 30) prints a WARNING. Exit codes:
0 = clean or warnings only, 1 = validation errors, 2 = stale data (only with
`--fail-on-stale`). Use `--today YYYY-MM-DD` for a deterministic run.

## eval_runner.py

Runs the eval suites in `skills/bts-ticket-safety/evals/`. Two explicit tiers:

- **Deterministic**: golden cases with URLs - every extracted host must match
  the allowlist and the matcher verdict must equal the expected verdict;
  adversarial cases with URLs - no extracted host may earn a trust verdict;
  golden `must_mention` domains must be allowlist-matched. A deterministic
  FAIL means data drift, a matcher regression, or a fixture contradicting the
  allowlist. These run in CI on every change.
- **LLM-judged**: verdicts that depend on reading prose (scam patterns,
  refusals, freshness behavior, routing answers). The runner lists them with
  expectations and never counts them as passed. Optional offline scoring of a
  recorded agent run: `--answers answers.yaml` mapping case id -> answer text
  applies `must_mention` string checks (`must_not` stays human-judged).

## check_links.py

Probes every URL cited by `official-domains.yaml` (verified_source) and
`evals/freshness.yaml` (recheck_at): HEAD first, GET fallback. OK = 2xx/3xx,
WARN = 401/403/429 (usually bot mitigation - needs a human spot check, not an
automatic data change), FAIL = 404/410/5xx/timeout/DNS error (the citation is
dead). `--fail` exits 1 on any FAIL.

## CI wiring

- `.github/workflows/ci.yml` (push/PR): unit tests on Python 3.10 and 3.13,
  full schema validation with a warn-only staleness report, deterministic
  evals.
- `.github/workflows/freshness.yml` (weekly, Mondays 09:17 UTC, or manual):
  staleness check with `--fail-on-stale` plus the live link check. On any
  finding it opens (or comments on) ONE issue labeled `stale-data`. It never
  modifies data and never auto-closes: re-verification needs a human with
  Tier 1 evidence.
