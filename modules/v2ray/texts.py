"""
modules/v2ray/texts.py
─────────────────────────────────────────────
Text builders for v2ray management pages.
─────────────────────────────────────────────
"""

import config
from modules.v2ray.v2ray import is_available


def build_v2ray_menu_text(users: list) -> str:
    if not is_available():
        path = getattr(config, "XRAY_CONFIG", "/root/xray/xray.json")
        return (
            "⚡ *V2Ray*\n\n"
            "❌ Xray not installed\\.\n\n"
            f"Expected: `{path}`\n\n"
            "Run on your VPS:\n"
            "`bash /root/bots/srvbot/install\\_xray\\.sh`"
        )
    domain = getattr(config, "DOMAIN", "yourdomain.com")
    tag    = getattr(config, "XRAY_INBOUND_TAG", "xray-vless")
    return (
        f"⚡ *V2Ray — {tag}*\n\n"
        f"Domain : `{domain}`\n"
        f"Users  : `{len(users)}`\n\n"
        "Select a user or add new:"
    )


def build_user_detail_text(user: dict) -> str:
    domain = getattr(config, "DOMAIN", "yourdomain.com")
    uid    = user.get("id",    "N/A")
    name   = user.get("email", "N/A")
    flow   = user.get("flow") or "default"
    link   = (
        f"vless://{uid}@{domain}:8445"
        f"?type=ws&security=tls&path=%2Fkun&host={domain}#{name}"
    )
    return (
        f"👤 *{name}*\n\n"
        f"UUID : `{uid}`\n"
        f"Flow : `{flow}`\n\n"
        f"*Import link:*\n`{link}`"
    )
