"""
modules/speedtest/texts.py
─────────────────────────────────────────────
Text builders for the speedtest module.
─────────────────────────────────────────────
"""

import config
from modules.speedtest.speedtest import format_result


def build_speedtest_menu_text() -> str:
    """Show last result or prompt to run."""
    st = config.SPEEDTEST
    if not st.get("last_run"):
        return (
            "🚀 *Speed Test*\n\n"
            "No results saved yet.\n"
            "Press *Run Now* to start."
        )
    return format_result(st)


def build_running_text() -> str:
    return (
        "⏳ *Running speed test...*\n\n"
        "This takes ~30 seconds.\n"
        "Please wait."
    )
