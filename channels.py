"""
PA 10: Channels -- starter (final PA of the semester).

Complete Channel below, plus the producer/consumer driver at the
bottom. See the assignment, Part B, for the full requirements.
Values passed through the channel are GCHeap handles (ints) -- see
gc_heap.py.
"""

import threading
from typing import Any, Optional

from gc_heap import GCHeap

_CLOSED_SENTINEL = object()


class Channel:
    def __init__(self, capacity: int, heap: GCHeap) -> None:
        # TODO: internal buffer (a deque or list works), a threading.Condition,
        # and a "closed" flag.
        raise NotImplementedError

    def put(self, value: Any) -> None:
        """
        Block while the buffer is full. `value` is expected to be a
        GCHeap handle -- incref it (the channel now holds a reference)
        BEFORE enqueuing. Wake a waiting get() once space is available.
        """
        # TODO
        raise NotImplementedError

    def get(self):
        """
        Block while the buffer is empty (and not closed). Returns the
        next value, transferring the channel's reference to the
        caller (do NOT decref here -- the caller now owns that
        reference and is responsible for eventually releasing it).
        On an empty, closed channel, return the sentinel from
        `Channel.CLOSED` instead of blocking forever.
        """
        # TODO
        raise NotImplementedError

    def close(self) -> None:
        """Mark closed and wake every blocked thread."""
        # TODO
        raise NotImplementedError

    CLOSED = _CLOSED_SENTINEL


def producer_consumer_driver(heap: GCHeap, values: list, channel: Channel, num_consumers: int = 1):
    """
    Given: a driver you can use as-is (or adapt) for your own testing.
    One producer thread allocates + puts each value in `values` onto
    `channel`, then closes it. `num_consumers` consumer threads pull
    handles off, look up and record their value, then release their
    transferred reference, exiting cleanly on the CLOSED sentinel.
    Returns the list of delivered (handle, value) pairs.
    """
    delivered = []
    delivered_lock = threading.Lock()

    def produce():
        for v in values:
            handle = heap.allocate(v)
            try:
                channel.put(handle)
            finally:
                heap.decref(handle)  # release the creator reference
        channel.close()

    def consume():
        while True:
            handle = channel.get()
            if handle is Channel.CLOSED:
                return
            value = heap._objects[handle][0]  # PA 9 stores [object, refcount]
            with delivered_lock:
                delivered.append((handle, value))
            heap.decref(handle)  # the consumer is done with its transferred reference

    producer_thread = threading.Thread(target=produce)
    consumer_threads = [threading.Thread(target=consume) for _ in range(num_consumers)]
    for t in [producer_thread] + consumer_threads:
        t.start()
    producer_thread.join()
    for t in consumer_threads:
        t.join(timeout=10.0)

    return delivered

