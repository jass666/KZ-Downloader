@echo off
setlocal EnableDelayedExpansion
title KZ Scanner - Guided Launch
set "ROOT=%~dp0"

:BANNER
cls
echo.
echo  ==========================================================
echo   KZ Downloader -- Playwright Media Scanner
echo   Guided Launcher
echo  ==========================================================
echo.

set "ADVANCED_FLOW=0"
set "CDP_HTTP=http://127.0.0.1:9222"
set "CDP_FLAG="
set "PROFILE_DIR=!ROOT!kz_browser_profile"
set "CDP_LABEL=Saved-login scanner window"
set "SCROLLS=10"
set "DELAY=2.5"
set "PLATFORM_FLAG="
set "SERVE_FLAG="
set "JSON_DIR=!ROOT!JSONs"
set "OUT_NAME=kz_scan_results.json"
if not exist "!JSON_DIR!" mkdir "!JSON_DIR!"
set "OUT_FILE=!JSON_DIR!\!OUT_NAME!"

echo  Choose launcher mode
echo.
echo    1  --  Defaults
echo             Saved-login scanner window, 10 scrolls, 2.5s delay,
echo             auto platform,
echo             no HTTP bridge, default JSON filename.
echo    2  --  Advanced
echo             Show all 7 setup options.
echo.
set /p "LAUNCH_CHOICE=  Choice (1-2): "

if "!LAUNCH_CHOICE!"=="2" goto ASK_MODE
if not "!LAUNCH_CHOICE!"=="1" echo  [!] Invalid choice. Using defaults.

:DEFAULT_FLOW
set "ADVANCED_FLOW=0"
echo.
goto ASK_URL


:: --- STEP 1 : BROWSER MODE -----------------------------------
:ASK_MODE
set "ADVANCED_FLOW=1"
echo  [1/7]  Browser mode
echo.
echo    1  --  Saved-login scanner window  [recommended]
echo             Opens a separate browser window using kz_browser_profile.
echo             Keeps login cookies between scans.
echo    2  --  Clean scanner window
echo             Opens a separate browser window using kz_clean_profile.
echo    S  --  Skip this option, keep default
echo    A  --  Skip all remaining options, keep defaults
echo.
set /p "MODE_CHOICE=  Choice (1-2/S/A): "

set "CDP_HTTP=http://127.0.0.1:9222"
set "CDP_FLAG="
set "PROFILE_DIR=!ROOT!kz_browser_profile"
set "CDP_LABEL=Saved-login scanner window"

if "!MODE_CHOICE!"=="1" ( set "PROFILE_DIR=!ROOT!kz_browser_profile" & set "CDP_LABEL=Saved-login scanner window" & goto MODE_DONE )
if "!MODE_CHOICE!"=="2" ( set "PROFILE_DIR=!ROOT!kz_clean_profile" & set "CDP_LABEL=Clean scanner window" & goto MODE_DONE )
if /i "!MODE_CHOICE!"=="S" goto MODE_DONE
if /i "!MODE_CHOICE!"=="A" goto ASK_URL
echo  [!] Invalid choice. Defaulting to saved-login scanner window.
set "PROFILE_DIR=!ROOT!kz_browser_profile"
set "CDP_LABEL=Saved-login scanner window"

:MODE_DONE
echo.


:: --- STEP 2 : URL --------------------------------------------
:ASK_URL
echo  [2/7]  Enter the page URL to scan
echo         (LinkedIn, Instagram, Facebook, YouTube, etc.)
echo.
set "URL="
set /p "URL=  URL: "
if "!URL!"=="" (
    echo.
    echo  [!] URL cannot be empty. Please try again.
    echo.
    goto ASK_URL
)
echo.
if "!ADVANCED_FLOW!"=="0" goto BUILD_ARGS


:: --- STEP 3 : SCROLLS ----------------------------------------
:ASK_SCROLLS
echo  [3/7]  How many scroll steps?
echo.
echo    1  --  Default :  10 scrolls
echo    2  --  Quick   :  20 scrolls
echo    3  --  Normal  :  60 scrolls
echo    4  --  Deep    : 120 scrolls
echo    5  --  Custom  : Enter your own number
echo    S  --  Skip this option, keep default
echo    A  --  Skip all remaining options, keep defaults
echo.
set /p "SCROLL_CHOICE=  Choice (1-5/S/A): "

if "!SCROLL_CHOICE!"=="1" ( set "SCROLLS=10"  & goto SCROLLS_DONE )
if "!SCROLL_CHOICE!"=="2" ( set "SCROLLS=20"  & goto SCROLLS_DONE )
if "!SCROLL_CHOICE!"=="3" ( set "SCROLLS=60"  & goto SCROLLS_DONE )
if "!SCROLL_CHOICE!"=="4" ( set "SCROLLS=120" & goto SCROLLS_DONE )
if "!SCROLL_CHOICE!"=="5" (
    echo.
    set /p "SCROLLS=  Enter number of scrolls: "
    if "!SCROLLS!"=="" set "SCROLLS=10"
    goto SCROLLS_DONE
)
if /i "!SCROLL_CHOICE!"=="S" goto SCROLLS_DONE
if /i "!SCROLL_CHOICE!"=="A" goto BUILD_ARGS
echo  [!] Invalid choice. Using default (10).
set "SCROLLS=10"

:SCROLLS_DONE
echo.


:: --- STEP 4 : DELAY ------------------------------------------
:ASK_DELAY
echo  [4/7]  Delay between scrolls (seconds)?
echo.
echo    1  --  Fast    : 1.5s
echo    2  --  Normal  : 2.5s  [default]
echo    3  --  Slow    : 4.0s
echo    4  --  Custom  : Enter your own value
echo    S  --  Skip this option, keep default
echo    A  --  Skip all remaining options, keep defaults
echo.
set /p "DELAY_CHOICE=  Choice (1-4/S/A): "

if "!DELAY_CHOICE!"=="1" ( set "DELAY=1.5" & goto DELAY_DONE )
if "!DELAY_CHOICE!"=="2" ( set "DELAY=2.5" & goto DELAY_DONE )
if "!DELAY_CHOICE!"=="3" ( set "DELAY=4.0" & goto DELAY_DONE )
if "!DELAY_CHOICE!"=="4" (
    echo.
    set /p "DELAY=  Enter delay in seconds (e.g. 3.0): "
    if "!DELAY!"=="" set "DELAY=2.5"
    goto DELAY_DONE
)
if /i "!DELAY_CHOICE!"=="S" goto DELAY_DONE
if /i "!DELAY_CHOICE!"=="A" goto BUILD_ARGS
echo  [!] Invalid choice. Using default (2.5s).
set "DELAY=2.5"

:DELAY_DONE
echo.


:: --- STEP 5 : PLATFORM ---------------------------------------
:ASK_PLATFORM
echo  [5/7]  Platform override (optional)
echo         Auto-detects from URL -- skip unless wrong.
echo.
echo    1  --  Auto-detect from URL  [recommended]
echo    2  --  YouTube    (yt)
echo    3  --  Instagram  (ig)
echo    4  --  Facebook   (fb)
echo    5  --  LinkedIn   (li)
echo    6  --  Twitter/X  (tw)
echo    7  --  Generic    (gen)
echo    S  --  Skip this option, keep default
echo    A  --  Skip all remaining options, keep defaults
echo.
set /p "PLATFORM_CHOICE=  Choice (1-7/S/A): "

set "PLATFORM_FLAG="
if "!PLATFORM_CHOICE!"=="1" ( set "PLATFORM_FLAG="   & goto PLATFORM_DONE )
if "!PLATFORM_CHOICE!"=="2" ( set "PLATFORM_FLAG=yt"  & goto PLATFORM_DONE )
if "!PLATFORM_CHOICE!"=="3" ( set "PLATFORM_FLAG=ig"  & goto PLATFORM_DONE )
if "!PLATFORM_CHOICE!"=="4" ( set "PLATFORM_FLAG=fb"  & goto PLATFORM_DONE )
if "!PLATFORM_CHOICE!"=="5" ( set "PLATFORM_FLAG=li"  & goto PLATFORM_DONE )
if "!PLATFORM_CHOICE!"=="6" ( set "PLATFORM_FLAG=tw"  & goto PLATFORM_DONE )
if "!PLATFORM_CHOICE!"=="7" ( set "PLATFORM_FLAG=gen" & goto PLATFORM_DONE )
if /i "!PLATFORM_CHOICE!"=="S" goto PLATFORM_DONE
if /i "!PLATFORM_CHOICE!"=="A" goto BUILD_ARGS
echo  [!] Invalid choice. Using auto-detect.
set "PLATFORM_FLAG="

:PLATFORM_DONE
echo.


:: --- STEP 6 : SERVE ------------------------------------------
:ASK_SERVE
echo  [6/7]  Start local HTTP bridge after scan?
echo         Lets KZ Downloader import live via Scanner tab.
echo.
echo    1  --  Yes, start bridge on port 7474
echo    2  --  No, just save JSON file  [default]
echo    S  --  Skip this option, keep default
echo    A  --  Skip all remaining options, keep defaults
echo.
set /p "SERVE_INPUT=  Choice (1-2/S/A): "

set "SERVE_FLAG="
if "!SERVE_INPUT!"=="1" set "SERVE_FLAG=--serve --port 7474"
if /i "!SERVE_INPUT!"=="A" goto BUILD_ARGS
echo.


:: --- STEP 7 : OUTPUT FILE ------------------------------------
:ASK_OUT
set "JSON_DIR=!ROOT!JSONs"

echo  [7/7]  Output file name
echo         Saved to: !JSON_DIR!\
echo.
echo    1  --  kz_scan_results.json  [default]
echo    2  --  Custom filename
echo    S  --  Skip this option, keep default
echo    A  --  Skip all remaining options, keep defaults
echo.
set /p "OUT_CHOICE=  Choice (1-2/S/A): "

set "OUT_NAME=kz_scan_results.json"
if "!OUT_CHOICE!"=="2" (
    echo.
    set /p "OUT_NAME=  Enter filename (include .json): "
    if "!OUT_NAME!"=="" set "OUT_NAME=kz_scan_results.json"
)
if /i "!OUT_CHOICE!"=="A" goto BUILD_ARGS

if not exist "!JSON_DIR!" mkdir "!JSON_DIR!"
set "OUT_FILE=!JSON_DIR!\!OUT_NAME!"
echo.


:: --- BUILD ARGS ----------------------------------------------
:BUILD_ARGS
set "ARGS=--scrolls !SCROLLS! --delay !DELAY! --out "!OUT_FILE!""
if not "!CDP_FLAG!"==""      set "ARGS=!ARGS! !CDP_FLAG!"
if not "!PLATFORM_FLAG!"=="" set "ARGS=!ARGS! --platform !PLATFORM_FLAG!"
if not "!SERVE_FLAG!"==""    set "ARGS=!ARGS! !SERVE_FLAG!"


:: --- CONFIRM SCREEN ------------------------------------------
cls
echo.
echo  ==========================================================
echo   Ready to Scan
echo  ==========================================================
echo.
echo   Browser  : !CDP_LABEL!
echo   URL      : !URL!
echo   Scrolls  : !SCROLLS!
echo   Delay    : !DELAY!s
if "!PLATFORM_FLAG!"=="" (
    echo   Platform : auto-detect
) else (
    echo   Platform : !PLATFORM_FLAG!
)
echo   Output   : !OUT_FILE!
if not "!SERVE_FLAG!"=="" echo   Bridge   : http://127.0.0.1:7474/results
echo.
echo  ----------------------------------------------------------
echo.
echo   Press ENTER to start
echo   Type R + ENTER to go back and change options
echo   Type Q + ENTER to quit
echo.
set /p "CONFIRM=  Your choice: "

if /i "!CONFIRM!"=="R" goto BANNER
if /i "!CONFIRM!"=="Q" (
    echo.
    echo  Exited. No scan was run.
    echo.
    pause
    exit /b 0
)

set "CDP_FLAG="
goto RUN_SCAN


:: --- CDP SETUP -----------------------------------------------
if "!CDP_FLAG!"=="" goto RUN_SCAN

cls
echo.
echo  ==========================================================
echo   Setting up Chrome for CDP connection...
echo  ==========================================================
echo.

:: Check if port 9222 is already responding
echo   Checking port 9222...
powershell -NoProfile -Command ^
  "try { Invoke-WebRequest -Uri 'http://127.0.0.1:9222/json/version' -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1

if !errorlevel! equ 0 (
    for /f "usebackq delims=" %%u in (`powershell -NoProfile -Command "try { $v = Invoke-RestMethod -Uri 'http://127.0.0.1:9222/json/version' -TimeoutSec 2; if ($v.webSocketDebuggerUrl) { Write-Output $v.webSocketDebuggerUrl; exit 0 }; exit 1 } catch { exit 1 }"`) do set "CDP_WS=%%u"
    if not "!CDP_WS!"=="" set "CDP_FLAG=--cdp !CDP_WS!"
    echo   [OK] Chrome is already on port 9222. Connecting directly.
    echo.
    goto RUN_SCAN
)

echo   Port 9222 not open. Launching a separate debug Chrome profile.
echo.

:: Find Chrome
set "CHROME_EXE="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe"       set "CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

:: Also check LocalAppData (user install)
if "!CHROME_EXE!"=="" (
    if exist "!LOCALAPPDATA!\Google\Chrome\Application\chrome.exe" (
        set "CHROME_EXE=!LOCALAPPDATA!\Google\Chrome\Application\chrome.exe"
    )
)

if "!CHROME_EXE!"=="" (
    echo   [!] Chrome not found at any standard path.
    echo.
    echo       Please launch Chrome manually with this flag:
    echo       --remote-debugging-port=9222
    echo.
    echo       Then run the scanner again and choose skip below.
    echo.
    pause
    goto RUN_SCAN
)

echo   Chrome found: !CHROME_EXE!
echo.

set "CDP_PROFILE=!ROOT!chrome_cdp_profile"
if not exist "!CDP_PROFILE!" mkdir "!CDP_PROFILE!"

echo   Launching Chrome with --remote-debugging-port=9222...
start "" "!CHROME_EXE!" --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir="!CDP_PROFILE!" --no-first-run --no-default-browser-check
echo.

:: Retry loop — wait up to 15 seconds for port to open
echo   Waiting for Chrome to be ready (up to 15s)...
set "CHROME_READY=0"
for /L %%i in (1,1,15) do (
    if "!CHROME_READY!"=="0" (
        timeout /t 1 /nobreak >nul
        powershell -NoProfile -Command ^
          "try { Invoke-WebRequest -Uri 'http://127.0.0.1:9222/json/version' -UseBasicParsing -TimeoutSec 1 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
        if !errorlevel! equ 0 (
            set "CHROME_READY=1"
            echo   [OK] Chrome is ready on port 9222 (%%i s^).
        )
    )
)

if "!CHROME_READY!"=="0" (
    echo.
    echo   [!] Chrome did not open port 9222 in 15 seconds.
    echo       This can happen if Chrome opened as a background process.
    echo       Try: close Chrome manually, then run the scanner again.
    echo.
    pause
    exit /b 1
)

set "CDP_WS="
for /f "usebackq delims=" %%u in (`powershell -NoProfile -Command "try { $v = Invoke-RestMethod -Uri 'http://127.0.0.1:9222/json/version' -TimeoutSec 2; if ($v.webSocketDebuggerUrl) { Write-Output $v.webSocketDebuggerUrl; exit 0 }; exit 1 } catch { exit 1 }"`) do set "CDP_WS=%%u"
if not "!CDP_WS!"=="" (
    set "CDP_FLAG=--cdp !CDP_WS!"
) else (
    echo.
    echo   [!] Chrome responded on port 9222 but did not expose a WebSocket URL.
    echo.
    pause
    exit /b 1
)

echo.
echo   Navigate to the target page in Chrome, log in if needed,
echo   then press ENTER here when ready...
pause >nul


:: --- RUN -----------------------------------------------------
:RUN_SCAN
cls
echo.
echo  ==========================================================
echo   Scanning in progress...
echo  ==========================================================
echo.
if not "!CDP_FLAG!"=="" (
    echo   Connected to your existing Chrome.
    echo   A new tab will open in that window.
    echo   Navigate to the target page, then press ENTER
    echo   in this terminal to begin scrolling.
) else (
    echo   A new browser window will open. Log in if prompted,
    echo   then press ENTER in this terminal to begin scrolling.
)
echo.
echo  ----------------------------------------------------------
echo.

set "PLATFORM_ARG="
if not "!PLATFORM_FLAG!"=="" set "PLATFORM_ARG=--platform !PLATFORM_FLAG!"

python kz_scanner.py "!URL!" --scrolls !SCROLLS! --delay !DELAY! --out "!OUT_FILE!" --profile "!PROFILE_DIR!" !PLATFORM_ARG! !SERVE_FLAG!

echo.
echo  ----------------------------------------------------------
echo.
echo  [OK] Scan finished!
echo  [OK] Results saved to: !OUT_FILE!
echo.
if not "!SERVE_FLAG!"=="" (
    echo  [OK] Local bridge running at http://127.0.0.1:7474/results
    echo       Open KZ Downloader - Scanner tab - Import from local scanner
    echo       Press Ctrl+C here when done importing.
    echo.
)
pause
exit /b 0
