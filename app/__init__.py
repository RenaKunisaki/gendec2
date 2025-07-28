from os import PathLike
from pathlib import Path
import math
import random
import shutil
import tempfile
import subprocess
from parser import Parser, Token, TokenType
from MutatorCollection import MutatorCollection
from config import cflags

Infinity = float("inf")

class App:
    """The application as a whole."""

    sourceFilePath: Path = None
    """The path of the file we're working on."""

    origSourcePath: Path = None
    """The path that the original file was copied to."""

    targetObjPath: Path = None
    """The object file path to compare to."""

    cflags: list[str] = None
    """The compiler flags."""

    parser: Parser = None
    """The C parser."""

    mutator: MutatorCollection = None
    """The mutator."""

    permuteLineRange: tuple[int,int] = (1, 1000000)
    """The first and last line to change."""

    populationSize: int = 100
    """Size of one generation."""

    mutationRate: int = 5
    """How much to change each member."""

    originalSource: str = ""
    """The original source code."""

    bestSource: str = ""
    """The best-scoring code found so far."""

    initialScore = Infinity
    """The score of the original code."""

    def __init__(self):
        self.cflags = cflags
        self.parser = Parser()
        self.mutator = MutatorCollection()

    def run(self, sourceFilePath:PathLike,
    targetObjPath:PathLike) -> None:
        """Run the app."""
        self.sourceFilePath = Path(sourceFilePath)
        self.targetObjPath = Path(targetObjPath)
        try:
            self.begin()
            self._mainLoop()
        finally:
            self.finish()

    def _mainLoop(self):
        """Main genetic algorithm loop."""
        population = self.generateInitialPopulation()
        self.bestSolution = None
        generation = 0
        bestScore = Infinity
        gBestSource = gOriginalSource

        while True:
            generation += 1

            # calculate fitness for each member
            print(f"Gen {generation:5d} ", end="")
            selected, scores = self.select(population)

            # show the result
            score = scores[id(selected[0])]
            if score < bestScore:
                bestScore = score
                gBestSource = selected[0]
                with open("best.c", "wt") as file:
                    file.write(self.parser.toString(selected[0]))
            print(
                f"score {score:7d} ({score-initialScore:5d}) "
                f"best {bestScore:7d} "
                f"({bestScore-initialScore:5d})"
            )

            # create next generation by combining best performers
            population = []
            population.append(gOriginalSource)  # prevent getting worse
            population.append(gBestSource)
            limit = len(selected) * 20
            i     = 0
            while (limit > 0 and i+1 < len(selected)
            and len(population) < self.populationSize * 0.8):
                parent1 = selected[i % len(selected)]
                parent2 = selected[(i + 1) % len(selected)]
                population.append(parent1)
                population.append(parent2)
                child = self.crossover(parent1, parent2)
                if len(child) > 1:
                    child = self.mutate(child)
                    if child:
                        population.append(child)
                        i += 2
                limit -= 1

            # add additional new members
            while len(population) < self.populationSize:
                child = self.mutate(gOriginalSource)
                if child: population.append(child)

    def begin(self) -> None:
        """Prepare source files."""
        self.origSourcePath = Path(str(self.sourceFilePath) + ".gendec-orig.c")
        shutil.move(self.sourceFilePath, self.origSourcePath)

    def finish(self) -> None:
        """Restore source files to original state."""
        try:
            #os.unlink(sourceFilePath)
            # debug
            shutil.move(self.sourceFilePath, "last.c")
        except FileNotFoundError:
            pass
        shutil.move(self.origSourcePath, self.sourceFilePath)

    # not used...
    def preprocess(self, srcPath: PathLike) -> str:
        """Preprocess the given source file.

        Returns preprocessed source.
        """
        tmp = tempfile.NamedTemporaryFile()
        cmd = [
            "./build/tools/wibo",
            "build/compilers/GC/1.0/mwcceppc.exe",
            *self.cflags,
            "-EP",  # preprocess and strip out #line directives
            "-o",
            tmp.name,
            srcPath,
        ]
        # print(' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True)
        # print(result.stdout.decode('utf-8'))
        # print(result.stderr.decode('utf-8'))
        return tmp.read()

    def compileObj(self, src: str | list[Token]) -> \
    tempfile.NamedTemporaryFile:
        """Compile the given source code.

        On success, returns an object file, the compiler stdout,
        and the compiler stderr.
        On failure, returns None, the compiler stdout,
        and the compiler stderr.
        """
        if type(src) is list: src = self.parser.toString(src)
        #print(src)
        tmpIn = tempfile.NamedTemporaryFile(suffix=".c")
        tmpIn.write(bytes(src, "utf-8"))

        tmpOut = tempfile.NamedTemporaryFile(suffix=".o")
        cmd = [
            "./build/tools/wibo",
            "build/compilers/GC/1.0/mwcceppc.exe",
            *self.cflags,
            "-c",  # compile only, do not link
            "-o",
            tmpOut.name,
            tmpIn.name,
        ]
        # print(' '.join(cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, check=False)
        except subprocess.CalledProcessError:
            return None, None, None
        if result.returncode != 0:
            tmpOut = None
        return tmpOut, result.stdout.decode('utf-8'), \
            result.stderr.decode('utf-8')

    def fitness(self, code: list[Token]) -> int:
        """Determine how closely this code matches the desired binary.

        Returns an arbitrary number where lower means more closely
        matching, with 0 meaning a perfect match, and Infinity
        meaning the compile failed.
        """
        code = self.parser.toString(code)
        # Write the source code to a file
        with open(self.sourceFilePath, "w") as f:
            f.write(code)

        #print('\x1B[2J', end='') # clear screen
        #subprocess.call(['diff', '-y', '--suppress-common-lines',
        #    origSourcePath, sourceFilePath])

        # Compile the source code to a binary
        objFile, _, __ = self.compileObj(code)
        if objFile is None:
            return Infinity  # compile failed

        # Compare the generated binary with the target binary
        cmd = [
            "../objdiff/target/release/objdiff-cli",
            "diff",
            "-1", self.targetObjPath,
            "-2", objFile.name,
            "-o", "-",
        ]
        #print(' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError("Scoring failed: " +
                result.stdout.decode('utf-8') + '\n' +
                result.stderr.decode('utf-8'))
        return len(result.stdout)

    def select(self, population):
        """Choose the best-performing individuals based on the
        fitness function."""
        scores = {}
        for member in population:
            mid = id(member)
            if mid not in scores:  # don't re-score duplicate members
                scores[mid] = self.fitness(member)
                print("#" if math.isfinite(scores[mid]) else '*',
                    end="", flush=True)
            else: print('.', end="", flush=True)
        print(" ", end="", flush=True)

        k = lambda code: scores[id(code)]
        population = sorted(population, key=k)[: len(population) // 3]
        return population, scores

    def crossover(self, parent1, parent2):
        """Combine parts of two or more source code snippets to
        create new individuals."""
        splitPos = random.randint(1, len(parent1))
        result = parent1[0:splitPos] + parent2[splitPos:]
        return result

    def tokenize(self, code):
        tokens = self.parser.parse(code)
        return tokens

    def mutate(self, tokens):
        lStart, lEnd = self.permuteLineRange

        # find which tokens belong to this line range
        iFirst, iLast = 0, 0
        for i, token in enumerate(tokens):
            if token.line < lStart:
                iFirst = i
            elif token.line <= lEnd:
                iLast = i + 1  # range is exclusive
            else:
                break
        if iLast <= iFirst: return None

        change = tokens[iFirst:iLast]
        assert len(change) > 1
        nMutations = random.randint(1, self.mutationRate)
        try:
            mutated = self.mutator.mutate(change, nMutations)
        except Exception as ex:
            print("Error during mutation", ex)
            return None
        return tokens[:iFirst] + mutated + tokens[iLast:]

    def generateInitialPopulation(self):
        """Generate initial population."""
        global gOriginalSource

        population = []
        gOriginalSource = None
        code = ''
        with open(self.origSourcePath, "r") as file:
            code = file.read()
            gOriginalSource = self.tokenize(code)
            assert len(gOriginalSource) > 1
            # keep the original code as one member
            population.append(gOriginalSource)

        # sanity check
        #if parser.toString(gOriginalSource) != code:
        #    with open('fail.c', 'w') as file:
        #        file.write(parser.toString(gOriginalSource))
        #    raise RuntimeError("Parser bug")

        assert len(gOriginalSource) > 1
        objFile, stdout, stderr = self.compileObj(gOriginalSource)
        if objFile is None:
            print("Initial compile failed")
            print(stdout)
            print(stderr)
            raise RuntimeError("Initial compile failed")

        assert len(gOriginalSource) > 1
        global initialScore

        initialScore = self.fitness(gOriginalSource)
        assert len(gOriginalSource) > 1
        if math.isinf(initialScore):
            raise RuntimeError("Initial score failed")
        print("Original score:", initialScore)

        for i in range(self.populationSize - 1):
            assert len(gOriginalSource) > 1
            code = self.mutate(gOriginalSource)
            assert len(code) > 1
            population.append(code)
            print("Generating %d/%d   " % (i + 1,
                self.populationSize), end="\r")
        print("")
        return population
