"""
core/runner.py
─────────────────────────────────────────────
Application bootstrap.
Builds the PTB Application and registers all handlers.
Add new handlers here when adding new modules.
─────────────────────────────────────────────
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

import config

log = logging.getLogger(__name__)


def build_app() -> Application:
    """Build and return the configured PTB Application."""

    # Import handlers here to keep bot.py clean
    from modules.system.handler    import cmd_start, cmd_cancel, on_refresh
    from modules.users.handler     import on_users_button, on_users_message
    from modules.services.handler  import on_services_button, on_services_message
    from modules.speedtest.handler import on_speedtest_button

    app = Application.builder().token(config.TOKEN).build()

    # ── Commands ──────────────────────────────────────────────
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("cancel", cmd_cancel))

    # ── Callback buttons ──────────────────────────────────────
    # Order matters — more specific prefixes first
    app.add_handler(CallbackQueryHandler(on_refresh,          pattern="^menu_refresh$"))
    app.add_handler(CallbackQueryHandler(on_users_button,     pattern="^(menu_users|user_|chpass_|expiry_|lock_|unlock_|delete_)"))
    app.add_handler(CallbackQueryHandler(on_services_button,  pattern="^(menu_services|svc_)"))
    app.add_handler(CallbackQueryHandler(on_speedtest_button, pattern="^(menu_speedtest|speedtest_)"))

    # ── Free text messages (multi-step flows) ─────────────────
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        _route_message
    ))

    return app


async def _route_message(update, context):
    """
    Route free-text messages to the correct module handler
    based on context.user_data['action'].
    """
    from modules.users.handler    import on_users_message
    from modules.services.handler import on_services_message

    action = context.user_data.get("action", "")

    user_actions    = {"add_user_name", "add_user_pass", "chpass", "expiry"}
    service_actions = {"wsssh_banner", "bot_addadmin"}

    if action in user_actions:
        await on_users_message(update, context)
    elif action in service_actions:
        await on_services_message(update, context)
    else:
        await update.message.reply_text("Use /start")
