"""
modules/system/handler.py
─────────────────────────────────────────────
/start, /cancel, and main menu refresh handler.
─────────────────────────────────────────────
"""

from telegram import Update
from telegram.ext import ContextTypes

from core.auth                import check_admin
from modules.system.keyboards import kb_main
from modules.system.texts     import build_main_text


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start — show main menu."""
    if not await check_admin(update):
        return
    await update.message.reply_text(
        build_main_text(),
        parse_mode="Markdown",
        reply_markup=kb_main()
    )


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/cancel — clear pending action and return to main menu."""
    if not await check_admin(update):
        return
    context.user_data.clear()
    await update.message.reply_text(
        build_main_text(),
        parse_mode="Markdown",
        reply_markup=kb_main()
    )


async def on_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Refresh main menu in-place (called from button router)."""
    context.user_data.clear()
    await update.callback_query.edit_message_text(
        build_main_text(),
        parse_mode="Markdown",
        reply_markup=kb_main()
    )
