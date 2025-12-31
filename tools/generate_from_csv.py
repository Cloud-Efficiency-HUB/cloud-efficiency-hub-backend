#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path

REQUIRED_COLS = [
    "cer_id",
    "cloud_provider",
    "focus_category",
    "service",
    "title",
]

MD_TEMPLATE = """# {title}

## Summary
{summary}

## Why this matters
{why}

## Common signals
{signals}

## Recommended action
{action}
"""

def norm(s: str) -> str:
    return (s or "").strip()

def slugify(s: str) -> str:
    s = norm(s).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "unknown"

def validate_row(row: dict, i: int) -> list[str]:
    issues = []
    for c in REQUIRED_COLS:
        if not norm(row.get(c, "")):
            issues.append(f"Row {i}: missing required column '{c}'")
    cer = norm(row.get("cer_id", ""))
    if cer and not re.match(r"^CER-\d{6}$", cer):
        issues.append(f"Row {i}: cer_id should look like CER-000123 (got '{cer}')")
    fc = norm(row.get("focus_category", ""))
    if fc and not fc.startswith("focus_"):
        issues.append(f"Row {i}: focus_category should start with 'focus_' (got '{fc}')")
    return issues

def write_file(path: Path, content: str, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")

def main(csv_path: str, overwrite: bool, dry_run: bool) -> int:
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"❌ CSV not found: {csv_file}")
        return 2

    with csv_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = [c.strip() for c in (reader.fieldnames or [])]
        missing_cols = [c for c in REQUIRED_COLS if c not in cols]
        if missing_cols:
            print(f"❌ CSV is missing required columns: {missing_cols}")
            print(f"   Found columns: {cols}")
            return 2

        rows = list(reader)

    # Validate first (fail fast)
    all_issues = []
    for idx, row in enumerate(rows, start=2):  # header is line 1
        all_issues.extend(validate_row(row, idx))

    if all_issues:
        print("❌ Fix these CSV issues first:")
        for msg in all_issues[:200]:
            print(" -", msg)
        if len(all_issues) > 200:
            print(f"... plus {len(all_issues) - 200} more")
        return 1

    hub_root = Path("hub")
    created = 0

    for row in rows:
        cer_id = norm(row["cer_id"])
        provider = slugify(row["cloud_provider"])
        focus_category = slugify(row["focus_category"])
        service = slugify(row["service"])
        title = norm(row["title"])

        summary = norm(row.get("summary", "")) or "TBD."
        severity = norm(row.get("severity", "")) or "medium"
        status = norm(row.get("status", "")) or "draft"

        # Nice defaults so files aren’t empty
        why = norm(row.get("why", "")) or "TBD."
        signals = norm(row.get("signals", "")) or "- TBD"
        action = norm(row.get("recommended_action", "")) or "TBD."

        out_dir = hub_root / provider / focus_category / service / cer_id
        meta_path = out_dir / "metadata.yaml"
        md_path = out_dir / "inefficiency.md"

        metadata = (
            f"cer_id: {cer_id}\n"
            f"cloud_provider: {provider}\n"
            f"focus_category: {focus_category}\n"
            f"service: {service}\n"
            f"title: {title}\n"
            f"severity: {severity}\n"
            f"status: {status}\n"
        )

        md = MD_TEMPLATE.format(
            title=title,
            summary=summary,
            why=why,
            signals=signals,
            action=action,
        )

        if dry_run:
            print(f"DRY RUN would generate: {out_dir}")
            continue

        write_file(meta_path, metadata, overwrite=overwrite)
        write_file(md_path, md, overwrite=overwrite)
        created += 1

    print(f"✅ Done. Processed {len(rows)} rows. Generated/updated: {created} entries under ./hub/")
    print("   Tip: use --overwrite if you want to regenerate existing files.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate hub/ entries from data/inefficiencies.csv")
    parser.add_argument("--csv", default="data/inefficiencies.csv", help="Path to CSV (default: data/inefficiencies.csv)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing metadata.yaml / inefficiency.md")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created, but don’t write files")
    args = parser.parse_args()
    raise SystemExit(main(args.csv, overwrite=args.overwrite, dry_run=args.dry_run))
