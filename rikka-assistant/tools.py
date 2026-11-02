"""
System integration tools: hardware stats, application launching,
browser search, and privacy-respecting screen context capture.
"""
from __future__ import annotations

import base64
import ctypes
import logging
import platform
import re
import shutil
import subprocess
import webbrowser
from typing import Optional

import psutil
from PyQt6.QtCore import QBuffer, QIODevice, Qt
from PyQt6.QtGui import QGuiApplication

log = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  Active Window & Screen Context                                      #
# ------------------------------------------------------------------ #

def get_active_window_title() -> str:
    """Return the title of the current foreground window on Windows/Linux."""
    if platform.system() == "Windows":
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                length = user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value.strip()
        except Exception as exc:
            log.debug("GetForegroundWindow error: %s", exc)
    return ""


def capture_screen_context(max_w: int = 1024, max_h: int = 768) -> tuple[Optional[str], str]:
    """
    Capture the primary screen as a downscaled JPEG base64 string.
    Also returns the active foreground window title.
    Returns (base64_jpeg_str, active_window_title).
    """
    active_win = get_active_window_title()
    screen = QGuiApplication.primaryScreen()
    if not screen:
        return None, active_win

    try:
        pix = screen.grabWindow(0)
        if pix.isNull():
            return None, active_win

        # Downscale for fast transmission and lower token usage
        if pix.width() > max_w or pix.height() > max_h:
            pix = pix.scaled(
                max_w, max_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        pix.save(buf, "JPEG", 75)
        b64_data = base64.b64encode(buf.data().data()).decode("utf-8")
        return b64_data, active_win
    except Exception as exc:
        log.warning("Screen capture error: %s", exc)
        return None, active_win


# ------------------------------------------------------------------ #
#  Browser & Web Search Tools                                          #
# ------------------------------------------------------------------ #

def browser_search(query: str) -> str:
    """Open default browser and search for query."""
    clean_query = query.strip()
    url = f"https://www.google.com/search?q={clean_query}"
    webbrowser.open(url)
    return f"Opened web search for '{clean_query}'."


def browser_open_url(url: str) -> str:
    """Open a URL in the user's default browser."""
    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url
    webbrowser.open(clean_url)
    return f"Opened URL in browser: {clean_url}"


def try_execute_system_intent(text: str) -> Optional[str]:
    """
    Inspect user input for direct quick action commands:
    e.g. 'search for X', 'google X', 'open youtube', 'open calc'.
    Returns a result message if handled, or None if it should be sent to the LLM.
    """
    lower = text.strip().lower()

    # Web search command: "search for ...", "google ..."
    match_search = re.match(r"^(?:search(?:\s+for|\s+web|\s+google)?|google)\s+(.+)$", lower)
    if match_search:
        query = match_search.group(1).strip()
        return browser_search(query)

    # Open specific websites: "open youtube", "open github", "open reddit"
    match_open_site = re.match(r"^open\s+(youtube|github|reddit|twitter|x|twitch|wikipedia|gmail)\.?(?:com)?$", lower)
    if match_open_site:
        site = match_open_site.group(1)
        urls = {
            "youtube": "https://youtube.com",
            "github": "https://github.com",
            "reddit": "https://reddit.com",
            "twitter": "https://x.com",
            "x": "https://x.com",
            "twitch": "https://twitch.tv",
            "wikipedia": "https://wikipedia.org",
            "gmail": "https://mail.google.com",
        }
        target_url = urls.get(site, f"https://{site}.com")
        return browser_open_url(target_url)

    # Open general URL: "open http..."
    match_url = re.match(r"^open\s+(https?://\S+)$", lower)
    if match_url:
        return browser_open_url(match_url.group(1))

    # Open desktop applications: "open notepad", "open calc", "open vscode", "open terminal"
    match_app = re.match(r"^open\s+([a-zA-Z0-9_\- ]+)$", lower)
    if match_app:
        app_name = match_app.group(1).strip()
        ok, msg = open_application(app_name)
        if ok:
            return msg

    return None


# ------------------------------------------------------------------ #
#  System Statistics                                                   #
# ------------------------------------------------------------------ #

def get_system_stats() -> dict:
    """
    Return a snapshot of key hardware metrics.
    Includes CPU, RAM, disk, optional battery and GPU.
    """
    stats: dict = {}

    stats["cpu_percent"] = psutil.cpu_percent(interval=0.4)
    stats["cpu_count_logical"] = psutil.cpu_count(logical=True)
    stats["cpu_count_physical"] = psutil.cpu_count(logical=False)

    mem = psutil.virtual_memory()
    stats["ram_total_gb"] = round(mem.total / 1024 ** 3, 1)
    stats["ram_used_gb"] = round(mem.used / 1024 ** 3, 1)
    stats["ram_percent"] = mem.percent

    root = "C:\\" if platform.system() == "Windows" else "/"
    try:
        disk = psutil.disk_usage(root)
        stats["disk_total_gb"] = round(disk.total / 1024 ** 3, 1)
        stats["disk_used_gb"] = round(disk.used / 1024 ** 3, 1)
        stats["disk_percent"] = disk.percent
    except Exception as exc:
        log.debug("Disk stats unavailable: %s", exc)

    try:
        batt = psutil.sensors_battery()
        if batt is not None:
            stats["battery_percent"] = round(batt.percent, 1)
            stats["battery_plugged"] = batt.power_plugged
    except Exception:
        pass

    try:
        import GPUtil  # type: ignore[import]
        gpus = GPUtil.getGPUs()
        if gpus:
            g = gpus[0]
            stats["gpu_name"] = g.name
            stats["gpu_load_percent"] = round(g.load * 100, 1)
            stats["gpu_mem_used_mb"] = int(g.memoryUsed)
            stats["gpu_mem_total_mb"] = int(g.memoryTotal)
    except ImportError:
        pass
    except Exception as exc:
        log.debug("GPU stats unavailable: %s", exc)

    return stats


def format_stats(stats: dict) -> str:
    """Format a stats dict into a human-readable string for chat display."""
    lines: list[str] = [
        f"🖥  CPU     {stats.get('cpu_percent', '?')}%"
        f"  ({stats.get('cpu_count_physical', '?')}P / {stats.get('cpu_count_logical', '?')}L cores)",
        f"🧠 RAM     {stats.get('ram_used_gb', '?')} / {stats.get('ram_total_gb', '?')} GB"
        f"  ({stats.get('ram_percent', '?')}%)",
    ]
    if "disk_total_gb" in stats:
        lines.append(
            f"💾 Disk    {stats.get('disk_used_gb', '?')} / {stats.get('disk_total_gb', '?')} GB"
            f"  ({stats.get('disk_percent', '?')}%)"
        )
    if "battery_percent" in stats:
        plug = "⚡" if stats.get("battery_plugged") else "🔋"
        lines.append(f"{plug}  Battery  {stats['battery_percent']:.0f}%")
    if "gpu_name" in stats:
        lines.append(
            f"🎮 GPU     {stats['gpu_name']}"
            f"  {stats.get('gpu_load_percent', '?')}%"
            f"  ({stats.get('gpu_mem_used_mb', '?')} / {stats.get('gpu_mem_total_mb', '?')} MB)"
        )
    return "\n".join(lines)


# ------------------------------------------------------------------ #
#  Application Launcher                                                #
# ------------------------------------------------------------------ #

_APP_CANDIDATES: dict[str, list[str]] = {
    "browser":      ["firefox", "google-chrome", "chrome", "chromium", "msedge"],
    "terminal":     ["wt", "cmd", "gnome-terminal", "xterm", "konsole", "alacritty"],
    "explorer":     ["explorer.exe", "nautilus", "dolphin", "thunar"],
    "notepad":      ["notepad.exe", "gedit", "kate", "mousepad"],
    "vscode":       ["code"],
    "calc":         ["calc.exe", "gnome-calculator", "kcalc", "qalculate-gtk"],
    "calculator":   ["calc.exe", "gnome-calculator", "kcalc", "qalculate-gtk"],
    "spotify":      ["spotify"],
    "discord":      ["discord", "Discord"],
    "steam":        ["steam"],
    "task manager": ["taskmgr.exe", "gnome-system-monitor"],
}


def open_application(name: str) -> tuple[bool, str]:
    """Attempt to launch a named application."""
    key = name.lower().strip()
    candidates = _APP_CANDIDATES.get(key, [key])

    for exe in candidates:
        resolved = shutil.which(exe)
        if resolved:
            try:
                subprocess.Popen([resolved], close_fds=True)
                return True, f"Launched `{exe}`."
            except OSError as exc:
                log.warning("Failed to launch %s: %s", exe, exc)

    return False, f"Application not found: '{name}'"
