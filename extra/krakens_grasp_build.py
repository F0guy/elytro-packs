"""Kraken's Grasp - a fishing rod skin (rare fishing-event reward), with its own line and bobber.

The rod is a kraken's tentacle: a black leather grip and brass reel, and above them the shaft
becomes one thick violet tentacle, tapering as it rises, its glowing cyan suckers in a row down
one side. At the top its tip curls round a shimmering pearl, holding it. The tentacle sways and
its grip on the pearl tightens and loosens (32 poses on the item model's random+wobble time).

The tentacle bends in one plane only, so every segment needs a single rotation about z and the
curve stays smooth instead of stepping like stacked blocks.

FishingCore draws the line and bobber for this rod (rod-cosmetics in its config), using:
  elytro:kraken_line    one segment of the spectral line (+z, one block, see-through glow)
  elytro:kraken_bobber  a tiny kraken bobbing at the end of the line, eyes lit, arms dangling

Writes into ./assets/elytro (this folder):
  items/krakens_grasp.json, items/kraken_line.json, items/kraken_bobber.json
  models/item/krakens_grasp_base.json, krakens_grasp_icon.json, krakens_grasp/writhe_00..31.json
  models/item/kraken_line.json, kraken_bobber/bob_00..15.json
  textures/item/krakens_grasp.png (+ .mcmeta), krakens_grasp_icon.png, kraken_line.png (+ .mcmeta)
Usage (needs Pillow): python krakens_grasp_build.py
"""
import json
import math
import os
import random
import shutil

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')
POSES = 32
BOB_POSES = 16
TEX = 'elytro:item/krakens_grasp'

# ---------------------------------------------------------------- texture
SW = {
    'grip': (0, 0), 'grip_dark': (1, 0), 'brass': (2, 0), 'brass_dark': (3, 0),
    'skin': (4, 0), 'skin_light': (5, 0), 'under': (6, 0), 'sucker': (7, 0),
    'pearl': (0, 1), 'pearl_shade': (1, 1), 'eye': (2, 1), 'mantle': (3, 1), 'spot': (4, 1), 'silver': (5, 1),
}
FRAMES = 8


def texture():
    rnd = random.Random(9)
    noise = {k: [[rnd.random() for _ in range(8)] for _ in range(8)] for k in SW}
    frames = []
    for f in range(FRAMES):
        phase = f / FRAMES * math.tau
        pulse = 0.5 + 0.5 * math.sin(phase)
        im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        px = im.load()

        def mix(a, b, t):
            t = max(0.0, min(1.0, t))
            return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)

        def fill(name, fn):
            cx, cy = SW[name]
            n = noise[name]
            for y in range(8):
                for x in range(8):
                    px[cx * 8 + x, cy * 8 + y] = fn(x, y, n[y][x])

        fill('grip', lambda x, y, n: mix((26, 20, 32), (64, 48, 74), 0.85 if (x + 2 * y) % 5 == 0 else 0.3 * n))
        fill('grip_dark', lambda x, y, n: mix((14, 10, 18), (32, 24, 40), n))
        fill('brass', lambda x, y, n: mix((140, 100, 44), (232, 192, 104), (1 - y / 7) * 0.85 + 0.15 * n))
        fill('brass_dark', lambda x, y, n: mix((62, 44, 22), (114, 84, 40), 0.7 * n))
        # tentacle skin: violet, darker ridges across it, lighter toward its edge
        fill('skin', lambda x, y, n: mix((54, 24, 92), (104, 58, 150), 0.25 + 0.55 * n - (0.25 if y % 3 == 0 else 0)))
        fill('skin_light', lambda x, y, n: mix((110, 66, 162), (156, 108, 206), 0.6 * n))
        fill('under', lambda x, y, n: mix((150, 112, 186), (196, 160, 222), 0.6 * n))

        def sucker(x, y, n):
            r = math.hypot(x - 3.5, y - 3.5)
            if r < 1.3:
                return mix((30, 110, 130), (110, 240, 238), pulse)
            if r < 3.2:
                return mix((96, 226, 228), (206, 255, 252), pulse)
            return (150, 112, 186, 255)
        fill('sucker', sucker)

        def pearl(x, y, n, shade=0.0):
            sweep = math.sin((x + y) * 0.55 - phase)
            base = mix((246, 240, 255), (200, 238, 252), 0.5 + 0.5 * sweep)
            tint = mix(base[:3], (228, 198, 252), 0.5 + 0.5 * math.sin(x * 0.7 + phase * 2))
            c = mix(tint[:3], (255, 255, 255), 0.75 if (x, y) == (2, 2) else 0)
            return mix(c[:3], (140, 116, 190), shade)
        fill('pearl', pearl)
        fill('pearl_shade', lambda x, y, n: pearl(x, y, n, 0.32))

        def eye(x, y, n):
            if x in (3, 4) and 1 <= y <= 6:
                return (20, 6, 4, 255)
            r = math.hypot(x - 3.5, y - 3.5)
            return mix((255, 140, 26), (255, 232, 120), (1 - r / 5) * (0.7 + 0.3 * pulse))
        fill('eye', eye)
        fill('mantle', lambda x, y, n: mix((46, 18, 78), (96, 50, 140), 0.25 + 0.6 * n) if (x * 5 + y * 3) % 9 else (24, 8, 40, 255))
        fill('spot', lambda x, y, n: mix((70, 200, 210), (180, 255, 250), pulse))
        fill('silver', lambda x, y, n: mix((140, 150, 160), (226, 232, 238), 1 - y / 7))
        frames.append(im)
    sheet = Image.new('RGBA', (64, 64 * FRAMES))
    for i, im in enumerate(frames):
        sheet.paste(im, (0, 64 * i))
    return sheet


def line_texture():
    """The spectral line: a see-through glowing tendril, cyan at its core fading to violet, with
    faint sucker rings along it. 16x16, animated so a glow ripples along it."""
    frames = []
    for f in range(8):
        im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        px = im.load()
        for y in range(16):
            for x in range(16):
                across = abs(x - 7.5) / 8
                along = (y + f * 2) % 16
                glow = 0.55 + 0.45 * math.cos(along / 16 * math.tau)
                r = int(110 + (176 - 110) * across)
                g = int(245 + (104 - 245) * across)
                b = int(232 + (255 - 232) * across)
                a = int((215 - 120 * across) * (0.75 + 0.25 * glow))
                if along in (3, 11) and 4 <= x <= 11:
                    r, g, b, a = 230, 255, 252, 235
                px[x, y] = (r, g, b, a)
        frames.append(im)
    sheet = Image.new('RGBA', (16, 16 * 8))
    for i, im in enumerate(frames):
        sheet.paste(im, (0, 16 * i))
    return sheet


def uv(name):
    cx, cy = SW[name]
    u0, v0 = cx * 2 + 0.2, cy * 2 + 0.2
    return [round(u0, 3), round(v0, 3), round(u0 + 1.6, 3), round(v0 + 1.6, 3)]


# ---------------------------------------------------------------- geometry

def box(frm, to, mat, rot=None, light=0, faces_mat=None):
    faces = {f: {'uv': uv((faces_mat or {}).get(f, mat)), 'texture': '#0'}
             for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    e = {'from': [round(v, 3) for v in frm], 'to': [round(v, 3) for v in to], 'faces': faces}
    if rot:
        e['rotation'] = rot
    if light:
        e['light_emission'] = light
    return e


def seg(p, q, w, depth, mat, faces_mat=None, light=0, axis='z', overlap=0.35):
    """A box from p to q lying in a plane (x-y for axis 'z', z-y for axis 'x'), w across and
    `depth` thick, turned with a single rotation. Any direction works: the box's long side is laid
    along whichever of its two in-plane axes is nearer, so the turn stays within +-45 degrees."""
    if axis == 'z':
        (a1, b1), (a2, b2) = (p[0], p[1]), (q[0], q[1])
    else:
        (a1, b1), (a2, b2) = (p[2], p[1]), (q[2], q[1])
    da, db = a2 - a1, b2 - b1
    length = math.hypot(da, db) + overlap
    ang = math.degrees(math.atan2(db, da))                      # 0 = along the first in-plane axis
    k = round(ang / 90)
    turn = ang - 90 * k
    along_first = k % 2 == 0
    ca, cb = (a1 + a2) / 2, (b1 + b2) / 2
    la, lb = (length, w) if along_first else (w, length)
    if axis == 'z':
        cz = (p[2] + q[2]) / 2
        frm, to = [ca - la / 2, cb - lb / 2, cz - depth / 2], [ca + la / 2, cb + lb / 2, cz + depth / 2]
        origin = [ca, cb, cz]
        rot = {'angle': round(turn, 3), 'axis': 'z', 'origin': [round(v, 3) for v in origin]}
    else:
        cx = (p[0] + q[0]) / 2
        frm, to = [cx - depth / 2, cb - lb / 2, ca - la / 2], [cx + depth / 2, cb + lb / 2, ca + la / 2]
        origin = [cx, cb, ca]
        # about x, a positive turn tips +y toward +z: the opposite sense of our (z, y) angle
        rot = {'angle': round(-turn, 3), 'axis': 'x', 'origin': [round(v, 3) for v in origin]}
    return box(frm, to, mat, rot if abs(turn) > 0.3 else None, light, faces_mat)


def sphere(c, r, mat, light=0, shade='pearl_shade'):
    els = [box([c[0] - r * 0.81, c[1] - r * 0.81, c[2] - r * 0.81], [c[0] + r * 0.81, c[1] + r * 0.81, c[2] + r * 0.81], mat, light=light)]
    for dx, dy, dz in ((2.0, 1.25, 1.25), (1.25, 2.0, 1.25), (1.25, 1.25, 2.0)):
        els.append(box([c[0] - r * dx / 2, c[1] - r * dy / 2, c[2] - r * dz / 2],
                       [c[0] + r * dx / 2, c[1] + r * dy / 2, c[2] + r * dz / 2], mat, light=light,
                       faces_mat={'down': shade, 'east': shade}))
    return els


# ---------------------------------------------------------------- the rod

def rod_parts():
    """Everything that doesn't move: grip, reel, the brass collar the tentacle grows from."""
    els = []
    els.append(box([7.2, -9.2, 7.2], [8.8, -8.6, 8.8], 'brass'))                       # butt cap
    els.append(box([7.0, -8.6, 7.0], [9.0, -0.8, 9.0], 'grip', faces_mat={'up': 'grip_dark', 'down': 'grip_dark'}))
    for y in (-6.4, -3.4):
        els.append(box([6.85, y - 0.2, 6.85], [9.15, y + 0.2, 9.15], 'brass_dark'))
    els.append(box([6.7, -0.8, 6.7], [9.3, 0.4, 9.3], 'brass'))                         # collar
    els.append(box([6.95, 0.4, 6.95], [9.05, 0.8, 9.05], 'brass_dark'))
    # reel on the right of the grip, with its handle
    els.append(box([9.0, -5.6, 7.3], [9.6, -3.9, 8.7], 'brass_dark'))
    els.append(box([9.6, -6.2, 6.8], [10.9, -3.3, 9.2], 'brass', faces_mat={'east': 'brass_dark'}))
    els.append(box([10.9, -5.0, 7.8], [11.5, -4.5, 8.2], 'silver'))
    els.append(box([11.2, -5.0, 8.2], [11.5, -4.5, 9.3], 'silver'))
    return els


def centreline(u):
    """The tentacle's spine from the collar up (x, y), and its width at each point."""
    phase = math.tau * u
    amp = 0.9 + 0.65 * math.sin(phase)
    pts = []
    n = 22
    for i in range(n + 1):
        t = i / n
        y = 0.6 + 18.0 * t
        x = 8.0 + amp * math.sin(math.pi * 1.35 * t + 0.6 * math.sin(phase + 1.3)) * t ** 0.8
        w = 2.35 - 1.55 * t
        pts.append((x, y, w))
    return pts


def tentacle(u):
    els = []
    phase = math.tau * u
    spine = centreline(u)
    z = 8.0
    # the shaft: skin facing out (north/south), the pale underside with suckers facing -x
    for (x1, y1, w1), (x2, y2, w2) in zip(spine, spine[1:]):
        w = (w1 + w2) / 2
        els.append(seg((x1, y1, z), (x2, y2, z), w, w * 0.9, 'skin',
                       faces_mat={'west': 'under', 'east': 'skin_light', 'up': 'skin_light'}))
    for i in range(2, len(spine) - 2, 2):
        x, y, w = spine[i]
        nx, ny, _ = spine[i + 1]
        px_, py_, _ = spine[i - 1]
        # the side facing -x, perpendicular to the spine
        dx, dy = nx - px_, ny - py_
        ln = math.hypot(dx, dy) or 1
        ox, oy = -dy / ln, dx / ln
        if ox > 0:
            ox, oy = -ox, -oy
        s = max(0.32, w * 0.34)
        c = (x + ox * w * 0.5, y + oy * w * 0.5, z)
        els.append(box([c[0] - s / 2, c[1] - s / 2, c[2] - s / 2], [c[0] + s / 2, c[1] + s / 2, c[2] + s / 2], 'sucker', light=8))
    # the tip curls round the pearl, clockwise over the top and down its far side
    tx, ty, tw = spine[-1]
    tight = 0.5 + 0.5 * math.sin(phase + 2.0)
    pr = 1.45
    pc = (tx + 1.75, ty + 1.15, z)
    start = math.atan2(ty - pc[1], tx - pc[0])
    end = math.radians(-70 - 60 * tight)
    sweep = (start - end) % math.tau
    prev = (tx, ty)
    m = 14
    for i in range(1, m + 1):
        t = i / m
        a = start - sweep * t
        r = (pr + 0.55) - 0.35 * t
        p = (pc[0] + r * math.cos(a), pc[1] + r * math.sin(a))
        w = tw * (1 - 0.6 * t)
        els.append(seg((prev[0], prev[1], z), (p[0], p[1], z), max(0.3, w), max(0.3, w * 0.9),
                       'skin', faces_mat={'west': 'under', 'east': 'skin_light'}, overlap=0.25))
        prev = p
    els += sphere(pc, pr, 'pearl', light=12)
    return els


# ---------------------------------------------------------------- the bobber: a tiny kraken

def bobber(u):
    """Centred on (8, 8, 8): a round mantle with two lit eyes above the waterline, four short arms
    dangling below it, swaying."""
    phase = math.tau * u
    els = []
    # mantle: a rounded dome, pointing up
    for (y0, y1, h) in ((7.0, 8.4, 3.1), (8.4, 10.6, 3.4), (10.6, 12.2, 2.9), (12.2, 13.4, 2.1), (13.4, 14.2, 1.1)):
        els.append(box([8 - h, y0, 8 - h], [8 + h, y1, 8 + h], 'mantle', faces_mat={'down': 'under'}))
    # two big amber eyes on its front, looking at whoever cast it
    for side in (-1, 1):
        els.append(box([8 + side * 1.45 - 0.75, 8.9, 11.4], [8 + side * 1.45 + 0.75, 10.4, 11.55], 'eye', light=13))
    for (x, y, zf) in ((8, 13.0, 10.15), (6.4, 11.4, 10.95), (9.6, 11.4, 10.95)):
        els.append(box([x - 0.32, y - 0.32, zf], [x + 0.32, y + 0.32, zf + 0.12], 'spot', light=9))
    # four arms, two swinging in each plane
    for k, (axis, side) in enumerate((('z', -1), ('z', 1), ('x', -1), ('x', 1))):
        sway = 0.8 * math.sin(phase + k * 1.6)
        prev = None
        for i in range(7):
            t = i / 6
            off = side * (2.0 + 1.1 * t) + sway * t * t + side * 0.9 * math.sin(t * 2.4) * t
            y = 7.2 - 5.6 * t + 0.7 * t * t * (1 + 0.5 * math.sin(phase + k))
            p = (8 + off, y, 8) if axis == 'z' else (8, y, 8 + off)
            if prev:
                w = 1.05 - 0.6 * t
                els.append(seg(prev, p, w, w, 'skin', faces_mat={'west': 'under', 'north': 'under'}, axis=axis, overlap=0.25))
            prev = p
    return els


# ---------------------------------------------------------------- models

def rod_display():
    # vanilla handheld_rod's transforms, each turned a further -45 degrees about z: the model
    # stands up straight, the vanilla sprite lies on the diagonal
    return {
        'thirdperson_righthand': {'rotation': [0, 90, 10], 'translation': [0, 4, 2.5], 'scale': [0.85, 0.85, 0.85]},
        'thirdperson_lefthand': {'rotation': [0, -90, -100], 'translation': [0, 4, 2.5], 'scale': [0.85, 0.85, 0.85]},
        'firstperson_righthand': {'rotation': [0, 90, -20], 'translation': [0, 1.6, 0.8], 'scale': [0.68, 0.68, 0.68]},
        'firstperson_lefthand': {'rotation': [0, -90, -70], 'translation': [0, 1.6, 0.8], 'scale': [0.68, 0.68, 0.68]},
        'ground': {'rotation': [0, 0, -45], 'translation': [0, 2, 0], 'scale': [0.5, 0.5, 0.5]},
        'head': {'rotation': [0, 180, -45], 'translation': [0, 13, 7], 'scale': [1, 1, 1]},
        'fixed': {'rotation': [0, 180, -45], 'scale': [1, 1, 1]},
        'gui': {'rotation': [0, 0, -45], 'scale': [0.58, 0.58, 0.58]},
    }


def model(elements, display=None, tex=TEX):
    out = {
        'credit': "Elytro - Kraken's Grasp (krakens_grasp_build.py)",
        'textures': {'0': tex, 'particle': tex},
        'gui_light': 'front',
        'elements': elements,
    }
    if display:
        out['display'] = display
    return out


def line_model():
    """One block of line along +z from the display's origin; FishingCore scales and points it."""
    faces = {f: {'uv': [0, 0, 16, 16], 'texture': '#0'} for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    return {
        'credit': "Elytro - Kraken's Grasp line (krakens_grasp_build.py)",
        'textures': {'0': 'elytro:item/kraken_line', 'particle': 'elytro:item/kraken_line'},
        'elements': [{'from': [7.5, 7.5, 8], 'to': [8.5, 8.5, 24], 'faces': faces, 'light_emission': 15}],
    }


def icon():
    """32x32 flat inventory icon: grip and reel bottom-left, the tentacle arcing up to the
    top-right with glowing suckers, its tip curled round the pearl."""
    S = 8
    im = Image.new('RGBA', (32 * S, 32 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    outline = (14, 6, 22, 255)

    def P(x, y):
        return (x * S, y * S)

    # grip
    d.line([P(2.5, 29.5), P(9, 23)], fill=outline, width=int(4.2 * S))
    d.line([P(2.5, 29.5), P(9, 23)], fill=(52, 38, 64, 255), width=int(2.6 * S))
    d.line([P(8.4, 23.6), P(10.2, 21.8)], fill=(232, 192, 104, 255), width=int(3.6 * S))
    d.ellipse([P(6.2, 25.4), P(9.8, 29.0)], fill=(196, 150, 70, 255), outline=(90, 64, 28, 255), width=S)
    # the tentacle: thick at the collar, thinning, bowing as it goes
    spine = []
    for i in range(70):
        t = i / 69
        bx, by = 10 + 16 * t, 22 - 16 * t
        bow = 3.0 * math.sin(math.pi * 1.2 * t) * t ** 0.8
        spine.append((bx + bow * 0.7, by + bow * 0.7, 3.4 - 2.3 * t))
    for x, y, w in spine:
        d.ellipse([P(x - w / 2 - 0.45, y - w / 2 - 0.45), P(x + w / 2 + 0.45, y + w / 2 + 0.45)], fill=outline)
    for x, y, w in spine:
        d.ellipse([P(x - w / 2, y - w / 2), P(x + w / 2, y + w / 2)], fill=(92, 50, 140, 255))
    for x, y, w in spine[::3]:
        d.ellipse([P(x - w / 2 + 0.3, y - w / 2 - 0.1), P(x + w / 2 - 0.6, y + w / 2 - 0.9)], fill=(128, 80, 182, 255))
    for i in range(6, 66, 9):
        x, y, w = spine[i]
        d.ellipse([P(x + w * 0.25 - 0.55, y + w * 0.25 - 0.55), P(x + w * 0.25 + 0.55, y + w * 0.25 + 0.55)], fill=(150, 250, 246, 255))
    # tip curling round the pearl at the top right
    tx, ty, _ = spine[-1]
    pc = (tx + 1.4, ty - 1.6)
    d.ellipse([P(pc[0] - 2.7, pc[1] - 2.7), P(pc[0] + 2.7, pc[1] + 2.7)], fill=outline)
    d.ellipse([P(pc[0] - 2.1, pc[1] - 2.1), P(pc[0] + 2.1, pc[1] + 2.1)], fill=(240, 232, 255, 255))
    d.ellipse([P(pc[0] - 1.4, pc[1] - 1.5), P(pc[0] - 0.4, pc[1] - 0.5)], fill=(255, 255, 255, 255))
    d.arc([P(pc[0] - 3.0, pc[1] - 3.0), P(pc[0] + 3.0, pc[1] + 3.0)], 120, 380, fill=outline, width=int(1.6 * S))
    d.arc([P(pc[0] - 2.8, pc[1] - 2.8), P(pc[0] + 2.8, pc[1] + 2.8)], 125, 375, fill=(110, 66, 160, 255), width=int(1.0 * S))
    small = im.resize((32, 32), Image.LANCZOS)
    px = small.load()
    for y in range(32):
        for x in range(32):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255 if a > 110 else 0)
    return small


def poses_dispatch(prefix, count):
    entries = [{'threshold': round(i / count, 6), 'model': {'type': 'minecraft:model', 'model': f'{prefix}_{i:02d}'}} for i in range(count)]
    return {'type': 'minecraft:range_dispatch', 'property': 'minecraft:time', 'source': 'random', 'wobble': True, 'entries': entries}


def item_definitions():
    rod = {
        'hand_animation_on_swap': False,
        'model': {
            'type': 'minecraft:select', 'property': 'minecraft:display_context',
            'cases': [{'when': ['gui', 'fixed'], 'model': {'type': 'minecraft:model', 'model': 'elytro:item/krakens_grasp_icon'}}],
            'fallback': {'type': 'minecraft:composite', 'models': [
                {'type': 'minecraft:model', 'model': 'elytro:item/krakens_grasp_base'},
                poses_dispatch('elytro:item/krakens_grasp/writhe', POSES)]},
        },
    }
    line = {'model': {'type': 'minecraft:model', 'model': 'elytro:item/kraken_line'}}
    bob = {'model': poses_dispatch('elytro:item/kraken_bobber/bob', BOB_POSES)}
    return rod, line, bob


def write(rel, data):
    path = os.path.join(A, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, Image.Image):
        data.save(path)
    else:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, separators=(',', ':'))


def check(els):
    for e in els:
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, v
        if 'rotation' in e:
            assert -45 <= e['rotation']['angle'] <= 45, e['rotation']


def build():
    for old in ('models/item/krakens_grasp', 'models/item/kraken_bobber'):
        shutil.rmtree(os.path.join(A, old), ignore_errors=True)
    for old in ('models/item/krakens_grasp_base_cast.json',):
        p = os.path.join(A, old)
        if os.path.exists(p):
            os.remove(p)
    write('textures/item/krakens_grasp.png', texture())
    write('textures/item/krakens_grasp.png.mcmeta', {'animation': {'frametime': 4, 'interpolate': True}})
    write('textures/item/krakens_grasp_icon.png', icon())
    write('textures/item/kraken_line.png', line_texture())
    write('textures/item/kraken_line.png.mcmeta', {'animation': {'frametime': 2, 'interpolate': True}})
    write('models/item/krakens_grasp_icon.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/krakens_grasp_icon'}})
    base = rod_parts()
    check(base)
    write('models/item/krakens_grasp_base.json', model(base, rod_display()))
    sizes = []
    for i in range(POSES):
        els = tentacle(i / POSES)
        check(els)
        sizes.append(len(els))
        write(f'models/item/krakens_grasp/writhe_{i:02d}.json', model(els, rod_display()))
    for i in range(BOB_POSES):
        els = bobber(i / BOB_POSES)
        check(els)
        write(f'models/item/kraken_bobber/bob_{i:02d}.json', model(els))
    write('models/item/kraken_line.json', line_model())
    rod, line, bob = item_definitions()
    write('items/krakens_grasp.json', rod)
    write('items/kraken_line.json', line)
    write('items/kraken_bobber.json', bob)
    print("Kraken's Grasp: base %d elements, %d poses x %d-%d; bobber %d poses x %d" % (
        len(base), POSES, min(sizes), max(sizes), BOB_POSES, len(bobber(0))))


if __name__ == '__main__':
    build()
