#!/usr/bin/env python3
"""
Fills in a remediation suggestion for every finding that doesn't already
have one (native OpenGrep `fix` covers ~10% of rules - the rest need this).

Reads the same raw result file render_comment.py reads, calls Claude
directly via the Anthropic Messages API once per finding lacking a native
fix, and writes an enriched copy with a "remediation" field added under
extra - which render_comment.py's loader already checks for
(extra.remediation), so no changes needed downstream.

Usage:
  ANTHROPIC_API_KEY=... python3 generate_remediation.py result.json result.enriched.json --changed-files=a.js,b.js
  ANTHROPIC_API_KEY=... python3 generate_remediation.py result.json result.enriched.json --changed-files=a.js --model=claude-sonnet-4-5

NOTE: not live-tested against the real API in this environment (no network
access here) - the request shape matches the documented Anthropic Messages
API, but run it once against a real key before wiring it into a pipeline.
"""
import json
import os
import sys
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-5"


def build_prompt(result):
    extra = result["extra"]
    return (
        f"You are generating a remediation suggestion for a static analysis finding.\n\n"
        f"Rule: {result['check_id']}\n"
        f"File: {result['path']}\n"
        f"Issue: {extra.get('message', '')}\n\n"
        f"Code:\n```\n{extra.get('lines', '')}\n```\n\n"
        f"Reply with ONLY the corrected code snippet - no explanation, "
        f"no markdown fences, just the fixed lines."
    )


def call_claude(api_key, prompt, model):
    payload = {
        "model": model,
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        API_URL,
        method="POST",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["content"][0]["text"].strip()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    in_path, out_path = sys.argv[1], sys.argv[2]
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    model = DEFAULT_MODEL
    changed_files = None
    for arg in sys.argv[3:]:
        if arg.startswith("--model="):
            model = arg.split("=", 1)[1]
        elif arg.startswith("--changed-files="):
            val = arg.split("=", 1)[1]
            changed_files = set(val.split(",")) if val else set()
    dry_run = "--dry-run" in sys.argv or not api_key

    with open(in_path) as f:
        data = json.load(f)

    generated, skipped, out_of_scope = 0, 0, 0
    for r in data["results"]:
        if changed_files is not None and r["path"] not in changed_files:
            out_of_scope += 1
            continue  # not in this PR's diff - don't spend a call on it
        if r.get("fix") or r["extra"].get("fix"):
            skipped += 1
            continue  # already has a native fix, don't waste a call
        prompt = build_prompt(r)
        if dry_run:
            r["extra"]["remediation"] = f"[DRY RUN - would call {model} via Anthropic API here]"
            generated += 1
            continue
        try:
            r["extra"]["remediation"] = call_claude(api_key, prompt, model)
            generated += 1
        except Exception as e:
            r["extra"]["remediation"] = None
            print(f"WARN: remediation failed for {r['check_id']} @ {r['path']}: {e}",
                  file=sys.stderr)

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"[{mode}] model={model} generated {generated} remediation(s), "
          f"{skipped} already had a native fix, {out_of_scope} out of diff scope (skipped)")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
