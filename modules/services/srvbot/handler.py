"""
modules/services/srvbot/handler.py
─────────────────────────────────────────────
srvbot sub-module handler: add admin flow.
─────────────────────────────────────────────
"""

from telegram.ext import ContextTypes

from ui.keyboards                        import kb_back_services
from modules.services.srvbot.srvbot      import add_admin
from modules.services.srvbot.texts       import build_addadmin_prompt_text


async def handle_addadmin_prompt(query, context: ContextTypes.DEFAULT_TYPE):
    """Show prompt asking for new admin Telegram ID."""
    context.user_data["action"] = "bot_addadmin"
    await query.edit_message_text(
        build_addadmin_prompt_text(),
        parse_mode="Markdown",
        reply_markup=kb_back_services()
    )


async def on_addadmin(message, context: ContextTypes.DEFAULT_TYPE):
    """Receive new admin ID, validate, save and confirm."""
    try:
        new_id  = int(message.text.strip())
        ok, msg = add_admin(new_id)
        context.user_data.clear()
        await message.reply_text(f"{'✅' if ok else '❌'} {msg}")
    except ValueError:
        await message.reply_text("❌ Send a valid Telegram user ID (numbers only)")
