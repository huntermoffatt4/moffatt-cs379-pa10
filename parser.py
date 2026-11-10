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
    if state.peek().type == "NUMBER":
        # Consumes/returns token and moves to next
        tok = state.advance()
        # Creates AST node
        return Number(int(tok.lexeme), tok.line)

    elif state.peek().type == "LPAREN":
        # Consumes (
        state.advance()
        node = parse_expr(state)
        # Expects )
        state.expect("RPAREN")
        return node

    elif state.peek().type == "IDENT":
        tok = state.advance()
        # Creates AST node
        return Variable(tok.lexeme, tok.line)

    else:
        tok = state.peek()
        raise ParseError(
            f"Line {tok.line}: expected NUMBER, IDENT, or LPAREN"
            f"found {tok.type} ({tok.lexeme!r})."
        )


def parse_term(state: _ParserState):
    node = parse_factor(state)
    while state.peek().type in ("STAR", "SLASH"):
        # Consumes and stores operator token
        op_tok = state.advance()
        # Parses and stores right side of operator
        right = parse_factor(state)
        # Combines everything into a binary-operation AST node
        node = BinOp(op_tok.lexeme, node, right, op_tok.line)
    return node


def parse_expr(state: _ParserState):
    node = parse_term(state)
    while state.peek().type in ("PLUS", "MINUS"):
        # Consumes and stores operator token
        op_tok = state.advance()
        # Parses and stores right side of operator
        right = parse_term(state)
        # Combines everything into a binary-operation AST node
        node = BinOp(op_tok.lexeme, node, right, op_tok.line)
    return node


def parse_declaration(state: _ParserState) -> Declaration:
    # Requires token to be LET and consumes it
    state.expect("LET")
    # Requires next token to be an identifier and stores it
    name_tok = state.expect("IDENT")
    # Requires next token to be an assignment and consumes it
    state.expect("ASSIGN")
    # Parses everything on the right side of the assignment
    expr = parse_expr(state)
    # Requires next token to be a semicolon and consumes it
    state.expect("SEMI")
    # Builds the declaration AST node
    return Declaration(name_tok.lexeme, expr, name_tok.line)


def parse_assignment(state: _ParserState) -> Assignment:
    # Requires next token to be an identifier and stores it
    name_tok = state.expect("IDENT")
    # Requires next token to be an assignment and consumes it
    state.expect("ASSIGN")
    # Parses everything on the right side of the assignment
    expr = parse_expr(state)
    # Requires next token to be a semicolon and consumes it
    state.expect("SEMI")
    # Builds the declaration AST node
    return Assignment(name_tok.lexeme, expr, name_tok.line)


def parse_statement(state: _ParserState):
    tok = state.peek()
    if tok.type == "LET":
        return parse_declaration(state)
    
    elif tok.type == "IDENT":
        return parse_assignment(state)

    else:
        raise ParseError(
            f"Line {tok.line}: expected LET or IDENT"
            f"found {tok.type} ({tok.lexeme!r})."
        )


def parse_program(state: _ParserState) -> Program:
    statements = []
    # Keeps parsing until we reach the end of file token
    while state.peek().type != "EOF":
        # Parses and stores one complete statement
        statement = parse_statement(state)
        # Adds the AST node to our statements list
        statements.append(statement)
    return Program(statements)


def parse(tokens: List[Token]) -> Program:
    # Create the parser state
    state = _ParserState(tokens)
    # Parse the whole program
    program = parse_program(state)
    # Check for the end of file token
    state.expect("EOF")
    # Return the program
    return program
