# Release checklist

Steps for cutting a release. Maintainer-facing doc: English-only.

## Before tagging

1. `python3 tools/test_domain_matcher.py` - matcher unit tests pass.
2. `python3 tools/validate_data.py` - no schema errors. Staleness warnings
   must be resolved first (re-verify against a Tier 1 notice, update
   `last_verified`).
3. `python3 tools/eval_runner.py` - zero deterministic failures.
4. `python3 tools/check_links.py` - no FAIL URLs. WARN (bot mitigation) needs
   a human spot check in a browser, not a blind data change.
5. CI green on the commit to be tagged.
6. CHANGELOG.md: move everything under `[Unreleased]` into a new
   `## [x.y.z] - YYYY-MM-DD` section.

## Tag and publish

7. `git tag -a vX.Y.Z -m "..."` on the release commit; push the tag.
8. Create the GitHub Release for the tag with notes copied from the new
   CHANGELOG section, so the Releases page shows what each tag contains.
9. Confirm the README Status line names exactly what the new tag contains
   and what remains unreleased on `main`. Released and unreleased scope must
   never be ambiguous - fans install from `main` and deserve to know which
   parts are community-validated.

## After publishing

10. Verify the install command still works: `npx skills add helenanova/sevensignal`.
11. Close issues delivered by the release; update the roadmap section in
    README.md.
