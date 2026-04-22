#!/bin/bash
# ═══════════════════════════════════════════════════════
#   srvbot — Installer
#   Installs in-place from the script's own directory.
#
#   One-liner install from GitHub:
#     bash <(curl -sL https://raw.githubusercontent.com/yassinecadi/srvbot/main/install.sh)
# ═══════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'
RED='\033[0;31m';   BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}[✔]${RESET} $1"; }
info() { echo -e "${CYAN}[*]${RESET} $1"; }
warn() { echo -e "${CYAN}[!]${RESET} $1"; }
die()  { echo -e "${RED}[✘]${RESET} $1"; exit 1; }

[[ $EUID -ne 0 ]] && die "Run as root."

# When run via bash <(curl ...), BASH_SOURCE[0] is /dev/fd/N — not a real path.
# In that case, clone the repo and re-exec from the real directory.
if [[ ! -f "${BASH_SOURCE[0]}" ]]; then
    CLONE_DIR="${1:-/opt/srvbot}"
    info "Running from pipe/process substitution — cloning repo to ${CLONE_DIR}..."
    apt-get install -y -qq git 2>/dev/null || true
    [[ -d "$CLONE_DIR/.git" ]] || git clone https://github.com/yassinecadi/srvbot.git "$CLONE_DIR"
    exec bash "$CLONE_DIR/install.sh"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_DIR="${SCRIPT_DIR}"
SERVICE="telegram-srvbot"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║         srvbot — Installer           ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""

# ── User input ────────────────────────────
read -rp "Telegram Bot Token: "                TOKEN
read -rp "Your Telegram Admin ID: "            ADMIN_ID
read -rp "Domain (e.g. yourdomain.com): "          DOMAIN
read -rp "Your Telegram handle (e.g. @username): "  HANDLE
read -rp "Network interface [eth0]: "               IFACE

DOMAIN="${DOMAIN:-yourdomain.com}"
HANDLE="${HANDLE:-@admin}"
IFACE="${IFACE:-eth0}"

echo ""
info "Installing at : ${BOT_DIR}"
info "Domain        : ${DOMAIN}"
echo ""

# ── Stop old service ──────────────────────
pkill -f "bot.py" 2>/dev/null || true
systemctl stop    ${SERVICE} 2>/dev/null || true
systemctl disable ${SERVICE} 2>/dev/null || true
sleep 1

# ── System dependencies ───────────────────
info "Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git curl
ok "System dependencies ready"

# ── Ookla speedtest (for result URLs) ─────
info "Installing Ookla speedtest..."
if ! command -v speedtest &>/dev/null; then
    curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash -s -- --os-codename "$(. /etc/os-release && echo $VERSION_CODENAME)" &>/dev/null
    apt-get install -y -qq speedtest 2>/dev/null && ok "Ookla speedtest installed" || warn "Ookla install failed — will use speedtest-cli fallback"
else
    ok "Ookla speedtest already installed"
fi

# ── Python venv ───────────────────────────
info "Setting up Python venv..."
python3 -m venv "${BOT_DIR}/venv"
"${BOT_DIR}/venv/bin/pip" install --upgrade pip -q
"${BOT_DIR}/venv/bin/pip" install python-telegram-bot speedtest-cli -q
ok "venv ready"

# ── Patch config.py ───────────────────────
info "Writing config values..."
sed -i "s|YOUR_BOT_TOKEN_HERE|${TOKEN}|"                   "${BOT_DIR}/config.py"
sed -i "s|ADMIN_ID = 123456789|ADMIN_ID = ${ADMIN_ID}|"    "${BOT_DIR}/config.py"
sed -i "s|yourdomain.com|${DOMAIN}|"                       "${BOT_DIR}/config.py"
sed -i "s|@yourhandle|${HANDLE}|"                          "${BOT_DIR}/config.py"
sed -i "s|IFACE  = \"eth0\"|IFACE  = \"${IFACE}\"|"        "${BOT_DIR}/config.py"
ok "config.py patched"

# ── SSH banner ────────────────────────────
info "Configuring SSH banner..."
sed -i '/^Banner/d' /etc/ssh/sshd_config
echo "Banner ${BOT_DIR}/bannerssh" >> /etc/ssh/sshd_config
systemctl restart ssh 2>/dev/null || systemctl restart sshd 2>/dev/null || true
ok "SSH banner set to ${BOT_DIR}/bannerssh"

# ── Systemd service ───────────────────────
info "Installing systemd service..."
cat > /etc/systemd/system/${SERVICE}.service << EOF
[Unit]
Description=srvbot — Server Management Bot
After=network.target

[Service]
ExecStart=${BOT_DIR}/venv/bin/python ${BOT_DIR}/bot.py
WorkingDirectory=${BOT_DIR}
Restart=always
RestartSec=5
StandardOutput=append:${BOT_DIR}/srvbot.log
StandardError=append:${BOT_DIR}/srvbot.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now ${SERVICE}
ok "Service installed and started"

# ── Verify ────────────────────────────────
sleep 2
if systemctl is-active --quiet ${SERVICE}; then
    ok "srvbot is RUNNING ✅"
else
    echo ""
    echo "Service failed — logs:"
    journalctl -u ${SERVICE} -n 30 --no-pager
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║                  DONE ✔                      ║${RESET}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${RESET}"
echo -e "${BOLD}║${RESET}  Logs    : tail -f ${BOT_DIR}/srvbot.log     ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Status  : systemctl status ${SERVICE}       ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  GitHub  : bash github_setup.sh              ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Send /start to your bot                     ${BOLD}║${RESET}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${RESET}"
echo -e "${BOLD}║${RESET}  Re-install one-liner:                       ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  bash <(curl -sL https://raw.githubusercontent${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}    .com/yassinecadi/srvbot/main/install.sh)  ${BOLD}║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
echo ""
