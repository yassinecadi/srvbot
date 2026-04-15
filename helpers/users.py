"""
helpers/users.py
────────────────────────────────────────────────────────────────
SSH Linux user management: list, add, delete, password,
expiry, lock/unlock
────────────────────────────────────────────────────────────────
"""

import subprocess
import pwd
import random
import string
from datetime import datetime, timedelta
from typing import Optional


# ── Constants ─────────────────────────────────────────────────

SHELL_WHITELIST = ["/bin/bash", "/bin/sh", "/usr/bin/bash"]
EXCLUDED_USERS  = {"root", "sync", "daemon", "bin", "sys", "nobody"}


# ── Internal helper ───────────────────────────────────────────

def _run(cmd: list) -> tuple:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


# ── List users ────────────────────────────────────────────────

def get_all_users() -> list:
    """
    Return all non-system SSH-capable users (uid >= 1000, bash shell).
    Each user: {username, active, expires, connections}
    """
    users = []
    try:
        for pw in pwd.getpwall():
            if pw.pw_name in EXCLUDED_USERS:
                continue
            if pw.pw_shell not in SHELL_WHITELIST:
                continue
            if pw.pw_uid < 1000:
                continue
            users.append(_build_user(pw.pw_name))
    except Exception:
        pass
    return users


def _build_user(username: str) -> dict:
    return {
        "username":    username,
        "active":      _is_active(username),
        "expires":     _get_expiry(username),
        "connections": _count_connections(username),
    }


def get_active_count(user_list: list) -> int:
    """Count users with active (unlocked) accounts."""
    return sum(1 for u in user_list if u["active"])


# ── User detail helpers ───────────────────────────────────────

def _is_active(username: str) -> bool:
    """Check if password is set and account is not locked."""
    code, out = _run(["passwd", "--status", username])
    if code == 0 and out:
        parts = out.split()
        if len(parts) >= 2:
            return parts[1] == "P"   # P = password set, L = locked, NP = no password
    return True


def _get_expiry(username: str) -> Optional[str]:
    """Return account expiry date string or None if never."""
    code, out = _run(["chage", "-l", username])
    if code != 0:
        return None
    for line in out.splitlines():
        if "Account expires" in line:
            val = line.split(":", 1)[1].strip()
            return None if val.lower() == "never" else val
    return None


def _count_connections(username: str) -> int:
    """Count active SSH sessions for this user via `who`."""
    code, out = _run(["who"])
    if code != 0:
        return 0
    return sum(1 for line in out.splitlines() if line.startswith(username))


# ── CRUD operations ───────────────────────────────────────────

def add_user(username: str, password: str,
             days: Optional[int] = None) -> tuple:
    """
    Create Linux user with bash shell.
    Optionally set expiry in N days.
    Returns (success, message).
    """
    code, out = _run(["useradd", "-m", "-s", "/bin/bash", username])
    if code != 0:
        return False, f"useradd failed: {out}"

    result = subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}",
        text=True, capture_output=True
    )
    if result.returncode != 0:
        return False, f"chpasswd failed: {result.stderr}"

    if days:
        exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        _run(["chage", "-E", exp, username])

    return True, f"User {username} created"


def delete_user(username: str) -> tuple:
    """Delete user and their home directory."""
    if username in EXCLUDED_USERS:
        return False, "Cannot delete system user"
    code, out = _run(["userdel", "-r", username])
    return code == 0, out or f"User {username} deleted"


def change_password(username: str, password: str) -> tuple:
    """Change user password via chpasswd."""
    result = subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}",
        text=True, capture_output=True
    )
    ok = result.returncode == 0
    return ok, "Password changed" if ok else result.stderr.strip()


def lock_user(username: str) -> tuple:
    """Lock user account (blocks password login)."""
    code, out = _run(["passwd", "--lock", username])
    return code == 0, "User locked" if code == 0 else out


def unlock_user(username: str) -> tuple:
    """Unlock user account."""
    code, out = _run(["passwd", "--unlock", username])
    return code == 0, "User unlocked" if code == 0 else out


def set_expiry(username: str, days: Optional[int]) -> tuple:
    """
    Set account expiry.
    days=None → never expire
    days=N    → expire in N days from now
    """
    if days is None:
        code, out = _run(["chage", "-E", "-1", username])
    else:
        exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        code, out = _run(["chage", "-E", exp, username])
    return code == 0, "Expiry updated" if code == 0 else out


# ── Utility ───────────────────────────────────────────────────

def random_password(length: int = 8) -> str:
    """Generate a random alphanumeric password."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))
