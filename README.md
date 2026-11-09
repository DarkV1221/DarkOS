# DarkOS 1.0

DarkOS is an Arch Linux-based desktop project with a terminal-first identity and a custom GTK4 desktop shell.

## Platform

- **Base operating system:** Arch Linux (rolling release)
- **Package manager:** pacman
- **Image builder:** archiso
- **Desktop session:** GNOME, initially retained for session and hardware integration
- **Primary interface:** DarkShell / the DarkOS GTK4 desktop shell
- **Planned update client:** DarkUpdate (not implemented yet)
- **Planned application catalog:** DarkBazzar (not implemented yet)

The project no longer uses Fedora Atomic, Silverblue, rpm-ostree, or BlueBuild as its build foundation.

## DarkOS desktop

The current shell milestone is a full-screen GTK4 desktop layer that starts automatically in the GNOME session. It uses a fixed **16:9 workspace** and the approved DarkOS layout:

- Dark charcoal surfaces with red accents.
- Top system bar with connectivity, sound, clock, and power controls.
- Tabs for DarkShell, Files, Settings, and DarkPlay, plus an Applications page.
- A TABS sidebar for Files, Settings, and DarkPlay.
- A bottom dock with the main shell, requested applications, and system pages.
- DarkShell embeds VTE and runs a real interactive Bash session.
- GNOME remains underneath as a development recovery path; this is not yet a replacement GNOME Shell.

## Included applications

The development image currently includes:

- Firefox
- Steam
- Prism Launcher
- Fastfetch

The GTK4 shell also contains launch entries for the planned application set. Not every launcher is guaranteed to have its application installed in this early image.

## Building the development ISO

The `archiso/` directory contains the x86_64 Archiso profile.

On an Arch Linux build machine:

```bash
sudo pacman -Syu --needed archiso
chmod +x archiso/airootfs/root/customize_airootfs.sh
sudo mkarchiso -v -w /tmp/darkos-work -o out archiso
```

The GitHub Actions workflow **DarkOS Arch ISO** builds the development ISO and uploads it as an artifact. It runs for relevant pushes to `main` and can also be started manually from GitHub Actions.

## Current development-image limitations

This is an **early Arch-based development ISO**, not a finished, validated installer or a production-ready operating system.

- The image boots a live GNOME session and starts the DarkOS shell.
- `archinstall` is included as an installer utility, but DarkOS does not yet provide its own tested `archinstall` profile.
- The live session creates a temporary `dark` user with passwordless sudo for development convenience. This is not a secure installed-system account policy.
- The installer flow, disk/partition handling, first-boot account setup, recovery, and installed-system configuration still need engineering and testing.
- DarkUpdate and signed, controlled rolling updates are not implemented yet.
- The ISO has not yet been validated on physical hardware. Test it in a virtual machine first.

Do not install a development image on a machine containing important data. Installing an operating system can erase data on the selected drive; back up important files and get help from a trusted adult before installing it on real hardware.

## Roadmap

- [x] Move the project build foundation to Arch Linux and archiso
- [x] Make the Arch ISO workflow the primary build workflow
- [x] Remove the Fedora Atomic / BlueBuild build configuration from the primary branch
- [ ] Run and fix the first Arch ISO CI build
- [ ] Test boot and GNOME/DarkShell startup in a virtual machine
- [ ] Design a proper installer and installed-system configuration
- [ ] Create and test a DarkOS `archinstall` profile
- [ ] Implement signed, controlled rolling updates (DarkUpdate)
- [ ] Implement DarkBazzar and its package/repository integration
