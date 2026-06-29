#!/usr/bin/env python3
"""
KZ Downloader — Playwright Media Scanner  v1.0
================================================
Scans any social page (LinkedIn, Instagram, Facebook, YouTube, etc.)
using a real browser session with your login cookies. Outputs a JSON
file that KZ Downloader can import directly via the Scanner tab.

Usage:
  python kz_scanner.py <URL> [options]

Options:
  --scrolls N       Number of scroll steps (default: 60)
  --delay N         Seconds between scrolls (default: 2.5)
  --out FILE        Output JSON path (default: kz_scan_results.json)
  --profile DIR     Browser profile dir to persist login (default: kz_browser_profile)
  --platform PLAT   Force platform label: yt/ig/fb/li/tw/gen (auto-detected if omitted)
  --headless        Run without opening a browser window (login won't work headless)
  --serve           After scan, start local HTTP server so KZ Downloader can import live
  --port N          Port for --serve mode (default: 7474)

Requirements:
  pip install playwright
  playwright install chromium

Examples:
  # LinkedIn company video posts (with scroll)
  python kz_scanner.py "https://www.linkedin.com/company/tata-motors/posts/?feedView=videos"

  # Instagram profile
  python kz_scanner.py "https://www.instagram.com/tatamotors/" --scrolls 40

  # Facebook page videos
  python kz_scanner.py "https://www.facebook.com/TataMotors/videos" --scrolls 50

  # With local HTTP bridge for live import into KZ Downloader
  python kz_scanner.py "https://www.linkedin.com/company/..." --serve
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen

# ─── PLATFORM DETECTION ──────────────────────────────────────────────────────

PLATFORM_RULES = [
    (re.compile(r'youtube\.com|youtu\.be'),        'yt',  'YouTube'),
    (re.compile(r'instagram\.com'),                'ig',  'Instagram'),
    (re.compile(r'facebook\.com|fb\.watch'),       'fb',  'Facebook'),
    (re.compile(r'linkedin\.com'),                 'li',  'LinkedIn'),
    (re.compile(r'twitter\.com|x\.com'),           'tw',  'Twitter/X'),
    (re.compile(r'tiktok\.com'),                   'gen', 'TikTok'),
    (re.compile(r'vimeo\.com'),                    'gen', 'Vimeo'),
    (re.compile(r'twitch\.tv'),                    'gen', 'Twitch'),
]

def detect_platform(url: str):
    for rx, dot, label in PLATFORM_RULES:
        if rx.search(url):
            return dot, label
    return 'gen', 'Generic'


def resolve_cdp_endpoint(cdp_url: str) -> str:
    """Return Chrome's WebSocket debugger URL when an HTTP CDP endpoint is supplied."""
    parsed = urlparse(cdp_url)
    if parsed.scheme in ('ws', 'wss'):
        return cdp_url

    base = cdp_url.rstrip('/')
    version_url = f'{base}/json/version'
    try:
        with urlopen(version_url, timeout=5) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        raise RuntimeError(f'CDP endpoint is not responding at {version_url}: {e}') from e

    ws_url = payload.get('webSocketDebuggerUrl')
    if not ws_url:
        raise RuntimeError(f'CDP endpoint responded, but did not include webSocketDebuggerUrl at {version_url}')

    browser_name = payload.get('Browser')
    if browser_name:
        print(f"  -> CDP browser endpoint: {browser_name}")
    return ws_url


def cdp_http_base(cdp_url: str) -> str:
    parsed = urlparse(cdp_url)
    if parsed.scheme in ('ws', 'wss'):
        scheme = 'https' if parsed.scheme == 'wss' else 'http'
        return f'{scheme}://{parsed.netloc}'
    return cdp_url.rstrip('/')


MEDIA_EXTS = re.compile(
    r'\.(mp4|webm|m4v|mov|avi|mkv|mp3|m4a|ogg|flac|wav)(\?[^"\']*)?$', re.I
)

# ─── EXTRACTOR STRATEGIES PER PLATFORM ───────────────────────────────────────

def extract_linkedin(page, url: str) -> list[dict]:
    """
    LinkedIn /posts/?feedView=videos  — scroll and collect feed/update URLs.
    LinkedIn never puts raw video src in the DOM; the actual stream URL is
    behind a DRM-like delivery API. yt-dlp handles that with --cookies-from-browser.
    So we collect the post page URLs (feed/update/urn:...) which yt-dlp can download.
    """
    found = {}  # url -> item dict

    def push_linkedin(raw: str, source: str):
        if not raw:
            return
        raw = raw.strip()
        if raw.startswith('/'):
            raw = 'https://www.linkedin.com' + raw
        raw = raw.replace('%3A', ':')

        activity = re.search(r'urn:li:activity:\d+', raw)
        if activity:
            clean = f'https://www.linkedin.com/feed/update/{activity.group(0)}/'
        else:
            m = re.search(r'(https://(?:www\.)?linkedin\.com/(?:feed/update/[^/?#]+|posts/[^/?#]+))', raw)
            if not m:
                return
            clean = m.group(1).replace('https://linkedin.com/', 'https://www.linkedin.com/')

        if clean not in found:
            found[clean] = {
                'type': 'PLATFORM',
                'url': clean,
                'dot': 'li',
                'platform': 'LinkedIn',
                'source': source,
            }

    def harvest():
        selectors = [
            "a[href*='/feed/update/']",
            "a[href*='/posts/']",
            "a[href*='urn:li:activity']",
            "[data-urn*='urn:li:activity']",
            "[data-id*='urn:li:activity']",
            "[id*='urn:li:activity']",
        ]
        for sel in selectors:
            try:
                for el in page.locator(sel).all():
                    for attr in ('href', 'data-urn', 'data-id', 'id'):
                        push_linkedin(el.get_attribute(attr) or '', f'linkedin_{attr}')
            except Exception:
                pass

        try:
            html = page.content()
            for match in re.finditer(r'urn:li:activity:\d+', html):
                push_linkedin(match.group(0), 'linkedin_html_activity')
                if len(found) > 500:
                    break
        except Exception:
            pass

    return harvest, found


def extract_instagram(page, url: str) -> tuple:
    """Instagram profile — collect post/reel URLs from the grid."""
    found = {}

    def harvest():
        links = page.locator("a[href*='/p/'], a[href*='/reel/'], a[href*='/tv/']").all()
        for link in links:
            href = link.get_attribute('href')
            if not href:
                continue
            # Make absolute
            if href.startswith('/'):
                href = 'https://www.instagram.com' + href
            href = href.split('?')[0]
            if href not in found:
                found[href] = {
                    'type': 'PLATFORM',
                    'url': href,
                    'dot': 'ig',
                    'platform': 'Instagram',
                    'source': 'instagram_grid_scroll',
                }
    return harvest, found


def extract_facebook(page, url: str) -> tuple:
    """Facebook page videos — collect /videos/ and /watch/ links."""
    found = {}

    def harvest():
        selectors = [
            "a[href*='/videos/']",
            "a[href*='/watch/']",
            "a[href*='/reel/']",
        ]
        for sel in selectors:
            links = page.locator(sel).all()
            for link in links:
                href = link.get_attribute('href')
                if not href:
                    continue
                if href.startswith('/'):
                    href = 'https://www.facebook.com' + href
                href = href.split('?')[0]
                if '/groups/' in href:  # skip group content
                    continue
                if href not in found:
                    found[href] = {
                        'type': 'PLATFORM',
                        'url': href,
                        'dot': 'fb',
                        'platform': 'Facebook',
                        'source': 'facebook_page_scroll',
                    }
    return harvest, found


def extract_generic(page, base_url: str) -> tuple:
    """
    Generic extractor for unknown pages:
    - <video src> and <source src>
    - og:video, og:video:url meta
    - a[href] pointing to media files
    - raw <script> tag regex for .mp4/.webm URLs
    """
    found = {}
    parsed_base = urlparse(base_url)
    dot, label = detect_platform(base_url)

    def abs_url(u: str) -> str:
        if not u:
            return ''
        try:
            return urljoin(base_url, u)
        except Exception:
            return u

    def push(item_type: str, raw_url: str, source: str = 'generic'):
        if not raw_url or len(raw_url) > 2000:
            return
        raw_url = raw_url.strip()
        if raw_url.startswith('{{') or raw_url.startswith('<%'):
            return
        full = abs_url(raw_url)
        if not full or full in found:
            return
        d, lbl = detect_platform(full)
        found[full] = {
            'type': item_type,
            'url': full,
            'dot': d,
            'platform': lbl,
            'source': source,
        }

    def harvest():
        # Video / audio elements
        for el in page.locator('video[src]').all():
            push('VIDEO', el.get_attribute('src') or '', 'video_element')
        for el in page.locator('audio[src]').all():
            push('AUDIO', el.get_attribute('src') or '', 'audio_element')
        for el in page.locator('video source[src], audio source[src]').all():
            push('VIDEO', el.get_attribute('src') or '', 'source_element')

        # OG meta
        for el in page.locator('meta[property="og:video"], meta[property="og:video:url"]').all():
            push('VIDEO', el.get_attribute('content') or '', 'og_meta')
        for el in page.locator('meta[property="og:video:secure_url"]').all():
            push('VIDEO', el.get_attribute('content') or '', 'og_meta')

        # Links to media files
        for el in page.locator('a[href]').all():
            href = el.get_attribute('href') or ''
            if MEDIA_EXTS.search(href):
                push('FILE', href, 'anchor_href')

        # Iframe embeds
        for el in page.locator('iframe[src]').all():
            src = el.get_attribute('src') or ''
            if detect_platform(src)[0] != 'gen' or re.search(r'embed|player|video', src, re.I):
                push('PLATFORM', src, 'iframe_embed')

        # Raw JS grep via page content
        try:
            html_content = page.content()
            url_re = re.compile(
                r'["\`\'](https?://[^"\`\'<>\s]{5,500}\.(?:mp4|webm|m4v|mov|avi|mkv|mp3|m4a|ogg|flac|wav)(?:\?[^"\`\'<>\s]*)?)',
                re.I
            )
            for m in url_re.finditer(html_content):
                push('VIDEO', m.group(1), 'js_grep')
                if len(found) > 200:
                    break
        except Exception:
            pass

    return harvest, found


# ─── PLATFORM → EXTRACTOR MAP ─────────────────────────────────────────────────

EXTRACTORS = {
    'li': extract_linkedin,
    'ig': extract_instagram,
    'fb': extract_facebook,
}


# ─── SCROLL LOOP ─────────────────────────────────────────────────────────────

def scroll_and_collect(page, harvest_fn, found: dict, scrolls: int, delay: float, label: str):
    scroll_px = 900 if label.lower().startswith('linkedin') else 2500
    for i in range(scrolls):
        harvest_fn()
        count = len(found)
        print(f"  Scroll {i+1:>3}/{scrolls}  |  {label} found: {count}", end='\r', flush=True)
        page.mouse.wheel(0, scroll_px)
        time.sleep(delay)
        harvest_fn()
        # Check for "no more content" signals
        if i > 5:
            try:
                # LinkedIn end-of-feed indicator
                end_indicators = [
                    page.locator("div.scaffold-finite-scroll__load-button").count(),
                    page.locator("[data-finite-scroll-hotkey-item]").count(),
                ]
            except Exception:
                pass
    # Final harvest after last scroll
    harvest_fn()
    print()  # newline after \r progress


# ─── MAIN SCANNER ─────────────────────────────────────────────────────────────

def run_scan(
    url: str,
    scrolls: int = 60,
    delay: float = 2.5,
    out_file: str = 'kz_scan_results.json',
    profile_dir: str = 'kz_browser_profile',
    force_platform: str | None = None,
    headless: bool = False,
    cdp_url: str | None = None,
) -> list[dict]:
    from playwright.sync_api import sync_playwright

    dot, label = (force_platform, force_platform) if force_platform else detect_platform(url)

    print(f"\n{'─'*60}")
    print(f"  KZ Scanner — {label} ({dot})")
    print(f"  URL     : {url}")
    print(f"  Scrolls : {scrolls}  |  Delay: {delay}s")
    if cdp_url:
        print(f"  Mode    : Reuse existing Chrome via CDP ({cdp_url})")
    else:
        print(f"  Profile : {profile_dir}/")
    print(f"  Output  : {out_file}")
    print(f"{'─'*60}\n")

    with sync_playwright() as p:

        if cdp_url:
            # ── CDP MODE: connect to already-running Chrome ──────────────
            print(f"  -> Checking Chrome CDP endpoint {cdp_url} ...")
            try:
                cdp_endpoint = resolve_cdp_endpoint(cdp_url)
                print(f"  -> Connecting to existing Chrome ...")
                endpoints = []
                for endpoint in (cdp_endpoint, cdp_url, cdp_http_base(cdp_url)):
                    if endpoint and endpoint not in endpoints:
                        endpoints.append(endpoint)
                last_error = None
                for endpoint in endpoints:
                    try:
                        browser = p.chromium.connect_over_cdp(endpoint)
                        break
                    except Exception as e:
                        last_error = e
                else:
                    raise last_error
            except Exception as e:
                print(f"\n  [!] Could not connect to Chrome: {e}")
                print( "  Make sure Chrome is running with --remote-debugging-port=9222")
                print( "  and a separate --user-data-dir for debugging.")
                print( "  The launcher should have done this automatically.")
                print( "  Try closing and reopening Chrome via the launcher.\n")
                sys.exit(1)

            # Reuse the first existing context (keeps all your logins/cookies)
            if browser.contexts:
                context = browser.contexts[0]
            else:
                context = browser.new_context()

            # Open a NEW tab inside the existing Chrome window
            page = context.new_page()
            print(f"  -> Opened new tab in your existing Chrome window")
            print(f"  -> Navigating to URL...")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=60_000)
            except Exception as e:
                print(f"  [!] Page load error: {e}")
                print("  Continuing anyway...")

            input(
                "\n  Navigate to the exact page you want to scan\n"
                "  (log in if needed), then press ENTER here to begin...\n> "
            )
            time.sleep(2)

            extractor_fn = EXTRACTORS.get(dot, extract_generic)
            harvest_fn, found = extractor_fn(page, url)

            print(f"\n  Starting scroll scan ({scrolls} scrolls)...")
            scroll_and_collect(page, harvest_fn, found, scrolls, delay, label)

            # Close only the tab we opened, not the whole browser
            page.close()

        else:
            # ── NORMAL MODE: launch a fresh Playwright-managed browser ───
            launch_kwargs = {
                'user_data_dir': profile_dir,
                'headless': headless,
                'viewport': {'width': 1366, 'height': 900},
                'args': ['--disable-blink-features=AutomationControlled'],
            }
            try:
                browser = p.chromium.launch_persistent_context(channel='chrome', **launch_kwargs)
            except Exception:
                browser = p.chromium.launch_persistent_context(**launch_kwargs)

            pages = browser.pages
            page = pages[0] if pages else browser.new_page()

            print(f"  -> Opening page...")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=15_000)
            except Exception as e:
                print(f"  [!] Page load error: {e}")
                print("  Continuing anyway...")

            if not headless:
                input(
                    "\n  Log in if needed, navigate to the target page,\n"
                    "  then press ENTER here to begin scanning...\n> "
                )

            time.sleep(2)

            extractor_fn = EXTRACTORS.get(dot, extract_generic)
            harvest_fn, found = extractor_fn(page, url)

            print(f"\n  Starting scroll scan ({scrolls} scrolls)...")
            scroll_and_collect(page, harvest_fn, found, scrolls, delay, label)

            browser.close()

    items = list(found.values())
    print(f"\n  ✓ Scan complete — {len(items)} items found")

    # Write output JSON
    output = {
        'scanner': 'KZ Downloader Playwright Scanner v1.0',
        'source_url': url,
        'platform': label,
        'dot': dot,
        'scrolls_done': scrolls,
        'item_count': len(items),
        'items': items,
    }
    Path(out_file).write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"  ✓ Saved → {out_file}")

    return items


# ─── OPTIONAL LOCAL HTTP BRIDGE ───────────────────────────────────────────────

def serve_results(json_file: str, port: int = 7474):
    """
    Serves the JSON results file over HTTP with CORS headers so KZ Downloader
    (even when opened as a local file:// URL) can fetch it.
    Access: http://localhost:{port}/results
    """
    import http.server
    import threading

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ('/results', '/results.json', '/'):
                try:
                    data = Path(json_file).read_bytes()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(data)
                except FileNotFoundError:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'{"error":"results file not found"}')
            elif self.path == '/ping':
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'pong')
            else:
                self.send_response(404)
                self.end_headers()

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()

        def log_message(self, *args):
            pass  # suppress request logging

    server = http.server.HTTPServer(('localhost', port), Handler)
    print(f"\n  ✓ Local bridge started — http://localhost:{port}/results")
    print(f"    In KZ Downloader → Scanner tab → click 'Import from local scanner'")
    print(f"    Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Bridge stopped.")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='KZ Downloader — Playwright Media Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('url', help='Page URL to scan')
    parser.add_argument('--scrolls',   type=int,   default=60,                    help='Scroll steps (default: 60)')
    parser.add_argument('--delay',     type=float, default=2.5,                   help='Seconds between scrolls (default: 2.5)')
    parser.add_argument('--out',       type=str,   default='kz_scan_results.json',help='Output JSON file')
    parser.add_argument('--profile',   type=str,   default='kz_browser_profile',  help='Browser profile directory')
    parser.add_argument('--platform',  type=str,   default=None,                  help='Force platform: yt/ig/fb/li/tw/gen')
    parser.add_argument('--headless',  action='store_true',                        help='Headless mode (no browser window)')
    parser.add_argument('--serve',     action='store_true',                        help='Start local HTTP bridge after scan')
    parser.add_argument('--port',      type=int,   default=7474,                  help='HTTP bridge port (default: 7474)')
    parser.add_argument('--cdp',       type=str,   default=None,  metavar='URL',  help='Connect to existing Chrome via CDP (e.g. http://127.0.0.1:9222)')
    args = parser.parse_args()

    try:
        run_scan(
            url=args.url,
            scrolls=args.scrolls,
            delay=args.delay,
            out_file=args.out,
            profile_dir=args.profile,
            force_platform=args.platform,
            headless=args.headless,
            cdp_url=args.cdp,
        )
    except KeyboardInterrupt:
        print('\n\n  Scan interrupted by user.')
        sys.exit(0)
    except ImportError:
        print('\n  ✗ Playwright not installed. Run:')
        print('      pip install playwright')
        print('      playwright install chromium')
        sys.exit(1)

    if args.serve:
        serve_results(args.out, args.port)


if __name__ == '__main__':
    main()
