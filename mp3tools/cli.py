# # Merge mp3 files from the current directory or from subfolders (each into one mp3 file)
# Group files into subfolders. Create groups of a certain size.
# Ungroup files from subfolders.
# Carsten Engelke 2023

import argparse
import os
import subprocess
import sys
import time

from _thread import start_new_thread
from pynput.keyboard import Controller, Key  # type: ignore
import math as m
from shutil import copyfile

__all__ = ["main", "mergemp3", "packsubdirs", "unpackdirs"]

VERSIONSTR = "1.0.8 (C)opyright Carsten Engelke 2022"
foobarpath = "C:/Users/carst/scoop/shims/foobar2000.exe"
mp3tagpath = "C:/Users/carst/scoop/shims/mp3tag.exe"
workingdir = os.getcwd()
autowaittime = 5
groupsize = 15
filefilter = ".mp3"
subdirfilter = "subdir-"
copymode = False
removesubdirmode = True
yes = ["yes", "y", "ja", "j", "", "1"]


def mergesubdirs(dir, foobarpath, autowaittime):
    filelist = []
    with os.scandir(dir) as it:
        for subdir in it:
            if not subdir.name.startswith(".") and subdir.is_dir():
                aimfile = mergedir(subdir, True)
                if aimfile != None:
                    filelist.append(aimfile)
    callfoobar(foobarpath, dir, filelist, autowaittime)
    print("Merging subdirectories of " + dir + " done.")


def mergedir(dir, copytoparent):
    if copytoparent:
        filestr = os.path.dirname(dir.path) + os.sep + dir.name + ".mp3"
    else:
        filestr = (
            os.path.dirname(dir) + os.sep + os.path.basename(dir) + ".mp3"
        )
    mp3number = " ".join(os.listdir(dir)).count(".mp3")
    mp3now = 0
    if mp3number > 0:
        print(
            "mp3 file found. Merging to: " + filestr + "...0%\r",
            end=" ",
            flush=True,
        )
        if os.path.exists(filestr):
            os.remove(filestr)
        with open(filestr, "ab") as aimfile:
            with os.scandir(dir) as it:
                for f in it:
                    if f.name.endswith(".mp3") and f.is_file():
                        mp3now += 1
                        srcfile = open(f, "rb")
                        aimfile.write(srcfile.read())
            return aimfile
    else:
        print("No mp3 in '" + dir.path + "' found.")
        return None


def callfoobar(foobarpath, workdir, filelist, autowaittime):
    # if not in windows skip foobar2000 execution
    if os.name == "nt":
        filenamelist = []
        for f in filelist:
            filenamelist.append(f.name)
        rebuildcmdlist = [foobarpath]
        rebuildcmdlist.append("/runcmd-files=Util/Rebuild")
        rebuildcmdlist.extend(filenamelist)
        fixcmdlist = [foobarpath]
        fixcmdlist.append("/runcmd-files=Util/Fix")
        fixcmdlist.extend(filenamelist)
        minimizecmdlist = [foobarpath]
        minimizecmdlist.append(
            "/runcmd-files=Utilities/Optimize file layout + minimize file size"
        )
        minimizecmdlist.extend(filenamelist)
        os.chdir(workdir)
        if autowaittime >= 0:
            print(
                "Calling foobar2000 for rebuilding the mp3 stream. Automatically ending in:"
                + str(autowaittime * len(filenamelist)),
                end="...",
                flush=True,
            )
            start_new_thread(
                closefoobar, (foobarpath, autowaittime, len(filelist), True)
            )
        else:
            print(
                "Calling foobar2000 for rebuilding the mp3 stream. Please close the foobar window to continue",
                end="...",
                flush=True,
            )
        subprocess.call(rebuildcmdlist)
        print("done")
        if autowaittime >= 0:
            print(
                "Calling foobar2000 for fixing the mp3 metadata length. Automatically ending in:"
                + str(autowaittime * len(filenamelist) / 2),
                end="...",
                flush=True,
            )
            start_new_thread(
                closefoobar,
                (foobarpath, autowaittime / 2, len(filelist), True),
            )
        else:
            print(
                "Calling foobar2000 for fixing the mp3 metadata length. Please close the foobar window to continue",
                end="...",
                flush=True,
            )
        subprocess.call(fixcmdlist)
        print("done")
        if autowaittime >= 0:
            print(
                "Calling foobar2000 for minimizing file. Automatically ending in "
                + str(autowaittime * len(filenamelist) / 3),
                end="...",
                flush=True,
            )
            start_new_thread(
                closefoobar,
                (foobarpath, autowaittime / 3, len(filelist), False),
            )
        else:
            print(
                "Calling foobar2000 for minimizing file. Please close the foobar window to continue",
                end="...",
                flush=True,
            )
        subprocess.call(minimizecmdlist)
        print("done")
        return True
    else:
        print(
            "foobar2000 onyl available in windows - skipping. Use mp3diags manually in linux e.g."
        )
        return False


def closefoobar(foobarpath, sleeptime, filenumber, press):
    closecmdlist = [foobarpath, "/exit"]
    k = Controller()
    if press:
        time.sleep(sleeptime)
        k.press(Key.enter)
        k.release(Key.enter)
    time.sleep(sleeptime * filenumber)
    subprocess.call(closecmdlist)


def mergemp3(dir, mergesub, foobarpath, autowaittime):

    print(
        "calling mergemp3 [mergesub="
        + str(mergesub)
        + "] [dir="
        + dir
        + "] [foobarpath="
        + foobarpath
        + "]  [autowaittime="
        + str(autowaittime)
        + "]"
    )

    if mergesub:
        mergesubdirs(dir, foobarpath, autowaittime)
    else:
        aimfile = mergedir(dir, False)
        if aimfile != None:
            callfoobar(foobarpath, dir, [aimfile], autowaittime)
        print("Merging mp3s in " + dir + " done.")


def packsubdirs(groupsize, dir, filter, copy):

    l = []
    with os.scandir(dir) as it:
        for entry in it:
            if entry.name.find(filter) >= 0 and os.path.isfile(entry):
                l.append(entry)
    dirnum = m.ceil(len(l) / groupsize)
    anz = 0
    dirnumactual = 1
    dirname = dir + "/subdir-" + str(dirnumactual)
    try:
        os.makedirs(dirname)
    except:
        print("directory already exists")
    for entry in l:
        if anz >= groupsize:
            anz = 0
            dirnumactual += 1
            dirname = dir + "/subdir-" + str(dirnumactual)
            print("create: " + dirname)
            try:
                os.mkdir(dirname)
            except:
                print("directory already exists")
        if copy:
            copyfile(dir + "/" + entry.name, dirname + "/" + entry.name)
            print("FILE_COPIED: " + entry.name)
        else:
            os.rename(dir + "/" + entry.name, dirname + "/" + entry.name)
            print("FILE_MOVED: " + entry.name)
        anz += 1


def unpackdirs(workdir, subdirfilter, filefilter, copy, remove):
    l = []
    with os.scandir(workdir) as it:
        for entry in it:
            if subdirfilter == "*" and os.path.isdir(entry):
                l.append(entry)
            else:
                if entry.name.find(subdirfilter) >= 0 and os.path.isdir(entry):
                    l.append(entry)

    for subdir in l:
        with os.scandir(subdir) as it:
            for entry in it:
                if entry.name.find(filefilter) >= 0 and os.path.isfile(entry):
                    if copy:
                        copyfile(
                            os.path.join(workdir, subdir.name, entry.name),
                            os.path.join(workdir, entry.name),
                        )
                        print("FILE_COPIED: " + entry.name)
                    else:
                        os.rename(
                            os.path.join(workdir, subdir.name, entry.name),
                            os.path.join(workdir, entry.name),
                        )
                        print("FILE_MOVED: " + entry.name)
        if remove:
            os.removedirs(subdir)
            print("DIR_REMOVED: " + subdir.name)


def selectsubprogram():
    while True:
        choice = input(
            "(M)erge mp3 files, (P)ack subfolders, (U)npack subfolders or (A)bort?"
        )
        if choice == "M" or choice == "m":
            run_command(build_parser().parse_args(["merge-mp3"]))
            return
        if choice == "P" or choice == "p":
            run_command(build_parser().parse_args(["pack-subdirs"]))
            return
        if choice == "U" or choice == "u":
            run_command(build_parser().parse_args(["unpack-subdirs"]))
            return
        if choice == "A" or choice == "a":
            sys.exit(0)


def parse_boolean(value):
    normalized = value.lower()
    if normalized in ("true", "yes", "y", "ja", "j", "1", "on"):
        return True
    if normalized in ("false", "no", "n", "nein", "0", "off", "move"):
        return False
    raise argparse.ArgumentTypeError(
        "expected true/false, yes/no, y/n, ja/nein, 1/0, on/off, or move"
    )


def positive_integer(value):
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer")
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mp3tools",
        description=(
            "Merge MP3 files and organize files into subdirectories.\n"
            "Run without a command to start the interactive wizard."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "For argument details and examples, run one of:\n"
            "  mp3tools merge-mp3 --help\n"
            "  mp3tools pack-subdirs --help\n"
            "  mp3tools unpack-subdirs --help\n"
            "  mp3tools wait --help\n"
            "\n"
            "The executable path options may be used before or after a command.\n"
            "Run without a command to use the interactive wizard."
            "\n"
            "Merging and fixing MP3 metadata requires foobar2000 on Windows."
        ),
    )
    parser.add_argument(
        "-V", "--version", action="version", version=VERSIONSTR
    )
    add_executable_arguments(parser)
    commands = parser.add_subparsers(dest="command")

    merge = commands.add_parser("merge-mp3", help="merge MP3 files")
    add_executable_arguments(merge, suppress_defaults=True)
    merge.add_argument(
        "dir",
        nargs="?",
        metavar="DIR",
        help="directory containing MP3s (default: current directory; '.' also selects it)",
    )
    merge.add_argument(
        "subdir_mode",
        nargs="?",
        metavar="SUBDIR-MODE",
        type=parse_boolean,
        help=(
            "merge each subdirectory into a separate MP3; accepts "
            "true/false, yes/no, y/n, ja/nein, 1/0, on/off (omitted: ask)"
        ),
    )
    merge.add_argument(
        "legacy_foobar_path",
        nargs="?",
        metavar="FOOBAR-PATH",
        help="legacy positional foobar2000 executable path; prefer --foobar-path",
    )
    merge.add_argument(
        "autowaittime",
        nargs="?",
        metavar="SECONDS",
        type=int,
        help="seconds before auto-closing foobar2000; use -1 to disable (default: 5)",
    )

    pack = commands.add_parser(
        "pack-subdirs", help="group files into subdirectories"
    )
    add_executable_arguments(pack, suppress_defaults=True)
    pack.add_argument(
        "group_size",
        nargs="?",
        metavar="GROUP-SIZE",
        type=positive_integer,
        help="maximum files per subdirectory (default: 15; must be greater than 0)",
    )
    pack.add_argument(
        "dir",
        nargs="?",
        metavar="DIR",
        help="directory containing files (default: current directory; '.' also selects it)",
    )
    pack.add_argument(
        "file_filter",
        nargs="?",
        metavar="FILE-FILTER",
        help="case-sensitive substring selecting files (default: '.mp3')",
    )
    pack.add_argument(
        "copy_mode",
        nargs="?",
        metavar="COPY-MODE",
        type=parse_boolean,
        help=(
            "copy instead of move; accepts true/false, yes/no, y/n, "
            "ja/nein, 1/0, on/off, or 'move' for false "
            "(default: false, move files)"
        ),
    )

    unpack = commands.add_parser(
        "unpack-subdirs", help="move files out of subdirectories"
    )
    add_executable_arguments(unpack, suppress_defaults=True)
    unpack.add_argument(
        "dir",
        nargs="?",
        metavar="DIR",
        help="directory containing subdirectories (default: current directory; '.' also selects it)",
    )
    unpack.add_argument(
        "subdir_filter",
        nargs="?",
        metavar="SUBDIR-FILTER",
        help="case-sensitive substring selecting subdirectories; '*' selects all (default: 'subdir-')",
    )
    unpack.add_argument(
        "file_filter",
        nargs="?",
        metavar="FILE-FILTER",
        help="case-sensitive substring selecting files (default: '.mp3')",
    )
    unpack.add_argument(
        "copy_mode",
        nargs="?",
        metavar="COPY-MODE",
        type=parse_boolean,
        help=(
            "copy instead of move; accepts true/false, yes/no, y/n, "
            "ja/nein, 1/0, on/off, or 'move' for false "
            "(default: false, move files)"
        ),
    )
    unpack.add_argument(
        "remove_subdirs",
        nargs="?",
        metavar="REMOVE-SUBDIRS",
        type=parse_boolean,
        help=(
            "remove emptied subdirectories; accepts true/false, yes/no, "
            "y/n, ja/nein, 1/0, on/off "
            "(default: true; ignored if files remain)"
        ),
    )

    wait = commands.add_parser(
        "wait", help="set the foobar2000 wait time, then choose a tool"
    )
    add_executable_arguments(wait, suppress_defaults=True)
    wait.add_argument(
        "seconds",
        nargs="?",
        metavar="SECONDS",
        type=int,
        help="seconds before auto-closing foobar2000; use -1 to disable (default: 5)",
    )
    return parser


def add_executable_arguments(parser, suppress_defaults=False):
    default = argparse.SUPPRESS if suppress_defaults else foobarpath
    parser.add_argument(
        "--foobar-path",
        metavar="PATH",
        default=default,
        help="path to the foobar2000 executable (default: configured path)",
    )
    default = argparse.SUPPRESS if suppress_defaults else mp3tagpath
    parser.add_argument(
        "--mp3tag-path",
        metavar="PATH",
        default=default,
        help="path to the Mp3tag executable (default: configured path)",
    )


def confirm(message):
    print(message)
    return input().lower() in yes


def run_command(args):
    global autowaittime
    global foobarpath
    global mp3tagpath

    foobarpath = args.foobar_path
    mp3tagpath = args.mp3tag_path
    if args.command == "merge-mp3":
        directory = workingdir if args.dir in (None, ".") else args.dir
        if directory != workingdir and not os.path.isdir(directory):
            choice = input(
                "Specified directory not found: {0} ... will use current "
                "directory instead: {1}...OK? (Y)es or (N)o?".format(
                    directory, workingdir
                )
            )
            if choice.lower() in ("n", "no", "nein"):
                return
            directory = workingdir
        mode = args.subdir_mode
        if mode is None:
            while True:
                choice = input(
                    " > Merge (S)ubfolders or this (D)irectory or (A)bort?"
                ).lower()
                if choice in ("s", "d"):
                    mode = choice == "s"
                    break
                if choice == "a":
                    return
        path = args.legacy_foobar_path
        if path is None or path == ".":
            path = foobarpath
        wait_time = (
            args.autowaittime
            if args.autowaittime is not None
            else autowaittime
        )
        print("mp3-tools merge-mp3 {0}".format(VERSIONSTR))
        mergemp3(directory, mode, path, wait_time)
    elif args.command == "pack-subdirs":
        group_size = (
            args.group_size if args.group_size is not None else groupsize
        )
        directory = workingdir if args.dir in (None, ".") else args.dir
        filter_value = (
            args.file_filter if args.file_filter is not None else filefilter
        )
        copy = args.copy_mode if args.copy_mode is not None else copymode
        print("pack-subdirs {0}".format(VERSIONSTR))
        print(
            "calling pack-subdirs: [group-size={0}] [dir={1}] "
            "[filter={2}] [copy-mode={3}]".format(
                group_size, directory, filter_value, copy
            )
        )
        if args.group_size is None and not confirm(
            "Pack files according to above settings into subdirectories [y/n]?"
        ):
            return
        packsubdirs(group_size, directory, filter_value, copy)
    elif args.command == "unpack-subdirs":
        directory = workingdir if args.dir in (None, ".") else args.dir
        subdirs = (
            args.subdir_filter
            if args.subdir_filter is not None
            else subdirfilter
        )
        filter_value = (
            args.file_filter if args.file_filter is not None else filefilter
        )
        copy = args.copy_mode if args.copy_mode is not None else copymode
        remove = (
            args.remove_subdirs
            if args.remove_subdirs is not None
            else removesubdirmode
        )
        print("unpack-subdirs {0}".format(VERSIONSTR))
        print(
            "calling unpack-subdirs [dir={0}] [subdir-filter={1}] "
            "[file-filter={2}] [copy-mode={3}] [removesubdir-mode={4}]".format(
                directory, subdirs, filter_value, copy, remove
            )
        )
        if args.dir is None and not confirm(
            "Unpack files according to above settings into subdirectories [y/n]?"
        ):
            return
        unpackdirs(directory, subdirs, filter_value, copy, remove)
    elif args.command == "wait":
        if args.seconds is not None:
            autowaittime = args.seconds
        selectsubprogram()


def main(argv=None):
    """
    The main function executes on commands:
    `python -m mp3tools` and `$ mp3tools `.

    This is your program's entry point.
    """
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        selectsubprogram()
        return

    if len(argv) == 1 and argv[0].startswith("wait="):
        argv = ["wait", argv[0][5:]]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
    else:
        run_command(args)


if __name__ == "__main__":
    main()
