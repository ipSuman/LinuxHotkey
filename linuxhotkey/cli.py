import argparse
import sys
from .engine import serve, load_scripts
from . import api
from .client import request
from .gnome import register

def main():
    p = argparse.ArgumentParser(prog="linuxhotkey")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("daemon")
    sub.add_parser("register")
    sub.add_parser("reload")
    sub.add_parser("list")
    t = sub.add_parser("trigger"); t.add_argument("name")
    args = p.parse_args()
    if args.cmd == "daemon":
        serve()
    elif args.cmd == "trigger":
        try: request({"action": "trigger", "name": args.name})
        except Exception as e:
            print(f"LinuxHotkey daemon unavailable: {e}", file=sys.stderr); return 1
    elif args.cmd in ("reload", "list"):
        try:
            result = request({"action": args.cmd})
            print(result)
        except Exception as e:
            print(f"LinuxHotkey daemon unavailable: {e}", file=sys.stderr); return 1
    elif args.cmd == "register":
        load_scripts()
        print(f"Registered {register()} GNOME shortcuts.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
