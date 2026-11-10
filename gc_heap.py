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

class HeapHandle(int):
    # Distinguishes allocated handles from arithmetic integers
    pass


class GCHeap:
    def __init__(self) -> None:
        # Stores each object and its reference count
        self._heap = {}
        self._next_handle = 1

    def allocate(self, obj: Any) -> int:
        """Store obj, return a new handle. Initial refcount is 1 (the creating reference)."""
        # Assigns a new handle and stores a ref count of 1
        handle = HeapHandle(self._next_handle)
        self._next_handle += 1
        self._heap[handle] = [obj, 1]
        return handle

    def incref(self, handle: int) -> None:
        # Increases reference count
        self._heap[handle][1] += 1

    def decref(self, handle: int) -> None:
        """
        Decrement the refcount. When it hits 0: free the object, AND
        cascade-decref every handle returned by the freed object's
        get_child_handles() (if it has that method), recursively.
        """
        # Retrieves object and its reference count,
        obj, count = self._heap[handle]

        # If there are multiple references, decrease the count without removing the object
        if count > 1:
            self._heap[handle][1] -= 1
            return

        # Remove the object and release its child references
        del self._heap[handle]

        # If the object has child handles, refernces are released recursively
        if hasattr(obj, "get_child_handles"):
            for child in obj.get_child_handles():
                self.decref(child)

    def is_alive(self, handle: int) -> bool:
        # Checks whether the object remains allocated
        return handle in self._heap

    def live_count(self) -> int:
        """Number of currently-alive (refcount > 0) handles."""
        # Counts all allocated objects
        return len(self._heap)
