"""
PA 8: The VTable Dispatcher -- starter.

Complete VTable, build_vtable, USIObject, and dispatch below. See
PA_08_The_VTable_Dispatcher.md, Part B, for the full requirements.

Design note (simplification): the assignment says to reuse the call
mechanism from PA6/PA7, but PA1-7's expression AST only evaluates
integer arithmetic -- there's no string-literal node, and this PA's
test scenario (Animal/Dog/Puppy) needs string-returning methods. Full
string-literal support would mean extending the grammar/lexer/parser/
evaluator, which is out of scope for what Part B actually asks you to
build (VTable/dispatch mechanics). So here, a method body is a plain
Python callable `fn(self) -> value` instead of a PA3 AST node --
dispatch() still resolves through the VTable and still invokes the
resolved method with the object as receiver, which is the actual
mechanism this PA is about.
"""

from typing import Dict, Optional, Protocol


class MethodLike(Protocol):
    def call(self, args: list, caller_env) -> object:
        """PA 7 Closure-compatible call interface."""


class ClassDecl:
    """Given: a minimal class declaration -- just a name and its own (non-inherited) methods."""

    __slots__ = ("name", "methods")

    def __init__(self, name: str, methods: Dict[str, MethodLike]) -> None:
        self.name = name
        self.methods = methods  # methods declared on THIS class only


class VTable:
    def __init__(self, entries: Dict[str, MethodLike], owning_class_name: str = "?") -> None:
        """`owning_class_name` is just for error messages -- store it alongside entries."""
        # Storing methods and class name
        self.entries = entries
        self.owning_class_name = owning_class_name

    def resolve(self, method_name: str) -> MethodLike:
        """
        Return the method object bound to `method_name`. Raise a clear
        error (e.g. AttributeError) whose message names BOTH the
        owning class and the missing method if it doesn't exist.
        """
        # Finds a method and returns it, or raise an error if it doesn't exist
        if method_name in self.entries:
            return self.entries[method_name]
        raise AttributeError(f"{self.owning_class_name} has no method '{method_name}'")


def build_vtable(class_node: ClassDecl, parent_vtable: Optional[VTable] = None) -> VTable:
    """
    Start from a copy of parent_vtable's entries (inherited methods),
    then overwrite only the slots class_node itself redeclares. A
    method class_node does NOT override must resolve to the EXACT SAME
    method object the parent uses -- don't wrap or duplicate it.
    Pass class_node.name as the new VTable's owning_class_name.
    """
    # Copies the parent's methods if there are any
    if parent_vtable is None:
        entries = {}
    else:
        entries = dict(parent_vtable.entries)

    # Adds or replaces methods declared by child
    entries.update(class_node.methods)
    return VTable(entries, class_node.name)


class USIObject:
    def __init__(self, class_descriptor: VTable, fields: dict) -> None:
        # Storing the object's class info and fields
        self.class_descriptor = class_descriptor
        self.fields = fields

    def get_child_handles(self) -> list[int]:
        # Return the references held by this object
        from gc_heap import HeapHandle
        return [v for v in self.fields.values() if isinstance(v, HeapHandle)]

    def set_field(self, name: str, value, heap) -> None:
        # Keep the new reference before dropping the old one
        from gc_heap import HeapHandle
        old = self.fields.get(name)
        if isinstance(value, HeapHandle):
            heap.incref(value)
        self.fields[name] = value
        if isinstance(old, HeapHandle):
            heap.decref(old)


def dispatch(obj: USIObject, method_name: str, args: list, caller_env) -> object:
    """
    Resolve method_name through obj's OWN VTable (never a declared/
    static type), then call the resolved method via PA 7's interface:
    resolved_method.call([obj, *args], caller_env).
    """
    # Looks up the method and calls it
    method = obj.class_descriptor.resolve(method_name)
    return method.call([obj, *args], caller_env)
