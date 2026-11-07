"""Octo Rig chestplate skin: textures + item models + item definitions, and a preview render.
Usage: python -I octo_rig_build.py <assets out dir> <preview.png>
Writes assets/elytro/{textures/item/octo_*.png, models/item/octo_*.json, items/octo_*.json}.

Parts (all drawn by ItemDisplays, NONE transform, model px 8 = display origin):
  octo_segment  arm tube, y 0..1 block along +Y, octagonal, brass collar at its base
  octo_claw     four-finger claw, wrist at y 0, fingers close at ~0.9 block (scale it down)
  octo_hub      back housing + waist belt, origin = body centre at the hub's height
  octo_rig      skin item (inventory icon + held)
"""
import json, math, os, sys
import numpy as np
from PIL import Image

OUT, PREVIEW = sys.argv[1], sys.argv[2]
TEX = os.path.join(OUT, 'elytro', 'textures', 'item')
MOD = os.path.join(OUT, 'elytro', 'models', 'item')
ITM = os.path.join(OUT, 'elytro', 'items')
for d in (TEX, MOD, ITM):
    os.makedirs(d, exist_ok=True)

S = 32  # px per texture

# ---------------------------------------------------------------- textures
TEXTURES = {}


def save(name, a):
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    img.save(os.path.join(TEX, 'octo_%s.png' % name))
    TEXTURES[name] = img


def tube_shade(u):
    """Cylinder-ish shading across a face: dark edges, bright band a third in."""
    return 0.62 + 0.5 * math.exp(-((u - 0.34) / 0.2) ** 2) + 0.12 * math.sin(math.pi * u)


def metal():
    a = np.zeros((S, S, 4), float)
    base = np.array([74, 79, 90])
    for y in range(S):
        for x in range(S):
            u = (x + 0.5) / S
            c = base * tube_shade(u)
            # panel seams: dark line with a lit line under it
            if y in (10, 21):
                c = base * 0.38
            elif y in (11, 22):
                c = c * 1.18
            a[y, x, :3] = c
    a[..., 3] = 255
    save('metal', a)


def brass():
    a = np.zeros((S, S, 4), float)
    base = np.array([182, 136, 64])
    for y in range(S):
        for x in range(S):
            u = (x + 0.5) / S
            c = base * tube_shade(u)
            if y in (7, 8, 23, 24):
                c = c * 0.55
            a[y, x, :3] = c
    a[..., 3] = 255
    save('brass', a)


def claw():
    a = np.zeros((S, S, 4), float)
    base = np.array([50, 53, 61])
    for y in range(S):
        for x in range(S):
            u = (x + 0.5) / S
            v = (y + 0.5) / S
            c = base * (0.75 + 0.55 * math.exp(-((u - 0.3) / 0.16) ** 2))
            # bright sharpened edge toward the top (finger tip end)
            c = c + np.array([60, 62, 70]) * max(0.0, 1 - v * 3.2) * (0.6 + 0.4 * (u < 0.5))
            if x in (0, S - 1):
                c = c * 0.6
            a[y, x, :3] = c
    a[..., 3] = 255
    save('claw', a)


def glow():
    a = np.zeros((S, S, 4), float)
    for y in range(S):
        for x in range(S):
            u = (x + 0.5) / S
            v = (y + 0.5) / S
            k = 1 - 0.55 * ((2 * u - 1) ** 2 + (2 * v - 1) ** 2) / 2
            a[y, x, :3] = (96 * k + 20, 230 * k, 70 * k)  # green core (farm look, 2026-11-07)
    a[..., 3] = 255
    save('glow', a)


def plate():
    a = np.zeros((S, S, 4), float)
    base = np.array([58, 62, 72])
    for y in range(S):
        for x in range(S):
            v = (y + 0.5) / S
            c = base * (1.15 - 0.4 * v)
            if x < 2 or x >= S - 2 or y < 2 or y >= S - 2:
                c = np.array([170, 126, 58]) * (1.1 - 0.4 * v)
            a[y, x, :3] = c
    for (rx, ry) in ((5, 5), (S - 6, 5), (5, S - 6), (S - 6, S - 6)):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if abs(dx) + abs(dy) < 2:
                    a[ry + dy, rx + dx, :3] = (200, 160, 86) if (dx, dy) != (1, 1) else (90, 66, 30)
    a[..., 3] = 255
    save('plate', a)


metal(); brass(); claw(); glow(); plate()
TEXREF = {k: 'elytro:item/octo_' + k for k in ('metal', 'brass', 'claw', 'glow', 'plate')}

# ---------------------------------------------------------------- model parts
FULLUV = [0, 0, 16, 16]


def box(frm, to, tex, rot=None, light=0, faces='nsewud'):
    names = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'u': 'up', 'd': 'down'}
    e = {'from': [round(v, 4) for v in frm], 'to': [round(v, 4) for v in to],
         'faces': {names[k]: {'texture': '#' + tex, 'uv': FULLUV} for k in faces}}
    if rot:
        e['rotation'] = rot
    if light:
        e['light_emission'] = light
    return e


def octo(cx, cz, r, y0, y1, tex, light=0):
    """Octagonal prism: a box plus the same box turned 45 deg about Y."""
    a = box((cx - r, y0, cz - r), (cx + r, y1, cz + r), tex, light=light)
    b = box((cx - r, y0, cz - r), (cx + r, y1, cz + r), tex, light=light,
            rot={'angle': 45, 'axis': 'y', 'origin': [cx, 8, cz]})
    return [a, b]


def segment_elements():
    return octo(8, 8, 3, 8, 24, 'metal') + octo(8, 8, 3.7, 8, 10.5, 'brass')


def finger(sx, sz, base_len=6.0, tip_len=5.0):
    """One finger leaning out toward (sx, sz) then hooking back in. sx/sz in {-1,0,1}."""
    out = []
    a = 22.5
    if sx:
        ox = 8 + sx * 3
        axis, ang = 'z', -a * sx          # right-handed about z: +angle leans toward -x
        base = box((ox - 1, 12.5, 7), (ox + 1, 12.5 + base_len, 9), 'claw',
                   rot={'angle': ang, 'axis': axis, 'origin': [ox, 12.5, 8]})
        tx = ox + sx * base_len * math.sin(math.radians(a))
        ty = 12.5 + base_len * math.cos(math.radians(a))
        tip = box((tx - 0.75, ty - 0.4, 7.25), (tx + 0.75, ty + tip_len, 8.75), 'claw',
                  rot={'angle': -ang, 'axis': axis, 'origin': [tx, ty, 8]})
    else:
        oz = 8 + sz * 3
        axis, ang = 'x', a * sz           # right-handed about x: +angle leans toward +z
        base = box((7, 12.5, oz - 1), (9, 12.5 + base_len, oz + 1), 'claw',
                   rot={'angle': ang, 'axis': axis, 'origin': [8, 12.5, oz]})
        tz = oz + sz * base_len * math.sin(math.radians(a))
        ty = 12.5 + base_len * math.cos(math.radians(a))
        tip = box((7.25, ty - 0.4, tz - 0.75), (8.75, ty + tip_len, tz + 0.75), 'claw',
                  rot={'angle': -ang, 'axis': axis, 'origin': [8, ty, tz]})
    out += [base, tip]
    return out


def claw_elements():
    e = octo(8, 8, 3, 8, 12.5, 'claw')                    # wrist cup
    e += octo(8, 8, 3.45, 9.6, 10.6, 'glow', light=15)     # red light band
    e += octo(8, 8, 3.6, 12, 13.2, 'brass')                # palm collar
    for sx, sz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        e += finger(sx, sz)
    return e


# Hub: origin = body centre at hub height. Body frame: +z = forward, so the back is -z.
# Two fits: over a chestplate (armour layer = torso + 1 px each side: 10 x 6 px) and over a bare
# torso (skin jacket layer = torso + 0.25 px: 8.5 x 4.5 px). The plugin picks one per tick.
FITS = {'armor': (5.0, 3.0), 'bare': (4.25, 2.25)}   # half width, half depth of the torso in px
CLEAR = 0.08                                         # gap between torso and belt / plate
SOCKETS = [(-3.3, 1.6), (3.3, 1.6), (-3.3, -2.3), (3.3, -2.3)]   # (x, y) px from hub centre
BACK = 8 - FITS['armor'][1] - CLEAR                  # armour fit back surface (sockets are set for this)


def hub_elements(fit='armor'):
    hw, hd = FITS[fit]
    back = 8 - hd - CLEAR
    e = [box((3, 3.5, back - 1.2), (13, 11.5, back), 'plate')]                 # back plate
    e += [box((6.6, 4.5, back - 2.2), (9.4, 12.5, back - 1.2), 'metal')]       # spine housing
    for sx, sy in SOCKETS:
        cx, cy = 8 + sx, 8 + sy
        e += [box((cx - 1.8, cy - 1.8, back - 3.2), (cx + 1.8, cy + 1.8, back - 1.2), 'brass')]
        e += [box((cx - 1.0, cy - 1.0, back - 3.5), (cx + 1.0, cy + 1.0, back - 3.1), 'glow', light=15,
                  faces='nsewd')]
    # belt hugging the torso, below the plate centre
    y0, y1, th = 6.4, 8.6, 0.15
    x0, x1 = 8 - hw - CLEAR - th, 8 + hw + CLEAR + th
    z0, z1 = 8 - hd - CLEAR - th, 8 + hd + CLEAR + th
    e += [box((x0, y0, z0), (x1, y1, z0 + th), 'brass')]                        # back strap
    e += [box((x0, y0, z1 - th), (x1, y1, z1), 'brass')]                        # front strap
    e += [box((x0, y0, z0), (x0 + th, y1, z1), 'brass')]
    e += [box((x1 - th, y0, z0), (x1, y1, z1), 'brass')]
    e += [box((6.6, y0 - 0.3, z1 - 0.1), (9.4, y1 + 0.3, z1 + 0.3), 'plate')]   # buckle
    return e


def icon_elements():
    """Skin item: a short arm with the claw, standing on its own (model px 0..32 range)."""
    cl = []
    for el in claw_elements():
        el = json.loads(json.dumps(el))
        el['from'][1] -= 8; el['to'][1] -= 8
        if 'rotation' in el:
            el['rotation']['origin'][1] -= 8
        cl.append(el)
    seg = []
    for el in octo(8, 8, 3, -6, 0.5, 'metal') + octo(8, 8, 3.7, -2, 0.5, 'brass'):
        seg.append(el)
    return seg + cl


def model(name, elements, display=None):
    m = {'textures': dict(TEXREF, particle=TEXREF['metal']), 'elements': elements}
    if display:
        m['display'] = display
    json.dump(m, open(os.path.join(MOD, name + '.json'), 'w'), indent=1)


def item_def(name, model_name):
    json.dump({'model': {'type': 'minecraft:model', 'model': 'elytro:item/' + model_name}},
              open(os.path.join(ITM, name + '.json'), 'w'), indent=1)


ICON_DISPLAY = {
    'gui': {'rotation': [200, 35, 0], 'translation': [0, 0, 0], 'scale': [0.62, 0.62, 0.62]},
    'fixed': {'rotation': [180, 0, 0], 'translation': [0, 0, 0], 'scale': [0.7, 0.7, 0.7]},
    'ground': {'rotation': [180, 0, 0], 'translation': [0, 3, 0], 'scale': [0.4, 0.4, 0.4]},
    'thirdperson_righthand': {'rotation': [100, 0, 0], 'translation': [0, 2, 0], 'scale': [0.45, 0.45, 0.45]},
    'thirdperson_lefthand': {'rotation': [100, 0, 0], 'translation': [0, 2, 0], 'scale': [0.45, 0.45, 0.45]},
    'firstperson_righthand': {'rotation': [160, -20, 10], 'translation': [0, 4, 0], 'scale': [0.5, 0.5, 0.5]},
    'firstperson_lefthand': {'rotation': [160, 20, -10], 'translation': [0, 4, 0], 'scale': [0.5, 0.5, 0.5]},
}

SEG, CLAW, HUB, ICON = segment_elements(), claw_elements(), hub_elements(), icon_elements()
model('octo_segment', SEG)
model('octo_claw', CLAW)
model('octo_hub', HUB)
model('octo_hub_bare', hub_elements('bare'))
model('octo_rig', ICON, ICON_DISPLAY)
for n in ('octo_segment', 'octo_claw', 'octo_hub', 'octo_hub_bare', 'octo_rig'):
    item_def(n, n)

# ---------------------------------------------------------------- pose (mirrors the plugin)
# Body frame: x = player's right, y = up, z = forward. Feet at origin.
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rig_params.json')))


def v(*a):
    return np.array(a, float)


def bezier(p0, p1, p2, p3, t):
    m = 1 - t
    return m ** 3 * p0 + 3 * m * m * t * p1 + 3 * m * t * t * p2 + t ** 3 * p3


def arm_points(leg, sock, tip, aim):
    """Shoulder->tip curve, resampled to equal arc length. Returns segment joints + claw base."""
    side = 1 if leg['home'][0] > 0 else -1
    p0 = sock
    p1 = sock + v(side * P['outward'], P['rise'], P['front_lean'] if leg.get('front') else -P['backward'])
    p2 = tip - aim * P['tip_pull']
    ts = np.linspace(0, 1, 64)
    pts = np.array([bezier(p0, p1, p2, tip, t) for t in ts])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    L = d[-1]
    claw_len = P['claw_scale'] * 14.6 / 16
    n = P['segments']
    targets = np.linspace(0, L - claw_len, n + 1)
    joints = [pts[np.searchsorted(d, s).clip(0, 63)] for s in targets]
    return joints, L


def look_mat(a, b, w):
    """Matrix taking model +Y (0..1) onto a->b with width scale w."""
    d = b - a
    ln = np.linalg.norm(d)
    y = d / ln
    ref = v(0, 0, 1) if abs(y[2]) < 0.9 else v(1, 0, 0)
    x = np.cross(y, ref); x /= np.linalg.norm(x)
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0] = x * w; M[:3, 1] = y * ln; M[:3, 2] = z * w; M[:3, 3] = a
    return M


def pose():
    inst = []
    hub = P['hub']
    H = np.eye(4); H[:3, 3] = v(0, hub[1], 0)
    inst.append((HUB, H @ np.diag([1, 1, 1, 1.0])))
    for i, leg in enumerate(P['legs']):
        sock = v(*leg['socket'])
        tip = v(leg['home'][0], 0, leg['home'][2])
        aim = v(0, -1, 0)
        if i < 2 and P.get('preview_raise'):
            tip = sock + v(np.sign(leg['home'][0]) * P['raise'][0], P['raise'][1], P['raise'][2])
            aim = v(np.sign(leg['home'][0]) * 0.3, 0.35, 1); aim /= np.linalg.norm(aim)
        joints, L = arm_points(leg, sock, tip, aim)
        n = len(joints) - 1
        for k in range(n):
            w = P['width_base'] + (P['width_tip'] - P['width_base']) * k / max(1, n - 1)
            inst.append((SEG, look_mat(joints[k], joints[k + 1] + (joints[k + 1] - joints[k]) * 0.04, w)))
        cb = joints[-1]
        inst.append((CLAW, look_mat(cb, cb + (tip - cb) / np.linalg.norm(tip - cb) * P['claw_scale'],
                                    P['claw_scale']) @ np.diag([1, 1 / 1, 1, 1])))
    return inst


# ---------------------------------------------------------------- preview render
FACES = {
    'north': (lambda f, t: [(t[0], t[1], f[2]), (f[0], t[1], f[2]), (f[0], f[1], f[2]), (t[0], f[1], f[2])]),
    'south': (lambda f, t: [(f[0], t[1], t[2]), (t[0], t[1], t[2]), (t[0], f[1], t[2]), (f[0], f[1], t[2])]),
    'west': (lambda f, t: [(f[0], t[1], f[2]), (f[0], t[1], t[2]), (f[0], f[1], t[2]), (f[0], f[1], f[2])]),
    'east': (lambda f, t: [(t[0], t[1], t[2]), (t[0], t[1], f[2]), (t[0], f[1], f[2]), (t[0], f[1], t[2])]),
    'up': (lambda f, t: [(f[0], t[1], f[2]), (t[0], t[1], f[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2])]),
    'down': (lambda f, t: [(f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], f[1], f[2]), (f[0], f[1], f[2])]),
}
LIGHT = v(0.35, 0.85, 0.4); LIGHT /= np.linalg.norm(LIGHT)


def rot_point(p, rot):
    if not rot:
        return p
    a = math.radians(rot['angle'])
    o = rot['origin']
    x, y, z = p[0] - o[0], p[1] - o[1], p[2] - o[2]
    c, s = math.cos(a), math.sin(a)
    if rot['axis'] == 'y':
        x, z = x * c + z * s, -x * s + z * c
    elif rot['axis'] == 'x':
        y, z = y * c - z * s, y * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    return (x + o[0], y + o[1], z + o[2])


def solid_box(frm, to, rgb):
    """Plain coloured box for the stand-in player, in block units."""
    return {'from': frm, 'to': to, 'col': rgb}


PLAYER = [solid_box((-0.25, 0.0, -0.125), (0.0, 0.75, 0.125), (52, 70, 120)),
          solid_box((0.0, 0.0, -0.125), (0.25, 0.75, 0.125), (52, 70, 120)),
          solid_box((-0.3125, 0.75, -0.1875), (0.3125, 1.5, 0.1875), (96, 190, 205)),
          solid_box((-0.5, 0.75, -0.125), (-0.25, 1.5, 0.125), (200, 160, 130)),
          solid_box((0.25, 0.75, -0.125), (0.5, 1.5, 0.125), (200, 160, 130)),
          solid_box((-0.25, 1.5, -0.25), (0.25, 2.0, 0.25), (200, 160, 130))]


def render(inst, path, yaw=210, pitch=18, size=900, span=5.2, centre=(0, 1.0, 0), ground=True, player=True):
    W = H = size
    img = np.zeros((H, W, 3), float); img[:] = (38, 34, 46)
    zbuf = np.full((H, W), -1e9)
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    sc = size / span

    def proj(p):
        x, y, z = p[0] - centre[0], p[1] - centre[1], p[2] - centre[2]
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return (W / 2 + x * sc, H / 2 - y * sc, z)

    texarr = {k: np.asarray(t.convert('RGBA'), float) for k, t in TEXTURES.items()}

    def tri_fill(P3, uvq, sampler, shade):
        for tri in ((0, 1, 2), (0, 2, 3)):
            (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = (P3[i] for i in tri)
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
            vv = a * v0 + b * v1 + c * v2
            col = sampler(u, vv)
            sub_z = zbuf[miny:maxy, minx:maxx]
            ok = inside & (z > sub_z)
            sub = img[miny:maxy, minx:maxx]
            sub[ok] = col[ok] * shade
            sub_z[ok] = z[ok]

    def quad_shade(pw, emissive=False):
        n = np.cross(pw[1] - pw[0], pw[3] - pw[0])
        nn = np.linalg.norm(n)
        if emissive or nn < 1e-12:
            return 1.0
        n = n / nn
        return 0.55 + 0.45 * abs(float(n @ LIGHT))

    if ground:
        g = [v(-3, 0, -3), v(3, 0, -3), v(3, 0, 3), v(-3, 0, 3)]
        tri_fill([proj(p) for p in g], [(0, 0), (1, 0), (1, 1), (0, 1)],
                 lambda u, vv: np.stack([np.where(((u * 12).astype(int) + (vv * 12).astype(int)) % 2, 70, 62)] * 3, -1)
                 * np.array([0.9, 1.15, 0.8]), 1.0)
    for b in (PLAYER if player else []):
        for fn, corners in FACES.items():
            pw = [v(*c) for c in corners(b['from'], b['to'])]
            col = np.array(b['col'], float)
            tri_fill([proj(p) for p in pw], [(0, 0), (1, 0), (1, 1), (0, 1)],
                     lambda u, vv, col=col: np.broadcast_to(col, u.shape + (3,)), quad_shade(pw))
    for elements, M in inst:
        for e in elements:
            for fn, face in e['faces'].items():
                pts = [rot_point(c, e.get('rotation')) for c in FACES[fn](e['from'], e['to'])]
                # model px -> display-local blocks (NONE transform centres px 8 on the origin)
                pw = [(M @ np.r_[(np.array(p) - 8) / 16, 1])[:3] for p in pts]
                tex = texarr[face['texture'][1:]]
                th, tw = tex.shape[:2]
                tri_fill([proj(p) for p in pw], [(0, 0), (1, 0), (1, 1), (0, 1)],
                         lambda u, vv, tex=tex: tex[np.clip((vv * th).astype(int), 0, th - 1),
                                                    np.clip((u * tw).astype(int), 0, tw - 1)][..., :3],
                         quad_shade(pw, e.get('light_emission', 0) > 0))
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(path)


inst = pose()
render(inst, PREVIEW)
render(inst, PREVIEW.replace('.png', '_back.png'), yaw=20, pitch=22)
render(inst, PREVIEW.replace('.png', '_side.png'), yaw=95, pitch=8)
P['preview_raise'] = True
render(pose(), PREVIEW.replace('.png', '_idle.png'), yaw=200, pitch=14)
# close-ups of the parts
render([(CLAW, np.diag([1.0, 1, 1, 1]))], PREVIEW.replace('.png', '_claw.png'), yaw=30, pitch=25,
       span=1.6, centre=(0, 0.45, 0), ground=False, player=False)
render([(SEG, np.eye(4))], PREVIEW.replace('.png', '_seg.png'), yaw=30, pitch=25, span=1.6,
       centre=(0, 0.5, 0), ground=False, player=False)
render(inst, PREVIEW.replace('.png', '_behind.png'), yaw=200, pitch=20)
P['preview_raise'] = True
render(pose(), PREVIEW.replace('.png', '_behind_idle.png'), yaw=200, pitch=20)
print('ok')
