# Description

Software installer to provide single interface for multiple software sources: software repo, flatpak etc.

# Supported Sources

Sources currently supported:
* Flatpak
* Pacman
* Yaourt (AUR)

# Usage

```
search <NAME>
```
Search all sources for any package matching `<NAME>`. The result table columns are:
* Status indicator:
	* Blank means uninstalled
	* `[I]` means installed
	* `[U]` means installed and an update is available.
* Source
* Reference
* Name
* Version available in remote source
* Version installed locally, if any
* Description

```
local [<NAME>]
```
Search locally installed packages for any package matching `<NAME>`. `<NAME>` is optional, if not given returns all packages. The table format is the same as `search`.

```
show <REF>
```
Show information about a specific package.

```
install <REF>
```
Install package.

```
remove <REF>
```
Uninstall package.
