"""
modules/speedtest/speedtest.py
─────────────────────────────────────────────
Run speedtest, parse result, save to config.py.
Tries Ookla binary first (provides result URL),
falls back to speedtest-cli pip package.
─────────────────────────────────────────────
"""

import re
import json
import subprocess
from datetime import datetime


# ── Run ───────────────────────────────────

def run_speedtest() -> dict:
    """
    Run speedtest. Tries Ookla first (has result URL),
    then speedtest-cli. Raises RuntimeError if none available.
    """
    result = _try_ookla()
    if result:
        return result

    result = _try_speedtest_cli()
    if result:
        return result

    raise RuntimeError(
        "No speedtest tool found.\n"
        "Install Ookla: curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && apt install speedtest\n"
        "Or pip: pip install speedtest-cli"
    )


def _try_ookla() -> dict | None:
    """Ookla official binary — JSON output with result URL."""
    try:
        r = subprocess.run(
            ["speedtest", "--format=json",
             "--accept-license", "--accept-gdpr"],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode != 0:
            return None
        d = json.loads(r.stdout)
        return {
            "download_mbps": round(d["download"]["bandwidth"] * 8 / 1e6, 2),
            "upload_mbps":   round(d["upload"]["bandwidth"]   * 8 / 1e6, 2),
            "ping_ms":       round(d["ping"]["latency"], 1),
            "isp":           d.get("isp", "Unknown"),
            "server_name":   d.get("server", {}).get("name", "Unknown"),
            "server_url":    d.get("result", {}).get("url", ""),
            "public_ip":     d.get("interface", {}).get("externalIp", ""),
            "last_run":      datetime.now().isoformat(timespec="seconds"),
        }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def _try_speedtest_cli() -> dict | None:
    """Python speedtest-cli — no result URL available."""
    try:
        r = subprocess.run(
            ["speedtest-cli", "--simple"],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode != 0:
            return None
        ping = dl = ul = None
        for line in r.stdout.splitlines():
            if line.startswith("Ping:"):
                ping = float(re.search(r"[\d.]+", line).group())
            elif line.startswith("Download:"):
                dl   = float(re.search(r"[\d.]+", line).group())
            elif line.startswith("Upload:"):
                ul   = float(re.search(r"[\d.]+", line).group())
        if dl is None:
            return None
        return {
            "download_mbps": dl,
            "upload_mbps":   ul,
            "ping_ms":       ping,
            "isp":           None,
            "server_name":   None,
            "server_url":    None,   # not available in speedtest-cli
            "public_ip":     None,
            "last_run":      datetime.now().isoformat(timespec="seconds"),
        }
    except FileNotFoundError:
        return None


# ── Save to config.py ─────────────────────

def save_to_config(result: dict, config_path: str) -> bool:
    """Write speedtest result into SPEEDTEST dict in config.py."""
    try:
        with open(config_path) as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            replaced = False
            for key, value in result.items():
                if f'"{key}"' in line and ":" in line:
                    indent  = len(line) - len(line.lstrip())
                    val_str = "None" if value is None else (
                        f'"{value}"' if isinstance(value, str) else str(value)
                    )
                    new_lines.append(f'{" " * indent}"{key}": {val_str},\n')
                    replaced = True
                    break
            if not replaced:
                new_lines.append(line)

        with open(config_path, "w") as f:
            f.writelines(new_lines)
        return True
    except Exception:
        return False


# ── Format result ─────────────────────────

def format_result(result: dict) -> str:
    """Format speedtest result as Telegram Markdown message."""
    dl   = result.get("download_mbps", "?")
    ul   = result.get("upload_mbps",   "?")
    ping = result.get("ping_ms",       "?")
    isp  = result.get("isp")         or "—"
    srv  = result.get("server_name")  or "—"
    url  = result.get("server_url")   or ""
    ip   = result.get("public_ip")    or "—"
    ts   = result.get("last_run")     or ""

    lines = [
        "🚀 *Speed Test Result*\n",
        f"⬇️ Download : `{dl} Mbps`",
        f"⬆️ Upload   : `{ul} Mbps`",
        f"📡 Ping     : `{ping} ms`",
        f"🌐 Public IP: `{ip}`",
        f"🏢 ISP      : `{isp}`",
        f"🖥 Server   : `{srv}`",
    ]
    if url:
        lines.append(f"🔗 [View full result]({url})")
    else:
        lines.append("🔗 Result link: install Ookla speedtest for links")
    if ts:
        lines.append(f"\n🕐 `{ts}`")

    return "\n".join(lines)
