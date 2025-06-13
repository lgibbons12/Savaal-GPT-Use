#!/usr/bin/env bash
# ------------------------------------------------------------
# Script: start_chrome_new_profile.sh
# Launch Chrome/Chromium with a brand-new user-data directory.
# Works on macOS or Linux.
# ------------------------------------------------------------

set -euo pipefail

echo "Closing existing Chrome instances …"
# macOS process name = “Google Chrome”; on Linux it’s usually “chrome” or “chromium”
pkill -x "Google Chrome" 2>/dev/null || true
pkill -x "chrome"        2>/dev/null || true
pkill -x "chromium"      2>/dev/null || true
sleep 2

# Create a fresh user-data dir under ~/selenium
timestamp=$(date +"%Y%m%d_%H%M%S")
baseDir="${HOME}/selenium"
userDataDir="${baseDir}/ChromeProfile_${timestamp}"
mkdir -p "${userDataDir}"
echo "Created new Chrome profile directory at ${userDataDir}"

# Candidate Chrome executables (add/remove paths if yours is elsewhere)
chrome_paths=(
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"       # macOS stable
  "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary" # macOS Canary
  "/usr/bin/google-chrome"           # Debian/Ubuntu stable
  "/usr/bin/google-chrome-stable"    # Arch/Fedora stable
  "/usr/bin/chromium"                # Generic Chromium
  "/usr/bin/chromium-browser"        # Debian/Ubuntu Chromium
)

chromePath=""
for p in "${chrome_paths[@]}"; do
  [[ -x "$p" ]] && { chromePath="$p"; break; }
done

if [[ -z "$chromePath" ]]; then
  echo "❌ Google Chrome/Chromium executable not found."
  echo "   → Install Chrome or update the chrome_paths array."
  exit 1
fi

echo "Starting Chrome with remote debugging enabled …"
echo "→ Chrome Path    : $chromePath"
echo "→ User-Data Dir  : $userDataDir"
"$chromePath" \
  --remote-debugging-port=9222 \
  --user-data-dir="$userDataDir" \
  --no-first-run \
  --no-default-browser-check \
  --window-size=1400,900 &    # wide window keeps ChatGPT’s sidebar visible
echo ""
echo "✅ Chrome launched successfully with a fresh profile!"
echo "1) A new user-data folder was created at:"
echo "   $userDataDir"
echo "2) Log in to your LLM of choice, then run your Python/Playwright script."
