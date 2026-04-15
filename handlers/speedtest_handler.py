"""
handlers/speedtest_handler.py
────────────────────────────────────────────────────────────────
Speedtest menu: show last result, run new test (async),
                save results to config.py, update main menu.
────────────────────────────────────────────────────────────────
"""

import asyncio
import os

from telegram.ext import ContextTypes

from handlers.keyboards import kb_speedtest, kb_main
from handlers.texts     import (
    build_speedtest_menu_text,
    build_speedtest_running_text,
    build_main_text,
)
from helpers import speedtest as sp
import config


CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py")


# ── Show speedtest screen ─────────────────────────────────────

async def handle_speedtest_menu(query):
    """Show speedtest menu with last result if available."""
    has_result = config.SPEEDTEST.get("last_run") is not None
    await query.edit_message_text(
        build_speedtest_menu_text(),
        parse_mode="Markdown",
        reply_markup=kb_speedtest(has_result),
        disable_web_page_preview=True,
    )


async def handle_speedtest_last(query):
    """Show last saved speedtest result."""
    st = config.SPEEDTEST
    if not st.get("last_run"):
        await query.edit_message_text(
            "⚠️ No speedtest result saved yet.",
            reply_markup=kb_speedtest(False)
        )
        return
    await query.edit_message_text(
        sp.format_result(st),
        parse_mode="Markdown",
        reply_markup=kb_speedtest(True),
        disable_web_page_preview=True,
    )


# ── Run speedtest ─────────────────────────────────────────────

async def handle_speedtest_run(query, context: ContextTypes.DEFAULT_TYPE):
    """
    Show 'running' message, run speedtest in background thread,
    then update message with results and save to config.
    """
    # Show loading message immediately
    await query.edit_message_text(
        build_speedtest_running_text(),
        parse_mode="Markdown"
    )

    chat_id = query.message.chat_id
    msg_id  = query.message.message_id

    async def _run_and_update():
        try:
            # Run blocking speedtest in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None, sp.run_speedtest
            )

            # Save to config.py on disk
            sp.save_to_config(result, CONFIG_PATH)

            # Update in-memory config so main menu shows updated values
            config.SPEEDTEST.update(result)

            # Format result text
            text = sp.format_result(result)
            has_result = True

        except RuntimeError as e:
            text       = f"❌ Speedtest failed:\n\n`{e}`"
            has_result = False

        # Edit the loading message with the result
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

    # Schedule in background so we don't block the handler
    asyncio.create_task(_run_and_update())
