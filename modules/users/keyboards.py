"""
modules/users/keyboards.py
─────────────────────────────────────────────
All keyboards for the users module.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def kb_users_list(user_list: list) -> InlineKeyboardMarkup:
    """One button per user + Add + Back."""
    rows = []
    for u in user_list:
        icon = "✅" if u["active"] else "❌"
        rows.append([InlineKeyboardButton(
            f"{icon} {u['username']}",
            callback_data=f"user_{u['username']}"
        )])
    rows.append([InlineKeyboardButton("➕ Add User", callback_data="user_add")])
    rows.append([InlineKeyboardButton("🔙 Back",     callback_data="menu_refresh")])
    return InlineKeyboardMarkup(rows)


def kb_user_actions(username: str, active: bool) -> InlineKeyboardMarkup:
    """Action buttons for a single user."""
    toggle_lbl = "🔒 Lock"          if active else "🔓 Unlock"
    toggle_cb  = f"lock_{username}" if active else f"unlock_{username}"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔑 Change Pass", callback_data=f"chpass_{username}"),
            InlineKeyboardButton("⏰ Set Expiry",  callback_data=f"expiry_{username}"),
        ],
        [
            InlineKeyboardButton(toggle_lbl,       callback_data=toggle_cb),
            InlineKeyboardButton("🗑 Delete",       callback_data=f"delete_{username}"),
        ],
        [InlineKeyboardButton("🔙 Users",           callback_data="menu_users")],
    ])
