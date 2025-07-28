from .Mutator import Mutator
from parser import Token
import random

class AddKeyword(Mutator):
    """Insert a keyword somewhere."""

    def mutate(self, code:list[Token]) -> list[Token]:
        pos = random.randint(0, len(code)-1)
        code.insert(pos, Token(random.choice(self.collection._keywords)))
        return code
