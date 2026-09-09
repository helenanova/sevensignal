# sevensignal

Fan-built agent skills for BTS fans. English-first, with Korean summaries.

팬이 만든 BTS 팬용 에이전트 스킬 모음입니다. 영어가 기본이며 한국어 요약을 함께 제공합니다.

**Status:** M0 - first public release. One skill (bts-ticket-safety) is complete and tested; more skills are on the roadmap.

## What this is

A collection of open-source skills that an AI agent can load to help BTS fans with
practical, safety-critical tasks. The first skill focuses on the highest-risk moment
in fandom life: buying concert tickets without getting scammed.

The name: "seven" is a nod to the seven members. "Signal" is what the skills do -
separate trusted signals (official announcements, official sellers) from noise
(scams, rumors, resellers). The codename deliberately avoids "BTS" and "ARMY" to
keep trademark risk low.

## Design principles

1. **Official sources only.** Every trust decision anchors on a deterministic
   allowlist of official domains, not on vibes or search rankings.
2. **Deterministic over clever.** Domain matching is exact string logic that anyone
   can audit. No model judgment calls on what "looks official".
3. **Advise, never transact.** These skills help a fan decide. They never buy
   tickets, hold credentials, or move money.
4. **Freshness is a feature.** Tour dates, onsale times, and prices go stale. Claims
   that expire are marked for re-verification, with the official place to check.
5. **Refusal is a valid answer.** Out-of-scope requests get a clear refusal plus a
   safe redirect, not a half-answer.

## Repository layout

```
sevensignal/
  LICENSE                     MIT
  README.md                   this file
  DISCLAIMER.md               unofficial-project and no-affiliation notice
  SECURITY.md                 how to report security and trust problems
  CONTRIBUTING.md             content and evidence rules for contributors
  CODE_OF_CONDUCT.md          contributor covenant
  CHANGELOG.md                release history
  .github/                    issue forms and pull request template
  skills/
    bts-ticket-safety/
      SKILL.md                the skill definition (English + Korean summary)
      data/
        official-domains.yaml deterministic allowlist of official domains
      references/
        scam-patterns.md      catalog of known ticket-scam patterns
        official-channels.md  where official announcements actually appear
      evals/
        README.md             eval schema and how to run them
        golden.yaml           legitimate scenarios -> expected trust verdicts
        adversarial.yaml      scam scenarios -> expected scam verdicts
        refusal.yaml          out-of-scope asks -> expected refusals
        freshness.yaml        claims that expire -> re-verification rules
```

## Roadmap (not built yet)

- Tour news tracking from official notices only
- Fan community safety (Discord/X impersonation detection)

## License

MIT. Home: https://github.com/helenanova/sevensignal
