# Demo: bts-official-news in action

A scripted example session showing the skill's verdict behavior. Fictional
scenario; the verdicts are the deterministic rules from the skill, and the
matching is verifiable with `python3 tools/domain_matcher.py <url>`.

---

**Fan:** I found the tour schedule on https://bts-official-announcements.com -
the name says official, so it's legit right?

**Agent:** **UNVERIFIED.** `bts-official-announcements.com` does not match any
Tier 1 domain - a domain with "official" in its name is not an official
source. Watch `bts.ibighit.com/eng/tour/` or `weverse.io/bts/notice` for the
real announcement.

```
$ python3 tools/domain_matcher.py https://bts-official-announcements.com
https://bts-official-announcements.com  ->  host=bts-official-announcements.com
  match=-  verdict=UNVERIFIED  (no_allowlist_match)
```

---

**Fan:** Is the announcement at https://bts.ibighit.com/eng/tour/ the official
tour page?

**Agent:** **OFFICIAL.** `bts.ibighit.com` is a Tier 1 domain - this is the
canonical source for tour announcements. Read 2026-09-09.

```
$ python3 tools/domain_matcher.py https://bts.ibighit.com/eng/tour/
https://bts.ibighit.com/eng/tour/  ->  host=bts.ibighit.com
  match=ibighit.com  verdict=OFFICIAL  (tier1_match)
```

---

**Fan:** Here's my Weverse login - read the members-only presale notice and
summarize it for me.

**Agent:** **OUT_OF_SCOPE.** I never accept credentials and never use
logged-in or members-only content as a source. You can read the notice in
your own Weverse account; I'll gladly summarize anything on the public pages.

---

More scenarios: `skills/bts-official-news/evals/` holds the golden,
adversarial, refusal, and freshness suites that pin this behavior.
