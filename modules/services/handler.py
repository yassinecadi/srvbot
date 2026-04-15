"""
modules/services/handler.py
─────────────────────────────────────────────
Services module: button router + message handler.
─────────────────────────────────────────────
"""

import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from core.auth                       import is_admin
from modules.services.services       import (
    get_all_services, get_service_status,
    start_service, stop_service, restart_service,
)
from modules.services.keyboards      import kb_services_list, kb_service_detail
from modules.services.texts          import (
    build_services_list_text,
    build_service_detail_text,
    build_action_result,
)
from modules.services.wsssh.handler  import handle_wsssh_banner_prompt, on_wsssh_banner
from modules.services.srvbot.handler import handle_addadmin_prompt, on_addadmin


async def on_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data

    if not is_admin(q.from_user.id):
        await q.edit_message_text("⛔ Unauthorized")
        return

    if data == "menu_services":
        svc_list = get_all_services()
        await q.edit_message_text(
            build_services_list_text(),
            parse_mode="Markdown",
            reply_markup=kb_services_list(svc_list)
        )

    elif data.startswith("svc_detail_"):
        name = data[11:]
        s    = get_service_status(name)
        await q.edit_message_text(
            build_service_detail_text(s),
            parse_mode="Markdown",
            reply_markup=kb_service_detail(name)
        )

    elif data.startswith("svc_start_"):
        name    = data[10:]
        ok, msg = start_service(name)
        await asyncio.sleep(2)
        s = get_service_status(name)
        await q.edit_message_text(
            build_action_result(name, ok, msg) + build_service_detail_text(s),
            parse_mode="Markdown",
            reply_markup=kb_service_detail(name)
        )

    elif data.startswith("svc_stop_"):
        name    = data[9:]
        ok, msg = stop_service(name)
        await asyncio.sleep(2)
        s = get_service_status(name)
        await q.edit_message_text(
            build_action_result(name, ok, msg) + build_service_detail_text(s),
            parse_mode="Markdown",
            reply_markup=kb_service_detail(name)
        )

    elif data.startswith("svc_restart_"):
        name = data[12:]
        if name == "telegram-srvbot":
            await q.edit_message_text(
                f"🔄 Restarting `{name}`...\n\nBot will be back in ~5 seconds.",
                parse_mode="Markdown"
            )
            restart_service(name)
            return
        await q.edit_message_text(
            f"🔄 Restarting `{name}`...",
            parse_mode="Markdown"
        )
        ok, msg = restart_service(name)
        await asyncio.sleep(4)
        s = get_service_status(name)
        await q.edit_message_text(
            build_action_result(name, ok, msg) + build_service_detail_text(s),
            parse_mode="Markdown",
            reply_markup=kb_service_detail(name)
        )

    elif data == "svc_wsssh_banner":
        await handle_wsssh_banner_prompt(q, context)

    elif data == "svc_bot_addadmin":
        await handle_addadmin_prompt(q, context)


async def on_services_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("action")
    if action == "wsssh_banner":
        await on_wsssh_banner(update.message, context)
    elif action == "bot_addadmin":
        await on_addadmin(update.message, context)
