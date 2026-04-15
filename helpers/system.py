"""
helpers/system.py
────────────────────────────────────────────────────────────────
System stats: CPU, RAM, Disk, IP, Bandwidth
All functions are pure — no side effects, no global state
────────────────────────────────────────────────────────────────
"""

import os
import time
import urllib.request


# ── Public IP ─────────────────────────────────────────────────

def get_public_ip() -> str:
    """Fetch server public IP via ipify."""
    try:
        return urllib.request.urlopen(
            "https://api.ipify.org", timeout=5
        ).read().decode()
    except Exception:
        return "Unknown"


# ── CPU ───────────────────────────────────────────────────────

def _read_cpu_times() -> tuple:
    """Read raw CPU time fields from /proc/stat."""
    with open("/proc/stat") as f:
        line = f.readline()
    fields = list(map(int, line.split()[1:]))
    idle  = fields[3]
    total = sum(fields)
    return idle, total


def get_cpu_percent() -> float:
    """
    CPU usage in percent (0–100).
    Sleeps 0.3s to measure delta — call once per refresh cycle.
    """
    idle1, total1 = _read_cpu_times()
    time.sleep(0.3)
    idle2, total2 = _read_cpu_times()
    delta_idle  = idle2  - idle1
    delta_total = total2 - total1
    if delta_total == 0:
        return 0.0
    return round((1 - delta_idle / delta_total) * 100, 1)


# ── RAM ───────────────────────────────────────────────────────

def _parse_meminfo() -> dict:
    """Parse /proc/meminfo into a key→kB dict."""
    mem = {}
    with open("/proc/meminfo") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                mem[parts[0].rstrip(":")] = int(parts[1])
    return mem


def get_total_ram_gb() -> float:
    """Total installed RAM in GB."""
    return round(_parse_meminfo().get("MemTotal", 0) / 1024 / 1024, 1)


def get_used_ram_mb() -> int:
    """Used RAM in MB (total minus available)."""
    mem = _parse_meminfo()
    return (mem.get("MemTotal", 0) - mem.get("MemAvailable", 0)) // 1024


def get_ram_percent() -> float:
    """RAM usage as a percentage."""
    mem   = _parse_meminfo()
    total = mem.get("MemTotal", 1)
    avail = mem.get("MemAvailable", 0)
    return round((total - avail) / total * 100, 1)


# ── Disk ──────────────────────────────────────────────────────

def get_disk_info() -> dict:
    """
    Disk usage for root filesystem.
    Returns: {total_gb, used_gb, free_gb, percent}
    """
    st       = os.statvfs("/")
    total_gb = round(st.f_blocks * st.f_frsize / 1024**3, 1)
    free_gb  = round(st.f_bfree  * st.f_frsize / 1024**3, 1)
    used_gb  = round(total_gb - free_gb, 1)
    percent  = round(used_gb / total_gb * 100, 1) if total_gb else 0
    return {
        "total":   total_gb,
        "used":    used_gb,
        "free":    free_gb,
        "percent": percent,
    }


# ── Bandwidth (live) ──────────────────────────────────────────

def _read_net_bytes(iface: str) -> tuple:
    """Read rx/tx byte counters from sysfs."""
    try:
        with open(f"/sys/class/net/{iface}/statistics/rx_bytes") as f:
            rx = int(f.read())
        with open(f"/sys/class/net/{iface}/statistics/tx_bytes") as f:
            tx = int(f.read())
        return rx, tx
    except FileNotFoundError:
        return 0, 0


def get_bandwidth_mbps(iface: str = "eth0", interval: float = 1.0) -> dict:
    """
    Measure live bandwidth over `interval` seconds.
    Returns: {rx_mbps, tx_mbps}
    """
    rx1, tx1 = _read_net_bytes(iface)
    time.sleep(interval)
    rx2, tx2 = _read_net_bytes(iface)
    return {
        "rx": round((rx2 - rx1) * 8 / 1e6 / interval, 2),
        "tx": round((tx2 - tx1) * 8 / 1e6 / interval, 2),
    }


# ── Combined snapshot ─────────────────────────────────────────

def get_all_stats(iface: str = "eth0") -> dict:
    """
    Collect all system stats in one call.
    Note: takes ~1.3s due to CPU + bandwidth measurement sleeps.
    """
    bw = get_bandwidth_mbps(iface)    # 1s sleep
    return {
        "ip":           get_public_ip(),
        "cpu":          get_cpu_percent(),   # 0.3s sleep
        "ram_used_mb":  get_used_ram_mb(),
        "ram_total_gb": get_total_ram_gb(),
        "ram_percent":  get_ram_percent(),
        "disk":         get_disk_info(),
        "bw_rx_mbps":   bw["rx"],
        "bw_tx_mbps":   bw["tx"],
    }
