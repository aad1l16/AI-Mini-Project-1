"""
heuristics.py
-------------
Heuristics for the basic maze problem (Question 6).

A heuristic is a function heuristic(state, problem) that returns an estimate
of the cost of the cheapest path from 'state' to a goal. For a MazeProblem,
'state' is a (row, col) tuple and the goal position is 'problem.goal'.
"""

import math

import util


def nullHeuristic(state, problem=None):
    """The trivial heuristic: it knows nothing, so it always says 0."""
    return 0


def manhattanHeuristic(state, problem):
    """
    Q6: the Manhattan distance from 'state' to problem.goal:
        |row1 - row2| + |col1 - col2|
    """
    "*** YOUR CODE HERE ***"
    return util.manhattanDistance(state, problem.goal)


def euclideanHeuristic(state, problem):
    """
    Q6: the straight-line (Euclidean) distance from 'state' to problem.goal.
    """
    "*** YOUR CODE HERE ***"
    x1, y1 = state
    x2, y2 = problem.goal
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
