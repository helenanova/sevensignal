# 5-minute quickstart

Load the skills into your agent, then try the prompts below. Everything here
is fictional-safe: no real tickets, no real money.

## 1. Install (1 minute)

```bash
npx skills add helenanova/sevensignal
```

This loads both skills (`bts-ticket-safety` and `bts-official-news`) into your
agent through the skills CLI. Works with Claude Code, Codex, Cursor, and any
client that supports the skills.sh format.

## 2. Try ticket safety (2 minutes)

Copy these prompts into your agent, one at a time.

**Prompt A (a scam):**
> A seller on KakaoTalk offered me BTS floor seats for 30% below face value
> but wants a direct bank deposit before "transferring" the ticket. Is this safe?

Expected: verdict **SCAM_INDICATORS** - advance-deposit pattern, no allowlist
match, do not engage, and a safe redirect to the official purchase flow.

**Prompt B (official source):**
> Is https://bts.ibighit.com/eng/tour/ the real tour page?

Expected: verdict **OFFICIAL** - `ibighit.com` is a Tier 1 domain; the answer
names the matched domain as evidence.

**Prompt C (lookalike domain):**
> I found tickets on interpark-tickets.com - same as Interpark, right?

Expected: verdict **UNVERIFIED** (with scam-pattern warning) - the domain does
not match `tickets.interpark.com`; there is no "close enough" in the matching
rules.

## 3. Try official news (2 minutes)

**Prompt D (real news check):**
> A fan account posted what looks like a Weverse notice about new tour dates.
> Can you confirm it?

Expected: verdict **UNVERIFIED** - screenshots and fan accounts are never
official; the answer names the Tier 1 page to watch (`weverse.io/bts/notice`
or `bts.ibighit.com/eng/tour/`).

**Prompt E (routing):**
> Where do official BTS tour announcements appear?

Expected: verdict **OFFICIAL** naming only Tier 1 public pages -
`bts.ibighit.com` and `weverse.io/bts/notice` - never aggregators.

## Verify the trust data yourself

```bash
python3 tools/test_domain_matcher.py   # 36 matcher unit tests (no dependencies)
python3 tools/validate_data.py         # schema + staleness checks
python3 tools/eval_runner.py           # deterministic eval assertions
python3 tools/check_links.py           # live check of every cited source URL
```

## Supported clients

Any client that loads skills via the [skills CLI](https://skills.sh/):
Claude Code, Codex, Cursor, and compatible agents. The skills are plain
Markdown + YAML; there is nothing to compile.

## Known limits

- **Advise only.** The skills never buy tickets, queue, log in, or hold
  credentials. They tell the fan what is safe; the fan transacts.
- **Sellers change per tour.** Tier 2 sellers are official only when a current
  Tier 1 notice names them. `unconfirmed_tier1` entries are UNVERIFIED until
  then. Re-check against the current tour notice.
- **Data ages.** Allowlist entries carry `last_verified` dates; anything past
  30 days is flagged stale by `validate_data.py` and the weekly workflow.
- **Public pages only.** Members-only Weverse content is out of scope; the
  fan reads it in their own account.
- **English-first.** User-facing safety guidance carries Korean parity, but
  maintainer docs are English-only.
- **BTS only.** No other groups yet (see README roadmap).
