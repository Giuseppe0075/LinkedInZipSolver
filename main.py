import time
import pyautogui
from MatrixExtractorScraping import extract_matrix_fast

class LinkedInZipSolver:
    def __init__(self):
        # Extract the matrix and initialize the driver
        self.driver, self.grid, self.start_i, self.start_j, self.n = extract_matrix_fast()

        # This is the final path to be taken
        self.path = []

        # Set of cells to visit
        self.to_visit = set((i, j) for i in range(self.n) for j in range(self.n))

    def solve(self, i, j, to_find=1):
        # If no cells left to visit, return
        if not self.to_visit:
            return False

        # Check if the current cell is inside the matrix
        if i < 0 or i >= self.n or j < 0 or j >= self.n:
            return False

        # Check if the current cell is a number higher than the one we are looking for
        if self.grid[i][j].value not in (to_find, 0):
            return False

        # Check if the current cell is already visited
        if self.grid[i][j].visited:
            return False

        # Mark the current cell as visited
        self.grid[i][j].visited = True

        # Remove the current cell from the set of cells to visit
        self.to_visit.remove((i, j))

        # If the current cell is the one we are looking for, check if we need to visit more cells
        # If no more cells to visit, we are in the last number and we can return True
        if self.grid[i][j].value == to_find:
            if not self.to_visit:
                return True
            to_find += 1

        # Try to move in all four directions if possible
        if not self.grid[i][j].b_u and self.solve(i - 1, j, to_find):
            self.path.insert(0, "up")
            return True
        if not self.grid[i][j].b_d and self.solve(i + 1, j, to_find):
            self.path.insert(0, "down")
            return True
        if not self.grid[i][j].b_l and self.solve(i, j - 1, to_find):
            self.path.insert(0, "left")
            return True
        if not self.grid[i][j].b_r and self.solve(i, j + 1, to_find):
            self.path.insert(0, "right")
            return True

        # Backtrack (we are in a dead end)
        self.grid[i][j].visited = False
        if self.path:
            self.path.pop(0)
        self.to_visit.add((i, j))
        return False

    def solve_puzzle(self):
        # Click arrows to solve the puzzle
        self.driver.switch_to.window(self.driver.current_window_handle)
        pyautogui.press(self.path, interval=0.1, presses=1)

if __name__ == "__main__":
    solver = LinkedInZipSolver()
    print("Starting to solve...")
    solver.solve(solver.start_i, solver.start_j)
    solver.solve_puzzle()
    print("Path:", solver.path)
    solver.driver.implicitly_wait(5)
    solver.driver.quit()