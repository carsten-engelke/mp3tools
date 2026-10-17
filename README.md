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
```
Usage: mp3tools merge-mp3 [dir] [subdir-mode] [foobarpath] [autowaittime]
Usage: mp3tools pack-subdirs [group-size] [dir] [file-filter] [copy-mode]
Usage: mp3tools unpack-subdirs [dir] [subdir-filter] [file-filter] [copy-mode] [removesubdir-mode]
Usage: mp3tools wait=seconds
Note: This script depends on a foobar2000 installation! (Get it from: https://www.foobar2000.org/)
```
