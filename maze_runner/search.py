"""
search.py
---------
THE MAZE RUNNER — Mini Project 1: Classical Search

This is where you implement the search algorithms (Questions 1–7).

Every algorithm receives a SearchProblem (see problems.py) and must return a
LIST OF ACTIONS that leads from the start state to a goal state, e.g.
['South', 'South', 'East']. Return [] if the start state is already a goal.

Conventions the grader relies on (please read — they matter!):

  * Use the fringe containers from util.py (Stack, Queue, PriorityQueue).
  * Calling problem.getSuccessors(state) counts as EXPANDING that state.
    Call it exactly once per expanded state, and never for a state you only
    generated.
  * Goal test when a state is POPPED from the fringe (just before you would
    expand it), not when it is pushed. (For BFS the grader also accepts
    the "early" goal test done when a state is generated.)
  * Push successors in the order getSuccessors returns them.
  * Q1, Q2, Q5, Q6, Q7 are GRAPH searches: keep a set of already-expanded
    states and never expand the same state twice.
"""

import util
from util import Stack, Queue, PriorityQueue, CUTOFF
from heuristics import nullHeuristic


# ----------------------------------------------------------------------
# Q0 (worked example, not graded): always go right
# ----------------------------------------------------------------------
def alwaysRightSearch(problem):
    """
    Not a real search: the runner keeps stepping right ('East') until he
    reaches the goal. If a wall blocks the way east, he is stuck and gives up
    (returns None). It shows you how to use the problem's methods. Try it:
        python runner.py -l maze_tiny -a right     (escapes)
        python runner.py -l maze_small -a right       (walks into a wall)
    """
    state = problem.getStartState()
    actions = []
    while not problem.isGoalState(state):
        successors = problem.getSuccessors(state)   # list of (next, action, cost)
        east = [s for s in successors if s[1] == 'East']
        if not east:
            return None   # a wall straight ahead: the doors close with him inside
        nextState, action, stepCost = east[0]
        actions.append(action)
        state = nextState
    return actions


def helper_func(fringe, problem):
    expanded = set()
    fringe.push((problem.getStartState(), []))
    while not fringe.isEmpty():
        state, actions = fringe.pop()
        if problem.isGoalState(state): return actions
        if state not in expanded:
            expanded.add(state)
            for (successor, action, cost) in problem.getSuccessors(state):
                fringe.push((successor, actions + [action]))
    return None

# ----------------------------------------------------------------------
# Q1: Depth-First Search
# ----------------------------------------------------------------------
def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first (graph search).

    To get started, try printing:
        print("Start:", problem.getStartState())
        print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
        print("Start's successors:", problem.getSuccessors(problem.getStartState()))

    Hint: a fringe entry can hold more than a state. Storing
    (state, actionsSoFar) is an easy way to remember how you got there.
    """
    "*** YOUR CODE HERE ***"
    actions = helper_func(util.Stack(), problem)
    if actions is None:
        return None
    return actions



# ----------------------------------------------------------------------
# Q2: Breadth-First Search
# ----------------------------------------------------------------------
def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first (graph search)."""
    "*** YOUR CODE HERE ***"
    actions = helper_func(util.Queue(), problem)
    if actions is None:
        return None
    return actions


# ----------------------------------------------------------------------
# Q3: Depth-Limited Search
# ----------------------------------------------------------------------

def recursive_dls_helper(state, actions, path, problem, limit):
    if(problem.isGoalState(state)): return actions
    if(limit == 0): return util.CUTOFF
    cutoff_occurred = False
    for (successor, action, cost) in problem.getSuccessors(state):
        if successor not in path:
            temp = recursive_dls_helper(successor, actions + [action], path | {successor}, problem, limit - 1)
            if temp is not util.CUTOFF and temp is not None:
                return temp
            elif temp is util.CUTOFF: cutoff_occurred = True
    if cutoff_occurred:
        return util.CUTOFF
    else: return None
def depthLimitedSearch(problem, limit):
    """
    Depth-first search that never goes deeper than 'limit' actions.

    Return value:
      * a list of at most 'limit' actions that reaches a goal, or
      * CUTOFF (from util) if no goal was found but the search was stopped
        by the depth limit somewhere, so a deeper solution may exist, or
      * None if no goal was found and the limit was never reached, which
        proves there is no solution at all.

    The start state is at depth 0. A state at depth == limit may be goal
    tested but must not be expanded.

    Do NOT use a global explored set here (think about why that can make the
    search miss a solution that fits within the limit). Instead, avoid cycles
    by not revisiting a state that is already on the current path.
    """
    "*** YOUR CODE HERE ***"
    return recursive_dls_helper(problem.getStartState(), [], {problem.getStartState()}, problem, limit)


# ----------------------------------------------------------------------
# Q4: Iterative Deepening Search
# ----------------------------------------------------------------------
def iterativeDeepeningSearch(problem, maxDepth=10000):
    """
    Run depthLimitedSearch with limit = 0, 1, 2, ... until it finds a
    solution. Return that solution, or None if the problem has no solution
    (or none within maxDepth).
    """
    "*** YOUR CODE HERE ***"
    i = 0
    while i < maxDepth:
        temp = depthLimitedSearch(problem, i)
        if temp is not util.CUTOFF:
            return temp
        i += 1


# ----------------------------------------------------------------------
# Q5: Uniform-Cost Search
# ----------------------------------------------------------------------
def uniformCostSearch(problem):
    """Search the node of least total path cost g(n) first (graph search)."""
    "*** YOUR CODE HERE ***"
    fringe = util.PriorityQueue()
    expanded = set()
    fringe.push((problem.getStartState(), [], 0), 0)
    while not fringe.isEmpty():
        state, actions, cost = fringe.pop()
        if problem.isGoalState(state):
            return actions
        if state not in expanded:
            expanded.add(state)
            for (successor, action, succCost) in problem.getSuccessors(state):
                fringe.push((successor, actions + [action], cost + succCost), cost + succCost)
    return None


# ----------------------------------------------------------------------
# Q6: Greedy Best-First Search
# ----------------------------------------------------------------------
def greedyBestFirstSearch(problem, heuristic=nullHeuristic):
    """
    Search the node that SEEMS closest to the goal first, i.e. the one with
    the lowest heuristic(state, problem) value (graph search).
    """
    "*** YOUR CODE HERE ***"
    fringe = util.PriorityQueue()
    expanded = set()
    start_state = problem.getStartState()
    fringe.push((start_state, [], 0), heuristic(start_state, problem))
    while not fringe.isEmpty():
        state, actions, cost = fringe.pop()
        if problem.isGoalState(state):
            return actions
        if state not in expanded:
            expanded.add(state)
            for (successor, action, succCost) in problem.getSuccessors(state):
                fringe.push((successor, actions + [action], succCost + cost), heuristic(successor, problem))
    return None


# ----------------------------------------------------------------------
# Q7: A* Search
# ----------------------------------------------------------------------
def aStarSearch(problem, heuristic=nullHeuristic):
    """
    Search the node with the lowest f(n) = g(n) + heuristic(n) first
    (graph search).
    """
    "*** YOUR CODE HERE ***"
    fringe = util.PriorityQueue()
    expanded = set()
    start_state = problem.getStartState()
    start_cost = 0
    fringe.push((start_state, [], 0), heuristic(start_state, problem))
    while not fringe.isEmpty():
        state, actions, cost = fringe.pop()
        if problem.isGoalState(state):
            return actions
        if state not in expanded:
            expanded.add(state)
            for (successor, action, succCost) in problem.getSuccessors(state):
                fringe.push((successor, actions + [action], succCost + cost), heuristic(successor, problem) + succCost + cost)
    return None

# Abbreviations
always_right = alwaysRightSearch
dfs = depthFirstSearch
bfs = breadthFirstSearch
dls = depthLimitedSearch
ids = iterativeDeepeningSearch
ucs = uniformCostSearch
gbfs = greedyBestFirstSearch
astar = aStarSearch
