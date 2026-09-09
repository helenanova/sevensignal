#!/usr/bin/env python3
"""Liveness check for the official source URLs the trust data relies on.

Checks every verified_source in official-domains.yaml and every URL in the
freshness evals' recheck_at lists. Standard library only.

Classification:
  OK    2xx/3xx response
  WARN  401/403/429 - reachable but refused; usually bot mitigation. Needs a
        human (or browser) spot check, not an automatic data change.
  FAIL  404/410, 5xx, DNS/connection errors, timeouts - the citation is dead
        or the host is gone. Trust data citing a dead source is a bug.

Exit: 0 always, unless --fail is given and at least one URL is FAIL.
"""

import argparse
import os
import re
import socket
import sys
import urllib.error
import urllib.request

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SKILL_DIR = os.path.join(REPO_ROOT, "skills", "bts-ticket-safety")
ALLOWLIST = os.path.join(SKILL_DIR, "data", "official-domains.yaml")
FRESHNESS = os.path.join(SKILL_DIR, "evals", "freshness.yaml")

USER_AGENT = ("sevensignal-link-check/0.1 "
              "(+https://github.com/helenanova/sevensignal)")
TIMEOUT = 15


URL_RE = re.compile("https?://[^\\s\\]\\[),<>\"']+")


def collect_urls():
    # Every URL in these two files is a check target (verified_source values,
    # recheck_at lists). A general extractor keeps block- and flow-style YAML
    # covered without depending on the file's exact shape.
    urls = []  # (url, where)
    for path, label in ((ALLOWLIST, "official-domains.yaml"),
                        (FRESHNESS, "freshness.yaml")):
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            sys.stderr.write(f"error: cannot read {path}: {exc}\n")
            raise SystemExit(3)
        for url in URL_RE.findall(text):
            urls.append((url.rstrip(".,;"), label))
    # dedupe, keep first source label
    seen = {}
    for url, where in urls:
        seen.setdefault(url, where)
    return sorted(seen.items())


def probe(url):
    """Return (status_class, detail). status_class in {'OK', 'WARN', 'FAIL'}."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return "OK", f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in (405, 501):
            pass  # HEAD unsupported; fall through to GET
        elif exc.code in (301, 302, 303, 307, 308):
            return "OK", f"HTTP {exc.code} redirect"
        elif exc.code in (401, 403, 429):
            return "WARN", f"HTTP {exc.code} (likely bot mitigation)"
        else:
            return "FAIL", f"HTTP {exc.code}"
    except (urllib.error.URLError, socket.timeout, OSError) as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}"
    # GET fallback for servers without HEAD
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            resp.read(512)
            return "OK", f"HTTP {resp.status} (GET)"
    except urllib.error.HTTPError as exc:
        if exc.code in (301, 302, 303, 307, 308):
            return "OK", f"HTTP {exc.code} redirect (GET)"
        if exc.code in (401, 403, 429):
            return "WARN", f"HTTP {exc.code} (GET; likely bot mitigation)"
        return "FAIL", f"HTTP {exc.code} (GET)"
    except (urllib.error.URLError, socket.timeout, OSError) as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fail", action="store_true",
                        help="exit 1 when any URL is FAIL")
    args = parser.parse_args(argv)

    urls = collect_urls()
    counts = {"OK": 0, "WARN": 0, "FAIL": 0}
    for url, where in urls:
        status, detail = probe(url)
        counts[status] += 1
        print(f"{status:4}  {url}  ({detail})  [{where}]")
    print(f"check_links: {counts['OK']} ok, {counts['WARN']} warn, "
          f"{counts['FAIL']} fail, {len(urls)} url(s)")
    if args.fail and counts["FAIL"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
