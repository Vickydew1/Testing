#!/usr/bin/env python3
"""
PR Decorator - comment renderer
Reads a raw accuknox-aspm-scanner SAST (OpenGrep) result file and renders
a GitHub-ready PR summary comment + inline comments, in the finding schema
from the PR Decorator PRD.

Usage:
    python3 render_comment.py <result.json> [--changed-files path1,path2,...]

If --changed-files is omitted, all findings in the file are treated as
in-scope (this is the "haven't built diff-scoping yet" honest default -
see the note printed at the end).
"""
import json
import sys
import hashlib
from collections import Counter

# Native OpenGrep severity -> AccuKnox-documented severity tier.
# This mapping isn't published anywhere - it's inferred from OpenGrep's own
# convention (ERROR/WARNING/INFO) against the CLI's documented --severity
# vocabulary (CRITICAL/HIGH/MEDIUM/LOW/UNKNOWN). Treat as a placeholder to
# confirm against real console output, not as a confirmed fact.
SEVERITY_MAP = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}
SEVERITY_ICON = {"HIGH": "\U0001F534", "MEDIUM": "\U0001F7E1", "LOW": "\u26AA"}


def load_findings(path, changed_files=None):
    with open(path) as f:
        data = json.load(f)

    findings = []
    for r in data["results"]:
        if changed_files is not None and r["path"] not in changed_files:
            continue  # diff-scope filter, applied client-side since the
                      # scanner itself doesn't support it (see the closing note)
        extra = r["extra"]
        native_sev = extra.get("severity", "INFO")
        findings.append({
            "rule_id": r["check_id"],
            "path": r["path"],
            "start_line": r["start"]["line"],
            "end_line": r["end"]["line"],
            "message": extra.get("message", ""),
            "severity": SEVERITY_MAP.get(native_sev, "LOW"),
            "native_severity": native_sev,
            "cwe": extra.get("metadata", {}).get("cwe", []),
            "owasp": extra.get("metadata", {}).get("owasp"),
            "confidence": extra.get("metadata", {}).get("confidence"),
            "category": extra.get("metadata", {}).get("category"),
            "code": extra.get("lines", ""),
            "fingerprint": extra.get("fingerprint", ""),
            "fix": r.get("fix") or extra.get("fix") or extra.get("remediation"),
        })
    meta = {
        "repo": data.get("repo"),
        "sha": data.get("sha"),
        "ref": data.get("ref"),
        "repo_url": data.get("repo_url"),
        "ai_analysis": data.get("ai_analysis", False),
    }
    return findings, meta


FOOTER = ("\n---\n"
          "🔷 **[AccuKnox ASPM](https://accuknox.com)** — AI-powered, security-first PR review "
          "· [Docs](https://help.accuknox.com) · [Report an issue](https://github.com/accuknox)")


def bucket_category(f):
    """Rough Bug vs Rule-violation split, mirroring Qodo's category badges.
    Anything CWE-mapped or security/injection/secrets-flavored counts as a
    real Bug; everything else (style, best-practice) is a Rule violation.
    We don't detect "Requirement gaps" (PR-vs-ticket-intent mismatches) at
    all yet - that badge always reads 0 until that capability exists."""
    rid = f["rule_id"].lower()
    if f["cwe"] or any(k in rid for k in ("injection", "secret", "xss", "csrf", "auth")):
        return "bug"
    return "rule_violation"


def render_summary_comment(findings, meta):
    counts = Counter(f["severity"] for f in findings)
    total = len(findings)
    bugs = sum(1 for f in findings if bucket_category(f) == "bug")
    rule_violations = sum(1 for f in findings if bucket_category(f) == "rule_violation")
    requirement_gaps = 0  # not a capability we have yet - see note in bucket_category

    lines = []
    lines.append("<!-- accuknox-pr-decorator:summary -->")
    lines.append("## Code Review by AccuKnox")
    lines.append("")
    lines.append(f"`\U0001F41B Bugs ({bugs})` `\U0001F4D8 Rule violations ({rule_violations})` "
                  f"`\U0001F4CE Requirement gaps ({requirement_gaps})`")
    lines.append("")

    if total == 0:
        lines.append("Great, no issues found!")
        lines.append("")
        lines.append("AccuKnox reviewed your code and found no material issues that require review.")
        lines.append("")
        lines.append(f"_Scanned `{meta['ref']}` @ `{(meta['sha'] or '')[:10]}` "
                      f"| AI analysis: {'on' if meta['ai_analysis'] else 'off'}_")
        return "\n".join(lines) + FOOTER

    banner = "\u274C Findings require attention" if counts.get("HIGH") else "\u26A0\uFE0F Findings to review"
    lines.append(f"**{banner}** — {total} finding(s): "
                  f"{counts.get('HIGH',0)} High, {counts.get('MEDIUM',0)} Medium, {counts.get('LOW',0)} Low")
    lines.append("")
    lines.append(f"_Scanned `{meta['ref']}` @ `{(meta['sha'] or '')[:10]}` "
                  f"| AI analysis: {'on' if meta['ai_analysis'] else 'off'}_")
    lines.append("")
    lines.append("| Severity | File | Line | Rule |")
    lines.append("|---|---|---|---|")
    for f in sorted(findings, key=lambda x: (-["LOW","MEDIUM","HIGH"].index(x["severity"]), x["path"])):
        lines.append(f"| {SEVERITY_ICON[f['severity']]} {f['severity']} "
                      f"| `{f['path']}` | {f['start_line']} "
                      f"| `{f['rule_id'].split('.')[-1]}` |")
    return "\n".join(lines) + FOOTER


def render_inline_comment(f):
    lines = []
    lines.append(f"<!-- accuknox-pr-decorator:finding:{f['fingerprint']} -->")
    lines.append(f"{SEVERITY_ICON[f['severity']]} **{f['severity']}** "
                  f"— {f['rule_id'].split('.')[-1].replace('-', ' ')}")
    lines.append("")
    lines.append(f["message"])
    if f["cwe"]:
        lines.append("")
        lines.append("**CWE:** " + "; ".join(f["cwe"]))
    if f["code"]:
        lines.append("")
        lines.append("```")
        lines.append(f["code"].strip())
        lines.append("```")
    lines.append("")
    if f.get("fix"):
        lines.append("**Suggested fix:**")
        lines.append("```suggestion")
        lines.append(f["fix"])
        lines.append("```")
    else:
        lines.append("_No automatic fix available for this rule — remediation needs to be "
                      "AI-generated (see generate_remediation.py) or reviewed manually._")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    result_path = sys.argv[1]
    changed_files = None
    for arg in sys.argv[2:]:
        if arg.startswith("--changed-files="):
            changed_files = set(arg.split("=", 1)[1].split(","))

    findings, meta = load_findings(result_path, changed_files)

    print("=" * 70)
    print("SUMMARY COMMENT (would post once per PR)")
    print("=" * 70)
    print(render_summary_comment(findings, meta))
    print()
    print("=" * 70)
    print(f"INLINE COMMENTS ({len(findings)} total — showing first 3)")
    print("=" * 70)
    for f in findings[:3]:
        print(f"\n--- {f['path']}:{f['start_line']} ---")
        print(render_inline_comment(f))

    print()
    print("=" * 70)
    print("NOTES")
    print("=" * 70)
    if changed_files is None:
        print(f"- No --changed-files passed: all {len(findings)} findings from "
              f"the full-repo scan are shown. Real diff-scoping still needs to "
              f"happen upstream (pass only the PR's changed files into the "
              f"scanner's --command, or filter here once that list exists).")
    print("- Severity mapping (ERROR/WARNING/INFO -> HIGH/MEDIUM/LOW) is inferred, "
          "not confirmed against the console - verify before relying on it.")
    print("- ai_analysis was False on this run, so there's no codeassure output "
          "to render yet - re-run with --ai-analysis to see that shape.")
    print("- Each finding carries a real `fingerprint` from the scanner - that's "
          "the natural key for \"update in place, don't repost\" and for new-vs-"
          "baseline diffing between two runs.")


if __name__ == "__main__":
    main()
