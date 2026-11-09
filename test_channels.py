"""
PA 10: Channels -- verification suite (final PA of the semester).

Run: python test_channels.py
Prints CHANNEL_SYNC_VERIFIED only if every check below passes.
"""

import sys
import threading
import time

from channels import Channel, producer_consumer_driver
from gc_heap import GCHeap


def check(label: str, condition: bool, failures: list) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        failures.append(label)


def bounded_trace_test(failures: list) -> None:
    """Part A, Question 1: capacity 2, P.put(1),put(2),put(3)[blocks], C.get(),get()."""
    heap = GCHeap()
    ch = Channel(capacity=2, heap=heap)

    h1, h2, h3 = heap.allocate(1), heap.allocate(2), heap.allocate(3)
    ch.put(h1)
    ch.put(h2)

    put3_done = threading.Event()

    def put_third():
        ch.put(h3)  # buffer is full (h1, h2) -- this must block
        put3_done.set()

    t = threading.Thread(target=put_third)
    t.start()
    time.sleep(0.3)
    check("put(3) blocks while the capacity-2 buffer already holds 2 items", not put3_done.is_set(), failures)

    first = ch.get()  # frees a slot -> should unblock the pending put(3)
    check("first get() returns the OLDEST item (FIFO order: h1)", first == h1, failures)

    t.join(timeout=2.0)
    check("put(3) unblocks and completes once a slot frees up", put3_done.is_set(), failures)

    second = ch.get()
    third = ch.get()
    check("remaining gets drain h2 then h3, in FIFO order", (second, third) == (h2, h3), failures)
    for handle in (h1, h2, h3):
        heap.decref(handle)  # creator reference
        heap.decref(handle)  # transferred channel reference
    check("bounded trace releases all references", heap.live_count() == 0, failures)


def close_semantics_test(failures: list) -> None:
    heap = GCHeap()
    ch = Channel(capacity=1, heap=heap)
    ch.close()
    result = ch.get()
    check("get() on an empty, closed channel returns Channel.CLOSED instead of blocking", result is Channel.CLOSED, failures)

    ch2 = Channel(capacity=1, heap=heap)
    h = heap.allocate("still buffered")
    ch2.put(h)
    ch2.close()
    check("get() still drains a value that was buffered before close()", ch2.get() == h, failures)
    check("only after draining does get() return CLOSED", ch2.get() is Channel.CLOSED, failures)
    heap.decref(h)  # creator reference
    heap.decref(h)  # transferred channel reference
    check("close and drain leave no live handles", heap.live_count() == 0, failures)

    ch3 = Channel(capacity=1, heap=heap)
    buffered = heap.allocate("buffered")
    blocked = heap.allocate("blocked")
    ch3.put(buffered)
    done = threading.Event()
    rejected = []

    def blocked_put():
        try:
            ch3.put(blocked)
        except RuntimeError:
            rejected.append(True)
        finally:
            done.set()

    waiter = threading.Thread(target=blocked_put, daemon=True)
    waiter.start()
    time.sleep(0.05)
    check("a full channel blocks the second producer before close", not done.is_set(), failures)
    ch3.close()
    waiter.join(timeout=2.0)
    check("close wakes a blocked producer and rejects its put", done.is_set() and bool(rejected), failures)
    check("rejected put leaves the creator reference alive", heap.is_alive(blocked), failures)
    check("close preserves an already buffered value", ch3.get() == buffered, failures)
    heap.decref(buffered)  # creator reference
    heap.decref(buffered)  # transferred channel reference
    heap.decref(blocked)  # rejected put retained only the creator reference
    check("closed put path leaves no live handles", heap.live_count() == 0, failures)


def stress_test(failures: list, num_values: int = 300, num_consumers: int = 5) -> None:
    heap = GCHeap()
    ch = Channel(capacity=1, heap=heap)  # smallest possible buffer -> maximum contention
    values = list(range(num_values))

    delivered = producer_consumer_driver(heap, values, ch, num_consumers=num_consumers)

    check(f"every one of {num_values} values delivered exactly once", sorted(v for _, v in delivered) == values, failures)
    check("no handle was delivered twice", len({h for h, _ in delivered}) == len(delivered), failures)
    check("GCHeap is fully drained after the run (no leaked references, nothing left buffered)", heap.live_count() == 0, failures)


def main() -> int:
    failures: list = []

    print("Replaying the Part A, Question 1 bounded put/get trace...\n")
    bounded_trace_test(failures)
    if failures:
        print(f"\n{len(failures)} check(s) failed -- fix these first. No token issued.")
        return 1

    print("\nTesting close() semantics...\n")
    close_semantics_test(failures)
    if failures:
        print(f"\n{len(failures)} check(s) failed. No token issued.")
        return 1

    print("\nRunning producer/consumer stress test (300 values, 5 consumers, capacity-1 channel)...\n")
    start = time.time()
    stress_test(failures)
    elapsed = time.time() - start
    check(f"driver terminated cleanly without deadlock (took {elapsed:.2f}s)", elapsed < 15.0, failures)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed. No token issued.")
        return 1

    print("CHANNEL_SYNC_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
