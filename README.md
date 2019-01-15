# Description

Software installer to provide single interface for multiple software sources: software repo, flatpak etc.

# Supported Sources

Sources currently supported:
* Flatpak
* Pacman
* Yaourt (AUR)

# Usage

`search <NAME>`
Search all sources for any package matching <NAME>.

`local [<NAME>]`
Search locally installed packages for any package matching <NAME>. <NAME> is optional, if not given returns all packages.

`show <REF>`
Show information about a specific package.

`install <REF>`
Install package.

`remove <REF>`
Uninstall package.
