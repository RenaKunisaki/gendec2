from .Mutator import Mutator
from parser import Token, TokenType
import random

class ChangeKeyword(Mutator):
    """Change a random keyword."""

    def mutate(self, code:list[Token]) -> list[Token]:
        token = self.collection.randomToken(code,
            lambda tk: tk.type == TokenType.KEYWORD)
        if token is None: return code
        self.collection.cloneToken(code, token)._value = \
            random.choice(self.collection._keywords)
        return code
