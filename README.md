# Description

Software installer to provide single interface for multiple software sources: software repo, flatpak etc.

# Supported Sources

Sources currently supported:
* Flatpak
* Pacman
* Zypper
* Yay (AUR)

# Installation

```
sudo pip3 install .
```

# Usage

## Remote Search

```
usage: si search [-h] [--source [{flatpak,pacman,yay} ...]] [--status [{N,I,U} ...]] [--column [{STATUS,SOURCE,REF,NAME,AVAILABLE,INSTALLED} ...]] [--csv] [--noheader] TERM [TERM ...]

positional arguments:
  TERM                  terms to search for

options:
  -h, --help            show this help message and exit
  --source [{flatpak,pacman,yay} ...]
                        sources to search
  --status [{N,I,U} ...]
                        filter results on installation status: [N]ot installed, [I]nstalled, [U]pdate available
  --column [{STATUS,SOURCE,REF,NAME,AVAILABLE,INSTALLED} ...]
                        choose the columns in results table
  --csv                 output table in CSV format
  --noheader            suppress outputting the header row
```

## Local Search

```
usage: si local [-h] [--source [{flatpak,pacman,yay} ...]] [--status [{N,I,U} ...]] [--column [{STATUS,SOURCE,REF,NAME,AVAILABLE,INSTALLED} ...]] [--csv] [--noheader] [TERM ...]

positional arguments:
  TERM                  terms to search for

options:
  -h, --help            show this help message and exit
  --source [{flatpak,pacman,yay} ...]
                        sources to search
  --status [{N,I,U} ...]
                        filter results on installation status: [N]ot installed, [I]nstalled, [U]pdate available
  --column [{STATUS,SOURCE,REF,NAME,AVAILABLE,INSTALLED} ...]
                        choose the columns in results table
  --csv                 output table in CSV format
  --noheader            suppress outputting the header row
```

## Show Package Info

```
usage: si info [-h] REF

positional arguments:
  REF         package reference

options:
  -h, --help  show this help message and exit
```

## Install Package

```
usage: si install [-h] REF

positional arguments:
  REF         package reference

options:
  -h, --help  show this help message and exit
```

## Remove Package

```
usage: si remove [-h] REF

positional arguments:
  REF         package reference

options:
  -h, --help  show this help message and exit
```

## Update Packages

```
usage: si update [-h] [--source [{flatpak,pacman,yay} ...]] [-y] [--force] [REF ...]

positional arguments:
  REF                   package reference

options:
  -h, --help            show this help message and exit
  --source [{flatpak,pacman,yay} ...]
                        sources to update
  -y                    update without asking for confirmation
  --force               run pre/post tasks even if there are no updates available
```

# Configuration

Optionally, you can configure the tool with a config file placed at
```
~/.config/softwareinstaller/config
```

Each line is a KEY=VALUE pair.

## Configuration options

```
apps.ref.delimiter=<DELIMITER>
```

Default: `:`

Determines the delimiter in application references.


```
sources.autodetect=true|false
```

Default: true

Automatically detects available sources by checking for installed tools.


```
sources.<SOURCE_ID>.enable=true|false
```

Explicitly enables or disables a given source.


```
install.tasks.pre=<COMMAND>
install.tasks.post=<COMMAND>
remove.tasks.pre=<COMMAND>
remove.tasks.post=<COMMAND>
update.tasks.pre=<COMMAND>
update.tasks.post=<COMMAND>
```

Adds a script or command to be run before or after an install, remove or update run. Can be a shell command. These options can each be given as many times as needed, and will run each task in the order given.
