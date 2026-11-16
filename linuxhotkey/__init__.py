"""LinuxHotkey: Python-first desktop automation for GNOME on Wayland."""

from .api import (
    hotkey, snippet, run, notify, type_text, press,
    key_down, key_up, click, move_mouse, sleep,
    get_clipboard, set_clipboard, input_lock,
)

__all__ = [
    "hotkey", "snippet", "run", "notify", "type_text",
    "press", "key_down", "key_up", "click", "move_mouse",
    "sleep", "get_clipboard", "set_clipboard", "input_lock",
]
