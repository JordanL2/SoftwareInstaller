# Description

Software installer to provide single interface for multiple software sources: software repo, flatpak etc.

# Supported Sources

Sources currently supported:
* Flatpak
* Pacman
* Yaourt (AUR)

# Usage

```
search <NAME> [--csv] [--noheader] [--status=N,I,U]
```
Search all sources for any package matching `<NAME>`.
Status indicator:
	* Blank - Uninstalled
	* `[I]` - Installed, up to date
	* `[U]` - Installed, an update is available.

If the --csv flag is present, outputs table in CSV format.

The --noheader flag suppresses the header row.

The --status flag filters the results based on its installation status. Multiple status types are possible.
* N - Not installed
* I - Installed, up to date
* U - Installed, an update is available

```
local [<NAME>] [--csv] [--noheader] [--status=N,I,U]
```
Search locally installed packages for any package matching `<NAME>`. `<NAME>` is optional, if not given returns all packages. The table format is the same as `search`.

The --csv, --noheader and --status flags work the same as they do for `search`.

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
