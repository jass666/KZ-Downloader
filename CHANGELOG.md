# Changelog - KZ Downloader

All notable changes to **KZ Downloader** are documented here.

Project created and maintained by **Jaswant Kanojia**.

**Date:** 22-07-2026

---

## v4.4 — Improvement: Run in Colab Now Auto-Reads the Command (No Paste Step)
**Date:** 22-07-2026

### Changed

**`KZ_Colab_Downloader.ipynb` no longer requires pasting the command into a form field.** The notebook's single cell now calls `google.colab.output.eval_js('navigator.clipboard.readText()')` on run and uses whatever was just copied by the site's **☁️ Run in Colab** button directly — reducing the flow to: click the button on the site → click ▶ once in the notebook → downloads start.

If clipboard reading fails or returns something that doesn't look like a yt-dlp command (browser blocked it, permission not yet granted, or nothing was copied), the cell falls back to an `input()` prompt asking for a manual paste, so it degrades gracefully rather than failing silently.

**Important limitation, not a bug:** Colab never auto-executes any cell on notebook open, by Google's own design — this is a deliberate anti-abuse safeguard that applies to every Colab notebook regardless of host or author. The single ▶ click in Colab can't be removed; this change only removes the paste step that used to follow it.

Site-side wording updated to match: the toast after clicking **☁️ Run in Colab** and the notice text under the action row both now describe "click ▶, no pasting" instead of "paste it into the cell."

### Files Changed

| File | Change |
|---|---|
| `KZ_Colab_Downloader.ipynb` | Replaced the `#@param` paste field with automatic clipboard reading via `google.colab.output.eval_js`; added fallback to manual `input()` paste prompt if clipboard read fails or looks wrong; intro/notes markdown updated to describe the new flow |
| `index.html` | `runInColab()` toast text and `colab-notice` copy updated to describe the no-paste flow; logo version bumped to `4.4` |
| `CHANGELOG.md` | This entry |

---

## v4.3 — Feature: Run in Colab (No-Install Cloud Downloads)
**Date:** 22-07-2026

### Added

**☁️ Run in Colab button** in the action row (Profiles tab), next to **▶ Launch in CMD** — copies the generated command to the clipboard and opens a companion Google Colab notebook (`KZ_Colab_Downloader.ipynb`) in a new tab. The notebook checks for yt-dlp/ffmpeg and installs whichever is missing (first run in a session only, ~20s; skipped on later runs), executes the pasted command, and streams each finished file straight to the browser's own download queue one at a time — no Python, FFmpeg, or any local install required on any device.

Built for devices where local Python setup isn't practical: Android without Termux, iOS, Chromebooks, or handing a link to a non-technical coworker who just needs a file. The notebook strips whatever `-o`/`--output` value is already in the pasted command — regardless of which device generated it (e.g. a Windows `D:/KZ Downloads/...` path) — and rewrites it to a safe path inside the Colab session automatically, so any command pasted from any device just works.

**Hosting:** the notebook is hosted on the user's own Google Drive (shared as "Anyone with the link" → Viewer) and opened via `https://colab.research.google.com/drive/FILE_ID`, rather than being pushed through the GitHub/Cloudflare Pages deploy pipeline — it isn't part of the static site itself. Updating the notebook means re-uploading the new version to the same Drive file (keeping its file ID, and therefore the link, unchanged), not running the deploy script.

**No Google Drive dependency for downloads** — despite being Drive-hosted as a notebook file, the notebook itself never touches the user's Drive for output. Downloaded files live only in a temporary folder inside the Colab session until they land in the browser's downloads, then they're gone from Colab.

**Notices updated** — the Android and iOS output notices now mention Run in Colab as the no-install alternative to Termux/SSH. A new universal notice under the action row explains what the button does and flags its one limitation: it only works for public content, since Colab has no way to interactively log into LinkedIn or private IG/FB the way the local Playwright scanner does.

### Files Changed

| File | Change |
|---|---|
| `index.html` | New `btn-run-colab` button + `runInColab()` handler; `COLAB_NOTEBOOK_URL` constant added (Drive-hosted link); new `colab-notice` div; Android/iOS output notices updated to mention the option; logo version bumped to `4.3` |
| `KZ_Colab_Downloader.ipynb` | New file — single-cell Colab notebook that auto-installs yt-dlp/ffmpeg if missing, executes pasted command(s), and downloads each finished file to the browser individually |
| `README.md` | New "Run in Colab" section; Quick Start step 3 and File Structure updated; version bumped to `4.3` |
| `CHANGELOG.md` | This entry |

---

## v4.2 — Fix: Batch Script / Launch-in-CMD Silently Corrupting URLs
**Date:** 17-07-2026

### Fixed

**`%` characters in `.bat` output not escaped for cmd.exe** — commands copied from the Terminal tab and pasted directly into a shell (typically PowerShell, where `%` is not a metacharacter) worked fine, but the same commands written into the downloaded `.bat` file (via the Batch Script tab or **▶ Launch in CMD**) could skip files or throw "bad url" errors.

Root cause: `.bat` files are always executed by `cmd.exe`, regardless of which shell the user normally uses. `cmd.exe` expands any `%...%` pattern as an environment variable reference and silently drops it if no matching variable exists. This corrupted two things on every batch run:
- yt-dlp's own output template (`%(title)s.%(ext)s`) — the percent signs got eaten by cmd's variable expansion before yt-dlp ever saw them.
- Percent-encoded characters inside URLs (`%20`, `%3D`, etc. — common in Instagram/Facebook links) — cmd tried to expand these as variables too, truncating or mangling the URL mid-command.

Because the exact same string wasn't a problem when typed/pasted directly (PowerShell doesn't touch `%`), the bug only showed up specifically in `.bat` output, which made it look like the batch generation itself was broken rather than a shell-parsing difference.

**Fix:** `buildCmd(url, forBatch)` now takes a second parameter. When `forBatch` is `true`, every `%` in the fully-built command line is doubled to `%%` — the standard cmd.exe escape for a literal percent sign — before being written into the `.bat` file. The Batch Script tab (`regenerate()`) and **▶ Launch in CMD** (`launchBat()`) now both call `buildCmd(u, true)`. The Terminal tab and command-history logging (`logCurrentToHistory()`) are unaffected and continue to call `buildCmd(u)` with single, un-doubled percent signs, since those are meant for direct copy/paste into an interactive shell.

### Files Changed

| File | Change |
|---|---|
| `index.html` | `buildCmd()` gained a `forBatch` parameter that doubles `%` for cmd.exe safety; `regenerate()`'s batch branch and `launchBat()` updated to pass `true`; logo version bumped to `4.2` |
| `CHANGELOG.md` | This entry |

---

## v4.1 — Feature: Import URL List From Text File
**Date:** 17-07-2026

### Added

**"📄 Import from text file" button in the Profiles tab** — sits directly under the manual add-profile row. Opens a file picker (`accept=".txt,.csv"`) and hands the selected file to a new `importUrlListFile(event)` handler.

**`importUrlListFile()`** — reads the file as plain text and parses it line by line:
- `#`-prefixed lines are treated as comments / section headers and ignored.
- Plain URL-per-line files are supported directly.
- Pipe-delimited lists in the form `filename | url | page | status` are also supported (e.g. an `image-sources.txt` export), splitting on `|` and reading the second field as the URL.
- Lines whose URL field is a placeholder (`TBD`, `N/A`, `(not found)`, `(not yet verified)`, dashes, or anything not starting with `http://`/`https://`) are **not** queued — they're collected and reported instead, so nothing malformed reaches the yt-dlp command builder.
- Valid, non-duplicate URLs are pushed into the existing `profiles` array and go through the normal `renderProfiles()` / `checkLinkedIn()` / `saveProfiles()` pipeline, so they behave exactly like manually-added URLs (persisted to `localStorage`, included in the generated terminal/batch/args output).

**Import summary** — on completion, an `alert()` reports how many URLs were queued, how many duplicates were skipped, and lists (up to 15, with a "…and N more" overflow note) which lines were skipped for having no usable URL, including the filename and status text from the source file where available. A `showToast('✓ Imported N URL(s)')` confirms success in the corner as well, consistent with the app's existing toast conventions.

### Notes

This reuses the existing single-URL `profiles` queue — it does not introduce per-item target filenames or a separate download path. It's meant for pulling a batch of confirmed URLs (e.g. from a sourcing/audit text file) straight into the queue instead of pasting them one at a time. For workflows where each URL needs to be saved under a *specific* target filename (like the Swift Trucks image-sources format), use the companion `download_images.py` script instead, which reads the same pipe-delimited format and writes files out under their intended names.

### Files Changed

| File | Change |
|---|---|
| `index.html` | Import button + hidden file input added to Profiles tab; `importUrlListFile()` and `LIST_IMPORT_PLACEHOLDER_RE` added; logo version bumped to `4.1` |
| `CHANGELOG.md` | This entry |

---

## v4.0 — Fix + UI/UX: History Spam, URL Validation, clearAll, Stale Notices, Settings Regen, Preset Modal Escape; Toast System, Terminal Badge, Input Glow, Action Row, Scrollbar
**Date:** 30-06-2026

### Fixed

**1. History logged on every keystroke (spam)** — `logToHistory()` was called inside `regenerate()`, which fires on every profile render and every option change. Typing a single character in the output folder field would write dozens of duplicate history entries per second, overwhelming the 500-entry cap and making history meaningless. Logging has been moved out of `regenerate()` entirely into a dedicated `logCurrentToHistory()` helper that is called only on explicit user actions: **Copy**, **Share**, **Download file**, and **Launch in CMD**. History now records what the user actually did, not passive state changes.

**2. No URL validation before addToQueue()** — `addToQueue()` accepted any string, including plain text like `asdfg` or partial paths, silently adding them to the queue and generating malformed yt-dlp commands. A guard now rejects any input that does not start with `http://` or `https://` and shows a clear alert before touching the queue.

**3. clearAll() wiped localStorage instead of saving the empty queue** — `clearAll()` called `localStorage.removeItem(STORAGE_KEY)` directly, meaning the key was deleted rather than updated. This diverged from how the rest of the app handles persistence and could cause stale data to reappear on edge cases. The function now calls `saveProfiles()` (which serialises the empty array into storage) to stay consistent. The confirm dialog text was also corrected from the ambiguous *"Clear all profiles?"* to *"Clear all profiles from the queue?"* to distinguish it from **⊘ Clear saved**.

**4. Stale "Setup Guide" references in notices and banners** — five places in the HTML referenced the old tab name "Setup Guide" after it was renamed to "Help" in v3.7. All have been updated to **"Help → Setup Guide"** (or **"Help → Setup Guide → Android / iOS"** where the OS sub-tab was also named):

| Location | Before | After |
|---|---|---|
| Mac output notice | `See Setup Guide for details` | `See Help → Setup Guide for details` |
| Linux output notice | `See Setup Guide` | `See Help → Setup Guide` |
| Android output notice | `see Setup Guide → Android` | `see Help → Setup Guide → Android` |
| Android device banner | `See Setup Guide → Android for one-time setup` | `See Help → Setup Guide → Android for one-time setup` |
| iOS device banner | `See Setup Guide → iOS` | `See Help → Setup Guide → iOS` |

**5. Settings changes did not update the generated command** — `format-sel`, `outdir`, `tmpl-custom`, and `date-filter` inputs called `saveOpts()` on change but not `regenerate()`. The download mode radio buttons called `updateMode()` but not `regenerate()`. The command block therefore showed a stale command whenever the user adjusted settings without switching tabs. All five listeners now chain `regenerate()` after saving, so the terminal block always reflects current options in real time.

**6. Preset modal had no keyboard dismiss** — the modal could only be closed via the Cancel button. An `Escape` keydown listener is now registered globally at init; if the preset modal is open, `Escape` calls `closePresetModal()`.

### Changed

**`regenerate()`** — history logging removed. Function is now purely responsible for building and rendering the command text.

**`logCurrentToHistory()`** — new helper function. Iterates `profiles` and writes one `command` entry and one `link` entry per URL to history. Called only from `copyCmd()`, `shareCmd()`, `downloadFile()`, and `launchBat()`.

**`addToQueue()`** — URL format guard added before duplicate check.

**`clearAll()`** — confirm text updated; `localStorage.removeItem()` replaced with `saveProfiles()`.

**Settings event listeners** — `regenerate()` chained onto `input`/`change` handlers for `format-sel`, `outdir`, `tmpl-custom`, `date-filter`, and `[name=dlmode]` radio buttons.

### Added (UI/UX)

**Toast / snackbar system** — a `showToast(msg, type, duration)` function and `.toast-stack` DOM container replace all in-place button-text mutations. Toasts appear in the bottom-right corner, stack vertically, animate in and out with opacity and a small Y-translate, and respect both dark and light themes. Three visual variants: `ok` (teal/green), `warn` (amber), `err` (red). Toasts are used for:

| Action | Toast message |
|---|---|
| Copy command | `✓ Copied to clipboard` |
| Share (fallback copy) | `✓ Copied to clipboard` |
| Download file | `⬇ kz-commands.txt downloaded` (filename varies by tab) |
| Add preset to queue | `✓ Added to queue` |
| Copy code block (Setup Guide) | `✓ Copied` |

**Terminal bar URL count badge** — a `#term-count` label is added to the right of the terminal bar. It shows `1 URL` / `N URLs` when profiles are queued and clears when the queue is empty. Updated live by `regenerate()`. Rendered in `.term-count` (monospace, muted colour, `user-select:none`).

**Input / select focus glow** — all `input[type=text]` and `select` elements now emit a `box-shadow: 0 0 0 3px var(--accent-dim)` ring on focus in addition to the existing `border-color` highlight. Consistent with the brand accent colour in both dark and light themes.

**Action row separator** — a `.action-sep` thin vertical rule (`1px` wide, `24px` tall) is inserted between the primary action buttons (Copy, Download file, Launch in CMD, Share) and the destructive ones (Clear queue, Clear saved). Hidden automatically on mobile via `@media(max-width:768px)` where buttons stack vertically.

**Profile item hover highlight** — `.profile-item` gains `transition` and on hover shows `border-color: var(--border-str)` and `background: var(--bg2)`, making the queue easier to scan.

**Terminal body scrollbar styling** — custom thin scrollbar (5px, rounded thumb, transparent track) via `::-webkit-scrollbar` rules on `.term-body`. Replaces the default fat browser scrollbar that occupied significant horizontal space inside the terminal block.

**Preset modal backdrop dismiss** — `onclick="if(event.target===this)closePresetModal()"` added to the modal overlay `div`. Clicking anywhere outside the modal card now closes it, consistent with standard modal UX. Works alongside the existing Cancel button and Escape key listener.

**Filename template dropdown now triggers regenerate** — `tmpl-sel` (`onchange`) previously only called `syncTemplate()`. It now also calls `saveOpts()` and `regenerate()`, so switching presets (e.g. from `Title.ext` to `Channel/Date_Title.ext`) immediately updates the command block.

### Changed

**`regenerate()`** — history logging removed; URL count badge update added.

**`logCurrentToHistory()`** — new helper function. Iterates `profiles` and writes one `command` entry and one `link` entry per URL to history. Called only from `copyCmd()`, `shareCmd()`, `downloadFile()`, and `launchBat()`.

**`addToQueue()`** — URL format guard added before duplicate check.

**`clearAll()`** — confirm text updated; `localStorage.removeItem()` replaced with `saveProfiles()`.

**`copyCmd()`** — button text mutation removed; `showToast('✓ Copied to clipboard')` used instead.

**`shareCmd()`** — button text mutation removed; `showToast('✓ Copied to clipboard')` used on fallback copy.

**`downloadFile()`** — `showToast()` added after download is triggered.

**`addPreset()`** — `showToast('✓ Added to queue')` added.

**`copyCode()`** — `showToast('✓ Copied')` added alongside the existing button label flash.

**`tmpl-sel` onchange** — extended from `syncTemplate()` to `syncTemplate(); saveOpts(); regenerate()`.

**Settings event listeners** — `regenerate()` chained onto `input`/`change` handlers for `format-sel`, `outdir`, `tmpl-custom`, `date-filter`, and `[name=dlmode]` radio buttons.

### Files Changed

| File | Change |
|---|---|
| `index.html` | `logToHistory()` removed from `regenerate()`; `logCurrentToHistory()` added and wired to Copy / Share / Download / Launch; URL validation guard in `addToQueue()`; `clearAll()` dialog text and storage call corrected; Mac / Linux / Android / iOS notice and banner text updated to reference Help tab; settings listeners extended with `regenerate()`; Escape key listener added for preset modal; `showToast()` function and `.toast-stack` container added; `.toast` / `.toast.ok` / `.toast.warn` / `.toast.err` CSS added; `.term-count` badge added to terminal bar and wired in `regenerate()`; input focus glow (`box-shadow`) added to `select` and `input[type=text]`; `.action-sep` CSS and element added to action row; `.profile-item` hover transition added; `.term-body` custom scrollbar CSS added; preset modal backdrop `onclick` dismiss added; `tmpl-sel` onchange extended; logo version updated to `4.0` |
| `CHANGELOG.md` | This entry |

---

## v3.9 — Docs: Quick-Install Callout via Hosted requirements.txt
**Date:** 29-06-2026

### Added

**Quick-install callout block in Setup Guide** — a highlighted callout added at the top of the Setup Guide section (before any OS-specific steps) for users who already have Python installed. Points to the hosted `requirements.txt` on MediaFire (`https://www.mediafire.com/file/rs8rde8jdrt2p8z/requirements.txt/file`) with two commands to get running immediately:

```
pip install -r requirements.txt
playwright install chromium
```

A note in the callout reminds users that FFmpeg still needs to be installed separately as a system dependency (not via pip). The callout is styled as a blockquote so it visually stands out from the rest of the step-by-step OS instructions, making the fast path immediately visible without disrupting the full guide below.

### Files Changed

| File | Change |
|---|---|
| `README.md` | Quick-install callout block added at top of Setup Guide / Install section |
| `index.html` | Same callout block added at top of the Setup Guide sub-panel |
| `CHANGELOG.md` | This entry |

---

## v3.8 — Docs: requirements.txt + README Install Guide Update
**Date:** 29-06-2026

### Added

**`requirements.txt`** — new file listing all pip-installable dependencies (`yt-dlp`, `playwright`) in one place. Includes inline comments covering the `playwright install chromium` post-install step and per-platform FFmpeg install commands (`winget`, `brew`, `apt`, `pkg`) with a confirm step (`ffmpeg -version`). FFmpeg is noted as a system dependency not installable via pip.

### Changed

**README install steps updated across all platforms** to reference `requirements.txt` instead of standalone `pip install yt-dlp` calls:

| Section | Change |
|---|---|
| **Windows** | Step 2 now installs FFmpeg via `winget install ffmpeg`; Step 3 (new) runs `pip install -r requirements.txt` + `playwright install chromium` |
| **macOS** | Homebrew block changed from `brew install python ffmpeg yt-dlp` to `brew install python ffmpeg`; Step 2 updated to `pip install -r requirements.txt` + `playwright install chromium` |
| **Linux** | Step 2 now runs `pip install -r requirements.txt` + `playwright install chromium` after the `apt install ffmpeg` line |
| **Android (Termux)** | Step 3 uses `pip install -r requirements.txt`; note added that Playwright won't run on Termux — yt-dlp installs and works normally |
| **Playwright Scanner Prerequisites** | Replaced standalone `pip install playwright` with `pip install -r requirements.txt` |

**File Structure table in README** updated to include `requirements.txt`.

### Files Changed

| File | Change |
|---|---|
| `requirements.txt` | Created — yt-dlp and playwright dependencies with FFmpeg guidance in comments |
| `README.md` | Install steps updated across Windows, macOS, Linux, Android, and Playwright sections; `requirements.txt` added to file structure table |
| `CHANGELOG.md` | This entry |

---

## v3.7 — Fix + UX: Scanner Download Link + Help Sub-Tabs
**Date:** 29-06-2026

### Fixed

**`kz_scanner.py` download link was a broken stub** — the `⬇ Download kz_scanner.py` link in the Scanner → Playwright → One-time setup (Step 2) previously called `downloadKzScanner()`, which generated a local blob containing only a placeholder comment. The link now points directly to the hosted file on MediaFire (`https://www.mediafire.com/file/26bwb82iipgktig/kz_scanner.py/file`) and opens in a new tab. The `onclick` stub and `downloadKzScanner()` function are no longer used for this link.

### Changed

**Help panel refactored from scrolling sections to horizontal sub-tabs** — the `❓ Help` panel previously rendered three sections (About, Setup Guide, Getting Started) stacked vertically, separated by `<hr>` dividers and uppercase plain-text labels. These are now presented as a horizontal sub-tab bar (`📄 About`, `⚙️ Setup Guide`, `🚀 Getting Started`) matching the same underline-active style as the main nav tabs. Only the active sub-panel is visible at a time, reducing scroll depth and improving discoverability.

#### Implementation details

**`.help-sub-tabs`** — flex row container for the three sub-tab buttons, with a bottom border matching the main nav style.

**`.help-sub-tab`** — individual tab button; inherits the same active/hover colour rules (teal underline in dark mode, dark green in light mode) as `.nav-tab`.

**`.help-sub-panel`** — wrapper for each section's content; `display:none` by default, `display:block` when `.active`.

**`switchHelpTab(id, btn)`** — removes `.active` from all `.help-sub-tab` and `.help-sub-panel` elements, then activates the clicked button and the matching `#help-{id}` panel.

### Files Changed

| File | Change |
|---|---|
| `index.html` | Scanner Step 2 download link changed from blob stub to direct MediaFire URL; Help panel HTML restructured into three `.help-sub-panel` divs under a `.help-sub-tabs` nav; CSS for `.help-sub-tabs`, `.help-sub-tab`, `.help-sub-panel` added; `switchHelpTab()` function added |
| `CHANGELOG.md` | This entry |

---

## v3.6 — Feature: Playwright Scanner — Collapsible Setup + Enhanced Run Options
**Date:** 29-06-2026

### Added

**Collapsible one-time setup block (Steps 1 & 2)** — the "Install dependencies" and "Download kz_scanner.py" steps are now grouped inside a collapsible `① ② One-time setup` section that starts collapsed. Clicking the header toggles the body open and closed with a chevron indicator. Reduces visual noise for users who have already completed initial setup.

**Website / Platform selector** — a dropdown added to Step 3 with explicit options for LinkedIn, Instagram, Facebook, YouTube, Twitter/X, TikTok, Vimeo, and Other/Generic, plus a default "Auto-detect from URL" entry. When the user pastes a Target URL the platform is detected automatically using URL pattern matching. A `⟳ Auto-detect` button beside the label re-runs detection on demand. Selection persists across sessions via `localStorage`.

**Output folder for JSON** — a path input field added to Step 3 where the user specifies the directory the JSON file should be saved in (e.g. `C:\Users\You\Downloads`). Leaving it blank saves to the current working directory. Value persists across sessions. A `✓ saved` flash badge confirms writes.

**KZ Downloader folder path** — a second path input field added to Step 3 specifying where `kz_scanner.py` lives. When filled in, the generated command is prefixed with `cd /d "..."` so the script can be run from any CMD window, not just one opened from inside that folder. A contextual hint notice appears when the field is active.

**Auto-named output filename** — the output filename is no longer a free-text field. It is generated automatically in the format `platform-dd-mm-yy-hh-mm.json` (e.g. `linkedin-29-06-26-14-03.json`) using the platform selection and the current time at the moment the command is viewed. The computed filename is shown in a read-only field. The full output path (folder + filename) is wired into the `--out` argument in the generated command.

**`togglePwSetup()`** — toggles the collapsible setup body and rotates the chevron icon.

**`loadPwPersist()` / `savePwPersist()`** — read and write the Playwright panel's persistent values (output folder, KZ folder, scroll count, platform selection) to `localStorage` under `kz_pw_persist_v1`. `loadPwPersist()` is called when the Playwright tab is activated. `savePwPersist()` is called on any field change.

**`pwAutoDetectPlatform(force)`** — checks the Target URL against `PW_PLATFORM_PATTERNS` and updates the platform selector. Called automatically on URL input (only overrides when selector is on `auto`) and manually via the `⟳ Auto-detect` button (always overrides).

**`buildPwFilename()`** — constructs the timestamped output filename from the current platform selection and `new Date()`. Called inside `updatePwCommand()` on every rebuild.

**`PW_PLATFORM_PATTERNS`** — array of `{rx, val}` objects mapping URL regexes to platform selector values; used by `pwAutoDetectPlatform()`.

**`PW_PERSIST_KEY`** — localStorage key constant (`'kz_pw_persist_v1'`) for Playwright panel persistence.

### Changed

**`updatePwCommand()`** — extended to read the new output folder, KZ folder, and platform fields. Now calls `buildPwFilename()` to compute the output filename, then constructs the full output path by joining the folder (if set) and the filename with the correct path separator. If a KZ folder is specified the command is prefixed with `cd /d "..."`. The `--out` argument always receives the full resolved path.

**Step 3 layout** — reorganised into four distinct rows: Target URL; Platform selector + Scrolls side-by-side; Output folder + KZ folder side-by-side; Output filename (read-only) + Generated command.

**`setScanMode()`** — now calls `loadPwPersist()` in addition to `updatePwCommand()` when switching to Playwright mode.

### Storage Keys

| Key | Contents |
|---|---|
| `kz_pw_persist_v1` | Playwright panel: output folder, KZ folder path, scroll count, platform selection |

### Files Changed

| File | Change |
|---|---|
| `index.html` | Collapsible setup block HTML + CSS (`.pw-collapsible`, `.pw-collapsible-header`, `.pw-collapsible-body`, `.pw-collapse-chevron`, `.pw-persist-badge`, `.pw-inline-btn`); Step 3 restructured with platform selector, output folder, KZ folder, read-only filename fields; `togglePwSetup()`, `loadPwPersist()`, `savePwPersist()`, `showBadge()`, `pwAutoDetectPlatform()`, `buildPwFilename()`, `PW_PLATFORM_PATTERNS`, `PW_PERSIST_KEY` added; `updatePwCommand()` and `setScanMode()` updated |
| `CHANGELOG.md` | This entry |

---

## v3.5 - Fix: LinkedIn Scanner Extraction + Safer Scrolling
**Date:** 29-06-2026

### Fixed

**LinkedIn video feed scrolling without collecting links** - the scanner was moving past visible LinkedIn video posts but often found `0` items because the extractor depended on older feed container selectors and only looked for `/feed/update/` anchors inside those containers.

LinkedIn extraction now captures post/activity links from multiple modern LinkedIn patterns:

- `/feed/update/` links
- `/posts/` links
- `urn:li:activity:*` values from `href`, `data-urn`, `data-id`, and `id`
- `urn:li:activity:*` references found in the page HTML

Activity URNs are converted into stable LinkedIn feed update URLs so the JSON output contains usable platform links.

**LinkedIn scroll speed too aggressive** - LinkedIn pages now scroll in smaller steps (`900px`) so posts stay in view long enough to be harvested. The scanner also harvests once before and once after each scroll.

### Files Changed

| File | Change |
|---|---|
| `kz_scanner.py` | Broadened LinkedIn extraction; added activity URN conversion; added page HTML fallback scan; reduced LinkedIn scroll distance; harvests before and after each scroll |
| `CHANGELOG.md` | This entry |

---

## v3.4 - Change: Saved-Login Scanner Window + Launcher Defaults
**Date:** 29-06-2026

### Changed

**CDP/debug Chrome flow replaced with a separate saved-login scanner window** - the guided launcher no longer kills Chrome or launches Chrome in remote debugging mode. The default browser mode now opens a separate persistent browser window using `kz_browser_profile`, so logins and cookies are preserved between scans without touching the user's normal Chrome session.

`kz_scanner.py` now tries to launch real Chrome via Playwright's `channel='chrome'` when available, falling back to bundled Chromium if Chrome is not available. The scanner also reuses the startup `about:blank` tab instead of opening an extra tab.

**Page load wait shortened** - normal navigation timeout reduced from `60s` to `15s`. If a site keeps loading in the browser, the scanner continues to the manual ENTER prompt instead of waiting too long.

**Launcher defaults simplified** - default mode now uses:

- Saved-login scanner window
- `10` scrolls
- `2.5s` delay
- Auto platform detection
- No HTTP bridge
- `kz_scan_results.json`

**Advanced launcher skip controls added** - advanced mode now supports:

- `S` - skip this option and keep the default
- `A` - skip all remaining options and keep defaults

Skip controls were added to browser mode, scroll count, delay, platform override, HTTP bridge, and output filename prompts.

**HTTP bridge prompt changed from Y/N to 1/2** - bridge selection now uses numbered choices for consistency with the rest of the launcher.

### Fixed

**Launcher killing Chrome and itself** - the scanner launcher no longer uses `taskkill` as part of the normal flow.

**Default scroll count too high** - default scroll count lowered from `60` to `10`.

### Files Changed

| File | Change |
|---|---|
| `kz_scan.bat` | Defaults changed to saved-login profile and 10 scrolls; advanced skip controls added; bridge prompt changed to 1/2; CDP/debug flow bypassed; final scanner command passes `--profile` |
| `kz_scanner.py` | Normal mode prefers real Chrome via `channel='chrome'`; reuses startup page; navigation timeout reduced to 15s |
| `CHANGELOG.md` | This entry |

---

## v3.3 — Feature: Guided BAT Launcher + CDP Browser Reuse
**Date:** 29-06-2026

### Added

**`kz_scan.bat` — step-by-step guided launcher for `kz_scanner.py`** — replaces manually typing the full command with a sequential prompt flow. Each parameter is asked one at a time with numbered presets; the final screen shows the assembled command before anything runs.

| Step | Prompt | Options |
|---|---|---|
| 1 | Browser mode | Reuse existing Chrome (CDP) / New browser window |
| 2 | Target URL | Free text; loops until non-empty |
| 3 | Scroll steps | Quick 20 / Normal 60 / Deep 120 / Custom |
| 4 | Scroll delay | Fast 1.5s / Normal 2.5s / Slow 4.0s / Custom |
| 5 | Platform override | Auto-detect / yt / ig / fb / li / tw / gen |
| 6 | HTTP bridge | Y starts `--serve` on port 7474 / N skips |
| 7 | Output filename | Default `kz_scan_results.json` / Custom |

Confirm screen shows all chosen values. User can press Enter to run, `R` to restart from the top, or `Q` to quit without running.

**CDP browser reuse mode (`--cdp` flag in `kz_scanner.py`)** — Playwright can now connect to an already-running Chrome instance via the Chrome DevTools Protocol instead of spawning a new Chromium window. This keeps the user's existing profiles, cookies, and logged-in sessions intact. A new tab is opened inside the existing Chrome window for the scan, and only that tab is closed when the scan finishes — the rest of the session is untouched.

`run_scan()` accepts a new `cdp_url` parameter (default `None`). When set:
- Connects via `p.chromium.connect_over_cdp(cdp_url)`
- Reuses `browser.contexts[0]` (existing profile context with all cookies)
- Opens a new page inside that context, navigates to the target URL, scans, then closes only the page

When `cdp_url` is `None`, existing behaviour (persistent profile launch) is unchanged.

**Fixed output directory for JSON results** — all scan output files are now saved to `D:\Projects\KZ Downloader\JSONs\` by default. Step 7 prompts only for the filename; the folder is fixed. The bat creates the directory automatically via `mkdir` if it does not exist.

### Fixed

**Box-drawing characters caused garbled output on Windows CMD** — the original bat used Unicode border characters (`╔ ║ ╚ ═`) that rendered as mojibake on CMD's default code page. All decorative characters replaced with plain ASCII (`= - [ ]`).

**Bat closed immediately after final confirmation** — `set "CMD=python kz_scanner.py "!URL!" ..."` embedded quotes around `!URL!` inside the outer `set "..."` quoting, which caused CMD to silently misparse and exit on execution. Fixed by keeping the URL separate from the args string and calling Python directly: `python kz_scanner.py "!URL!" !ARGS!`.

**CDP connection refused (`ECONNREFUSED 127.0.0.1:9222`)** — `localhost` on modern Windows resolves to IPv6 `::1`, but Chrome's debug server binds to IPv4 `127.0.0.1`. All CDP references changed from `http://localhost:9222` to `http://127.0.0.1:9222` in both `kz_scan.bat` and `kz_scanner.py`.

**Chrome debug port setup unreliable** — the original setup used text-parsing of PowerShell output (prone to whitespace/encoding mismatches), a fixed 4-second wait after launch (not enough), and a single hardcoded Chrome path. Replaced with:

- **Port check via exit code** — PowerShell uses `exit 0` / `exit 1` instead of printing text; CMD reads `!errorlevel!`, eliminating any text-parsing issues
- **Chrome path finder** — checks three locations in order: `C:\Program Files\...`, `C:\Program Files (x86)\...`, `%LOCALAPPDATA%\...` (user installs); exits with a clear message if none found
- **Kill-wait loop** — polls `tasklist` every second after `taskkill` and only proceeds once `chrome.exe` is fully gone from the process list
- **Port retry loop** — after launching Chrome, polls `http://127.0.0.1:9222/json/version` every second for up to 15 seconds; reports which second the port became ready; exits with a diagnostic message if the port never opens

### Files Changed

| File | Change |
|---|---|
| `kz_scan.bat` | Created; 7-step guided prompt flow; ASCII-only output; URL kept separate from ARGS to fix quote nesting; CDP URL changed to `127.0.0.1`; Chrome setup replaced with path finder, kill-wait loop, and 15s port retry loop; output directory fixed to `D:\Projects\KZ Downloader\JSONs\` |
| `kz_scanner.py` | `run_scan()` gains `cdp_url` parameter; CDP branch added (connect, reuse context, open tab, scan, close tab only); CLI gains `--cdp URL` argument; CDP default URL changed to `http://127.0.0.1:9222` |
| `CHANGELOG.md` | This entry |

---

## v3.2 — Feature: Guided BAT Launcher + CDP Browser Reuse
**Date:** 29-06-2026

### Added

**`kz_scan.bat` — step-by-step guided launcher for `kz_scanner.py`** — replaces manually typing the full command with a sequential prompt flow. Each parameter is asked one at a time with numbered presets; the final screen shows the assembled command before anything runs.

| Step | Prompt | Options |
|---|---|---|
| 1 | Browser mode | Reuse existing Chrome (CDP) / New browser window |
| 2 | Target URL | Free text; loops until non-empty |
| 3 | Scroll steps | Quick 20 / Normal 60 / Deep 120 / Custom |
| 4 | Scroll delay | Fast 1.5s / Normal 2.5s / Slow 4.0s / Custom |
| 5 | Platform override | Auto-detect / yt / ig / fb / li / tw / gen |
| 6 | HTTP bridge | Y starts `--serve` on port 7474 / N skips |
| 7 | Output filename | Default `kz_scan_results.json` / Custom |

Confirm screen shows all chosen values and the final `python kz_scanner.py ...` command. User can press Enter to run, `R` to restart from the top, or `Q` to quit without running.

**CDP browser reuse mode (`--cdp` flag in `kz_scanner.py`)** — Playwright can now connect to an already-running Chrome instance via the Chrome DevTools Protocol instead of spawning a new Chromium window. This keeps the user's existing profiles, cookies, and logged-in sessions intact. A new tab is opened inside the existing Chrome window for the scan, and only that tab is closed when the scan finishes — the rest of the session is untouched.

`run_scan()` accepts a new `cdp_url` parameter (default `None`). When set:
- Connects via `p.chromium.connect_over_cdp(cdp_url)`
- Reuses `browser.contexts[0]` (existing profile context with all cookies)
- Opens a new page inside that context, navigates to the target URL, scans, then closes only the page

When `cdp_url` is `None`, existing behaviour (persistent profile launch) is unchanged.

**Auto Chrome debug port setup in `kz_scan.bat`** — when CDP mode is selected, the bat pings `http://localhost:9222/json` via PowerShell to check if Chrome is already in debug mode. If the port is open, it connects directly. If not, it closes Chrome via `taskkill`, relaunches it with `--remote-debugging-port=9222 --no-first-run`, waits for it to start, and holds for user confirmation before handing off to the scanner.

### Fixed

**Box-drawing characters caused garbled output on Windows CMD** — the original bat used Unicode border characters (`╔ ║ ╚ ═`) that rendered as mojibake on CMD's default code page. All decorative characters replaced with plain ASCII (`= - [ ]`).

### Files Changed

| File | Change |
|---|---|
| `kz_scan.bat` | Created; 7-step guided prompt flow; CDP mode step with auto port-check and Chrome relaunch; ASCII-only output for CMD compatibility |
| `kz_scanner.py` | `run_scan()` gains `cdp_url` parameter; CDP branch added (connect, reuse context, open tab, scan, close tab only); CLI gains `--cdp URL` argument passed through to `run_scan()` |
| `CHANGELOG.md` | This entry |

---

## v3.1 — Feature: Playwright Scanner + Proxy Scanner Limitations
**Date:** 29-06-2026
 
### Root Cause (Context)
 
The existing `scanMedia()` function fetched pages through public CORS proxies (`allorigins.win` → `corsproxy.io`) and parsed the returned static HTML for video elements, `og:video` meta tags, and media URLs embedded in `<script>` tags.
 
This approach is architecturally incapable of working for the following categories of target:
 
| Target type | Why the proxy fails |
|---|---|
| LinkedIn | Returns a login wall or heavily stripped JS-rendered shell to unauthenticated requests. The actual video post HTML is only generated after authentication and JS execution. The proxy receives zero usable content. |
| Instagram, Facebook | Same pattern — proxy receives the pre-auth shell. |
| Any SPA / React / Next.js page | Media URLs are injected by JavaScript after initial HTML load. The proxy delivers the empty shell; `<video src>` tags and media fetch calls happen entirely client-side. |
| Proxy availability | Both `allorigins.win` and `corsproxy.io` are public free proxies that go down, get rate-limited, or get blocked by LinkedIn and Meta CDN headers with no notice. |
 
The Python companion script `linkedin_video_posts.py` already solved this correctly: it uses Playwright precisely because a real browser session — with cookies, JavaScript execution, and scroll simulation — is required to see authenticated post content.
 
---
 
### Added
 
**`kz_scanner.py` — Playwright-based local scanner** — a new Python helper script that the user runs locally. Unlike the in-browser proxy scanner, it uses Playwright to launch a persistent browser profile (`kz_browser_profile`) so the user's existing logins and cookies are preserved. Playwright performs real JS execution, authenticated page load, and configurable infinite-scroll simulation before harvesting media URLs.
 
The scanner operates in two output modes, selectable via CLI flag:
 
| Mode | Flag | Behaviour |
|---|---|---|
| JSON file | *(default)* | Writes scan results to `kz_scan_results.json` in the configured output directory |
| HTTP bridge | `--serve` | Starts a local HTTP server on port `7474`; the KZ Downloader HTML page polls it for results |
 
**`run_scan(url, platform, scrolls, delay, output_path, cdp_url, serve)` function** — core scanner entry point. Accepts all scan parameters via keyword arguments. Browser launch, page navigation, scroll loop, and URL harvest are fully encapsulated here.
 
**Platform-aware extraction** — the scanner applies per-platform extraction logic based on a `platform` argument (`yt` / `ig` / `fb` / `li` / `tw` / `gen`). When set to `auto`, platform is inferred from the URL before extraction begins.
 
**LinkedIn-specific extraction** — captures post and activity links from multiple modern LinkedIn DOM patterns:
 
- `/feed/update/` anchors
- `/posts/` anchors
- `urn:li:activity:*` values found in `href`, `data-urn`, `data-id`, and `id` attributes
- `urn:li:activity:*` references found anywhere in the raw page HTML
Activity URNs are normalised into stable `https://www.linkedin.com/feed/update/urn:li:activity:…` URLs so the JSON output contains directly usable platform links.
 
**Configurable scroll behaviour** — scroll step count and inter-step delay are CLI parameters. The scroll loop harvests once before and once after each step so that posts visible at the top and bottom of each viewport position are both captured. LinkedIn pages use a smaller scroll step (`900 px`) to keep posts in view long enough to be registered by the extractor.
 
**`--serve` HTTP bridge mode** — when enabled, after the scan completes the script starts a `http.server`-based local HTTP server at `http://127.0.0.1:7474`. The server exposes a single JSON endpoint (`/results`) that the Scanner tab in KZ Downloader polls. Enables a real-time workflow: run scanner in one window, import results live in the browser without touching a file.
 
**CLI interface** — full argument set:
 
| Argument | Default | Purpose |
|---|---|---|
| `url` | *(required)* | Target page URL |
| `--platform` | `auto` | Platform override (`yt` / `ig` / `fb` / `li` / `tw` / `gen`) |
| `--scrolls` | `10` | Number of scroll steps |
| `--delay` | `2.5` | Seconds between scroll steps |
| `--output` | `kz_scan_results.json` | Output JSON filename |
| `--cdp` | *(none)* | CDP URL to connect to an already-running Chrome instance instead of launching a new window |
| `--serve` | *(off)* | Start HTTP bridge after scan completes |
| `--profile` | `kz_browser_profile` | Persistent browser profile directory name |
 
---
 
### Changed
 
**Scanner tab UI — Playwright workflow** — the Scanner tab in `KZ-Downloader.html` now presents two distinct scanning paths:
 
| Path | When to use | How it works |
|---|---|---|
| **Playwright scanner** (primary) | LinkedIn, Instagram, Facebook, authenticated pages, SPAs | User runs `kz_scanner.py` locally; results imported into the tab via JSON file upload or HTTP bridge poll |
| **Proxy scanner** (secondary) | Simple public pages with static HTML | Existing `allorigins.win` / `corsproxy.io` flow; retained for non-authenticated, non-JS-rendered targets |
 
**Proxy scanner — honest capability display** — the proxy scanner section is now clearly labelled with a limitations notice. The UI explains that it cannot scan authenticated platforms (LinkedIn, Instagram, Facebook), SPA-rendered pages, or any target that requires JS execution. A contextual warning is shown automatically when the user pastes a LinkedIn, Instagram, or Facebook URL into the proxy scanner input.
 
**Playwright import panel** — a new UI section in the Scanner tab guides the user through the Playwright workflow:
 
| Step | UI element |
|---|---|
| 1 | Code block showing the `kz_scanner.py` install and run command |
| 2 | JSON file import button — reads `kz_scan_results.json` and populates the results list |
| 3 | HTTP bridge poll button — fetches `http://127.0.0.1:7474/results` if `--serve` mode is active |
 
Imported results flow into the same `renderScanResults()` / `addScannedItems()` pipeline as proxy scan results — no separate handling path.
 
---
 
### Files Changed
 
| File | Change |
|---|---|
| `kz_scanner.py` | Created — Playwright scanner; persistent profile launch; `channel='chrome'` preference with Chromium fallback; LinkedIn multi-pattern extraction; activity URN normalisation; configurable scroll count and delay; harvest-before-and-after-scroll loop; `--serve` HTTP bridge mode; `--cdp` CDP connect mode; full CLI interface |
| `KZ-Downloader.html` | Scanner tab updated — Playwright workflow panel added (install guide, JSON import, HTTP bridge poll); proxy scanner moved to secondary position with limitations notice; LinkedIn/Instagram/Facebook URL detection triggers contextual proxy-scanner warning; imported results routed through existing `renderScanResults()` and `addScannedItems()` |
| `CHANGELOG.md` | This entry |

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
