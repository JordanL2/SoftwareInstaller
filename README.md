# Description

Software installer to provide single interface for multiple software sources: software repo, flatpak etc.

# Supported Sources

Sources currently supported:
* Flatpak
* Pacman
* Yay (AUR)

# Installation

```
sudo pip3 install .
```

# Usage

```
search <NAME> [--csv] [--noheader] [--status=N,I,U]  [--source=<SOURCE>[,<SOURCE>...]]
```
Search all sources for any package matching `<NAME>`.
Status indicator:
	* Blank - Uninstalled
	* `[I]` - Installed, up to date
	* `[U]` - Installed, an update is available.

If the --csv flag is present, outputs table in CSV format.

The --noheader flag suppresses the header row.

The --status argument filters the results based on its installation status. Multiple status types are possible, seperated by a comma, e.g. "I,U".
* N - Not installed
* I - Installed, up to date
* U - Installed, an update is available

The --source argument only searches the given source(s), identified by the source ID. Multiple sources are possible, seperated by a comma, e.g. "flatpak,pacman".

```
local [<NAME>] [--csv] [--noheader] [--status=N,I,U]
```
Search locally installed packages for any package matching `<NAME>`. `<NAME>` is optional, if not given returns all packages. The table format is the same as `search`.

The --csv, --noheader, --status and --source arguments work the same as they do for `search`.

```
info <REF>
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

```
update [<REF>...] [-y]
```
Updates packages. By default updates everything, if one or more `<REF>` is given will only update those packages.

All available updates are shown in a table, and confirmation is required before proceeding.

If -y flag is given, the update is performed without asking for confirmation.
