#!/usr/bin/env python3
"""
UI/UX PRO MAX v8.0 — Data Lookup Engine

Programmatic lookup tool for style/palette/font/rule data.
Searches across all CSV data files for matching records.

Usage:
    python3 lookup.py --domain color --query "SaaS" --format json
    python3 lookup.py --domain style --query "glassmorphism" --format table
    python3 lookup.py --domain stack:nextjs --query "routing" --format csv
    python3 lookup.py --list-domains
    python3 lookup.py --domain ux --query "animation" --count
"""

import argparse
import csv
import json
import os
import sys
from difflib import SequenceMatcher
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DATA_DIR = SKILL_ROOT / "data"
INDEX_PATH = DATA_DIR / "index.json"

# Domain → relative CSV path (from DATA_DIR)
DOMAIN_MAP = {
    "color": "colors.csv",
    "style": "styles.csv",
    "typography": "typography.csv",
    "ux": "ux-guidelines.csv",
    "chart": "charts.csv",
    "icon": "icons.csv",
    "reasoning": "ui-reasoning.csv",
    "web": "web-interface.csv",
    "performance": "react-performance.csv",
    "landing": "landing.csv",
    "product": "products.csv",
    # Stacks
    "stack:astro": "stacks/astro.csv",
    "stack:flutter": "stacks/flutter.csv",
    "stack:html-tailwind": "stacks/html-tailwind.csv",
    "stack:jetpack-compose": "stacks/jetpack-compose.csv",
    "stack:nextjs": "stacks/nextjs.csv",
    "stack:nuxt-ui": "stacks/nuxt-ui.csv",
    "stack:nuxtjs": "stacks/nuxtjs.csv",
    "stack:react-native": "stacks/react-native.csv",
    "stack:react": "stacks/react.csv",
    "stack:shadcn": "stacks/shadcn.csv",
    "stack:svelte": "stacks/svelte.csv",
    "stack:swiftui": "stacks/swiftui.csv",
    "stack:vue": "stacks/vue.csv",
}

# Aliases for convenience
ALIAS_MAP = {
    "colors": "color",
    "styles": "style",
    "fonts": "typography",
    "typo": "typography",
    "ux-guidelines": "ux",
    "ux-guideline": "ux",
    "guidelines": "ux",
    "charts": "chart",
    "icons": "icon",
    "ui-reasoning": "reasoning",
    "reasoning": "reasoning",
    "web-interface": "web",
    "web-interface-guidelines": "web",
    "react-perf": "performance",
    "react-performance": "performance",
    "perf": "performance",
    "landing-page": "landing",
    "landings": "landing",
    "products": "product",
    "astro": "stack:astro",
    "flutter": "stack:flutter",
    "html-tailwind": "stack:html-tailwind",
    "tailwind": "stack:html-tailwind",
    "jetpack-compose": "stack:jetpack-compose",
    "compose": "stack:jetpack-compose",
    "nextjs": "stack:nextjs",
    "next": "stack:nextjs",
    "next.js": "stack:nextjs",
    "nuxt-ui": "stack:nuxt-ui",
    "nuxtui": "stack:nuxt-ui",
    "nuxtjs": "stack:nuxtjs",
    "nuxt": "stack:nuxtjs",
    "nuxt.js": "stack:nuxtjs",
    "react-native": "stack:react-native",
    "rn": "stack:react-native",
    "react": "stack:react",
    "shadcn": "stack:shadcn",
    "shadcn-ui": "stack:shadcn",
    "svelte": "stack:svelte",
    "swiftui": "stack:swiftui",
    "vue": "stack:vue",
    "vuejs": "stack:vue",
}

FUZZY_THRESHOLD = 0.6  # Minimum similarity ratio for fuzzy matching

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def resolve_domain(domain: str) -> str:
    """Resolve domain aliases to canonical domain names."""
    domain_lower = domain.lower().strip()
    if domain_lower in DOMAIN_MAP:
        return domain_lower
    if domain_lower in ALIAS_MAP:
        return ALIAS_MAP[domain_lower]
    # Try stack: prefix
    if not domain_lower.startswith("stack:"):
        prefixed = f"stack:{domain_lower}"
        if prefixed in DOMAIN_MAP:
            return prefixed
    raise ValueError(
        f"Unknown domain: '{domain}'. Use --list-domains to see available domains."
    )


def get_csv_path(domain: str) -> Path:
    """Get the full path to the CSV file for a domain."""
    relative = DOMAIN_MAP.get(domain)
    if not relative:
        raise ValueError(f"No CSV file mapped for domain: '{domain}'")
    path = DATA_DIR / relative
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return path


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    """Read a CSV file and return (headers, rows). Each row is a dict."""
    rows = []
    headers = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        for row in reader:
            # Skip empty rows
            if any(v.strip() for v in row.values()):
                rows.append(row)
    return headers, rows


def exact_match(query: str, value: str) -> bool:
    """Check if query appears in value (case-insensitive)."""
    return query.lower() in value.lower()


def fuzzy_match(query: str, value: str, threshold: float = FUZZY_THRESHOLD) -> bool:
    """Check if query fuzzy-matches value above threshold."""
    if not value.strip():
        return False
    # Check if query is a substring first (cheaper)
    if query.lower() in value.lower():
        return True
    # Token-level matching: check if any word in query fuzzy-matches any word in value
    query_tokens = query.lower().split()
    value_tokens = value.lower().split()
    for qt in query_tokens:
        for vt in value_tokens:
            ratio = SequenceMatcher(None, qt, vt).ratio()
            if ratio >= threshold:
                return True
    # Full string comparison for short values
    ratio = SequenceMatcher(None, query.lower(), value.lower()).ratio()
    return ratio >= threshold


def search_rows(
    rows: list[dict], query: str, columns: list[str] | None = None, fuzzy: bool = True
) -> list[dict]:
    """Search rows for query term across all (or specified) columns."""
    matches = []
    for row in rows:
        matched = False
        cols_to_search = columns if columns else list(row.keys())
        for col in cols_to_search:
            value = row.get(col, "")
            if exact_match(query, value):
                matched = True
                break
            if fuzzy and fuzzy_match(query, value):
                matched = True
                break
        if matched:
            matches.append(row)
    return matches


def format_json(rows: list[dict], headers: list[str]) -> str:
    """Format results as JSON."""
    return json.dumps(rows, indent=2, ensure_ascii=False)


def format_csv(rows: list[dict], headers: list[str]) -> str:
    """Format results as CSV."""
    import io

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return output.getvalue().strip()


def format_table(rows: list[dict], headers: list[str]) -> str:
    """Format results as a readable text table."""
    if not rows:
        return "No matching records found."

    # Truncate long values for display
    max_col_width = 50

    def truncate(val: str) -> str:
        val = val.replace("\n", " ").strip()
        if len(val) > max_col_width:
            return val[: max_col_width - 3] + "..."
        return val

    # Calculate column widths
    col_widths = {}
    for h in headers:
        col_widths[h] = min(len(h), max_col_width)
    for row in rows:
        for h in headers:
            val_len = len(truncate(row.get(h, "")))
            col_widths[h] = min(max(col_widths[h], val_len), max_col_width)

    # For many columns, show a compact view
    if len(headers) > 6:
        # Show key columns only in table, full data in JSON/CSV
        key_cols = headers[:4]  # First 4 columns
        col_widths = {h: col_widths[h] for h in key_cols}
        headers_display = key_cols
        note = f"\n  ({len(headers) - 4} more columns — use --format json to see all fields)"
    else:
        headers_display = headers
        note = ""

    # Build table
    lines = []

    # Header
    header_line = " | ".join(h.ljust(col_widths[h]) for h in headers_display)
    separator = "-+-".join("-" * col_widths[h] for h in headers_display)
    lines.append(header_line)
    lines.append(separator)

    # Rows
    for row in rows:
        row_line = " | ".join(
            truncate(row.get(h, "")).ljust(col_widths[h]) for h in headers_display
        )
        lines.append(row_line)

    lines.append(f"\n  {len(rows)} record(s) found.{note}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# List domains
# ---------------------------------------------------------------------------


def list_domains() -> str:
    """Return a formatted list of all available domains."""
    lines = []
    lines.append("Available Domains:")
    lines.append("=" * 60)

    # Load index for descriptions
    index = {}
    if INDEX_PATH.exists():
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            index = json.load(f)

    file_info = {fi["domain"]: fi for fi in index.get("files", [])}

    # Core domains
    lines.append("\n  Core Domains:")
    lines.append("-" * 60)
    core_domains = [d for d in DOMAIN_MAP if not d.startswith("stack:")]
    for domain in core_domains:
        info = file_info.get(domain, {})
        desc = info.get("description", "No description")[:60]
        count = info.get("recordCount", "?")
        lines.append(f"    {domain:<16} ({count:>3} records)  {desc}")

    # Stack domains
    lines.append("\n  Stack Domains:")
    lines.append("-" * 60)
    stack_domains = [d for d in DOMAIN_MAP if d.startswith("stack:")]
    for domain in sorted(stack_domains):
        info = file_info.get(domain, {})
        stack_name = domain.replace("stack:", "")
        count = info.get("recordCount", "?")
        lines.append(f"    {domain:<26} ({count:>3} records)")

    # Aliases
    lines.append("\n  Common Aliases:")
    lines.append("-" * 60)
    alias_groups = {}
    for alias, canonical in ALIAS_MAP.items():
        if canonical not in alias_groups:
            alias_groups[canonical] = []
        alias_groups[canonical].append(alias)
    for canonical, aliases in alias_groups.items():
        if aliases:
            lines.append(f"    {canonical:<16} ← {', '.join(aliases[:5])}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="UI/UX PRO MAX v8.0 — Data Lookup Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lookup.py --list-domains
  python3 lookup.py --domain color --query "SaaS" --format json
  python3 lookup.py --domain style --query "glassmorphism" --format table
  python3 lookup.py --domain stack:nextjs --query "routing" --format csv
  python3 lookup.py --domain ux --query "animation" --count
  python3 lookup.py --domain typography --query "luxury" --format json
  python3 lookup.py --domain icon --query "menu" --format table
  python3 lookup.py --domain product --query "fintech" --format json
        """,
    )
    parser.add_argument(
        "--domain",
        "-d",
        type=str,
        help="Data domain to search (e.g., color, style, typography, ux, stack:nextjs)",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Search term to look up across all columns",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["json", "csv", "table"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--list-domains",
        "-l",
        action="store_true",
        help="List all available data domains",
    )
    parser.add_argument(
        "--count",
        "-c",
        action="store_true",
        help="Return only the count of matching records",
    )
    parser.add_argument(
        "--exact",
        "-e",
        action="store_true",
        help="Use exact matching only (no fuzzy matching)",
    )
    parser.add_argument(
        "--column",
        type=str,
        help="Search only in a specific column name",
    )

    args = parser.parse_args()

    # List domains mode
    if args.list_domains:
        print(list_domains())
        return

    # Validate required arguments
    if not args.domain:
        parser.error("--domain is required (use --list-domains to see available domains)")
    if not args.query:
        parser.error("--query is required")

    # Resolve domain
    try:
        domain = resolve_domain(args.domain)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Get CSV path
    try:
        csv_path = get_csv_path(domain)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Read data
    headers, rows = read_csv(csv_path)

    # Search
    columns = [args.column] if args.column else None
    matches = search_rows(rows, args.query, columns=columns, fuzzy=not args.exact)

    # Count mode
    if args.count:
        print(len(matches))
        return

    # Format output
    if args.format == "json":
        print(format_json(matches, headers))
    elif args.format == "csv":
        print(format_csv(matches, headers))
    else:
        print(format_table(matches, headers))


if __name__ == "__main__":
    main()
