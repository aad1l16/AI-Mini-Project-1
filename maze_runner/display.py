"""
display.py
----------
Text and graphical (Tkinter) displays for the Maze Runner.

You do NOT need to edit or read this file.
"""

import maze as mazeModule

# ----------------------------------------------------------------------
# Text display
# ----------------------------------------------------------------------


def pathPositions(start, actions):
    positions = [start]
    for action in actions or []:
        dr, dc = mazeModule.DELTA[action]
        r, c = positions[-1]
        positions.append((r + dr, c + dc))
    return positions


class TextDisplay:
    """
    Prints the maze with the solution path drawn on it.
        *  cells on the returned path
        .  cells that were expanded but are not on the path
    """

    def show(self, maze, problem, actions, statsLines):
        grid = [list(row) for row in maze.grid]
        keep = (mazeModule.START, mazeModule.EXIT, mazeModule.KEY)
        for (r, c) in set(problem.expandedPositions()):
            if grid[r][c] == ' ':
                grid[r][c] = '.'
        for (r, c) in pathPositions(maze.start, actions)[1:]:
            if grid[r][c] not in keep and not maze.isWall((r, c)):
                grid[r][c] = '*'
        print()
        print(maze.title)
        print('\n'.join(''.join(row) for row in grid))
        print("Legend: * path   . expanded   ~ ivy (3)   G Griever (10)   K code piece")
        for line in statsLines:
            print(line)


# ----------------------------------------------------------------------
# Graphical display
# ----------------------------------------------------------------------
COLORS = {
    mazeModule.WALL: '#34403a',
    ' ': '#ece2c6',
    '.': '#ece2c6',
    mazeModule.START: '#3fa34d',
    mazeModule.EXIT: '#e0a526',
    mazeModule.KEY: '#ece2c6',
    mazeModule.IVY: '#86b35f',
    mazeModule.GRIEVER: '#8e2c38',
}
HEAT_EARLY = '#ffe08a'
HEAT_LATE = '#e4572e'
RUNNER = '#1d5f9e'
TRAIL = '#2b7bc4'
KEY_COLOR = '#2f7fd8'
BACKGROUND = '#1f2622'


def _hex(color):
    color = color.lstrip('#')
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def _blend(c1, c2, t):
    a, b = _hex(c1), _hex(c2)
    return '#%02x%02x%02x' % tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


class TkDisplay:
    def __init__(self, zoom=1.0, frameTime=None):
        self.zoom = zoom
        self.frameTime = frameTime   # seconds per runner step (None = auto)

    def show(self, maze, problem, actions, statsLines):
        import tkinter as tk

        self.tk = tk
        self.maze = maze
        root = tk.Tk()
        root.title("Maze Runner - " + maze.title)
        root.configure(bg=BACKGROUND)
        self.root = root

        size = int(max(6, min(36, 900 / max(maze.width, maze.height * 1.4))) * self.zoom)
        self.size = size
        pad = 10
        self.pad = pad
        canvas = tk.Canvas(root, width=maze.width * size + 2 * pad,
                           height=maze.height * size + 2 * pad,
                           bg=BACKGROUND, highlightthickness=0)
        canvas.pack(padx=6, pady=(6, 0))
        self.canvas = canvas

        status = tk.Label(root, text='\n'.join(statsLines), justify='left',
                          font=('Menlo', 11), fg='#e8e8e8', bg=BACKGROUND, anchor='w')
        status.pack(fill='x', padx=12, pady=6)
        hint = tk.Label(root, text="Space: skip animation    Q / Esc: close",
                        font=('Helvetica', 10), fg='#9aa59e', bg=BACKGROUND)
        hint.pack(pady=(0, 6))

        self.cells = {}
        self.keyItems = {}
        self._drawMaze()

        self.expanded = []
        seen = set()
        for pos in problem.expandedPositions():
            if pos not in seen:
                seen.add(pos)
                self.expanded.append(pos)
        self.path = pathPositions(maze.start, actions)
        self.skip = False
        root.bind('<space>', lambda e: setattr(self, 'skip', True))
        root.bind('<Escape>', lambda e: root.destroy())
        root.bind('q', lambda e: root.destroy())

        self.expandIndex = 0
        n = len(self.expanded)
        self.batch = max(1, n // 150)
        root.after(300, self._animateExpansion)
        root.mainloop()

    # ------------------------------------------------------------------
    def _box(self, pos, inset=0):
        r, c = pos
        s, p = self.size, self.pad
        return (p + c * s + inset, p + r * s + inset,
                p + (c + 1) * s - inset, p + (r + 1) * s - inset)

    def _drawMaze(self):
        cv, m = self.canvas, self.maze
        for r in range(m.height):
            for c in range(m.width):
                ch = m.grid[r][c]
                item = cv.create_rectangle(*self._box((r, c)), fill=COLORS[ch],
                                           outline=COLORS[ch])
                self.cells[(r, c)] = item
                if ch == mazeModule.WALL and self.size >= 10:
                    # a little texture: ivy on the stone
                    x0, y0, x1, y1 = self._box((r, c), self.size // 3)
                    if (r * 7 + c * 3) % 5 == 0:
                        cv.create_oval(x0, y0, x1, y1, fill='#46594a', outline='')
        font = ('Helvetica', max(7, int(self.size * 0.55)), 'bold')
        for pos, label in ((m.start, 'S'), (m.exit, 'E')):
            x0, y0, x1, y1 = self._box(pos)
            cv.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, fill='white', font=font)
        for pos in m.keys:
            x0, y0, x1, y1 = self._box(pos, max(2, self.size // 5))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            self.keyItems[pos] = cv.create_polygon(cx, y0, x1, cy, cx, y1, x0, cy,
                                                   fill=KEY_COLOR, outline='white')
        for pos in m.openCells():
            ch = m.terrain(pos)
            if ch == mazeModule.GRIEVER and self.size >= 12:
                x0, y0, x1, y1 = self._box(pos, self.size // 3)
                cv.create_line(x0, y0, x1, y1, fill='#c4505e', width=2)
                cv.create_line(x0, y1, x1, y0, fill='#c4505e', width=2)

    def _animateExpansion(self):
        n = len(self.expanded)
        end = n if self.skip else min(n, self.expandIndex + self.batch)
        for i in range(self.expandIndex, end):
            pos = self.expanded[i]
            base = COLORS[self.maze.terrain(pos)]
            heat = _blend(HEAT_EARLY, HEAT_LATE, i / max(1, n - 1))
            color = _blend(base, heat, 0.7)
            self.canvas.itemconfig(self.cells[pos], fill=color, outline=color)
        self.expandIndex = end
        if end < n:
            self.root.after(16, self._animateExpansion)
        else:
            self.skip = False
            self.stepIndex = 0
            self._drawTrail()
            steps = max(1, len(self.path) - 1)
            ft = self.frameTime if self.frameTime is not None else min(0.08, 6.0 / steps)
            self.stepMs = max(1, int(ft * 1000))
            x0, y0, x1, y1 = self._box(self.path[0], max(1, self.size // 6))
            self.runner = self.canvas.create_oval(x0, y0, x1, y1, fill=RUNNER, outline='white', width=2)
            self.root.after(250, self._animateRunner)

    def _drawTrail(self):
        if len(self.path) < 2:
            return
        pts = []
        for pos in self.path:
            x0, y0, x1, y1 = self._box(pos)
            pts.extend([(x0 + x1) / 2, (y0 + y1) / 2])
        self.canvas.create_line(*pts, fill=TRAIL, width=max(2, self.size // 5),
                                capstyle='round', joinstyle='round', dash=(4, 3))

    def _animateRunner(self):
        if self.skip:
            self.stepIndex = len(self.path) - 1
        else:
            self.stepIndex += 1
        if self.stepIndex >= len(self.path):
            return
        pos = self.path[self.stepIndex]
        if self.skip:
            for p in self.path:
                self._pickUp(p)
        self._pickUp(pos)
        x0, y0, x1, y1 = self._box(pos, max(1, self.size // 6))
        self.canvas.coords(self.runner, x0, y0, x1, y1)
        self.canvas.tag_raise(self.runner)
        if self.stepIndex < len(self.path) - 1:
            self.root.after(self.stepMs, self._animateRunner)

    def _pickUp(self, pos):
        item = self.keyItems.pop(pos, None)
        if item is not None:
            self.canvas.itemconfig(item, fill='#b9c9dc', outline='#8899aa')
