# KZ Downloader

A browser-based GUI for generating [yt-dlp](https://github.com/yt-dlp/yt-dlp) commands — built for downloading videos from any social media profile, channel, or page without touching the command line directly.

**Live:** [kzdownloader.pages.dev](https://kzdownloader.pages.dev/)

Project created and maintained by **Jaswant Kanojia**.

**Version:** v2.7 · **Date:** 28-06-2026

---

## What It Does

Open the app at [kzdownloader.pages.dev](https://kzdownloader.pages.dev/). Paste social profile URLs, configure options, and the app generates ready-to-run yt-dlp commands.

| Tab | Purpose |
|---|---|
| **Profiles** | Add any social profile or video URL. Platform detected automatically. Generated command appears inline — no tab switch needed. |
| **History** | Searchable log of every URL queued and every command generated. Export, import, and re-queue entries. |
| **Presets** | Manage saved channel shortcuts. Add, edit, delete, export, and import presets. Seeded with built-in Tata presets on first load. |
| **Options** | Format/quality, output folder, save location mode, filename template, date filter, extra flags. |
| **Setup Guide** | Step-by-step install instructions for Python, FFmpeg, and yt-dlp on Windows, macOS, Linux, Android (Termux), and iOS. |

---

## Supported Platforms

| Platform | Profile / Channel | Single video | Notes |
|---|---|---|---|
| YouTube | ✅ | ✅ | Full channel scrape supported |
| Instagram | ✅ | ✅ | May require cookies for private accounts |
| Facebook | ✅ | ✅ | Public pages only without cookies |
| LinkedIn | ✅ | ✅ | Requires cookies from a logged-in Chrome session |
| Twitter / X | ✅ | ✅ | Rate limits apply |
| Generic URLs | — | ✅ | Any site yt-dlp supports |

---

## Quick Start

### 1. Check Python & install dependencies (one-time)

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

**Step 2 — Install yt-dlp:**
```cmd
python -m pip install yt-dlp
```

> Need FFmpeg too? The **Setup Guide** tab inside the app walks through the full FFmpeg install and PATH setup.

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

# Then install Python, FFmpeg, and yt-dlp in one go
brew install python ffmpeg yt-dlp
```

> **Apple Silicon (M1/M2/M3) users:** If `brew` isn't recognised after install, add it to your PATH:
> ```bash
> echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
> source ~/.zprofile
> ```

**Step 2 — Install yt-dlp** (skip if you ran `brew install yt-dlp` above):
```bash
python -m pip install yt-dlp
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

**Step 2 — Install FFmpeg and yt-dlp:**
```bash
sudo apt install ffmpeg -y
python -m pip install yt-dlp
```

---

#### 🤖 Android (Termux)

1. Install [Termux from F-Droid](https://f-droid.org/packages/com.termux/) (not the Play Store version)
2. Install dependencies:
```bash
pkg install python ffmpeg -y
```
3. Install yt-dlp:
```bash
python -m pip install yt-dlp
```
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

Go to [kzdownloader.pages.dev](https://kzdownloader.pages.dev/) **or** open `KZ-Downloader.html` locally in Chrome, Firefox, or Edge.

### 3. Generate commands

1. **Profiles** → paste a URL or click a preset → **+ Add**
2. **Options** → set format, output folder, save location mode, filename template, flags
3. The generated command appears inline in the **Profiles** tab — copy it, download the `.bat`, or click **Launch in CMD**
4. **History** → find any past URL or command, re-queue or export it

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

In **Options**, a toggle below the output folder field controls how the save path is handled:

| Mode | Behaviour |
|---|---|
| **Fixed folder** (default) | The output folder field value is used as-is — `-o "path/template"` appears in the generated command |
| **Ask every time** | The `-o` flag is omitted; yt-dlp downloads to its working directory. The output folder field is dimmed and disabled |

---

## LinkedIn

LinkedIn requires an authenticated browser session. Before running LinkedIn commands:

1. Log in to LinkedIn in **Google Chrome**
2. Enable **Cookies from Chrome** in the Options → Extra flags section
3. Run the generated command immediately after — cookies expire quickly

---

## Local Storage

All data stays in your browser's `localStorage`, scoped to the file path (or origin when using the hosted version). Nothing leaves your machine.

| Key | Contents |
|---|---|
| `kz-downloader-profiles` | Profile queue — restored automatically on every open |
| `kz-downloader-opts` | Options: format, output folder, save mode, filename template, date filter |
| `kz-history` | Link and command history — up to 500 entries, newest first |
| `kz-presets` | User-managed presets — seeded with built-in Tata presets on first load |
| `kz-device` | Selected device (`windows` / `mac` / `linux` / `android` / `ios`) |

To back up history, use **Export selected** in the History tab. To wipe everything, use **⊘ Clear saved** in the Options tab or **Clear all history** in the History tab.

---

## File Structure

```
KZ-Downloader/
├── KZ-Downloader.html   # Main app — open this in a browser
├── README.md            # This file
└── CHANGELOG.md         # Full version history
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

| Version | Date | Summary |
|---|---|---|
| **v2.7** | 28-06-2026 | Save location mode toggle (Fixed / Ask every time); History and Options tabs swapped positions |
| **v2.6** | 28-06-2026 | Presets tab with full CRUD, export, import; Output block moved inline to Profiles tab; all commands updated to `python -m yt_dlp` |
| **v2.5** | 28-06-2026 | Device selector (Windows / Mac / Linux / Android / iOS) with auto-detection and per-device UI |
| **v2.4** | 28-06-2026 | Android / Termux support; Share button; mobile fixes (clipboard fallback, touch targets, input zoom) |
| **v2.3** | 27-06-2026 | Button and tab contrast fixes across both themes |
| **v2.2** | 27-06-2026 | History tab; responsive code blocks; Linux setup guide expanded |
| **v2.1** | 27-06-2026 | Persistent localStorage for profiles and options |
| **v2.0** | 27-06-2026 | Rebuilt as KZ Downloader (universal); platform auto-detection; Setup Guide tab |
| **v1.0** | 26-06-2026 | Initial release — yt-dlp Tata Downloader |

---

*Project created and maintained by Jaswant Kanojia — LDE Bajaj, LDE Royal Enfield & Swift Trucks LLP, Lucknow.*
