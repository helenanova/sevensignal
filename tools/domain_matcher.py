#!/usr/bin/env python3
"""Deterministic reference implementation of the sevensignal domain-matching rules.

This module is the executable form of the "Deterministic domain matching" section
of skills/bts-ticket-safety/SKILL.md. It is intentionally dependency-free
(Python standard library only) so anyone can audit and run it.

Documented rules (SKILL.md):
  1. Lowercase the host. Strip a leading "www.".
  2. Match if the host equals a listed domain, or ends with "." + a listed domain.
  3. Anything else is NOT a match. There is no "close enough".

Deliberate strictness (fail closed): a trailing dot ("weverse.io.") is NOT
normalized away, because the documented rules do not normalize it. Anything the
rules do not explicitly cover fails to match and the verdict stays UNVERIFIED.
"""

from urllib.parse import urlsplit

TAXONOMY = ("OFFICIAL", "OFFICIAL_SELLER", "UNVERIFIED", "SCAM_INDICATORS", "OUT_OF_SCOPE")


def normalize_host(host):
    """Lowercase and strip ONE leading 'www.' per the documented rules."""
    h = (host or "").strip().lower()
    if h.startswith("www."):
        h = h[4:]
    return h


def extract_host(value):
    """Best-effort host extraction from a URL or bare host string.

    Handles scheme URLs, scheme-less URLs, ports, and userinfo tricks
    ('https://weverse.io@evil.com' -> 'evil.com'). Returns '' on empty input.
    """
    v = (value or "").strip()
    if not v:
        return ""
    if "://" in v or v.startswith("//"):
        return urlsplit(v).hostname or ""
    if any(c in v for c in "/?#@:"):
        # Scheme-less URL-ish string: parse it as a network-path reference.
        return urlsplit("//" + v).hostname or ""
    return v


def is_valid_hostname(host):
    """Reject strings that are not valid hostnames (empty labels, etc.).

    The documented matching rules operate on real hostnames. Inputs with empty
    labels - leading/trailing dots or doubled dots - are not valid hostnames,
    so they never match. This keeps the matcher fail closed.
    """
    if not host or len(host) > 253:
        return False
    return all(0 < len(label) <= 63 for label in host.split("."))


def match_domain(host, domains):
    """Return the listed domain that `host` matches, or None.

    Longest listed domain wins if several could match (e.g. both
    'interpark.com' and 'tickets.interpark.com' listed).
    """
    h = normalize_host(host)
    if not is_valid_hostname(h):
        return None
    best = None
    for d in domains:
        d = normalize_host(d)
        if h == d or h.endswith("." + d):
            if best is None or len(d) > len(best):
                best = d
    return best


def verdict_for(host, entries):
    """Map a host to the SKILL.md verdict taxonomy.

    entries: iterable of dicts with keys domain, tier (1|2), confirmation
    (tier 2 only: 'confirmed_tier1' or 'unconfirmed_tier1').

    Returns (verdict, reason, matched_domain_or_None). The matcher never emits
    SCAM_INDICATORS or OUT_OF_SCOPE: those come from pattern screening and
    refusal rules, which are agent judgment, not string logic.
    """
    h = normalize_host(host)
    if not is_valid_hostname(h):
        return ("UNVERIFIED", "invalid_hostname", None)
    matches = [e for e in entries if h == e["domain"] or h.endswith("." + e["domain"])]
    if not matches:
        return ("UNVERIFIED", "no_allowlist_match", None)
    entry = max(matches, key=lambda e: len(e["domain"]))
    if entry["tier"] == 1:
        return ("OFFICIAL", "tier1_match", entry["domain"])
    if entry.get("confirmation") == "confirmed_tier1":
        return ("OFFICIAL_SELLER", "tier2_confirmed_tier1", entry["domain"])
    return ("UNVERIFIED", "tier2_unconfirmed_tier1", entry["domain"])


def load_allowlist_entries(path):
    """Convenience loader for the controlled shape of official-domains.yaml.

    Extracts (domain, tier, confirmation) with a small line parser so this tool
    stays dependency-free. This is NOT a general YAML parser; it only supports
    the documented allowlist layout. tools/validate_data.py performs the real
    schema validation with PyYAML in CI.
    """
    entries = []
    tier = None
    current = None
    tier_names = {1: "tier_1_source_of_truth", 2: "tier_2_ticketing_partners"}
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if line.startswith("  tier_1_source_of_truth:"):
                tier = 1
                continue
            if line.startswith("  tier_2_ticketing_partners:"):
                tier = 2
                continue
            if line.startswith("  tier_3_never_authoritative:"):
                tier = None
                continue
            if stripped.startswith("- domain:"):
                if tier not in tier_names:
                    raise ValueError(
                        f"{path}:{lineno}: domain entry outside a recognized tier section"
                    )
                if current:
                    entries.append(current)
                current = {
                    "domain": stripped.split(":", 1)[1].strip(),
                    "tier": tier,
                    "confirmation": None,
                }
                continue
            if current is not None and stripped.startswith("confirmation:"):
                current["confirmation"] = stripped.split(":", 1)[1].strip()
                continue
    if current:
        entries.append(current)
    if not entries:
        raise ValueError(f"{path}: no domain entries found - file shape not recognized")
    return entries


def main(argv=None):
    import argparse
    import json
    import os
    import sys

    parser = argparse.ArgumentParser(
        description="Deterministic domain matcher for the bts-ticket-safety allowlist."
    )
    default_allowlist = os.path.join(
        os.path.dirname(__file__), "..", "skills", "bts-ticket-safety",
        "data", "official-domains.yaml",
    )
    parser.add_argument("inputs", nargs="+", help="hosts or URLs to check")
    parser.add_argument("--allowlist", default=default_allowlist,
                        help="path to official-domains.yaml")
    parser.add_argument("--json", action="store_true", help="emit JSON results")
    args = parser.parse_args(argv)

    entries = load_allowlist_entries(args.allowlist)
    results = []
    for raw in args.inputs:
        host = extract_host(raw)
        verdict, reason, matched = verdict_for(host, entries)
        results.append({
            "input": raw,
            "host": host,
            "matched_domain": matched,
            "verdict": verdict,
            "reason": reason,
        })
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            matched = r["matched_domain"] or "-"
            print(f"{r['input']}  ->  host={r['host'] or '-'}  match={matched}  "
                  f"verdict={r['verdict']}  ({r['reason']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
