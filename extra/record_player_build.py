"""Elytro Jukebox record player: textures + item models + item definitions, and a preview render.
Usage: python -I build.py <assets out dir> <preview.png>
Writes assets/elytro/{textures/item/record_player_*.png, models/item/record_player*.json,
items/record_player*.json}."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw

OUT, PREVIEW = sys.argv[1], sys.argv[2]
TEX = os.path.join(OUT, 'elytro', 'textures', 'item')
MOD = os.path.join(OUT, 'elytro', 'models', 'item')
ITM = os.path.join(OUT, 'elytro', 'items')
for d in (TEX, MOD, ITM):
    os.makedirs(d, exist_ok=True)

rng = np.random.default_rng(7)

# ---------------------------------------------------------------- textures

def save(name, img):
    img.save(os.path.join(TEX, 'record_player_%s.png' % name))
    return img


def wood():
    # walnut: dark warm brown with long horizontal grain streaks
    w, h = 16, 16
    a = np.zeros((h, w, 4), np.uint8)
    base = np.array([92, 56, 34], float)
    for y in range(h):
        band = 0.86 + 0.14 * math.sin(y * 1.7 + 0.6) + rng.normal(0, 0.03)
        for x in range(w):
            g = band + 0.06 * math.sin(x * 0.45 + y * 2.3) + rng.normal(0, 0.025)
            c = np.clip(base * g, 0, 255)
            a[y, x] = [*c, 255]
    for y in (3, 9, 13):
        for x in range(w):
            if rng.random() < 0.8:
                a[y, x, :3] = (a[y, x, :3] * 0.78).astype(np.uint8)
    return save('wood', Image.fromarray(a, 'RGBA'))


def wood_front():
    # front panel: wood with a gold trim line top and bottom and a dark speaker grille
    img = wood().copy()
    px = img.load()
    for x in range(16):
        px[x, 0] = (214, 170, 72, 255)
        px[x, 15] = (176, 132, 52, 255)
    for y in range(4, 12):
        for x in range(3, 13):
            on = (x + y) % 2 == 0
            px[x, y] = (40, 26, 18, 255) if on else (58, 38, 26, 255)
    for x in range(3, 13):
        px[x, 3] = (196, 152, 64, 255)
        px[x, 12] = (150, 110, 44, 255)
    return save('front', img)


def plate():
    # top deck: charcoal with a soft brushed finish and a gold pinstripe border
    a = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            v = 44 + 6 * math.sin(x * 0.9 + y * 0.15) + rng.normal(0, 2)
            a[y, x] = [v, v - 2, v + 4, 255]
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            a[y, x] = [184, 140, 58, 255]
    return save('plate', Image.fromarray(a, 'RGBA'))


def metal():
    a = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            v = 196 + 30 * math.sin(y * 0.6) + rng.normal(0, 4)
            a[y, x] = [v, v, min(255, v + 8), 255]
    return save('metal', Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def dark():
    a = np.zeros((16, 16, 4), np.uint8)
    a[..., :3] = 30
    a[..., 3] = 255
    return save('dark', Image.fromarray(a, 'RGBA'))


def disc(name, r_out, body, rim=None, vinyl=False, size=64):
    """A round cut-out disc on a square texture (transparent outside r_out, in 0..1 of half width)."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    px = img.load()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            dx, dy = (x - c) / (size / 2), (y - c) / (size / 2)
            r = math.hypot(dx, dy)
            if r > r_out:
                continue
            col = body
            if rim and r > r_out - rim[1]:
                col = rim[0]
            if vinyl:
                ang = math.atan2(dy, dx)
                groove = 0.5 + 0.5 * math.sin(r * 120)
                sheen = max(0.0, math.cos(2 * (ang - 0.7))) ** 6 * 26
                v = 16 + groove * 7 + sheen * (0.35 + 0.65 * r)
                col = (int(v), int(v), int(v + 3), 255)
                if r > r_out - 0.04:
                    col = (34, 34, 38, 255)
                if r < 0.36:
                    # the label: Elytro purple with a gold ring and a white mark so the spin shows
                    col = (142, 91, 216, 255)
                    if r > 0.31:
                        col = (214, 170, 72, 255)
                    if 0.12 < r < 0.27 and abs(ang - 1.2) < 0.32:
                        col = (240, 230, 255, 255)
                    if 0.12 < r < 0.27 and abs(ang + 1.94) < 0.18:
                        col = (214, 170, 72, 255)
                    if r < 0.05:
                        col = (20, 20, 22, 255)
            px[x, y] = col
    img.save(os.path.join(TEX, 'record_player_%s.png' % name))
    return img


TEXTURES = {
    'wood': wood(), 'front': wood_front(), 'plate': plate(), 'metal': metal(), 'dark': dark(),
    'mat': disc('mat', 0.99, (58, 58, 64, 255), rim=((150, 150, 158, 255), 0.07)),
    'vinyl': disc('vinyl', 0.99, (20, 20, 22, 255), vinyl=True),
}
# translucent-free empty texture for faces we want invisible is just "no face"

# ---------------------------------------------------------------- model parts

def box(frm, to, tex, faces='nsewud', rot=None, uv=None):
    f = {}
    names = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'u': 'up', 'd': 'down'}
    for k in faces:
        t = tex if isinstance(tex, str) else tex.get(k, tex.get('*'))
        face = {'texture': '#' + t}
        if uv and k in uv:
            face['uv'] = uv[k]
        f[names[k]] = face
    e = {'from': frm, 'to': to, 'faces': f}
    if rot:
        e['rotation'] = rot
    return e


# Platter centre in the full model (x, z); the platter model is built around (8, 8).
PCX, PCZ = 8.0, 8.0
DECK = 7.0  # top of the cabinet


def platter_elements(cx, cz):
    """Mat + record + spindle around (cx, cz): round cut-out textures on thin boxes, top/bottom faces only."""
    r_mat, r_rec = 6.3, 5.9
    return [
        box([cx - r_mat, DECK, cz - r_mat], [cx + r_mat, DECK + 0.4, cz + r_mat], 'mat', faces='ud'),
        box([cx - r_rec, DECK + 0.45, cz - r_rec], [cx + r_rec, DECK + 0.7, cz + r_rec], 'vinyl', faces='ud'),
        box([cx - 0.35, DECK + 0.7, cz - 0.35], [cx + 0.35, DECK + 1.3, cz + 0.35], 'metal'),
    ]


def body_elements():
    els = []
    for (x, z) in ((1, 1), (13, 1), (1, 13), (13, 13)):
        els.append(box([x, 0, z], [x + 2, 1, z + 2], 'dark'))
    els.append(box([0.5, 1, 0.5], [15.5, DECK, 15.5],
                   {'n': 'front', 'u': 'plate', '*': 'wood'}))
    # speed knob and start button on the deck, front right
    els.append(box([13.6, DECK, 1.0], [15.0, DECK + 0.8, 2.4], 'metal', faces='nsewu'))
    els.append(box([1.0, DECK, 1.0], [2.0, DECK + 0.4, 2.0], 'dark', faces='nsewu'))
    # tonearm in the back-right corner: pivot, counterweight, arm swung over the record, headshell
    els.append(box([13.3, DECK, 13.3], [15.3, DECK + 1.6, 15.3], 'metal'))
    piv = [14.3, DECK + 1.3, 14.3]
    arm_rot = {'angle': 22.5, 'axis': 'y', 'origin': piv}
    els.append(box([13.9, DECK + 1.1, 14.3], [14.7, DECK + 1.9, 15.9], 'dark', rot=arm_rot))
    els.append(box([14.05, DECK + 1.2, 6.2], [14.55, DECK + 1.6, 14.3], 'metal', rot=arm_rot))
    els.append(box([13.6, DECK + 0.8, 5.0], [15.0, DECK + 1.5, 6.5], 'dark', rot=arm_rot))
    return els


TEXREF = {k: 'elytro:item/record_player_' + k for k in ('wood', 'front', 'plate', 'metal', 'dark', 'mat', 'vinyl')}
DISPLAY = {
    'gui': {'rotation': [30, 225, 0], 'translation': [0, 0, 0], 'scale': [0.625, 0.625, 0.625]},
    'ground': {'rotation': [0, 0, 0], 'translation': [0, 3, 0], 'scale': [0.25, 0.25, 0.25]},
    'fixed': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [0.5, 0.5, 0.5]},
    'thirdperson_righthand': {'rotation': [75, 45, 0], 'translation': [0, 2.5, 0], 'scale': [0.375, 0.375, 0.375]},
    'firstperson_righthand': {'rotation': [0, 45, 0], 'translation': [0, 0, 0], 'scale': [0.4, 0.4, 0.4]},
    'firstperson_lefthand': {'rotation': [0, 225, 0], 'translation': [0, 0, 0], 'scale': [0.4, 0.4, 0.4]},
    'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [1, 1, 1]},
}


def model(name, elements, display=True):
    m = {'textures': dict(TEXREF, particle=TEXREF['wood']), 'elements': elements}
    if display:
        m['display'] = DISPLAY
    json.dump(m, open(os.path.join(MOD, name + '.json'), 'w'), indent=1)


def item_def(name, model_name):
    json.dump({'model': {'type': 'minecraft:model', 'model': 'elytro:item/' + model_name}},
              open(os.path.join(ITM, name + '.json'), 'w'), indent=1)


FULL = body_elements() + platter_elements(PCX, PCZ)
model('record_player', FULL)
model('record_player_base', body_elements(), display=False)
model('record_player_platter', platter_elements(8, 8), display=False)
item_def('record_player', 'record_player')
item_def('record_player_base', 'record_player_base')
item_def('record_player_platter', 'record_player_platter')

# ---------------------------------------------------------------- preview render

FACE_DIRS = {
    'north': ((0, 0, -1), lambda f, t: [(t[0], t[1], f[2]), (f[0], t[1], f[2]), (f[0], f[1], f[2]), (t[0], f[1], f[2])]),
    'south': ((0, 0, 1), lambda f, t: [(f[0], t[1], t[2]), (t[0], t[1], t[2]), (t[0], f[1], t[2]), (f[0], f[1], t[2])]),
    'west': ((-1, 0, 0), lambda f, t: [(f[0], t[1], f[2]), (f[0], t[1], t[2]), (f[0], f[1], t[2]), (f[0], f[1], f[2])]),
    'east': ((1, 0, 0), lambda f, t: [(t[0], t[1], t[2]), (t[0], t[1], f[2]), (t[0], f[1], f[2]), (t[0], f[1], t[2])]),
    'up': ((0, 1, 0), lambda f, t: [(f[0], t[1], f[2]), (t[0], t[1], f[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2])]),
    'down': ((0, -1, 0), lambda f, t: [(f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], f[1], f[2]), (f[0], f[1], f[2])]),
}
SHADE = {'up': 1.0, 'down': 0.5, 'north': 0.8, 'south': 0.8, 'east': 0.6, 'west': 0.6}


def rot_point(p, rot):
    if not rot:
        return p
    a = math.radians(rot['angle'])
    o = rot['origin']
    x, y, z = p[0] - o[0], p[1] - o[1], p[2] - o[2]
    if rot['axis'] == 'y':
        x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    return (x + o[0], y + o[1], z + o[2])


def render(elements, path, yaw=225, pitch=30, size=640, spin=0.0):
    W = H = size
    img = np.zeros((H, W, 3), float)
    img[:] = (38, 34, 46)
    zbuf = np.full((H, W), -1e9)
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def proj(p):
        x, y, z = p[0] - 8, p[1] - 4, p[2] - 8
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        s = size / 26
        return (W / 2 + x * s, H / 2 - y * s, z)

    texarr = {k: np.asarray(v.convert('RGBA'), float) for k, v in TEXTURES.items()}
    for e in elements:
        for fname, face in e['faces'].items():
            normal, corners = FACE_DIRS[fname]
            pts3 = [rot_point(c, e.get('rotation')) for c in corners(e['from'], e['to'])]
            P = [proj(p) for p in pts3]
            tex = texarr[face['texture'][1:]]
            th, tw = tex.shape[:2]
            uvq = [(0, 0), (1, 0), (1, 1), (0, 1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = (P[i] for i in tri)
                (u0, v0), (u1, v1), (u2, v2) = (uvq[i] for i in tri)
                den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
                if abs(den) < 1e-9:
                    continue
                minx, maxx = int(max(0, min(x0, x1, x2))), int(min(W - 1, max(x0, x1, x2)) + 1)
                miny, maxy = int(max(0, min(y0, y1, y2))), int(min(H - 1, max(y0, y1, y2)) + 1)
                if minx >= maxx or miny >= maxy:
                    continue
                xs, ys = np.meshgrid(np.arange(minx, maxx) + 0.5, np.arange(miny, maxy) + 0.5)
                a = ((y1 - y2) * (xs - x2) + (x2 - x1) * (ys - y2)) / den
                b = ((y2 - y0) * (xs - x2) + (x0 - x2) * (ys - y2)) / den
                c = 1 - a - b
                inside = (a >= 0) & (b >= 0) & (c >= 0)
                if not inside.any():
                    continue
                z = a * z0 + b * z1 + c * z2
                u = a * u0 + b * u1 + c * u2
                v = a * v0 + b * v1 + c * v2
                if spin and face['texture'] == '#vinyl':
                    uu, vv = u - 0.5, v - 0.5
                    cs, sn = math.cos(spin), math.sin(spin)
                    u, v = uu * cs - vv * sn + 0.5, uu * sn + vv * cs + 0.5
                ti = np.clip((v * th).astype(int), 0, th - 1)
                tj = np.clip((u * tw).astype(int), 0, tw - 1)
                col = tex[ti, tj]
                sub_z = zbuf[miny:maxy, minx:maxx]
                ok = inside & (col[..., 3] > 128) & (z > sub_z)
                sub_img = img[miny:maxy, minx:maxx]
                sub_img[ok] = col[ok][:, :3] * SHADE[fname]
                sub_z[ok] = z[ok]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(path)


render(FULL, PREVIEW)
render(FULL, PREVIEW.replace('.png', '_front.png'), yaw=200, pitch=22)
print('ok')
