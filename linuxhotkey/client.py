import json
import os
import socket
from pathlib import Path

SOCKET = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "linuxhotkey.sock"

def request(payload):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(3)
    client.connect(str(SOCKET))
    client.sendall(json.dumps(payload).encode("utf-8"))
    data = client.recv(65536)
    client.close()
    return json.loads(data.decode("utf-8"))
