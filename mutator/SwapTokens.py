from .Mutator import Mutator
from parser import Token
import random

class SwapTokens(Mutator):
    """Swap two random adjacent tokens."""

    def mutate(self, code:list[Token]) -> list[Token]:
        if len(code) > 2:
            pos = random.randint(0, len(code)-2)
            code[pos], code[pos+1] = code[pos+1], code[pos]
        return code
