#!/usr/bin/env bash
set -euo pipefail

# Configure the live environment for the DarkOS development ISO.
useradd --create-home --groups wheel --shell /bin/bash dark
printf 'dark ALL=(ALL:ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/10-darkos-live
chmod 0440 /etc/sudoers.d/10-darkos-live

systemctl enable NetworkManager.service
systemctl enable gdm.service
