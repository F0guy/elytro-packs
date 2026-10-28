"""Build the bug net: a 3D item model (assets/elytro/models/item/bug_net.json) and its
64x64 texture (assets/elytro/textures/item/bug_net.png), styled after a butterfly net:
a curved bamboo handle with node bands, a wrapped collar, a round pale hoop and a white
diamond-mesh bag that tapers and droops behind the hoop, see-through between the threads.

Model space: the handle runs up the y axis, the hoop stands in the x/y plane on top of it,
and the bag hangs back along -z and sags. The display transforms tilt it 45 degrees so it
sits like the vanilla fishing rod sprite (tip to the top right).
Usage: python bug_net_build.py   (then ../rebuild.ps1 to publish)
"""
import json, math, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets', 'elytro')

# ---------------------------------------------------------------- texture (64x64)
T = 64
tex = Image.new('RGBA', (T, T), (0, 0, 0, 0))
px = tex.load()

# net: diamond mesh; nothing between the threads (the game doesn't sort see-through
# faces inside one model, so a film would hide the threads behind it)
NET_REGION = (0, 0, 32, 32)
for y in range(32):
    for x in range(32):
        c = (0, 0, 0, 0)
        if (x + y) % 8 == 0 or (x - y) % 8 == 0:
            c = (246, 249, 253, 255)
        px[x, y] = c

# handle: bamboo, light left / shaded right, a node band every 12 px
for y in range(64):
    for i, x in enumerate(range(32, 36)):
        base = [(240, 208, 132), (226, 184, 104), (214, 170, 92), (182, 138, 66)][i]
        k = y % 12
        if k in (0, 1):
            base = tuple(int(v * 0.74) for v in base)
        elif k == 2:
            base = tuple(min(255, int(v * 1.08)) for v in base)
        px[x, y] = base + (255,)

# collar: a cord wrapped round the top of the handle
for y in range(16):
    for i, x in enumerate(range(40, 44)):
        dark = (x + y) % 3 == 0
        base = (132, 88, 44) if dark else (190, 140, 72)
        if i == 0:
            base = tuple(min(255, int(v * 1.12)) for v in base)
        if i == 3:
            base = tuple(int(v * 0.8) for v in base)
        px[x, y] = base + (255,)

# hoop: pale bent cane
for y in range(32):
    for i, x in enumerate(range(48, 52)):
        base = [(250, 232, 182), (240, 214, 150), (232, 202, 134), (200, 168, 104)][i]
        if y % 16 == 0:
            base = tuple(int(v * 0.86) for v in base)
        px[x, y] = base + (255,)

os.makedirs(os.path.join(ASSETS, 'textures', 'item'), exist_ok=True)
tex.save(os.path.join(ASSETS, 'textures', 'item', 'bug_net.png'))

# ---------------------------------------------------------------- model
U = 4.0  # texture px per uv unit (64 px over 16 uv)


def uv(x1, y1, x2, y2):
    return [x1 / U, y1 / U, x2 / U, y2 / U]


HANDLE = uv(32, 0, 36, 64)
HANDLE_SHORT = uv(32, 0, 36, 40)
HANDLE_END = uv(32, 0, 36, 4)
COLLAR = uv(40, 0, 44, 16)
COLLAR_END = uv(40, 0, 44, 4)
RING = uv(48, 0, 52, 16)
RING_END = uv(48, 0, 52, 2)
NET = uv(0, 0, 32, 32)
NET_HALF = uv(0, 0, 24, 32)


def box(frm, to, faces, rot=None, name=None):
    e = {'from': [round(v, 3) for v in frm], 'to': [round(v, 3) for v in to], 'faces': {}}
    for f, u in faces.items():
        e['faces'][f] = {'uv': [round(v, 3) for v in u], 'texture': '#0'}
    if rot:
        e['rotation'] = rot
    if name:
        e['name'] = name
    return e


def stick(frm, to, side, end, rot=None, name=None):
    return box(frm, to, {'north': side, 'south': side, 'east': side, 'west': side,
                         'up': end, 'down': end}, rot, name)


els = []
# handle (two lengths of cane, so the node bands keep their size)
els.append(stick([7.4, -1.0, 7.4], [8.6, 12.0, 8.6], HANDLE_SHORT, HANDLE_END, name='handle'))
els.append(stick([7.4, -14.0, 7.4], [8.6, -0.8, 8.6], HANDLE_SHORT, HANDLE_END, name='handle'))
# collar
els.append(stick([7.05, 9.8, 7.05], [8.95, 13.6, 8.95], COLLAR, COLLAR_END, name='collar'))

# hoop: an octagon standing in the y/z plane (x 7.55..8.45), inradius 6 round (y 19.4, z 8)
cy, cz, ri, t = 19.4, 8.0, 6.0, 0.45
side = 2 * ri * math.tan(math.radians(22.5)) + 0.35
hs = side / 2
for (by, bz, along_y) in ((cy - ri, cz, False), (cy + ri, cz, False),
                          (cy, cz - ri, True), (cy, cz + ri, True)):
    if along_y:
        els.append(stick([7.55, by - hs, bz - t], [8.45, by + hs, bz + t], RING, RING_END, name='hoop'))
    else:
        els.append(stick([7.55, by - t, bz - hs], [8.45, by + t, bz + hs], RING, RING_END, name='hoop'))
d = ri / math.sqrt(2)
for sy, sz in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
    py_, pz_ = cy + sy * d, cz + sz * d
    angle = 45 if sy * sz > 0 else -45
    els.append(stick([7.55, py_ - t, pz_ - hs], [8.45, py_ + t, pz_ + hs], RING, RING_END,
                     {'angle': angle, 'axis': 'x', 'origin': [8, py_, pz_]}, 'hoop'))

# bag: double-sided mesh planes (a flat element shows both its faces), out along -x from
# the hoop, narrowing and sagging; risers close each step, a cap closes the end
K = 0.8   # net uv units per model unit, so the mesh keeps one size everywhere


def net_uv(a, b):
    return [0, 0, round(min(8, a * K), 3), round(min(8, b * K), 3)]


def plane(frm, to):
    (x1, y1, z1), (x2, y2, z2) = frm, to
    if abs(y2 - y1) < 1e-6:
        f = net_uv(x2 - x1, z2 - z1); faces = {'up': f, 'down': f}
    elif abs(z2 - z1) < 1e-6:
        f = net_uv(x2 - x1, y2 - y1); faces = {'north': f, 'south': f}
    else:
        f = net_uv(z2 - z1, y2 - y1); faces = {'east': f, 'west': f}
    els.append(box(frm, to, faces, name='net'))


N = 7
x0, x_end = 7.6, -9.0
seg = []
for i in range(N):
    s = i / N
    hw = 5.5 * (1 - 0.62 * s ** 1.2)
    sag = 9.0 * s ** 1.5
    xa = x0 + (x_end - x0) * s
    xb = x0 + (x_end - x0) * (i + 1) / N
    seg.append((xa, xb, cy - hw - sag, cy + hw - sag, cz - hw, cz + hw))
for i, (xa, xb, y1, y2, z1, z2) in enumerate(seg):
    plane([xb, y2, z1], [xa, y2, z2])      # top
    plane([xb, y1, z1], [xa, y1, z2])      # bottom
    plane([xb, y1, z2], [xa, y2, z2])      # side
    plane([xb, y1, z1], [xa, y2, z1])      # other side
    if i + 1 < N:                          # riser to the next, smaller, lower step
        _, _, ny1, ny2, nz1, nz2 = seg[i + 1]
        if y2 - ny2 > 0.05:
            plane([xb, ny2, z1], [xb, y2, z2])
        if abs(ny1 - y1) > 0.05:
            plane([xb, min(y1, ny1), z1], [xb, max(y1, ny1), z2])
        lo, hi = max(y1, ny1), min(y2, ny2)
        if nz1 - z1 > 0.05 and hi > lo:
            plane([xb, lo, z1], [xb, hi, nz1])
            plane([xb, lo, nz2], [xb, hi, z2])
    else:
        plane([xb, y1, z1], [xb, y2, z2])  # the closed end
model = {
    'credit': 'Elytro bug net - elytra-packs/extra/bug_net_build.py',
    'texture_size': [64, 64],
    'textures': {'0': 'elytro:item/bug_net', 'particle': 'elytro:item/bug_net'},
    'elements': els,
    # vanilla handheld_rod angles, less 45 on z (the model stands upright; the rod
    # sprite they were made for runs corner to corner), scaled for a 39-unit model.
    # First person turned a little so you see into the net. No left-hand entries:
    # the game mirrors the right-hand ones.
    'display': {
        'thirdperson_righthand': {'rotation': [0, 90, 10], 'translation': [0, 3, 1], 'scale': [0.5, 0.5, 0.5]},
        'firstperson_righthand': {'rotation': [0, -75, -10], 'translation': [-1, 2, 1], 'scale': [0.36, 0.36, 0.36]},
        'gui': {'rotation': [0, 150, 45], 'translation': [0, 0, 0], 'scale': [0.42, 0.42, 0.42]},
        'ground': {'rotation': [0, 150, 45], 'translation': [0, 2, 0], 'scale': [0.3, 0.3, 0.3]},
        'fixed': {'rotation': [0, 150, 45], 'translation': [0, 0, 0], 'scale': [0.5, 0.5, 0.5]},
        'head': {'rotation': [0, 0, -45], 'translation': [0, 10, 0], 'scale': [0.6, 0.6, 0.6]},
    },
}


# icon, item frame and ground: scale and centre the turned model to fill the slot
def fit(view, size):
    r = model['display'][view]['rotation']

    def rot(v, a, axis):
        a = math.radians(a); c, s = math.cos(a), math.sin(a)
        x, y, z = v
        if axis == 'x':
            return (x, y * c - z * s, y * s + z * c)
        if axis == 'y':
            return (x * c + z * s, y, -x * s + z * c)
        return (x * c - y * s, x * s + y * c, z)
    pts = []
    for e in els:
        (x1, y1, z1), (x2, y2, z2) = e['from'], e['to']
        for p in ((x, y, z) for x in (x1, x2) for y in (y1, y2) for z in (z1, z2)):
            if 'rotation' in e:
                o = e['rotation']['origin']
                p = rot((p[0] - o[0], p[1] - o[1], p[2] - o[2]), e['rotation']['angle'], e['rotation']['axis'])
                p = (p[0] + o[0], p[1] + o[1], p[2] + o[2])
            p = (p[0] - 8, p[1] - 8, p[2] - 8)
            p = rot(rot(rot(p, r[2], 'z'), r[1], 'y'), r[0], 'x')   # R = Rx Ry Rz
            pts.append(p)
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    s = size / max(hi[0] - lo[0], hi[1] - lo[1])
    model['display'][view]['scale'] = [round(s, 4)] * 3
    model['display'][view]['translation'] = [round(-(lo[i] + hi[i]) / 2 * s, 3) for i in range(3)]


fit('gui', 15.5)
fit('fixed', 14)
fit('ground', 8)

os.makedirs(os.path.join(ASSETS, 'models', 'item'), exist_ok=True)
with open(os.path.join(ASSETS, 'models', 'item', 'bug_net.json'), 'w', newline='\n') as f:
    json.dump(model, f, indent=1)
    f.write('\n')
print('bug net:', len(els), 'elements')
