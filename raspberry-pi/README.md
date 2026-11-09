# DarkOS 1.0 Raspberry Pi 4 desktop

This is the separate 64-bit ARM edition of DarkOS 1.0 for the Raspberry Pi 4 Model B with 4GB RAM. It does not change the x86_64 PC build.

## What the image includes

- Arch Linux ARM (AArch64) base and Raspberry Pi firmware
- The existing DarkOS 1.0 GTK4 desktop shell, copied into the image at build time
- Cage, a small Wayland kiosk compositor that launches directly into the full-screen DarkOS shell
- DarkShell with RED Normal, GREEN Extras, and BLUE WinMode selectors
- Files, Settings, DarkPlay, application page, and the charcoal/black with red-accent UI
- Firefox, Thunar, Fastfetch, PipeWire audio, NetworkManager, Bluetooth tools, and lightweight settings utilities
- Bazzar app-store setup from Flathub on first boot after networking is available
- A 1GiB zram swap profile and bounded system journal

## First boot

The Pi starts the DarkOS desktop automatically under the unprivileged alarm account. The account is automatically signed in on the local display so the Pi can boot straight to the desktop. It is in the wheel group. This is a development image, not a production security policy; change the default Arch Linux ARM credentials before using it on an untrusted network.

If the desktop does not start, press Ctrl+Alt+F2 to reach another console and log in with the Arch Linux ARM account credentials. The image remains a development build and has not been physically validated on every Pi 4 display/cable combination.

## Build and download

The DarkOS Raspberry Pi 4 Image workflow builds the compressed raw disk image and uploads an artifact named DarkOS-1.0-Raspberry-Pi-4-aarch64-4GB-desktop-development. Flash the .img.gz image with Raspberry Pi Imager or another trusted image-writing tool.

The image is 12GB before compression and requires a microSD card with at least 16GB capacity. Writing an image erases the selected card; verify the target carefully.

## Current limitations

- This is an early desktop integration, not a fully validated release.
- Bazaar installs in the background after the first successful network connection.
- Steam and Prism Launcher are not included in this ARM build.
- BLUE WinMode is a UI mode only on the Pi build; Windows executable compatibility is not included.
