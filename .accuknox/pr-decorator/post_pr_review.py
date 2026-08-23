#!/usr/bin/env python3
"""
PR Decorator - posts findings to the actual PR.

Reuses render_comment.py's parsing/formatting, then either:
  --dry-run           print the exact API payloads (no network call)
  (no --dry-run)      actually call the GitHub REST API

Required env vars for a real post:
  GITHUB_TOKEN      - needs pull-requests:write, checks:write (or the
                      default GITHUB_TOKEN in a workflow, with those
                      permissions granted in the `permissions:` block)
  GITHUB_REPOSITORY - "owner/repo" (set automatically by Actions)
  PR_NUMBER         - pull request number
  HEAD_SHA          - commit SHA the review attaches to

Usage:
  python3 post_pr_review.py <result.json> --changed-files=a.js,b.js --dry-run
  python3 post_pr_review.py <result.json> --changed-files=a.js,b.js --mode=advisory
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from render_comment import load_findings, render_summary_comment, render_inline_comment  # noqa: E402

API_ROOT = "https://api.github.com"


def build_review_payload(findings, meta, mode):
    """One GitHub 'create a review' call = one summary body + N inline comments.
    This is the correct primitive for bulk PR annotation - avoids N separate
    API calls, and avoids the more restrictive single pull-request-comment
    endpoint that only supports one inline comment per call."""
    comments = []
    for f in findings:
        comments.append({
            "path": f["path"],
            "line": f["start_line"],
            "body": render_inline_comment(f),
        })
    event = "REQUEST_CHANGES" if (mode == "blocking" and any(f["severity"] == "HIGH" for f in findings)) else "COMMENT"
    return {
        "body": render_summary_comment(findings, meta),
        "event": event,
        "comments": comments,
    }


def find_existing_summary_comment(repo, pr_number, token):
    """Look for a prior run's summary comment (by its hidden marker) so we
    update it in place instead of posting a duplicate every push."""
    url = f"{API_ROOT}/repos/{repo}/issues/{pr_number}/comments"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req) as resp:
        comments = json.loads(resp.read())
    for c in comments:
        if "accuknox-pr-decorator:summary" in c.get("body", ""):
            return c["id"]
    return None


def post_or_update_summary(repo, pr_number, token, body, dry_run):
    existing_id = None if dry_run else find_existing_summary_comment(repo, pr_number, token)
    if existing_id:
        url = f"{API_ROOT}/repos/{repo}/issues/comments/{existing_id}"
        method = "PATCH"
    else:
        url = f"{API_ROOT}/repos/{repo}/issues/{pr_number}/comments"
        method = "POST"

    payload = {"body": body}
    if dry_run:
        print(f"[DRY RUN] {method} {url}")
        print(json.dumps(payload, indent=2)[:500], "...\n")
        return

    req = urllib.request.Request(url, method=method,
                                  data=json.dumps(payload).encode(),
                                  headers={"Authorization": f"Bearer {token}",
                                           "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as resp:
        print(f"Summary comment {'updated' if existing_id else 'created'}: {resp.status}")


def post_review(repo, pr_number, head_sha, token, review_payload, dry_run):
    url = f"{API_ROOT}/repos/{repo}/pulls/{pr_number}/reviews"
    payload = {"commit_id": head_sha, **review_payload}
    if dry_run:
        print(f"[DRY RUN] POST {url}")
        print(json.dumps(payload, indent=2)[:1500], "...\n")
        return

    req = urllib.request.Request(url, method="POST",
                                  data=json.dumps(payload).encode(),
                                  headers={"Authorization": f"Bearer {token}",
                                           "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as resp:
        print(f"Review posted: {resp.status}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    result_path = sys.argv[1]
    changed_files, mode, dry_run = None, "advisory", False
    for arg in sys.argv[2:]:
        if arg.startswith("--changed-files="):
            changed_files = set(arg.split("=", 1)[1].split(","))
        elif arg.startswith("--mode="):
            mode = arg.split("=", 1)[1]
        elif arg == "--dry-run":
            dry_run = True

    findings, meta = load_findings(result_path, changed_files)

    repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
    pr_number = os.environ.get("PR_NUMBER", "0")
    head_sha = os.environ.get("HEAD_SHA", meta["sha"] or "unknown")
    token = os.environ.get("GITHUB_TOKEN", "")

    if not dry_run and not token:
        print("ERROR: GITHUB_TOKEN required for a real post. Use --dry-run to preview without one.")
        sys.exit(1)

    summary_body = render_summary_comment(findings, meta)
    post_or_update_summary(repo, pr_number, token, summary_body, dry_run)

    review_payload = build_review_payload(findings, meta, mode)
    post_review(repo, pr_number, head_sha, token, review_payload, dry_run)


if __name__ == "__main__":
    main()
