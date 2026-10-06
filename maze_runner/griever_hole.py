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

    def getStartState(self):
        """Returns the start state, a tuple (startPosition, ...)."""
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def isGoalState(self, state):
        """True when every code piece has been collected AND Thomas is at the exit."""
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

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
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()
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
    """
    Q9: A heuristic for KeyHuntProblem.

    It must be CONSISTENT (and therefore admissible): for every state s and
    successor s' reached with step cost c,  h(s) <= c + h(s'),  and h must be
    0 at goal states. The grader checks this.

    The more informed (larger) your heuristic is while staying consistent,
    the fewer states A* expands and the more points you earn.

    Useful tools:
      * problem.keys, problem.exit, and whatever your state stores
      * mazeDistance(pos1, pos2, problem.maze, problem.heuristicInfo) gives
        the true number of steps between two cells, and caches the result
      * util.manhattanDistance(pos1, pos2)
    """
    position = state[0]
    "*** YOUR CODE HERE ***"
    return 0   # the trivial (but consistent!) heuristic
