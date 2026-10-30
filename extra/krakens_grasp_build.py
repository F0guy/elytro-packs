"""Kraken's Grasp - a fishing rod skin (rare fishing-event reward).

The kraken itself forms the butt of the rod: a mottled violet head with two glowing amber eyes.
Four of its tentacles braid up the dark driftwood shaft, their suckers glowing cyan like deep-sea
light; a fifth reaches off the rod and holds up a shimmering pearl, swaying it as it writhes
(32 poses picked by the item model's random+wobble time, the same trick as the Eureka and
Singularity skins). A ship's-wheel reel, brass fittings and a curled coral spike at the tip.
While the rod is cast, the eyes and suckers burn brighter. Inventories and item frames show a
flat 32x32 icon instead.

The model is built standing up (rod along +y); the display transforms tilt it 45 degrees so it
lies where the vanilla rod sprite does, which keeps the fishing line on the rod tip. That frees
each element's own rotation for the tentacle segments.

Writes into ./assets/elytro (this folder):
  items/krakens_grasp.json
  models/item/krakens_grasp_base.json, krakens_grasp_base_cast.json, krakens_grasp_icon.json
  models/item/krakens_grasp/writhe_00..31.json
  textures/item/krakens_grasp.png (+ .mcmeta), krakens_grasp_icon.png
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
TEX = 'elytro:item/krakens_grasp'
AXIS_X, AXIS_Z = 8.0, 8.0

# ---------------------------------------------------------------- texture
# 64x64, 8x8-pixel swatches (2x2 uv units each), animated over FRAMES frames.
SW = {
    'wood': (0, 0), 'wood_light': (1, 0), 'grip': (2, 0), 'brass': (3, 0), 'brass_dark': (4, 0),
    'skin': (5, 0), 'skin_tip': (6, 0), 'sucker': (7, 0),
    'pearl': (0, 1), 'pearl_shade': (1, 1), 'barnacle': (2, 1), 'silver': (3, 1), 'under': (4, 1),
    'mantle': (5, 1), 'eye': (6, 1), 'coral': (7, 1),
}
FRAMES = 8


def texture():
    rnd = random.Random(5)
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

        # dark, wet driftwood with grain along the rod
        fill('wood', lambda x, y, n: mix((26, 34, 40), (48, 64, 70), 0.3 * n + (0.35 if x in (1, 5) else 0)))
        fill('wood_light', lambda x, y, n: mix((52, 70, 76), (80, 104, 108), 0.6 * n + (0.3 if x == 3 else 0)))
        # grip: black leather bound with cord
        fill('grip', lambda x, y, n: mix((24, 18, 30), (60, 44, 70), 0.85 if (x + y) % 4 == 0 else 0.3 * n))
        fill('brass', lambda x, y, n: mix((140, 100, 44), (226, 186, 100), (1 - y / 7) * 0.8 + 0.2 * n))
        fill('brass_dark', lambda x, y, n: mix((62, 44, 22), (112, 82, 38), 0.7 * n))
        # kraken skin: deep violet-indigo, mottled with darker blotches and faint cyan flecks
        def skin(x, y, n):
            if n < 0.16:
                return (24, 10, 40, 255)
            if n > 0.94:
                return mix((90, 210, 220), (160, 255, 250), pulse)
            return mix((48, 22, 82), (96, 52, 140), 0.2 + 0.6 * n)
        fill('skin', skin)
        fill('skin_tip', lambda x, y, n: mix((96, 54, 150), (150, 100, 200), 0.7 * n))
        fill('mantle', lambda x, y, n: mix((40, 16, 66), (84, 40, 124), 0.25 + 0.5 * n) if (x * 5 + y * 3) % 9 else (22, 8, 36, 255))
        fill('under', lambda x, y, n: mix((120, 80, 160), (160, 120, 196), 0.6 * n))

        # suckers: bioluminescent rings that pulse
        def sucker(x, y, n):
            r = math.hypot(x - 3.5, y - 3.5)
            if r < 1.4:
                return mix((40, 120, 140), (120, 240, 240), pulse)
            if r < 3.1:
                return mix((100, 230, 230), (200, 255, 252), pulse)
            return (60, 30, 96, 255)
        fill('sucker', sucker)

        # eyes: amber with a slit pupil, glowing
        def eye(x, y, n):
            if x in (3, 4) and 1 <= y <= 6:
                return (20, 6, 4, 255)
            r = math.hypot(x - 3.5, y - 3.5)
            return mix((255, 150, 30), (255, 230, 120), (1 - r / 5) * (0.7 + 0.3 * pulse))
        fill('eye', eye)

        # the pearl: iridescent white with a sheen that sweeps across it frame by frame
        def pearl(x, y, n, shade=0.0):
            sweep = math.sin((x + y) * 0.55 - phase)
            base = mix((244, 238, 255), (200, 238, 250), 0.5 + 0.5 * sweep)
            tint = mix(base[:3], (226, 196, 250), 0.5 + 0.5 * math.sin(x * 0.7 + phase * 2))
            c = mix(tint[:3], (255, 255, 255), 0.7 if (x, y) == (2, 2) else 0)
            return mix(c[:3], (140, 116, 190), shade)
        fill('pearl', pearl)
        fill('pearl_shade', lambda x, y, n: pearl(x, y, n, 0.35))
        fill('barnacle', lambda x, y, n: mix((104, 108, 100), (170, 172, 160), n) if (x * 3 + y * 5) % 7 else (50, 52, 48, 255))
        fill('silver', lambda x, y, n: mix((140, 150, 160), (226, 232, 238), 1 - y / 7))
        fill('coral', lambda x, y, n: mix((200, 70, 90), (255, 140, 140), 0.4 + 0.5 * n))
        frames.append(im)
    sheet = Image.new('RGBA', (64, 64 * FRAMES))
    for i, im in enumerate(frames):
        sheet.paste(im, (0, 64 * i))
    return sheet


def uv(name):
    """A uv rect inside a swatch, inset so neighbours never bleed in."""
    cx, cy = SW[name]
    u0, v0 = cx * 2 + 0.2, cy * 2 + 0.2
    return [round(u0, 3), round(v0, 3), round(u0 + 1.6, 3), round(v0 + 1.6, 3)]


# ---------------------------------------------------------------- geometry helpers

def box(frm, to, mat, rot=None, light=0, faces_mat=None):
    """An element: [frm, to] in rod-local units, all faces `mat` (per-face overrides in faces_mat)."""
    faces = {f: {'uv': uv((faces_mat or {}).get(f, mat)), 'texture': '#0'}
             for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    e = {'from': [round(v, 3) for v in frm], 'to': [round(v, 3) for v in to], 'faces': faces}
    if rot:
        e['rotation'] = rot
    if light:
        e['light_emission'] = light
    return e


def cube_at(c, size, mat, length=None, yaw=0.0, light=0, faces_mat=None, height=None):
    """A cuboid centred on c; `length` stretches it along x before turning it `yaw` degrees about y."""
    sx = (length or size) / 2
    s = size / 2
    sy = (height or size) / 2
    frm = [c[0] - sx, c[1] - sy, c[2] - s]
    to = [c[0] + sx, c[1] + sy, c[2] + s]
    # a long axis turned by yaw: fold the angle into [-45, 45] by swapping x/z extents
    a = ((yaw + 45) % 90) - 45
    if length and abs(((yaw + 45) % 180) - 45) > 45:
        frm = [c[0] - s, c[1] - sy, c[2] - sx]
        to = [c[0] + s, c[1] + sy, c[2] + sx]
    rot = {'angle': round(a, 3), 'axis': 'y', 'origin': [round(v, 3) for v in c]} if abs(a) > 0.5 else None
    return box(frm, to, mat, rot, light, faces_mat)


def sphere(c, r, mat, light=0, shade='pearl_shade'):
    """Three crossed slabs and a core: reads as a ball at item scale."""
    els = [cube_at(c, r * 1.62, mat, light=light)]
    for dx, dy, dz in ((2.0, 1.25, 1.25), (1.25, 2.0, 1.25), (1.25, 1.25, 2.0)):
        els.append(box([c[0] - r * dx / 2, c[1] - r * dy / 2, c[2] - r * dz / 2],
                       [c[0] + r * dx / 2, c[1] + r * dy / 2, c[2] + r * dz / 2], mat, light=light,
                       faces_mat={'down': shade, 'east': shade}))
    return els


# ---------------------------------------------------------------- the rod and the kraken head

def rod_parts(cast=False):
    glow = 15 if cast else 9
    els = []
    # the kraken's head is the pommel: a tapering mantle pointing down, two eyes on its flanks
    for (y0, y1, half) in ((-9.0, -8.0, 0.9), (-8.0, -6.8, 1.55), (-6.8, -5.2, 2.05), (-5.2, -3.8, 2.15), (-3.8, -2.9, 1.8)):
        els.append(box([AXIS_X - half, y0, AXIS_Z - half], [AXIS_X + half, y1, AXIS_Z + half], 'mantle',
                       faces_mat={'down': 'skin'}))
    for side in (-1, 1):
        ex = AXIS_X + side * 2.12
        els.append(box([ex - 0.12, -5.0, AXIS_Z - 0.75], [ex + 0.12, -3.9, AXIS_Z + 0.35], 'eye', light=glow))
        # a heavy brow ridge over each eye
        els.append(box([ex - 0.25 * side - 0.25, -3.95, AXIS_Z - 0.95], [ex - 0.25 * side + 0.25, -3.6, AXIS_Z + 0.55], 'mantle'))
    # glowing spots down the mantle's back
    for (y, z) in ((-7.4, 9.5), (-6.2, 10.0), (-5.0, 10.1)):
        els.append(box([AXIS_X - 0.3, y - 0.3, z], [AXIS_X + 0.3, y + 0.3, z + 0.12], 'sucker', light=glow - 2))
    # the grip, bound in black leather with brass bands, sitting in the tentacles' roots
    els.append(box([6.85, -2.9, 6.85], [9.15, 3.0, 9.15], 'grip'))
    for y in (-2.2, 0.4, 2.6):
        els.append(box([6.7, y - 0.25, 6.7], [9.3, y + 0.25, 9.3], 'brass'))
    els.append(box([7.0, 3.0, 7.0], [9.0, 3.6, 9.0], 'brass_dark'))
    # ship's-wheel reel on the side: a rim, a hub and spokes
    hub = (10.4, 4.8, 8.0)
    els.append(box([9.0, hub[1] - 0.35, 7.65], [hub[0], hub[1] + 0.35, 8.35], 'brass_dark'))
    els.append(box([hub[0] - 0.3, hub[1] - 1.4, 6.6], [hub[0] + 0.3, hub[1] + 1.4, 9.4], 'brass',
                   faces_mat={'east': 'brass_dark', 'west': 'brass_dark'}))
    els.append(box([hub[0] - 0.42, hub[1] - 0.45, 7.55], [hub[0] + 0.42, hub[1] + 0.45, 8.45], 'brass_dark'))
    for dy, dz in ((1.9, 0), (-1.9, 0), (0, 1.9), (0, -1.9)):
        c = (hub[0], hub[1] + dy * 0.82, 8.0 + dz * 0.82)
        els.append(box([c[0] - 0.12, c[1] - 0.18, c[2] - 0.18], [c[0] + 0.12, c[1] + 0.18, c[2] + 0.18], 'brass'))
    # shaft: thick near the reel, tapering to the tip
    els.append(box([7.25, 3.6, 7.25], [8.75, 9.0, 8.75], 'wood'))
    els.append(box([7.4, 9.0, 7.4], [8.6, 15.0, 8.6], 'wood', faces_mat={'south': 'wood_light'}))
    els.append(box([7.55, 15.0, 7.55], [8.45, 20.6, 8.45], 'wood_light'))
    for y in (9.0, 15.0):
        els.append(box([7.15, y - 0.25, 7.15], [8.85, y + 0.25, 8.85], 'brass'))
    # line guides standing off the top of the rod
    for y in (7.0, 12.0, 16.5):
        els.append(box([6.5, y, 7.85], [7.25, y + 0.35, 8.15], 'silver'))
    # the tip: a brass ring, then a little curled coral spike
    els.append(box([7.5, 20.6, 7.5], [8.5, 21.1, 8.5], 'brass'))
    els.append(box([7.7, 21.1, 7.7], [8.3, 21.8, 8.3], 'coral'))
    els.append(box([7.25, 21.6, 7.8], [7.75, 22.0, 8.2], 'coral'))
    # barnacles crusted near the grip
    for (x, y, z, s) in ((9.25, -0.8, 7.4, 0.55), (6.7, 1.6, 8.6, 0.5), (8.6, -1.8, 9.3, 0.45)):
        els.append(cube_at((x, y, z), s, 'barnacle'))
    return els


# ---------------------------------------------------------------- the tentacles

def braid_path(k, u):
    """Coiling tentacle k (0..3): out from under the head, braided up the shaft, tip curling off."""
    phase = math.tau * u + k * math.tau / 4
    twist = math.radians(34) * math.sin(phase)
    curl = 0.5 + 0.5 * math.sin(phase + 1.1)
    start = k * 90 + 20
    top = (14.5, 11.0, 16.8, 7.5)[k]
    pts = []
    # from the rim of the head, sweeping up around the grip
    for i in range(6):
        t = i / 5
        a = math.radians(start - 30 + 30 * t)
        r = 2.0 - 0.15 * t
        pts.append((AXIS_X + r * math.cos(a), -3.4 + 1.4 * t, AXIS_Z + r * math.sin(a), 0.9))
    turns = 1.05 + 0.1 * (k % 2)
    n = 24
    for i in range(1, n + 1):
        t = i / n
        y = -2.0 + (top + 2.0) * t
        a = math.radians(start) + t * turns * math.tau * (1 if k % 2 == 0 else -1) + twist * t
        r = (1.72 - 0.4 * t) if y < 9 else (1.3 - 0.3 * t)
        r += 0.14 * math.sin(t * 9 + phase)
        pts.append((AXIS_X + r * math.cos(a), y, AXIS_Z + r * math.sin(a), 0.8 - 0.4 * t))
    x0, y0, z0, _ = pts[-1]
    a0 = math.atan2(z0 - AXIS_Z, x0 - AXIS_X)
    out = (math.cos(a0), math.sin(a0))
    for i in range(1, 9):
        t = i / 8
        ang = t * (1.4 + 1.8 * curl) * math.pi
        rad = 1.4 * (1 - 0.6 * t)
        d = rad * math.sin(ang)
        h = rad * (1 - math.cos(ang)) * 0.8
        pts.append((x0 + out[0] * d, y0 + 0.5 * t + h * (0.6 - t), z0 + out[1] * d, 0.38 - 0.16 * t))
    return pts


def bearer(u):
    """The fifth tentacle: off the shaft and up, holding the pearl out. Returns (points, pearl centre)."""
    phase = math.tau * u
    sway = math.sin(phase)
    lift = math.sin(phase + 1.9)
    out = math.radians(-35 + 18 * sway)                         # direction it reaches, swaying
    ox, oz = math.cos(out), math.sin(out)
    pts = []
    # leaves the coil just above the reel and arcs outward and up
    base_y = 5.2
    for i in range(16):
        t = i / 15
        r = 1.6 + 2.0 * math.sin(t * math.pi / 2)
        y = base_y + 5.4 * t + 0.6 * lift * t * t
        bend = math.radians(25) * math.sin(t * math.pi) * (1 + 0.3 * sway)
        a = out + bend
        pts.append((AXIS_X + r * math.cos(a), y, AXIS_Z + r * math.sin(a), 0.82 - 0.34 * t))
    x1, y1, z1, _ = pts[-1]
    pearl = (x1 + ox * 0.35, y1 + 1.35, z1 + oz * 0.35)
    # the tip wraps round the pearl from below, like fingers closing on it
    for i in range(1, 10):
        t = i / 9
        a = out + math.pi + t * 1.6 * math.pi
        rr = 1.05
        pts.append((pearl[0] + rr * math.cos(a), pearl[1] - 0.9 + 1.5 * t, pearl[2] + rr * math.sin(a), 0.42 - 0.14 * t))
    return pts, pearl


def segments(pts, tip_from, suckers=True):
    els = []
    for i, (x, y, z, w) in enumerate(pts):
        nx, _, nz, _ = pts[min(i + 1, len(pts) - 1)]
        px_, _, pz, _ = pts[max(i - 1, 0)]
        yaw = math.degrees(math.atan2(-(nz - pz), nx - px_)) if (nx, nz) != (px_, pz) else 0
        mat = 'skin_tip' if i >= tip_from else 'skin'
        els.append(cube_at((x, y, z), w, mat, length=w * 1.9, yaw=yaw, faces_mat={'down': 'under'}))
        if suckers and i % 3 == 1 and i < len(pts) - 3:
            a = math.atan2(z - AXIS_Z, x - AXIS_X)
            sc = (x + math.cos(a) * w * 0.5, y, z + math.sin(a) * w * 0.5)
            els.append(cube_at(sc, max(0.22, w * 0.38), 'sucker', light=6))
    return els


def tentacles(u):
    els = []
    for k in range(4):
        pts = braid_path(k, u)
        els += segments(pts, len(pts) - 8)
    pts, pearl = bearer(u)
    els += segments(pts, len(pts) - 9)
    els += sphere(pearl, 1.25, 'pearl', light=12)
    return els


# ---------------------------------------------------------------- models

def display():
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
        'gui': {'rotation': [0, 0, -45], 'scale': [0.6, 0.6, 0.6]},
    }


def model(elements):
    return {
        'credit': "Elytro - Kraken's Grasp (krakens_grasp_build.py)",
        'textures': {'0': TEX, 'particle': TEX},
        'gui_light': 'front',
        'elements': elements,
        'display': display(),
    }


def icon():
    """32x32 flat inventory icon: the kraken head at the butt, a tentacle braided up the rod with
    glowing suckers, and the pearl held out on a second one."""
    S = 8
    im = Image.new('RGBA', (32 * S, 32 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def P(x, y):
        return (x * S, y * S)

    outline = (12, 6, 20, 255)
    # shaft
    d.line([P(9, 23), P(30, 2)], fill=outline, width=int(3.2 * S))
    d.line([P(9, 23), P(30, 2)], fill=(44, 60, 66, 255), width=int(1.7 * S))
    d.line([P(20, 12), P(30, 2)], fill=(76, 100, 104, 255), width=int(0.9 * S))
    d.ellipse([P(29.2, 1.2), P(31.2, 3.2)], fill=(255, 120, 130, 255))
    # grip and wheel reel
    d.line([P(7, 25), P(12, 20)], fill=outline, width=int(4.0 * S))
    d.line([P(7, 25), P(12, 20)], fill=(52, 38, 62, 255), width=int(2.6 * S))
    d.ellipse([P(11.6, 20.6), P(16.2, 25.2)], outline=(226, 186, 100, 255), width=int(0.9 * S))
    d.ellipse([P(13.3, 22.3), P(14.5, 23.5)], fill=(150, 108, 46, 255))
    # the braided tentacle with glowing suckers
    pts = []
    for i in range(60):
        t = i / 59
        cx, cy = 9 + 11 * t, 23 - 11 * t
        off = 2.1 * math.sin(t * math.tau * 2.2) * (1 - 0.4 * t)
        pts.append(P(cx + off * 0.7, cy + off * 0.7))
    d.line(pts, fill=outline, width=int(2.5 * S), joint='curve')
    d.line(pts, fill=(84, 44, 130, 255), width=int(1.5 * S), joint='curve')
    for i in range(5, 58, 9):
        x, y = pts[i]
        d.ellipse([x - S * 0.55, y - S * 0.55, x + S * 0.55, y + S * 0.55], fill=(130, 245, 240, 255))
    # the pearl-bearer reaching off the rod
    arm = []
    for i in range(30):
        t = i / 29
        arm.append(P(15 + 3.0 * t - 4.5 * t * t, 18 - 8.5 * t))
    d.line(arm, fill=outline, width=int(2.3 * S), joint='curve')
    d.line(arm, fill=(110, 66, 160, 255), width=int(1.3 * S), joint='curve')
    px_, py_ = arm[-1][0] / S, arm[-1][1] / S - 2.2
    d.ellipse([P(px_ - 2.4, py_ - 2.4), P(px_ + 2.4, py_ + 2.4)], fill=outline)
    d.ellipse([P(px_ - 1.8, py_ - 1.8), P(px_ + 1.8, py_ + 1.8)], fill=(240, 232, 255, 255))
    d.ellipse([P(px_ - 1.1, py_ - 1.2), P(px_ - 0.2, py_ - 0.3)], fill=(255, 255, 255, 255))
    # the kraken's head as the pommel, one amber eye toward us
    d.ellipse([P(1.0, 23.5), P(9.4, 31.4)], fill=outline)
    d.ellipse([P(1.7, 24.2), P(8.7, 30.7)], fill=(70, 34, 112, 255))
    d.ellipse([P(2.6, 25.0), P(5.4, 27.8)], fill=(96, 52, 140, 255))
    d.ellipse([P(4.6, 25.4), P(7.2, 28.0)], fill=(255, 170, 40, 255))
    d.line([P(5.9, 25.6), P(5.9, 27.8)], fill=(20, 6, 4, 255), width=int(0.6 * S))
    small = im.resize((32, 32), Image.LANCZOS)
    px = small.load()
    for y in range(32):
        for x in range(32):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255 if a > 110 else 0)
    return small


def item_definition():
    poses = [{'threshold': round(i / POSES, 6), 'model': {'type': 'minecraft:model', 'model': f'elytro:item/krakens_grasp/writhe_{i:02d}'}}
             for i in range(POSES)]

    def held(base):
        return {'type': 'minecraft:composite', 'models': [
            {'type': 'minecraft:model', 'model': base},
            {'type': 'minecraft:range_dispatch', 'property': 'minecraft:time', 'source': 'random', 'wobble': True, 'entries': poses},
        ]}
    return {
        'hand_animation_on_swap': False,
        'model': {
            'type': 'minecraft:select', 'property': 'minecraft:display_context',
            'cases': [{'when': ['gui', 'fixed'], 'model': {'type': 'minecraft:model', 'model': 'elytro:item/krakens_grasp_icon'}}],
            'fallback': {'type': 'minecraft:condition', 'property': 'minecraft:fishing_rod/cast',
                         'on_true': held('elytro:item/krakens_grasp_base_cast'),
                         'on_false': held('elytro:item/krakens_grasp_base')},
        },
    }


def write(rel, data):
    path = os.path.join(A, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, Image.Image):
        data.save(path)
    else:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, separators=(',', ':'))


def build():
    shutil.rmtree(os.path.join(A, 'models', 'item', 'krakens_grasp'), ignore_errors=True)
    write('textures/item/krakens_grasp.png', texture())
    write('textures/item/krakens_grasp.png.mcmeta', {'animation': {'frametime': 4, 'interpolate': True}})
    write('textures/item/krakens_grasp_icon.png', icon())
    write('models/item/krakens_grasp_icon.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/krakens_grasp_icon'}})
    write('models/item/krakens_grasp_base.json', model(rod_parts(False)))
    write('models/item/krakens_grasp_base_cast.json', model(rod_parts(True)))
    sizes = []
    for i in range(POSES):
        els = tentacles(i / POSES)
        sizes.append(len(els))
        write(f'models/item/krakens_grasp/writhe_{i:02d}.json', model(els))
    write('items/krakens_grasp.json', item_definition())
    # sanity: every coordinate inside the model limits, every rotation within +-45
    for i in range(POSES):
        for e in tentacles(i / POSES) + rod_parts(True):
            for v in e['from'] + e['to']:
                assert -16 <= v <= 32, v
            if 'rotation' in e:
                assert -45 <= e['rotation']['angle'] <= 45
    print("Kraken's Grasp: base %d elements, %d poses x %d-%d tentacle elements" % (len(rod_parts()), POSES, min(sizes), max(sizes)))


if __name__ == '__main__':
    build()
