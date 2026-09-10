#!/usr/bin/env python3
"""Unit tests for the maintainer tools themselves (validate_data, eval_runner,
check_links). Network calls in check_links are mocked - no live requests.

Run: python3 tools/test_tools.py [-v]
Requires PyYAML (pip install -r requirements-dev.txt).
"""

import datetime
import io
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_links  # noqa: E402
import eval_runner as er  # noqa: E402
import validate_data as vd  # noqa: E402


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


ALLOWLIST_YAML = """\
version: 2
last_reviewed: 2026-09-01
tiers:
  tier_1_source_of_truth:
    - domain: ibighit.com
      role: official site
      regions: global
      verified_source: https://bts.ibighit.com/eng/tour/
      last_verified: 2026-09-01
    - domain: weverse.io
      role: fan platform
      regions: global
      verified_source: https://weverse.io/bts/notice
      last_verified: 2026-09-01
  tier_2_ticketing_partners:
    - domain: tickets.example.com
      role: test seller
      regions: [KR]
      confirmation: confirmed_tier1
      verified_source: https://weverse.io/bts/notice/1
      last_verified: 2026-09-08
  tier_3_never_authoritative:
    classes: []
"""


def make_skill_dir(root, name, allowlist=None, evals=None):
    """Build a minimal skills/<name>/ tree; returns the skills dir path."""
    if allowlist is not None:
        write(os.path.join(root, name, "data", "official-domains.yaml"), allowlist)
    for fname, text in (evals or {}).items():
        write(os.path.join(root, name, "evals", fname), text)
    return root


class ValidateDataHelpers(unittest.TestCase):
    def setUp(self):
        vd.errors.clear()
        vd.warnings.clear()

    def test_parse_date_valid_string(self):
        self.assertEqual(vd.parse_date("2026-09-01", "t"), datetime.date(2026, 9, 1))
        self.assertEqual(vd.errors, [])

    def test_parse_date_accepts_date_objects(self):
        d = datetime.date(2026, 1, 5)
        self.assertEqual(vd.parse_date(d, "t"), d)

    def test_parse_date_rejects_bad_format(self):
        self.assertIsNone(vd.parse_date("09/01/2026", "w"))
        self.assertEqual(len(vd.errors), 1)

    def test_parse_date_rejects_impossible_date(self):
        self.assertIsNone(vd.parse_date("2026-13-40", "w"))
        self.assertEqual(len(vd.errors), 1)

    def test_host_of(self):
        self.assertEqual(vd.host_of("https://BTS.ibighit.com/x?y=1"), "bts.ibighit.com")
        self.assertEqual(vd.host_of("not a url"), "")

    def test_host_matches(self):
        self.assertTrue(vd.host_matches("shop.weverse.io", "weverse.io"))
        self.assertFalse(vd.host_matches("notweverse.io", "weverse.io"))


class ValidateAllowlist(unittest.TestCase):
    """validate_allowlist against synthetic allowlists in a temp skills dir."""

    def setUp(self):
        vd.errors.clear()
        vd.warnings.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.skills_dir = os.path.join(self.tmp.name, "skills")
        os.makedirs(self.skills_dir)
        self._orig_skills_dir = vd.SKILLS_DIR
        vd.SKILLS_DIR = self.skills_dir

    def tearDown(self):
        vd.SKILLS_DIR = self._orig_skills_dir
        self.tmp.cleanup()

    def validate(self, text, today="2026-09-09"):
        make_skill_dir(self.skills_dir, "skill-a", allowlist=text)
        path = os.path.join(self.skills_dir, "skill-a", "data",
                            "official-domains.yaml")
        return vd.validate_allowlist(path,
                                     datetime.date.fromisoformat(today), 30)

    def test_clean_allowlist_passes(self):
        entries = self.validate(ALLOWLIST_YAML)
        self.assertEqual(vd.errors, [])
        self.assertEqual(len(entries), 3)

    def test_duplicate_domain_flagged(self):
        bad = ALLOWLIST_YAML + """
    - domain: ibighit.com
      role: dup
      regions: global
      verified_source: https://bts.ibighit.com/x
      last_verified: 2026-09-01
"""
        # append into tier_1 by replacing the tier_2 header anchor
        bad = ALLOWLIST_YAML.replace(
            "  tier_2_ticketing_partners:",
            "    - domain: ibighit.com\n"
            "      role: dup\n"
            "      regions: global\n"
            "      verified_source: https://bts.ibighit.com/x\n"
            "      last_verified: 2026-09-01\n"
            "  tier_2_ticketing_partners:")
        self.validate(bad)
        self.assertTrue(any("duplicate domain ibighit.com" in e
                            for e in vd.errors))

    def test_tier2_source_must_be_on_tier1_domain(self):
        bad = ALLOWLIST_YAML.replace(
            "verified_source: https://weverse.io/bts/notice/1",
            "verified_source: https://random-blog.example/post")
        self.validate(bad)
        self.assertTrue(any("not on a Tier 1 domain" in e for e in vd.errors))

    def test_future_last_verified_is_error(self):
        bad = ALLOWLIST_YAML.replace("last_verified: 2026-09-01",
                                     "last_verified: 2099-01-01")
        self.validate(bad, today="2026-09-09")
        self.assertTrue(any("in the future" in e for e in vd.errors))

    def test_stale_entry_warns_not_errors(self):
        self.validate(ALLOWLIST_YAML, today="2027-06-01")
        self.assertEqual(vd.errors, [])
        self.assertTrue(any("STALE" in w for w in vd.warnings))

    def test_tier2_entry_missing_confirmation_flagged(self):
        bad = ALLOWLIST_YAML.replace("      confirmation: confirmed_tier1\n", "")
        self.validate(bad)
        self.assertTrue(any("confirmation must be one of" in e
                            for e in vd.errors))


class ValidateEvalFile(unittest.TestCase):
    def setUp(self):
        vd.errors.clear()
        vd.warnings.clear()
        self.tier1 = ["ibighit.com", "weverse.io"]

    def validate(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(text)
            path = fh.name
        try:
            vd.validate_eval_file(path, self.tier1)
        finally:
            os.unlink(path)

    def test_duplicate_case_ids_flagged(self):
        self.validate("""\
suite: golden
cases:
  - id: golden-01
    input: a
    expected: {verdict: OFFICIAL}
    rationale: x
  - id: golden-01
    input: b
    expected: {verdict: OFFICIAL}
    rationale: y
""")
        self.assertTrue(any("duplicate id" in e for e in vd.errors))

    def test_wrong_id_prefix_flagged(self):
        self.validate("""\
suite: golden
cases:
  - id: adversarial-99
    input: a
    expected: {verdict: UNVERIFIED}
    rationale: x
""")
        self.assertTrue(any("must start with 'golden-'" in e
                            for e in vd.errors))

    def test_freshness_recheck_must_be_tier1(self):
        self.validate("""\
suite: freshness
claim_classes:
  - id: freshness-01
    claim_type: dates
    example_input: x
    stale_rule: y
    recheck_at: ["https://random-blog.example/post"]
""")
        self.assertTrue(any("not on a Tier 1 domain" in e for e in vd.errors))


class EvalRunnerHelpers(unittest.TestCase):
    ENTRIES = [{"domain": "ibighit.com", "tier": 1, "confirmation": None},
               {"domain": "weverse.io", "tier": 1, "confirmation": None},
               {"domain": "tickets.example.com", "tier": 2,
                "confirmation": "confirmed_tier1"},
               {"domain": "maybe.example.com", "tier": 2,
                "confirmation": "unconfirmed_tier1"}]

    def test_extract_hosts_urls_and_bare_domains(self):
        hosts = er.extract_hosts(
            "see https://bts.ibighit.com/eng/tour/ and shop.weverse.io today")
        self.assertIn("bts.ibighit.com", hosts)
        self.assertIn("shop.weverse.io", hosts)

    def test_golden_case_passes_when_verdict_matches(self):
        case = {"id": "golden-99",
                "input": "Fan: is https://bts.ibighit.com/eng/tour/ official?",
                "expected": {"verdict": "OFFICIAL",
                             "must_mention": ["bts.ibighit.com"]}}
        checks, fully = er.run_deterministic(case, self.ENTRIES)
        self.assertTrue(fully)
        self.assertTrue(all(p for _n, p, _d in checks),
                        [c for c in checks if not c[1]])

    def test_golden_case_fails_when_verdict_mismatches(self):
        case = {"id": "golden-98",
                "input": "Fan: is https://maybe.example.com/x official?",
                "expected": {"verdict": "OFFICIAL", "must_mention": []}}
        checks, fully = er.run_deterministic(case, self.ENTRIES)
        self.assertTrue(fully)
        self.assertFalse(all(p for _n, p, _d in checks))

    def test_adversarial_subcheck_fails_if_host_would_be_trusted(self):
        case = {"id": "adversarial-98",
                "input": "Fan: trust https://tickets.example.com/x ?",
                "expected": {"verdict": "UNVERIFIED"}}
        checks, fully = er.run_deterministic(case, self.ENTRIES)
        self.assertFalse(fully)  # adversarial is never fully deterministic
        self.assertFalse(all(p for _n, p, _d in checks))

    def test_score_with_answers_checks_must_mention(self):
        case = {"id": "refusal-01",
                "expected": {"must_mention": ["members-only"],
                             "must_not": ["accept credentials"]}}
        results = er.score_with_answers(
            case, "This is members-only content; read it in your own account.")
        by_name = {n: p for n, p in results}
        self.assertTrue(by_name["must_mention 'members-only'"])
        # must_not entries are human-judged only
        self.assertIsNone(by_name["must_not 'accept credentials' "
                                  "(needs human judgment)"])

    def test_score_with_answers_flags_missing_mention(self):
        case = {"id": "x", "expected": {"must_mention": ["weverse.io"]}}
        results = er.score_with_answers(case, "no relevant text here")
        self.assertFalse(results[0][1])


def fake_response(status=200):
    resp = mock.Mock()
    resp.status = status
    resp.read.return_value = b""
    resp.__enter__ = lambda s: s
    resp.__exit__ = lambda s, *a: False
    return resp


def http_error(code):
    return urllib.error.HTTPError("http://x", code, "msg", {}, None)


class CheckLinksProbing(unittest.TestCase):
    """check_links.probe classification with the network fully mocked."""

    def probe_with(self, side_effect):
        with mock.patch.object(
                check_links.urllib.request, "urlopen",
                side_effect=side_effect) as m:
            return check_links.probe("https://example.com/x"), m

    def test_head_200_is_ok(self):
        (status, _detail), _m = self.probe_with([fake_response(200)])
        self.assertEqual(status, "OK")

    def test_redirect_is_ok(self):
        (status, _d), _m = self.probe_with([http_error(301)])
        self.assertEqual(status, "OK")

    def test_403_is_warn(self):
        (status, detail), _m = self.probe_with([http_error(403)])
        self.assertEqual(status, "WARN")
        self.assertIn("403", detail)

    def test_404_is_fail(self):
        (status, _d), _m = self.probe_with([http_error(404)])
        self.assertEqual(status, "FAIL")

    def test_500_is_fail(self):
        (status, _d), _m = self.probe_with([http_error(500)])
        self.assertEqual(status, "FAIL")

    def test_head_405_falls_back_to_get(self):
        (status, detail), m = self.probe_with(
            [http_error(405), fake_response(200)])
        self.assertEqual(status, "OK")
        self.assertIn("GET", detail)
        self.assertEqual(m.call_count, 2)

    def test_get_fallback_warns_on_403(self):
        (status, _d), m = self.probe_with([http_error(405), http_error(403)])
        self.assertEqual(status, "WARN")
        self.assertEqual(m.call_count, 2)

    def test_dns_failure_is_fail(self):
        err = urllib.error.URLError("name or service not known")
        (status, _d), _m = self.probe_with([err])
        self.assertEqual(status, "FAIL")

    def test_timeout_is_fail(self):
        (status, _d), _m = self.probe_with([TimeoutError("timed out")])
        self.assertEqual(status, "FAIL")


class CheckLinksCollectUrls(unittest.TestCase):
    def test_collects_urls_from_allowlist_and_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = os.path.join(tmp, "skills")
            make_skill_dir(
                skills, "skill-a", allowlist=ALLOWLIST_YAML,
                evals={"freshness.yaml": """\
suite: freshness
claim_classes:
  - id: freshness-01
    claim_type: dates
    example_input: x
    stale_rule: y
    recheck_at: ["https://bts.ibighit.com/eng/tour/"]
"""})
            orig = check_links.SKILLS_DIR
            check_links.SKILLS_DIR = skills
            try:
                urls = dict(check_links.collect_urls())
            finally:
                check_links.SKILLS_DIR = orig
        self.assertIn("https://bts.ibighit.com/eng/tour/", urls)
        self.assertIn("https://weverse.io/bts/notice/1", urls)


if __name__ == "__main__":
    unittest.main()
