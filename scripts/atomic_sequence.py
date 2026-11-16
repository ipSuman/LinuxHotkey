from linuxhotkey import hotkey, input_lock, press, type_text, click

@hotkey("<Control><Alt>a")
def atomic_sequence():
    with input_lock():
        press("CTRL", "A")
        type_text("LinuxHotkey atomic sequence!")
        click("left")

