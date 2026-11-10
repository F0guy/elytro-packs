"""Helpers for item models animated by 'pose gating' (see king_of_nothing_build.py for the why).

Every pose of a moving part is in the model at once. Each pose's faces use their own little cell
of an animated texture, and frame f of that texture paints only cell f; every other cell is fully
transparent, so the game discards those faces. The texture's animation is a steady client clock
that never stops and runs the same in every world, unlike minecraft:time (random wanders, daytime
stands still on Elytro). Interpolation must stay off: the game blends colour but takes alpha from
the current frame. Frame times may vary per frame (Gated.durations) to ease the motion.

Element rotations are single-axis, +-45 degrees: a box turned by any angle about z is first turned
by whole quarter turns (width and height swap, faces move round) and only the rest is a rotation.
"""
import math

from PIL import Image

FACES = ('north', 'south', 'east', 'west', 'up', 'down')
QUARTER = {'east': 'up', 'up': 'west', 'west': 'down', 'down': 'east', 'north': 'north', 'south': 'south'}


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def rnd3(v):
    return [round(x, 4) for x in v]


class Gated:
    """One animated texture. mats: name -> (dark, light) or (dark, light, alpha). A pose's cell is
    4 px wide and 2 px per row of two materials, in a 64x64 frame (up to 64 poses with 8 materials,
    128 with 4)."""

    def __init__(self, kind, ref, poses, ticks, mats):
        self.kind, self.ref, self.poses, self.ticks, self.mats = kind, ref, poses, ticks, mats
        self.names = list(mats)
        self.rows = (len(self.names) + 1) // 2
        self.cell_h = self.rows * 2
        assert (poses + 15) // 16 * self.cell_h <= 64, 'too many poses x materials for one frame'
        self.durations = None            # optional list of ticks per pose
        self.vary = None                 # optional (pose, material, (dark, light)) -> (dark, light)

    def cell(self, pose):
        return (pose % 16) * 4, (pose // 16) * self.cell_h

    def uv(self, pose, mat):
        k = self.names.index(mat)
        cx, cy = self.cell(pose)
        px, py = cx + (k % 2) * 2, cy + (k // 2) * 2
        u0, v0 = px / 4, py / 4
        return [round(u0 + 0.125, 4), round(v0 + 0.125, 4), round(u0 + 0.375, 4), round(v0 + 0.375, 4)]

    def paint(self, px, pose):
        cx, cy = self.cell(pose)
        for k, name in enumerate(self.names):
            spec = self.mats[name]
            lo, hi = spec[0], spec[1]
            if self.vary:
                lo, hi = self.vary(pose, name, (lo, hi))
            alpha = spec[2] if len(spec) > 2 else 255
            for dy in range(2):
                for dx in range(2):
                    c = mix(lo, hi, 0.55 if dy == 0 else 0.25)
                    px[cx + (k % 2) * 2 + dx, cy + (k // 2) * 2 + dy] = c[:3] + (alpha,)

    def texture(self):
        sheet = Image.new('RGBA', (64, 64 * self.poses), (0, 0, 0, 0))
        for f in range(self.poses):
            frame = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            self.paint(frame.load(), f)
            sheet.paste(frame, (0, 64 * f))
        return sheet

    def opaque(self):
        im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        for p in range(self.poses):
            self.paint(im.load(), p)
        return im

    def mcmeta(self):
        anim = {'frametime': self.ticks, 'interpolate': False}
        if self.durations:
            anim['frames'] = [{'index': i, 'time': int(t)} for i, t in enumerate(self.durations)]
        return {'animation': anim}

    def box(self, pose, centre, local, half, angle, mats, light=0, spin=0, cull=()):
        """A box at `local` from `centre`, half sizes `half`, all turned `angle` degrees about z
        round `centre`; spin turns the box about its own centre too. mats: face -> material with
        'all' for the rest. cull: faces (before turning) always hidden inside something."""
        a = math.radians(angle)
        lx, ly, lz = local
        cx = centre[0] + lx * math.cos(a) - ly * math.sin(a)
        cy = centre[1] + lx * math.sin(a) + ly * math.cos(a)
        cz = centre[2] + lz
        total = angle + spin
        k = round(total / 90)
        rest = total - 90 * k
        hx, hy, hz = half
        if k % 2:
            hx, hy = hy, hx
        face_mat = {f: (None if f in cull else mats.get(f, mats['all'])) for f in FACES}
        for _ in range(k % 4):
            face_mat = {QUARTER[f]: m for f, m in face_mat.items()}
        faces = {f: {'uv': self.uv(pose, face_mat[f]), 'texture': self.ref} for f in FACES if face_mat[f]}
        e = {'from': rnd3([cx - hx, cy - hy, cz - hz]), 'to': rnd3([cx + hx, cy + hy, cz + hz]), 'faces': faces}
        if abs(rest) > 0.01:
            e['rotation'] = {'angle': round(rest, 3), 'axis': 'z', 'origin': rnd3([cx, cy, cz])}
        if light:
            e['light_emission'] = light
        e['name'] = '%s %03d' % (self.kind, pose)
        return e


class Swatches:
    """A static 64x64 texture of 8x8 swatches drawn by functions (x, y, noise) -> rgba."""

    def __init__(self, ref, layout):
        self.ref, self.layout = ref, layout

    def uv(self, name):
        cx, cy = self.layout[name]
        u0, v0 = cx * 2 + 0.2, cy * 2 + 0.2
        return [round(u0, 3), round(v0, 3), round(u0 + 1.6, 3), round(v0 + 1.6, 3)]

    def box(self, frm, to, mat, rot=None, light=0, faces_mat=None, name=None, cull=()):
        faces = {f: {'uv': self.uv((faces_mat or {}).get(f, mat)), 'texture': self.ref} for f in FACES if f not in cull}
        e = {'from': rnd3(frm), 'to': rnd3(to), 'faces': faces}
        if rot:
            e['rotation'] = rot
        if light:
            e['light_emission'] = light
        if name:
            e['name'] = name
        return e


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


def check(E):
    for e in E:
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, (e.get('name'), v)
        if 'rotation' in e:
            assert -45 <= e['rotation']['angle'] <= 45, e['rotation']


def strip_names(E):
    return [{k: v for k, v in e.items() if k != 'name'} for e in E]
