# DarkShell interactive Bash configuration.
# Bash remains the actual shell; this file adds the DarkOS command layer.

[[ $- == *i* ]] || return

# Keep the normal system and user Bash configuration available.
[[ -r /etc/bashrc ]] && source /etc/bashrc
[[ -r "$HOME/.bashrc" ]] && source "$HOME/.bashrc"

DARKOS_MODE_FILE="${XDG_RUNTIME_DIR:-/tmp}/darkos-mode"

Lord() {
    if (( $# == 0 )); then
        printf 'Usage: Lord <command> [arguments...]\n'
        return 2
    fi
    sudo "$@"
}

file() {
    if (( $# == 0 )); then
        printf 'Usage: file <name> [name...]\n'
        return 2
    fi
    command touch -- "$@"
}

folder() {
    if (( $# == 0 )); then
        printf 'Usage: folder <name> [name...]\n'
        return 2
    fi
    command mkdir -p -- "$@"
}

delete() {
    if (( $# == 0 )); then
        printf 'Usage: delete <file-or-folder> [path...]\n'
        return 2
    fi
    printf 'Interactive delete: each item will be confirmed by rm.\n'
    command rm -ri -- "$@"
}

FileInfo() {
    if (( $# == 0 )); then
        printf 'Usage: FileInfo <file> [file...]\n'
        return 2
    fi
    local path
    for path in "$@"; do
        if [[ -f "$path" ]]; then
            printf '\n--- %s ---\n' "$path"
            command cat -- "$path"
            printf '\n'
        else
            printf 'FileInfo: not a regular file: %s\n' "$path" >&2
        fi
    done
}

Help() {
    cat <<'DARKOS_HELP'
DarkShell custom commands
  Help        Show this command list
  Lord        Run a command with sudo authentication
  find        Search for files and folders
  file        Create an empty file
  folder      Create a folder (including parent folders)
  delete      Interactively remove files or folders
  FileInfo    Display a text file's contents
  Neofetch    Display system information
  clear       Clear the terminal

Bash is the shell underneath DarkShell. Standard Bash builtins and
installed Linux commands remain available.
DARKOS_HELP
}

Neofetch() {
    if command -v neofetch >/dev/null 2>&1; then
        command neofetch "$@"
        return $?
    fi

    # Fedora 45 no longer ships the original Neofetch RPM. Until the
    # upstream utility is bundled, provide the same core system summary.
    local os_name kernel uptime_text shell_name
    os_name="$(. /etc/os-release 2>/dev/null; printf '%s' "${PRETTY_NAME:-Linux}")"
    kernel="$(uname -r)"
    uptime_text="$(uptime -p 2>/dev/null || true)"
    shell_name="${SHELL##*/}"
    printf '\033[31m        /\\_/\\\033[0m    \033[1mDarkOS\033[0m\n'
    printf '\033[31m       ( o.o )\033[0m   OS: %s\n' "$os_name"
    printf '\033[31m        > ^ <\033[0m   Host: %s\n' "$(hostname)"
    printf '                  Kernel: %s\n' "$kernel"
    printf '                  Shell: %s\n' "$shell_name"
    [[ -n "$uptime_text" ]] && printf '                  Uptime: %s\n' "$uptime_text"
    printf '                  Desktop: DarkOS 1.0\n'
}

_darkos_update_prompt() {
    local mode="RED" color="31"
    if [[ -r "$DARKOS_MODE_FILE" ]]; then
        IFS= read -r mode < "$DARKOS_MODE_FILE"
    fi
    case "$mode" in
        GREEN) color="32" ;;
        BLUE) color="34" ;;
        *) mode="RED"; color="31" ;;
    esac
    PS1="\[\e[${color}m\][Dark@DarkOS \w]$ \[\e[0m\]"
}

PROMPT_COMMAND="_darkos_update_prompt"
_darkos_update_prompt
