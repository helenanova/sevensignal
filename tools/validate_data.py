#!/usr/bin/env python3
"""Schema and freshness validation for sevensignal trust data and eval fixtures.

Checks skills/bts-ticket-safety/data/official-domains.yaml against the rules in
CONTRIBUTING.md and SKILL.md, plus the eval fixture files against the schema in
evals/README.md. Also parses every other YAML file in the repo for basic sanity.

Staleness fail-safe (the "data older than 30 days triggers warnings" rule):
  Every allowlist entry whose last_verified is more than --max-age-days old,
  and the file-level last_reviewed, produces a WARNING. Warnings do not fail
  the run unless --fail-on-stale is given (used by the scheduled freshness
  workflow). Pass --today YYYY-MM-DD for a deterministic run.

Requires PyYAML (see requirements-dev.txt). The domain matcher itself stays
dependency-free; this is a maintainer tool.

Exit codes: 0 = clean (or warnings only), 1 = schema/validation errors,
2 = stale data (only with --fail-on-stale and no schema errors).
"""

import argparse
import datetime
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "error: PyYAML is required for validate_data.py "
        "(pip install -r requirements-dev.txt)\n"
    )
    raise SystemExit(3)

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SKILL_DIR = os.path.join(REPO_ROOT, "skills", "bts-ticket-safety")
ALLOWLIST = os.path.join(SKILL_DIR, "data", "official-domains.yaml")
EVALS_DIR = os.path.join(SKILL_DIR, "evals")

DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9](-?[a-z0-9])*\.)+[a-z]{2,63}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERDICTS = {"OFFICIAL", "OFFICIAL_SELLER", "UNVERIFIED", "SCAM_INDICATORS",
            "OUT_OF_SCOPE"}
CONFIRMATIONS = {"confirmed_tier1", "unconfirmed_tier1"}

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def parse_date(value, where):
    if isinstance(value, datetime.date):
        return value
    if not isinstance(value, str) or not DATE_RE.match(value):
        err(f"{where}: expected ISO date YYYY-MM-DD, got {value!r}")
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        err(f"{where}: invalid date {value!r}")
        return None


def host_of(url):
    m = re.match(r"^https?://([^/?#]+)", url or "")
    return m.group(1).lower() if m else ""


def host_matches(host, domain):
    return host == domain or host.endswith("." + domain)


def validate_allowlist(today, max_age_days):
    try:
        with open(ALLOWLIST, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        err(f"official-domains.yaml: cannot load: {exc}")
        return []

    if not isinstance(data, dict):
        err("official-domains.yaml: top level must be a mapping")
        return []
    if not isinstance(data.get("version"), int):
        err("official-domains.yaml: 'version' must be an integer")
    last_reviewed = parse_date(data.get("last_reviewed"),
                               "official-domains.yaml last_reviewed")
    if last_reviewed:
        if last_reviewed > today:
            err(f"last_reviewed {last_reviewed} is in the future")
        age = (today - last_reviewed).days
        if age > max_age_days:
            warn(f"STALE: allowlist last_reviewed {last_reviewed} is "
                 f"{age} days old (limit {max_age_days})")

    tiers = data.get("tiers") or {}
    for required in ("tier_1_source_of_truth", "tier_2_ticketing_partners",
                     "tier_3_never_authoritative"):
        if required not in tiers:
            err(f"official-domains.yaml: missing tiers.{required}")

    tier1_domains = [e.get("domain", "")
                     for e in tiers.get("tier_1_source_of_truth") or []]
    entries = []
    seen = set()
    for tier_key, tier_num in (("tier_1_source_of_truth", 1),
                               ("tier_2_ticketing_partners", 2)):
        tier_entries = tiers.get(tier_key) or []
        if not isinstance(tier_entries, list):
            err(f"{tier_key}: must be a list")
            continue
        for i, entry in enumerate(tier_entries):
            where = f"{tier_key}[{i}]"
            if not isinstance(entry, dict):
                err(f"{where}: entry must be a mapping")
                continue
            domain = entry.get("domain")
            if not isinstance(domain, str) or not DOMAIN_RE.match(domain):
                err(f"{where}: bad domain {domain!r} (lowercase registrable "
                    f"domain, no 'www.', no spaces)")
                continue
            if domain in seen:
                err(f"{where}: duplicate domain {domain}")
            seen.add(domain)
            if tier_num == 2 and domain in tier1_domains:
                err(f"{where}: {domain} is already a Tier 1 domain")
            for field in ("role", "regions", "verified_source"):
                if field not in entry:
                    err(f"{where} ({domain}): missing '{field}'")
            source = entry.get("verified_source", "")
            if not str(source).startswith("https://"):
                err(f"{where} ({domain}): verified_source must be an https URL")
            else:
                source_host = host_of(str(source))
                if tier_num == 2 and not any(
                        host_matches(source_host, t1) for t1 in tier1_domains):
                    # Executable form of 'Tier 1 confirms Tier 2'.
                    err(f"{where} ({domain}): verified_source host "
                        f"'{source_host}' is not on a Tier 1 domain - a Tier 2 "
                        f"entry must cite a Tier 1 notice")
                if tier_num == 1 and not any(
                        host_matches(source_host, t1) for t1 in tier1_domains):
                    err(f"{where} ({domain}): Tier 1 verified_source host "
                        f"'{source_host}' is not itself on a Tier 1 domain")
            confirmation = entry.get("confirmation")
            if tier_num == 2:
                if confirmation not in CONFIRMATIONS:
                    err(f"{where} ({domain}): confirmation must be one of "
                        f"{sorted(CONFIRMATIONS)}")
            elif confirmation is not None:
                err(f"{where} ({domain}): Tier 1 entries do not carry a "
                    f"confirmation field")
            verified = parse_date(entry.get("last_verified"),
                                  f"{where} ({domain}) last_verified")
            if verified:
                if verified > today:
                    err(f"{where} ({domain}): last_verified {verified} is in "
                        f"the future")
                age = (today - verified).days
                if age > max_age_days:
                    warn(f"STALE: {domain} last_verified {verified} is "
                         f"{age} days old (limit {max_age_days})")
            entries.append({"domain": domain, "tier": tier_num,
                            "confirmation": confirmation,
                            "last_verified": verified})
    return entries


def validate_eval_file(path, tier1_domains):
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        err(f"{name}: cannot load: {exc}")
        return
    if not isinstance(data, dict):
        err(f"{name}: top level must be a mapping")
        return
    suite = data.get("suite")
    if not isinstance(suite, str):
        err(f"{name}: missing 'suite'")
        return

    if suite == "freshness":
        classes = data.get("claim_classes")
        if not isinstance(classes, list) or not classes:
            err(f"{name}: 'claim_classes' must be a non-empty list")
            return
        seen = set()
        for cls in classes:
            cid = (cls or {}).get("id", "?")
            if cid in seen:
                err(f"{name}: duplicate id {cid}")
            seen.add(cid)
            if not str(cid).startswith("freshness-"):
                err(f"{name}: id {cid} must start with 'freshness-'")
            for field in ("claim_type", "example_input", "stale_rule"):
                if not (cls or {}).get(field):
                    err(f"{name} ({cid}): missing '{field}'")
            recheck = (cls or {}).get("recheck_at")
            if not isinstance(recheck, list) or not recheck:
                err(f"{name} ({cid}): 'recheck_at' must be a non-empty list")
                continue
            for target in recheck:
                if str(target).startswith("http"):
                    host = host_of(str(target))
                    if not any(host_matches(host, t1) for t1 in tier1_domains):
                        err(f"{name} ({cid}): recheck_at URL '{target}' is not "
                            f"on a Tier 1 domain")
                elif "tier 1" not in str(target).lower():
                    err(f"{name} ({cid}): recheck_at prose '{target}' must "
                        f"name a Tier 1 source")
        return

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        err(f"{name}: 'cases' must be a non-empty list")
        return
    seen = set()
    for case in cases:
        cid = (case or {}).get("id", "?")
        if cid in seen:
            err(f"{name}: duplicate id {cid}")
        seen.add(cid)
        if not str(cid).startswith(f"{suite}-"):
            err(f"{name}: id {cid} must start with '{suite}-'")
        if not (case or {}).get("input"):
            err(f"{name} ({cid}): missing 'input'")
        expected = (case or {}).get("expected")
        if not isinstance(expected, dict):
            err(f"{name} ({cid}): missing 'expected' block")
            continue
        if expected.get("verdict") not in VERDICTS:
            err(f"{name} ({cid}): verdict must be one of {sorted(VERDICTS)}")
        for field in ("must_mention", "must_not"):
            if field in expected and not (
                    isinstance(expected[field], list)
                    and all(isinstance(x, str) for x in expected[field])):
                err(f"{name} ({cid}): '{field}' must be a list of strings")
        if not (case or {}).get("rationale"):
            err(f"{name} ({cid}): missing 'rationale'")


def validate_yaml_parses():
    """Every other YAML file in the repo must at least parse."""
    for root, _dirs, files in os.walk(REPO_ROOT):
        if ".git" in root.split(os.sep):
            continue
        for fname in files:
            if not fname.endswith((".yml", ".yaml")):
                continue
            path = os.path.join(root, fname)
            if os.path.abspath(path) in (os.path.abspath(ALLOWLIST),) or \
               os.path.dirname(os.path.abspath(path)) == os.path.abspath(EVALS_DIR):
                continue  # schema-validated above
            try:
                with open(path, encoding="utf-8") as fh:
                    yaml.safe_load(fh)
            except yaml.YAMLError as exc:
                err(f"{os.path.relpath(path, REPO_ROOT)}: YAML parse error: {exc}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--today", help="YYYY-MM-DD; defaults to system date")
    parser.add_argument("--max-age-days", type=int, default=30,
                        help="staleness threshold for last_verified/last_reviewed")
    parser.add_argument("--fail-on-stale", action="store_true",
                        help="exit 2 when any entry is stale")
    args = parser.parse_args(argv)

    today = (datetime.date.fromisoformat(args.today) if args.today
             else datetime.date.today())

    entries = validate_allowlist(today, args.max_age_days)
    tier1_domains = [e["domain"] for e in entries if e["tier"] == 1]
    for fname in sorted(os.listdir(EVALS_DIR)):
        if fname.endswith(".yaml"):
            validate_eval_file(os.path.join(EVALS_DIR, fname), tier1_domains)
    validate_yaml_parses()

    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"validate_data: {len(errors)} error(s), {len(warnings)} warning(s), "
          f"{len(entries)} allowlist entries checked (today={today}, "
          f"max_age={args.max_age_days}d)")
    if errors:
        return 1
    if warnings and args.fail_on_stale:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
