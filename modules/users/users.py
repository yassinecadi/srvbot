"""
modules/users/users.py
─────────────────────────────────────────────
SSH Linux user management.
Pure logic — no Telegram imports.
─────────────────────────────────────────────
"""

import subprocess
import pwd
import random
import string
from datetime import datetime, timedelta
from typing import Optional

from core.utils import run_cmd


SHELL_WHITELIST = ["/bin/bash", "/bin/sh", "/usr/bin/bash"]
EXCLUDED_USERS  = {"root", "sync", "daemon", "bin", "sys", "nobody"}


# ── List ──────────────────────────────────

def get_all_users() -> list:
    """Return all non-system SSH users (uid >= 1000, bash shell)."""
    result = []
    try:
        for pw in pwd.getpwall():
            if pw.pw_name in EXCLUDED_USERS:
                continue
            if pw.pw_shell not in SHELL_WHITELIST:
                continue
            if pw.pw_uid < 1000:
                continue
            result.append(_build_user(pw.pw_name))
    except Exception:
        pass
    return result


def _build_user(username: str) -> dict:
    return {
        "username":    username,
        "active":      _is_active(username),
        "expires":     _get_expiry(username),
        "connections": _count_connections(username),
    }


def get_active_count(user_list: list) -> int:
    return sum(1 for u in user_list if u["active"])


# ── Detail helpers ────────────────────────

def _is_active(username: str) -> bool:
    code, out = run_cmd(["passwd", "--status", username])
    if code == 0 and out:
        parts = out.split()
        if len(parts) >= 2:
            return parts[1] == "P"
    return True


def _get_expiry(username: str) -> Optional[str]:
    code, out = run_cmd(["chage", "-l", username])
    if code != 0:
        return None
    for line in out.splitlines():
        if "Account expires" in line:
            val = line.split(":", 1)[1].strip()
            return None if val.lower() == "never" else val
    return None


def _count_connections(username: str) -> int:
    code, out = run_cmd(["who"])
    if code != 0:
        return 0
    return sum(1 for line in out.splitlines() if line.startswith(username))


# ── CRUD ──────────────────────────────────

def add_user(username: str, password: str,
             days: Optional[int] = None) -> tuple:
    code, out = run_cmd(["useradd", "-m", "-s", "/bin/bash", username])
    if code != 0:
        return False, f"useradd failed: {out}"
    r = subprocess.run(["chpasswd"], input=f"{username}:{password}",
                       text=True, capture_output=True)
    if r.returncode != 0:
        return False, f"chpasswd failed: {r.stderr}"
    if days:
        exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        run_cmd(["chage", "-E", exp, username])
    return True, f"User {username} created"


def delete_user(username: str) -> tuple:
    if username in EXCLUDED_USERS:
        return False, "Cannot delete system user"
    code, out = run_cmd(["userdel", "-r", username])
    return code == 0, out or f"User {username} deleted"


def change_password(username: str, password: str) -> tuple:
    r = subprocess.run(["chpasswd"], input=f"{username}:{password}",
                       text=True, capture_output=True)
    ok = r.returncode == 0
    return ok, "Password changed" if ok else r.stderr.strip()


def lock_user(username: str) -> tuple:
    code, out = run_cmd(["passwd", "--lock", username])
    return code == 0, "User locked" if code == 0 else out


def unlock_user(username: str) -> tuple:
    code, out = run_cmd(["passwd", "--unlock", username])
    return code == 0, "User unlocked" if code == 0 else out


def set_expiry(username: str, days: Optional[int]) -> tuple:
    if days is None:
        code, out = run_cmd(["chage", "-E", "-1", username])
    else:
        exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        code, out = run_cmd(["chage", "-E", exp, username])
    return code == 0, "Expiry updated" if code == 0 else out


def random_password(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
