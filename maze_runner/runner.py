"""
runner.py
---------
Run a search algorithm on a maze and watch the runner escape (or not).

Examples
    python runner.py                                  # BFS on maze_tiny
    python runner.py -l maze_small -a dfs
    python runner.py -l griever_alley -a ucs
    python runner.py -l greedy_trap -a astar -H manhattan
    python runner.py -l maze_small -a dls -d 40
    python runner.py -l keys_small -p keys -a astar -H keyhunt
    python runner.py -l maze_medium --compare            # table of all algorithms
    python runner.py -l maze_medium -a bfs -t            # text output, no window
    python runner.py --list                           # list all mazes

Run 'python runner.py -h' for all options.
"""

import argparse
import contextlib
import signal
import sys
import time

import maze as mazeModule
import util
from problems import MazeProblem

sys.setrecursionlimit(20000)

ALGORITHM_NAMES = {
    'right': 'Always go right',
    'dfs': 'Depth-first search',
    'bfs': 'Breadth-first search',
    'dls': 'Depth-limited search',
    'ids': 'Iterative deepening search',
    'ucs': 'Uniform-cost search',
    'gbfs': 'Greedy best-first search',
    'astar': 'A* search',
}
INFORMED = ('gbfs', 'astar')


class SearchTimeout(Exception):
    pass


@contextlib.contextmanager
def timeLimit(seconds):
    """Raise SearchTimeout if the body runs longer than 'seconds' (Unix only)."""
    if not seconds or not hasattr(signal, 'SIGALRM'):
        yield
        return

    def handler(signum, frame):
        raise SearchTimeout("timed out after %s seconds" % seconds)

    old = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def timedProblem(problem, seconds):
    """Make problem.getSuccessors raise SearchTimeout once 'seconds' have
    passed. Unlike timeLimit, this also works on Windows."""
    if not seconds:
        return problem
    deadline = time.perf_counter() + seconds
    original = problem.getSuccessors

    def getSuccessors(state):
        if time.perf_counter() > deadline:
            raise SearchTimeout("timed out after %s seconds" % seconds)
        return original(state)

    problem.getSuccessors = getSuccessors
    return problem


def getHeuristic(name):
    import heuristics
    if name in (None, 'null'):
        return heuristics.nullHeuristic
    if name == 'manhattan':
        return heuristics.manhattanHeuristic
    if name == 'euclidean':
        return heuristics.euclideanHeuristic
    if name == 'keyhunt':
        import griever_hole
        return griever_hole.keyHuntHeuristic
    raise ValueError("Unknown heuristic: %s" % name)


def buildProblem(maze, kind):
    if kind == 'maze':
        return MazeProblem(maze)
    if kind == 'keys':
        import griever_hole
        return griever_hole.KeyHuntProblem(maze)
    raise ValueError("Unknown problem type: %s" % kind)


def callAlgorithm(algorithm, problem, heuristic=None, depth=None):
    import search
    if algorithm == 'right':
        return search.alwaysRightSearch(problem)
    if algorithm == 'dfs':
        return search.depthFirstSearch(problem)
    if algorithm == 'bfs':
        return search.breadthFirstSearch(problem)
    if algorithm == 'dls':
        return search.depthLimitedSearch(problem, depth)
    if algorithm == 'ids':
        return search.iterativeDeepeningSearch(problem)
    if algorithm == 'ucs':
        return search.uniformCostSearch(problem)
    if algorithm == 'gbfs':
        return search.greedyBestFirstSearch(problem, heuristic)
    if algorithm == 'astar':
        return search.aStarSearch(problem, heuristic)
    raise ValueError("Unknown algorithm: %s" % algorithm)


def checkSolution(maze, kind, actions):
    """Walk the actions through the maze. Returns (ok, message)."""
    if not isinstance(actions, list):
        return False, "expected a list of actions, got %r" % (actions,)
    pos = maze.start
    collected = set()
    for i, action in enumerate(actions):
        if action not in mazeModule.DELTA:
            return False, "action %d is %r, which is not a legal action" % (i, action)
        dr, dc = mazeModule.DELTA[action]
        pos = (pos[0] + dr, pos[1] + dc)
        if maze.isWall(pos):
            return False, "action %d (%s) walks into a wall at %s" % (i, action, pos)
        if pos in maze.keys:
            collected.add(pos)
    if pos != maze.exit:
        return False, "the path ends at %s, not at the exit %s" % (pos, maze.exit)
    if kind == 'keys' and len(collected) != len(maze.keys):
        return False, "the path only collects %d of %d code pieces" % (len(collected), len(maze.keys))
    return True, "escaped"


def solve(maze, kind, algorithm, heuristicName=None, depth=None, timeout=None):
    """Run one search. Returns a dict describing what happened."""
    problem = timedProblem(buildProblem(maze, kind), timeout)
    heuristic = getHeuristic(heuristicName) if algorithm in INFORMED else None
    result = {'problem': problem, 'actions': None, 'error': None}
    start = time.perf_counter()
    try:
        with timeLimit(timeout):
            actions = callAlgorithm(algorithm, problem, heuristic, depth)
        result['actions'] = actions
    except util.NotImplementedYet as e:
        result['error'] = str(e)
    except SearchTimeout as e:
        result['error'] = str(e)
    result['time'] = time.perf_counter() - start
    result['expanded'] = problem._expanded
    actions = result['actions']
    if result['error'] is None:
        if actions is util.CUTOFF:
            result['status'] = 'cutoff'
        elif actions is None:
            result['status'] = 'failure'
        else:
            ok, msg = checkSolution(maze, kind, actions)
            result['status'] = 'escaped' if ok else 'invalid'
            result['message'] = msg
            if ok:
                result['cost'] = problem.getCostOfActions(actions)
                result['steps'] = len(actions)
    else:
        result['status'] = 'error'
    return result


def describe(result, algorithm, heuristicName, depth):
    name = ALGORITHM_NAMES[algorithm]
    if algorithm in INFORMED:
        name += " (heuristic: %s)" % heuristicName
    if algorithm == 'dls':
        name += " (limit: %s)" % depth
    lines = ["Algorithm:      " + name]
    status = result['status']
    if status == 'escaped':
        lines.append("Result:         ESCAPED!  path cost %s, %d steps" % (_fmt(result['cost']), result['steps']))
    elif status == 'cutoff':
        lines.append("Result:         CUTOFF - no exit within %s steps" % depth)
    elif status == 'failure':
        lines.append("Result:         no path found - the doors closed")
    elif status == 'invalid':
        lines.append("Result:         INVALID PATH - " + result['message'])
    else:
        lines.append("Result:         ERROR - " + result['error'])
    lines.append("Nodes expanded: %d" % result['expanded'])
    lines.append("Search time:    %.3f s" % result['time'])
    return lines


def _fmt(x):
    return str(int(x)) if float(x).is_integer() else "%.2f" % x


def compare(maze, kind, heuristicName, depth, timeout):
    algorithms = ['dfs', 'bfs', 'ids', 'ucs', 'gbfs', 'astar']
    if depth is not None:
        algorithms.insert(2, 'dls')
    print("\n%s  (%dx%d, problem: %s)" % (maze.title, maze.height, maze.width, kind))
    header = "%-34s %10s %8s %10s %9s" % ("Algorithm", "Path cost", "Steps", "Expanded", "Time (s)")
    print(header)
    print('-' * len(header))
    for alg in algorithms:
        h = heuristicName if alg in INFORMED else None
        r = solve(maze, kind, alg, h, depth, timeout)
        label = ALGORITHM_NAMES[alg] + (" [%s]" % h if h else "")
        if r['status'] == 'escaped':
            print("%-34s %10s %8d %10d %9.3f" % (label, _fmt(r['cost']), r['steps'], r['expanded'], r['time']))
        else:
            what = r['error'] if r['status'] == 'error' else r['status']
            print("%-34s %10s %8s %10d %9.3f   (%s)" % (label, '-', '-', r['expanded'], r['time'], what))


def main(argv=None):
    parser = argparse.ArgumentParser(description="The Maze Runner: classical search.")
    parser.add_argument('-l', '--maze', default='maze_tiny', help="maze name or path (default: maze_tiny)")
    parser.add_argument('-a', '--algorithm', default='bfs', choices=sorted(ALGORITHM_NAMES))
    parser.add_argument('-p', '--problem', default='maze', choices=['maze', 'keys'],
                        help="'maze' = reach the exit, 'keys' = collect all code pieces then exit")
    parser.add_argument('-H', '--heuristic', default=None,
                        choices=['null', 'manhattan', 'euclidean', 'keyhunt'],
                        help="heuristic for gbfs/astar (default: manhattan, or keyhunt with -p keys)")
    parser.add_argument('-d', '--depth', type=int, default=None, help="depth limit for dls")
    parser.add_argument('-t', '--text', action='store_true', help="text output instead of a window")
    parser.add_argument('-q', '--quiet', action='store_true', help="only print statistics")
    parser.add_argument('-z', '--zoom', type=float, default=1.0, help="zoom the window")
    parser.add_argument('-f', '--frame-time', type=float, default=None,
                        help="seconds per runner step in the animation")
    parser.add_argument('--compare', action='store_true', help="run every algorithm and print a table")
    parser.add_argument('--timeout', type=float, default=None,
                        help="give up after this many seconds (default: 60, or 10 per algorithm with --compare)")
    parser.add_argument('--list', action='store_true', help="list available mazes and exit")
    args = parser.parse_args(argv)

    if args.list:
        for name in mazeModule.availableMazes():
            m = mazeModule.loadMaze(name)
            print("%-16s %3dx%-3d  %s" % (name, m.height, m.width, m.title))
        return

    maze = mazeModule.loadMaze(args.maze)
    heuristicName = args.heuristic or ('keyhunt' if args.problem == 'keys' else 'manhattan')
    depth = args.depth
    if args.algorithm == 'dls' and depth is None and not args.compare:
        depth = 50
        print("(no -d given; using depth limit %d)" % depth)

    if args.compare:
        compare(maze, args.problem, heuristicName, depth, args.timeout or 10)
        return

    result = solve(maze, args.problem, args.algorithm, heuristicName, depth, args.timeout or 60)
    lines = ["Maze:           %s (%dx%d)" % (maze.title, maze.height, maze.width)]
    lines += describe(result, args.algorithm, heuristicName, depth)
    actions = result['actions'] if result['status'] == 'escaped' else []

    if args.quiet or result['status'] == 'error':
        print('\n'.join(lines))
    elif args.text:
        from display import TextDisplay
        TextDisplay().show(maze, result['problem'], actions, lines)
    else:
        print('\n'.join(lines))
        try:
            from display import TkDisplay
            TkDisplay(args.zoom, args.frame_time).show(maze, result['problem'], actions, lines)
        except Exception as e:   # no display available (e.g. over SSH)
            print("(could not open a window: %s; showing text instead)" % e)
            from display import TextDisplay
            TextDisplay().show(maze, result['problem'], actions, [])


if __name__ == '__main__':
    main()
