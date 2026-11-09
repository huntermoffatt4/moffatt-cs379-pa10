"""
PA 9: The Garbage Collector -- starter.

Complete GCHeap below. See the assignment, Part B,
for the full requirements.

Named gc_heap.py, not gc.py, to avoid shadowing Python's own built-in
gc module -- the assignment's Part B says "gc.py" but that name
collides with the standard library, so this starter renames it.
Submit under whichever name your instructor prefers; the test harness
just imports from gc_heap.

Design note: GCHeap.allocate(obj) takes exactly one argument per the
spec, so an allocated object that references OTHER heap handles must
expose them itself for decref's cascade to find -- via a
get_child_handles() -> list[int] method. HeapNode below is a given
example object shaped this way, used by the cyclic-structure test.
"""

from typing import Any, List


class HeapNode:
    """
    Given: a minimal heap object whose fields may hold OTHER handles
    (ints). get_child_handles() is what GCHeap.decref's cascade calls
    to find them -- it must reflect the CURRENT field values, not a
    snapshot taken at creation time.
    """

    def __init__(self, **fields: Any) -> None:
        self.fields = fields

    def get_child_handles(self) -> List[int]:
        return [v for v in self.fields.values() if isinstance(v, int)]


class GCHeap:
    def __init__(self) -> None:
        # TODO: internal storage -- e.g. {handle: (obj, refcount)} -- and a handle counter.
        raise NotImplementedError

    def allocate(self, obj: Any) -> int:
        """Store obj, return a new handle. Initial refcount is 1 (the creating reference)."""
        # TODO
        raise NotImplementedError

    def incref(self, handle: int) -> None:
        # TODO
        raise NotImplementedError

    def decref(self, handle: int) -> None:
        """
        Decrement the refcount. When it hits 0: free the object, AND
        cascade-decref every handle returned by the freed object's
        get_child_handles() (if it has that method), recursively.
        """
        # TODO
        raise NotImplementedError

    def is_alive(self, handle: int) -> bool:
        # TODO
        raise NotImplementedError

    def live_count(self) -> int:
        """Number of currently-alive (refcount > 0) handles."""
        # TODO
        raise NotImplementedError
