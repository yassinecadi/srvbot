"""
ui/texts.py
─────────────────────────────────────────────
Shared text formatting utilities.
─────────────────────────────────────────────
"""


def section(title: str, lines: list) -> str:
    """Build a formatted section block."""
    return f"*{title}*\n\n" + "\n".join(lines)


def status_icon(active: bool) -> str:
    return "🟢" if active else "🔴"


def active_icon(active: bool) -> str:
    return "✅" if active else "❌"
