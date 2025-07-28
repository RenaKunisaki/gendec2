from .Mutator import Mutator
from parser import Token
import random

class AddString(Mutator):
    """Add a string."""

    def mutate(self, code:list[Token]) -> list[Token]:
        pos = random.randint(0, len(code)-1)
        code.insert(pos,
            Token(f'\n"Dummy string {random.randint(0,999999999)}";'))
        return code
