from __future__ import annotations
from sctokenizer import Token as ScToken
from sctokenizer import Source
from sctokenizer.token import TokenType
import re

re_lineBreak = re.compile('\n')
re_space = re.compile(r'(\s+)')

class Token:
    """One token in a source code."""
    def __init__(self, token:Token | ScToken | str):
        # note, line and column are 1-indexed
        if type(token) is str:
            self._value  = token
            self._type   = TokenType.OTHER
            self._line   = 0
            self._column = 0
        elif type(token) is ScToken:
            self._value  = token.token_value
            self._type   = token.token_type
            self._line   = token.line
            self._column = token.column
        else:
            self._value = token.value
            self._type = token.type
            self._line = token.line
            self._column = token.column
            self._endLine = token.endLine
            self._endColumn = token.endColumn
            self._trailingWhitespace = token.trailingWhitespace
            return
        # most tokens only span one line.
        # we'll handle the others in parsing.
        self._endLine   = self.line
        self._endColumn = self.column + len(self.value)
        self._trailingWhitespace = ''

    # tokens are immutable because otherwise we can
    # easily accidentally make a change to one
    # member that affects all members.

    @property
    def value(self) -> str:
        return self._value

    @property
    def type(self) -> TokenType:
        return self._type

    @property
    def line(self) -> int:
        return self._line

    @property
    def column(self) -> int:
        return self._column

    @property
    def endLine(self) -> int:
        return self._endLine

    @property
    def endColumn(self) -> int:
        return self._endColumn

    @property
    def trailingWhitespace(self) -> str:
        return self._trailingWhitespace

    def __str__(self) -> str:
        return self.value + self.trailingWhitespace

    def clone(self) -> Token:
        return Token(self)

    def isComment(self) -> bool:
        return self.type == TokenType.COMMENT_SYMBOL

    def isLineComment(self) -> bool:
        return self.isComment() and self.value == '//'

    def isBlockCommentStart(self) -> bool:
        return self.isComment() and self.value == '/*'

    def isBlockCommentEnd(self) -> bool:
        return self.isComment() and self.value == '*/'

class Parser:
    """Parses C source into a list of tokens."""

    colors = {
        TokenType.KEYWORD: -5, # gold (hack)
        TokenType.IDENTIFIER: 1, # red
        TokenType.CONSTANT: 2, # numbers and characters - green
        TokenType.STRING: 3, # yellow
        TokenType.SPECIAL_SYMBOL: 4, # blue
        TokenType.OPERATOR: 5, # pink
        TokenType.COMMENT_SYMBOL: 6, # cyan
        TokenType.OTHER: 7, # white
    }
    """Colors used by dump()."""

    def parse(self, code:str) -> list[Token]:
        """Parse the given code."""
        self._findLineStarts(code)
        src: str = Source.from_str(code, lang='c')
        tokens: list[Token] = [Token(t) for t in src.tokenize()]
        result: list[Token] = []
        i: int = 0
        while i < len(tokens):
            token = tokens[i]
            i += 1
            if token.isBlockCommentStart():
                # The next token should be the end.
                # Fill in the comment body.
                tkEnd = tokens[i]
                i += 1
                startOffs = self._getTokenStartIdx(token)
                endOffs   = self._getTokenStartIdx(tkEnd)+2 # +2 for the '*/'
                token._value = code[startOffs:endOffs]
                token._endLine = tkEnd.line
                token._endColumn = tkEnd.column+2

            elif token.isLineComment():
                # Add the body (comment to end of line)
                startOffs = self._getTokenStartIdx(token)
                # line is 1-indexed so this gives the next line
                endOffs   = self._lineStarts[token.line]
                token._value = code[startOffs:endOffs]
                token._endColumn = token.column + len(token.value)

            # extract the whitespace following the token
            offs = self._getTokenStartIdx(token)+len(token.value)
            space = re_space.match(code[offs:])
            token._trailingWhitespace = space.group(1) if space else ''
            result.append(token)
        return result

    def toString(self, tokens:list[Token]) -> str:
        """Convert the list of tokens back to a string."""
        result = []
        for token in tokens:
            result.append(token.value)
            result.append(token.trailingWhitespace)
        return ''.join(result)

    def dump(self, tokens:list[Token]) -> str:
        """Dump the tokens as a string with ANSI color codes
        for debugging."""
        result = []
        for k, v in self.colors.items():
            result.append("\x1B[38;5;%dm%s\x1B[0m\n" % (v+8, k))

        for tk in tokens:
            #result.append('[%d:%d]' % (tk.line, tk.column))
            result.append('\x1B[0;38;5;'+str(self.colors[tk.type]+8)+'m')
            result.append(self._resetColorsForLineEnd(tk.value))
            result.append('\x1B[48;5;8m') # gray background
            result.append(self._resetColorsForLineEnd(tk.trailingWhitespace))
        result.append('\x1B[0m')
        return ''.join(result)

    def _resetColorsForLineEnd(self, text):
        """Do some replacements to prevent the colors from extending
        past the end of the line, and to make whitespace visible."""
        # BUG: this will color multi-line comments as whitespace.
        return (text.replace('\n', '↩\x1B[0m\n\x1B[48;5;8m')
            .replace('\t', '↦')
            .replace(' ', '·'))

    def _findLineStarts(self, code:str) -> None:
        """Find the index at which each line begins in the code.

        Note the first line is numbered 0.
        """
        self._lineStarts = [0] + [m.start()+1 for m in re_lineBreak.finditer(code)]
        self._lineStarts.append(len(code))

    def _getTokenStartIdx(self, token:Token) -> int:
        """Convert the token's line number and column number
        to an offset into the code."""
        # line and column are 1-based so subtract 1
        offs = self._lineStarts[token.line - 1]
        return offs + token.column - 1
