#!/usr/bin/env python3
"""Eval runner for every skills/*/evals suite in the repo.

Two explicit tiers of rigor, reported separately:

1. DETERMINISTIC checks - mechanical assertions this runner executes now:
   - every host extractable from a golden case input must match the allowlist,
     and the matcher's verdict must equal the case's expected verdict
   - no host extractable from an adversarial case input may earn a trust
     verdict (OFFICIAL / OFFICIAL_SELLER)
   - domains named in a golden case's must_mention must be allowlist-matched
   A deterministic FAIL is a real bug (data drift, matcher regression, or a
   fixture contradicting the allowlist) and fails the run.

2. LLM-JUDGED cases - verdicts that depend on reading prose: scam-pattern
   screening, refusals, freshness behavior, and routing answers. These need an
   agent (or a human) applying SKILL.md; the runner lists them with their
   expectations so a judged run can score them. They are NEVER silently counted
   as passed. Optional offline scoring: --answers answers.yaml with
   {case_id: answer_text} applies must_mention / must_not string checks.

Run: python3 tools/eval_runner.py [--answers answers.yaml] [--json]
Exit: 0 = all deterministic checks pass, 1 = a deterministic check failed,
3 = PyYAML missing.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import domain_matcher as dm  # noqa: E402

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "error: PyYAML is required for eval_runner.py "
        "(pip install -r requirements-dev.txt)\n"
    )
    raise SystemExit(3)

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")


def discover_skills():
    """Every skills/<name>/ directory that ships an evals/ folder."""
    skills = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, name)
        evals_dir = os.path.join(skill_dir, "evals")
        allowlist = os.path.join(skill_dir, "data", "official-domains.yaml")
        if os.path.isdir(evals_dir):
            skills.append((name, evals_dir,
                           allowlist if os.path.isfile(allowlist) else None))
    return skills

URL_RE = re.compile(r"https?://[^\s)\]>'\"]+")
BARE_DOMAIN_RE = re.compile(r"\b(?:[a-z0-9](?:-?[a-z0-9])*\.)+[a-z]{2,}\b")
TRUST_VERDICTS = {"OFFICIAL", "OFFICIAL_SELLER"}


def extract_hosts(text):
    """Hosts from explicit URLs, plus bare domains mentioned in prose."""
    hosts = []
    for url in URL_RE.findall(text or ""):
        host = dm.extract_host(url.rstrip(".,;"))
        if host:
            hosts.append(host)
    for token in BARE_DOMAIN_RE.findall((text or "").lower()):
        host = dm.normalize_host(token)
        if host and host not in hosts:
            hosts.append(host)
    return hosts


def run_deterministic(case, entries):
    """Automated checks for one case. Returns (checks, fully_deterministic)."""
    suite = case["id"].split("-")[0]
    expected = (case.get("expected") or {}).get("verdict")
    checks = []
    hosts = extract_hosts(case.get("input", ""))

    if suite == "golden" and hosts:
        verdicts = []
        for host in hosts:
            verdict, reason, matched = dm.verdict_for(host, entries)
            verdicts.append(verdict)
            checks.append((f"host {host} matches allowlist",
                           matched is not None,
                           f"verdict={verdict} ({reason})"))
        best = "OFFICIAL" if "OFFICIAL" in verdicts else \
               "OFFICIAL_SELLER" if "OFFICIAL_SELLER" in verdicts else "UNVERIFIED"
        checks.append((f"matcher verdict '{best}' == expected '{expected}'",
                       best == expected, ""))
        # must_mention domains must themselves be allowlist-matched.
        for token in (case.get("expected") or {}).get("must_mention") or []:
            t = token.strip().lower()
            if BARE_DOMAIN_RE.fullmatch(t):
                checks.append((f"must_mention domain '{t}' is allowlist-matched",
                               dm.match_domain(t, [e["domain"] for e in entries])
                               is not None, ""))
        return checks, True  # verdict fully determined by string logic

    if suite == "adversarial" and hosts:
        for host in hosts:
            verdict, reason, matched = dm.verdict_for(host, entries)
            checks.append((f"host {host} earns no trust verdict",
                           verdict not in TRUST_VERDICTS,
                           f"verdict={verdict} ({reason})"))
        # Full verdict (scam patterns, shortener rule) still needs judgment.
        return checks, False

    return checks, False


def score_with_answers(case, answer):
    """must_mention / must_not string checks against a provided answer."""
    expected = case.get("expected") or {}
    lower = (answer or "").lower()
    results = []
    for token in expected.get("must_mention") or []:
        results.append((f"must_mention '{token}'", token.lower() in lower))
    for token in expected.get("must_not") or []:
        # must_not entries are behavior descriptions, not literal strings;
        # they always need a judge. Flag them as uncheckable.
        results.append((f"must_not '{token}' (needs human judgment)", None))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", help="YAML mapping case id -> answer text")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    skills = discover_skills()
    # Skills without their own allowlist share the union of every skill's
    # entries (Tier 1 domains are project-wide). Skills with their own
    # data/official-domains.yaml match against that file.
    all_entries = []
    per_skill = {}
    for name, _evals_dir, allowlist in skills:
        if allowlist:
            per_skill[name] = dm.load_allowlist_entries(allowlist)
            all_entries.extend(per_skill[name])
    answers = {}
    if args.answers:
        with open(args.answers, encoding="utf-8") as fh:
            answers = yaml.safe_load(fh) or {}

    report = {"deterministic": [], "llm_judged": [], "answers_scored": []}
    failures = 0
    for skill_name, evals_dir, allowlist in skills:
        entries = per_skill.get(skill_name) or all_entries
        for fname in sorted(os.listdir(evals_dir)):
            if not fname.endswith(".yaml"):
                continue
            with open(os.path.join(evals_dir, fname), encoding="utf-8") as fh:
                suite = yaml.safe_load(fh)
            if suite.get("suite") == "freshness":
                for cls in suite.get("claim_classes") or []:
                    report["llm_judged"].append({
                        "id": cls["id"], "suite": "freshness",
                        "skill": skill_name,
                        "why": "freshness behavior needs a live agent run",
                        "expectation": cls.get("stale_rule", ""),
                    })
                continue
            for case in suite.get("cases") or []:
                checks, fully = run_deterministic(case, entries)
                if fully:
                    ok = all(p for _n, p, _d in checks)
                    if not ok:
                        failures += 1
                    report["deterministic"].append({
                        "id": case["id"], "skill": skill_name,
                        "result": "PASS" if ok else "FAIL",
                        "checks": [{"check": n, "pass": p, "detail": d}
                                   for n, p, d in checks],
                    })
                else:
                    report["llm_judged"].append({
                        "id": case["id"], "suite": suite["suite"],
                        "skill": skill_name,
                        "why": "verdict depends on prose screening / refusal rules",
                        "expectation": (case.get("expected") or {}).get("verdict"),
                        "automated_subchecks": [
                            {"check": n, "pass": p, "detail": d}
                            for n, p, d in checks] or None,
                    })
                    if any(not p for _n, p, _d in checks):
                        failures += 1
                if case["id"] in answers:
                    report["answers_scored"].append({
                        "id": case["id"],
                        "checks": [{"check": n, "pass": p}
                                   for n, p in score_with_answers(
                                       case, answers[case["id"]])],
                    })

    n_det = len(report["deterministic"])
    n_llm = len(report["llm_judged"])
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("== Deterministic checks (run in CI) ==")
        for item in report["deterministic"]:
            print(f"  [{item['result']}] {item['skill']}/{item['id']}")
            for c in item["checks"]:
                mark = "ok" if c["pass"] else "XX"
                detail = f" - {c['detail']}" if c["detail"] else ""
                print(f"      {mark} {c['check']}{detail}")
        for item in report["llm_judged"]:
            if item.get("automated_subchecks"):
                print(f"  [sub-checks] {item['skill']}/{item['id']}")
                for c in item["automated_subchecks"]:
                    mark = "ok" if c["pass"] else "XX"
                    print(f"      {mark} {c['check']}")
        print()
        print(f"== LLM-judged cases (NOT run here; need an agent applying "
              f"SKILL.md) ==  {n_llm} case(s)")
        for item in report["llm_judged"]:
            print(f"  - {item['skill']}/{item['id']} ({item['suite']}): "
                  f"expect {item.get('expectation', 'n/a')}")
        if report["answers_scored"]:
            print()
            print("== Offline answer scoring (--answers) ==")
            for item in report["answers_scored"]:
                print(f"  {item['id']}")
                for c in item["checks"]:
                    mark = {True: "ok", False: "XX", None: "??"}[c["pass"]]
                    print(f"      {mark} {c['check']}")
        print()
        print(f"eval_runner: {n_det} deterministic case(s), "
              f"{n_llm} LLM-judged case(s), {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
