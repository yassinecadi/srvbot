#!/bin/bash
# ═══════════════════════════════════════════════════════
#   srvbot — GitHub Repository Setup
#   Run this once after unzipping to push to GitHub
# ═══════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'
RED='\033[0;31m';   BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}[✔]${RESET} $1"; }
info() { echo -e "${CYAN}[*]${RESET} $1"; }
die()  { echo -e "${RED}[✘]${RESET} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║     srvbot — GitHub Setup            ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""

# ── Check git ─────────────────────────────
command -v git &>/dev/null || { apt-get install -y -qq git; ok "git installed"; }

# ── Get GitHub info ───────────────────────
read -rp "GitHub username: "       GH_USER
read -rp "Repository name [srvbot]: " GH_REPO
GH_REPO="${GH_REPO:-srvbot}"
read -rp "GitHub email: "          GH_EMAIL
read -rsp "GitHub token (PAT): "   GH_TOKEN
echo ""

# ── Create .gitignore ─────────────────────
cat > .gitignore << 'EOF'
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/

# Bot runtime files
srvbot.log
*.log

# Never commit config with real tokens/passwords
# config.py is included but with placeholder values
EOF
ok ".gitignore created"

# ── Reset config.py to safe placeholder values ───────
info "Resetting config.py to placeholder values for GitHub..."
cat > config.py << 'EOF'
"""
config.py
─────────────────────────────────────────────
Global configuration — edit before first run.
─────────────────────────────────────────────
"""

# ── Telegram ──────────────────────────────
TOKEN    = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 123456789          # int or list: [111, 222]

# ── Server ────────────────────────────────
DOMAIN = "yourdomain.com"
HANDLE = "@yourhandle"
IFACE  = "eth0"

# ── Managed systemd services ──────────────
SERVICES = [
    "wsssh",
    "telegram-srvbot",
]

# ── Speedtest cache ───────────────────────
SPEEDTEST = {
    "download_mbps": None,
    "upload_mbps":   None,
    "ping_ms":       None,
    "isp":           None,
    "server_name":   None,
    "server_url":    None,
    "public_ip":     None,
    "last_run":      None,
}
EOF
ok "config.py reset to placeholder values"

# ── Init git repo ─────────────────────────
info "Initialising git repository..."
git init
git config user.email "$GH_EMAIL"
git config user.name  "$GH_USER"

# ── Create README ─────────────────────────
cat > README.md << EOF
# srvbot — Server Management Telegram Bot

A modular Telegram bot for managing your VPS.

## Features
- 📊 Live server stats (CPU, RAM, disk, bandwidth)
- 👥 SSH user management (add, delete, lock, expiry, password)
- ⚙️ Systemd service management (start, stop, restart)
- 🚀 Speed test with Ookla integration
- ✏️ wsssh banner editing
- ➕ Add Telegram admin IDs live

## Structure
\`\`\`
srvbot/
├── bot.py
├── config.py
├── core/           # auth, runner, utils
├── ui/             # shared keyboards, texts
└── modules/
    ├── system/     # main menu stats
    ├── users/      # SSH user management
    ├── services/   # systemd + wsssh + srvbot sub-modules
    └── speedtest/  # speedtest integration
\`\`\`

## Install
\`\`\`bash
bash <(curl -sL https://raw.githubusercontent.com/${GH_USER}/${GH_REPO}/main/install.sh)
\`\`\`

Or clone and run locally:
\`\`\`bash
git clone https://github.com/${GH_USER}/${GH_REPO}.git && cd ${GH_REPO} && bash install.sh
\`\`\`

## Requirements
- Python 3.11+
- systemd
- Ookla speedtest (for result links): \`apt install speedtest\`
EOF
ok "README.md created"

# ── Commit and push ───────────────────────
info "Committing all files..."
git add .
git commit -m "initial commit — srvbot"

info "Pushing to GitHub..."
git remote add origin "https://${GH_TOKEN}@github.com/${GH_USER}/${GH_REPO}.git"
git branch -M main
git push -u origin main

echo ""
ok "Pushed to https://github.com/${GH_USER}/${GH_REPO}"
echo ""
echo -e "  ${BOLD}To clone on a new VPS:${RESET}"
echo -e "  ${CYAN}git clone https://github.com/${GH_USER}/${GH_REPO}.git${RESET}"
echo -e "  ${CYAN}cd ${GH_REPO} && bash install.sh${RESET}"
echo ""
