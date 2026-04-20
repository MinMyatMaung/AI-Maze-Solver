import random


def generate_maze(
    rows: int,
    cols: int,
    seed: int | None = None,
) -> tuple[list[list[int]], tuple[int, int], tuple[int, int]]:
    """
    Generate a perfect maze using recursive backtracking.

    Parameters
    ----------
    rows, cols : odd integers ≥ 11

    Returns
    -------
    maze   : 2-D list  (0 = open path, 1 = wall)
    start  : (row, col) — top-left passage cell
    end    : (row, col) — bottom-right passage cell
    """
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1

    rng = random.Random(seed)

    # start fully walled
    maze = [[1] * cols for _ in range(rows)]

    def carve(r: int, c: int) -> None:
        maze[r][c] = 0
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        rng.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and maze[nr][nc] == 1:
                maze[r + dr // 2][c + dc // 2] = 0  # knock down wall
                carve(nr, nc)

    carve(1, 1)

    start = (1, 1)
    end   = (rows - 2, cols - 2)

    return maze, start, end