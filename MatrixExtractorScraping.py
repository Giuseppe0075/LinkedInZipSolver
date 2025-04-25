# MatrixExtractorScraping.py
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


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
    options = webdriver.ChromeOptions()
    # Uncomment the following lines to use a specific user profile
    user_profile_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument(f"--user-data-dir={user_profile_path}")
    options.add_argument("--profile-directory=Default")
    driver = webdriver.Chrome(options=options)
    # Go to LinkedIn Zip game
    driver.get("https://www.linkedin.com/games/zip")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.maximize_window()

    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    driver.execute_script("document.body.click();")

    if len(options.arguments) == 0 :
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
    # Wait for the game to load
    print("Waiting for game...")
    # Dopo essere entrato nell'iframe
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "artdeco-modal"))
    )

    main = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "main"))
    )
    wait = WebDriverWait(main, 20)
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
            const border_top = cell.querySelector(".trail-cell-wall--up");
            const border_down = cell.querySelector(".trail-cell-wall--down");
            const border_left = cell.querySelector(".trail-cell-wall--left");
            const border_right = cell.querySelector(".trail-cell-wall--right");
            return {
                val:  txt ? parseInt(txt.textContent.trim()) || 0 : 0,
                b_u:  border_top ? 1 : 0,
                b_d:  border_down ? 1 : 0,
                b_l:  border_left ? 1 : 0,
                b_r:  border_right ? 1 : 0,
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

    # Adjust walls
    for i in range(n):
        for j in range(n):
            if i > 0 and matrix[i][j].b_u:
                matrix[i-1][j].b_d = True
            if i < n and matrix[i][j].b_d:
                matrix[i+1][j].b_u = True
            if j > 0 and matrix[i][j].b_l:
                matrix[i][j-1].b_r = True
            if j < n and matrix[i][j].b_r:
                matrix[i][j+1].b_l = True

    return driver, matrix, start_i, start_j, n


if __name__ == "__main__":
    driver, matrix, start_i, start_j, n = extract_matrix_fast()
    print([[node.value for node in row] for row in matrix])
    input("Press Enter to close the browser...")
    driver.quit()
