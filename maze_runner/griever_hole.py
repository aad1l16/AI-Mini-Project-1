"""
griever_hole.py
---------------
Questions 8 and 9: escaping through the Griever Hole.

The Griever Hole only opens after the runners have entered the escape code.
The pieces of the code (marked K in the maze) are scattered through the
corridors. Thomas has to pick up ALL of them, in any order, and then reach the
exit E. Picking up a piece happens automatically when he steps onto its cell.

Try it once you are done:
    python runner.py -l keys_small -p keys -a bfs
    python runner.py -l keys_medium -p keys -a astar -H keyhunt
"""

import util
from problems import SearchProblem, mazeDistance
from itertools import permutations


class KeyHuntProblem(SearchProblem):
    """
    Q8: Collect every code piece, then reach the exit.

    You choose the state representation, with two requirements:
    1. A state must be HASHABLE (tuples, frozensets, ints, strings... but
        not lists, sets or dicts), because your search keeps them in sets.
    2. A state must be a TUPLE whose FIRST element is Thomas's (row, col)
        position. The display and the grader read state[0].

    Keep the state small: store only what you need to know to decide what
    happens next. Do NOT put the whole maze in the state.
    """

    def __init__(self, maze):
        self.maze = maze
        self.startPosition = maze.start
        self.keys = tuple(maze.keys)      # positions of all code pieces
        self.exit = maze.exit
        self.heuristicInfo = {}           # scratch space for your heuristic
        # Bookkeeping for the display and the grader. Do not touch.
        self._expanded = 0
        self._expandedOrder = []
        "*** YOUR CODE HERE (optional: set up anything else you need) ***"
        # Not needed

    def getStartState(self):
        """Returns the start state, a tuple (startPosition, remainingKeys)."""
        # If Thomas starts on a code piece, it is collected already.
        remaining = frozenset(k for k in self.keys if k != self.startPosition)
        return (self.startPosition, remaining)

    def isGoalState(self, state):
        """True when every code piece has been collected AND Thomas is at the exit."""
        position, remaining = state
        return len(remaining) == 0 and position == self.exit

    def getSuccessors(self, state):
        """
        Returns a list of (successor, action, stepCost) triples.

        Use self.maze.neighbors(position), which gives the legal
        (action, nextPosition) pairs in North, South, East, West order, and
        self.maze.cost(nextPosition) for the step cost.
        """
        # Bookkeeping. Keep these two lines.
        self._expanded += 1
        self._expandedOrder.append(state[0])

        successors = []
        position, remaining = state
        for action, nextPosition in self.maze.neighbors(position):
            stepCost = self.maze.cost(nextPosition)
            if nextPosition in remaining:
                # Stepping on a code piece collects it.
                newRemaining = remaining - frozenset([nextPosition])
            else:
                newRemaining = remaining
            successors.append(((nextPosition, newRemaining), action, stepCost))
        return successors

    # --- Provided: you do not need to change anything below -------------
    def getCostOfActions(self, actions):
        """Total step cost of a sequence of actions (inf if it hits a wall)."""
        import maze as mazeModule
        if actions is None:
            return float('inf')
        pos = self.startPosition
        total = 0
        for action in actions:
            dr, dc = mazeModule.DELTA[action]
            pos = (pos[0] + dr, pos[1] + dc)
            if self.maze.isWall(pos):
                return float('inf')
            total += self.maze.cost(pos)
        return total

    def positionOf(self, state):
        return state[0]

    def expandedPositions(self):
        return list(self._expandedOrder)


def keyHuntHeuristic(state, problem):
    position, remaining = state[0], state[1]
    cache = problem.heuristicInfo
    memoKey = ('keyhunt', position, remaining)
    if memoKey in cache:
        return cache[memoKey]
    exitPos = problem.exit
    maze = problem.maze
    def dist(a, b):
        return mazeDistance(a, b, maze, cache)
    if len(remaining) == 0:
        # No keys left: only the walk to the exit remains.
        value = dist(exitPos, position)
    else:
        value = float('inf')
        # Try every possible order of visiting the remaining keys.
        for order in permutations(remaining):
            # walk from Thomas to the first key in this order
            total = dist(order[0], position)
            # walk from each key to the next one
            for i in range(len(order) - 1):
                total += dist(order[i], order[i + 1])
            # finally walk from the last key to the exit
            total += dist(exitPos, order[-1])
            # keep the shortest order found so far
            if total < value:
                value = total

    cache[memoKey] = value
    return value
