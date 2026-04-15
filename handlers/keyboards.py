"""
handlers/keyboards.py
────────────────────────────────────────────────────────────────
All InlineKeyboardMarkup builders in one place.
Each function returns a keyboard for a specific screen.
────────────────────────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ── Main menu ─────────────────────────────────────────────────

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Manage Users", callback_data="menu_users"),
            InlineKeyboardButton("⚙️ Services",     callback_data="menu_services"),
        ],
        [
            InlineKeyboardButton("🚀 Speed Test",   callback_data="menu_speedtest"),
            InlineKeyboardButton("🔄 Refresh",      callback_data="menu_refresh"),
        ],
    ])


# ── Navigation ────────────────────────────────────────────────

def kb_back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="menu_refresh")],
    ])


def kb_back_services() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Services", callback_data="menu_services")],
    ])


def kb_back_users() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Users", callback_data="menu_users")],
    ])


# ── Users ─────────────────────────────────────────────────────

def kb_users(user_list: list) -> InlineKeyboardMarkup:
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
    """Actions for a single user."""
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


# ── Services ──────────────────────────────────────────────────

def kb_services(svc_list: list) -> InlineKeyboardMarkup:
    """Services list — one button per service (name + status icon)."""
    rows = []
    for s in svc_list:
        icon = "🟢" if s["active"] else "🔴"
        rows.append([InlineKeyboardButton(
            f"{icon} {s['name']}",
            callback_data=f"svc_detail_{s['name']}"
        )])
    rows.append([InlineKeyboardButton("🔙 Back", callback_data="menu_refresh")])
    return InlineKeyboardMarkup(rows)


def kb_service_detail(name: str) -> InlineKeyboardMarkup:
    """
    Service detail page keyboard.
    Base: Start / Stop / Restart
    Per-service extras:
      wsssh            → Change Banner
      telegram-srvbot  → Add Admin ID
    """
    rows = [
        [
            InlineKeyboardButton("▶️ Start",   callback_data=f"svc_start_{name}"),
            InlineKeyboardButton("⏹ Stop",    callback_data=f"svc_stop_{name}"),
            InlineKeyboardButton("🔄 Restart", callback_data=f"svc_restart_{name}"),
        ],
    ]
    if name == "wsssh":
        rows.append([
            InlineKeyboardButton("✏️ Change Banner", callback_data="svc_wsssh_banner"),
        ])
    elif name == "telegram-srvbot":
        rows.append([
            InlineKeyboardButton("➕ Add Admin ID", callback_data="svc_bot_addadmin"),
        ])
    rows.append([InlineKeyboardButton("🔙 Services", callback_data="menu_services")])
    return InlineKeyboardMarkup(rows)


# ── Speedtest ─────────────────────────────────────────────────

def kb_speedtest(has_result: bool) -> InlineKeyboardMarkup:
    """Speedtest screen keyboard."""
    rows = [
        [InlineKeyboardButton("🚀 Run Now", callback_data="speedtest_run")],
    ]
    if has_result:
        rows.append([
            InlineKeyboardButton("📋 Last Result", callback_data="speedtest_last"),
        ])
    rows.append([InlineKeyboardButton("🔙 Back", callback_data="menu_refresh")])
    return InlineKeyboardMarkup(rows)
