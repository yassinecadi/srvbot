"""
handlers/services_handler.py
────────────────────────────────────────────────────────────────
Services menu: list, detail, start/stop/restart,
               wsssh banner, bot admin management
────────────────────────────────────────────────────────────────
"""

import config
from telegram.ext import ContextTypes

from handlers.keyboards import kb_services, kb_service_detail, kb_back_services
from handlers.texts     import (
    build_services_list_text,
    build_service_detail_text,
    build_service_action_text,
)
from helpers import services


# ── Button handlers ───────────────────────────────────────────

async def handle_services_list(query):
    """Show list of all managed services."""
    svc_list = services.get_all_services()
    await query.edit_message_text(
        build_services_list_text(),
        parse_mode="Markdown",
        reply_markup=kb_services(svc_list)
    )


async def handle_service_detail(query, name: str):
    """Show detail page for one service."""
    s = services.get_service_status(name)
    await query.edit_message_text(
        build_service_detail_text(s),
        parse_mode="Markdown",
        reply_markup=kb_service_detail(name)
    )


async def handle_service_start(query, name: str):
    ok, msg = services.start_service(name)
    s = services.get_service_status(name)
    await query.edit_message_text(
        build_service_action_text(name, ok, msg) + build_service_detail_text(s),
        parse_mode="Markdown",
        reply_markup=kb_service_detail(name)
    )


async def handle_service_stop(query, name: str):
    ok, msg = services.stop_service(name)
    s = services.get_service_status(name)
    await query.edit_message_text(
        build_service_action_text(name, ok, msg) + build_service_detail_text(s),
        parse_mode="Markdown",
        reply_markup=kb_service_detail(name)
    )


async def handle_service_restart(query, name: str):
    ok, msg = services.restart_service(name)
    s = services.get_service_status(name)
    await query.edit_message_text(
        build_service_action_text(name, ok, msg) + build_service_detail_text(s),
        parse_mode="Markdown",
        reply_markup=kb_service_detail(name)
    )


# ── wsssh: change banner prompt ───────────────────────────────

async def handle_wsssh_banner_prompt(query, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["action"] = "wsssh_banner"
    current = services.get_wsssh_banner()
    await query.edit_message_text(
        f"✏️ *Change WebSocket Banner*\n\nCurrent:\n`{current}`\n\nSend new banner text:\n\n/cancel to go back",
        parse_mode="Markdown",
        reply_markup=kb_back_services()
    )


async def on_wsssh_banner(message, context: ContextTypes.DEFAULT_TYPE):
    """Receive new banner text and apply."""
    ok, msg = services.set_wsssh_banner(message.text.strip())
    context.user_data.clear()
    await message.reply_text(f"{'✅' if ok else '❌'} {msg}")


# ── telegram-srvbot: add admin prompt ────────────────────────

async def handle_addadmin_prompt(query, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["action"] = "bot_addadmin"
    await query.edit_message_text(
        f"➕ *Add Admin ID*\n\nCurrent admin: `{config.ADMIN_ID}`\n\nSend new Telegram user ID:\n\n/cancel to go back",
        parse_mode="Markdown",
        reply_markup=kb_back_services()
    )


async def on_addadmin(message, context: ContextTypes.DEFAULT_TYPE):
    """Receive new admin ID and save to config."""
    try:
        new_id  = int(message.text.strip())
        ok, msg = services.add_bot_admin(new_id)
        context.user_data.clear()
        await message.reply_text(f"{'✅' if ok else '❌'} {msg}")
    except ValueError:
        await message.reply_text("❌ Send a valid Telegram user ID (numbers only)")
