"""User-facing automation helpers for LinuxHotkey."""
import shutil
import subprocess
import time
from contextlib import contextmanager

@contextmanager
def input_lock():
    """Group multiple input operations into one atomic sequence."""
    with _INPUT_LOCK:
        yield

_REGISTRY = {}
_INPUT_LOCK = __import__("threading").RLock()


# Linux input-event key codes (KEY_* from linux/input-event-codes.h).
_KEYCODES = {
    "ESC": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    "MINUS": 12, "EQUAL": 13, "BACKSPACE": 14, "TAB": 15,
    "Q": 16, "W": 17, "E": 18, "R": 19, "T": 20, "Y": 21,
    "U": 22, "I": 23, "O": 24, "P": 25, "LEFTBRACE": 26,
    "RIGHTBRACE": 27, "ENTER": 28, "CTRL": 29, "A": 30,
    "S": 31, "D": 32, "F": 33, "G": 34, "H": 35,
    "J": 36, "K": 37, "L": 38, "SEMICOLON": 39,
    "APOSTROPHE": 40, "GRAVE": 41, "SHIFT": 42, "BACKSLASH": 43,
    "Z": 44, "X": 45, "C": 46, "V": 47, "B": 48,
    "N": 49, "M": 50, "COMMA": 51, "DOT": 52, "SLASH": 53,
    "ALT": 56, "SPACE": 57, "CAPSLOCK": 58, "F1": 59,
    "F2": 60, "F3": 61, "F4": 62, "F5": 63, "F6": 64,
    "F7": 65, "F8": 66, "F9": 67, "F10": 68, "NUMLOCK": 69,
    "SCROLLLOCK": 70, "HOME": 102, "UP": 103, "PAGEUP": 104,
    "LEFT": 105, "RIGHT": 106, "END": 107, "DOWN": 108,
    "PAGEDOWN": 109, "INSERT": 110, "DELETE": 111,
    "MUTE": 113,
    "VOLUMEDOWN": 114, "VOLUMEUP": 115, "POWER": 116,
    "PAUSE": 119, "LEFTCTRL": 29, "RIGHTCTRL": 97,
    "RIGHTALT": 100, "RIGHTSHIFT": 54, "SUPER": 125,
    "LEFTSUPER": 125, "RIGHTSUPER": 126,
}


def hotkey(binding):
    """Register a function. Example: @hotkey('<Control><Alt>t')."""
    def decorate(func):
        if func.__name__ in _REGISTRY:
            raise ValueError(f"Duplicate hotkey function name: {func.__name__}")
        _REGISTRY[func.__name__] = {"binding": binding, "function": func}
        return func
    return decorate

def snippet(binding):
    """Register a text snippet or other action to run from a keyboard shortcut."""
    return hotkey(binding)

def run(command, *, wait=False, check=False, cwd=None, env=None):
    """Run a command. Pass a list for safer argument handling."""
    kwargs = {"cwd": cwd, "env": env}
    if isinstance(command, str):
        if wait:
            return subprocess.run(command, shell=True, check=check, **kwargs)
        return subprocess.Popen(command, shell=True, **kwargs)
    if wait:
        return subprocess.run(command, check=check, **kwargs)
    return subprocess.Popen(command, **kwargs)


def notify(title, message):
    """Show a GNOME desktop notification (requires notify-send)."""
    if not shutil.which("notify-send"):
        raise RuntimeError("notify-send is missing. Install it with: sudo apt install libnotify-bin")
    return subprocess.run(["notify-send", str(title), str(message)], check=True)


def _ydotool(*args, input_text=None):
    if not shutil.which("ydotool"):
        raise RuntimeError("Input automation requires ydotool. Install it with: sudo apt install ydotool")
    try:
        return subprocess.run(["ydotool", *map(str, args)], input=input_text, check=True,
                              capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        hint = "Make sure ydotoold is running and has access to /dev/uinput."
        raise RuntimeError(f"ydotool failed: {detail or exc}. {hint}") from exc


def type_text(text, *, key_delay_ms=20, start_delay=500):
    """Type text into the focused application."""
    with _INPUT_LOCK:
        _ydotool(
            "type",
            "--delay", int(start_delay),
            "--key-delay", int(key_delay_ms),
            "--file", "-",
            input_text=str(text),
        )


def _keycode(key):
    name = str(key).strip().upper().replace(" ", "")
    if name in _KEYCODES:
        return _KEYCODES[name]
    if name.startswith("KEY_"):
        name = name[4:]
        if name in _KEYCODES:
            return _KEYCODES[name]
    raise ValueError(f"Unknown key '{key}'. Use a supported key name such as ENTER, A, F5, CTRL, ALT or SPACE.")


def press(*keys, key_delay_ms=12):
    """Press one key or a chord."""
    if not keys:
        raise ValueError("press() needs at least one key")

    for key in keys:
        _keycode(key)

    chord = "+".join(str(key).upper() for key in keys)

    with _INPUT_LOCK:
        _ydotool("key", "--key-delay", int(key_delay_ms), chord)


def key_down(key):
    """Hold a key down."""
    with _INPUT_LOCK:
        _ydotool("key", f"{_keycode(key)}:1")


def key_up(key):
    """Release a held key."""
    with _INPUT_LOCK:
        _ydotool("key", f"{_keycode(key)}:0")

def click(button="left", *, repeat=1, delay_ms=25):
    """Click the mouse. Supports left, right and middle buttons."""
    buttons = {"left": 1, "right": 2, "middle": 3}
    try:
        code = buttons[str(button).lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported mouse button: {button}") from exc

    repeat = int(repeat)
    if repeat < 1:
        raise ValueError("repeat must be at least 1")

    with _INPUT_LOCK:
        for _ in range(repeat):
            _ydotool("click", "--delay", int(delay_ms), str(code))


def move_mouse(x, y, *, absolute=True):
    """Move pointer to (x, y)."""
    x, y = int(x), int(y)

    if not absolute:
        raise NotImplementedError("Relative mouse movement is not yet supported.")

    with _INPUT_LOCK:
        _ydotool("mousemove", x, y)

def sleep(seconds):
    """Pause the current automation function."""
    time.sleep(max(0, float(seconds)))


def get_clipboard():
    """Read clipboard text using wl-paste on Wayland."""
    if not shutil.which("wl-paste"):
        raise RuntimeError("Install wl-clipboard to use get_clipboard(): sudo apt install wl-clipboard")

    with _INPUT_LOCK:
        return subprocess.check_output(
            ["wl-paste", "--no-newline"],
            text=True,
        )


def set_clipboard(text):
    """Set clipboard text using wl-copy on Wayland."""
    if not shutil.which("wl-copy"):
        raise RuntimeError("Install wl-clipboard to use set_clipboard(): sudo apt install wl-clipboard")

    with _INPUT_LOCK:
        subprocess.run(
            ["wl-copy"],
            input=str(text),
            text=True,
            check=True,
        )
