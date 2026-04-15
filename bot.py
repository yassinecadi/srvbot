#!/usr/bin/env python3
"""
bot.py — srvbot entry point
─────────────────────────────────────────────
Starts the bot via core/runner.py.
All logic lives in modules/ and core/.
─────────────────────────────────────────────
"""

import logging
import config
from core.runner import build_app

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)


def main():
    if config.TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Edit config.py — set TOKEN and ADMIN_ID first.")
        return

    app = build_app()

    import logging
    logging.getLogger(__name__).info("srvbot started.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
