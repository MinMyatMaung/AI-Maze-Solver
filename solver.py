from collections import deque
import heapq

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]



def get_neighbors(maze, r, c):
    rows, cols = len(maze), len(maze[0])
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
            yield nr, nc


def reconstruct_path(parent, start, end):
    path = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = parent.get(cur)
        if cur is None:
            return []
    path.append(start)
    path.reverse()
    return path


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])



def bfs(maze, start, end):
    queue = deque([start])
    visited = set([start])
    parent = {}
    explored = []

    while queue:
        node = queue.popleft()
        explored.append(node)

        if node == end:
            return reconstruct_path(parent, start, end), explored

        for neighbor in get_neighbors(maze, *node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                queue.append(neighbor)

    return [], explored



def dfs(maze, start, end):
    stack = [start]
    visited = set([start])
    parent = {}
    explored = []

    while stack:
        node = stack.pop()
        explored.append(node)

        if node == end:
            return reconstruct_path(parent, start, end), explored

        for neighbor in get_neighbors(maze, *node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                stack.append(neighbor)

    return [], explored



def astar(maze, start, end, weight=1.0):
    open_set = []
    heapq.heappush(open_set, (0, start))

    g_cost = {start: 0}
    parent = {}
    explored = []
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)
        explored.append(current)

        if current == end:
            return reconstruct_path(parent, start, end), explored

        for neighbor in get_neighbors(maze, *current):
            tentative_g = g_cost[current] + 1

            if neighbor not in g_cost or tentative_g < g_cost[neighbor]:
                g_cost[neighbor] = tentative_g
                h = manhattan(neighbor, end)
                f = tentative_g + weight * h
                heapq.heappush(open_set, (f, neighbor))
                parent[neighbor] = current

    return [], explored



def solve(maze, algorithm, weight=1.5):
    start = (1, 1)
    end = (len(maze) - 2, len(maze[0]) - 2)

    if algorithm == "BFS":
        path, explored = bfs(maze, start, end)

    elif algorithm == "DFS":
        path, explored = dfs(maze, start, end)

    elif algorithm == "A* (Manhattan)":
        path, explored = astar(maze, start, end, weight=1.0)

    elif algorithm == "Weighted A*":
        path, explored = astar(maze, start, end, weight=weight)

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    stats = {}  
    return path, explored, stats
