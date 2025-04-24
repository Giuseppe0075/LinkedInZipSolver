# MatrixExtractorScraping.py
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Node:
    def __init__(self, value: int, b_u: bool, b_d: bool, b_l: bool, b_r: bool):
        self.value = value
        self.b_u = b_u
        self.b_d = b_d
        self.b_l = b_l
        self.b_r = b_r
        self.visited = False

    def __str__(self):
        return str(self.value)


def extract_matrix_fast():
    """
    Starts a Chrome WebDriver instance and navigates to the LinkedIn Zip game, extracts the game matrix,
    """
    # Uncomment the following lines to use a specific user profile
    # user_profile_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
    options = webdriver.ChromeOptions()

    # options.add_argument(f"--user-data-dir={user_profile_path}")
    # options.add_argument("--profile-directory=Default")
    driver = webdriver.Chrome(options=options)
    # Go to LinkedIn Zip game
    driver.get("https://www.linkedin.com/games/zip")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.maximize_window()
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe)
    # Wait for the game to load
    print("Waiting for game...")
    wait = WebDriverWait(driver, 20)
    button = wait.until(
        EC.element_to_be_clickable((By.ID, "launch-footer-start-button"))
    )

    print("Pressing 'Start Game'...")
    button.click()

    # Wait for the grid to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".trail-cell"))
    )

    # Extract data from the grid
    cells_info = driver.execute_script("""
        return Array.from(document.querySelectorAll(".trail-cell")).map(cell => {
            const cls = cell.className;
            const txt = cell.querySelector(".trail-cell-content");
            return {
                val:  txt ? parseInt(txt.textContent.trim()) || 0 : 0,
                b_u:  /border-top/.test(cls),
                b_d:  /border-bottom/.test(cls),
                b_l:  /border-left/.test(cls),
                b_r:  /border-right/.test(cls)
            };
        });
    """)

    # Recreate the matrix
    n = int(len(cells_info) ** 0.5)
    matrix = []
    start_i = start_j = 0
    for i in range(n):
        row = []
        for j in range(n):
            cell = cells_info[i * n + j]
            if cell["val"] == 1:
                start_i, start_j = i, j
            row.append(Node(cell["val"], cell["b_u"], cell["b_d"], cell["b_l"], cell["b_r"]))
        matrix.append(row)

    return driver, matrix, start_i, start_j, n


if __name__ == "__main__":
    driver, matrix, start_i, start_j, n = extract_matrix_fast()
    print([[node.value for node in row] for row in matrix])
    input("Press Enter to close the browser...")
    driver.quit()
