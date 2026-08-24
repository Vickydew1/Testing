#!/usr/bin/env python3
"""
Fills in a remediation suggestion for every finding that doesn't already
have one (native OpenGrep `fix` covers ~10% of rules - the rest need this).

Reads the same raw result file render_comment.py reads, calls an LLM via
OpenRouter once per finding lacking a native fix, and writes an enriched
copy with a "remediation" field added under extra - which render_comment.py's
loader already checks for (extra.remediation), so no changes needed downstream.

Usage:
  OPENROUTER_API_KEY=... python3 generate_remediation.py result.json result.enriched.json --changed-files=a.js,b.js
  OPENROUTER_API_KEY=... python3 generate_remediation.py result.json result.enriched.json --changed-files=a.js --model=anthropic/claude-sonnet-4.5

NOTE: not live-tested against the real API in this environment (no network
access here) - the request shape matches OpenRouter's documented OpenAI-
compatible chat completions endpoint, but run it once against a real key
before wiring it into a pipeline.
"""
import json
import os
import sys
import urllib.request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"  # any OpenRouter-listed model works


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


def call_openrouter(api_key, prompt, model):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
    }
    req = urllib.request.Request(
        API_URL,
        method="POST",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # OpenRouter asks for these two for attribution/rankings - optional
            # but good practice, replace with your real repo once this ships.
            "HTTP-Referer": "https://github.com/accuknox/pr-decorator",
            "X-Title": "AccuKnox PR Decorator",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    in_path, out_path = sys.argv[1], sys.argv[2]
    api_key = os.environ.get("OPENROUTER_API_KEY")
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
            r["extra"]["remediation"] = f"[DRY RUN - would call {model} via OpenRouter here]"
            generated += 1
            continue
        try:
            r["extra"]["remediation"] = call_openrouter(api_key, prompt, model)
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
