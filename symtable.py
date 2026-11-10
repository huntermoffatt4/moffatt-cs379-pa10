"""
PA 5 dependency: paste in YOUR OWN completed PA 4 symtable.py here.

Complete Environment and check_program below. See
PA_04_The_USILang_Symbol_Table.md, Part B, for the full requirements.
"""

from typing import Optional

from gc_heap import HeapHandle

from parser import Assignment, BinOp, Declaration, Number, Program, Variable


class SemanticError(Exception):
    pass


class Environment:
    def __init__(self, parent: Optional["Environment"] = None, heap=None) -> None:
        self.parent = parent
        self.heap = heap if heap is not None else (parent.heap if parent else None)
        self._names: dict = {}  # name -> declaration line, THIS scope only

    # *Updated for PA07*
    def define(self, name: str, line: object) -> None:
        """
        Store name -> line in THIS scope. Raise SemanticError if `name`
        is already defined in THIS scope (not a parent scope --
        shadowing a parent name is allowed).
        """
        # Checking only the current scope
        if name in self._names:
            # Storing where the declaration occured
            original_line = self._names[name]
            raise SemanticError(
                f"Duplicate declaration of '{name}' (line {line}; originally declared line {original_line})."
            )
        self._names[name] = line
        if self.heap is not None and isinstance(line, HeapHandle):
            self.heap.incref(line)

    # *Updated for PA07*
    def resolve(self, name: str) -> object:
        """
        Look up `name` in this scope, then climb `parent` links.
        Return the declaration line, or raise SemanticError if not
        found anywhere in the chain.
        """
        # Current scope
        if name in self._names:
            return self._names[name]

        # Checking if an enclosing scope exists
        elif self.parent is not None:
            # Parent environment lookup
            return self.parent.resolve(name)

        # Name doesn't exist
        raise SemanticError(f"Use of undeclared variable '{name}'.")

    def assign(self, name: str, value) -> None:
        # Assign a direct handle or update an existing parameter cell
        if name not in self._names:
            if self.parent is not None:
                self.parent.assign(name, value)
                return
            raise SemanticError(f"Use of undeclared variable '{name}'.")

        old = self._names[name]
        from parameters import Cell, replace_cell_value
        if isinstance(old, Cell):
            replace_cell_value(old, value, self.heap)
            return
        if self.heap is not None:
            if isinstance(value, HeapHandle):
                self.heap.incref(value)
            if isinstance(old, HeapHandle):
                self.heap.decref(old)
        self._names[name] = value

    def release(self, borrowed_cells=()) -> None:
        # Release owned references; borrowed cells belong to the caller
        from parameters import Cell
        borrowed = set(borrowed_cells)
        seen = set()
        for value in self._names.values():
            if isinstance(value, Cell):
                if value in borrowed or value in seen:
                    continue
                seen.add(value)
                value = value.value
            if self.heap is not None and isinstance(value, HeapHandle):
                self.heap.decref(value)
        self._names.clear()


def check_program(ast: Program) -> Environment:
    """
    Walk `ast.statements` in order, using one top-level Environment.
    For a Declaration: resolve every Variable in its expr BEFORE
    defining the new name (so `let x = x;` fails as use-before-decl).
    For an Assignment: resolve the assigned-to name, then resolve
    every Variable in its expr. Errors must surface at the first
    offending statement, not be collected and reported together.
    """
    # Global symbol table
    env = Environment(parent=None)

    # Expression
    def check_expr(expr) -> None:
        # Number; no variable name to resolve
        if isinstance(expr, Number):
            return

        # Variable; check if its already been declared
        elif isinstance(expr, Variable):
            try:
                env.resolve(expr.name)
            except SemanticError:
                raise SemanticError(
                    f"Use of undeclared variable '{expr.name}' (line {expr.line})."
                )
            return

        # BinOp; recursively checks both left and right
        elif isinstance(expr, BinOp):
            check_expr(expr.left)
            check_expr(expr.right)
            return

    # Statement
    for stmt in ast.statements:
        # Declaration Statements
        if isinstance(stmt, Declaration):
            check_expr(stmt.expr)
            env.define(stmt.name, stmt.line)

        # Assignment Statements
        elif isinstance(stmt, Assignment):
            # Assignment exists
            try:
                env.resolve(stmt.name)
            # Assignment does not exist
            except SemanticError:
                raise SemanticError(
                    f"Use of undeclared variable '{stmt.name}' (line {stmt.line})."
                )
            check_expr(stmt.expr)

    return env
