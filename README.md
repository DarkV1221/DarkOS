# DarkOS 1.0

[![BlueBuild](https://github.com/DarkV1221/DarkOS/actions/workflows/build.yml/badge.svg)](https://github.com/DarkV1221/DarkOS/actions/workflows/build.yml)

DarkOS is a Fedora Atomic desktop project built on the Universal Blue Silverblue image. Version 1.0 introduces the DarkOS visual desktop shell, DarkShell terminal, and the initial preinstalled application set.

## DarkOS 1.0 desktop

The first shell milestone is a full-screen GTK4 desktop layer that starts automatically in the GNOME session. It uses a fixed **16:9 workspace** and the approved DarkOS layout:

- Dark charcoal surfaces with red accents.
- Top system bar with connectivity, sound, battery, clock, and power controls.
- Tabs for DarkShell, Files, Settings, and DarkPlay, plus an Applications page.
- A TABS sidebar for Files, Settings, and DarkPlay.
- A bottom dock with the main shell, the requested applications, and system pages.
- DarkShell embeds VTE and runs a real interactive Bash session.
- F12 closes the DarkOS shell and returns to the underlying GNOME desktop as a recovery path.

This is the first desktop implementation, not yet a replacement GNOME Shell or a finished installer ISO. GNOME continues to provide the session, hardware integration, and underlying desktop services.

## Preinstalled applications

DarkOS configures these Flathub applications for all users:

| Application | Flatpak ID |
| --- | --- |
| Firefox | `org.mozilla.firefox` |
| Steam | `com.valvesoftware.Steam` |
| Prism Launcher | `org.prismlauncher.PrismLauncher` |
| Bazzite Bazaar | `io.github.kolunmi.Bazaar` |

The default-Flatpak setup runs during first boot. App launchers show a helpful message if the initial installation is still running.

## DarkShell commands

DarkShell is Bash with a small DarkOS command layer. Bash builtins and normal Linux commands remain available.

| Command | Purpose |
| --- | --- |
| `Help` | Show DarkShell custom commands |
| `Lord` | Run a command with sudo authentication |
| `find` | Search files and folders |
| `file` | Create an empty file |
| `folder` | Create a folder |
| `delete` | Interactively remove files or folders |
| `FileInfo` | Print a text file |
| `Neofetch` | Show system information |
| `clear` | Clear the terminal |

On Fedora 45, the original Neofetch RPM is not in the Fedora repositories. DarkShell therefore runs Neofetch if it is present, and otherwise displays a built-in DarkOS system summary. Fastfetch is not substituted.

## Building

Every push and pull request runs a Python syntax check, a Bash syntax check, and the BlueBuild image workflow.

The image is signed when the GitHub Actions repository secret `SIGNING_SECRET` contains the Cosign private key matching the repository's `cosign.pub`. Until that secret is configured, CI uses BlueBuild's `--no-sign` option and publishes an **unsigned development image**. Do not treat an unsigned development image as verified. See the [BlueBuild Cosign setup guide](https://blue-build.org/how-to/cosign/) before enabling signed releases.

## Installer ISO

The **DarkOS ISO** GitHub Actions workflow builds a complete x86_64 installer ISO from `recipes/recipe.yml`. It uses BlueBuild's ISO generator with the Silverblue installer variant, matching DarkOS's GNOME-based Silverblue foundation. The locally built DarkOS image is bundled into the installer, so the OS payload does not need to be downloaded from GHCR during installation.

When the workflow succeeds:

1. Open the repository's [Actions page](https://github.com/DarkV1221/DarkOS/actions/workflows/iso.yml).
2. Open the latest successful **DarkOS ISO** run.
3. Download the **DarkOS-1.0-x86_64** artifact. It contains the ISO and its SHA-256 checksum.

Artifacts are retained for 90 days, so download and keep a copy somewhere safe.

This is an installer ISO, not a live desktop session. It installs DarkOS onto a selected drive. The first boot downloads the configured system Flatpaks (Firefox, Steam, Prism Launcher, and Bazaar), so an internet connection is needed to finish setting up those applications. The current ISO target is x86_64 PCs.

The installer has not yet been validated on physical hardware. Test it in a virtual machine first. Installing an operating system can erase data on the selected drive; back up important files and get help from a trusted adult before installing it on a real computer.

The ISO workflow runs when the recipe, system files, modules, or ISO workflow change on `main` or `darkos-1.0-desktop`. It can also be started manually from GitHub Actions after the workflow is present on the default branch.

## Base image

DarkOS currently tracks `ghcr.io/ublue-os/silverblue-main:latest`. The base image provides the GNOME session and Atomic update foundation; DarkOS adds the shell and application configuration on top.
