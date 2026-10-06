"""
util.py
-------
Data structures and helpers for the Maze Runner project.

You do NOT need to edit this file, but you should read it: the Stack, Queue
and PriorityQueue classes below are the fringe (frontier) containers you are
expected to use in search.py.
"""

import heapq
import inspect
from collections import deque


class Stack:
    """A last-in-first-out (LIFO) container."""

    def __init__(self):
        self.list = []

    def push(self, item):
        """Push 'item' onto the stack."""
        self.list.append(item)

    def pop(self):
        """Pop the most recently pushed item from the stack."""
        return self.list.pop()

    def isEmpty(self):
        """Returns True if the stack is empty."""
        return len(self.list) == 0

    def __len__(self):
        return len(self.list)


class Queue:
    """A first-in-first-out (FIFO) container."""

    def __init__(self):
        self.list = deque()

    def push(self, item):
        """Enqueue 'item' at the back of the queue."""
        self.list.append(item)

    def pop(self):
        """Dequeue the earliest enqueued item still in the queue."""
        return self.list.popleft()

    def isEmpty(self):
        """Returns True if the queue is empty."""
        return len(self.list) == 0

    def __len__(self):
        return len(self.list)


class PriorityQueue:
    """
    A min-priority queue: pop() always returns the item with the LOWEST
    priority value.

    Ties are broken in first-in-first-out order, which makes every search
    deterministic (the grader relies on this).

    Note that this queue does not change the priority of an item that is
    already inside it. If you push the same item twice with different
    priorities, it will simply be stored twice. Use update() if you want
    decrease-key behaviour.
    """

    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        """
        If 'item' is already in the queue with a higher priority, lower its
        priority and rebuild the heap. If it is already there with an equal or
        lower priority, do nothing. If it is not there at all, push it.
        """
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    return
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                return
        self.push(item, priority)

    def __len__(self):
        return len(self.heap)


class _Cutoff:
    """Singleton returned by depth-limited search when it hits the depth limit."""

    def __repr__(self):
        return "CUTOFF"

    __str__ = __repr__


# depthLimitedSearch returns this object (compare with `result is CUTOFF`)
# when it hit the depth limit, so a solution might exist deeper down.
CUTOFF = _Cutoff()


def manhattanDistance(xy1, xy2):
    """Returns the Manhattan distance between points xy1 and xy2."""
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


class NotImplementedYet(Exception):
    """Raised by functions that the student still has to implement."""


def raiseNotDefined():
    """Call this in functions you have not implemented yet."""
    caller = inspect.stack()[1]
    raise NotImplementedYet(
        "Method not implemented: %s (line %d of %s)"
        % (caller.function, caller.lineno, caller.filename)
    )
