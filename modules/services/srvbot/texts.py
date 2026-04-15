"""
modules/services/srvbot/texts.py
─────────────────────────────────────────────
Text builders for srvbot self-management.
─────────────────────────────────────────────
"""

import config


def build_addadmin_prompt_text() -> str:
    return (
        "➕ *Add Admin ID*\n\n"
        f"Current admin(s): `{config.ADMIN_ID}`\n\n"
        "Send new Telegram user ID:\n\n"
        "/cancel to go back"
    )
