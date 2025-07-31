version = "GSAP01-DEBUG"
version_num = 0
cflags = [
    "-nodefaults",
    "-proc",
    "gekko",
    "-align",
    "powerpc",
    "-enum",
    "int",
    "-fp",
    "hardware",
    "-Cpp_exceptions",
    "off",
    # "-W all",
    # "-O4,p",
    # "-O1,p",
    "-O0",
    "-opt",
    "peephole",
    # "-opt off",
    "-g",
    # "-func_align 8",
    # "-common on",
    # "-inline auto",
    # "-inline noauto,deferred",
    "-use_lmw_stmw",
    "on",
    "-pragma",
    '"cats off"',
    "-pragma",
    '"warn_notinlined off"',
    "-maxerrors",
    "1",
    "-nosyspath",
    "-RTTI",
    "off",
    "-fp_contract",
    "on",
    "-str",
    "reuse",
    "-multibyte",  # For Wii compilers, replace with `-enc SJIS`
    "-i",
    "include",
    "-i",
    "include/libc",
    "-i",
    f"build/{version}/include",
    f"-DVERSION={version_num}",
]

# Not currently used.
def buildPreprocessCommand(cflags:list[str],
inPath:str, outPath:str):
    return [
        "./build/tools/wibo",
        "build/compilers/GC/1.0/mwcceppc.exe",
        *cflags,
        "-EP",  # preprocess and strip out #line directives
        "-o",
        outPath,
        inPath,
    ]

def buildCompileCommand(cflags:list[str],
inPath:str, outPath:str):
    return [
        "./build/tools/wibo",
        "build/compilers/GC/1.0/mwcceppc.exe",
        *cflags,
        "-c",  # compile only, do not link
        "-o",
        outPath,
        inPath,
    ]

def buildScoreCommand(origPath:str, newPath:str):
    return [
        "../objdiff/target/release/objdiff-cli",
        "diff",
        "-1", origPath,
        "-2", newPath,
        "-o", "-",
    ]
