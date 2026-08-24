#!/usr/bin/env python3
"""
Merges alibaba/open-code-review (OCR) output into the existing scan result
file, converting OCR findings into the same OpenGrep-shaped entries
render_comment.py / generate_remediation.py / post_pr_review.py already
know how to parse. Nothing downstream needs to change.

Usage:
  python3 merge_ocr_findings.py results.json ocr_output.json merged.json

NOTE: OCR's exact JSON field names are NOT confirmed - the README and a
third-party technical writeup confirm --format json exists and is meant
for CI consumption, but no published schema was found. This script
defensively checks several likely key names per field and prints a
warning for any finding it can't confidently map, rather than silently
dropping or guessing wrong. Run this once against real `ocr review
--format json` output before trusting it in a pipeline - if the warnings
fire, the actual field names need to be read from the output and this
script's *_KEYS lists updated to match.
"""
import json
import sys

# Candidate key names per field - first match wins. Update these once a
# real OCR JSON output is seen; this is inference, not a confirmed schema.
PATH_KEYS = ["file", "path", "filepath", "file_path"]
LINE_KEYS = ["line", "line_number", "lineNumber", "start_line"]
MESSAGE_KEYS = ["comment", "message", "content", "text"]
PRIORITY_KEYS = ["priority", "severity", "level"]
RULE_KEYS = ["rule", "category", "type"]

HIGH_PRIORITY_VALUES = {"high", "critical", "p0", "p1", "blocker"}
MED_PRIORITY_VALUES = {"medium", "major", "p2"}


def first_present(d, keys, default=None):
    for k in keys:
        if k in d and d[k]:
            return d[k]
    return default


def map_priority_to_severity(value):
    if not value:
        return "WARNING"
    v = str(value).strip().lower()
    if v in HIGH_PRIORITY_VALUES:
        return "ERROR"
    if v in MED_PRIORITY_VALUES:
        return "WARNING"
    return "INFO"


def find_comment_list(ocr_data):
    """OCR's top-level JSON shape isn't confirmed either - try the most
    likely container keys before giving up."""
    if isinstance(ocr_data, list):
        return ocr_data
    for key in ["comments", "results", "findings", "issues", "reviews"]:
        if key in ocr_data and isinstance(ocr_data[key], list):
            return ocr_data[key]
    return []


def convert_ocr_finding(item, index):
    path = first_present(item, PATH_KEYS)
    line = first_present(item, LINE_KEYS, default=1)
    message = first_present(item, MESSAGE_KEYS)
    priority = first_present(item, PRIORITY_KEYS)
    rule = first_present(item, RULE_KEYS, default="quality-issue")

    if not path or not message:
        return None, f"finding #{index}: missing path or message - raw keys seen: {list(item.keys())}"

    severity = map_priority_to_severity(priority)
    try:
        line = int(line)
    except (TypeError, ValueError):
        line = 1

    converted = {
        "check_id": f"ocr.quality.{rule}",
        "path": path,
        "start": {"line": line, "col": 1},
        "end": {"line": line, "col": 1},
        "extra": {
            "message": message,
            "severity": severity,
            "metadata": {"category": "quality", "source": "open-code-review"},
            "fingerprint": f"ocr-{path}-{line}-{index}",
            "lines": "",  # OCR's raw snippet field, if any, isn't confirmed either
        },
    }
    return converted, None


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    results_path, ocr_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(results_path) as f:
        results_data = json.load(f)
    with open(ocr_path) as f:
        ocr_data = json.load(f)

    ocr_items = find_comment_list(ocr_data)
    if not ocr_items:
        print("WARN: no OCR findings recognized - top-level keys were: "
              f"{list(ocr_data.keys()) if isinstance(ocr_data, dict) else 'a list, but empty'}",
              file=sys.stderr)

    converted, skipped = 0, 0
    for i, item in enumerate(ocr_items):
        entry, warning = convert_ocr_finding(item, i)
        if entry:
            results_data.setdefault("results", []).append(entry)
            converted += 1
        else:
            print(f"WARN: {warning}", file=sys.stderr)
            skipped += 1

    with open(out_path, "w") as f:
        json.dump(results_data, f, indent=2)

    print(f"Merged {converted} OCR finding(s), {skipped} unmapped. Wrote {out_path}")
    if skipped > 0:
        print("Unmapped findings mean the *_KEYS field-name guesses at the top "
              "of this script don't match OCR's real output - inspect a raw "
              "ocr_output.json and update them.", file=sys.stderr)


if __name__ == "__main__":
    main()
