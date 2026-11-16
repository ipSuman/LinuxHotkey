LinuxHotkey v0.2

Python-first automation for Ubuntu GNOME on Wayland.

What's new in v0.2

- "type_text(text)" — type text into the focused application with configurable delays.
- "press("ENTER")" — press a key; "press("CTRL", "A")" presses a chord.
- "key_down()" / "key_up()" — hold and release a key.
- "click("left")" — left, right, and middle mouse clicks.
- "move_mouse(x, y)" — move the pointer to absolute screen coordinates.
- "input_lock()" — group multiple keyboard, mouse, and clipboard operations into one atomic sequence.
- "snippet(binding)" — register a shortcut-triggered text insertion function.
- Improved "ydotool" handling and safer text input through stdin.
- Installer can be run again to upgrade the engine without overwriting existing user scripts.

Install or upgrade

Extract the ZIP, open a terminal in the "LinuxHotkey" directory, then:

chmod +x install.sh
./install.sh

The installer updates the user-level daemon and leaves your scripts in "~/.config/linuxhotkey/scripts/" intact.

Enable keyboard and mouse injection on Wayland

Install ydotool:

sudo apt update
sudo apt install ydotool

"ydotool" needs its "ydotoold" background daemon and access to "/dev/uinput". Package and service setup can vary by Ubuntu package version. Inspect what your package installed:

command -v ydotool
command -v ydotoold
systemctl list-unit-files | grep -i ydotool
ydotoold --help

If an installed ydotool system service is listed, inspect it before enabling it. Do not run LinuxHotkey itself as root or grant broad input-device permissions casually.

Write a script

Create or edit a ".py" file under:

"~/.config/linuxhotkey/scripts/"

Example:

from linuxhotkey import (
    hotkey, run, notify, type_text, press,
    click, move_mouse, sleep
)

@hotkey("<Control><Alt>h")
def insert_greeting():
    type_text("Hello from LinuxHotkey!")

@hotkey("<Control><Alt>j")
def open_terminal_and_type():
    run(["gnome-terminal"])
    sleep(1)
    type_text("echo LinuxHotkey is running")
    press("ENTER")

@hotkey("<Control><Alt>k")
def mouse_demo():
    move_mouse(500, 400)
    click("left")
    notify("LinuxHotkey", "Mouse action completed")

Atomic input sequences

Use "input_lock()" when several operations must execute together without another LinuxHotkey script interleaving its input:

from linuxhotkey import input_lock, press, type_text, click

with input_lock():
    press("CTRL", "A")
    type_text("Replacement text")
    click("left")

The lock is shared by LinuxHotkey's keyboard, mouse, and clipboard API operations. It does not block physical keyboard or mouse input, or input injected by unrelated applications.

See "scripts/atomic_sequence.py" for a complete hotkey example.

Shortcut-triggered text snippets

"snippet()" is a shortcut decorator for text insertion:

from linuxhotkey import snippet, type_text

@snippet("<Control><Alt>e")
def insert_email():
    type_text("your-email@example.com")

This runs when the registered shortcut is pressed. It is not automatic abbreviation expansion: LinuxHotkey does not monitor all typed characters to detect abbreviations such as ";email".

Register and reload

After creating or editing scripts:

linuxhotkey reload
linuxhotkey register

"reload" updates the running daemon's scripts. "register" updates GNOME's global shortcut registrations.

GNOME accelerator syntax is used for global shortcuts, e.g. "<Control><Alt>h", "<Shift>F10", "<Super>e".

API reference

Function| Description
"hotkey(binding)"| Decorator to bind a Python function to a GNOME shortcut
"snippet(binding)"| Shortcut-triggered text insertion decorator
"run(command, wait=False, check=False)"| Launch a command; use an argument list where possible
"notify(title, message)"| Desktop notification using "notify-send"
"type_text(text, key_delay_ms=20, start_delay=500)"| Type text using ydotool
"press(*keys, key_delay_ms=12)"| Press one key or a chord
"key_down(key)" / "key_up(key)"| Hold and release a key
"click(button="left", repeat=1, delay_ms=25)"| Mouse click
"move_mouse(x, y, absolute=True)"| Move pointer to absolute screen coordinates
"sleep(seconds)"| Delay the current script function
"get_clipboard()" / "set_clipboard(text)"| Clipboard access using Wayland clipboard tools
"input_lock()"| Context manager for atomic sequences of LinuxHotkey input operations

Key names supported by "press()" include letters A–Z, digits 0–9, ENTER, ESC, TAB, SPACE, BACKSPACE, DELETE, INSERT, HOME, END, arrows, PAGEUP/PAGEDOWN, F1–F10, CTRL, ALT, SHIFT, SUPER, and common volume keys.

"press()" sends a chord when multiple keys are passed. Use "type_text()" for arbitrary text.

Manage and troubleshoot

linuxhotkey list
linuxhotkey reload
linuxhotkey register
systemctl --user status linuxhotkey.service
journalctl --user -u linuxhotkey.service -f
tail -f ~/.config/linuxhotkey/linuxhotkey.log

Wayland limitations

- GNOME owns global shortcut registration; LinuxHotkey does not globally snoop raw keystrokes.
- Keyboard and mouse injection uses ydotool's virtual input device. It must be configured separately and works only where the desktop accepts synthetic input.
- Pointer-position reading and arbitrary window introspection are not included in this milestone; Wayland intentionally restricts these capabilities.
- Automatic hotstring detection requires global input monitoring and is not supported by this architecture.
- Never run user automation scripts with "sudo".

Uninstall

systemctl --user disable --now linuxhotkey.service
rm -f ~/.config/systemd/user/linuxhotkey.service ~/.local/bin/linuxhotkey
rm -rf ~/.local/share/linuxhotkey
systemctl --user daemon-reload

Remove LinuxHotkey entries from GNOME Settings > Keyboard > View and Customize Shortcuts > Custom Shortcuts if you no longer need them. Your scripts under "~/.config/linuxhotkey/scripts/" are kept unless you remove that directory yourself.
