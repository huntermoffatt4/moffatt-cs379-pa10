"""
PA 5 dependency: paste in YOUR OWN completed PA 3 parser.py here
(needed transitively -- symtable.py imports from this file).

Complete the parsing functions below. AST node types are already
defined -- do not modify them. See the assignment,
Part B, for the full requirements.
"""

from dataclasses import dataclass, field
from typing import List

from lexer import Token, tokenize


@dataclass
class Program:
    statements: list


@dataclass
class Declaration:
    name: str
    expr: object
    line: int


@dataclass
class Assignment:
    name: str
    expr: object
    line: int


@dataclass
class BinOp:
    op: str
    left: object
    right: object
    line: int


@dataclass
class Number:
    value: int
    line: int


@dataclass
class Variable:
    name: str
    line: int


class ParseError(Exception):
    pass


class _ParserState:
    """Given: a small cursor wrapper over the token list. Not required to use, but handy."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type_: str) -> Token:
        tok = self.peek()
        if tok.type != type_:
            raise ParseError(f"Line {tok.line}: expected {type_}, found {tok.type} ({tok.lexeme!r}).")
        return self.advance()


def parse_factor(state: _ParserState):
    # TODO
    raise NotImplementedError


def parse_term(state: _ParserState):
    # TODO
    raise NotImplementedError


def parse_expr(state: _ParserState):
    # TODO
    raise NotImplementedError


def parse_declaration(state: _ParserState) -> Declaration:
    # TODO
    raise NotImplementedError


def parse_assignment(state: _ParserState) -> Assignment:
    # TODO
    raise NotImplementedError


def parse_statement(state: _ParserState):
    # TODO: peek at state.peek().type to choose declaration vs. assignment
    raise NotImplementedError


def parse_program(state: _ParserState) -> Program:
    # TODO: loop parse_statement() until EOF
    raise NotImplementedError


def parse(tokens: List[Token]) -> Program:
    state = _ParserState(tokens)
    return parse_program(state)
