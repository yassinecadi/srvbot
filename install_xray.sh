#!/bin/bash
# ═══════════════════════════════════════════════════════
#   srvbot — Xray Installer
#   Installs xray-core for V2Ray/VLESS management.
#   Run after install.sh (needs srvbot already installed).
# ═══════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'
RED='\033[0;31m';   BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}[✔]${RESET} $1"; }
info() { echo -e "${CYAN}[*]${RESET} $1"; }
warn() { echo -e "${CYAN}[!]${RESET} $1"; }
die()  { echo -e "${RED}[✘]${RESET} $1"; exit 1; }

[[ $EUID -ne 0 ]] && die "Run as root."

XRAY_DIR="/root/xray"
XRAY_PORT=8445
XRAY_PATH="/kun"
SERVICE="xray"

# Detect srvbot config location
SRVBOT_CONFIG=""
for p in \
    "/root/bots/srvbot/srvbot/config.py" \
    "/root/bots/srvbot/config.py" \
    "/opt/srvbot/config.py" \
    "/root/srvbot/config.py"; do
    [[ -f "$p" ]] && SRVBOT_CONFIG="$p" && break
done

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║     srvbot — Xray Installer          ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""

read -rp "Domain (e.g. yourdomain.com): " DOMAIN
DOMAIN="${DOMAIN:-yourdomain.com}"

echo ""
info "Install dir : ${XRAY_DIR}"
info "Domain      : ${DOMAIN}"
info "Port        : ${XRAY_PORT} (VLESS+WS+TLS)"
info "Path        : ${XRAY_PATH}"
echo ""

# ── Stop old service ──────────────────────────────────
systemctl stop ${SERVICE} 2>/dev/null || true

# ── Install dir ───────────────────────────────────────
mkdir -p "${XRAY_DIR}"

# ── Download xray binary ──────────────────────────────
info "Downloading xray-core..."
ARCH="64"
[[ "$(uname -m)" == "aarch64" ]] && ARCH="arm64-v8a"
XRAY_URL="https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-${ARCH}.zip"

apt-get install -y -qq unzip curl 2>/dev/null || true
curl -fsSL "${XRAY_URL}" -o /tmp/xray.zip || die "Failed to download xray"
unzip -o /tmp/xray.zip -d /tmp/xray_extract > /dev/null
cp /tmp/xray_extract/xray "${XRAY_DIR}/xray"
chmod +x "${XRAY_DIR}/xray"
rm -rf /tmp/xray.zip /tmp/xray_extract
ok "xray binary installed: $("${XRAY_DIR}/xray" version | head -1)"

# ── TLS certificates ──────────────────────────────────
info "Generating TLS certificate..."
openssl req -x509 -newkey rsa:2048 -nodes \
    -out  "${XRAY_DIR}/server.crt" \
    -keyout "${XRAY_DIR}/server.key" \
    -days 3650 -subj "/CN=${DOMAIN}" 2>/dev/null
ok "Self-signed cert generated (3650 days)"

# ── Write xray.json ───────────────────────────────────
info "Writing xray.json..."
cat > "${XRAY_DIR}/xray.json" << JSONEOF
{
  "log": {
    "loglevel": "warning",
    "error": "${XRAY_DIR}/error.log"
  },
  "inbounds": [
    {
      "tag": "xray-vless",
      "protocol": "vless",
      "listen": "0.0.0.0",
      "port": ${XRAY_PORT},
      "settings": {
        "clients": [],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "certificates": [
            {
              "certificateFile": "${XRAY_DIR}/server.crt",
              "keyFile": "${XRAY_DIR}/server.key"
            }
          ],
          "minVersion": "1.2"
        },
        "wsSettings": {
          "path": "${XRAY_PATH}",
          "host": "${DOMAIN}"
        }
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "settings": {}
    }
  ]
}
JSONEOF
ok "xray.json written"

# ── Systemd service ───────────────────────────────────
info "Installing systemd service..."
cat > /etc/systemd/system/${SERVICE}.service << EOF
[Unit]
Description=Xray — V2Ray/VLESS Service
After=network.target

[Service]
ExecStart=${XRAY_DIR}/xray run -c ${XRAY_DIR}/xray.json
ExecReload=/bin/kill -HUP \$MAINPID
WorkingDirectory=${XRAY_DIR}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now ${SERVICE}
ok "xray service installed and started"

# ── Update srvbot config.py ───────────────────────────
if [[ -n "$SRVBOT_CONFIG" ]]; then
    info "Updating srvbot config.py..."
    python3 - << PYEOF
import re, sys

path = "${SRVBOT_CONFIG}"
try:
    content = open(path).read()

    # Update XRAY_CONFIG path
    content = re.sub(
        r'XRAY_CONFIG\s*=\s*"[^"]*"',
        'XRAY_CONFIG      = "${XRAY_DIR}/xray.json"',
        content
    )

    # Add xray to SERVICES list if missing
    if '"xray"' not in content:
        content = content.replace(
            'SERVICES = [',
            'SERVICES = [\n    "xray",'
        )

    open(path, "w").write(content)
    print("config.py updated")
except Exception as e:
    print(f"WARNING: could not update config.py: {e}", file=sys.stderr)
PYEOF
    ok "srvbot config.py updated"
else
    warn "srvbot config.py not found — set XRAY_CONFIG = \"${XRAY_DIR}/xray.json\" manually"
fi

# ── Verify ────────────────────────────────────────────
sleep 2
if systemctl is-active --quiet ${SERVICE}; then
    ok "xray is RUNNING ✅"
else
    warn "xray may have failed — logs:"
    journalctl -u ${SERVICE} -n 20 --no-pager
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║                  DONE ✔                      ║${RESET}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${RESET}"
echo -e "${BOLD}║${RESET}  Config  : ${XRAY_DIR}/xray.json              ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Logs    : tail -f ${XRAY_DIR}/error.log      ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Status  : systemctl status xray             ${BOLD}║${RESET}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${RESET}"
echo -e "${BOLD}║${RESET}  Client settings:                            ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Protocol : VLESS                            ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Port     : ${XRAY_PORT}                            ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Path     : ${XRAY_PATH}                          ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  TLS      : yes (self-signed)                ${BOLD}║${RESET}"
echo -e "${BOLD}║${RESET}  Network  : ws                               ${BOLD}║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Restart srvbot to apply changes:"
echo -e "  ${CYAN}systemctl restart telegram-srvbot${RESET}"
echo ""
