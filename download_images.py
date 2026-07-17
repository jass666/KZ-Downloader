#!/usr/bin/env python3
"""
download_images.py — bulk-download images from a pipe-delimited source list.

Reads a text file in this format (one entry per line):

    target_filename | source_image_url | source_page | status/notes

Comment / section-header lines start with "#" and are ignored for parsing,
except that "## SECTION NAME (page.html)" headers are used to group output
into subfolders (e.g. images/trucks/, images/buses/).

Only lines whose status contains "CONFIRMED" are downloaded by default.
Everything else (NEEDS CONFIRMATION, NOT ON CURRENT SITE, LIKELY MATCH, TBD,
blank URLs, etc.) is skipped and written out to a report so you know exactly
what still needs manual sourcing.

Usage:
    python download_images.py swift-trucks-image-sources.txt
    python download_images.py sources.txt --outdir images --report report.md
    python download_images.py sources.txt --include-likely   # also fetch "LIKELY MATCH" rows
    python download_images.py sources.txt --dry-run           # parse + report only, no downloads

Requires: requests  (pip install requests)
"""

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    sys.stderr.write("This script needs the 'requests' package.\n  pip install requests\n")
    sys.exit(1)

PLACEHOLDER_URL_RE = re.compile(r'^\(|^tbd$|^n/a$|^-+$', re.IGNORECASE)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def slugify_section(raw_title, raw_page):
    """Turn a '## TRUCKS & HCV (trucks.html)' header into a folder slug like 'trucks'."""
    if raw_page:
        stem = Path(raw_page.strip()).stem  # trucks.html -> trucks
        if stem:
            return re.sub(r'[^a-z0-9_-]+', '-', stem.lower()).strip('-') or 'misc'
    slug = re.sub(r'[^a-z0-9]+', '-', raw_title.lower()).strip('-')
    return slug or 'misc'


def parse_source_file(path):
    """
    Returns a list of dicts:
      {filename, url, page, status, section, line_no, raw_line}
    """
    entries = []
    current_section = 'misc'

    with open(path, 'r', encoding='utf-8') as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip('\n')
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith('#'):
                if stripped.startswith('##'):
                    header_body = stripped.lstrip('#').strip()
                    page_match = re.search(r'\(([^)]+\.html?)\)', header_body)
                    title_only = re.sub(r'\([^)]*\)', '', header_body).strip()
                    current_section = slugify_section(title_only, page_match.group(1) if page_match else None)
                continue  # all '#' lines (single or double) are comments, not data

            if '|' not in stripped:
                # Not a recognized data line; skip silently (keeps parser tolerant of stray text)
                continue

            parts = [p.strip() for p in stripped.split('|')]
            # Pad to at least 4 fields
            while len(parts) < 4:
                parts.append('')
            filename, url, page, status = parts[0], parts[1], parts[2], ' | '.join(parts[3:])

            entries.append({
                'filename': filename,
                'url': url,
                'page': page,
                'status': status,
                'section': current_section,
                'line_no': line_no,
                'raw_line': stripped,
            })

    return entries


def classify(entry, include_likely):
    """Return one of: 'download', 'skip_placeholder', 'skip_needs_confirmation',
    'skip_not_on_site', 'skip_likely_match'."""
    url = entry['url']
    status = entry['status'].upper()

    if not url or PLACEHOLDER_URL_RE.match(url) or not re.match(r'^https?://', url, re.IGNORECASE):
        return 'skip_placeholder'

    if 'NOT ON CURRENT SITE' in status or 'NOT FOUND' in status:
        return 'skip_not_on_site'

    if 'NEEDS CONFIRMATION' in status:
        return 'skip_needs_confirmation'

    if 'LIKELY MATCH' in status:
        return 'download' if include_likely else 'skip_likely_match'

    if 'CONFIRMED' in status:
        return 'download'

    # Unlabeled status but has a real-looking URL — treat conservatively as needing confirmation
    return 'skip_needs_confirmation'


def download_one(entry, outdir, timeout, retries):
    dest_dir = outdir / entry['section']
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / entry['filename']

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(
                entry['url'],
                headers={'User-Agent': USER_AGENT},
                timeout=timeout,
                stream=True,
            )
            resp.raise_for_status()
            ctype = resp.headers.get('Content-Type', '')
            if 'image' not in ctype and not re.search(r'\.(webp|jpe?g|png|gif|svg|avif)$', urlparse(entry['url']).path, re.IGNORECASE):
                last_err = f"unexpected content-type '{ctype}'"
                # still write it — some CDNs mislabel content-type — but flag it in the report
            with open(dest_path, 'wb') as out_f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        out_f.write(chunk)
            size_kb = dest_path.stat().st_size / 1024
            return True, dest_path, size_kb, last_err
        except Exception as e:  # noqa: BLE001 - report every failure mode to the user
            last_err = str(e)
            if attempt < retries:
                time.sleep(1.5 * attempt)
    return False, dest_path, 0, last_err


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source_file', help='Path to the pipe-delimited image-sources.txt file')
    ap.add_argument('--outdir', default='images', help='Output folder (default: ./images)')
    ap.add_argument('--report', default='download-report.md', help='Report filename (default: download-report.md)')
    ap.add_argument('--include-likely', action='store_true', help='Also download rows marked "LIKELY MATCH"')
    ap.add_argument('--dry-run', action='store_true', help='Parse and classify only — no downloads, no files written')
    ap.add_argument('--timeout', type=float, default=20.0, help='Per-request timeout in seconds (default: 20)')
    ap.add_argument('--retries', type=int, default=3, help='Retries per download (default: 3)')
    args = ap.parse_args()

    src_path = Path(args.source_file)
    if not src_path.exists():
        sys.stderr.write(f"File not found: {src_path}\n")
        sys.exit(1)

    outdir = Path(args.outdir)
    entries = parse_source_file(src_path)

    if not entries:
        sys.stderr.write("No pipe-delimited entries found in the source file.\n")
        sys.exit(1)

    buckets = {
        'download': [],
        'skip_placeholder': [],
        'skip_needs_confirmation': [],
        'skip_not_on_site': [],
        'skip_likely_match': [],
    }
    for e in entries:
        buckets[classify(e, args.include_likely)].append(e)

    print(f"Parsed {len(entries)} entries from {src_path.name}")
    print(f"  → {len(buckets['download'])} to download")
    print(f"  → {len(buckets['skip_needs_confirmation'])} need confirmation (skipped)")
    print(f"  → {len(buckets['skip_not_on_site'])} not found on current site (skipped)")
    print(f"  → {len(buckets['skip_likely_match'])} likely match, not yet confirmed (skipped)")
    print(f"  → {len(buckets['skip_placeholder'])} not yet sourced / placeholder (skipped)")

    results = []  # (entry, ok, dest_path, size_kb, note)
    if not args.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)
        total = len(buckets['download'])
        for i, entry in enumerate(buckets['download'], start=1):
            print(f"[{i}/{total}] {entry['section']}/{entry['filename']} ...", end=' ', flush=True)
            ok, dest_path, size_kb, note = download_one(entry, outdir, args.timeout, args.retries)
            if ok:
                print(f"OK ({size_kb:.1f} KB){' — ' + note if note else ''}")
            else:
                print(f"FAILED — {note}")
            results.append((entry, ok, dest_path, size_kb, note))
    else:
        print("\n(--dry-run: no files downloaded)")
        results = [(e, None, None, None, None) for e in buckets['download']]

    # ── Write report ──────────────────────────────────────────
    report_path = Path(args.report)
    lines = [f"# Image download report — {src_path.name}", ""]
    lines.append(f"Source file: `{src_path}`  ")
    lines.append(f"Output folder: `{outdir}`  ")
    lines.append(f"Mode: {'dry-run (no files written)' if args.dry_run else 'live download'}")
    lines.append("")

    if not args.dry_run:
        ok_count = sum(1 for _, ok, *_ in results if ok)
        fail_count = sum(1 for _, ok, *_ in results if ok is False)
        lines.append(f"## Downloaded ({ok_count}/{len(results)} succeeded)")
        lines.append("")
        for entry, ok, dest_path, size_kb, note in results:
            status_icon = "✅" if ok else "❌"
            detail = f"{size_kb:.1f} KB" if ok else f"FAILED — {note}"
            lines.append(f"- {status_icon} `{entry['section']}/{entry['filename']}` ← {entry['url']}  ({detail})")
        lines.append("")

    def section(title, bucket):
        lines.append(f"## {title} ({len(bucket)})")
        lines.append("")
        if not bucket:
            lines.append("_None._")
        for e in bucket:
            lines.append(f"- `{e['filename']}` — {e['status'] or '(no status)'}  (line {e['line_no']})")
        lines.append("")

    section("Needs manual confirmation", buckets['skip_needs_confirmation'])
    section("Not found on current site", buckets['skip_not_on_site'])
    section("Likely match, not yet confirmed", buckets['skip_likely_match'])
    section("Not yet sourced (TBD / placeholder)", buckets['skip_placeholder'])

    report_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\nReport written to {report_path}")


if __name__ == '__main__':
    main()
