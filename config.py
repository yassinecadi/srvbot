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

# ── V2Ray / Xray ──────────────────────────
XRAY_CONFIG      = "/root/xray/xray.json"
XRAY_INBOUND_TAG = "xray-vless"

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
