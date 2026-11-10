"""
PA 7: The Parameter Simulator -- starter.

Complete bind_parameters, commit_value_result, and Closure below.
Cell, evaluate(), and FunctionDecl are already provided -- do not
modify them. See the assignment, Part B, for the
full requirements.

Design note (filling a gap in the assignment spec): Requirement 1
says value-result mode must write the callee's final local value back
to the caller "only when the function returns" -- but bind_parameters
runs once, at CALL time, before the body executes. One function alone
can't do both "bind at call time" and "write back at return time," so
this starter adds a second function, commit_value_result, called
AFTER the simulated function body finishes. bind_parameters sets up
bookkeeping for value-result parameters (a list of (param_name,
caller_var_name) pairs), and commit_value_result uses it to do the
delayed write-back.

Design note 2: variables are stored as Cell objects (a mutable box),
not raw values, specifically so reference-mode parameters can share
the exact same storage as the caller's variable -- see Part A,
Questions 1-2, for why "bind directly to the caller's slot" requires
this instead of just copying a plain value.
"""

from typing import Any, List, Tuple

from parser import BinOp, Number, Variable
from symtable import Environment
from gc_heap import HeapHandle


class Cell:
    """Given: a mutable box. Two names that share the SAME Cell are aliased."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


def replace_cell_value(cell: Cell, value: Any, heap=None) -> None:
    # A Cell owns one reference; keep the new value before releasing the old
    if heap is not None:
        if isinstance(value, HeapHandle):
            heap.incref(value)
        if isinstance(cell.value, HeapHandle):
            heap.decref(cell.value)
    cell.value = value


class FunctionDecl:
    """Given: a minimal function declaration -- params and a single expr body."""

    __slots__ = ("params", "body")

    def __init__(self, params: List[str], body) -> None:
        self.params = params
        self.body = body


def evaluate(node, env: Environment):
    """Given: evaluate a PA3 expression AST node against `env` (Cells are transparently dereferenced)."""
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        val = env.resolve(node.name)
        return val.value if isinstance(val, Cell) else val
    if isinstance(node, BinOp):
        if node.op == "neg":
            return -evaluate(node.left, env)
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        return {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}[node.op](left, right)
    raise ValueError(f"cannot evaluate node: {node!r}")


def assign_through(env: Environment, name: str, value: Any) -> None:
    """Given: write `value` into whatever Cell `name` resolves to (mutates in place, does not rebind)."""
    cell = env.resolve(name)
    if not isinstance(cell, Cell):
        raise TypeError(f"'{name}' is not bound to a Cell -- did you forget to wrap it?")
    replace_cell_value(cell, value, env.heap)


def bind_parameters(param_specs: List[Tuple[str, str]], arg_nodes: list, caller_env: Environment, callee_record) -> None:
    """
    Populate callee_record.locals_env according to each parameter's
    mode ("value", "reference", or "value-result"). For value-result
    parameters, also record what commit_value_result needs to do the
    delayed write-back later -- store it whichever way you like (e.g.
    an attribute on callee_record such as callee_record.pending_writeback).
    """
    # List to store info about parameters that need to be copied back to the caller
    # Used for pass-by-value-result
    callee_record.pending_writeback = []
    callee_record.borrowed_cells = set()

    # Matches each function parameter with its argument
    for (name, mode), arg in zip(param_specs, arg_nodes):
        if mode == "reference" or mode == "value-result":
            if not isinstance(arg, Variable):
                raise TypeError("Argument must be a variable")

        # Pass-by-reference
        if mode == "reference":
            cell = caller_env.resolve(arg.name)
            callee_record.borrowed_cells.add(cell)
        # Pass-by-value and pass-by-value-result
        else:
            value = evaluate(arg, caller_env)
            cell = Cell(value)
            heap = callee_record.locals_env.heap
            if heap is not None and isinstance(value, HeapHandle):
                heap.incref(value)

        # Adds the parameter to the callee's local environment
        callee_record.locals_env.define(name, cell)

        # Checks whether the parameter needs to be copied back
        if mode == "value-result":
            callee_record.pending_writeback.append(
                (name, caller_env.resolve(arg.name))
            )


def commit_value_result(callee_record, caller_env: Environment) -> None:
    """
    For every value-result parameter bound by bind_parameters on this
    callee_record, copy its FINAL local value back into the caller's
    corresponding variable now (call this only after the callee's body
    has finished running).
    """
    # Waits until the function returns before changing the caller's variables
    for name, cell in callee_record.pending_writeback:
        value = callee_record.locals_env.resolve(name).value
        replace_cell_value(cell, value, caller_env.heap)


class Closure:
    def __init__(self, declaration: FunctionDecl, defining_env: Environment) -> None:
        # Stores function's definition
        self.declaration = declaration
        # Stores environment where function was defined
        self.defining_env = defining_env

    def call(self, args: list, caller_env: Environment):
        """
        Create the callee Environment as a child of self.defining_env
        (NOT caller_env) -- this is what makes closure capture work.
        Bind each declaration.params[i] to args[i] (already-evaluated
        values, wrapped in a Cell), then evaluate declaration.body in
        that new environment and return the result.
        """
        # Creates a new environment with static link
        env = Environment(self.defining_env)

        # Matches each function parameter with its argument
        for name, value in zip(self.declaration.params, args):
            env.define(name, Cell(value))
            if env.heap is not None and isinstance(value, HeapHandle):
                env.heap.incref(value)

        try:
            result = evaluate(self.declaration.body, env)
            if env.heap is not None and isinstance(result, HeapHandle):
                env.heap.incref(result)
            return result
        finally:
            env.release()
