import pyautogui


class Node:
    def __init__(self, value, b_u, b_d, b_l, b_r):
        self.value = value
        self.b_u = b_u
        self.b_d = b_d
        self.b_l = b_l
        self.b_r = b_r
        self.visited = False

    def __str__(self):
        return str(self.value)

class LinkedInZipSolver:
    def __init__(self):
        from MatrixInput import get_matrix, analyze_cells

        self.path = []
        self.start_i, self.start_j = 0, 0
        self.grid = []
        cells = get_matrix(debug=True)
        values, walls = analyze_cells(cells, debug=True)
        self.n = len(cells)
        for i in range(len(cells)):
            row = []
            for j in range(len(cells)):
                v = int(values[i][j])
                if v == 1:
                    self.start_i, self.start_j = i, j
                b_u, b_d, b_l, b_r = walls[i][j]
                node = Node(v, b_u, b_d, b_l, b_r)
                row.append(node)
            self.grid.append(row)

        self.to_visit = set([(i,j) for i in range(self.n) for j in range(self.n)])
        print([self.grid[i][j].value for i in range(self.n) for j in range(self.n)])

    def solve(self, i, j, to_find = 1):
        if not bool(self.to_visit):
            return False
        if i < 0 or i >= self.n or j < 0 or j >= self.n:
            return False
        if self.grid[i][j].value != to_find and self.grid[i][j].value != 0:
            return False
        if self.grid[i][j].visited:
            return True
        self.grid[i][j].visited = True
        self.to_visit.remove((i, j))
        if self.grid[i][j].value == to_find:
            if not bool(self.to_visit):
                return True
            to_find += 1
        if not self.grid[i][j].b_u:
            if self.solve(i - 1, j, to_find) and not bool(self.to_visit):
                self.path.insert(0,"up")
                return True
        if not self.grid[i][j].b_d :
            if self.solve(i + 1, j, to_find) and not bool(self.to_visit):
                self.path.insert(0,"down")
                return True
        if not self.grid[i][j].b_l:
            if self.solve(i, j - 1, to_find) and not bool(self.to_visit):
                self.path.insert(0,"left")
                return True
        if not self.grid[i][j].b_r:
            if self.solve(i, j + 1, to_find) and not bool(self.to_visit):
                self.path.insert(0,"right")
                return True
        self.grid[i][j].visited = False
        self.path = self.path[1:]
        self.to_visit.add((i, j))
        return False

    def solve_puzzle(self):
        for arrow in self.path:
            pyautogui.keyDown(arrow)


if __name__ == "__main__":

    solver = LinkedInZipSolver()
    solver.solve(solver.start_i, solver.start_j)
    solver.solve_puzzle()
    print(solver.path)