# DarkOS 1.0 Raspberry Pi 4 graphical login.
[[ -r "$HOME/.bashrc" ]] && source "$HOME/.bashrc"
if [[ "$(tty 2>/dev/null)" == "/dev/tty1" && -z "${DARKOS_SESSION_STARTED:-}" ]]; then
    export DARKOS_SESSION_STARTED=1
    export GDK_BACKEND=wayland
    if command -v lxqt-policykit-agent >/dev/null 2>&1; then
        lxqt-policykit-agent >/dev/null 2>&1 &
    fi
    exec cage -- /usr/bin/python3 /usr/share/darkos-shell/darkos-shell.py
fi
