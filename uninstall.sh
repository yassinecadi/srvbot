#!/bin/bash
# ═══════════════════════════════════════════════════════
#   srvbot — Uninstaller
# ═══════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'
RED='\033[0;31m';   BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}[✔]${RESET} $1"; }
info() { echo -e "${CYAN}[*]${RESET} $1"; }
warn() { echo -e "${CYAN}[!]${RESET} $1"; }
die()  { echo -e "${RED}[✘]${RESET} $1"; exit 1; }

[[ $EUID -ne 0 ]] && die "Run as root."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_DIR="${SCRIPT_DIR}"
BOT_SERVICE="telegram-srvbot"
XRAY_SERVICE="xray"
XRAY_DIR="/root/xray"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║       srvbot — Uninstaller           ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Bot dir  : ${BOT_DIR}"
echo -e "  Xray dir : ${XRAY_DIR}"
echo ""
read -rp "Remove srvbot AND xray? [y/N]: " CONFIRM
[[ "$CONFIRM" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

# ── Stop and remove srvbot service ────────────────────
info "Removing srvbot service..."
systemctl stop    ${BOT_SERVICE} 2>/dev/null || true
systemctl disable ${BOT_SERVICE} 2>/dev/null || true
rm -f /etc/systemd/system/${BOT_SERVICE}.service
ok "srvbot service removed"

# ── Stop and remove xray service ──────────────────────
info "Removing xray service..."
systemctl stop    ${XRAY_SERVICE} 2>/dev/null || true
systemctl disable ${XRAY_SERVICE} 2>/dev/null || true
rm -f /etc/systemd/system/${XRAY_SERVICE}.service
ok "xray service removed"

# ── Remove xray directory ─────────────────────────────
if [[ -d "${XRAY_DIR}" ]]; then
    rm -rf "${XRAY_DIR}"
    ok "Removed ${XRAY_DIR}"
fi

# ── Restore SSH banner config ─────────────────────────
info "Restoring SSH banner config..."
sed -i '/^Banner/d' /etc/ssh/sshd_config
systemctl reload ssh 2>/dev/null || systemctl reload sshd 2>/dev/null || true
ok "SSH banner removed from sshd_config"

# ── Reload systemd ────────────────────────────────────
systemctl daemon-reload
ok "systemd reloaded"

# ── Remove bot directory ──────────────────────────────
echo ""
read -rp "Also delete bot files at ${BOT_DIR}? [y/N]: " DEL_FILES
if [[ "$DEL_FILES" =~ ^[Yy]$ ]]; then
    cd /
    rm -rf "${BOT_DIR}"
    ok "Removed ${BOT_DIR}"
else
    warn "Bot files kept at ${BOT_DIR}"
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║            Uninstall done ✔          ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""
