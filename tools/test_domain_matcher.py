#!/usr/bin/env python3
"""Unit tests for tools/domain_matcher.py - stdlib unittest, no dependencies.

Covers: exact matches, valid subdomains, case/whitespace normalization,
www-stripping, verdict mapping per tier/confirmation, and adversarial
lookalikes (the cases that must NEVER match).

Run: python3 tools/test_domain_matcher.py [-v]
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import domain_matcher as dm  # noqa: E402

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ALLOWLIST = os.path.join(REPO_ROOT, "skills", "bts-ticket-safety", "data",
                         "official-domains.yaml")
ENTRIES = dm.load_allowlist_entries(ALLOWLIST)
DOMAINS = [e["domain"] for e in ENTRIES]


class TestNormalization(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(dm.normalize_host("WeVerse.IO"), "weverse.io")
        self.assertEqual(dm.normalize_host("TICKETMASTER.COM"), "ticketmaster.com")

    def test_strip_leading_www(self):
        self.assertEqual(dm.normalize_host("www.weverse.io"), "weverse.io")
        self.assertEqual(dm.normalize_host("WWW.Weverse.IO"), "weverse.io")

    def test_strip_only_one_www_prefix(self):
        self.assertEqual(dm.normalize_host("www.www.weverse.io"), "www.weverse.io")

    def test_whitespace_stripped(self):
        self.assertEqual(dm.normalize_host("  weverse.io \n"), "weverse.io")

    def test_www2_is_not_stripped(self):
        # Only a literal leading "www." is stripped; "www2" is a normal subdomain.
        self.assertEqual(dm.normalize_host("www2.weverse.io"), "www2.weverse.io")


class TestExtractHost(unittest.TestCase):
    def test_plain_host(self):
        self.assertEqual(dm.extract_host("weverse.io"), "weverse.io")

    def test_url_with_path(self):
        self.assertEqual(dm.extract_host("https://bts.ibighit.com/eng/tour/"),
                         "bts.ibighit.com")

    def test_schemeless_url(self):
        self.assertEqual(dm.extract_host("weverse.io/bts/notice"), "weverse.io")

    def test_port_stripped(self):
        self.assertEqual(dm.extract_host("https://weverse.io:443/bts"), "weverse.io")

    def test_userinfo_trick(self):
        # Classic phish shape: everything before '@' is userinfo, not the host.
        self.assertEqual(dm.extract_host("https://weverse.io@evil.com/"), "evil.com")

    def test_host_in_query_does_not_leak(self):
        self.assertEqual(dm.extract_host("https://evil.com/?next=weverse.io"),
                         "evil.com")

    def test_empty(self):
        self.assertEqual(dm.extract_host(""), "")
        self.assertEqual(dm.extract_host(None), "")


class TestExactAndSubdomainMatches(unittest.TestCase):
    def assertMatches(self, host, expected_domain):
        self.assertEqual(dm.match_domain(host, DOMAINS), expected_domain)

    def test_every_allowlisted_domain_matches_itself(self):
        for d in DOMAINS:
            with self.subTest(domain=d):
                self.assertMatches(d, d)

    def test_documented_subdomain_examples(self):
        # The exact examples in SKILL.md rule 2.
        self.assertMatches("shop.weverse.io", "weverse.io")
        self.assertMatches("help.ticketmaster.co.uk", "ticketmaster.co.uk")

    def test_other_valid_subdomains(self):
        self.assertMatches("bts.ibighit.com", "ibighit.com")
        self.assertMatches("m.world.nol.com", "world.nol.com")
        self.assertMatches("deep.sub.tickets.interpark.com", "tickets.interpark.com")

    def test_www_prefixed_listed_domain(self):
        self.assertMatches("www.ticketmaster.com", "ticketmaster.com")

    def test_uppercase_host_matches(self):
        self.assertMatches("SHOP.Weverse.IO", "weverse.io")


class TestAdversarialLookalikes(unittest.TestCase):
    """Every host here must NOT match. Fail closed, always."""

    def assertNoMatch(self, host):
        self.assertIsNone(dm.match_domain(host, DOMAINS), msg=f"{host} matched!")

    def test_documented_non_match_examples(self):
        # The exact examples in SKILL.md rule 3.
        self.assertNoMatch("ticketmaster.evil.com")
        self.assertNoMatch("interpark-tickets.com")
        self.assertNoMatch("weverse.io.secure-login.net")

    def test_suffix_and_prefix_tricks(self):
        self.assertNoMatch("weverse.io.evil.com")
        self.assertNoMatch("evilweverse.io")
        self.assertNoMatch("weverseio.com")
        self.assertNoMatch("tickets.interpark.com.evil.com")

    def test_hyphen_lookalikes(self):
        self.assertNoMatch("nol-world.com")
        self.assertNoMatch("world-nol.com")
        self.assertNoMatch("ticket-master.com")

    def test_missing_letter_lookalikes(self):
        # The Korea trust bug fixed on 2026-09-08: no 's' is a different host.
        self.assertNoMatch("ticket.interpark.com")
        self.assertNoMatch("ticketsinterpark.com")

    def test_phishing_domains_from_eval_fixtures(self):
        self.assertNoMatch("weverse-verify.net")   # adversarial-05

    def test_link_shorteners(self):
        for shortener in ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd"):
            with self.subTest(shortener=shortener):
                self.assertNoMatch(shortener)

    def test_unicode_homoglyph(self):
        # Cyrillic 'e' (U+0435) in 'weverse' - visually identical, must not match.
        self.assertNoMatch("w\u0435verse.io")
        self.assertNoMatch("w\u0435v\u0435rs\u0435.io")

    def test_punycode_lookalike(self):
        self.assertNoMatch("xn--weverse-9nf.io")

    def test_trailing_dot_fails_closed(self):
        # The documented rules do not normalize a trailing dot, so it must NOT
        # match (fail closed to UNVERIFIED; documented in tools/README.md).
        self.assertNoMatch("weverse.io.")

    def test_empty_and_garbage(self):
        self.assertNoMatch("")
        self.assertNoMatch("   ")
        self.assertNoMatch(".")
        self.assertNoMatch(".weverse.io")   # leading dot: empty label, invalid
        self.assertNoMatch("weverse..io")   # doubled dot: empty label, invalid

    def test_ip_addresses(self):
        self.assertNoMatch("192.168.0.1")
        self.assertNoMatch("127.0.0.1")

    def test_url_based_attacks_end_to_end(self):
        for url in ("https://weverse.io@evil.com/",
                    "https://evil.com/?next=weverse.io",
                    "https://tickets.interpark.com.phish.net/checkout"):
            with self.subTest(url=url):
                host = dm.extract_host(url)
                self.assertIsNone(dm.match_domain(host, DOMAINS), msg=url)


class TestVerdictMapping(unittest.TestCase):
    def verdict(self, host):
        return dm.verdict_for(host, ENTRIES)

    def test_tier1_gives_official(self):
        self.assertEqual(self.verdict("bts.ibighit.com")[0], "OFFICIAL")
        self.assertEqual(self.verdict("shop.weverse.io")[0], "OFFICIAL")

    def test_tier2_confirmed_gives_official_seller(self):
        self.assertEqual(self.verdict("www.ticketmaster.com")[0], "OFFICIAL_SELLER")
        self.assertEqual(self.verdict("world.nol.com")[0], "OFFICIAL_SELLER")
        self.assertEqual(self.verdict("tickets.interpark.com")[0], "OFFICIAL_SELLER")

    def test_tier2_unconfirmed_gives_unverified(self):
        v, reason, matched = self.verdict("ticketmaster.com.au")
        self.assertEqual(v, "UNVERIFIED")
        self.assertEqual(reason, "tier2_unconfirmed_tier1")
        self.assertEqual(matched, "ticketmaster.com.au")
        self.assertEqual(self.verdict("ticketmaster.ph")[0], "UNVERIFIED")

    def test_no_match_gives_unverified(self):
        v, reason, matched = self.verdict("evil.com")
        self.assertEqual(v, "UNVERIFIED")
        self.assertEqual(reason, "no_allowlist_match")
        self.assertIsNone(matched)

    def test_matcher_never_emits_judgment_verdicts(self):
        # SCAM_INDICATORS and OUT_OF_SCOPE come from agent judgment, never from
        # string logic.
        for host in ("evil.com", "weverse-verify.net", "weverse.io", ""):
            self.assertNotIn(self.verdict(host)[0],
                             ("SCAM_INDICATORS", "OUT_OF_SCOPE"))


class TestAllowlistLoader(unittest.TestCase):
    def test_entries_have_required_shape(self):
        self.assertGreaterEqual(len(ENTRIES), 4)
        for e in ENTRIES:
            self.assertIn(e["tier"], (1, 2))
            self.assertEqual(e["domain"], e["domain"].lower())
            self.assertNotIn(" ", e["domain"])
            self.assertFalse(e["domain"].startswith("www."))
            if e["tier"] == 2:
                self.assertIn(e["confirmation"],
                              ("confirmed_tier1", "unconfirmed_tier1"))

    def test_line_parser_agrees_with_pyyaml(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed; consistency check runs in CI")
        with open(ALLOWLIST, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        expected = []
        for tier_key, tier_num in (("tier_1_source_of_truth", 1),
                                   ("tier_2_ticketing_partners", 2)):
            for entry in data["tiers"][tier_key]:
                expected.append({
                    "domain": entry["domain"],
                    "tier": tier_num,
                    "confirmation": entry.get("confirmation"),
                })
        self.assertEqual(sorted(ENTRIES, key=lambda e: e["domain"]),
                         sorted(expected, key=lambda e: e["domain"]))


if __name__ == "__main__":
    unittest.main()
