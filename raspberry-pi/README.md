# DarkOS Raspberry Pi 4

This directory contains the Raspberry Pi 4 ARM64 bring-up image workflow.

## Target

- Board: Raspberry Pi 4 Model B
- Architecture: AArch64 (64-bit ARM)
- Base: Arch Linux ARM Raspberry Pi aarch64 root filesystem
- Image: raw disk image compressed as `.img.gz`
- Partition layout: FAT32 boot partition plus ext4 root partition

## Build

Run the **DarkOS Raspberry Pi 4 Image** workflow from the GitHub Actions tab, or push a change under `raspberry-pi/` to the `main` or `raspberry-pi-4` branch. Download the artifact named `DarkOS-Raspberry-Pi-4-aarch64-development`.

## Important development status

This is an initial ARM hardware bring-up image based on the Arch Linux ARM Raspberry Pi root filesystem. It is **not yet the complete DarkOS desktop edition**: DarkShell, GNOME, the DarkOS first-boot setup, and a tested update/recovery flow still need to be integrated and validated for the Pi.

The image is intended for a spare microSD card and test hardware only. Writing it to a card erases that card. Confirm the device by model and capacity before writing; never guess a `/dev/sdX` or `/dev/mmcblkX` device name.

The upstream Arch Linux ARM image has its own initial account and credential policy. Before connecting a test Pi to an untrusted network, follow the current Arch Linux ARM Raspberry Pi documentation to change default credentials and complete its recommended first-boot setup.

Do not use this image for important data or as a production system. Test it on a spare Raspberry Pi 4 and spare microSD card.
