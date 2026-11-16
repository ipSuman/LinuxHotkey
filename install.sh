#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HOME/.local/share/linuxhotkey"
mkdir -p "$ROOT/linuxhotkey" "$HOME/.config/linuxhotkey/scripts" \
         "$HOME/.local/bin" "$HOME/.config/systemd/user"

# Upgrade package files without nesting the package directory on repeat installs.
cp -a "$SOURCE_DIR/linuxhotkey/." "$ROOT/linuxhotkey/"

cat > "$HOME/.local/bin/linuxhotkey" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="$ROOT\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m linuxhotkey.cli "\$@"
EOF
chmod +x "$HOME/.local/bin/linuxhotkey"

# Keep existing user scripts intact; only seed the example on first install.
if [[ ! -e "$HOME/.config/linuxhotkey/scripts/example.py" ]]; then
    cp "$SOURCE_DIR/scripts/example.py" "$HOME/.config/linuxhotkey/scripts/example.py"
fi

if [[ ! -e "$HOME/.config/linuxhotkey/scripts/atomic_sequence.py" ]]; then
    cp "$SOURCE_DIR/scripts/atomic_sequence.py" "$HOME/.config/linuxhotkey/scripts/atomic_sequence.py"
fi

cat > "$HOME/.config/systemd/user/linuxhotkey.service" <<EOF
[Unit]
Description=LinuxHotkey Python automation daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=$HOME/.local/bin/linuxhotkey daemon
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
if systemctl --user is-enabled --quiet linuxhotkey.service 2>/dev/null; then
    systemctl --user restart linuxhotkey.service
else
    systemctl --user enable --now linuxhotkey.service
fi

# Make the command available in Fish in future terminals.
if command -v fish >/dev/null 2>&1; then
    fish -c 'fish_add_path "$HOME/.local/bin"' >/dev/null 2>&1 || true
fi

echo
echo "LinuxHotkey updated."
echo "Scripts: $HOME/.config/linuxhotkey/scripts"
echo "Next: linuxhotkey reload && linuxhotkey register"
echo "Input injection additionally requires ydotool + ydotoold setup."
