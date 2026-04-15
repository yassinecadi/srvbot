"""
modules/system/keyboards.py
─────────────────────────────────────────────
Main menu keyboard.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Users",     callback_data="menu_users"),
            InlineKeyboardButton("⚙️ Services",  callback_data="menu_services"),
        ],
        [
            InlineKeyboardButton("🚀 Speed Test", callback_data="menu_speedtest"),
            InlineKeyboardButton("🔄 Refresh",    callback_data="menu_refresh"),
        ],
    ])
