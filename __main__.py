#!/usr/bin/env python
# eg: ./__main__.py --dir=../sfadebug/ --lines=1,4 src/main/objects.c build/GSAP01-DEBUG/src/main/objects.o

# BUG: extra spaces are being added to string constants
# (maybe only when they start with spaces?)
import os
import argparse
from app import App

argParser = argparse.ArgumentParser()
argParser.add_argument("srcPath")
argParser.add_argument("tgtPath")
argParser.add_argument("--dir", help="Working directory")
argParser.add_argument(
    "--lines", help="Range of lines to mutate "
    "(separated by comma eg: 1,4)"
)


def main():
    app = App()
    args = argParser.parse_args()
    if "dir" in args and args.dir is not None:
        os.chdir(args.dir)
    if "lines" in args and args.lines is not None:
        lines = args.lines.split(",", maxsplit=1)
        if len(lines) != 2:
            print("Invalid line range")
            return
        try:
            app.setPermuteLineRange(int(lines[0]), int(lines[1]))
        except ValueError:
            print("Invalid line numbers")
            return

    app.run(args.srcPath, args.tgtPath)


if __name__ == "__main__":
    main()
