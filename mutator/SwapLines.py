from .Mutator import Mutator
from parser import Token
import random

class SwapLines(Mutator):
    """Swap two random adjacent lines."""

    def mutate(self, code:list[Token]) -> list[Token]:
        if len(code) > 2:
            pos = random.randint(0, len(code)-2)
            line = code[pos].line

            # find first and last tokens of this range
            tokens, iFirst, iLast = self.collection.getTokensForLineRange(
                code, (line, line+1))
            if tokens:
                # there's probably a better way to do this
                line1, line2 = [], []
                for token in tokens:
                    if token.line == line: line1.append(token)
                    else: line2.append(token)

                code = code[:iFirst] + line2 + line1 + code[iLast:]
        return code
