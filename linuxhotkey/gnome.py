import json
import shlex
import subprocess
import sys
from pathlib import Path
from . import api

SCHEMA = "org.gnome.settings-daemon.plugins.media-keys"
CHILD = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"
ROOT = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"

def gset(schema, key, value):
    subprocess.run(["gsettings", "set", schema, key, value], check=True)

def register():
    """Register current script shortcuts as GNOME custom keyboard shortcuts."""
    existing = subprocess.check_output(["gsettings", "get", SCHEMA, "custom-keybindings"], text=True).strip()
    try:
        paths = json.loads(existing.replace("'", '"'))
    except Exception:
        # GVariant arrays are usually printed as ['path', ...].
        paths = []
        import re
        paths = re.findall(r"'([^']+)'", existing)
    paths = [p for p in paths if not p.startswith(ROOT)]
    script = str(Path.home() / ".local" / "bin" / "linuxhotkey")
    idx = 0
    for name, item in api._REGISTRY.items():
        path = ROOT + f"custom{idx}/"
        idx += 1
        paths.append(path)
        command = f"{shlex.quote(script)} trigger {shlex.quote(name)}"
        def gv_string(value):
            return "'" + str(value).replace("\\\\", "\\\\\\\\").replace("'", "\\\\'") + "'"
        gset(CHILD + ":" + path, "name", gv_string("LinuxHotkey: " + name))
        gset(CHILD + ":" + path, "command", gv_string(command))
        gset(CHILD + ":" + path, "binding", gv_string(item["binding"]))
    gset(SCHEMA, "custom-keybindings", str(paths))
    return len(api._REGISTRY)
