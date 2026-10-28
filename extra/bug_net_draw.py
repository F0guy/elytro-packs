"""Draw the bug net sprite (32x32) and an enlarged preview on a dark checker."""
import math, sys
from PIL import Image

out = sys.argv[1]
N = 32
img = Image.new('RGBA', (N, N), (0, 0, 0, 0))
px = img.load()

WOOD = (150, 104, 56, 255)
WOOD_LT = (198, 150, 92, 255)
WOOD_DK = (88, 56, 28, 255)
GRIP = (60, 38, 30, 255)
GRIP_LT = (110, 74, 54, 255)
BAND = (176, 60, 52, 255)
RING = (226, 228, 236, 255)
RING_MID = (168, 170, 184, 255)
RING_DK = (108, 110, 126, 255)
NET = (240, 244, 236, 255)
NET_DK = (196, 204, 196, 255)
NET_SH = (160, 170, 164, 255)

cx, cy, r = 21.0, 10.0, 7.0          # hoop centre / radius (pixel centres)


def put(x, y, c):
    if 0 <= x < N and 0 <= y < N:
        px[x, y] = c


def ring_dist(x, y):
    return math.hypot(x - cx, y - cy)


def in_hoop(x, y):
    return ring_dist(x, y) < r - 0.5


def in_bag(x, y):
    # an egg shape hanging off the hoop's lower-right edge, drooping along the diagonal
    bx, by = cx + 2.4, cy + 6.0
    dx, dy = x - bx, y - by
    u = (dx * 0.94 + dy * 0.34)
    v = (dx * -0.34 + dy * 0.94)
    return (u / 5.6) ** 2 + (v / 7.4) ** 2 < 1.0


# --- net mesh: diamond grid, open holes ---
for y in range(N):
    for x in range(N):
        hoop, bag = in_hoop(x, y), in_bag(x, y) and not in_hoop(x, y) and ring_dist(x, y) > r
        if not (hoop or bag):
            continue
        if x % 3 == 0 or y % 3 == 1:
            put(x, y, NET if hoop else NET_DK)

# bag outline (the netting's edge)
for y in range(N):
    for x in range(N):
        if in_bag(x, y) and ring_dist(x, y) > r + 0.5:
            if any(not in_bag(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                put(x, y, NET_SH)

# --- hoop ring: one clean pixel loop, lit from the top left ---
for y in range(N):
    for x in range(N):
        d = ring_dist(x, y)
        if abs(d - r) <= 0.5:
            ang = math.atan2(y - cy, x - cx)
            light = math.cos(ang - math.radians(-135))
            put(x, y, RING if light > 0.3 else RING_MID if light > -0.4 else RING_DK)

# --- handle: from the bottom-left corner up to the hoop ---
x0, y0 = 2, 29
hx, hy = round(cx - r * 0.707), round(cy + r * 0.707)
steps = hx - x0
for i in range(steps):
    x, y = x0 + i, y0 - i
    grip = i <= 5
    band = i == 6
    hi, mid = (GRIP_LT, GRIP) if grip else (BAND, BAND) if band else (WOOD_LT, WOOD)
    put(x, y, hi)
    put(x + 1, y, mid)
    put(x, y + 1, mid)
    put(x + 1, y + 1, WOOD_DK if not grip else GRIP)
# butt cap
for dx, dy in ((-1, 1), (0, 1), (-1, 0), (0, 2), (1, 2)):
    put(x0 + dx, y0 + dy, GRIP)
# metal ferrule where the handle meets the hoop
for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 1), (0, -1)):
    put(hx + dx - 1, hy + dy + 1, RING_DK)
put(hx - 1, hy, RING_MID)

img.save(out)
big = img.resize((N * 16, N * 16), Image.NEAREST)
bg = Image.new('RGBA', big.size)
for y in range(N):
    for x in range(N):
        c = (58, 62, 70, 255) if (x + y) % 2 else (48, 52, 60, 255)
        bg.paste(c, (x * 16, y * 16, x * 16 + 16, y * 16 + 16))
bg.alpha_composite(big)
bg.save(out.replace('.png', '_preview.png'))
print('saved', out)
