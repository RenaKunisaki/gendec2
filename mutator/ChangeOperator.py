from .Mutator import Mutator
from parser import Token, TokenType
import random

operators = ('+', '-', '*', '/', '<<', '>>', '&', '|', '^',
    '%', '++', '--', '=', '==', '!=', '>', '<', '>=', '<=',
    '->', '.', ',')

class ChangeOperator(Mutator):
    """Change a random operator."""

    def mutate(self, code:list[Token]) -> list[Token]:
        token = self.collection.randomToken(code,
            lambda tk: tk.type == TokenType.OPERATOR)
        if token is None: return code
        self.collection.cloneToken(code, token)._value = \
            random.choice(operators)
        return code
