"""Elytro rank wings: chunky purple voxel angel wings (Skript rank_wings.sk shows them on players
with the Elytro rank), in the style of a low-poly wing: a solid slab with a thick rounded rim along
the top, a row of coverts below it and the flight feathers below that, each row a step thinner
than the one above so the wing has bevelled depth, and the bottom edge stepped into feather tips.

The wing is built from 1-unit columns per row. Each column's front and back faces show its own
patch of one painted wing image (projected flat onto the wing), so the columns of a row read as
one surface with feathers, quills and shading painted across it. Each wing is two jointed
models, the arm (columns 0-7, hinged at the spine) and the hand (columns 7-19, hinged at the
wrist), so the script can fold and flap them. Writes into ./assets/elytro."""
import json, math, os
import numpy as np
from PIL import Image

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'elytro')
O = 8.0                        # model units of the display origin (each piece's hinge)
TEX = 'elytro:item/rank_wing'
WRIST = 7                      # the hand starts at this column
COLS = 19
# the painted image covers wing x -1..21 and y -11..11 (model units, hinge at 0,0)
X0, Y1, SPAN = -1.0, 11.0, 22.0
N = 512


def interp(x, pts):
    xs, ys = zip(*pts)
    return float(np.interp(x, xs, ys))


def y_top(x):
    """The rim: a long, low arch that reaches out to the side, cresting just past the wrist and
    easing down toward the tip."""
    return interp(x, ((0, 0.8), (2, 2.6), (4, 3.8), (6, 4.5), (8, 4.7), (10, 4.4), (12, 3.7),
                      (14, 2.7), (16, 1.3), (17.5, -0.2), (19, -1.8)))


def y_bottom(x):
    """Where the flight feathers end: the wing stays shallow, so the feathers are short all
    along it, a little longer past the wrist."""
    return interp(x, ((0, -2.5), (3, -3.8), (6, -4.6), (9, -5.0), (12, -4.8), (15, -4.3), (17, -3.8), (19, -3.4)))


RIM, COVERT = 1.2, 1.8          # row depths below the top edge (model units)
ROWS = (  # name, z front/back half-thickness
    ('rim', 0.8), ('covert', 0.55), ('flight', 0.35))


def rows_at(x, i):
    """(row, y_low, y_high) for column i; each row's bottom is stepped into feather tips."""
    t, b = y_top(x), y_bottom(x)
    step = 0.6 if i % 2 else 0.0
    rim_low = t - RIM
    cov_low = max(b + 1.0, rim_low - COVERT + step * 0.7)
    out = [('rim', rim_low, t), ('covert', cov_low, rim_low + 0.4)]
    if cov_low - (b - step) > 0.3:
        out.append(('flight', b - step, cov_low + 0.4))
    return out


# --------------------------------------------------------------------------- painting
deep = np.array((48, 14, 98), float)
violet = np.array((104, 44, 186), float)
lilac = np.array((168, 112, 240), float)
pale = np.array((232, 208, 255), float)
ink = np.array((30, 6, 64), float)


def paint():
    """One image for the whole wing: each point is coloured by the row it falls in."""
    px = (np.arange(N) + 0.5) / N * SPAN + X0
    py = Y1 - (np.arange(N) + 0.5) / N * SPAN
    X, Y = np.meshgrid(px, py)
    top = np.vectorize(y_top)(X)
    bot = np.vectorize(y_bottom)(X)
    d = top - Y                                                    # depth below the rim edge
    img = np.zeros((N, N, 3))
    # rim: a rounded bone, lit along its crest and shaded underneath
    rim = d < RIM
    k = np.clip(d / RIM, 0, 1)[..., None]
    rimc = lilac * np.clip(1 - k * 3, 0, 1) + violet * np.clip(1 - np.abs(k - 0.4) * 2.5, 0, 1) + deep * np.clip(k * 2 - 0.8, 0, 1)
    rimc = np.where((d < 0.18)[..., None], pale * 0.7 + lilac * 0.3, rimc)
    img[rim] = rimc[rim]
    # coverts: overlapping rounded scales in two staggered rows, lit at the top of each scale,
    # with a dark rim along each scale's rounded bottom edge
    cov = (d >= RIM) & (d < RIM + COVERT + 0.6)
    rows_h = (COVERT + 0.6) / 2
    r = np.floor((d - RIM) / rows_h)
    fy = ((d - RIM) / rows_h) % 1.0
    fx = ((X / 1.25 + r * 0.5) % 1.0) - 0.5
    shape = fy + (2 * fx) ** 2 * 0.55                  # 1.0 traces each scale's rounded bottom
    covc = (lilac * (1 - fy[..., None] * 0.55) + violet * (fy[..., None] * 0.55)) * (1 - 0.18 * np.abs(2 * fx)[..., None])
    covc = np.where((shape > 0.9)[..., None] & (shape < 1.12)[..., None], ink * 0.75 + covc * 0.25, covc)
    covc = np.where((shape >= 1.12)[..., None], violet * 0.75, covc)
    covc = np.where((np.abs(fx) < 0.04)[..., None] & (fy < 0.7)[..., None], pale * 0.45 + covc * 0.55, covc)
    img[cov] = covc[cov]
    # flight feathers: long vanes fanning out from a point above the shoulder, each with a pale
    # quill, a lit vane and a shaded vane, darker outlines, lighter toward the tip
    fl = d >= RIM + COVERT
    ang = np.degrees(np.arctan2(Y - 6.0, X + 3.0))                 # fan centre above the shoulder
    w = 7.5
    fi = ang / w
    fxx = (fi % 1.0) - 0.5
    span = np.clip((d - RIM - COVERT) / np.maximum(top - bot - RIM - COVERT, 0.5), 0, 1)
    flc = violet * (1 - span[..., None]) + pale * span[..., None]
    flc = flc * (1 + 0.16 * np.sign(fxx)[..., None])               # lit and shaded vanes
    barbs = (np.sin((X - Y) * 9.0) * 0.5 + 0.5)[..., None]
    flc = flc * (0.94 + 0.06 * barbs)
    flc = np.where((np.abs(fxx) > 0.43)[..., None], ink * 0.65 + flc * 0.35, flc)
    flc = np.where((np.abs(fxx) < 0.06)[..., None], pale * 0.6 + flc * 0.4, flc)
    img[fl] = flc[fl]
    img = np.clip(img, 0, 255).astype(np.uint8)
    rgba = np.dstack([img, np.full((N, N), 255, np.uint8)])
    # two flat colours for the sides of the columns, in a corner the wing never covers
    rgba[:20, -40:-20, :3] = (deep * 0.8).astype(np.uint8)
    rgba[:20, -20:, :3] = (violet * 0.7).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def uv(x0, x1, y0, y1):
    """The patch of the painted image under a wing rectangle (uv units 0..16)."""
    s = 16 / SPAN
    return [(x0 - X0) * s, (Y1 - y1) * s, (x1 - X0) * s, (Y1 - y0) * s]


SIDE_RIM = [16 - 40 / N * 16, 0, 16 - 20 / N * 16, 20 / N * 16]
SIDE = [16 - 20 / N * 16, 0, 16, 20 / N * 16]


def column(i, ox):
    els = []
    x0, x1 = float(i), float(i + 1)
    for name, lo, hi in rows_at(i + 0.5, i):
        half = dict(ROWS)[name]
        u = uv(x0, x1, lo, hi)
        side = SIDE_RIM if name == 'rim' else SIDE
        faces = {'south': {'uv': u, 'texture': '#w'},
                 'north': {'uv': [u[2], u[1], u[0], u[3]], 'texture': '#w'}}
        for f in ('east', 'west', 'up', 'down'):
            faces[f] = {'uv': side, 'texture': '#w'}
        els.append({'from': [O + x0 - ox, O + lo, 8 - half], 'to': [O + x1 - ox, O + hi, 8 + half], 'faces': faces})
        if name == 'rim':                                  # a narrower crest rounds the rim off
            cu = uv(x0 + 0.1, x1 - 0.1, hi, hi + 0.5)
            cf = {'south': {'uv': cu, 'texture': '#w'}, 'north': {'uv': [cu[2], cu[1], cu[0], cu[3]], 'texture': '#w'}}
            for f in ('east', 'west', 'up', 'down'):
                cf[f] = {'uv': SIDE, 'texture': '#w'}
            els.append({'from': [O + x0 + 0.1 - ox, O + hi, 8 - half * 0.6], 'to': [O + x1 - 0.1 - ox, O + hi + 0.5, 8 + half * 0.6], 'faces': cf})
    return els


def check(els):
    for e in els:
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, e


def write(rel, obj):
    p = os.path.join(A, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', newline='\n') as f:
        json.dump(obj, f, indent=1)
        f.write('\n')


tex = os.path.join(A, 'textures', 'item')
os.makedirs(tex, exist_ok=True)
paint().save(os.path.join(tex, 'rank_wing.png'))
arm = [e for i in range(WRIST) for e in column(i, 0)]
hand = [e for i in range(WRIST, COLS) for e in column(i, WRIST)]
for part, els in (('arm', arm), ('hand', hand)):
    check(els)
    write('models/item/rank_wing_%s.json' % part, {'textures': {'w': TEX, 'particle': TEX}, 'elements': els})
    write('items/rank_wing_%s.json' % part, {'model': {'type': 'minecraft:model', 'model': 'elytro:item/rank_wing_%s' % part}})
print('rank wings written; %d + %d elements' % (len(arm), len(hand)))
