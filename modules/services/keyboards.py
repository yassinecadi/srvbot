"""
modules/services/keyboards.py
─────────────────────────────────────────────
Keyboards for services list and detail pages.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ui.texts import status_icon


def kb_services_list(svc_list: list) -> InlineKeyboardMarkup:
    """One button per service — name + status icon."""
    rows = []
    for s in svc_list:
        icon = status_icon(s["active"])
        rows.append([InlineKeyboardButton(
            f"{icon} {s['name']}",
            callback_data=f"svc_detail_{s['name']}"
        )])
    rows.append([InlineKeyboardButton("🔙 Back", callback_data="menu_refresh")])
    return InlineKeyboardMarkup(rows)


def kb_service_detail(name: str) -> InlineKeyboardMarkup:
    """
    Detail page keyboard.
    telegram-srvbot: Restart only (can't respond after Stop).
    Other services: Start / Stop / Restart.
    """
    if name == "telegram-srvbot":
        rows = [
            [InlineKeyboardButton("🔄 Restart", callback_data=f"svc_restart_{name}")],
        ]
    else:
        rows = [
            [
                InlineKeyboardButton("▶️ Start",   callback_data=f"svc_start_{name}"),
                InlineKeyboardButton("⏹ Stop",    callback_data=f"svc_stop_{name}"),
                InlineKeyboardButton("🔄 Restart", callback_data=f"svc_restart_{name}"),
            ],
        ]

    # Inject per-service custom buttons
    if name == "wsssh":
        from modules.services.wsssh.keyboards import kb_wsssh_extra
        rows += kb_wsssh_extra()
    elif name == "telegram-srvbot":
        from modules.services.srvbot.keyboards import kb_srvbot_extra
        rows += kb_srvbot_extra()

    rows.append([InlineKeyboardButton("🔙 Services", callback_data="menu_services")])
    return InlineKeyboardMarkup(rows)
