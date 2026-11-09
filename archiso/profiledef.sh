#!/usr/bin/env bash
# archiso profile for DarkOS. This builds a bootable development ISO;
# it is not yet a finished graphical installer.
iso_name="darkos"
iso_label="DARKOS_$(date +%Y%m)"
iso_publisher="DarkOS"
iso_application="DarkOS Arch Linux live environment"
iso_version="$(date +%Y.%m.%d)"
install_dir="darkos"
buildmodes=('iso')
bootmodes=('uefi.systemd-boot')
arch=('x86_64')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
)
