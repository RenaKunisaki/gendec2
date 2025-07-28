from .Mutator import Mutator
from parser import Token
import random

class AddCast(Mutator):
    """Insert a cast somewhere."""

    # this could be much smarter if it knew which identifiers
    # are types and where to actually insert casts

    def mutate(self, code:list[Token]) -> list[Token]:
        pos = random.randint(0, len(code)-1)
        code.insert(pos, Token(')'))
        code.insert(pos,
            Token(self.collection.getRandomIdentifier()))
        code.insert(pos, Token('('))
        return code
