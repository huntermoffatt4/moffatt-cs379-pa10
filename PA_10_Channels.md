# PA 10: Channels

**Instructor starter repository:** https://github.com/cwillpinto/cs379-pa10-channels
**Points:** 100. **Due:** Wednesday, November 4, 2026 at 11:59 PM Central.
## CS 379: Programming Languages (Fall 2026)

### 🔧 Pipeline Context
This is the **concurrency stage** of the USILang pipeline, and the **final numbered PA of the semester**. It consumes the memory-safe runtime from PA 9 — objects flowing between threads are `GCHeap` handles, not raw Python references, so their reference counts must stay correct even as they cross thread boundaries — and adds a synchronized, bounded **Channel** that lets producer and consumer threads exchange USILang values safely. What you build here is the concurrency-safe foundation the rest of the term's work (Weeks 12–16: paradigm labs and the capstone extension) sits on top of.

---

### Part A: The Specification (50 Points)
**Instructions:** Answer the following in a separate document (PDF or Markdown).

1. **Bounded Buffer Trace:**
   A channel has capacity 2. Thread P (producer) attempts, in order: `put(1)`, `put(2)`, `put(3)`. Thread C (consumer) attempts, in order: `get()`, `get()`. The operations are interleaved as: `P.put(1)`, `P.put(2)`, `P.put(3)` (starts, but the channel is full), `C.get()`, then `P.put(3)` completes, then `C.get()`. Trace the channel's internal buffer state after each completed operation, and identify the exact moment `P.put(3)` blocks and the exact moment it is allowed to proceed.

2. **Deadlock by Design:**
   Two channels, `ch_a` and `ch_b`, both empty and both capacity 1. Thread 1 executes `ch_b.put(ch_a.get())`. Thread 2 executes `ch_a.put(ch_b.get())`. Diagram the resulting deadlock — show exactly what each thread is blocked waiting on. Then propose a concrete fix (e.g., an ordering rule, a timeout, or a redesign of who produces vs. consumes on which channel) and explain why it breaks the cycle.

3. **Bounded vs. Unbounded, and the GC Connection:**
   An unbounded channel's `put` never blocks. Explain, referencing PA 9's `GCHeap`, why an unbounded channel can still cause a memory problem even though no individual object is leaked or uncollected — connect this to reference counting specifically (what is holding the refcount up while a value sits in the buffer?).

---

### Part B: The Implementation (50 Points)
**Instructions:** Implement a synchronized, bounded channel in `channels.py` and use it to coordinate producer/consumer threads operating on `GCHeap` handles from PA 9.

**Requirements:**
1. Implement `Channel`:
   ```python
   class Channel:
       def __init__(self, capacity: int, heap: GCHeap):
           ...
       def put(self, value) -> None:
           ...  # blocks while the buffer is full
       def get(self):
           ...  # blocks while the buffer is empty
       def close(self) -> None:
           ...  # wakes any blocked threads; subsequent get() on an empty, closed channel returns a sentinel instead of blocking forever
   ```
   Use `threading.Condition` (or an equivalent lock+condition pattern) — a busy-wait / polling `sleep` loop is not acceptable and will be treated as a correctness failure, not a style nitpick.
2. `put` must block when the buffer already holds `capacity` items, and must wake exactly one waiting `get` (or become immediately visible to a next `get` call) once space frees up. `get` must block when the buffer is empty and wake once an item is available.
3. Values passed through the channel must be `GCHeap` handles (PA 9). The constructor receives the shared heap. `put` must `incref` a handle only after confirming the channel is open and space is available, before enqueuing it. The channel owns that reference while buffered. `get` transfers it to the caller without another count change; the caller eventually calls `decref`. A producer releases its creator reference after a successful `put`. A `put` on a closed channel raises `RuntimeError` and leaves the creator reference with the caller. `close` wakes blocked producers and consumers, and buffered items remain available in FIFO order before the closed sentinel.
4. Write a producer/consumer driver: one producer thread pushes a sequence of USILang values (allocated through `GCHeap.allocate`) onto a bounded channel; one or more consumer threads pull them off and process them (e.g., sum numeric values). No value may be delivered twice, dropped, or corrupted under concurrent access.
5. **No Deadlocks in the Driver:** your submitted producer/consumer driver must terminate cleanly (producer signals completion via `close()`, consumers exit on the sentinel) — a driver that requires killing the process is an automatic failure of this requirement.

**Verification:** Run `python test_channels.py`. The harness runs the bounded put/get trace from Part A Question 1 under real threads and asserts the blocking points occur where predicted, stress-tests a producer/consumer pair with a capacity-1 channel and confirms every value is delivered exactly once with correct `GCHeap` refcounts throughout (no premature collection while a value sits in the buffer, no leaked references after `close()`), and confirms the driver terminates without deadlock. If every assertion passes, the script prints:
```
CHANNEL_SYNC_VERIFIED
```

---

### 🚀 Submission
1. `PA10_Theory.pdf` (or `.md`) — Part A answers.
2. `channels.py` — your `Channel` implementation and the producer/consumer driver — plus your working prior-stage files.
3. Terminal output/screenshot showing the **`CHANNEL_SYNC_VERIFIED`** Success Token from `python test_channels.py`.

4. Your student-owned repository URL and commit SHA in Blackboard, alongside the required execution evidence.
