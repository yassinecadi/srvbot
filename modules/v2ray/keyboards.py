"""
modules/v2ray/keyboards.py
─────────────────────────────────────────────
Keyboards for v2ray user management pages.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def kb_v2ray_menu(users: list) -> InlineKeyboardMarkup:
    rows = []
    for u in users:
        rows.append([InlineKeyboardButton(
            f"👤 {u['email']}",
            callback_data=f"v2_user_{u['email']}"
        )])
    rows.append([InlineKeyboardButton("➕ Add User",  callback_data="v2_add")])
    rows.append([InlineKeyboardButton("🔙 Back",      callback_data="menu_refresh")])
    return InlineKeyboardMarkup(rows)


def kb_v2ray_user(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Delete", callback_data=f"v2_del_{username}")],
        [InlineKeyboardButton("🔙 V2Ray",  callback_data="menu_v2ray")],
    ])


def kb_back_v2ray() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 V2Ray", callback_data="menu_v2ray")],
    ])
