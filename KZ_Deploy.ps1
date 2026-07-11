# ============================================================
#  KZ Downloader — Deploy (Local Wins)
#  WARNING: Overwrites remote with local state.
#  Place this file in the repo root.
# ============================================================

$REPO_PATH   = $PSScriptRoot
$BRANCH      = 'main'
$REMOTE_URL  = 'https://github.com/jass666/KZ-Downloader'

Write-Host ""
Write-Host " ====================================================="
Write-Host "  KZ Downloader  |  Deploy to GitHub"
Write-Host " ====================================================="
Write-Host ""
Write-Host " [INFO]  Repo  : $REPO_PATH"
Write-Host " [INFO]  Remote: $REMOTE_URL"
Write-Host " [INFO]  Branch: $BRANCH"
Write-Host ""
Write-Host " Press ENTER to start deployment, or type anything and press ENTER to abort."
$confirm = Read-Host " >"
if ($confirm -ne "") {
    Write-Host ""
    Write-Host " [INFO]  Aborted. Nothing was changed."
    Write-Host ""
    Read-Host " Press Enter to exit"
    exit 0
}
Write-Host ""

# -- STEP 1: Verify repo -------------------------------------------------------
Write-Host " [STEP 1/5]  Verifying repo path..."
if (-not (Test-Path $REPO_PATH)) {
    Write-Host " [ERROR] Repo path not found: $REPO_PATH"
    Write-Host "         Expected: $REPO_PATH"
    Read-Host " Press Enter to exit"
    exit 1
}
Set-Location $REPO_PATH
Write-Host " [OK]    Repo found at $REPO_PATH"
Write-Host ""

# -- STEP 2: Verify git --------------------------------------------------------
Write-Host " [STEP 2/5]  Verifying Git repository..."
git rev-parse --is-inside-work-tree 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host " [ERROR] Not a Git repository."
    Write-Host "         Run: git init && git remote add origin $REMOTE_URL"
    Read-Host " Press Enter to exit"
    exit 1
}
Write-Host " [OK]    Git repo confirmed."
$localHash = git log -1 --pretty=format:%h
$localMsg  = git log -1 --pretty=format:%s
Write-Host " [INFO]  Local HEAD: $localHash - $localMsg"
Write-Host ""

# -- STEP 3: Show uncommitted changes ------------------------------------------
Write-Host " [STEP 3/5]  Checking for uncommitted changes..."
Write-Host ""
$changed   = git status --short
$fileCount = 0
foreach ($line in $changed) {
    Write-Host " [FILE]  $line"
    $fileCount++
}
Write-Host ""

# -- STEP 4: Stage + Commit ----------------------------------------------------
Write-Host " [STEP 4/5]  Staging & committing..."
Write-Host ""

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if ($fileCount -gt 0) {
    Write-Host " [INFO]  Found $fileCount changed file(s) -- staging all."
    git add -A
    if ($LASTEXITCODE -ne 0) {
        Write-Host " [ERROR] git add failed."
        Read-Host " Press Enter to exit"
        exit 1
    }
} else {
    Write-Host " [INFO]  No file changes detected. Writing deploy stamp to force new SHA."
}

# Always write deploy stamp so the remote always sees a new commit SHA
Set-Content -Path ".deploy_stamp" -Value $timestamp -Encoding UTF8
git add .deploy_stamp
if ($LASTEXITCODE -ne 0) {
    Write-Host " [ERROR] Could not stage .deploy_stamp"
    Read-Host " Press Enter to exit"
    exit 1
}

$date      = Get-Date -Format "yyyy-MM-dd HH:mm"
$commitMsg = "Deploy $date"

Write-Host " [GIT]   Committing: $commitMsg"
git commit -m $commitMsg
if ($LASTEXITCODE -ne 0) {
    Write-Host " [ERROR] Commit failed."
    Read-Host " Press Enter to exit"
    exit 1
}

$newHash = git log -1 --pretty=format:%h
$newMsg  = git log -1 --pretty=format:%s
Write-Host " [OK]    New HEAD: $newHash - $newMsg"
Write-Host ""

# -- STEP 5: Force push --------------------------------------------------------
Write-Host " [STEP 5/5]  Force pushing to origin/$BRANCH..."
git push origin $BRANCH --force
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host " [ERROR] Force push failed. Possible reasons:"
    Write-Host "         - No internet connection"
    Write-Host "         - Authentication not configured (set up Git credential manager)"
    Write-Host "         - Branch is protected on remote"
    Write-Host ""
    Write-Host "         Remote: $REMOTE_URL"
    Read-Host " Press Enter to exit"
    exit 1
}

$finalHash = git log -1 --pretty=format:%h
Write-Host " [OK]    GitHub is now at: $finalHash"
Write-Host ""

Write-Host " ====================================================="
Write-Host "  SUCCESS  |  Push complete"
Write-Host "  Commit  : $finalHash"
Write-Host "  Branch  : $BRANCH"
Write-Host "  Repo    : $REMOTE_URL"
Write-Host " ====================================================="
Write-Host ""
Read-Host " Press Enter to exit"
