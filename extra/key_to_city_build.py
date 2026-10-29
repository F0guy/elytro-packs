"""Key to the City held sprite (128x128), after nikoc's reference (a gold key-scythe): drawn as
smooth shapes on a 128-unit layout, rendered four times over (512px) and reduced to a 128x128
mask so the curves come out smooth, then shaded in Minecraft's style (lit up-left, shaded
down-right, dark gold outline). Run inventory_icons_build.py after it: that writes the item
definition, the bigger held angles and the inventory icon. Parts: comb bit at the grip end, a shaft with three collar rings, a
figure-eight bow of two rounded loops at the top, and a crescent blade sweeping down."""
import json, math, os
from PIL import Image, ImageDraw

F = 4                     # the layout is in 128 units; it's drawn at 4x (512px) for smooth edges
B, T = 128 * F, 128
big = Image.new('L', (B, B), 0)


class Scaled:
    """ImageDraw on the 128-unit layout, drawn at F times the size."""
    def __init__(self, im):
        self.d = ImageDraw.Draw(im)

    def line(self, pts, fill, width):
        self.d.line([(x * F, y * F) for x, y in pts], fill=fill, width=int(width * F))

    def polygon(self, pts, fill):
        self.d.polygon([(x * F, y * F) for x, y in pts], fill=fill)

    def rounded_rectangle(self, box, radius, outline, width):
        self.d.rounded_rectangle([v * F for v in box], radius=radius * F, outline=outline, width=width * F)


d = Scaled(big)

# shaft
a, b = (17, 113), (70, 44)
d.line([a, b], fill=255, width=8)
u = ((b[0] - a[0]) / math.dist(a, b), (b[1] - a[1]) / math.dist(a, b))     # along the shaft
p = (-u[1], u[0]) if -u[1] > 0 else (u[1], -u[0])                            # across, down-right
p = (abs(p[0]), abs(p[1]))
# collar rings across the shaft
for t in (0.2, 0.47, 0.74):
    c = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    d.line([(c[0] - p[0] * 8, c[1] - p[1] * 8), (c[0] + p[0] * 8, c[1] + p[1] * 8)], fill=255, width=6)
# the bit: a comb flag off the grip end, three prongs (an E)
def at(s, q):
    return (a[0] + u[0] * s + p[0] * q, a[1] + u[1] * s + p[1] * q)
d.polygon([at(-2, 0), at(22, 0), at(22, 20), at(-2, 20)], fill=255)
for s0, s1 in ((3, 8), (12, 17)):
    d.polygon([at(s0, 8), at(s1, 8), at(s1, 21), at(s0, 21)], fill=0)
# the bow: two rounded loops, a figure eight
d.rounded_rectangle([57, 23, 83, 49], radius=7, outline=255, width=6)
d.rounded_rectangle([65, 1, 91, 28], radius=7, outline=255, width=6)


# the blade: a crescent from the top loop sweeping down the right side to a point
def bez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (k / n for k in range(n + 1))]


tip = (104, 112)
outer = bez((84, 4), (124, 20), (122, 62)) + bez((122, 62), (120, 96), tip)[1:]
inner = bez(tip, (108, 70), (98, 42)) + bez((98, 42), (93, 28), (86, 26))[1:]
d.polygon(outer + inner, fill=255)

# turned around in the hand: mirrored across the shaft (the grip-to-tip diagonal), so the
# blade sweeps the other way; shading is worked out after, so the light stays top-left
big = big.transpose(Image.TRANSVERSE)

# reduce to a 128x128 mask
small = big.resize((T, T), Image.BOX)
mask = {(x, y) for x in range(T) for y in range(T) if small.getpixel((x, y)) >= 120}

# shade like a vanilla item: lit where open to the up-left, shaded where open to the
# down-right, a dark gold outline round it
L, M, D = (255, 224, 90), (246, 190, 38), (206, 140, 16)
EDGE = (120, 72, 6)
img = Image.new('RGBA', (T, T), (0, 0, 0, 0))
px = img.load()
HI, LO = (255, 244, 170), (176, 112, 10)
for (x, y) in mask:
    # bands a few pixels deep: brightest right at the lit edge, deepest right at the shaded one
    open_ul = [(x - k, y) not in mask or (x, y - k) not in mask for k in (1, 2, 3, 4)]
    open_dr = [(x + k, y) not in mask or (x, y + k) not in mask for k in (1, 2, 3, 4)]
    c = M
    if open_ul[0] or open_ul[1]:
        c = HI
    elif open_ul[2] or open_ul[3]:
        c = L
    elif open_dr[0] or open_dr[1]:
        c = LO
    elif open_dr[2] or open_dr[3]:
        c = D
    px[x, y] = c + (255,)
# a two-pixel outline (128px is twice the 64px detail)
ring1 = {(x, y) for x in range(T) for y in range(T) if (x, y) not in mask
         and any((x + dx, y + dy) in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
ring2 = {(x, y) for x in range(T) for y in range(T) if (x, y) not in mask and (x, y) not in ring1
         and any((x + dx, y + dy) in ring1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
for (x, y) in ring1 | ring2:
    px[x, y] = EDGE + (255,)

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'elytro')
for sub in ('textures/item', 'models/item', 'items'):
    os.makedirs(os.path.join(A, sub), exist_ok=True)
img.save(os.path.join(A, 'textures/item/key_to_city.png'))
json.dump({'parent': 'minecraft:item/handheld', 'textures': {'layer0': 'elytro:item/key_to_city'}},
          open(os.path.join(A, 'models/item/key_to_city.json'), 'w'), indent=1)
json.dump({'model': {'type': 'minecraft:model', 'model': 'elytro:item/key_to_city'}},
          open(os.path.join(A, 'items/key_to_city.json'), 'w'), indent=1)

print('key to the city: sprite written')
