"""

Old version, used to get the matrix using a screenshot and OCR.

"""

import os
import cv2
import numpy as np
import pyautogui
from typing import Tuple, List

try:
    import pytesseract
except ImportError:
    pytesseract = None  # OCR opzionale

# --------------------------------------------------
# utility
# --------------------------------------------------

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

# --------------------------------------------------
# estrazione celle e coordinate
# --------------------------------------------------
def _line_centers(binary: np.ndarray, axis: int) -> List[int]:
    """Restituisce la lista ordinata dei centri delle linee (verticali o orizzontali).
    Algoritmo in 3 step:
      1. Profila la somma di pixel bianchi per colonna/riga e fissa una soglia relativa (50 % del picco).
      2. Raggruppa gli indici consecutivi sopra soglia → cluster iniziali.
      3. Unisce i centri *troppo vicini* (dist < 0.3·mediana) per evitare splitting dovuto a linee molto spesse.
    """
    profile = binary.sum(axis=axis)
    thresh = profile.max() * 0.5
    mask = profile > thresh

    # cluster iniziali
    clusters = []
    run_start = None
    for idx, val in enumerate(mask):
        if val and run_start is None:
            run_start = idx
        if not val and run_start is not None:
            clusters.append((run_start, idx - 1))
            run_start = None
    if run_start is not None:
        clusters.append((run_start, len(mask) - 1))

    centers = [(s + e) // 2 for s, e in clusters]
    centers.sort()

    # -----------------------------
    # MERGE centri troppo vicini
    # -----------------------------
    if len(centers) > 2:
        dists = np.diff(centers)
        median_d = np.median(dists)
        merged = [centers[0]]
        for c in centers[1:]:
            if c - merged[-1] < 0.3 * median_d:  # troppo vicino ⇒ fuse
                merged[-1] = (merged[-1] + c) // 2
            else:
                merged.append(c)
        centers = merged

    return centers

# --------------------------------------------------
# estrazione celle e coordinate
# --------------------------------------------------

def get_matrix(save_cells_dir: str = "cells", debug: bool = True):
    """Rileva la board, divide in celle e salva le ROI. Ritorna list[list[np.ndarray]]."""
    # 1) screenshot intero
    screen = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    # 2) trova board
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        raise RuntimeError("Board non trovata")
    x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
    board = img[y : y + h, x : x + w].copy()

    if debug:
        dbg = img.copy()
        cv2.rectangle(dbg, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Board", dbg)
        cv2.waitKey(200)

    # 3) binarizza per trovare linee
    gray_b = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(gray_b, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 2)

    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(1, h // 30)))
    vert = cv2.dilate(cv2.erode(bw, v_kernel, 1), v_kernel, 2)
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(1, w // 30), 1))
    hor = cv2.dilate(cv2.erode(bw, h_kernel, 1), h_kernel, 2)

    xs = _line_centers(vert, axis=0)
    ys = _line_centers(hor, axis=1)

    if len(xs) < 2 or len(ys) < 2:
        raise RuntimeError("Non riesco a determinare la griglia: linee insufficienti")

    n_cols, n_rows = len(xs) - 1, len(ys) - 1
    if debug:
        print(f"Grid rilevata: {n_rows}x{n_cols}")

    # margine per scartare la linea (10 % spaziatura media)
    marg_x = int(np.median(np.diff(xs)) * 0.04)
    marg_y = int(np.median(np.diff(ys)) * 0.04)

    _ensure_dir(save_cells_dir)
    cells: List[List[np.ndarray]] = []
    for i in range(n_rows):
        row: List[np.ndarray] = []
        for j in range(n_cols):
            x1, x2 = xs[j] + marg_x, xs[j + 1] - marg_x
            y1, y2 = ys[i] + marg_y, ys[i + 1] - marg_y
            roi = board[y1:y2, x1:x2]
            cv2.imwrite(f"{save_cells_dir}/cell_{i}_{j}.png", roi)
            if debug:
                cv2.rectangle(board, (x1, y1), (x2, y2), (255, 0, 0), 1)
            row.append(roi)
        cells.append(row)

    # salva coord cella (0,0) in coordinate schermo
    global _top_left_screen
    _top_left_screen = (x + xs[0] + marg_x, y + ys[0] + marg_y)

    if debug:
        cv2.imshow("Cells", board)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return cells

# --------------------------------------------------
# OCR + walls
# --------------------------------------------------

def detect_cell_value(roi, debug=False, cell_id: Tuple[int, int] | None = None):
    if roi is None or roi.size == 0 or pytesseract is None:
        return 0
    h, w = roi.shape[:2]
    r = int(min(h, w) * 0.6 / 2)
    cx, cy = w // 2, h // 2
    mask = np.zeros((h, w), np.uint8)
    cv2.circle(mask, (cx, cy), r, 255, -1)
    mask = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    center = cv2.bitwise_and(gray, gray, mask=mask)
    if center.mean() > 200:
        return 0
    _, thresh = cv2.threshold(center, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if debug and cell_id is not None:
        _ensure_dir("debug_cells")
        cv2.imwrite(f"debug_cells/cell_{cell_id[0]}_{cell_id[1]}_th.png", thresh)
    txt = pytesseract.image_to_string(thresh, config="--psm 10 -c tessedit_char_whitelist=0123456789").strip()
    return int(txt) if txt.isdigit() else 0


def detect_cell_walls(roi, wall_thresh=0.5):
    if roi is None or roi.size == 0:
        return False, False, False, False
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    h, w = bw.shape
    sh, sw = max(1, h // 10), max(1, w // 10)
    def wall(section):
        return cv2.countNonZero(section) / section.size > wall_thresh
    return (
        wall(bw[:sh, :]),
        wall(bw[h - sh :, :]),
        wall(bw[:, :sw]),
        wall(bw[:, w - sw :]),
    )


def analyze_cells(cells, debug=False):
    n = len(cells)
    values = [[0] * n for _ in range(n)]
    walls = [[(False, False, False, False) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            values[i][j] = detect_cell_value(cells[i][j], debug, (i, j))
            walls[i][j] = detect_cell_walls(cells[i][j])
    return values, walls
