import importlib.util
import json
import os
import socket
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from . import api

BASE = Path.home() / ".config" / "linuxhotkey"
SCRIPTS = BASE / "scripts"
SOCKET = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "linuxhotkey.sock"
LOG = BASE / "linuxhotkey.log"

def log(message):
    BASE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(message.rstrip() + "\\n")

def load_scripts():
    api._REGISTRY.clear()
    SCRIPTS.mkdir(parents=True, exist_ok=True)
    for path in sorted(SCRIPTS.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"lh_user_{path.stem}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            log(f"Loaded {path.name}")
        except Exception:
            log(f"ERROR loading {path.name}:\\n{traceback.format_exc()}")

def execute(name):
    item = api._REGISTRY.get(name)
    if not item:
        log(f"Unknown hotkey function: {name}")
        return
    try:
        log(f"RUN {name}")
        item["function"]()
        log(f"OK {name}")
    except Exception:
        log(f"ERROR in {name}:\\n{traceback.format_exc()}")

def serve():
    BASE.mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)
    try:
        SOCKET.unlink()
    except FileNotFoundError:
        pass
    load_scripts()
    pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="lh-task")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(SOCKET))
    os.chmod(SOCKET, 0o600)
    server.listen(16)
    log(f"LinuxHotkey daemon started; {len(api._REGISTRY)} hotkeys loaded")
    while True:
        conn, _ = server.accept()
        with conn:
            try:
                data = conn.recv(4096).decode("utf-8")
                request = json.loads(data)
                if request.get("action") == "trigger":
                    pool.submit(execute, request.get("name", ""))
                    conn.sendall(b'{"ok":true}')
                elif request.get("action") == "reload":
                    load_scripts()
                    conn.sendall(json.dumps({"ok": True, "hotkeys": list(api._REGISTRY)}).encode())
                elif request.get("action") == "list":
                    result = {k: v["binding"] for k, v in api._REGISTRY.items()}
                    conn.sendall(json.dumps(result).encode())
                else:
                    conn.sendall(b'{"ok":false,"error":"unknown action"}')
            except Exception as exc:
                log(f"IPC ERROR: {exc}")
                try: conn.sendall(json.dumps({"ok": False, "error": str(exc)}).encode())
                except Exception: pass
