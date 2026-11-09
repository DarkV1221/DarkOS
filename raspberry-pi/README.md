# DarkOS Raspberry Pi 4

This directory contains the Raspberry Pi 4 ARM64 bring-up image and the dedicated 2GB memory profile.

## Target

- Board: Raspberry Pi 4 Model B with 2GB RAM
- Architecture: AArch64 (64-bit ARM)
- Base: Arch Linux ARM Raspberry Pi aarch64 root filesystem
- Image: raw disk image compressed as `.img.gz`
- Partition layout: FAT32 boot partition plus ext4 root partition
- Memory goal: stay lean and avoid a full GNOME desktop stack on the Pi

## 2GB memory profile

The image applies a small set of conservative, low-memory settings:

- A 768MiB zram swap device using LZ4 compression. This is compressed RAM-backed swap, not a swap file on the microSD card.
- Higher swappiness so inactive pages can move to compressed zram before the system runs out of memory.
- Bounded dirty-page writeback to avoid large bursts of cached writes.
- Bounded system and runtime journal sizes.
- No GNOME Shell, GDM, or heavyweight desktop bundle is added by this Pi image.
- NetworkManager is enabled for networking; optional hardware services should be started only when needed.

The plan is to run the DarkOS interface over a lightweight session instead of copying the PC edition's GNOME session onto a 2GB board. The current image is still an early ARM bring-up base: the DarkShell graphical session and lightweight window manager are **not integrated yet**.

These settings are a starting profile, not a benchmark claim. Real idle and workload memory use must be measured on the actual Pi 4 before calling the edition fully optimized.

## Build

Run the **DarkOS Raspberry Pi 4 Image** workflow from GitHub Actions, or push a change under `raspberry-pi/` to the `main` or `raspberry-pi-4` branch. Download the artifact named `DarkOS-Raspberry-Pi-4-aarch64-2GB-development`.

## Important development status

This is an initial hardware bring-up image based on the Arch Linux ARM Raspberry Pi root filesystem. It is **not yet the complete DarkOS desktop edition**: DarkShell, the lightweight graphical session, first-boot account setup, and a tested update/recovery flow still need to be integrated.

The image is intended for a spare microSD card and test hardware only. Writing it to a card erases that card. Confirm the target device by model and capacity before writing; never guess a `/dev/sdX` or `/dev/mmcblkX` device name.

The upstream Arch Linux ARM image has its own initial account and credential policy. Before connecting a test Pi to an untrusted network, follow the current Arch Linux ARM Raspberry Pi documentation to change default credentials and complete its recommended first-boot setup.

Do not use this image for important data or as a production system. Test it on a spare Raspberry Pi 4 and spare microSD card.
