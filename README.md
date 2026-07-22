# KZ Downloader

A browser-based GUI for generating [yt-dlp](https://github.com/yt-dlp/yt-dlp) commands — built for downloading videos from any social media profile, channel, or page without touching the command line directly.

**Live:** [kzdownloader.pages.dev](https://kzdownloader.pages.dev/)

Project created and maintained by **Jaswant Kanojia**.

**Version:** v4.3 · **Date:** 22-07-2026

---

## What it is

Open the app at [kzdownloader.pages.dev](https://kzdownloader.pages.dev/). Paste social profile URLs, configure options, and the app generates ready-to-run yt-dlp commands.

| Tab | Purpose |
|---|---|
| **Profiles** | Add any social profile or video URL. Platform detected automatically. Generated command appears inline — no tab switch needed. Includes a **☁️ Run in Colab** option for running commands with no local Python/FFmpeg install. |
| **History** | Searchable log of every URL queued and every command generated. Export, import, and re-queue entries. |
| **Presets** | Manage saved channel shortcuts. Add, edit, delete, export, and import presets. Seeded with built-in Tata presets on first load. |
| **Scanner** | Scan any page for media. Quick Scan uses a CORS proxy for public pages; Playwright mode runs a local Python script for login-gated pages (LinkedIn, Instagram, Facebook); Live Bridge imports results directly from a running scanner over HTTP. |
| **Settings** | Format/quality, output folder, save location mode, filename template, date filter, extra flags. |
| **Setup Guide** | Step-by-step install instructions for Python, FFmpeg, and yt-dlp on Windows, macOS, Linux, Android (Termux), and iOS. |

---

## Supported Platforms

| Platform | Profile / Channel | Single video | Notes |
|---|---|---|---|
| YouTube | ✅ | ✅ | Full channel scrape supported |
| Instagram | ✅ | ✅ | May require cookies for private accounts |
| Facebook | ✅ | ✅ | Public pages only without cookies |
| LinkedIn | ✅ | ✅ | Requires cookies or Playwright scanner with saved login |
| Twitter / X | ✅ | ✅ | Rate limits apply |
| TikTok | — | ✅ | Single video via yt-dlp |
| Generic URLs | — | ✅ | Any site yt-dlp supports |

---

## Quick Start

### 1. Check Python & install dependencies (one-time)

> **Quick option — already have Python?** Download `requirements.txt` directly and run:
> ```
> pip install -r requirements.txt
> playwright install chromium
> ```
> 📥 [Download requirements.txt from MediaFire](https://www.mediafire.com/file/rs8rde8jdrt2p8z/requirements.txt/file)
>
> This installs both `yt-dlp` and `playwright` in one shot. FFmpeg still needs a separate system install — see your OS section below.

---

#### 🪟 Windows

**Step 1 — Check if Python is installed:**
```cmd
python --version
```

✅ **If you see a version number** (e.g. `Python 3.11.4`) → Python is ready, skip to Step 2.

❌ **If you get an error or `Python was not found`** → Install Python first:

1. Go to [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Download the latest **Python 3.x** installer
3. Run the installer — **check "Add Python to PATH"** before clicking Install
4. Once installed, close and reopen your terminal, then re-run `python --version` to confirm

**Step 2 — Install FFmpeg:**

```cmd
winget install ffmpeg
```

> No `winget`? Download manually from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html). The **Setup Guide** tab inside the app walks through the full PATH setup.

**Step 3 — Install Python dependencies:**
```cmd
pip install -r requirements.txt
playwright install chromium
```

---

#### 🍎 macOS

**Step 1 — Check if Python is installed:**
```bash
python3 --version
```

✅ **If you see a version number** (e.g. `Python 3.12.0`) → Python is ready, skip to Step 2.

❌ **If you get `command not found`** → Install Python via Homebrew:

```bash
# Install Homebrew first (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Python and FFmpeg
brew install python ffmpeg
```

> **Apple Silicon (M1/M2/M3) users:** If `brew` isn't recognised after install, add it to your PATH:
> ```bash
> echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
> source ~/.zprofile
> ```

**Step 2 — Install Python dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

---

#### 🐧 Linux (Debian / Ubuntu)

**Step 1 — Check if Python is installed:**
```bash
python3 --version
```

✅ **If you see a version number** → Python is ready, skip to Step 2.

❌ **If you get `command not found`** → Install Python:

```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

> For **Fedora**: `sudo dnf install python3 python3-pip -y`
> For **Arch**: `sudo pacman -S python python-pip`

**Step 2 — Install FFmpeg and Python dependencies:**
```bash
sudo apt install ffmpeg -y
pip install -r requirements.txt
playwright install chromium
```

---

#### 🤖 Android (Termux)

1. Install [Termux from F-Droid](https://f-droid.org/packages/com.termux/) (not the Play Store version)
2. Install dependencies:
```bash
pkg install python ffmpeg -y
```
3. Install Python dependencies:
```bash
pip install -r requirements.txt
```
> Playwright (included in `requirements.txt`) won't run on Android — the Playwright Scanner tab is not available on Termux. yt-dlp will install and work normally.
4. Grant storage access:
```bash
termux-setup-storage
```
5. Use the **Copy** or **Share** button in the app to paste the generated command into Termux.

> For a full walkthrough, see the **Setup Guide → Android** tab in the app.

---

#### 📱 iOS

yt-dlp cannot run natively on iOS. Recommended options:

- **SSH into a remote server** using an app like [Termius](https://apps.apple.com/app/termius-ssh-client/id549039908) or iSSH — run yt-dlp on the server, transfer files back.
- **a-Shell** — limited workaround; audio-only downloads with no FFmpeg support.

> See the **Setup Guide → iOS** tab in the app for full details.

---

### 2. Open the app

Go to [kzdownloader.pages.dev](https://kzdownloader.pages.dev/) in Chrome, Firefox, or Edge.

### 3. Generate commands

1. **Profiles** → paste a URL or click a preset → **+ Add**
2. **Settings** → set format, output folder, save location mode, filename template, flags
3. The generated command appears inline in the **Profiles** tab — copy it, download the `.bat`, click **Launch in CMD**, or click **☁️ Run in Colab** to run it in the cloud with no install at all
4. **History** → find any past URL or command, re-queue or export it

---

## Playwright Scanner

For login-gated pages (LinkedIn, Instagram, Facebook) the built-in proxy scanner cannot access authenticated content. Use the **Scanner → Playwright** tab instead.

### Prerequisites (one-time)

```cmd
pip install -r requirements.txt
playwright install chromium
```

Download `kz_scanner.py` from the Scanner tab and save it anywhere on your machine.

### Running a scan

1. Open the **Scanner → Playwright** tab
2. Paste the target URL — the platform is auto-detected
3. Set your output folder, KZ Downloader folder path, and scroll count
4. Copy the generated command and run it in any CMD window
5. When the scan finishes, drag the output JSON into the import zone

**Output files** are named automatically: `platform-dd-mm-yy-hh-mm.json` (e.g. `linkedin-29-06-26-14-03.json`).

**KZ Downloader folder** — fill this in once and the generated command will include `cd /d "path"` so it runs from any CMD window regardless of where it is opened.

Alternatively, use **Live Bridge** mode: run `kz_scanner.py --serve` and the app polls the local HTTP server directly — no file step needed.

---

## Run in Colab (No Install Needed)

Don't want to install Python, FFmpeg, or anything else on a device? Click **☁️ Run in Colab** next to the generated command.

**What it does:**
1. Copies the generated command to your clipboard.
2. Opens a companion Google Colab notebook (`KZ_Colab_Downloader.ipynb`) in a new browser tab.
3. Paste the command into the notebook's single input cell and run it — it installs yt-dlp/ffmpeg automatically the first time in a session (skipped on later runs), then downloads.
4. Each finished file pops up as its own browser download automatically, one at a time.

**Best for:** Android (skip the Termux setup entirely), iOS, Chromebooks, or sharing a link with someone non-technical who just needs a file.

**Doesn't work for:** LinkedIn or private/login-gated Instagram/Facebook content — Colab has no way to log in interactively the way a real browser session can. Use **Scanner → Playwright** for those instead.

**Nothing is saved to Google Drive as output** — despite the notebook file itself living on Drive, downloaded videos only ever sit in a temporary folder inside the Colab session until they land in your browser's downloads.

**Hosting note:** the notebook is hosted on Google Drive (shared as *Anyone with the link → Viewer*) rather than deployed through Cloudflare Pages, since it isn't part of the static site. To update it, re-upload the new version to the same Drive file (keeping the same file ID) rather than running the deploy script — the link in `index.html` only needs to change if the file ID itself changes.

---

## Device Selector

The header includes a device selector — choose your OS and the app adapts automatically:

| Device | Effect |
|---|---|
| 🖥 Windows | Batch script and Launch in CMD available; default output path set to `D:/KZ Downloads` |
| 🍎 Mac | Batch and Launch in CMD hidden; terminal label shows "Terminal" |
| 🐧 Linux | Same as Mac |
| 🤖 Android | Share button shown; terminal label shows "Termux"; default path set to `/sdcard/Download/KZ Downloads` |
| 📱 iOS | Download file hidden; iOS-specific guidance shown |

The selected device is auto-detected from your browser on first load and saved to `localStorage`.

---

## Save Location Mode

In **Settings**, a toggle below the output folder field controls how the save path is handled:

| Mode | Behaviour |
|---|---|
| **Fixed folder** (default) | The output folder field value is used as-is — `-o "path/template"` appears in the generated command |
| **Ask every time** | The `-o` flag is omitted; yt-dlp downloads to its working directory. The output folder field is dimmed and disabled |

---

## LinkedIn

LinkedIn requires an authenticated browser session. Two options:

**Option A — Cookies (Quick Scan / yt-dlp):**
1. Log in to LinkedIn in **Google Chrome**
2. Enable **Cookies from Chrome** in Settings → Extra flags
3. Run the generated command immediately after — cookies expire quickly

**Option B — Playwright Scanner (recommended):**
1. Run `kz_scanner.py` via the Scanner tab — it opens a persistent browser profile
2. Log in once; the session is reused on every subsequent scan
3. Import the JSON results into the app

---

## Local Storage

All data stays in your browser's `localStorage`, scoped to the file path (or origin when using the hosted version). Nothing leaves your machine.

| Key | Contents |
|---|---|
| `kz-downloader-profiles` | Profile queue — restored automatically on every open |
| `kz-downloader-opts` | Settings: format, output folder, save mode, filename template, date filter |
| `kz-history` | Link and command history — up to 500 entries, newest first |
| `kz-presets` | User-managed presets — seeded with built-in Tata presets on first load |
| `kz-device` | Selected device (`windows` / `mac` / `linux` / `android` / `ios`) |
| `kz_pw_persist_v1` | Playwright scanner: output folder, KZ folder path, scroll count, platform selection |

To back up history, use **Export selected** in the History tab. To wipe everything, use **⊘ Clear saved** in the Settings tab or **Clear all history** in the History tab.

---

## Deployment

The browser app itself is static, but the scanner helpers use Python locally.

1. Edit `index.html`, `kz_scanner.py`, or helper scripts as needed.
2. Open the app locally or on the hosted Pages URL and test the affected tab.
3. Run `KZ_Deploy_Launcher.bat` or `KZ_Deploy.ps1` when the local folder should become the GitHub branch state.
4. Cloudflare Pages serves the static app; local scanner files remain user-run tools.

`KZ_Deploy.ps1` is a local-wins deploy helper. Use it only when local files are the intended source of truth.

---

## File Structure

```
KZ-Downloader/
├── kz_scanner.py                 # Playwright scanner script (download from Scanner tab)
├── kz_scan.bat                   # Guided launcher for kz_scanner.py (Windows)
├── requirements.txt              # Python dependencies (yt-dlp, playwright)
├── KZ_Colab_Downloader.ipynb     # Colab notebook for no-install cloud downloads (hosted on Google Drive, not deployed via Cloudflare Pages)
├── README.md                     # This file
└── CHANGELOG.md                  # Full version history
```

---

## yt-dlp References

- [yt-dlp GitHub — docs and releases](https://github.com/yt-dlp/yt-dlp)
- [Format selection](https://github.com/yt-dlp/yt-dlp#format-selection)
- [Output template variables](https://github.com/yt-dlp/yt-dlp#output-template)
- [Cookies and authentication](https://github.com/yt-dlp/yt-dlp#cookies)

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

*Project created and maintained by Jaswant Kanojia — LDE Bajaj, LDE Royal Enfield & Swift Trucks LLP, Lucknow.*
