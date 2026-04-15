"""
handlers/menu.py
────────────────────────────────────────────────────────────────
Main menu: /start command and refresh button handler
────────────────────────────────────────────────────────────────
"""

from telegram import Update
from telegram.ext import ContextTypes

from handlers.auth     import check_admin
from handlers.keyboards import kb_main
from handlers.texts    import build_main_text


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start — show main menu."""
    if not await check_admin(update):
        return
    text = await build_main_text()
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=kb_main()
    )


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/cancel — clear state and return to main menu."""
    if not await check_admin(update):
        return
    context.user_data.clear()
    text = await build_main_text()
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=kb_main()
    )


async def handle_menu_refresh(query, context: ContextTypes.DEFAULT_TYPE):
    """Refresh main menu in-place (called from button handler)."""
    context.user_data.clear()
    text = await build_main_text()
    await query.edit_message_text(
        text, parse_mode="Markdown", reply_markup=kb_main()
    )
