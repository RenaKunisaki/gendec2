from .Mutator import Mutator
from parser import Token
import random

class DeleteToken(Mutator):
    """Delete a random token."""

    def mutate(self, code:list[Token]) -> list[Token]:
        pos = random.randint(0, len(code)-1)
        code.pop(pos)
        return code
