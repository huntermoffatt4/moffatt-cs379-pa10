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


def tokenize(source: str) -> List[Token]:
    """
    Convert `source` into a list of Token objects, ending in an EOF
    token with an empty lexeme. Recognize NUMBER, IDENT, LET, PLUS,
    MINUS, STAR, SLASH, LPAREN, RPAREN, ASSIGN, SEMI. Discard
    whitespace and '#'-prefixed comments without emitting tokens for
    them. Track 1-indexed line numbers. Raise LexError (with the
    offending character and line) on unrecognized input.
    """
    # TODO
    raise NotImplementedError
