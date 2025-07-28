from .Mutator import Mutator
from parser import Token, TokenType
import random

intFormatters = ('%d', '%du', '0x%x',
    '(int)%d', '(uint)%d', '(short)%d', '(ushort)%d',
    '(char)%d', '(uchar)%d')
floatFormatters = ('%f', '%1.1f', '%ff', '%1.1ff',
    '(float)%f', '(double)%f')

class ChangeNumberFormat(Mutator):
    """Change how a number is written."""

    def mutate(self, code:list[Token]) -> list[Token]:
        limit = 1000
        val   = None
        while limit > 0 and val is None:
            token = self.collection.randomToken(code,
                lambda tk: tk.type == TokenType.CONSTANT)
            if token is None: return code
            try: val = int(token.value, 0)
            except ValueError:
                try: val = float(token.value)
                except ValueError: val = None
            limit -= 1
        if not val: return code

        token = self.collection.cloneToken(code, token)
        formatters = intFormatters if type(val) is int else floatFormatters
        token._value = random.choice(formatters) % val
        return code
