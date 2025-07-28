from .Mutator import Mutator
from parser import Token, TokenType
import random

class ChangeIdentifier(Mutator):
    """Change a random identifier to another one
    found in the same code."""

    def mutate(self, code:list[Token]) -> list[Token]:
        token = self.collection.randomToken(code,
            lambda tk: tk.type == TokenType.IDENTIFIER)
        if token is None: return code
        val = self.collection.getRandomIdentifier(token.value)
        if val is not None:
            self.collection.cloneToken(code, token)._value = val
        return code
