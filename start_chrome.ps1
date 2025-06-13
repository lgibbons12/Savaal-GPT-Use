# ------------------------------------------------------------
# PowerShell script: start_chrome_new_profile.ps1
# Launch Chrome with a brand-new user-data directory each time.
# ------------------------------------------------------------

# 1) Kill any existing Chrome processes
Write-Host "Closing existing Chrome instances..."
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force

# Give Chrome a moment to exit
Start-Sleep -Seconds 2

# 2) Generate a fresh timestamp-based folder name under C:\selenium
$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$baseDir   = "C:\selenium"
$userDataDir = Join-Path $baseDir ("ChromeProfile_$timestamp")

# Create the directory if it doesn’t exist
if (-not (Test-Path $userDataDir)) {
    New-Item -ItemType Directory -Path $userDataDir | Out-Null
    Write-Host "Created new Chrome profile directory at $userDataDir"
}

# 3) Locate Chrome executable
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

$chromePath = $null
foreach ($p in $chromePaths) {
    if (Test-Path $p) {
        $chromePath = $p
        break
    }
}

if ($null -eq $chromePath) {
    Write-Host "Error: Chrome executable not found in default locations."
    Write-Host "Please install Google Chrome or adjust \$chromePaths."
    exit 1
}

# 4) Start Chrome with remote debugging on port 9222, using the new profile
Write-Host "Starting Chrome with remote debugging enabled..."
Write-Host "→ Chrome Path: $chromePath"
Write-Host "→ User-Data-Dir: $userDataDir"

Start-Process $chromePath -ArgumentList @(
    "--remote-debugging-port=9222",
    "--user-data-dir=`"$userDataDir`"",
    "--no-first-run",
    "--no-default-browser-check"
)

Write-Host ""
Write-Host "✅ Chrome launched successfully with a fresh profile!"
Write-Host "1) A new user-data folder was created at:"
Write-Host "   $userDataDir"
Write-Host "2) Please navigate to your llm of choice and log in there."
Write-Host "3) After you’re logged in, run your Python script in a separate terminal to attach via CDP."
