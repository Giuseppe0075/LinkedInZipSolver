import time
import pyautogui
from MatrixExtractorScraping import extract_matrix_fast

class LinkedInZipSolver:
    def __init__(self):
        print("Starting LinkedIn Zip Solver...")
        # Estrai driver e matrice con il metodo veloce
        self.driver, self.grid, self.start_i, self.start_j, self.n = extract_matrix_fast()

        self.path = []
        self.to_visit = set((i, j) for i in range(self.n) for j in range(self.n))
        print("Grid:", [self.grid[i][j].value for i in range(self.n) for j in range(self.n)])

    def solve(self, i, j, to_find=1):
        if not self.to_visit:
            return False
        if i < 0 or i >= self.n or j < 0 or j >= self.n:
            return False
        if self.grid[i][j].value not in (to_find, 0):
            return False
        if self.grid[i][j].visited:
            return True
        self.grid[i][j].visited = True
        self.to_visit.remove((i, j))
        if self.grid[i][j].value == to_find:
            if not self.to_visit:
                return True
            to_find += 1
        if not self.grid[i][j].b_u and self.solve(i - 1, j, to_find) and not self.to_visit:
            self.path.insert(0, "up")
            return True
        if not self.grid[i][j].b_d and self.solve(i + 1, j, to_find) and not self.to_visit:
            self.path.insert(0, "down")
            return True
        if not self.grid[i][j].b_l and self.solve(i, j - 1, to_find) and not self.to_visit:
            self.path.insert(0, "left")
            return True
        if not self.grid[i][j].b_r and self.solve(i, j + 1, to_find) and not self.to_visit:
            self.path.insert(0, "right")
            return True
        self.grid[i][j].visited = False
        if self.path:
            self.path.pop(0)
        self.to_visit.add((i, j))
        return False

    def solve_puzzle(self):
        # Porta il browser in primo piano
        self.driver.switch_to.window(self.driver.current_window_handle)
        time.sleep(1)
        for arrow in self.path:
            pyautogui.press(arrow)

if __name__ == "__main__":
    solver = LinkedInZipSolver()
    print("Starting to solve...")
    solver.solve(solver.start_i, solver.start_j)
    solver.solve_puzzle()
    print("Path:", solver.path)
    time.sleep(3)
    solver.driver.quit()