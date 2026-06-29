# Changelog

All notable changes to **KZ Downloader** are documented here.

Project created and maintained by **Jaswant Kanojia**.

**Date:** 29-06-2026

---

## v3.0 — Fix: Media Scanner Deep Extraction + UI Polish
**Date:** 29-06-2026

### Fixed

**Scanner returned single stale PLATFORM result** — the root cause of the scanner being non-functional. `scanMedia()` had an early-exit block: if the pasted URL matched any entry in `SCAN_PLATFORMS`, the function immediately rendered one fake `{type:'PLATFORM'}` result and returned without fetching anything. For any YouTube, Instagram, Facebook, Twitter/X, LinkedIn, Vimeo, TikTok, Twitch, SoundCloud, or Dailymotion URL, the actual page was never scanned. The short-circuit is removed entirely. All URLs now go through the full proxy fetch and extraction pipeline.

**`extractMediaItems()` was blind to modern pages** — the extractor only checked `<video src>`, `<audio src>`, `<source src>`, `<a href>` with media extensions, and `og:video` / `og:audio` meta tags. Modern sites deliver media URLs inside JS strings, inline JSON, JSON-LD blocks, lazy-load attributes, and iframe embeds — none of which were covered. The function signature changed from `(doc, baseUrl)` to `(doc, rawHtml, baseUrl)` to enable raw-string grepping alongside DOM parsing.

Extraction now covers seven source layers:

| Layer | What it catches |
|---|---|
| 1 · Semantic HTML5 | `<video src>`, `<audio src>`, `<source src>` |
| 2 · Lazy-load attributes | `data-src`, `data-video`, `data-url`, `data-media`, `data-mp4`, `data-stream` with media extensions |
| 3 · Anchor links | `<a href>` ending in `.mp4 .webm .m4v .mov .avi .mkv .mp3 .m4a .ogg .flac .wav` |
| 4 · OpenGraph / Twitter Card meta | `og:video`, `og:video:url`, `og:video:secure_url`, `og:audio`, `twitter:player:stream`; `og:url` only if it matches a known platform |
| 5 · JSON-LD structured data | Walks `application/ld+json` blocks; extracts `contentUrl`, `embedUrl`, `url`, `thumbnailUrl` where value matches a media extension or known platform |
| 6 · Raw HTML grep | Regex over the full proxy response string; finds quoted `.mp4/.webm/etc.` URLs in JS blobs and platform-specific video URLs embedded in script text |
| 7 · iframe embed players | `<iframe src>` where src matches a known platform or contains `embed` / `player` / `video` |

**PLATFORM type promotion centralised** — previously scattered across caller sites with inconsistent logic. Now handled inside `push()` in `extractMediaItems()`: any resolved URL that matches `SCAN_PLATFORMS` is unconditionally promoted to `PLATFORM` type regardless of which extraction layer found it.

**Single proxy, no fallback** — if `allorigins.win` failed, the scanner showed an error with no retry. A second proxy (`corsproxy.io`) is now tried automatically on any non-timeout failure. If both proxies fail and the URL is a known platform, the URL itself is surfaced as a PLATFORM entry so the user can still add it to the queue.

**Fetch timeout too short** — `AbortController` timeout raised from 10 s to 15 s to accommodate slow proxy responses.

**Safety cap on raw HTML grepping** — regex loops over the full HTML string break early at 200 accumulated items to prevent blocking the main thread on very large pages.

### Changed

**Result cap raised from 20 → 30** — `.slice(0, 20)` updated to `.slice(0, 30)`; truncation notice threshold updated to match.

**Scanner and Settings tabs swapped positions** — Scanner moved to position 4 (before Settings) so the two utility tabs appear in logical usage order: Scanner to discover content → Settings to configure output.

| Position | Before | After |
|---|---|---|
| 4th | ⚙️ Settings | 🔍 Scanner |
| 5th | 🔍 Scanner | ⚙️ Settings |

### Added

**"Settings" tab label** — Options tab renamed to Settings in the nav.

**Clear queue button in profile queue card header** — a compact 🗑 Clear button added to the top-right of the Profile queue card (alongside the ✓ SAVED indicator), giving one-tap access to `clearAll()` without scrolling to the action row below the terminal output.

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | `scanMedia()` early-exit removed; dual-proxy fallback with timeout bump; `extractMediaItems()` signature updated, 7-layer extraction added; `push()` centralises PLATFORM promotion; result cap raised to 30; Options nav tab renamed to Settings; Scanner and Settings nav tabs swapped positions; Clear button added in queue card header |
| `CHANGELOG.md` | This entry |

---

## v2.9 — Fix: Media Scanner Correctness & Robustness
**Date:** 29-06-2026

### Fixed

**`platLabel` coupling removed** — `renderScanResults()` referenced the global `platLabel` map defined 400+ lines away in the presets/history section. If that map were ever renamed or restructured the scanner would throw a silent `ReferenceError` and no platform badge would render. A local `SCAN_PLAT_LABEL` constant is now defined inside the scanner block, making it fully self-contained.

**`detectPlatform()` delegation replaced** — `extractMediaItems()` was calling `detectPlatform(url)` to resolve a platform dot string, coupling the scanner to whatever format that function returns. Replaced with a dedicated `scanDot(url)` helper that reads directly from `SCAN_PLATFORMS` and always returns a guaranteed dot string (`'yt'` / `'ig'` / etc. / `'gen'`).

**`og:video` / `og:audio` meta tags misclassified** — content URLs from `og:video` and `og:audio` were unconditionally pushed as type `PLATFORM`. In practice these are CDN stream URLs (e.g. `video.cdninstagram.com`, `fbcdn.net`) that yt-dlp cannot use as platform inputs. Fix: URL is now checked against `SCAN_PLATFORMS` first; only if it matches a known platform does it become `PLATFORM` — otherwise it is classified as `VIDEO` or `AUDIO` respectively.

**Redundant platform badge on PLATFORM-type rows** — when `item.type === 'PLATFORM'` the type badge already renders with the platform's colour (e.g. `.plat-yt`), and a second platform name badge was also shown alongside it, duplicating the information. The secondary platform badge is now suppressed when `item.type === 'PLATFORM'`; it only appears for `VIDEO` / `AUDIO` / `FILE` rows where a known platform is detected.

**No fetch timeout** — the proxy fetch to `allorigins.win` had no timeout. Slow or dead targets left the spinner running indefinitely. An `AbortController` with a 10-second limit is now applied; `clearTimeout` runs in `.finally()` to prevent timer leaks regardless of outcome.

**No Enter key handler on `#scanner-input`** — the scanner input had no keyboard shortcut. Pressing Enter did nothing. `onkeydown="if(event.key==='Enter')scanMedia()"` added.

**Fragile `switchTab` selector in `addScannedItems()`** — the call used `document.querySelector('.nav-tab')` which grabs whichever `.nav-tab` element appears first in the DOM — coincidentally the Profiles tab today, but silently wrong if tab order ever changes. Changed to `document.querySelector('.nav-tab[onclick*="profiles"]')` which targets the correct tab by intent rather than position.

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | `SCAN_PLAT_LABEL` constant added; `scanDot()` helper added; `extractMediaItems()` updated (`detectPlatform` → `scanDot`, `og:video`/`og:audio` type logic corrected); `renderScanResults()` updated (platform badge condition fixed, `SCAN_PLAT_LABEL` used); `scanMedia()` updated (`AbortController` timeout added); `#scanner-input` gets `onkeydown` handler; `addScannedItems()` selector hardened |
| `CHANGELOG.md` | This entry |

---

## v2.8 — Feature: 🔍 Media Scanner Tab
**Date:** 29-06-2026

### Added

**🔍 Scanner nav tab** — a new tab inserted between History and Setup Guide. Lets the user paste any URL and extract downloadable media items from it, then add them directly to the Profiles queue.

**`scanMedia()`** — entry point called by the Scan button and the Enter key on the scanner input.

| Step | Detail |
|---|---|
| Known platform URL | If the pasted URL matches any entry in `SCAN_PLATFORMS` (YouTube, Instagram, Facebook, Twitter/X, LinkedIn, Vimeo, TikTok, Twitch, SoundCloud, Dailymotion), the proxy fetch is skipped entirely. The URL is treated as one `PLATFORM` result and rendered immediately |
| Unknown URL | Page HTML is fetched via the public CORS proxy `https://api.allorigins.win/get?url=ENCODED_URL`. The `contents` field is parsed as HTML by `DOMParser` |
| Spinner | Shown during proxy fetch; replaced by results or error notice on completion |
| Failure | Inline `.notice-warn` displayed: *"Could not scan this page directly. Paste the URL into the Profiles tab and use List mode to preview via yt-dlp instead."* |

**`extractMediaItems(doc, baseUrl)`** — extracts up to (but not capped at) N items from the parsed HTML across five source types:

| Source | Type assigned |
|---|---|
| `<video src>` | `VIDEO` |
| `<audio src>` | `AUDIO` |
| `<source src>` inside `<video>` / `<audio>` | `VIDEO` / `AUDIO` (inherits parent) |
| `<a href>` ending in `.mp4 .webm .m4v .mov .avi .mkv .mp3 .m4a .ogg .flac .wav` | `FILE` |
| `<meta property="og:video">` / `og:audio` / `og:url` content | `PLATFORM` (if URL matches known platform) |

All URLs are resolved against `baseUrl` via `new URL(rawUrl, baseUrl)`. Duplicate resolved URLs are deduplicated with a `Set`.

**`renderScanResults(items, totalFound)`** — renders the (already capped) result set:

| Element | Detail |
|---|---|
| Type badge | `VIDEO` · `AUDIO` · `FILE` · `PLATFORM` · `PLAYLIST` — colour-coded (see Badge colours below) |
| Platform badge | Shown for `VIDEO` / `AUDIO` / `FILE` rows where a known platform is detected; omitted for `PLATFORM` rows (colour already on type badge) and unknown platforms |
| Truncated URL | Full URL in `title` tooltip; display truncated to 60 characters |
| Checkbox | Pre-checked; used by Add selected |
| Truncation notice | If `totalFound > 20`: *"Showing first 20 of N items found. Run a yt-dlp flat-playlist scan for the full list."* |
| Empty state | Reuses `.empty-state` pattern: 🔍 "No media found on this page." |
| Action row | Hidden until results render |

**20-item hard cap** — enforced with `.slice(0, 20)` before `renderScanResults` is called. `totalFound` (pre-cap count) is passed separately for the truncation notice.

**`addScannedItems(addAll)`** — action row buttons:

| Button | Behaviour |
|---|---|
| ☑ Add all | Calls `addToQueue(url)` for every item in `scanResults`; switches to Profiles tab |
| ＋ Add selected | Calls `addToQueue(url)` for checked items only; switches to Profiles tab |

Reuses `addToQueue()` without modification. Scanner state (`scanResults`) is session-only — no new `localStorage` keys.

### Badge colours

| Badge | Style |
|---|---|
| `VIDEO` | `background: var(--accent); color: #000` |
| `AUDIO` | `background: #7c3aed; color: #fff` |
| `FILE` | `background: #555; color: #fff` |
| `PLATFORM` | Reuses `.plat-yt` / `.plat-ig` / `.plat-fb` / `.plat-tw` / `.plat-li` / `.plat-gen` |
| `PLAYLIST` | `background: #b45309; color: #fff` |

### Spinner

`.scan-spinner` — 16×16px CSS border-spin using `var(--accent)` top border and `var(--border-str)` base; `@keyframes spin` at 0.7s linear. Renders inline inside the `.notice-info` scanning state div.

### Constants added

| Constant | Purpose |
|---|---|
| `SCAN_PLATFORMS` | Array of `{ rx, dot }` objects for the 10 supported yt-dlp platforms |
| `SCAN_MEDIA_EXTS` | Regex matching all 11 recognised media file extensions (with optional query string) |

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | Scanner panel HTML (`#panel-scanner`) added; 🔍 Scanner nav tab added; `.scan-type-video`, `.scan-type-audio`, `.scan-type-file`, `.scan-type-playlist` CSS rules added; `.scan-spinner` + `@keyframes spin` added; `SCAN_PLATFORMS`, `SCAN_MEDIA_EXTS`, `scanResults`, `scanMedia()`, `extractMediaItems()`, `renderScanResults()`, `addScannedItems()` added inside clearly delimited `/* ─── MEDIA SCANNER ─── */` block |
| `CHANGELOG.md` | This entry |

---

## v2.7 — Save Location Mode & Nav Reorder
**Date:** 28-06-2026

### Added

**Save location mode toggle** — A two-option segmented control added directly below the `#outdir` field in the Options tab (Format & quality card), matching the visual style of the existing Download mode radio labels (`font-size:12px`, `padding:10px`, `background:var(--surface2)`, `border`, `border-radius:8px`, `accent-color:var(--accent)`).

| Mode | Behaviour |
|---|---|
| Fixed folder (default) | Current behaviour — `#outdir` value is used as-is; `-o "path/template"` appears in the generated command |
| Ask every time | `-o` flag omitted entirely; `--no-mtime` added so yt-dlp downloads to the working directory; `#outdir` input disabled and dimmed (opacity `0.4`, `cursor:not-allowed`); `#outdir-hint` hidden |

**`applySaveMode()`** — reads the checked `[name=savemode]` radio and toggles `#outdir` disabled state, opacity, cursor, and `#outdir-hint` visibility accordingly.

**`updateSaveMode()`** — called via `onchange` on both save-mode radio buttons; runs `applySaveMode()`, `saveOpts()`, then `regenerate()`.

**`saveMode` field in `kz-downloader-opts`** — persisted under the existing opts storage key. Values: `'fixed'` | `'ask'`.

### Changed

**`saveOpts()`** — now writes `saveMode` (value of the checked `[name=savemode]` radio) alongside the existing `outdir`, `format`, `tmpl`, and `dateFilter` fields.

**`loadOpts()`** — restores `saveMode` from storage by checking the matching radio, then calls `applySaveMode()` after all fields are restored so the UI reflects the saved state immediately on load.

**`getOpts()`** — now includes `saveMode` in its returned object, sourced from the checked `[name=savemode]` radio (falls back to `'fixed'` if no radio is found).

**`buildCmd()`** — branches on `saveMode`:
- `'fixed'` → existing behaviour: `-o "dir/template"` included in the command
- `'ask'` → `-o` segment omitted; `--no-mtime` inserted in its place

**`regenerate()` — args file branch** — destructures `saveMode` from `getOpts()`; when `'ask'`, emits `--no-mtime` instead of `-o dir/template` in the args file text.

**`regenerate()` — batch branch** — `rem Output folder: ${dir}` comment replaced with `rem Output folder: (prompted at runtime / working directory)` when `saveMode === 'ask'`.

**`setDevice()`** — calls `applySaveMode()` immediately after updating `#outdir-hint` text, ensuring hint visibility always reflects the active save mode rather than being unconditionally shown on every device switch.

**Nav tab order** — Options and History tabs swapped positions.

| Position | Before | After |
|---|---|---|
| 2nd | ⚙️ Options | 🕓 History |
| 4th | 🕓 History | ⚙️ Options |

### Storage Keys

| Key | Field | Change |
|---|---|---|
| `kz-downloader-opts` | `saveMode` | New field added; `'fixed'` \| `'ask'`; reads as `'fixed'` when absent (radio default) |

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | Save location mode toggle HTML (two radio labels) added below `#outdir` inside the Format & quality card; `saveOpts()`, `loadOpts()`, `getOpts()`, `buildCmd()`, `regenerate()` (batch + args branches), and `setDevice()` updated; `applySaveMode()` and `updateSaveMode()` added; nav tab order swapped (History ↔ Options) |
| `CHANGELOG.md` | This entry |

---

## v2.6 — Refactor: Inline Output, Presets Manager & pip Command Standardisation
**Date:** 28-06-2026

### Added

**⭐ Presets tab** — Quick presets promoted from a static card inside the Profiles tab to a fully managed, dedicated nav tab. All preset data is stored in `localStorage` under `kz-presets`.

| Feature | Detail |
|---|---|
| Add preset | Modal form with Brand, Handle, URL, Platform fields. Platform auto-detects from URL as the user types |
| Edit preset | ✏️ button on each card opens the same modal pre-populated |
| Delete preset | ✕ button per card with confirmation |
| Add to queue | "＋ Add to queue" button per card; switches back to Profiles tab so the user sees it land in the queue |
| Export | Downloads all presets as `kz-presets.json` |
| Import | Accepts a previously exported `.json`; duplicate URLs are skipped; count of added vs skipped reported |
| Clear all | Confirmation-gated wipe of all presets |
| Seed data | On first load (no `kz-presets` key in storage), the 8 built-in Tata presets are written as the initial value |

**`BUILTIN_PRESETS` array** — replaces the old `PRESETS` constant. Tata Motors (YouTube / Instagram / Facebook / LinkedIn), Tata Trucks (YouTube), Tata Commercial Vehicles (Facebook / LinkedIn), Tata SCV (YouTube).

**`loadPresets()` / `savePresetsStore()`** — read and write `kz-presets` in localStorage. Seed with `BUILTIN_PRESETS` on first run.

**`openPresetModal(idx?)` / `closePresetModal()` / `savePresetModal()`** — modal lifecycle functions. `idx` is `null` for new presets, numeric for edits. Modal closes on backdrop click.

**`exportPresets()` / `importPresets(e)`** — JSON export and file-import for presets, consistent with the existing History import/export pattern.

**`deletePreset(i)` / `clearAllPresets()`** — per-entry and bulk delete with confirmation guards.

### Changed

**Output moved inline to Profiles tab** — the generated command block (output mode tabs, terminal chrome, action row, per-device notices, list-mode note) is now the third card inside the Profiles panel, sitting directly below the Profile Queue. The command regenerates automatically whenever a profile is added or removed — no tab switch required.

| Element | Before | After |
|---|---|---|
| Output block location | Separate 💻 Output tab | Inline card in Profiles tab, always visible |
| Command regeneration trigger | Only on switching to Output tab or device change | Every `renderProfiles()` call — i.e. any add, remove, or clear |
| Quick Presets | Static card at the bottom of Profiles tab | Full ⭐ Presets tab with CRUD, export, import |
| Nav tabs | Profiles / Options / **Output** / History / Setup Guide | Profiles / Options / **Presets** / History / Setup Guide |
| `renderProfiles()` | Rendered queue only | Renders queue and calls `regenerate()` |
| `switchTab()` | Called `regenerate()` on `output` | Calls `renderPresets()` on `presets` |
| Empty command placeholder text | "Add profiles in the Profiles tab to generate commands." | "Add profiles above to generate commands." |

**All `yt-dlp` CLI invocations changed to `python -m yt_dlp`** — applies to every executable command across all OS panels in the Setup Guide and to both command-builder functions in JS.

| Location | Before | After |
|---|---|---|
| Windows Step 2 — install | `pip install yt-dlp` | `python -m pip install yt-dlp` |
| Windows Step 2 — update | `pip install -U yt-dlp` | `python -m pip install -U yt-dlp` |
| Windows Step 4 — cookies | `pip install yt-dlp[default]` | `python -m pip install yt-dlp[default]` |
| Windows Step 5 — verify | `yt-dlp --version` | `python -m yt_dlp --version` |
| macOS Step 4 — via pip | `pip3 install yt-dlp` | `python -m pip install yt-dlp` |
| macOS Step 4 — verify | `yt-dlp --version` | `python -m yt_dlp --version` |
| macOS Step 5 — cookies | `pip3 install yt-dlp[default]` | `python -m pip install yt-dlp[default]` |
| Linux Step 2 — install | `pip3 install yt-dlp` | `python -m pip install yt-dlp` |
| Linux Step 3 — verify | `yt-dlp --version && ffmpeg -version` | `python -m yt_dlp --version && ffmpeg -version` |
| Linux output notice | `pip3 install yt-dlp` (inline code) | `python -m pip install yt-dlp` |
| Android Step 3 — install | `pip install yt-dlp` | `python -m pip install yt-dlp` |
| Android Step 3 — verify | `yt-dlp --version` | `python -m yt_dlp --version` |
| Android Step 6 — update | `pip install -U yt-dlp` | `python -m pip install -U yt-dlp` |
| iOS a-Shell panel | `pip install yt-dlp` | `python -m pip install yt-dlp` |
| JS `buildCmd()` — download | `yt-dlp -f … -o … URL` | `python -m yt_dlp -f … -o … URL` |
| JS `buildCmd()` — list mode | `yt-dlp --flat-playlist …` | `python -m yt_dlp --flat-playlist …` |

**Contrast improvements** — text tokens tightened across both themes for better legibility on card and surface backgrounds.

| Token | Dark (before → after) | Light (before → after) |
|---|---|---|
| `--text` | `#e4e5e8` → `#edeef1` | `#111213` → `#0d0e0f` |
| `--text-sec` | `#9a9ba0` → `#b8b9c0` | `#555760` → `#3a3b42` |
| `--text-muted` | `#5a5b60` → `#78797f` | `#9a9ba8` → `#70717a` |
| Nav tab inactive | `#7a7b82` (dark) / `#555760` (light) | `#a0a1a8` (dark) / `#3a3b44` (light) |
| `.card-title` color | `--text-muted` | `--text-sec` |
| `.opt-label` color | `--text-muted` | `--text-sec` |
| `.preset-plat` color | `--text-muted` | `--text-sec` |
| `.preset-handle` | no `font-weight` | `font-weight: 500` added |

**Nav tab scrollbar hidden** — `.nav-tabs` gains `overflow-y: hidden`, `scrollbar-width: none`, and `::-webkit-scrollbar { display: none }` to eliminate the vertical scroll arrows that appeared when the tab bar was taller than its clipping container. Tab padding increased from `9px 18px` to `10px 20px`.

### Removed

- `PRESETS` constant array (superseded by `BUILTIN_PRESETS` inside the presets storage system).
- Standalone `panel-output` panel and its nav tab entry.

### Storage Keys

| Key | Contents |
|---|---|
| `kz-presets` | User-managed preset list (new in v2.6); seeded from `BUILTIN_PRESETS` on first load |

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | Nav tab restructure; Output block moved inline to Profiles panel; Presets panel added with full modal, CRUD, export/import; `BUILTIN_PRESETS`, `loadPresets()`, `savePresetsStore()`, `openPresetModal()`, `closePresetModal()`, `savePresetModal()`, `exportPresets()`, `importPresets()`, `deletePreset()`, `clearAllPresets()`, `renderPresets()` added; `switchTab()` updated; `renderProfiles()` now calls `regenerate()`; all `pip`/`pip3`/`yt-dlp` CLI strings updated to `python -m pip`/`python -m yt_dlp`; contrast tokens tightened; nav scrollbar suppressed |
| `CHANGELOG.md` | This entry |

---

## v2.5 — Feature: Device Selector (Windows / Mac / Linux / Android / iOS)
**Date:** 28-06-2026

### Added

**Global device selector** — a segmented control in the header lets the user pick their operating system. The selection persists in `localStorage` (`kz-device`) and is auto-detected from the browser's user agent on first load.

Supported devices: 🖥 Windows · 🍎 Mac · 🐧 Linux · 🤖 Android · 📱 iOS.

**`DEVICE_CONFIG` object** — central config table that drives all per-device behaviour. Each device entry defines:

| Key | Purpose |
|---|---|
| `terminalLabel` | Label shown in the terminal chrome bar (Command Prompt / Terminal / Termux / Terminal (SSH)) |
| `outdirDefault` | Platform-appropriate default output path |
| `outdirHint` | Hint text below the output folder field explaining path format |
| `showBatch` | Whether the Batch script (.bat) output tab is visible |
| `showLaunchCmd` | Whether the ▶ Launch in CMD button is visible |
| `showShare` | Whether the 📤 Share button is visible |
| `showDownload` | Whether the ⬇ Download file button is visible |
| `setupOS` | Which Setup Guide OS panel auto-activates |
| `bannerClass` | CSS class for the platform banner (`info` / `warn` / empty) |
| `bannerText` | Contextual message shown below the nav tabs |

**Platform banner** — a persistent info/warn strip below the nav tabs. Hidden on Windows (no guidance needed), info on Mac/Linux (paste in terminal), info on Android (use Copy/Share + Termux), warn on iOS (yt-dlp cannot run natively).

**Per-device output notices** — five hidden `<div>` elements in the Output tab, one per device. The active device's notice is shown after the action row, giving contextual instructions without cluttering the UI.

**`setDevice(dev, btnEl)`** — master function that applies all device-specific state in one call: updates selector button active state, platform banner, terminal label, batch tab visibility, action button visibility, output notices, outdir default, outdir hint, Setup Guide OS panel sync, and triggers `regenerate()`.

**`syncSetupOS(osKey)`** — syncs the Setup Guide OS tabs and panels to match the selected device, so switching device on any tab keeps Setup Guide in the correct state.

**`detectDeviceFromUA()`** — UA string check: Android → `android`, iPhone/iPad → `ios`, Mac OS X (non-iOS) → `mac`, Linux (non-Android) → `linux`, default → `windows`.

**iOS Setup Guide panel** (`#os-ios`) — three documented options: SSH via Termius/iSSH, limited a-Shell workaround (audio-only, no FFmpeg), and self-hosted remote server. Includes links to iOS SSH clients on the App Store.

### Changed

| Element | Before | After |
|---|---|---|
| Output mode tabs | Batch tab always visible | Hidden on Mac / Linux / Android / iOS |
| ▶ Launch in CMD | Always visible | Hidden on Mac / Linux / Android / iOS |
| ⬇ Download file | Always visible | Hidden on iOS (no local execution path) |
| Terminal chrome label | "Command Prompt" always | Per-device: Command Prompt / Terminal / Termux / Terminal (SSH) |
| Output folder default | `D:/KZ Downloads` always | Per-device path; only overrides if user hasn't customised |
| Setup Guide OS tabs | Manual selection only | Auto-syncs with device selector |
| Version string | v2.4 | v2.5 |

### Storage Keys

| Key | Contents |
|---|---|
| `kz-device` | Selected device (`windows` / `mac` / `linux` / `android` / `ios`) — new in v2.5 |

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | Device selector HTML + CSS in header; `DEVICE_CONFIG` object; `setDevice()`, `syncSetupOS()`, `detectDeviceFromUA()` functions; per-device output notices; platform banner; iOS Setup Guide panel; `#btn-launch-cmd`, `#btn-share`, `#btn-download` IDs added to action buttons; `#outtab-batch` ID added; `outdir-hint` div added; init reads `kz-device` from localStorage |
| `CHANGELOG.md` | This file |

---

## v2.4 — Feature: Android Compatibility
**Date:** 28-06-2026

### Added

**📤 Share button** — uses the Web Share API (`navigator.share`) to trigger Android's native share sheet. Falls back to clipboard copy on browsers that don't support it. Visible on mobile (≤768px), hidden on desktop.

**Android / Termux Setup Guide panel** (`#os-android`) — full six-step Termux install guide: install from F-Droid, `pkg install python ffmpeg -y`, `pip install yt-dlp`, `termux-setup-storage` for Downloads access, copy-paste workflow, update command.

**iOS Setup Guide panel** (`#os-ios`) — stub added (expanded in v2.5).

**`safeCopy(text, onSuccess)`** — safe clipboard wrapper. Tries `navigator.clipboard.writeText()` first; on failure (file:// protocol, WebView contexts, older browsers) falls back to `execCmdCopy()`.

**`execCmdCopy(text, onSuccess)`** — `document.execCommand('copy')` fallback via off-screen textarea. Works in Android WebViews and any context where the async Clipboard API is unavailable.

**Platform-aware output folder hint** — `#outdir-hint` div below the output folder field; shows Android-specific Termux storage path guidance.

**Android auto-detection** — `isAndroid` / `isIOS` / `isMobile` flags from UA string; on first load (no saved device), auto-selects the closest device config.

### Fixed

| Issue | Fix |
|---|---|
| `navigator.clipboard` fails on `file://` and Android WebViews | `safeCopy()` + `execCmdCopy()` fallback applied to all three copy functions: `copyCmd()`, `copyCode()`, `copyHistItem()` |
| Input auto-zoom on Android/iOS (font-size < 16px triggers browser zoom) | `@media(max-width:768px)` override sets `font-size:16px!important` on all `<input>` and `<select>` elements |
| Touch targets too small (hist-act-btn, code-copy, profile-del: 3px padding) | Minimum padding and `min-height` enforced at ≤768px |
| Action row buttons cramped on narrow screens | `flex-direction:column; align-items:stretch` at ≤768px |
| "Launch in CMD" shown on Android (useless) | Hidden via `display:none` on mobile; replaced by Share button |
| Output folder default `D:/KZ Downloads` shown on Android | Auto-set to `/sdcard/Download/KZ Downloads` on first load |
| Viewport missing `viewport-fit=cover` (notch/cutout devices) | Meta tag updated; `apple-mobile-web-app-capable` added |

### Changed

| Element | Before | After |
|---|---|---|
| All `navigator.clipboard` calls | Raw, no fallback | Routed through `safeCopy()` |
| Setup Guide OS tabs | Windows / macOS / Linux | + Android / iOS |
| Version string | v2.3 | v2.4 |

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | `safeCopy()`, `execCmdCopy()`, `shareCmd()` added; all clipboard calls updated; mobile CSS block added; viewport meta updated; Android + iOS setup panels added; Share button added; outdir-hint div added; `applyPlatformDefaults()` added |
| `CHANGELOG.md` | This file |

---

## v2.3 — Fix: Button and Tab Contrast in Both Themes
**Date:** 27-06-2026

### Problem

All interactive controls — action buttons, nav tabs, history type tabs, OS tabs, output mode tabs, and flag chip toggles — had near-invisible labels in both dark and light mode. In light mode the issue was obvious on a phone screen; in dark mode the inactive tab text was equally washed out.

### Root Cause

Every coloured button and tab was styled using low-opacity tint tokens (`--ok-bg`, `--accent-dim`, `--warn-bg`, `--danger-bg`, `--tab-inactive`) at 8–12% opacity. These tokens were designed for notice box backgrounds where the surrounding card provides visual separation. Used as button fills, the tint is too faint to create contrast with the card surface behind it, so the text label blends in regardless of theme.

The single shared token values for `color` (e.g. `--accent-text`, `--text-muted`) compound the issue — the same muted values are used in both themes, so neither theme gets text dark or bright enough to read against a near-transparent fill.

### Fix

| Element | Before | After |
|---|---|---|
| `.btn` (base) | `--surface2` background, `--border-str` border, `--text` color | Per-theme solid fills: dark `#2e3035`, light `#e2e3e8`; high-contrast text |
| `.btn-accent` (Import) | `--accent-dim` tint (~12%) | Dark: solid `#00a896` with black text. Light: solid `#007a6a` with white text |
| `.btn-ok` (Export selected) | `--ok-bg` tint (~8%) | Dark: solid `#0d6646` with bright mint text. Light: solid `#0a6640` with white text |
| `.btn-ghost` (Delete selected) | `background:none`, `--text-muted` color | Dark: dark crimson `#2a1f1f` with muted red text. Light: pale rose with deep red text |
| `.btn-warn` (Launch in CMD) | `--warn-bg` tint (~8%) | Dark: solid `#5a3e00` with gold text. Light: solid `#7a5000` with white text |
| Nav tabs (inactive) | `--text-muted` on transparent | Dark: `#7a7b82`. Light: `#555760` |
| Nav tabs (active) | `--accent-text` + `--accent` underline | Dark: `#00d9b8`. Light: `#006657` |
| History type tabs, OS tabs, Output mode tabs | `--tab-inactive` + `--text-muted` | Per-theme solid fills matching button pattern above |
| Flag chips (inactive) | `--surface2` + `--border` + `--text-sec` | Dark: `#2e3035`. Light: `#e2e3e8` |
| Flag chips (active) | `--accent-dim` tint | Dark: solid `#004d44` with `#00e8c8` text. Light: solid `#006657` with white text |

All styles migrated from shared token references to explicit `:root[data-theme="dark"]` and `:root[data-theme="light"]` selectors so each theme has fully independent, contrast-verified values.

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | `.btn`, `.btn-accent`, `.btn-ok`, `.btn-ghost`, `.btn-warn` — per-theme solid colour overrides; `.nav-tab`, `.hist-type`, `.os-tab`, `.out-tab`, `.flag-chip` — all converted from tint tokens to per-theme explicit styles |

---

## v2.2 — Feature: History Tab + Setup Guide Improvements + Responsive Code Blocks
**Date:** 27-06-2026

### Added

**History tab (`kz-history`)**

A new 🕓 History tab logs every URL queued and every command generated. Stored in `localStorage` under `kz-history`, capped at 500 entries, newest-first.

| Feature | Detail |
|---|---|
| Link history / Command history | Two sub-views toggled by a tab strip |
| Live search | Filters across URLs and command text in real time |
| Selectable entries | Checkbox per row; Select All / Deselect All toggle |
| Export selected | Exports checked entries (or all visible if none checked) as a dated `.json` file |
| Import | Accepts a previously exported `.json`; duplicate entry IDs are skipped |
| Per-entry actions | Copy URL, copy command, re-add to profile queue, delete |
| Clear all history | Confirmation-gated link at the bottom of the tab |
| Auto-logging | Commands generated in the Output tab silently log each URL + command pair; deduped within a 5-second window to prevent spam |

### Fixed

**1. macOS code block overflow**

Long commands (e.g. the Homebrew install URL) broke out of their container on mobile and narrow viewports.

Root cause: `.step-body` was a flex child with no `min-width: 0`, so the browser refused to shrink it below its content width regardless of available space.

Fix: added `min-width: 0` to `.step-body` and all history flex children. Combined with existing `white-space: pre-wrap` and `word-break: break-all` on `.code-block`, text now wraps correctly at any width.

**2. OS tab strip clipping**

The Windows / macOS / Linux tab strip was set to `display: inline-flex`, causing it to overflow its card on narrow screens.

Fix: changed to `display: flex; width: 100%` so tabs always fill the available card width.

### Changed

| Element | Before | After |
|---|---|---|
| `.code-block` font size | Hard-coded `12px` | `clamp(9px, 1.8vw, 12.5px)` — scales with viewport; bumps to `13px` above 900px |
| `.code-block` padding | Hard-coded `.75rem 4rem .75rem 1rem` | `clamp()` values on all four sides; Copy button offset also clamped |
| Linux setup guide | Single combined install line | Three full steps: install Python + pip + FFmpeg (with `python3 --version && pip3 --version` verification), install yt-dlp, verify. Note added for non-Debian distros (Fedora, Arch) |

### Storage Keys

| Key | Contents |
|---|---|
| `kz-downloader-profiles` | Profile queue |
| `kz-downloader-opts` | Options: format, output dir, template, date filter |
| `kz-history` | Link + command history (new in v2.2) |

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | History tab HTML + CSS + JS; `.code-block` responsive sizing; `.step-body` flex fix; `.os-tabs` width fix; Linux setup guide expanded |
| `README.md` | History tab documented; local storage table added; Quick Start notes for Python and Homebrew expanded |
| `CHANGELOG.md` | This file |

---

## v2.1 — Feature: Persistent Local Storage
**Date:** 27-06-2026

### Added

- **Profile queue persistence** — profiles saved to `localStorage` (`kz-downloader-profiles`) on every add or remove. Reopening the file restores the full queue automatically.
- **Options persistence** — output folder, format/quality, filename template, and date filter saved to `localStorage` (`kz-downloader-opts`) and restored on load.
- **✓ SAVED indicator** — flash label next to the queue count confirms each write to storage.
- **⊘ Clear saved** button in the Output tab — wipes `localStorage` so the queue does not reload on next open. Separate from "Clear queue" which only clears the in-memory session.

### Notes

`localStorage` is scoped to the file path. Works correctly when opening `KZ-Downloader.html` directly from disk in any Chromium or Firefox browser. No server or internet connection required.

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | `saveProfiles()`, `loadProfiles()`, `saveOpts()`, `loadOpts()`, `flashSaved()`, `clearSavedData()` added; init calls added |

---

## v2.0 — Rebuild: KZ Downloader (Universal Profile Scanner)
**Date:** 27-06-2026

### Changed

Renamed from **yt-dlp Tata Downloader** to **KZ Downloader**. App restructured from a single-purpose Tata tool into a universal yt-dlp GUI supporting any social platform.

### Added

- **Universal profile scanner** — any YouTube channel, Instagram profile, Facebook page, LinkedIn company page, Twitter/X account, or direct video URL can be added.
- **Platform auto-detection** — URLs are identified on paste and labelled with a coloured platform badge (YouTube, Instagram, Facebook, LinkedIn, Twitter/X, Generic).
- **Download mode toggle** — *Download all* or *List only* (`--flat-playlist --print`) to preview a channel before committing.
- **LinkedIn support** — with contextual cookie-auth warning when a LinkedIn URL is detected in the queue.
- **Quick presets** — one-click shortcuts for Tata Motors, Tata Trucks, Tata Commercial Vehicles, Tata SCV across YouTube, Instagram, Facebook, and LinkedIn.
- **Date filter** — optional `--dateafter YYYYMMDD` field.
- **Channel/Date_Title.ext** filename template — organises downloads into per-channel subfolders.
- **Launch in CMD** — generates and downloads `KZ-Launch.bat`; double-click to open CMD with commands ready.
- **Dark / Light mode toggle** — header button, persistent within session.
- **Setup Guide tab** — step-by-step install instructions for Python, FFmpeg, and yt-dlp on Windows, macOS, and Linux. Copy buttons on every code block.
- **Terminal-style output block** — dark terminal UI with macOS window chrome.
- `README.md` and `CHANGELOG.md` added.

### Removed

- Tata-only hardcoded handles as the primary interface (retained as optional quick presets).

### Files Changed

| File | Change |
|---|---|
| `KZ-Downloader.html` | Full rewrite — universal scanner, platform detection, tabs, setup guide, terminal output |
| `README.md` | Created |
| `CHANGELOG.md` | Created |

---

## v1.0 — Initial Release: yt-dlp Tata Downloader
**Date:** 26-06-2026

First working version. Tata-specific tool for queuing social profiles and generating yt-dlp commands.

- Hardcoded quick-add handles for Tata Motors, Tata Commercial Vehicles, Tata SCV across YouTube, Instagram, Facebook.
- URL queue with duplicate detection and per-URL removal.
- Format / quality selector (Best, 1080p, 720p, 480p, Audio-only, MP4-preferred).
- Output folder and filename template configuration (4 presets + custom).
- Flag toggles: embed thumbnail, add metadata, embed subtitles, full playlist, single video, rate limit, cookies from Chrome, parallel fragments, SponsorBlock.
- Three output modes: terminal command, `.bat` batch script, args file.
- Copy-to-clipboard and download-file actions.
- LinkedIn quick-add with contextual authentication notice.
- Responsive layout down to mobile widths.

**Files:** `KZ-Downloader.html`

---

*Project created and maintained by Jaswant Kanojia — LDE Bajaj, LDE Royal Enfield & Swift Trucks LLP, Lucknow.*
