"""
modules/services/srvbot/keyboards.py
─────────────────────────────────────────────
Extra keyboard rows for telegram-srvbot detail page.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton


def kb_srvbot_extra() -> list:
    return [
        [InlineKeyboardButton("➕ Add Admin ID", callback_data="svc_bot_addadmin")],
    ]
