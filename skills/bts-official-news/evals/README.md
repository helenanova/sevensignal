# Evals for bts-official-news

Same case schema and rules as `skills/bts-ticket-safety/evals/README.md`:
every case has an `id`, an `input`, an `expected` block, and a `rationale`;
fixtures are fictional; run everything on every change.

- `golden.yaml` - official-source situations that must be recognized.
- `adversarial.yaml` - unofficial sources (fan accounts, leaks, lookalike
  links) that must never be treated as official news.
- `refusal.yaml` - members-only content, credential use, and text
  reproduction requests that must be refused.
- `freshness.yaml` - announcement claims that expire and must be re-read on
  the Tier 1 public page.

Run all suites (both skills) with `python3 tools/eval_runner.py`.
