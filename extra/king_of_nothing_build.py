"""King of Nothing - a sword skin (reward for reaching #1 on /baltop).

A royal sword snapped a hand above the guard. Its missing pieces hang in the air above the break,
bobbing, still in the order they broke off, and above them floats a crooked gold crown that slowly
tumbles: it tips over, hangs upside down for a moment, and comes back round, forever.

How it moves (the important part)
  minecraft:time can't drive this: the 'random' source wanders back and forth (fine for Kraken's
  writhing, wrong for a steady turn) and 'daytime' stands still on Elytro (advance_time is false).
  So every crown pose is in the model at once, each pose's faces on its own little patch of an
  ANIMATED texture, and frame f of that texture paints only pose f's patch; every other patch is
  fully transparent and the item shader discards those faces. The texture animation is a client
  clock that never stops, runs the same in every world, and steps once every FRAME_TICKS.
  Interpolation is off on purpose: Minecraft blends colour but takes alpha from the current frame.
  The floating shards work the same way on a second texture with its own, shorter cycle.

  Element rotations are single-axis and limited to +-45 degrees, so a crown element turned by any
  angle is first turned by whole quarter turns (swap its width and height, move its faces round)
  and only the remainder goes into its rotation.

Writes into ./assets/elytro (this folder):
  items/king_of_nothing.json
  models/item/king_of_nothing.json, king_of_nothing_icon.json
  textures/item/king_of_nothing.png, king_of_nothing_crown.png (+ .mcmeta),
  king_of_nothing_shards.png (+ .mcmeta), king_of_nothing_icon.png
Usage (needs Pillow): python king_of_nothing_build.py [--preview DIR]
  --preview also writes preview_static.json, an element list with pose tags and a fully opaque
  copy of each gated texture, for render_kon_blender.py.
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')
NAME = 'king_of_nothing'

CROWN_POSES = 112          # one full tumble = 112 frames x 2 ticks = 11.2 s
CROWN_TICKS = 2
SHARD_POSES = 24           # one bob = 24 x 4 ticks = 4.8 s
SHARD_TICKS = 4

T_STATIC = 'elytro:item/king_of_nothing'
T_CROWN = 'elytro:item/king_of_nothing_crown'
T_SHARDS = 'elytro:item/king_of_nothing_shards'

FACES = ('north', 'south', 'east', 'west', 'up', 'down')

# ---------------------------------------------------------------- palette
GOLD = (232, 182, 72)
GOLD_LIGHT = (255, 226, 140)
GOLD_DARK = (150, 100, 34)
STEEL = (196, 204, 216)
STEEL_LIGHT = (236, 242, 250)
STEEL_DARK = (112, 122, 138)
VELVET = (92, 30, 92)
VELVET_DARK = (52, 14, 56)
RUBY = (206, 30, 58)
RUBY_LIGHT = (255, 110, 130)
CRACK = (34, 30, 40)

# ---------------------------------------------------------------- static texture (8x8 swatches)
SW = {
    'gold': (0, 0), 'gold_dark': (1, 0), 'steel': (2, 0), 'steel_dark': (3, 0),
    'velvet': (4, 0), 'velvet_dark': (5, 0), 'ruby': (6, 0), 'wire': (7, 0),
    'steel_edge': (0, 1), 'crack': (1, 1), 'gold_light': (2, 1),
}


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def static_texture():
    rnd = random.Random(31)
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    px = im.load()

    def fill(name, fn):
        cx, cy = SW[name]
        for y in range(8):
            for x in range(8):
                px[cx * 8 + x, cy * 8 + y] = fn(x, y, rnd.random())

    fill('gold', lambda x, y, n: mix(GOLD, GOLD_LIGHT, (1 - y / 7) * 0.55 + 0.25 * n))
    fill('gold_dark', lambda x, y, n: mix(GOLD_DARK, GOLD, 0.35 * n))
    fill('gold_light', lambda x, y, n: mix(GOLD, GOLD_LIGHT, 0.6 + 0.4 * n))
    # steel: brushed, faint streaks along the blade, a little tarnish
    streak = [rnd.random() for _ in range(8)]
    fill('steel', lambda x, y, n: mix(STEEL, STEEL_LIGHT, 0.25 + 0.45 * streak[x] + 0.1 * n - 0.25 * (y / 7)))
    fill('steel_dark', lambda x, y, n: mix(STEEL_DARK, STEEL, 0.3 * n))
    fill('steel_edge', lambda x, y, n: mix(STEEL, (255, 255, 255), 0.55 + 0.3 * n))
    # velvet grip: a diagonal weave
    fill('velvet', lambda x, y, n: mix(VELVET_DARK, VELVET, 0.9 if (x + y) % 3 else 0.25 + 0.2 * n))
    fill('velvet_dark', lambda x, y, n: mix(VELVET_DARK, VELVET, 0.25 * n))
    fill('wire', lambda x, y, n: mix(GOLD_DARK, GOLD_LIGHT, 0.8 if y % 2 else 0.3))

    def ruby(x, y, n):
        r = math.hypot(x - 2.5, y - 2.5)
        return mix(RUBY_LIGHT, RUBY, r / 4.5) if r < 5 else mix(RUBY, (110, 10, 30), (r - 5) / 4)
    fill('ruby', ruby)
    fill('crack', lambda x, y, n: mix(CRACK, (70, 62, 80), 0.4 * n))
    return im


def uv_static(name):
    cx, cy = SW[name]
    u0, v0 = cx * 2 + 0.2, cy * 2 + 0.2
    return [round(u0, 3), round(v0, 3), round(u0 + 1.6, 3), round(v0 + 1.6, 3)]


# ---------------------------------------------------------------- gated textures
# Each pose owns a 4x6 pixel cell of a 64x64 frame holding 2x2 patches (one per material).
GATED_MATS = {'crown': ('gold', 'gold_dark', 'velvet', 'ruby', 'gold_light'),
              'shards': ('steel', 'steel_edge', 'gold', 'steel_dark')}
GATED_COL = {
    'gold': (GOLD, GOLD_LIGHT), 'gold_light': (GOLD_LIGHT, (255, 246, 200)), 'gold_dark': (GOLD_DARK, GOLD), 'velvet': (VELVET_DARK, VELVET),
    'ruby': (RUBY, RUBY_LIGHT), 'steel': (STEEL, STEEL_LIGHT), 'steel_edge': (STEEL_LIGHT, (255, 255, 255)),
    'steel_dark': (STEEL_DARK, STEEL),
}


def cell_of(pose):
    return (pose % 16) * 4, (pose // 16) * 6          # 4x6 cell: up to six 2x2 patches


def gated_uv(kind, pose, mat):
    k = GATED_MATS[kind].index(mat)
    cx, cy = cell_of(pose)
    px, py = cx + (k % 2) * 2, cy + (k // 2) * 2          # top-left pixel of the 2x2 patch
    u0, v0 = px / 4, py / 4                                # 64 px = 16 units
    return [round(u0 + 0.125, 4), round(v0 + 0.125, 4), round(u0 + 0.375, 4), round(v0 + 0.375, 4)]


def paint_cell(px, kind, pose):
    cx, cy = cell_of(pose)
    for k, mat in enumerate(GATED_MATS[kind]):
        lo, hi = GATED_COL[mat]
        for dy in range(2):
            for dx in range(2):
                px[cx + (k % 2) * 2 + dx, cy + (k // 2) * 2 + dy] = mix(lo, hi, 0.55 if dy == 0 else 0.25)


def gated_texture(kind, poses, opaque=False):
    """Frame f shows only pose f's cell. opaque=True: one frame with every cell painted (preview)."""
    if opaque:
        im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        for p in range(poses):
            paint_cell(im.load(), kind, p)
        return im
    sheet = Image.new('RGBA', (64, 64 * poses), (0, 0, 0, 0))
    for f in range(poses):
        frame = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        paint_cell(frame.load(), kind, f)
        sheet.paste(frame, (0, 64 * f))
    return sheet


# ---------------------------------------------------------------- elements
def rnd3(v):
    return [round(x, 4) for x in v]


def static_box(frm, to, mat, rot=None, light=0, faces_mat=None, name=None):
    faces = {f: {'uv': uv_static((faces_mat or {}).get(f, mat)), 'texture': '#0'} for f in FACES}
    e = {'from': rnd3(frm), 'to': rnd3(to), 'faces': faces}
    if rot:
        e['rotation'] = rot
    if light:
        e['light_emission'] = light
    if name:
        e['name'] = name
    return e


# turning a box by +90 about z (x toward y) moves its faces: east->up->west->down->east
QUARTER = {'east': 'up', 'up': 'west', 'west': 'down', 'down': 'east', 'north': 'north', 'south': 'south'}


def turned_box(centre, local, half, angle, mats, kind, pose, tex, light=0, name=None, spin=0, cull=()):
    """A box whose centre sits at `local` (x, y, z) from `centre`, half sizes `half`, the whole lot
    turned `angle` degrees about z round `centre`. mats: face -> material (key 'all' for the rest).
    spin: extra turn of the box about its own centre (a square stood on its corner, say).
    cull: faces (before turning) that are always hidden inside something else; left out."""
    a = math.radians(angle)
    lx, ly, lz = local
    cx = centre[0] + lx * math.cos(a) - ly * math.sin(a)
    cy = centre[1] + lx * math.sin(a) + ly * math.cos(a)
    cz = centre[2] + lz
    k = round((angle + spin) / 90)
    rest = angle + spin - 90 * k
    hx, hy, hz = half
    if k % 2:
        hx, hy = hy, hx
    face_mat = {f: (None if f in cull else mats.get(f, mats['all'])) for f in FACES}
    for _ in range(k % 4):
        face_mat = {QUARTER[f]: m for f, m in face_mat.items()}
    faces = {f: {'uv': gated_uv(kind, pose, face_mat[f]), 'texture': tex} for f in FACES if face_mat[f]}
    e = {'from': rnd3([cx - hx, cy - hy, cz - hz]), 'to': rnd3([cx + hx, cy + hy, cz + hz]), 'faces': faces}
    if abs(rest) > 0.01:
        e['rotation'] = {'angle': round(rest, 3), 'axis': 'z', 'origin': rnd3([cx, cy, cz])}
    if light:
        e['light_emission'] = light
    e['name'] = name or '%s %03d' % (kind, pose)
    return e


# ---------------------------------------------------------------- the sword (static)
def sword():
    E = []
    # pommel: a gold knob with a ruby cap
    E.append(static_box([6.9, -13.6, 6.9], [9.1, -12.0, 9.1], 'gold', faces_mat={'down': 'gold_dark'}, name='pommel'))
    E.append(static_box([7.45, -14.2, 7.45], [8.55, -13.6, 8.55], 'ruby', light=6, name='pommel ruby'))
    E.append(static_box([7.4, -12.0, 7.4], [8.6, -11.4, 8.6], 'gold_dark', name='pommel neck'))
    # grip: purple velvet bound with gold wire
    E.append(static_box([7.25, -11.4, 7.25], [8.75, -2.2, 8.75], 'velvet', faces_mat={'up': 'velvet_dark', 'down': 'velvet_dark'}, name='grip'))
    for y in (-10.2, -8.0, -5.8, -3.6):
        E.append(static_box([7.12, y - 0.18, 7.12], [8.88, y + 0.18, 8.88], 'wire', name='grip wire'))
    # guard: a heavy gold bar with curled ends and a ruby on each face
    E.append(static_box([6.1, -2.4, 6.8], [9.9, -0.3, 9.2], 'gold', faces_mat={'down': 'gold_dark'}, name='guard block'))
    for z0, z1 in ((9.2, 9.45), (6.55, 6.8)):
        E.append(static_box([7.35, -1.95, z0], [8.65, -0.75, z1], 'ruby', light=8, name='guard ruby'))
    E.append(static_box([2.9, -1.7, 7.2], [6.1, -0.8, 8.8], 'gold', faces_mat={'down': 'gold_dark'}, name='guard arm L'))
    E.append(static_box([9.9, -1.7, 7.2], [13.1, -0.8, 8.8], 'gold', faces_mat={'down': 'gold_dark'}, name='guard arm R'))
    E.append(static_box([2.0, -1.5, 7.3], [3.2, 0.5, 8.7], 'gold', rot={'angle': -22.5, 'axis': 'z', 'origin': [2.6, -1.0, 8]}, name='guard curl L'))
    E.append(static_box([12.8, -1.5, 7.3], [14.0, 0.5, 8.7], 'gold', rot={'angle': 22.5, 'axis': 'z', 'origin': [13.4, -1.0, 8]}, name='guard curl R'))
    E.append(static_box([1.55, 0.25, 7.45], [2.65, 1.35, 8.55], 'gold_light', name='finial L'))
    E.append(static_box([13.35, 0.25, 7.45], [14.45, 1.35, 8.55], 'gold_light', name='finial R'))
    # the stump of the blade: steel, a gold inlay line down each face, snapped off jaggedly
    E.append(static_box([6.45, -0.3, 7.6], [9.55, 8.6, 8.4], 'steel', faces_mat={'east': 'steel_edge', 'west': 'steel_edge'}, name='blade'))
    E.append(static_box([7.8, -0.3, 7.45], [8.2, 7.4, 8.55], 'gold', name='blade inlay'))
    E.append(static_box([6.45, 8.6, 7.6], [7.45, 11.3, 8.4], 'steel', faces_mat={'west': 'steel_edge', 'up': 'steel_dark'}, name='break tooth L'))
    E.append(static_box([7.45, 8.6, 7.6], [8.35, 9.7, 8.4], 'steel', faces_mat={'up': 'steel_dark'}, name='break notch'))
    E.append(static_box([8.35, 8.6, 7.6], [9.55, 12.1, 8.4], 'steel', faces_mat={'east': 'steel_edge', 'up': 'steel_dark'}, name='break tooth R'))
    E.append(static_box([8.6, 11.6, 7.65], [9.2, 13.0, 8.35], 'steel', rot={'angle': -28, 'axis': 'z', 'origin': [8.9, 12.0, 8]}, faces_mat={'up': 'steel_dark'}, name='break splinter'))
    E.append(static_box([6.7, 10.9, 7.65], [7.2, 12.0, 8.35], 'steel', rot={'angle': 24, 'axis': 'z', 'origin': [6.95, 11.0, 8]}, faces_mat={'up': 'steel_dark'}, name='break sliver'))
    # a crack running down from the break, on both faces
    for z0, z1 in ((8.4, 8.46), (7.54, 7.6)):
        E.append(static_box([7.9, 5.6, z0], [8.12, 9.2, z1], 'crack', rot={'angle': 14, 'axis': 'z', 'origin': [8.0, 7.4, 8]}, name='crack'))
        E.append(static_box([8.2, 4.2, z0], [8.4, 6.0, z1], 'crack', rot={'angle': -20, 'axis': 'z', 'origin': [8.3, 5.4, 8]}, name='crack'))
    return E


# ---------------------------------------------------------------- the shards (gated)
def shards(pose):
    """The blade's missing pieces, in the order they broke off, each bobbing on its own phase."""
    u = pose / SHARD_POSES
    ph = math.tau * u
    E = []
    # (centre, base tilt, bob phase, sway)
    pieces = [
        ((8.2, 14.6, 8), 7, 0.0),
        ((7.6, 18.3, 8), -11, 2.1),
        ((8.5, 22.0, 8), 5, 4.2),
    ]
    steel = {'all': 'steel', 'east': 'steel_edge', 'west': 'steel_edge', 'up': 'steel_dark', 'down': 'steel_dark'}
    gold = {'all': 'gold'}
    for i, (c, tilt, off) in enumerate(pieces):
        bob = 0.45 * math.sin(ph + off)
        sway = 3.5 * math.sin(ph + off + 1.1)
        t = tilt + sway
        C = (c[0], c[1] + bob, c[2])

        def add(local, half, mats, spin=0, cull=()):
            E.append(turned_box(C, local, half, t, mats, 'shards', pose, '#2', spin=spin, cull=cull))
        if i == 0:
            # the piece that fits the break: a tooth underneath that fits the notch, its top
            # snapped off at a slant (a square on its corner sticking up off-centre)
            add((0, 0.2, 0), (1.55, 0.95, 0.36), steel)
            add((-0.25, -1.15, 0), (0.42, 0.45, 0.36), steel, cull=('up',))
            add((0.75, 1.05, 0), (0.62, 0.62, 0.34), steel, spin=45)
            add((0, 0.15, 0), (0.2, 0.9, 0.42), gold, cull=('up', 'down'))
        elif i == 1:
            # a long sliver, broken across at an angle at both ends
            add((0, 0, 0), (1.2, 1.25, 0.34), steel)
            add((-0.85, -1.15, 0), (0.55, 0.55, 0.32), steel, spin=45)
            add((0.7, 1.2, 0), (0.48, 0.48, 0.32), steel, spin=45)
            add((0, 0, 0), (0.2, 1.1, 0.4), gold, cull=('up', 'down'))
        else:
            # the tip: a short block narrowing to a point
            add((0, -0.75, 0), (1.0, 0.8, 0.32), steel)
            add((0, 0.25, 0), (0.72, 0.72, 0.3), steel, spin=45)
            add((0, 0.95, 0), (0.36, 0.36, 0.28), steel, spin=45)
    # a stray chip off to the side
    cb = 0.35 * math.sin(ph + 3.0)
    E.append(turned_box((10.6, 16.4 + cb, 8), (0, 0, 0), (0.32, 0.32, 0.25), 20 + 6 * math.sin(ph), steel, 'shards', pose, '#2', spin=45))
    return E


# ---------------------------------------------------------------- the crown (gated)
CROWN_C = (8.0, 27.75, 8.0)
CROOK = 16          # degrees it sits askew at rest


def crown_angle(u):
    """Full turn per cycle, slow near upright and upside down (it lingers on both)."""
    a = 0.72
    return CROOK + 360 * (u - a * math.sin(4 * math.pi * u) / (4 * math.pi))


def crown(pose):
    u = pose / CROWN_POSES
    ang = crown_angle(u)
    bob = 0.5 * math.sin(math.tau * u * 2)
    C = (CROWN_C[0] + 0.35 * math.sin(math.tau * u), CROWN_C[1] + bob, CROWN_C[2])
    W, D, t = 3.3, 2.5, 0.5          # half width (x), half depth (z), wall thickness
    y0, y1 = -1.5, 0.3               # band bottom/top relative to the crown centre
    hb = (y1 - y0) / 2
    yb = (y0 + y1) / 2
    band = {'all': 'gold', 'down': 'gold_dark'}
    E = []

    def add(local, half, mats, light=0, cull=(), spin=0):
        E.append(turned_box(C, local, half, ang, mats, 'crown', pose, '#1', light, cull=cull, spin=spin))

    # the band: four walls, velvet on the inside
    add((0, yb, D - t / 2), (W, hb, t / 2), dict(band, north='velvet'))
    add((0, yb, -D + t / 2), (W, hb, t / 2), dict(band, south='velvet'))
    add((-W + t / 2, yb, 0), (t / 2, hb, D - t), dict(band, east='velvet'))
    add((W - t / 2, yb, 0), (t / 2, hb, D - t), dict(band, west='velvet'))
    # points: four at the corners, one tall one at the front
    # points: triangular teeth along the front and back walls (squares stood on a corner, their
    # lower halves hidden in the band), the middle ones taller
    for sz in (-1, 1):
        zc = sz * (D - t / 2)
        for x, h in ((-2.45, 0.6), (0, 0.88), (2.45, 0.6)):
            add((x, y1 + 0.2, zc), (h, h, t / 2 - 0.02), {'all': 'gold', 'up': 'gold_light', 'west': 'gold_light'}, spin=45)
    # the ruby on its front
    add((0, yb, D + 0.12), (0.55, 0.55, 0.14), {'all': 'ruby'}, light=10, cull=('north',))
    return E


# ---------------------------------------------------------------- display (Eureka's, approved in game)
DISPLAY = {
    'gui': {'rotation': [12, -24, -37], 'translation': [0, 0, 0], 'scale': [0.51, 0.51, 0.51]},
    'firstperson_righthand': {'rotation': [0, -90, 22], 'translation': [1, -1, -1.7], 'scale': [0.67, 0.67, 0.67]},
    'firstperson_lefthand': {'rotation': [0, 90, -22], 'translation': [1, -1, -1.7], 'scale': [0.67, 0.67, 0.67]},
    'thirdperson_righthand': {'rotation': [0, 90, -18], 'translation': [0, 2, 0], 'scale': [0.63, 0.63, 0.63]},
    'thirdperson_lefthand': {'rotation': [0, -90, 18], 'translation': [0, 2, 0], 'scale': [0.63, 0.63, 0.63]},
    'ground': {'rotation': [0, 0, -25], 'translation': [0, 3, 0], 'scale': [0.35, 0.35, 0.35]},
    'fixed': {'rotation': [0, 180, -35], 'translation': [0, 0, 0], 'scale': [0.48, 0.48, 0.48]},
    'head': {'rotation': [0, 180, 0], 'translation': [0, 6, 0], 'scale': [0.6, 0.6, 0.6]},
}


# ---------------------------------------------------------------- inventory icon (32x32, drawn)
def outline(im, col=(30, 18, 34, 255)):
    """A 1-pixel dark edge round every opaque shape (4-neighbours), like hand-drawn item art."""
    px = im.load()
    w, h = im.size
    edge = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] == 255
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                edge.append((x, y))
    for x, y in edge:
        px[x, y] = col
    return im


def icon():
    """32x32, drawn at size: the snapped sword on the vanilla diagonal (pommel bottom-left), its
    pieces drifting up toward the top-right corner, where the crown hangs tipped over."""
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    g, gl, gd = GOLD + (255,), GOLD_LIGHT + (255,), GOLD_DARK + (255,)
    st, sl, sd = STEEL + (255,), STEEL_LIGHT + (255,), STEEL_DARK + (255,)
    vel, rb = VELVET + (255,), RUBY + (255,)
    # grip: velvet with gold wire, pommel
    for i in range(5):
        d.point([(4 + i, 27 - i), (5 + i, 27 - i), (4 + i, 26 - i)], fill=vel)
    d.point([(5, 26), (7, 24)], fill=gl)
    d.rectangle([2, 28, 3, 29], fill=g)
    d.point([(2, 29)], fill=gd)
    # guard: a bar across the diagonal, curled ends, ruby in the middle
    for i in range(7):
        d.point([(6 + i, 19 + i)], fill=g)
        d.point([(7 + i, 19 + i)], fill=gd if i % 3 == 0 else g)
    d.point([(5, 18), (13, 26), (14, 26), (5, 19)], fill=gl)
    d.point([(9, 22), (10, 22), (9, 23)], fill=rb)
    # the stump: three pixels wide, snapped off in two teeth
    for i in range(4):
        x, y = 11 + i, 20 - i
        d.point([(x, y), (x + 1, y)], fill=st)
        d.point([(x, y - 1)], fill=sl)
        d.point([(x + 1, y + 1)], fill=sd)
    d.point([(15, 15), (14, 15)], fill=sl)
    d.point([(16, 17), (16, 16)], fill=st)
    # the pieces, gaps between them, the last one the tip
    d.point([(18, 13), (19, 13), (19, 12), (20, 12), (19, 11)], fill=st)
    d.point([(18, 12)], fill=sl)
    d.point([(22, 9), (23, 9), (23, 8)], fill=sl)
    d.point([(22, 10)], fill=st)
    d.point([(25, 6)], fill=sl)
    # the crown, upside down: band on top, points hanging down
    d.rectangle([24, 1, 31, 2], fill=g)
    d.line([(24, 1), (31, 1)], fill=gd)
    d.point([(24, 3), (25, 3), (24, 4), (27, 3), (28, 3), (27, 4), (28, 4), (28, 5), (30, 3), (31, 3), (31, 4)], fill=g)
    d.point([(24, 4), (28, 5), (31, 4)], fill=gl)
    d.point([(26, 2), (29, 2)], fill=rb)
    return outline(im)


# ---------------------------------------------------------------- write
def write(rel, data, root=A):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, Image.Image):
        data.save(path)
    else:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, separators=(',', ':'))


def check(E):
    for e in E:
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, (e.get('name'), v)
        if 'rotation' in e:
            assert -45 <= e['rotation']['angle'] <= 45, e['rotation']


def build(preview_dir=None):
    static = sword()
    gated_s = [e for p in range(SHARD_POSES) for e in shards(p)]
    gated_c = [e for p in range(CROWN_POSES) for e in crown(p)]
    E = static + gated_s + gated_c
    check(E)
    textures = {'0': T_STATIC, '1': T_CROWN, '2': T_SHARDS, 'particle': T_STATIC}
    # 'name' is ignored by the game; keep it only for the preview
    game = [{k: v for k, v in e.items() if k != 'name'} for e in E]
    write('models/item/king_of_nothing.json', {
        'credit': 'Elytro - King of Nothing (king_of_nothing_build.py)',
        'textures': textures, 'gui_light': 'front', 'display': DISPLAY, 'elements': game})
    write('textures/item/king_of_nothing.png', static_texture())
    write('textures/item/king_of_nothing_crown.png', gated_texture('crown', CROWN_POSES))
    write('textures/item/king_of_nothing_crown.png.mcmeta', {'animation': {'frametime': CROWN_TICKS, 'interpolate': False}})
    write('textures/item/king_of_nothing_shards.png', gated_texture('shards', SHARD_POSES))
    write('textures/item/king_of_nothing_shards.png.mcmeta', {'animation': {'frametime': SHARD_TICKS, 'interpolate': False}})
    write('textures/item/king_of_nothing_icon.png', icon())
    write('models/item/king_of_nothing_icon.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/king_of_nothing_icon'}})
    write('items/king_of_nothing.json', {
        'hand_animation_on_swap': False,
        'model': {'type': 'minecraft:select', 'property': 'minecraft:display_context',
                  'cases': [{'when': ['gui', 'fixed'], 'model': {'type': 'minecraft:model', 'model': 'elytro:item/king_of_nothing_icon'}}],
                  'fallback': {'type': 'minecraft:model', 'model': 'elytro:item/king_of_nothing'}}})
    print('King of Nothing: %d static, %d shard (%d poses), %d crown (%d poses) = %d elements' % (
        len(static), len(gated_s), SHARD_POSES, len(gated_c), CROWN_POSES, len(E)))
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)
        write('kon_static.png', static_texture(), preview_dir)
        write('kon_crown_all.png', gated_texture('crown', CROWN_POSES, opaque=True), preview_dir)
        write('kon_shards_all.png', gated_texture('shards', SHARD_POSES, opaque=True), preview_dir)
        write('kon_icon.png', icon().resize((256, 256), Image.NEAREST), preview_dir)
        write('kon_elements.json', {'crown_poses': CROWN_POSES, 'shards_poses': SHARD_POSES,
                                    'crown_ticks': CROWN_TICKS, 'shards_ticks': SHARD_TICKS,
                                    'textures': {'#0': 'kon_static.png', '#1': 'kon_crown_all.png', '#2': 'kon_shards_all.png'},
                                    'elements': E}, preview_dir)


if __name__ == '__main__':
    build(sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None)
