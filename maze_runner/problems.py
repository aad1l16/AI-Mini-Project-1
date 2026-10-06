"""
problems.py
-----------
Search problem definitions.

You do NOT need to edit this file, but read it carefully. Every search
algorithm you write in search.py only talks to a problem through the four
methods of SearchProblem, so the same code will solve mazes, the small test
graphs used by the grader, and the key-hunting problem in griever_hole.py.
"""

from collections import deque

import maze as mazeModule


class SearchProblem:
    """
    The abstract interface of a search problem. You never create one of these
    directly; the concrete problems below implement it.
    """

    def getStartState(self):
        """Returns the start state of the problem."""
        raise NotImplementedError

    def isGoalState(self, state):
        """Returns True if and only if 'state' is a goal state."""
        raise NotImplementedError

    def getSuccessors(self, state):
        """
        Returns a list of (successor, action, stepCost) triples, where
        'successor' is a state reachable from 'state' by doing 'action',
        and 'stepCost' is the cost of doing so.

        Calling this method counts as EXPANDING 'state'. Only call it when you
        pop a state off the fringe and actually expand it: the grader
        watches the order of these calls.
        """
        raise NotImplementedError

    def getCostOfActions(self, actions):
        """Returns the total cost of a sequence of actions from the start."""
        raise NotImplementedError


class MazeProblem(SearchProblem):
    """
    Get a runner from the Glade door (S) to the exit (E).

    State: the runner's position, a (row, col) tuple.
    Actions: 'North', 'South', 'East', 'West'.
    Step cost: the terrain cost of the cell being entered (see maze.py).
    """

    def __init__(self, maze, start=None, goal=None):
        self.maze = maze
        self.startState = start if start is not None else maze.start
        self.goal = goal if goal is not None else maze.exit
        # A scratch dictionary your heuristics may use to cache information.
        self.heuristicInfo = {}
        # Bookkeeping for the display and the grader. Do not touch.
        self._expanded = 0
        self._expandedOrder = []

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        return state == self.goal

    def getSuccessors(self, state):
        self._expanded += 1
        self._expandedOrder.append(state)
        return [(nxt, action, self.maze.cost(nxt))
                for action, nxt in self.maze.neighbors(state)]

    def getCostOfActions(self, actions):
        if actions is None:
            return float('inf')
        pos = self.startState
        total = 0
        for action in actions:
            dr, dc = mazeModule.DELTA[action]
            pos = (pos[0] + dr, pos[1] + dc)
            if self.maze.isWall(pos):
                return float('inf')
            total += self.maze.cost(pos)
        return total

    # Helpers used by the display ---------------------------------------
    def positionOf(self, state):
        return state

    def expandedPositions(self):
        return list(self._expandedOrder)


class GraphProblem(SearchProblem):
    """
    A search problem on an explicit, directed graph. The grader uses these
    small graphs to check the exact order in which your algorithms expand
    states. You can build your own to debug, e.g.

        p = GraphProblem('A', ['G'], [('A', 'A->B', 'B', 1), ('B', 'B->G', 'G', 2)])

    Each edge is (fromState, action, toState, cost). Successors are returned in
    the same order the edges are listed. 'heuristic' is an optional dictionary
    mapping state -> estimated cost to goal.
    """

    def __init__(self, start, goals, edges, heuristic=None):
        self.start = start
        self.goals = set(goals)
        self.edges = {}
        for (u, action, v, cost) in edges:
            self.edges.setdefault(u, []).append((v, action, cost))
            self.edges.setdefault(v, [])
        self.edges.setdefault(start, [])
        self.heuristic = dict(heuristic or {})
        self.heuristicInfo = {}
        self.expandedStates = []

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state in self.goals

    def getSuccessors(self, state):
        self.expandedStates.append(state)
        return list(self.edges.get(state, []))

    def getCostOfActions(self, actions):
        if actions is None:
            return float('inf')
        state = self.start
        total = 0
        for action in actions:
            for (v, a, cost) in self.edges.get(state, []):
                if a == action:
                    state = v
                    total += cost
                    break
            else:
                return float('inf')
        return total

    def endStateOfActions(self, actions):
        state = self.start
        for action in actions:
            for (v, a, cost) in self.edges.get(state, []):
                if a == action:
                    state = v
                    break
            else:
                return None
        return state


def graphHeuristic(state, problem):
    """The heuristic stored inside a GraphProblem."""
    return problem.heuristic.get(state, 0)


def mazeDistance(pos1, pos2, maze, cache=None):
    """
    The number of STEPS on the shortest path between pos1 and pos2, ignoring
    terrain costs (every step counts as 1). Because every step in the maze
    costs at least 1, this never overestimates the true travel cost.

    Pass a dictionary as 'cache' (for example problem.heuristicInfo) to avoid
    recomputing distances you have already asked for.

    This is provided for you (it is a plain breadth-first search) so that your
    heuristics in griever_hole.py do not depend on your own search code.
    """
    key = ('mazeDistance', pos1, pos2)
    if cache is not None and key in cache:
        return cache[key]
    # One BFS from pos1 gives the distance to every cell; cache all of them.
    dist = {pos1: 0}
    frontier = deque([pos1])
    while frontier:
        cur = frontier.popleft()
        for _, nxt in maze.neighbors(cur):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                frontier.append(nxt)
    if cache is not None:
        for p, d in dist.items():
            cache[('mazeDistance', pos1, p)] = d
    return dist.get(pos2, float('inf'))
