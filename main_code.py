import numpy as np
import cv2 as cv
from helper_function import arrowdraw
from typing import Tuple, List

# cap = cv.VideoCapture("monkey.avi")

# calculating the grid of blocks, no overlapping, no spillover outside of the dimension
def block_grid_centers(width: int, height: int, k: int) -> List[Tuple[int, int]]:
    block = 2 * k + 1
    xs = list(range(k, width - k, block))
    # print(xs, "boom")
    ys = list(range(k, height - k, block))
    centers = [(x, y) for y in ys for x in xs]
    return centers

print(block_grid_centers(10,10,1))
thing = [0,1,2,3,4]
print(thing[0:3])

def extract_block(frame: np.ndarray, cx: int, cy: int, k: int) -> np.ndarray:
    x0, x1 = cx - k, cx + k + 1
    y0, y1 = cy - k, cy + k + 1
    #(row, col) -> (y, x)
    #frame is a numpy array with shape(height, width, color channel)
    #e.g. frame.shape = (640, 800, 3)
    # ":" below is explicitly telling python to keep that color channel :3
    return frame[y0:y1, x0:x1, :]

#restricting the val if it exceed a certain bound, used to keep the blocks in borders
def clamp(val: int, low: int, high: int) -> int:
    return max(low, min(high, val))

def ssd_calc(b1: np.ndarray, b2: np.ndarray) -> float:
    dif = b1.astype(np.float64) - b2.astype(np.float64)
    summed = np.sum(dif * dif)
    return summed

#matching alg using minimum sum of squared distances
def match_blocks(frame_now: np.ndarray, frame_next: np.ndarray, cx: int, cy: int, k: int, radius: int) -> Tuple[int, int, float]:
    h, w = frame_now.shape[:2]
    best_SSD = float("inf")
    best_x, best_y = cx, cy

    b_source = extract_block(frame_now, cx, cy, k)

    # w - k - 1 because index is from 0 to w - 1
    x_min = clamp(cx - radius, k, w - k - 1)
    x_max = clamp(cx + radius, k, w - k - 1)
    y_min = clamp(cy - radius, k, h - k - 1)
    y_max = clamp(cy + radius, k, h - k - 1)

    #y_max and x_max + 1 because range doesnt take last index, probably could
    #remove the -1 above and the +1 below cause they cancel out but whatever
    for yy in range(y_min, y_max + 1):
        for xx in range(x_min, x_max + 1):
            b_candidate = extract_block(frame_next, xx, yy, k)
            ssd = ssd_calc(b_source, b_candidate)
            if ssd < best_SSD:
                best_SSD = ssd
                best_x, best_y = xx, yy

    return best_x, best_y, best_SSD

def check_T(sqrtssd, tmin, tmax) -> bool:
    return tmin < sqrtssd < tmax

print(":3 AEUOFNAUEG", check_T(8,0,6))

#code below is where we put it all together and run it

cap = cv.VideoCapture("monkey.avi")
ret, prev = cap.read()
cap_h, cap_w = prev.shape[:2]
print("HEIGHT: " ,cap_h,"WIDTH: ", cap_w)

block_centers = block_grid_centers(cap_w, cap_h, 5)

#output
writer = None
fourcc = cv.VideoWriter_fourcc(*"mp4v")
writer = cv.VideoWriter("monkey.mp4", fourcc, cap.get(cv.CAP_PROP_FPS), (cap_w, cap_h))
#output

while True:
    ret, current = cap.read()
    if not ret:
        break

    arrows = []
    for (cx, cy) in block_centers:
        bx, by, best_ssd = match_blocks(prev, current, cx, cy, 5, 6)
        dx = bx - cx
        dy = by - cy
        sqrtssd = np.sqrt(best_ssd)
        arrows.append((cx, cy, dx, dy, sqrtssd))

    for (cx, cy, dx, dy, sqrtssd) in arrows:
        if check_T(sqrtssd, 200, 800):
            # arrowdraw(prev, int(cx), int(cy), int(cx + dx), int(cy + dy))
            # cv.arrowedLine(prev, (int(cx), int(cy)), (int(cx + dx), int(cy + dy)), (0, 255, 0), 2)
            cv.line(prev, (int(cx), int(cy)), (int(cx + dx), int(cy + dy)), (0, 255, 0), 2)
            cv.circle(prev, (int(cx), int(cy)), 1, (0, 0, 255), -1)

    print("moving")
    # cv.imshow('frame', prev)
    # cv.waitKey(0)
    # # cv.destroyAllWindows()

    out_frame = prev.copy()
    writer.write(out_frame)

    prev = current

    