"""
maze.py
-------
Loads maze layouts (mazes/*.maze) and answers questions about them.

You do NOT need to edit this file.

Layout characters
    %   wall (ivy-covered stone, impassable)
    ' ' or .   open corridor           step cost 1
    S   the Glade door (start)       step cost 1
    E   the exit / Griever Hole      step cost 1
    K   a piece of the escape code   step cost 1
    ~   thick ivy                    step cost 3
    G   Griever territory            step cost 10

The step cost is paid when you ENTER a cell. Lines at the top of a file that
start with '#' are comments (the first one is used as the maze's title).

Positions are (row, col) tuples. Row 0 is the top of the maze, so moving
North decreases the row and moving East increases the column.
"""

import os

WALL = '%'
START = 'S'
EXIT = 'E'
KEY = 'K'
IVY = '~'
GRIEVER = 'G'

TERRAIN_COST = {
    ' ': 1, '.': 1, START: 1, EXIT: 1, KEY: 1,
    IVY: 3,
    GRIEVER: 10,
}

TERRAIN_NAME = {
    ' ': 'corridor', '.': 'corridor', START: 'Glade door', EXIT: 'exit',
    KEY: 'code piece', IVY: 'ivy', GRIEVER: 'Griever territory', WALL: 'wall',
}

# The order in which neighbours are generated. Keep it fixed: the grader
# checks the exact order in which your algorithms expand states.
NORTH, SOUTH, EAST, WEST = 'North', 'South', 'East', 'West'
DIRECTIONS = [
    (NORTH, (-1, 0)),
    (SOUTH, (1, 0)),
    (EAST, (0, 1)),
    (WEST, (0, -1)),
]
DELTA = dict(DIRECTIONS)

MAZE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mazes')


class Maze:
    def __init__(self, lines, name='maze', title=None):
        width = max(len(line) for line in lines)
        # Pad ragged lines with walls so the grid is rectangular.
        self.grid = [line.ljust(width, WALL) for line in lines]
        self.height = len(self.grid)
        self.width = width
        self.name = name
        self.title = title or name

        self.start = None
        self.exit = None
        self.keys = []
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                if ch not in TERRAIN_COST and ch != WALL:
                    raise ValueError("Unknown character %r at %s in maze %s" % (ch, (r, c), name))
                if ch == START:
                    if self.start is not None:
                        raise ValueError("Maze %s has more than one S" % name)
                    self.start = (r, c)
                elif ch == EXIT:
                    if self.exit is not None:
                        raise ValueError("Maze %s has more than one E" % name)
                    self.exit = (r, c)
                elif ch == KEY:
                    self.keys.append((r, c))
        if self.start is None or self.exit is None:
            raise ValueError("Maze %s needs exactly one S and one E" % name)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def inBounds(self, pos):
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width

    def terrain(self, pos):
        """The layout character at pos."""
        r, c = pos
        return self.grid[r][c]

    def isWall(self, pos):
        return (not self.inBounds(pos)) or self.terrain(pos) == WALL

    def cost(self, pos):
        """The cost of stepping INTO pos."""
        return TERRAIN_COST[self.terrain(pos)]

    def neighbors(self, pos):
        """
        Legal moves from pos, as a list of (action, nextPosition) pairs,
        always in the order North, South, East, West.
        """
        r, c = pos
        result = []
        for action, (dr, dc) in DIRECTIONS:
            nxt = (r + dr, c + dc)
            if not self.isWall(nxt):
                result.append((action, nxt))
        return result

    def openCells(self):
        return [(r, c) for r in range(self.height) for c in range(self.width)
                if self.grid[r][c] != WALL]

    def hasTerrainCosts(self):
        return any(ch in (IVY, GRIEVER) for row in self.grid for ch in row)

    def __str__(self):
        return '\n'.join(self.grid)


def mazePath(name):
    """Resolve a maze name ('maze_small') or a file path to a file path."""
    if os.path.exists(name):
        return name
    candidate = os.path.join(MAZE_DIR, name)
    if not candidate.endswith('.maze'):
        candidate += '.maze'
    if os.path.exists(candidate):
        return candidate
    raise FileNotFoundError("Could not find maze '%s' (looked in %s)" % (name, MAZE_DIR))


def loadMaze(name):
    path = mazePath(name)
    with open(path) as f:
        raw = f.read().splitlines()
    comments = []
    while raw and raw[0].startswith('#'):
        comments.append(raw.pop(0).lstrip('#').strip())
    while raw and not raw[-1].strip():
        raw.pop()
    base = os.path.splitext(os.path.basename(path))[0]
    title = comments[0] if comments else base
    return Maze(raw, name=base, title=title)


def availableMazes():
    return sorted(f[:-5] for f in os.listdir(MAZE_DIR) if f.endswith('.maze'))
