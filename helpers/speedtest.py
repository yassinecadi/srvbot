"""
helpers/speedtest.py
────────────────────────────────────────────────────────────────
Run speedtest-cli, parse results, save to config.py SPEEDTEST dict
────────────────────────────────────────────────────────────────
"""

import subprocess
import json
import re
import os
from datetime import datetime


# ── Run speedtest ─────────────────────────────────────────────

def run_speedtest() -> dict:
    """
    Run speedtest-cli and return parsed results.
    Tries JSON mode first (speedtest-cli >= 0.3.4),
    falls back to text parsing.
    Returns dict with all result fields or raises RuntimeError.
    """
    # Try official Ookla speedtest binary first
    result = _try_ookla()
    if result:
        return result

    # Fall back to speedtest-cli (pip)
    result = _try_speedtest_cli()
    if result:
        return result

    raise RuntimeError(
        "No speedtest tool found. Install with:\n"
        "pip install speedtest-cli\n"
        "or: apt install speedtest-cli"
    )


def _try_ookla() -> dict | None:
    """Try official Ookla speedtest binary (outputs JSON)."""
    try:
        r = subprocess.run(
            ["speedtest", "--format=json", "--accept-license", "--accept-gdpr"],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode != 0:
            return None
        data = json.loads(r.stdout)
        return {
            "download_mbps": round(data["download"]["bandwidth"] * 8 / 1e6, 2),
            "upload_mbps":   round(data["upload"]["bandwidth"]   * 8 / 1e6, 2),
            "ping_ms":       round(data["ping"]["latency"], 1),
            "isp":           data.get("isp", "Unknown"),
            "server_name":   data.get("server", {}).get("name", "Unknown"),
            "server_url":    data.get("result", {}).get("url", ""),
            "public_ip":     data.get("interface", {}).get("externalIp", ""),
            "last_run":      datetime.now().isoformat(timespec="seconds"),
        }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def _try_speedtest_cli() -> dict | None:
    """Try speedtest-cli python package (text output)."""
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

        if dl is None or ul is None:
            return None

        return {
            "download_mbps": dl,
            "upload_mbps":   ul,
            "ping_ms":       ping,
            "isp":           None,
            "server_name":   None,
            "server_url":    None,
            "public_ip":     None,
            "last_run":      datetime.now().isoformat(timespec="seconds"),
        }
    except FileNotFoundError:
        return None


# ── Save to config.py ─────────────────────────────────────────

def save_to_config(result: dict, config_path: str) -> bool:
    """
    Write speedtest results into the SPEEDTEST dict in config.py.
    Uses regex substitution so the file format is preserved.
    """
    try:
        with open(config_path) as f:
            content = f.read()

        def _replace(key: str, value) -> str:
            nonlocal content
            if value is None:
                val_str = "None"
            elif isinstance(value, str):
                val_str = f'"{value}"'
            else:
                val_str = str(value)
            content = re.sub(
                rf'("{key}":\s*).*?(,?\s*#[^\n]*|,?\s*\n)',
                lambda m: m.group(0).replace(
                    m.group(0),
                    f'    "{key}": {val_str},\n'
                ),
                content
            )

        for key in ["download_mbps", "upload_mbps", "ping_ms",
                    "isp", "server_name", "server_url", "public_ip", "last_run"]:
            # Simple line-by-line replace
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                if f'"{key}"' in line and ":" in line:
                    v = result.get(key)
                    if v is None:
                        val_str = "None"
                    elif isinstance(v, str):
                        val_str = f'"{v}"'
                    else:
                        val_str = str(v)
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(f'{" " * indent}"{key}": {val_str},')
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)

        with open(config_path, "w") as f:
            f.write(content)
        return True
    except Exception:
        return False


# ── Format result for Telegram ────────────────────────────────

def format_result(result: dict) -> str:
    """Format speedtest result into a clean Telegram message."""
    dl   = result.get("download_mbps", "?")
    ul   = result.get("upload_mbps",   "?")
    ping = result.get("ping_ms",       "?")
    isp  = result.get("isp",           "Unknown")
    srv  = result.get("server_name",   "Unknown")
    url  = result.get("server_url",    "")
    ip   = result.get("public_ip",     "Unknown")
    ts   = result.get("last_run",      "")

    lines = [
        "🚀 *Speedtest Result*\n",
        f"⬇️ Download : `{dl} Mbps`",
        f"⬆️ Upload   : `{ul} Mbps`",
        f"📡 Ping     : `{ping} ms`",
        f"🌐 Public IP: `{ip}`",
        f"🏢 ISP      : `{isp}`",
        f"🖥 Server   : `{srv}`",
    ]
    if url:
        lines.append(f"🔗 [View result]({url})")
    if ts:
        lines.append(f"\n🕐 `{ts}`")

    return "\n".join(lines)


# ── Install speedtest-cli if missing ──────────────────────────

def ensure_installed() -> tuple:
    """Check if any speedtest tool is available, install if not."""
    for cmd in ["speedtest", "speedtest-cli"]:
        r = subprocess.run(["which", cmd], capture_output=True)
        if r.returncode == 0:
            return True, f"{cmd} already installed"
    # Try installing via pip
    r = subprocess.run(
        ["pip3", "install", "speedtest-cli", "--break-system-packages"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        return True, "speedtest-cli installed"
    return False, "Could not install speedtest-cli"
