"""
modules/services/wsssh/handler.py
─────────────────────────────────────────────
wsssh sub-module handler: banner change flow.
─────────────────────────────────────────────
"""

from telegram.ext import ContextTypes

from ui.keyboards                      import kb_back_services
from modules.services.wsssh.wsssh      import set_banner
from modules.services.wsssh.texts      import build_banner_prompt_text


async def handle_wsssh_banner_prompt(query, context: ContextTypes.DEFAULT_TYPE):
    """Show prompt asking for new banner text."""
    context.user_data["action"] = "wsssh_banner"
    await query.edit_message_text(
        build_banner_prompt_text(),
        parse_mode="Markdown",
        reply_markup=kb_back_services()
    )


async def on_wsssh_banner(message, context: ContextTypes.DEFAULT_TYPE):
    """Receive new banner text, apply and confirm."""
    ok, msg = set_banner(message.text.strip())
    context.user_data.clear()
    await message.reply_text(f"{'✅' if ok else '❌'} {msg}")
