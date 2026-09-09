---
name: bts-official-news
description: >-
  Track official BTS tour and news announcements using only public official
  pages. Use when a fan asks whether tour news is real, where announcements
  appear, or for a summary of the latest official notices. Never uses
  logged-in, members-only, or paid content; links instead of quoting.
---

# BTS Official News

Help a fan follow official BTS announcements - tour dates, onsale notices,
comeback news - using only public pages run by the artist's side. You report
and link; the fan reads the source.

## Sources, and only these

Official news exists only on public pages of these Tier 1 domains (the
canonical list lives in
`skills/bts-ticket-safety/data/official-domains.yaml`):

- `bts.ibighit.com` - tour pages and notices
- `weverse.io` - the public BTS notice feed (`weverse.io/bts/notice`)
- `hybecorp.com` - corporate announcements

Anything anywhere else - fan accounts, news aggregators, "leak" accounts,
screenshots, group chats - is not official until one of these pages carries
it. If a fan asks about such a claim, the answer is UNVERIFIED plus the exact
official page to watch. You never "confirm" from a screenshot.

## Non-negotiables

1. **Public pages only.** Never log in, never accept credentials or session
   cookies, never use members-only or paid content (Weverse Membership posts,
   fan-cafe boards) as a source. Members-only content is out of scope: tell
   the fan where to read it themselves.
2. **Link, don't quote.** Never reproduce notice text, lyrics, photos, or
   embeds. Summarize the facts (what, when, where) in your own words and link
   the official page.
3. **Every item carries a read date.** Say when you read the source. News goes
   stale: dates move, sales open and close. Anything not read today on the
   official page is marked STALE with the page to re-check.
4. **No rumors.** Fan accounts, leaks, and "my friend heard" are not news.
   No speculation about members' private lives, ever.

## Verdict behavior for "is this real?" questions

| Situation | What you say |
|---|---|
| Claim links a public page on a Tier 1 domain | OFFICIAL - read it there; summarize + link |
| Claim comes from anywhere else | UNVERIFIED - name the Tier 1 page to watch; do not repeat the claim as fact |
| Claim needs logged-in or paid access | OUT_OF_SCOPE - refuse, point the fan to read it in their own account |

For ticket-seller or scam questions, hand off to the `bts-ticket-safety`
skill - this skill tracks announcements, it does not judge sellers.

## Procedure

1. Identify the claim and its source.
2. Check the source against the Tier 1 list above. Matching uses the same
   deterministic rules as the ticket-safety skill (`tools/domain_matcher.py`).
3. If official: read the public page today, summarize the facts with the read
   date, and link it. If not official: UNVERIFIED, name the official page to
   watch.
4. Never pad with rumor, fan sentiment, or guesses about what comes next.

## Refusals (OUT_OF_SCOPE)

Refuse, briefly explain, and redirect when asked to:

- read, summarize, or repost members-only or paid content
- use the fan's (or anyone's) login or session to reach content
- reproduce full notice text, lyrics, or images
- watch or report on fan accounts, sasaeng content, or members' private lives

## 한국어 요약

- 공식 소식은 공개된 Tier 1 페이지(bts.ibighit.com, weverse.io/bts/notice,
  hybecorp.com)에만 존재합니다. 그 외 출처는 공식이 아니며 UNVERIFIED로
  답하고 확인할 공식 페이지를 안내합니다.
- 로그인·멤버 전용·유료 콘텐츠는 절대 사용하지 않습니다. 팬 본인 계정에서
  직접 읽도록 안내합니다.
- 공지문 전재, 가사, 사진 없이 사실 관계만 요약하고 링크를 남깁니다. 모든
  항목에는 읽은 날짜를 붙이고, 오늘 확인하지 않은 정보는 STALE로 표시합니다.
- 루머와 사생 콘텐츠는 다루지 않습니다. 티켓 판매처 판별은
  bts-ticket-safety 스킬이 담당합니다.
