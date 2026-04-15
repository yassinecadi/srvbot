"""
modules/speedtest/handler.py
─────────────────────────────────────────────
Speedtest button handler.
Runs speedtest async so the bot stays responsive.
─────────────────────────────────────────────
"""

import os
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from core.auth                      import is_admin
from modules.speedtest.speedtest    import run_speedtest, save_to_config, format_result
from modules.speedtest.keyboards    import kb_speedtest
from modules.speedtest.texts        import build_speedtest_menu_text, build_running_text
import config

# Path to config.py for saving speedtest results
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config.py"
)


async def on_speedtest_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data

    if not is_admin(q.from_user.id):
        await q.edit_message_text("⛔ Unauthorized")
        return

    # Speedtest menu
    if data == "menu_speedtest":
        has_result = config.SPEEDTEST.get("last_run") is not None
        await q.edit_message_text(
            build_speedtest_menu_text(),
            parse_mode="Markdown",
            reply_markup=kb_speedtest(has_result),
            disable_web_page_preview=True,
        )

    # Show last saved result
    elif data == "speedtest_last":
        st = config.SPEEDTEST
        if not st.get("last_run"):
            await q.edit_message_text(
                "⚠️ No result saved yet.",
                reply_markup=kb_speedtest(False)
            )
            return
        await q.edit_message_text(
            format_result(st),
            parse_mode="Markdown",
            reply_markup=kb_speedtest(True),
            disable_web_page_preview=True,
        )

    # Run new speedtest
    elif data == "speedtest_run":
        await _run_speedtest(q, context)


async def _run_speedtest(query, context: ContextTypes.DEFAULT_TYPE):
    """
    Show loading message immediately, run speedtest in background thread,
    update message with result when done.
    """
    await query.edit_message_text(
        build_running_text(),
        parse_mode="Markdown"
    )

    chat_id = query.message.chat_id
    msg_id  = query.message.message_id

    async def _execute():
        try:
            # Run blocking speedtest in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None, run_speedtest
            )
            # Save to disk and update in-memory config
            save_to_config(result, CONFIG_PATH)
            config.SPEEDTEST.update(result)

            text       = format_result(result)
            has_result = True

        except RuntimeError as e:
            text       = f"❌ *Speedtest failed*\n\n`{e}`"
            has_result = False

        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=kb_speedtest(has_result),
                disable_web_page_preview=True,
            )
        except Exception:
            pass

    asyncio.create_task(_execute())
