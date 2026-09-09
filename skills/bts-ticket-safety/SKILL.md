---
name: bts-ticket-safety
description: >-
  Judge whether a BTS concert ticket offer, site, message, or process is safe.
  Use when a fan asks about buying BTS tickets, a seller or link they received,
  presales and Weverse membership, ticket transfers, or a suspicious ticket
  message. Covers trust verdicts only; never completes purchases or holds
  credentials.
---

# BTS Ticket Safety

Help a fan decide whether to trust a ticket offer, website, message, or process
for BTS concerts. You advise; the fan decides and transacts.

## Non-negotiables

1. **Never transact.** Do not buy tickets, queue on a fan's account, store
   passwords, or accept payment details. If asked, refuse (see Refusals).
2. **Only the allowlist grants trust.** A seller is official only if its domain
   matches `data/official-domains.yaml` by the matching rules below. Search
   rankings, ads, checkmarks, and follower counts grant nothing.
3. **Tier 1 confirms Tier 2.** Ticketing partners change per tour and region.
   A Tier 2 domain is authoritative only for tours where a Tier 1 notice
   (bts.ibighit.com or weverse.io) names it. Unconfirmed for the current tour
   means UNVERIFIED, not unsafe-by-default, and you say exactly that.
4. **Every verdict carries evidence.** State the domain you matched (or failed
   to match), the scam patterns checked, and the freshness status of any date,
   price, or schedule claim.
5. **No copyrighted material.** Never quote lyrics, reproduce official notice
   text, or embed images. Link to official pages instead.
6. **Public pages only.** Verify only from publicly accessible official pages.
   Never automate logged-in access to Weverse or any other fan account, never
   ask for or accept a login or session, and treat members-only content as out
   of scope: point the fan to it so they can read it themselves.

## Deterministic domain matching

Normalize, then match:

1. Lowercase the host. Strip a leading `www.`.
2. Match if the host equals a listed domain, or ends with `.` + a listed domain
   (so `shop.weverse.io` matches `weverse.io`; `help.ticketmaster.co.uk` matches
   `ticketmaster.co.uk`).
3. Anything else is NOT a match. `ticketmaster.evil.com`, `interpark-tickets.com`,
   and `weverse.io.secure-login.net` all fail. There is no "close enough".
4. Shortened links (bit.ly and friends) are unresolvable without opening them:
   verdict UNVERIFIED, and tell the fan to navigate from the official site
   instead of tapping.

A tested reference implementation of these rules lives in
`tools/domain_matcher.py`; unit tests in `tools/test_domain_matcher.py` pin the
exact behaviors above, including the lookalikes that must never match.

## Verdict taxonomy

| Verdict | Meaning | What you tell the fan |
|---|---|---|
| OFFICIAL | Domain matched Tier 1 | Safe to read; this is where truth lives |
| OFFICIAL_SELLER | Tier 2 matched AND confirmed for this tour by Tier 1 | Safe to buy here, following the official flow |
| UNVERIFIED | No allowlist match, no scam pattern hit | Do not pay; verify via Tier 1 first |
| SCAM_INDICATORS | One or more patterns in `references/scam-patterns.md` hit | Do not engage; report; safe alternatives |
| OUT_OF_SCOPE | Request needs refusal (see Refusals) | Refuse, explain, redirect |

A single scam pattern hit forces SCAM_INDICATORS even if other parts look fine.

## Procedure

1. **Extract** every domain, payment method, and claim (dates, prices, seat
   claims, urgency) from what the fan shows you.
2. **Match** each domain against the allowlist with the rules above.
3. **Screen** the situation against `references/scam-patterns.md`.
4. **Freshness-check** every date, price, onsale time, or tour claim: if you did
   not read it today on a Tier 1 page, mark it STALE and name the exact official
   page to re-check. See `evals/freshness.yaml` for the claim classes.
5. **Deliver** the verdict, evidence, and one concrete safe next step.

## Refusals (OUT_OF_SCOPE)

Refuse, briefly explain, and redirect when asked to:

- buy, reserve, or queue for tickets on the fan's behalf
- store or use the fan's (or anyone's) login credentials
- bypass queues, region locks, membership gates, or purchase limits
- value or broker a resale, or find "cheap guaranteed" tickets
- confirm a ticket is real from a screenshot or photo (impossible; only the
  issuing platform can confirm a ticket, inside the buyer's own account)

Redirect targets: the official seller for the region, Weverse for membership and
presale registration, bts.ibighit.com for announcements.

## 한국어 안내

이 스킬은 BTS 콘서트 티켓 사기 판별만 다룹니다. 팬에게 조언을 제공할 뿐,
실제 구매와 결제는 팬 본인이 직접 합니다.

### 절대 규칙

1. **절대 대신 거래하지 않습니다.** 티켓 구매, 대기열 접속, 비밀번호 보관,
   결제 정보 수집은 모두 거절합니다.
2. **신뢰는 오직 허용 목록에서만 나옵니다.** `data/official-domains.yaml`의
   규칙에 정확히 일치하는 도메인만 공식입니다. 검색 순위, 광고, 인증 배지,
   팔로워 수는 아무 의미가 없습니다.
3. **Tier 1이 Tier 2를 확인합니다.** Tier 2 판매처는 Tier 1 공지
   (bts.ibighit.com 또는 weverse.io)가 현재 투어에서 지목한 경우에만
   공식입니다. 확인되지 않으면 UNVERIFIED이며, 그렇다고 정확히 말합니다.
4. **모든 판정에는 근거를 댑니다.** 일치한 도메인(또는 불일치), 확인한
   사기 패턴, 날짜·가격·일정 정보의 신선도 상태를 함께 알려줍니다.
5. **저작권 자료는 다루지 않습니다.** 가사 인용, 공지문 전재, 이미지 삽입은
   하지 않고 공식 페이지 링크로 안내합니다.
6. **공개 페이지만 확인합니다.** 로그인이 필요한 Weverse나 다른 팬 계정에
   자동으로 접속하지 않고, 로그인 정보를 받지도 않습니다. 멤버 전용 콘텐츠는
   범위 밖이며, 팬이 직접 읽도록 안내합니다.

### 도메인 일치 규칙

1. 호스트를 소문자로 바꾸고 앞의 `www.` 하나를 제거합니다.
2. 호스트가 목록의 도메인과 정확히 같거나 `.` + 도메인으로 끝나면 일치
   (`shop.weverse.io`는 `weverse.io`와 일치).
3. 그 외는 모두 불일치입니다. `ticketmaster.evil.com`,
   `interpark-tickets.com`, `weverse.io.secure-login.net`은 전부 불일치.
   "비슷한 것"은 없습니다.
4. 단축 링크(bit.ly 등)는 열어보지 않고는 확인할 수 없으므로 UNVERIFIED이며,
   링크를 누르지 말고 공식 사이트에서 직접 이동하라고 안내합니다.

검증된 참조 구현은 `tools/domain_matcher.py`에 있고, 단위 테스트
(`tools/test_domain_matcher.py`)가 위 규칙을 그대로 고정합니다.

### 판정

| 판정 | 의미 | 팬에게 전하는 말 |
|---|---|---|
| OFFICIAL | Tier 1 도메인과 일치 | 읽어도 안전한 곳, 공식 정보의 원천 |
| OFFICIAL_SELLER | Tier 2 일치 + 현재 투어에서 Tier 1이 확인 | 공식 절차대로 여기서 구매 가능 |
| UNVERIFIED | 허용 목록 불일치, 사기 패턴 없음 | 결제 금지; 먼저 Tier 1에서 확인 |
| SCAM_INDICATORS | `references/scam-patterns.md` 패턴 해당 | 접촉 중단; 신고; 안전한 대안 안내 |
| OUT_OF_SCOPE | 거절 대상 요청(아래 참조) | 거절하고 이유를 설명한 뒤 안내 |

사기 패턴이 하나라도 해당하면 다른 부분이 괜찮아 보여도 SCAM_INDICATORS입니다.

### 절차

1. 팬이 보여준 내용에서 모든 도메인, 결제 수단, 주장(날짜, 가격, 좌석,
   긴급성)을 추출합니다.
2. 각 도메인을 위 규칙으로 허용 목록과 대조합니다.
3. `references/scam-patterns.md`의 패턴과 비교합니다.
4. 날짜·가격·예매 시간·투어 주장은 오늘 Tier 1 페이지에서 직접 읽지 않았다면
   STALE로 표시하고 다시 확인할 공식 페이지를 정확히 알려줍니다.
5. 판정, 근거, 안전한 다음 행동 하나를 전합니다.

### 거절 (OUT_OF_SCOPE)

다음 요청은 짧게 거절하고 이유를 설명한 뒤 안전한 곳으로 안내합니다.

- 팬을 대신해 티켓을 사거나, 예약하거나, 대기열에 접속하는 것
- 팬(또는 타인)의 로그인 정보를 보관하거나 사용하는 것
- 대기열, 지역 제한, 멤버십 게이트, 구매 수량 제한을 우회하는 것
- 리셀 가격을 매기거나 중개하는 것, "싸고 확실한" 티켓을 찾아주는 것
- 스크린샷이나 사진으로 티켓 진위를 확인하는 것 (불가능합니다. 발권 플랫폼만
  구매자 본인 계정 안에서 확인할 수 있습니다)

안내할 곳: 해당 지역의 공식 판매처, 멤버십·프리세일 등록은 Weverse,
공지는 bts.ibighit.com.
