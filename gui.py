import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from maze_generator import generate_maze

#  Backend interface

try:
    from solver import solve
except ImportError:
    def solve(maze, algorithm, weight=1.5):
        raise NotImplementedError("Backend solver not connected yet.")


#  Constants

CELL_SIZE      = 20
WALL_COLOR     = "#1e1e2e"
PATH_COLOR     = "#cdd6f4"
START_COLOR    = "#a6e3a1"
END_COLOR      = "#f38ba8"
EXPLORE_COLOR  = "#89b4fa"
SOLUTION_COLOR = "#fab387"
GRID_LINE      = "#313244"

ALGORITHMS = ["BFS", "DFS", "A* (Manhattan)", "Weighted A*"]
SPEEDS     = {"Slow": 80, "Medium": 35, "Fast": 10, "Instant": 0}


#  MazeCanvas

class MazeCanvas(tk.Canvas):
    """Draws the maze grid and animates the search."""

    def __init__(self, parent, rows: int, cols: int, **kwargs):
        width  = cols * CELL_SIZE + 1
        height = rows * CELL_SIZE + 1
        super().__init__(parent, width=width, height=height,
                         bg=WALL_COLOR, highlightthickness=0, **kwargs)
        self.rows = rows
        self.cols = cols
        self._cell_ids: dict[tuple[int, int], int] = {}

    def draw_maze(self, maze: list[list[int]],
                  start: tuple[int, int], end: tuple[int, int]) -> None:
        self.delete("all")
        self._cell_ids.clear()
        self.rows = len(maze)
        self.cols = len(maze[0])
        self._resize(self.rows, self.cols)
        for r, row in enumerate(maze):
            for c, cell in enumerate(row):
                color = PATH_COLOR if cell == 0 else WALL_COLOR
                if (r, c) == start:
                    color = START_COLOR
                elif (r, c) == end:
                    color = END_COLOR
                self._cell_ids[(r, c)] = self._draw_cell(r, c, color)

    def color_cell(self, row: int, col: int, color: str) -> None:
        cid = self._cell_ids.get((row, col))
        if cid:
            self.itemconfig(cid, fill=color)

    def _resize(self, rows: int, cols: int) -> None:
        self.config(width=cols * CELL_SIZE + 1,
                    height=rows * CELL_SIZE + 1)

    def _draw_cell(self, row: int, col: int, color: str) -> int:
        x1 = col * CELL_SIZE + 1
        y1 = row * CELL_SIZE + 1
        x2 = x1 + CELL_SIZE - 1
        y2 = y1 + CELL_SIZE - 1
        return self.create_rectangle(x1, y1, x2, y2,
                                     fill=color, outline=GRID_LINE, width=1)


#  StatsPanel

class StatsPanel(tk.Frame):
    """Displays algorithm performance metrics."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._labels: dict[str, tk.StringVar] = {}
        fields = [
            ("Algorithm",      "algorithm"),
            ("Time (ms)",      "time_ms"),
            ("Nodes Explored", "nodes"),
            ("Path Length",    "path_len"),
            ("Optimal",        "optimal"),
            ("Status",         "status"),
        ]
        for i, (label, key) in enumerate(fields):
            tk.Label(self, text=label + ":", anchor="w",
                     width=16).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            var = tk.StringVar(value="—")
            self._labels[key] = var
            tk.Label(self, textvariable=var, anchor="w",
                     width=14).grid(row=i, column=1, sticky="w")

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in self._labels:
                self._labels[key].set(str(value))

    def reset(self) -> None:
        for var in self._labels.values():
            var.set("—")


#  App

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Maze Solver — CPSC 481")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self._maze:  list[list[int]] | None = None
        self._start: tuple[int, int] = (1, 1)
        self._end:   tuple[int, int] = (1, 1)
        self._solving = False

        self._build_ui()
        self._new_maze()

    def _build_ui(self) -> None:
        # ── left: canvas ──
        canvas_frame = tk.Frame(self, bg="#1e1e2e", padx=10, pady=10)
        canvas_frame.grid(row=0, column=0)
        self.canvas = MazeCanvas(canvas_frame, rows=21, cols=21)
        self.canvas.pack()

        # ── right: controls + stats ──
        side = tk.Frame(self, bg="#1e1e2e", padx=10, pady=10)
        side.grid(row=0, column=1, sticky="n")

        # maze size — rows 0, 1
        tk.Label(side, text="Maze Size", bg="#1e1e2e",
                 fg="#cdd6f4").grid(row=0, column=0, columnspan=2, sticky="w")
        self._size_var = tk.IntVar(value=21)
        tk.Scale(side, from_=11, to=51, resolution=2,
                 orient="horizontal", variable=self._size_var,
                 bg="#1e1e2e", fg="#cdd6f4",
                 troughcolor="#313244", highlightthickness=0,
                 length=160).grid(row=1, column=0, columnspan=2, sticky="ew")

        # algorithm — rows 2, 3
        tk.Label(side, text="Algorithm", bg="#1e1e2e",
                 fg="#cdd6f4").grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self._algo_var = tk.StringVar(value="BFS")
        ttk.Combobox(side, textvariable=self._algo_var,
                     values=ALGORITHMS, state="readonly",
                     width=14).grid(row=3, column=0, columnspan=2, sticky="ew")

        # speed — rows 4, 5
        tk.Label(side, text="Animation Speed", bg="#1e1e2e",
                 fg="#cdd6f4").grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self._speed_var = tk.StringVar(value="Medium")
        ttk.Combobox(side, textvariable=self._speed_var,
                     values=list(SPEEDS.keys()), state="readonly",
                     width=14).grid(row=5, column=0, columnspan=2, sticky="ew")

        # heuristic weight — rows 6, 7
        tk.Label(side, text="Heuristic Weight (w)", bg="#1e1e2e",
                 fg="#cdd6f4").grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self._weight_var = tk.DoubleVar(value=1.5)
        tk.Scale(side, from_=1.0, to=5.0, resolution=0.5,
                 orient="horizontal", variable=self._weight_var,
                 bg="#1e1e2e", fg="#cdd6f4",
                 troughcolor="#313244", highlightthickness=0,
                 length=160).grid(row=7, column=0, columnspan=2, sticky="ew")

        # buttons — rows 8, 9, 10, 11
        btn_cfg = dict(width=12, relief="flat", cursor="hand2",
                       bg="#313244", fg="#000000", activebackground="#45475a",
                       activeforeground="#eaf4cd", pady=6)
        self._gen_btn = tk.Button(side, text="New Maze",
                                  command=self._new_maze, **btn_cfg)
        self._gen_btn.grid(row=8, column=0, columnspan=2, pady=(14, 4), sticky="ew")

        self._solve_btn = tk.Button(side, text="Solve",
                                    command=self._start_solve, **btn_cfg)
        self._solve_btn.grid(row=9, column=0, columnspan=2, pady=4, sticky="ew")

        self._stop_btn = tk.Button(side, text="Stop",
                                   command=self._stop_solve,
                                   state="disabled", **btn_cfg)
        self._stop_btn.grid(row=10, column=0, columnspan=2, pady=4, sticky="ew")

        self._compare_btn = tk.Button(side, text="Compare All",
                                      command=self._compare_all, **btn_cfg)
        self._compare_btn.grid(row=11, column=0, columnspan=2, pady=4, sticky="ew")

        # legend — row 12
        legend_frame = tk.LabelFrame(side, text=" Legend ", bg="#1e1e2e",
                                     fg="#6c7086", labelanchor="n", padx=6, pady=4)
        legend_frame.grid(row=12, column=0, columnspan=2, pady=(12, 4), sticky="ew")
        self._add_legend(legend_frame, START_COLOR,    "Start")
        self._add_legend(legend_frame, END_COLOR,      "End")
        self._add_legend(legend_frame, EXPLORE_COLOR,  "Explored")
        self._add_legend(legend_frame, SOLUTION_COLOR, "Solution")

        # stats — row 13
        stats_frame = tk.LabelFrame(side, text=" Stats ", bg="#1e1e2e",
                                    fg="#6c7086", labelanchor="n", padx=6, pady=4)
        stats_frame.grid(row=13, column=0, columnspan=2, pady=(8, 0), sticky="ew")
        self.stats = StatsPanel(stats_frame, bg="#1e1e2e")
        self.stats.pack()

    @staticmethod
    def _add_legend(parent: tk.Frame, color: str, label: str) -> None:
        row = tk.Frame(parent, bg="#1e1e2e")
        row.pack(anchor="w", pady=1)
        tk.Canvas(row, width=14, height=14, bg=color,
                  highlightthickness=0).pack(side="left", padx=(0, 6))
        tk.Label(row, text=label, bg="#1e1e2e",
                 fg="#cdd6f4", font=("Helvetica", 10)).pack(side="left")

    def _new_maze(self) -> None:
        if self._solving:
            self._stop_solve()
        size = self._size_var.get()
        self._maze, self._start, self._end = generate_maze(size, size)
        self.canvas.draw_maze(self._maze, self._start, self._end)
        self.stats.reset()

    def _start_solve(self) -> None:
        if self._maze is None or self._solving:
            return
        self._solving = True
        self._solve_btn.config(state="disabled")
        self._gen_btn.config(state="disabled")
        self._stop_btn.config(state="normal")
        self.stats.reset()
        self.canvas.draw_maze(self._maze, self._start, self._end)

        algo  = self._algo_var.get()
        delay = SPEEDS[self._speed_var.get()]
        threading.Thread(target=self._run_solve,
                         args=(algo, delay), daemon=True).start()

    def _run_solve(self, algorithm: str, delay_ms: int) -> None:
        try:
            weight = self._weight_var.get()
            t0 = time.perf_counter()
            path, explored, stats = solve(self._maze, algorithm, weight)
            elapsed = (time.perf_counter() - t0) * 1000

            if delay_ms == 0:
                self.after(0, self._paint_instant,
                           explored, path, algorithm, elapsed, stats)
            else:
                self.after(0, self._animate,
                           explored, path, algorithm, elapsed, stats, delay_ms, 0)

        except NotImplementedError:
            self.after(0, messagebox.showwarning,
                       "Backend Missing",
                       "solver.py is not connected yet.\n"
                       "Ask Cristian to wire up solve().")
            self.after(0, self._finish_solve)
        except Exception as exc:
            self.after(0, messagebox.showerror, "Error", str(exc))
            self.after(0, self._finish_solve)

    def _paint_instant(self, explored, path,
                       algorithm, elapsed, stats) -> None:
        for (r, c) in explored:
            if (r, c) not in (self._start, self._end):
                self.canvas.color_cell(r, c, EXPLORE_COLOR)
        for (r, c) in path:
            if (r, c) not in (self._start, self._end):
                self.canvas.color_cell(r, c, SOLUTION_COLOR)
        self._update_stats(algorithm, elapsed, len(explored), len(path), stats)
        self._finish_solve()

    def _animate(self, explored, path,
                 algorithm, elapsed, stats,
                 delay_ms: int, idx: int) -> None:
        if not self._solving:
            return
        if idx < len(explored):
            r, c = explored[idx]
            if (r, c) not in (self._start, self._end):
                self.canvas.color_cell(r, c, EXPLORE_COLOR)
            self.after(delay_ms, self._animate, explored, path,
                       algorithm, elapsed, stats, delay_ms, idx + 1)
        else:
            for (r, c) in path:
                if (r, c) not in (self._start, self._end):
                    self.canvas.color_cell(r, c, SOLUTION_COLOR)
            self._update_stats(algorithm, elapsed,
                               len(explored), len(path), stats)
            self._finish_solve()

    def _stop_solve(self) -> None:
        self._solving = False
        self._finish_solve()

    def _finish_solve(self) -> None:
        self._solving = False
        self._solve_btn.config(state="normal")
        self._gen_btn.config(state="normal")
        self._stop_btn.config(state="disabled")

    def _update_stats(self, algorithm, elapsed,
                      nodes, path_len, extra) -> None:
        found = path_len > 0
        optimal_algos = {"BFS", "A* (Manhattan)"}
        self.stats.update(
            algorithm=algorithm,
            time_ms=f"{elapsed:.2f}",
            nodes=nodes,
            path_len=path_len if found else "N/A",
            optimal="Yes" if algorithm in optimal_algos else "Depends on w",
            status="Found" if found else "No path",
        )

    def _compare_all(self) -> None:
        if self._maze is None:
            return
        results = []
        weight = self._weight_var.get()
        for algo in ALGORITHMS:
            try:
                t0 = time.perf_counter()
                path, explored, _ = solve(self._maze, algo, weight)
                elapsed = (time.perf_counter() - t0) * 1000
                results.append((algo, f"{elapsed:.2f}ms",
                                len(explored), len(path) or "N/A"))
            except NotImplementedError:
                results.append((algo, "N/A", "N/A", "N/A"))

        win = tk.Toplevel(self)
        win.title("Algorithm Comparison")
        win.configure(bg="#1e1e2e")
        headers = ["Algorithm", "Time (ms)", "Nodes Explored", "Path Length"]
        for c, h in enumerate(headers):
            tk.Label(win, text=h, bg="#313244", fg="#cdd6f4",
                     font=("Helvetica", 10, "bold"),
                     padx=10, pady=4).grid(row=0, column=c,
                                           sticky="ew", padx=1, pady=1)
        for r, row in enumerate(results, start=1):
            for c, val in enumerate(row):
                tk.Label(win, text=val, bg="#1e1e2e", fg="#cdd6f4",
                         padx=10, pady=4).grid(row=r, column=c,
                                               sticky="ew", padx=1, pady=1)


# ──────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()