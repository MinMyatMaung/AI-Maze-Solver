AI Maze Solver – CPSC 481 Project

This project is an AI-based maze solver that uses different search algorithms to find a path from a start point to a goal in a randomly generated maze. The program also visualizes how each algorithm explores the maze.

Files in this project:

* main.py
  This is the entry point of the program. Running this file will start the application.

* gui.py
  Handles the graphical user interface using tkinter. This includes drawing the maze, handling user input (buttons, dropdowns), animating the search process, and displaying performance stats.

* maze_generator.py
  Generates a random maze using a recursive backtracking algorithm. It returns the maze grid along with the start and end positions.

* solver.py
  Contains the backend logic for solving the maze. It implements BFS, DFS, A* (with Manhattan distance), and Weighted A*. It also tracks explored nodes and reconstructs the final path.

How to run:
Run main.py using Python:
python main.py

Once the program opens, you can:

* generate a new maze
* select a search algorithm
* adjust the animation speed
* adjust the heuristic weight for Weighted A*
* visualize how the algorithm explores the maze and finds a solution

Notes:

* No external datasets were used. Mazes are generated programmatically.
* Standard Python libraries such as tkinter, collections, and heapq were used.
* All search algorithms were implemented from scratch.
