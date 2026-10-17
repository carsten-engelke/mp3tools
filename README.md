# mp3tools
Merge mp3 files and set correct audio length using foobar2000 with an automated python script. These scripts can merge all files in one directory or create one file for each subdirectory.


![merge mp3 files from subdirectories](https://github.com/carsten-engelke/mp3tools/blob/main/mergemp3subdirs.jpg)
 - mp3tools merge-mp3: merging script, works with foobar2000
 - mp3tools pack-subdirs: pack files into grouped subdirectories (good for large audiobooks)
 - mp3tools unpack-subdirs.py: unpack files from grouped subdirectories (undo mp3tools pack-subdirs)

## Version
1.2.2 Fixed 

1.2.0 Added PI/CI Support thanks to https://github.com/rochacbruno/python-project-template

1.0.0 release version. Ported to vscode.

0.2.0 bug corrected foobar needs to be called from working directory as the command line plugin cannot handle empty spaces in file names or paths given by command line

0.1.0 initial release. Port from windows script to python, introducing automation

## Requirements
- Python (script was created using python 3.7.0) (https://www.python.org/)
- foobar2000 (https://www.foobar2000.org/)

## Installation
pip install mp3tools

## Usage
Command-line-use:
```
mp3tools -> start tools using the interactive wizard.
mp3tools --help -> show available commands and options.
mp3tools merge-mp3 --help -> show command-specific help.

mp3tools merge-mp3 [DIR] [SUBDIR-MODE] [FOOBAR-PATH] [SECONDS]
    DIR: folder containing MP3 files (default: current directory)
    SUBDIR-MODE: merge each subfolder separately; if omitted, choose interactively
    FOOBAR-PATH: legacy positional executable path; prefer --foobar-path
    SECONDS: auto-close delay (default: 5; use -1 to disable)

mp3tools pack-subdirs [GROUP-SIZE] [DIR] [FILE-FILTER] [COPY-MODE]
    GROUP-SIZE: maximum files per subdirectory (default: 15; must be positive)
    DIR: folder containing files (default: current directory)
    FILE-FILTER: case-sensitive substring selecting files (default: '.mp3')
    COPY-MODE: copy rather than move (default: false)

mp3tools unpack-subdirs [DIR] [SUBDIR-FILTER] [FILE-FILTER] [COPY-MODE] [REMOVE-SUBDIRS]
    DIR: folder containing subdirectories (default: current directory)
    SUBDIR-FILTER: case-sensitive substring; '*' selects all (default: 'subdir-')
    FILE-FILTER: case-sensitive substring selecting files (default: '.mp3')
    COPY-MODE: copy rather than move (default: false)
    REMOVE-SUBDIRS: remove emptied subdirectories (default: true)

mp3tools wait [SECONDS]
    set the foobar2000 auto-close delay before opening the interactive wizard

Boolean arguments accept true/false, yes/no, y/n, ja/nein, 1/0, and on/off.
For COPY-MODE, 'move' is also accepted as false. Use --foobar-path PATH and
--mp3tag-path PATH to set executable locations; both default to their configured
paths and may be placed before or after a subcommand. The legacy `wait=SECONDS`
form remains supported.
```