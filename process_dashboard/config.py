"""Application configuration and shared formatting helpers."""

APP_NAME = "Process Dashboard Pro"
SAMPLE_INTERVAL = 1.0
GRAPH_POINTS = 60
CPU_ALERT = 25.0
MEMORY_ALERT_BYTES = 500 * 1024 * 1024
PROTECTED_NAMES = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "winlogon.exe", "svchost.exe",
    "fontdrvhost.exe", "dwm.exe", "system idle process"
}

def format_bytes(value):
    value = float(value or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{int(value)} B" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"

def safe_name(proc):
    """Return a process name safely even if it exits during a UI action."""
    try:
        return proc.name() or f"PID {proc.pid}"
    except Exception:
        return f"PID {getattr(proc, 'pid', '?')}"
