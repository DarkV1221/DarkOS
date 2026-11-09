#!/usr/bin/python3
"""DarkOS 1.0 desktop shell.

DarkOS 1.0 full-screen GTK4 shell, running in a lightweight Wayland kiosk session.
"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
from gi.repository import Gdk, Gio, GLib, Gtk, Pango, Vte


APP_ID = "com.darkos.DesktopShell"
APP_DIR = "/usr/share/darkos-shell"
BASHRC = os.path.join(APP_DIR, "darkos.bash")
MODE_FILE = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "darkos-mode")

APPS = [
    ("Firefox", "org.mozilla.firefox", "web-browser-symbolic"),
    ("Bazzar", "io.github.kolunmi.Bazaar", "system-software-install-symbolic"),
]

CSS = """
window.darkos-window {
  background: #101114;
  color: #eeeeef;
  font-family: Cantarell, Inter, sans-serif;
}
.darkos-header, .darkos-tabs, .darkos-dock {
  background: #202126;
}
.darkos-header { padding: 8px 18px; }
.darkos-tabs { padding: 4px 12px 8px 12px; }
.darkos-dock { padding: 8px 12px; }
.darkos-brand { font-size: 17px; font-weight: 800; letter-spacing: 0.3px; }
.darkos-brand-mark {
  color: #ff4545; font-size: 20px; font-weight: 900;
}
.darkos-muted { color: #92949b; font-size: 11px; }
.darkos-sidebar {
  background: #191a1e;
  padding: 18px 10px;
  min-width: 150px;
}
.darkos-sidebar-title {
  color: #858790; font-size: 10px; font-weight: 800;
  letter-spacing: 1.3px; padding: 0 8px 8px 8px;
}
.darkos-workspace { padding: 16px; background: #111215; }
.darkos-page-title { font-size: 16px; font-weight: 750; }
.darkos-terminal-frame {
  background: #08090b;
  border: 1px solid #292a30;
  border-radius: 12px;
  padding: 10px;
}
.darkos-mode {
  font-size: 10px; font-weight: 800; letter-spacing: 0.8px;
  padding: 5px 9px; border-radius: 8px;
}
.mode-red { color: #ff7777; background: #3a1e22; }
.mode-green { color: #81df9a; background: #173022; }
.mode-blue { color: #8eb9ff; background: #192a43; }
button.darkos-nav, button.darkos-tab, button.darkos-dock-button,
button.darkos-status-button, button.darkos-folder-button {
  background: transparent;
  color: #d8d9dd;
  border: 0;
  border-radius: 9px;
  box-shadow: none;
}
button.darkos-tab { padding: 7px 14px; }
button.darkos-tab:checked, button.darkos-tab.active {
  background: #3a2529; color: #ff7777;
}
button.darkos-nav { padding: 9px 10px; }
button.darkos-nav.active { background: #342328; color: #ff7777; }
button.darkos-dock-button { padding: 5px 10px; min-width: 68px; }
button.darkos-status-button { padding: 5px; }
button.darkos-nav:hover, button.darkos-tab:hover,
button.darkos-dock-button:hover, button.darkos-status-button:hover,
button.darkos-folder-button:hover { background: #303136; }
button.darkos-app-card {
  background: #202126;
  color: #eeeeef;
  border: 1px solid #303137;
  border-radius: 12px;
  padding: 15px;
  min-width: 125px;
  min-height: 105px;
  box-shadow: none;
}
button.darkos-app-card:hover { background: #2c2d33; border-color: #aa3c43; }
button.darkos-mode-button {
  background: #24252a; color: #c8c9ce; border: 1px solid #36373d;
  border-radius: 8px; padding: 5px 12px; box-shadow: none;
}
button.darkos-mode-button.active { background: #3b2529; color: #ff7777; border-color: #81363d; }
.darkos-empty-icon { color: #686a72; font-size: 42px; }
.darkos-terminal-hint { color: #777982; font-size: 11px; }
popover contents { background: #24252a; border: 1px solid #3a3b42; }
"""

class DarkOSApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.stack = None
        self.terminal = None
        self.mode = "RED"
        self.mode_badge = None
        self.mode_buttons = {}
        self.clock_label = None
        self.tab_buttons = {}
        self.sidebar_buttons = {}
        self.status_images = {}
        self.status_buttons = {}
        self._status_refresh_running = False

    def do_activate(self):
        if self.window is None:
            self.build_window()
        self.window.present()
        self.window.fullscreen()

    def build_window(self):
        self.install_css()

        self.window = Gtk.ApplicationWindow(application=self, title="DarkOS 1.0")
        self.window.set_default_size(1280, 720)
        self.window.add_css_class("darkos-window")

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.window.add_controller(key_controller)

        aspect = Gtk.AspectFrame(
            xalign=0.5, yalign=0.5, ratio=16 / 9, obey_child=False
        )
        aspect.set_hexpand(True)
        aspect.set_vexpand(True)

        desktop = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        aspect.set_child(desktop)
        self.window.set_child(aspect)

        desktop.append(self.build_header())
        desktop.append(self.build_tab_bar())

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        body.set_vexpand(True)
        body.append(self.build_sidebar())

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(120)
        self.stack.add_named(self.build_shell_page(), "DarkShell")
        self.stack.add_named(self.build_files_page(), "Files")
        self.stack.add_named(self.build_settings_page(), "Settings")
        self.stack.add_named(self.build_darkplay_page(), "DarkPlay")
        self.stack.add_named(self.build_apps_page(), "Apps")
        body.append(self.stack)
        desktop.append(body)
        desktop.append(self.build_dock())

        self.show_tab("DarkShell")
        self.change_mode("RED")
        self.update_clock()
        self.update_status()
        GLib.timeout_add_seconds(30, self.update_clock)
        GLib.timeout_add_seconds(20, self.update_status)

    def install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode("utf-8"))
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def label(self, text, css_class=None, xalign=0.0):
        widget = Gtk.Label(label=text)
        widget.set_xalign(xalign)
        if css_class:
            widget.add_css_class(css_class)
        return widget

    def icon_button(self, icon_name, tooltip, callback, css_class="darkos-status-button"):
        button = Gtk.Button.new_from_icon_name(icon_name)
        button.set_tooltip_text(tooltip)
        button.add_css_class(css_class)
        button.connect("clicked", callback)
        return button

    def build_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header.add_css_class("darkos-header")

        mark = self.label("●", "darkos-brand-mark")
        header.append(mark)
        brand = self.label("DarkOS 1.0", "darkos-brand")
        header.append(brand)
        header.append(self.label("DESKTOP", "darkos-muted"))

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)

        for key, icon_name, tooltip, panel in [
            ("wifi", "network-wireless-symbolic", "Wi-Fi settings", "wifi"),
            ("bluetooth", "bluetooth-active-symbolic", "Bluetooth settings", "bluetooth"),
            ("volume", "audio-volume-high-symbolic", "Sound settings", "sound"),
            ("battery", "battery-full-symbolic", "Power and battery", "power"),
        ]:
            button, image = self.status_icon_button(
                key, icon_name, tooltip, panel
            )
            header.append(button)

        self.clock_label = self.label("--:--", "darkos-muted")
        header.append(self.clock_label)

        power_button = Gtk.Button.new_from_icon_name("system-shutdown-symbolic")
        power_button.set_tooltip_text("Power menu")
        power_button.add_css_class("darkos-status-button")
        header.append(power_button)
        self.build_power_popover(power_button)
        return header

    def status_icon_button(self, key, icon_name, tooltip, panel):
        image = Gtk.Image.new_from_icon_name(icon_name)
        button = Gtk.Button()
        button.set_child(image)
        button.set_tooltip_text(tooltip)
        button.add_css_class("darkos-status-button")
        button.connect(
            "clicked",
            lambda *_args, target=panel: self.open_control_center(target)
        )
        self.status_images[key] = image
        self.status_buttons[key] = button
        return button, image

    @staticmethod
    def command_output(command, timeout=1.5):
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except (OSError, subprocess.TimeoutExpired):
            return ""

    def update_status(self):
        # Poll hardware/services in a worker so a slow command never freezes GTK.
        if not self._status_refresh_running:
            self._status_refresh_running = True
            threading.Thread(
                target=self.collect_status,
                name="darkos-status",
                daemon=True,
            ).start()
        return GLib.SOURCE_CONTINUE

    def collect_status(self):
        wifi_power = self.command_output(
            ["nmcli", "-t", "-f", "WIFI", "general"]
        ).lower()
        wifi_devices = self.command_output(
            ["nmcli", "-t", "-f", "TYPE,STATE", "device", "status"]
        ).lower()
        wifi_connected = any(
            row.startswith("wifi:connected")
            for row in wifi_devices.splitlines()
        )
        if wifi_power == "enabled" and wifi_connected:
            wifi = ("network-wireless-symbolic", "Wi-Fi: Connected")
        elif wifi_power == "enabled":
            wifi = ("network-wireless-symbolic", "Wi-Fi: Enabled, not connected")
        elif wifi_power == "disabled":
            wifi = ("network-wireless-offline-symbolic", "Wi-Fi: Disabled")
        else:
            wifi = ("network-wireless-symbolic", "Wi-Fi status unavailable")

        bluetooth = self.command_output(["bluetoothctl", "show"]).lower()
        if "powered: yes" in bluetooth:
            bt = ("bluetooth-active-symbolic", "Bluetooth: On")
        elif "powered: no" in bluetooth:
            bt = ("bluetooth-disabled-symbolic", "Bluetooth: Off")
        else:
            bt = ("bluetooth-active-symbolic", "Bluetooth status unavailable")

        mute = self.command_output(
            ["pactl", "get-sink-mute", "@DEFAULT_SINK@"]
        ).lower()
        volume = self.command_output(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"]
        )
        match = re.search(r"(\d+)%", volume)
        level = int(match.group(1)) if match else None
        if "yes" in mute:
            sound = ("audio-volume-muted-symbolic", "Sound: Muted")
        elif level is not None and level < 30:
            sound = ("audio-volume-low-symbolic", f"Sound: {level}%")
        elif level is not None and level < 70:
            sound = ("audio-volume-medium-symbolic", f"Sound: {level}%")
        elif level is not None:
            sound = ("audio-volume-high-symbolic", f"Sound: {level}%")
        else:
            sound = ("audio-volume-high-symbolic", "Sound status unavailable")

        devices = self.command_output(["upower", "-e"])
        battery_path = next(
            (line for line in devices.splitlines() if "/battery_" in line),
            None,
        )
        battery = None
        if battery_path:
            info = self.command_output(["upower", "-i", battery_path])
            percentage_match = re.search(r"percentage:\s*(\d+)%", info, re.I)
            state_match = re.search(r"state:\s*(\w+)", info, re.I)
            percentage = int(percentage_match.group(1)) if percentage_match else None
            state = state_match.group(1).lower() if state_match else "unknown"
            if percentage is None:
                battery = ("battery-full-symbolic", "Battery status unavailable")
            else:
                icon = (
                    "battery-caution-symbolic" if percentage <= 10 else
                    "battery-low-symbolic" if percentage <= 25 else
                    "battery-good-symbolic" if percentage <= 60 else
                    "battery-full-symbolic"
                )
                battery = (icon, f"Battery: {percentage}% ({state})")

        GLib.idle_add(
            self.apply_status,
            {"wifi": wifi, "bluetooth": bt, "volume": sound, "battery": battery},
        )

    def apply_status(self, statuses):
        for key in ("wifi", "bluetooth", "volume"):
            icon_name, tooltip = statuses[key]
            self.status_images[key].set_from_icon_name(icon_name)
            self.status_buttons[key].set_tooltip_text(tooltip)

        battery = statuses["battery"]
        button = self.status_buttons["battery"]
        button.set_visible(battery is not None)
        if battery is not None:
            icon_name, tooltip = battery
            self.status_images["battery"].set_from_icon_name(icon_name)
            button.set_tooltip_text(tooltip)

        self._status_refresh_running = False
        return GLib.SOURCE_REMOVE

    def build_power_popover(self, anchor):
        popover = Gtk.Popover()
        popover.set_autohide(True)
        menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        menu.set_margin_top(8)
        menu.set_margin_bottom(8)
        menu.set_margin_start(8)
        menu.set_margin_end(8)
        for caption, command in [
            ("Log out", ["gnome-session-quit", "--logout", "--no-prompt"]),
            ("Restart", ["systemctl", "reboot"]),
            ("Shut down", ["systemctl", "poweroff"]),
        ]:
            button = Gtk.Button(label=caption)
            button.add_css_class("darkos-nav")
            button.connect("clicked", lambda _b, c=command: self.power_action(c, popover))
            menu.append(button)
        close = Gtk.Button(label="Cancel")
        close.add_css_class("darkos-nav")
        close.connect("clicked", lambda *_: popover.popdown())
        menu.append(close)
        popover.set_child(menu)
        popover.set_parent(anchor)
        anchor.connect("clicked", lambda *_: popover.popup())

    def power_action(self, command, popover):
        popover.popdown()
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as exc:
            self.show_message("Power action unavailable", str(exc))

    def build_tab_bar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        bar.add_css_class("darkos-tabs")
        for name in ("DarkShell", "Files", "Settings", "DarkPlay"):
            button = Gtk.Button(label=name)
            button.add_css_class("darkos-tab")
            button.connect("clicked", lambda _b, tab=name: self.show_tab(tab))
            self.tab_buttons[name] = button
            bar.append(button)
        plus = Gtk.Button.new_from_icon_name("list-add-symbolic")
        plus.set_tooltip_text("Open applications")
        plus.add_css_class("darkos-tab")
        plus.connect("clicked", lambda *_: self.show_tab("Apps"))
        bar.append(plus)
        return bar

    def build_sidebar(self):
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sidebar.add_css_class("darkos-sidebar")
        sidebar.append(self.label("TABS", "darkos-sidebar-title"))
        for name, icon in [
            ("Files", "folder-symbolic"),
            ("Settings", "preferences-system-symbolic"),
            ("DarkPlay", "applications-games-symbolic"),
        ]:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=9)
            row.append(Gtk.Image.new_from_icon_name(icon))
            row.append(self.label(name))
            button = Gtk.Button()
            button.set_child(row)
            button.set_halign(Gtk.Align.FILL)
            button.add_css_class("darkos-nav")
            button.connect("clicked", lambda _b, tab=name: self.show_tab(tab))
            self.sidebar_buttons[name] = button
            sidebar.append(button)
        sidebar.append(Gtk.Box())  # Keeps the sidebar compact and top-aligned.
        return sidebar

    def build_shell_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        page.set_margin_top(12)
        page.set_margin_bottom(12)
        page.set_margin_start(16)
        page.set_margin_end(16)
        page.add_css_class("darkos-workspace")

        title_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_row.append(self.label("DarkShell", "darkos-page-title"))
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        title_row.append(spacer)

        self.mode_badge = self.label("RED · NORMAL", "darkos-mode mode-red")
        title_row.append(self.mode_badge)
        page.append(title_row)

        terminal_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        terminal_frame.set_hexpand(True)
        terminal_frame.set_vexpand(True)
        terminal_frame.add_css_class("darkos-terminal-frame")

        self.terminal = Vte.Terminal.new()
        self.terminal.set_hexpand(True)
        self.terminal.set_vexpand(True)
        self.terminal.set_scrollback_lines(5000)
        self.terminal.set_scroll_on_keystroke(True)
        self.terminal.set_font(Pango.FontDescription.from_string("Monospace 11"))

        foreground = Gdk.RGBA()
        foreground.parse("#d8d8dc")
        background = Gdk.RGBA()
        background.parse("#08090b")
        self.terminal.set_color_foreground(foreground)
        self.terminal.set_color_background(background)

        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_scroll.set_child(self.terminal)
        terminal_scroll.set_hexpand(True)
        terminal_scroll.set_vexpand(True)
        terminal_frame.append(terminal_scroll)
        page.append(terminal_frame)

        mode_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        mode_row.append(self.label("SHELL MODE", "darkos-muted"))
        mode_spacer = Gtk.Box()
        mode_spacer.set_hexpand(True)
        mode_row.append(mode_spacer)
        for mode in ("RED", "GREEN", "BLUE"):
            button = Gtk.Button(label=mode)
            button.add_css_class("darkos-mode-button")
            button.connect("clicked", lambda _b, value=mode: self.change_mode(value))
            self.mode_buttons[mode] = button
            mode_row.append(button)
        page.append(mode_row)

        try:
            self.terminal.spawn_async(
                Vte.PtyFlags.DEFAULT,
                str(pathlib.Path.home()),
                ["/bin/bash", "--rcfile", BASHRC, "-i"],
                None,
                GLib.SpawnFlags.DEFAULT,
                None,
                -1,
                None,
                self.on_terminal_spawned,
                None,
            )
        except Exception as exc:
            self.show_message("DarkShell could not start", str(exc))
        return page

    def on_terminal_spawned(self, _terminal, _pid, error, _user_data):
        if error:
            self.show_message("DarkShell could not start", str(error))

    def change_mode(self, mode):
        self.mode = mode
        os.makedirs(os.path.dirname(MODE_FILE), exist_ok=True)
        try:
            pathlib.Path(MODE_FILE).write_text(mode + "\n", encoding="utf-8")
        except OSError:
            pass
        label = {"RED": "RED · NORMAL", "GREEN": "GREEN · EXTRAS", "BLUE": "BLUE · WINMODE"}[mode]
        css = {"RED": "mode-red", "GREEN": "mode-green", "BLUE": "mode-blue"}[mode]
        self.mode_badge.set_text(label)
        self.mode_badge.set_css_classes(["darkos-mode", css])
        for key, button in self.mode_buttons.items():
            if key == mode:
                button.add_css_class("active")
            else:
                button.remove_css_class("active")

    def build_files_page(self):
        page = self.new_workspace("Files", "Home  /  Dark")
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        home = pathlib.Path.home()
        items = ["Desktop", "Documents", "Downloads", "Music", "Pictures", "Videos"]
        try:
            for item in sorted(home.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                if item.name not in items and not item.name.startswith("."):
                    items.append(item.name)
        except OSError:
            pass
        for name in items:
            path = home / name
            row = Gtk.Button()
            content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            content.append(Gtk.Image.new_from_icon_name(
                "folder-symbolic" if path.is_dir() or not path.exists() else "text-x-generic-symbolic"
            ))
            content.append(self.label(name))
            row.set_child(content)
            row.set_halign(Gtk.Align.FILL)
            row.add_css_class("darkos-folder-button")
            row.connect("clicked", lambda _b, target=path: self.open_path(target))
            list_box.append(row)
        scroll.set_child(list_box)
        scroll.set_vexpand(True)
        page.append(scroll)
        return page

    def build_settings_page(self):
        page = self.new_workspace("Settings", "Configure your DarkOS desktop")
        settings = [
            ("Display", "video-display-symbolic", "display"),
            ("Network", "network-wireless-symbolic", "wifi"),
            ("Bluetooth", "bluetooth-active-symbolic", "bluetooth"),
            ("Sound", "audio-volume-high-symbolic", "sound"),
            ("Appearance", "preferences-desktop-wallpaper-symbolic", "background"),
            ("About", "help-about-symbolic", "about"),
        ]
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        for index, (name, icon, panel) in enumerate(settings):
            button = Gtk.Button()
            inside = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            inside.set_margin_top(12)
            inside.set_margin_bottom(12)
            inside.set_margin_start(12)
            inside.set_margin_end(12)
            inside.append(Gtk.Image.new_from_icon_name(icon))
            inside.append(self.label(name))
            button.set_child(inside)
            button.add_css_class("darkos-app-card")
            button.connect("clicked", lambda _b, target=panel: self.open_control_center(target))
            grid.attach(button, index % 2, index // 2, 1, 1)
        page.append(grid)
        return page

    def build_darkplay_page(self):
        page = self.new_workspace("DarkPlay", "Your game library")
        empty = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=9)
        empty.set_hexpand(True)
        empty.set_vexpand(True)
        empty.set_halign(Gtk.Align.CENTER)
        empty.set_valign(Gtk.Align.CENTER)
        game_icon = Gtk.Image.new_from_icon_name("applications-games-symbolic")
        game_icon.set_pixel_size(52)
        game_icon.add_css_class("darkos-empty-icon")
        empty.append(game_icon)
        empty.append(self.label("No games added yet", "darkos-page-title"))
        empty.append(self.label("Your library will appear here when you add games.", "darkos-muted"))
        page.append(empty)
        return page

    def build_apps_page(self):
        page = self.new_workspace("Applications", "Preinstalled DarkOS applications")
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        for index, (name, app_id, icon) in enumerate(APPS):
            button = Gtk.Button()
            inside = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            inside.set_halign(Gtk.Align.CENTER)
            inside.set_valign(Gtk.Align.CENTER)
            image = Gtk.Image.new_from_icon_name(icon)
            image.set_pixel_size(34)
            inside.append(image)
            inside.append(self.label(name, xalign=0.5))
            button.set_child(inside)
            button.add_css_class("darkos-app-card")
            button.connect("clicked", lambda _b, target=app_id: self.launch_flatpak(target))
            grid.attach(button, index % 4, index // 4, 1, 1)
        page.append(grid)
        return page

    def new_workspace(self, title, subtitle):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.set_margin_top(18)
        page.set_margin_bottom(18)
        page.set_margin_start(20)
        page.set_margin_end(20)
        page.add_css_class("darkos-workspace")
        page.append(self.label(title, "darkos-page-title"))
        page.append(self.label(subtitle, "darkos-muted"))
        return page

    def build_dock(self):
        dock = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        dock.set_halign(Gtk.Align.CENTER)
        dock.add_css_class("darkos-dock")

        dock_items = [
            ("DarkShell", "utilities-terminal-symbolic", "tab"),
            ("Firefox", "web-browser-symbolic", "app"),
            ("Bazzar", "system-software-install-symbolic", "app"),
            ("Files", "folder-symbolic", "tab"),
            ("Settings", "preferences-system-symbolic", "tab"),
            ("DarkPlay", "applications-games-symbolic", "tab"),
        ]
        app_ids = {
            "Firefox": APPS[0][1], "Bazzar": APPS[1][1],
        }
        for name, icon, kind in dock_items:
            button = Gtk.Button()
            inside = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            image = Gtk.Image.new_from_icon_name(icon)
            image.set_pixel_size(21)
            inside.append(image)
            caption = Gtk.Label(label=name)
            caption.add_css_class("darkos-muted")
            inside.append(caption)
            button.set_child(inside)
            button.add_css_class("darkos-dock-button")
            if kind == "app":
                button.connect("clicked", lambda _b, target=app_ids[name]: self.launch_flatpak(target))
            else:
                button.connect("clicked", lambda _b, tab=name: self.show_tab(tab))
            dock.append(button)
        return dock

    def show_tab(self, name):
        if self.stack:
            self.stack.set_visible_child_name(name)
        for tab, button in self.tab_buttons.items():
            if tab == name:
                button.add_css_class("active")
            else:
                button.remove_css_class("active")
        for tab, button in self.sidebar_buttons.items():
            if tab == name:
                button.add_css_class("active")
            else:
                button.remove_css_class("active")

    def update_clock(self):
        if self.clock_label:
            now = GLib.DateTime.new_now_local()
            self.clock_label.set_text(now.format("%-I:%M %p"))
        return GLib.SOURCE_CONTINUE

    def launch_flatpak(self, app_id):
        if app_id == "org.mozilla.firefox":
            self.launch_command(["firefox"])
            return
        if not shutil.which("flatpak"):
            self.show_message("Flatpak is unavailable", "The Flatpak command is not installed.")
            return
        check = subprocess.run(
            ["flatpak", "info", "--system", app_id],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if check.returncode != 0:
            self.show_message(
                "Bazzar is still being installed",
                "The first-boot setup installs Bazzar from Flathub after the Pi connects to the internet."
            )
            return
        try:
            subprocess.Popen(
                ["flatpak", "run", "--system", app_id],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        except OSError as exc:
            self.show_message("Could not launch application", str(exc))

    def open_control_center(self, panel):
        commands = {
            "display": ["wdisplays"],
            "wifi": ["nm-connection-editor"],
            "bluetooth": ["blueman-manager"],
            "sound": ["pavucontrol"],
            "background": ["lxappearance"],
            "about": ["foot", "-e", "fastfetch"],
        }
        command = commands.get(panel)
        if command and shutil.which(command[0]):
            self.launch_command(command)
        else:
            self.show_message(
                "Setting unavailable",
                "That control panel is not included in this lightweight Raspberry Pi build."
            )

    def open_path(self, path):
        target = path if path.exists() else pathlib.Path.home()
        self.launch_command(["thunar", str(target)])

    def launch_command(self, command):
        try:
            subprocess.Popen(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        except OSError as exc:
            self.show_message("Could not open application", str(exc))

    def show_message(self, title, details):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title,
        )
        dialog.set_secondary_text(details)
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()

    def on_key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_F12:
            # Exit the shell and return to the autologin console.
            self.window.unfullscreen()
            self.quit()
            return True
        if keyval == Gdk.KEY_F11:
            self.window.unfullscreen()
            return True
        return False


def main():
    app = DarkOSApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
