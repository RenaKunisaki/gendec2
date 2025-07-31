import random
import copy
from parser import Token, TokenType
from mutator.AddCast            import AddCast
from mutator.AddKeyword         import AddKeyword
from mutator.AddString          import AddString
from mutator.ChangeIdentifier   import ChangeIdentifier
from mutator.ChangeKeyword      import ChangeKeyword
from mutator.ChangeNumberFormat import ChangeNumberFormat
from mutator.ChangeOperator     import ChangeOperator
from mutator.ChangeWhitespace   import ChangeWhitespace
from mutator.DeleteToken        import DeleteToken
from mutator.SwapLines          import SwapLines
from mutator.SwapTokens         import SwapTokens

# what others should we have?
# - remove cast
# - change type (technically covered by ChangeIdentifier)
# - add temporary var
# - swap for/while/do/goto
# - swap conditions: if(x) -> if(!x)
# - reorder conditions: if(x) a; else b; -> if(!x) b; else a;
# - add/remove dummy var
# - move some lines to inline
# - add/remove STUBBED_OP
# - change pointer deref (*foo vs foo[0] vs foo->field0 vs (*foo).field0)
# - change operators: x = x + 1 vs x += 1 vs x++ vs ++x
# - if(a) x=1; else x=2; vs x = a ? 1 : 2;
# - x - 1 vs x + -1

# not all of these are actually keywords but they're words we're
# interested in. this also doesn't include every keyword.
keywords = (
    'break',
    'case',
    'char',
    'const',
    'default',
    'do',
    'double',
    'else',
    'enum',
    'extern',
    'false',
    'float',
    'goto',
    'if',
    'inline',
    'int',
    'long',
    'register',
    'return',
    'short',
    'signed',
    'static',
    'struct',
    'switch',
    'true',
    'union',
    'unsigned',
    'void',
    'volatile',
    'while',
)

class MutatorCollection:
    """Makes random changes to C code by picking random
    Mutators and applying them to the token list.
    """

    _keywords = keywords

    _identifiers: list[str] = None
    """The identifiers present in the code being mutated."""

    def __init__(self):
        self._mutators = tuple(map(lambda c: c(self), (
            AddCast,
            AddKeyword,
            AddString,
            ChangeIdentifier,
            ChangeKeyword,
            ChangeNumberFormat,
            ChangeOperator,
            #ChangeWhitespace, # makes debugging difficult
            DeleteToken,
            SwapLines,
            SwapTokens,
        )))
        self._identifiers = []

    def mutate(self, code:list[Token], count:int=1) -> list[Token]:
        """Applies specified number of random mutations."""
        self._findIdentifiers(code) # do this once at start
        for _ in range(count):
            code = self._mutateOnce(code)
        return code

    def _mutateOnce(self, code:list[Token]) -> list[Token]:
        """Applies one random mutation."""
        limit = 100
        while limit > 0:
            limit -= 1
            oldCode = copy.copy(code)
            mutator = random.choice(self._mutators)
            code = mutator.mutate(code)
            # do not delete everything. leave at least
            # 2 tokens so that randint(0, len(code)-1)
            # is not an empty range.
            if len(code) < 2: code = oldCode
            if code != oldCode: break
        return code

    def _findIdentifiers(self, code:list[Token]) -> None:
        """Populate self._identifiers."""
        # convert to set and back to list to remove duplicates
        self._identifiers = list(
            set(map(lambda t: t.value,
                filter(lambda t: t.type == TokenType.IDENTIFIER,
                code))))

    def getIdentifers(self) -> list[str]:
        """Get the identifiers found in the current code."""
        return self._identifiers

    def getRandomIdentifier(self, exclude:str=None) -> str:
        """Return one random identifier name."""
        idents = self._identifiers
        if len(idents) < 1:
            raise RuntimeError("No identifiers found")
        for limit in range(1000):
            val = random.choice(idents)
            if val != exclude: return val
        raise RuntimeError("No identifiers found")

    def randomToken(self, tokens:list[Token], filt:callable) -> Token:
        """Return one random token from the given list.

        :param tokens: The token list to choose from.
        :param filt: Function to select eligible tokens.
        """
        tokens = list(filter(filt, tokens))
        if len(tokens) == 0: return None
        return random.choice(tokens)

    def cloneToken(self, code:list[Token], token:Token) -> Token:
        """Create a duplicate of the given token.

        :param code: The list of tokens being processed.
        :param token: The token to clone.
        :returns: A clone of the token.

        This is used when we want to change the properties of
        a token, because tokens are immutable.
        """
        idx = code.index(token)
        token = token.clone()
        code[idx] = token # replace with the clone
        return token

    def getTokensForLineRange(self, code:list[Token],
    lines:tuple[int]) -> (list[Token], int, int):
        """Get the tokens that occupy the given line range.

        :param code: Token list to read.
        :param lines: First and last line number.
        :returns: The tokens, and the indices of the first
            and last token in the code.
        """
        iFirst, iLast = 0, 0
        lStart, lEnd = lines
        for i, token in enumerate(code):
            if token.line < lStart:
                iFirst = i
            elif token.line <= lEnd:
                iLast = i + 1  # range is exclusive
            else:
                break
        if iLast <= iFirst: return [], 0, 0
        return code[iFirst:iLast], iFirst, iLast
