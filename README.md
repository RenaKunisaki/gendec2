# gendec2
## Genetic Algorithm Decompile Permuter

This is a tool to help with matching decompiled source code to the original binary.

It's still very crude and awkward to use, but it works. Maybe. You'll need to edit config.py to your own project's configuration.

It should work for any C source. C++ isn't supported yet.

## How it works

You need to already have a partial decompile in progress, which builds an object file from your WIP code, as well as an "original" object file to compare to. The script attempts to modify the code to produce the same object file as the original.

Edit config.py to set up the compile flags and the commands to build and compare your program. The score command should take two object files and return some description of their differences. The script uses the output length to determine which variations are a closer match, so the actual output format isn't important.

The script will make random changes to the original code and try to compile it. Most of these will be nonsense that doesn't compile, but a few should manage to build.

For each iteration, it will run 100 attempts. The first generation will consist of the original code and 99 randomly modified versions. After each generation, it will combine the best-scoring versions. Subsequent generations consist of the original code, the best-scoring code found so far, some combinations of the best-scoring code found in the previous generation, and some randomly modified versions of all of these.

(The original code and best-scoring code are included in every generation so that, in theory, the result can't be any worse than those.)

When run for long enough, in theory, it will produce code that reproduces the original binary exactly (though might be an utter mess). In practice, since the modifications it can make are limited, it's unlikely to ever find a perfect match, but the results can give hints for what changes you need to make.

## What needs improving

- Mostly, it needs more, smarter mutators, to expand what changes it can make, and increase the chances it can find a match.
- C++ support would be great.
- The interface is command-line only and awkward because of the use of chdir.
- It prints cryptic information to the terminal which is assumed to be fairly wide.

## What to watch out for

- It runs a lot of subprocesses (compiling, linking, scoring) and writes a lot of temporary files, so it will heat up your CPU and wear out your SSD.
- It *should* always restore your original source when it exits, but always make backups.
- Since it's still early WIP, it writes some additional files for debugging.

## Why the name?

Gendec is short for genetic decompiler. This is a bit of a misnomer since it doesn't directly decompile, but assists in decompiling. "gendec1" was an earlier attempt that didn't work.
