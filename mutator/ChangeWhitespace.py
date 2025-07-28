from .Mutator import Mutator
from parser import Token
import random

class ChangeWhitespace(Mutator):
    """Change the whitespace following a random token."""

    def mutate(self, code:list[Token]) -> list[Token]:
        pos = random.randint(0, len(code)-1)
        token = code[pos]
        token.trailingWhitespace = random.choice((
            '', ' ', '\t', '\n', '\r\n'))
        return code
