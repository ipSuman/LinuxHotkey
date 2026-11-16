from linuxhotkey import hotkey, run, notify

@hotkey("<Control><Alt>t")
def open_terminal():
    run(["gnome-terminal"])

@hotkey("<Control><Alt>h")
def hello():
    notify("LinuxHotkey", "Your first custom Python hotkey works!")
