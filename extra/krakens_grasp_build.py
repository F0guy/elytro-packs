"""Kraken's Grasp - a fishing rod skin (rare fishing-event reward).

Three crimson tentacles grip a glowing pearl at the butt of a driftwood rod and coil up the
shaft, writhing slowly (32 poses picked by the item model's random+wobble time, the same trick
as the Eureka and Singularity skins). The pearl shimmers (animated texture) and glows brighter
while the rod is cast. Inventories and item frames show a flat 32x32 icon instead.

The model is built standing up (rod along +y); the display transforms tilt it 45 degrees so it
lies where the vanilla rod sprite does, which keeps the fishing line on the rod tip. That frees
each element's own rotation for the tentacle segments.

Writes into ./assets/elytro (this folder):
  items/krakens_grasp.json
  models/item/krakens_grasp_base.json, krakens_grasp_base_cast.json, krakens_grasp_icon.json
  models/item/krakens_grasp/writhe_00..31.json
  textures/item/krakens_grasp.png (+ .mcmeta), krakens_grasp_icon.png
Usage: python krakens_grasp_build.py [--preview out.png]
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')
POSES = 32
TEX = 'elytro:item/krakens_grasp'

# ---------------------------------------------------------------- texture
# 64x64, 8x8-pixel swatches (2x2 uv units each). (column, row) -> material
SW = {
    'wood': (0, 0), 'wood_light': (1, 0), 'grip': (2, 0), 'brass': (3, 0), 'brass_dark': (4, 0),
    'tentacle': (5, 0), 'tentacle_tip': (6, 0), 'sucker': (7, 0),
    'pearl': (0, 1), 'pearl_shade': (1, 1), 'barnacle': (2, 1), 'silver': (3, 1), 'under': (5, 1),
}
FRAMES = 8


def texture():
    rnd = random.Random(5)
    frames = []
    for f in range(FRAMES):
        im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        px = im.load()

        def fill(name, fn):
            cx, cy = SW[name]
            for y in range(8):
                for x in range(8):
                    px[cx * 8 + x, cy * 8 + y] = fn(x, y)

        def mix(a, b, t):
            return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)

        noise = [[rnd.random() for _ in range(8)] for _ in range(8)]
        # driftwood: dark sea-teal with grain running along the rod
        fill('wood', lambda x, y: mix((34, 58, 60), (58, 86, 84), 0.35 * noise[y][x] + (0.35 if x in (2, 5) else 0)))
        fill('wood_light', lambda x, y: mix((70, 102, 98), (98, 132, 124), noise[y][x] * 0.6 + (0.3 if x == 3 else 0)))
        # grip: dark plum leather wrapped on the diagonal
        fill('grip', lambda x, y: mix((42, 22, 40), (78, 40, 66), 0.75 if (x + y) % 4 == 0 else 0.25 * noise[y][x]))
        fill('brass', lambda x, y: mix((150, 112, 50), (222, 184, 98), (1 - y / 7) * 0.8 + 0.2 * noise[y][x]))
        fill('brass_dark', lambda x, y: mix((70, 50, 24), (120, 88, 40), noise[y][x] * 0.7))
        # tentacle: deep crimson-violet, mottled with darker spots
        fill('tentacle', lambda x, y: mix((88, 18, 46), (150, 40, 82), 0.25 + 0.5 * noise[y][x]) if noise[y][x] > 0.18 else (58, 10, 34, 255))
        fill('tentacle_tip', lambda x, y: mix((150, 46, 84), (206, 92, 128), noise[y][x] * 0.7))
        # suckers: pale coral rings that pulse a little brighter with the pearl
        pulse = 0.5 + 0.5 * math.sin(f / FRAMES * math.tau)

        def sucker(x, y):
            r = math.hypot(x - 3.5, y - 3.5)
            ring = (232, 160, 178) if 1.6 < r < 3.1 else (184, 98, 126) if r <= 1.6 else (150, 40, 82)
            return mix(ring, (255, 214, 226), 0.25 * pulse if r < 3.1 else 0)
        fill('sucker', sucker)
        fill('under', lambda x, y: mix((176, 86, 116), (214, 132, 152), noise[y][x] * 0.6))

        # the pearl: iridescent white with a sheen that sweeps across it frame by frame
        def pearl(x, y, shade=0.0):
            sweep = math.sin((x + y) * 0.55 - f / FRAMES * math.tau)
            base = mix((244, 236, 255), (206, 236, 250), 0.5 + 0.5 * sweep)
            tint = mix(base[:3], (226, 196, 250), 0.5 + 0.5 * math.sin(x * 0.7 + f / FRAMES * math.tau * 2))
            spark = 1 if (x, y) == (2, 2) else 0
            c = mix(tint[:3], (255, 255, 255), 0.6 * spark)
            return mix(c[:3], (150, 120, 190), shade)
        fill('pearl', lambda x, y: pearl(x, y))
        fill('pearl_shade', lambda x, y: pearl(x, y, 0.35))
        fill('barnacle', lambda x, y: mix((118, 120, 112), (176, 178, 166), noise[y][x]) if (x * 3 + y * 5) % 7 else (60, 62, 58, 255))
        fill('silver', lambda x, y: mix((150, 160, 170), (226, 232, 238), 1 - y / 7))
        frames.append(im)
    sheet = Image.new('RGBA', (64, 64 * FRAMES))
    for i, im in enumerate(frames):
        sheet.paste(im, (0, 64 * i))
    return sheet


def uv(name, face_w=2.0, face_h=2.0):
    """A uv rect inside a swatch, inset so neighbours never bleed in."""
    cx, cy = SW[name]
    u0, v0 = cx * 2 + 0.2, cy * 2 + 0.2
    return [round(u0, 3), round(v0, 3), round(u0 + min(1.6, face_w), 3), round(v0 + min(1.6, face_h), 3)]


# ---------------------------------------------------------------- geometry helpers

def box(frm, to, mat, rot=None, light=0, faces_mat=None):
    """An element: [frm, to] in rod-local units, all faces `mat` (per-face overrides in faces_mat)."""
    frm = [round(v, 3) for v in frm]
    to = [round(v, 3) for v in to]
    faces = {}
    for f in ('north', 'south', 'east', 'west', 'up', 'down'):
        m = (faces_mat or {}).get(f, mat)
        faces[f] = {'uv': uv(m), 'texture': '#0'}
    e = {'from': frm, 'to': to, 'faces': faces}
    if rot:
        e['rotation'] = rot
    if light:
        e['light_emission'] = light
    return e


def cube_at(c, size, mat, length=None, yaw=0.0, light=0, faces_mat=None):
    """A cube centred on c; `length` stretches it along x before turning it `yaw` degrees about y."""
    sx = (length or size) / 2
    s = size / 2
    frm = [c[0] - sx, c[1] - s, c[2] - s]
    to = [c[0] + sx, c[1] + s, c[2] + s]
    # a long axis turned by yaw: fold the angle into [-45, 45] by swapping x/z extents
    a = ((yaw + 45) % 90) - 45
    if length and abs(((yaw + 45) % 180) - 45) > 45:
        frm = [c[0] - s, c[1] - s, c[2] - sx]
        to = [c[0] + s, c[1] + s, c[2] + sx]
    rot = {'angle': round(a, 3), 'axis': 'y', 'origin': [round(v, 3) for v in c]} if abs(a) > 0.5 else None
    return box(frm, to, mat, rot, light, faces_mat)


AXIS_X, AXIS_Z = 8.0, 8.0


def rod_parts(cast=False):
    els = []
    # the pearl at the butt, gripped by the tentacles (three crossed slabs read as a sphere)
    pl = 15 if cast else 10
    pc = (AXIS_X, -5.4, AXIS_Z)
    els.append(cube_at(pc, 3.1, 'pearl', light=pl))
    for dims in ((3.8, 2.4, 2.4), (2.4, 3.8, 2.4), (2.4, 2.4, 3.8)):
        els.append(box([pc[0] - dims[0] / 2, pc[1] - dims[1] / 2, pc[2] - dims[2] / 2],
                       [pc[0] + dims[0] / 2, pc[1] + dims[1] / 2, pc[2] + dims[2] / 2], 'pearl', light=pl,
                       faces_mat={'down': 'pearl_shade', 'east': 'pearl_shade'}))
    # brass cup the pearl sits in, the grip with two bands, a reel, guides, the shaft
    els.append(box([6.9, -3.5, 6.9], [9.1, -3.0, 9.1], 'brass'))
    els.append(box([6.8, -3.0, 6.8], [9.2, 3.0, 9.2], 'grip'))
    for y in (-1.6, 1.6):
        els.append(box([6.65, y - 0.3, 6.65], [9.35, y + 0.3, 9.35], 'brass'))
    els.append(box([7.0, 3.0, 7.0], [9.0, 3.6, 9.0], 'brass_dark'))
    # reel: a drum on the side with a little crank
    els.append(box([9.0, 3.6, 7.0], [10.8, 6.0, 9.0], 'brass', faces_mat={'east': 'brass_dark', 'west': 'brass_dark'}))
    els.append(box([10.8, 4.6, 7.8], [11.6, 5.0, 8.2], 'brass_dark'))
    els.append(box([11.2, 4.6, 8.2], [11.6, 5.0, 9.4], 'silver'))
    # shaft: thick near the reel, tapering to the tip
    els.append(box([7.25, 3.6, 7.25], [8.75, 9.0, 8.75], 'wood'))
    els.append(box([7.4, 9.0, 7.4], [8.6, 15.0, 8.6], 'wood', faces_mat={'south': 'wood_light'}))
    els.append(box([7.55, 15.0, 7.55], [8.45, 21.0, 8.45], 'wood_light'))
    for y in (9.0, 15.0):
        els.append(box([7.15, y - 0.25, 7.15], [8.85, y + 0.25, 8.85], 'brass'))
    # line guides: small silver loops standing off the top of the rod
    for y in (7.0, 12.0, 16.5, 20.2):
        els.append(box([6.55, y, 7.85], [7.25, y + 0.35, 8.15], 'silver'))
    els.append(box([7.6, 21.0, 7.6], [8.4, 21.5, 8.4], 'silver'))
    # barnacles crusted on the grip
    for (x, y, z, s) in ((6.6, -1.0, 8.3, 0.7), (9.3, 0.4, 7.6, 0.6), (8.4, 2.4, 9.3, 0.55), (7.4, -2.4, 6.6, 0.5)):
        els.append(cube_at((x, y, z), s, 'barnacle'))
    return els


def tentacle_path(k, u):
    """Points along tentacle k (0..2) at writhe parameter u (0..1): grips the pearl, coils up
    the shaft, then curls off it at the tip. All three move out of step with each other."""
    phase = math.tau * u + k * math.tau / 3
    twist = math.radians(38) * math.sin(phase)                  # the coil winds and unwinds
    curl = 0.5 + 0.5 * math.sin(phase + 1.1)                    # the tip curls tighter and looser
    start = k * 120 + 30
    top = (15.5, 11.5, 8.0)[k]                                  # where each one leaves the shaft
    pts = []
    # 1. gripping the pearl like fingers: up from below it, hugging its side, onto the grip
    for i in range(8):
        t = i / 7
        a = math.radians(start - 25 + 25 * t)
        y = -7.6 + 4.8 * t
        r = 1.0 + 1.35 * math.sin(math.pi * min(1, 0.15 + t * 0.95))
        pts.append((AXIS_X + r * math.cos(a), y, AXIS_Z + r * math.sin(a), 0.95 - 0.08 * t))
    # 2. coiling up the shaft (radius shrinks as the shaft thins)
    turns = 1.0
    n = 26
    for i in range(1, n + 1):
        t = i / n
        y = -2.8 + (top + 2.8) * t
        a = math.radians(start) + t * turns * math.tau + twist * t
        r = 1.8 - 0.55 * t if y < 9 else 1.3 - 0.35 * t
        r += 0.15 * math.sin(t * 9 + phase)                     # a little ripple along it
        pts.append((AXIS_X + r * math.cos(a), y, AXIS_Z + r * math.sin(a), 0.86 - 0.42 * t))
    # 3. the tip curls outward off the shaft in a shrinking spiral
    x0, y0, z0, _ = pts[-1]
    a0 = math.atan2(z0 - AXIS_Z, x0 - AXIS_X)
    out = (math.cos(a0), math.sin(a0))
    for i in range(1, 11):
        t = i / 10
        ang = t * (1.4 + 1.8 * curl) * math.pi
        rad = 1.6 * (1 - 0.6 * t)
        d = rad * math.sin(ang)
        h = rad * (1 - math.cos(ang)) * 0.8
        pts.append((x0 + out[0] * d, y0 + 0.6 * t + h * (0.6 - t), z0 + out[1] * d, 0.44 - 0.2 * t))
    return pts


def tentacles(u):
    els = []
    for k in range(3):
        pts = tentacle_path(k, u)
        for i, (x, y, z, w) in enumerate(pts):
            nx, _, nz, _ = pts[min(i + 1, len(pts) - 1)]
            px_, _, pz, _ = pts[max(i - 1, 0)]
            yaw = math.degrees(math.atan2(-(nz - pz), nx - px_)) if (nx, nz) != (px_, pz) else 0
            mat = 'tentacle_tip' if i > len(pts) - 9 else 'tentacle'
            els.append(cube_at((x, y, z), w, mat, length=w * 1.9, yaw=yaw, faces_mat={'down': 'under'}))
            # suckers on the outside of the coil, every third segment
            if i % 3 == 1 and i < len(pts) - 3:
                a = math.atan2(z - AXIS_Z, x - AXIS_X)
                sc = (x + math.cos(a) * w * 0.48, y, z + math.sin(a) * w * 0.48)
                els.append(cube_at(sc, max(0.22, w * 0.36), 'sucker', light=3))
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
        'gui': {'rotation': [0, 0, -45], 'scale': [0.62, 0.62, 0.62]},
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
    """32x32 flat inventory icon: the rod on the diagonal, a tentacle round it, the pearl."""
    S = 8
    im = Image.new('RGBA', (32 * S, 32 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def P(x, y):
        return (x * S, y * S)
    # shaft (dark outline, then wood)
    d.line([P(7, 25), P(29, 3)], fill=(16, 26, 28, 255), width=int(3.4 * S))
    d.line([P(7, 25), P(29, 3)], fill=(58, 92, 90, 255), width=int(1.8 * S))
    d.line([P(18, 14), P(29, 3)], fill=(96, 132, 124, 255), width=int(1.0 * S))
    # grip and reel
    d.line([P(5, 27), P(11, 21)], fill=(20, 10, 18, 255), width=int(4.2 * S))
    d.line([P(5, 27), P(11, 21)], fill=(78, 40, 66, 255), width=int(2.8 * S))
    d.ellipse([P(10.5, 21), P(14.5, 25)], fill=(222, 184, 98, 255), outline=(70, 50, 24, 255), width=S)
    # tentacle coiling up the shaft
    pts = []
    for i in range(60):
        t = i / 59
        cx, cy = 7 + 13 * t, 25 - 13 * t
        off = 2.3 * math.sin(t * math.tau * 2.1) * (1 - 0.35 * t)
        pts.append(P(cx + off * 0.7, cy + off * 0.7))
    d.line(pts, fill=(40, 6, 22, 255), width=int(2.6 * S), joint='curve')
    d.line(pts, fill=(150, 40, 82, 255), width=int(1.6 * S), joint='curve')
    for i in range(4, 60, 9):
        x, y = pts[i]
        d.ellipse([x - S * 0.5, y - S * 0.5, x + S * 0.5, y + S * 0.5], fill=(240, 176, 194, 255))
    # tip curl
    cx, cy = pts[-1]
    d.arc([cx - 2.2 * S, cy - 3.4 * S, cx + 2.2 * S, cy + 1.0 * S], 200, 520, fill=(206, 92, 128, 255), width=int(1.1 * S))
    # the pearl at the butt, glowing
    d.ellipse([P(1.2, 25), P(7.8, 31.6)], fill=(30, 18, 44, 255))
    d.ellipse([P(1.9, 25.7), P(7.1, 30.9)], fill=(236, 226, 252, 255))
    d.ellipse([P(3.0, 26.6), P(4.6, 28.2)], fill=(255, 255, 255, 255))
    small = im.resize((32, 32), Image.LANCZOS)
    # snap alpha so the icon stays crisp
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
