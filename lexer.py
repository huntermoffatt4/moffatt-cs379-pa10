"""
PA 5 dependency: paste in YOUR OWN completed PA 2 lexer.py here.
(Needed transitively -- symtable.py imports from parser.py, which
imports from this file. PA 5's own new work doesn't touch lexing or
parsing directly.)

This is the same file from PA 2's repo -- copy your own working
tokenize() implementation over this stub before starting parser.py.
Every PA repo is independent (no shared filesystem across repos), so
each pipeline stage bundles its own copy of the prior stages.

Complete tokenize() below. See the assignment, Part B,
for the full requirements. Must use a single compiled master regex
with named groups -- not a hand-rolled character-by-character loop.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    type: str
    lexeme: str
    line: int


class LexError(Exception):
    pass


# TODO: build your master regex here, e.g.:
# _MASTER_RE = re.compile(r"(?P<NUMBER>\d+)|(?P<IDENT>[A-Za-z_]\w*)|...")

# List of reserved words
KEYWORDS = {"let"}

# All one line
_MASTER_RE = re.compile(
    # Number rules; no decimals
    r"(?P<NUMBER>[0-9]+)"
    # Identifier rules; must begin with a letter or _, then can contain numbers
    r"|(?P<IDENT>[a-zA-Z_][a-zA-Z0-9_]*)"
    # Four math operators
    # Addition
    r"|(?P<PLUS>\+)"
    # Subtraction
    r"|(?P<MINUS>-)"
    # Multiplication
    r"|(?P<STAR>\*)"
    # Division
    r"|(?P<SLASH>/)"
    # Parenthesis
    # Left parenthesis
    r"|(?P<LPAREN>\()"
    # Right parenthesis
    r"|(?P<RPAREN>\))"
    # Assignment
    r"|(?P<ASSIGN>=)"
    # Semicolon
    r"|(?P<SEMI>;)"
    # Comment; starts with #
    r"|(?P<COMMENT>#.*)"
    # New line
    r"|(?P<NEWLINE>\n)"
    # Catches spaces and tabs
    r"|(?P<SKIP>[ \t]+)"
    # Catches anything illegal to raise LexError
    r"|(?P<MISMATCH>.)"
)


def tokenize(source: str) -> List[Token]:
    """
    Convert `source` into a list of Token objects, ending in an EOF
    token with an empty lexeme. Recognize NUMBER, IDENT, LET, PLUS,
    MINUS, STAR, SLASH, LPAREN, RPAREN, ASSIGN, SEMI. Discard
    whitespace and '#'-prefixed comments without emitting tokens for
    them. Track 1-indexed line numbers. Raise LexError (with the
    offending character and line) on unrecognized input.
    """
    # List for tokens
    tokens = []
    # Start at line 1
    line = 1
    # Start scanning at first character
    pos = 0

    # Keeps scanning until we reach the end of the source code
    while pos < len(source):
        # Try to match at our current position
        m = _MASTER_RE.match(source, pos)
        # Tells which group matched
        kind = m.lastgroup
        # Gets matched characters
        lexeme = m.group()
        # Example: x = 12 would be kind = NUMBER, lexeme = 12

        # Creates a newline
        if kind == "NEWLINE":
            line += 1
        # Skips comments, spaces, and tabs
        elif kind in ("SKIP", "COMMENT"):
            pass
        # LexError for anything illegal
        elif kind == "MISMATCH":
            raise LexError(f"Unexpected char {lexeme!r} at line {line}.")
        # Change let into LET
        elif kind == "IDENT" and lexeme in KEYWORDS:
            tokens.append(Token("LET", lexeme, line))
        # Normal tokens
        else:
            tokens.append(Token(kind, lexeme, line))

        # Moves position where next scan should begin
        pos = m.end()

    # Marks the end of the token
    tokens.append(Token("EOF", "", line))
    return tokens
