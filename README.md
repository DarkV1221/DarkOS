# DarkOS — Arch Port

DarkOS is being ported from its original Fedora Atomic / BlueBuild foundation to **Arch Linux**.

This work is happening on the `arch-port` branch. The existing `main` branch remains unchanged while the Arch image is developed and tested.

## Direction

- **Base:** Arch Linux (rolling release)
- **Image builder:** `archiso`
- **Desktop session:** GNOME, retained initially to host the existing DarkOS GTK4 shell
- **Primary interface:** DarkShell
- **Package management:** pacman
- **Planned update client:** DarkUpdate (not implemented yet)
- **Planned app catalog:** DarkBazzar (not implemented yet)

## Current development image

The `archiso/` directory contains an initial x86_64 Archiso profile. It includes the existing DarkShell GTK4 application, GNOME, GDM, NetworkManager, and Arch's `archinstall` installer utility.

The GitHub Actions workflow **DarkOS Arch ISO** builds a development ISO and uploads it as an artifact. This is an early development image, not a finished or hardware-validated installer. Test it in a virtual machine first.

The live session currently creates a temporary `dark` user with passwordless sudo for development convenience. Do not treat this live-image configuration as a secure installed-system account policy. A proper installer and first-boot account setup are still required.

## Build locally

On an Arch Linux build machine:

```bash
sudo pacman -Syu --needed archiso
chmod +x archiso/airootfs/root/customize_airootfs.sh
sudo mkarchiso -v -w /tmp/darkos-work -o out archiso
```

## Migration status

- [x] Create a separate Arch port branch
- [x] Add an initial Archiso profile and package list
- [x] Add a GitHub Actions ISO build workflow
- [x] Include the existing DarkShell application in the live image
- [ ] Run and fix the first CI build
- [ ] Test boot and GNOME/DarkShell startup in a VM
- [ ] Design a proper installer and installed-system configuration
- [ ] Implement signed, controlled rolling updates (DarkUpdate)
- [ ] Retire the Fedora Atomic / BlueBuild build path after the Arch port is validated

## Important

The Arch port is not yet a replacement for the existing Fedora-based ISO. Do not install this development image on a machine containing important data. The installer, partitioning flow, secure account setup, recovery, and update system still need engineering and testing.
