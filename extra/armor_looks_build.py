"""Custom worn looks for Elytro's mining, fishing and PvP armor sets (2026-11-06).

Writes Minecraft equipment textures into pack/assets/elytro/: for each set a `humanoid` layer
(helmet, chestplate, boots) and a `humanoid_leggings` layer, plus the equipment asset JSON
assets/elytro/equipment/<id>.json. Plugins point a piece's equippable asset_id at elytro:<id>.

Texture layout is the 64x32 humanoid sheet (box UVs): head at (0,0) 8x8x8, body at (16,16)
8x12x4, right arm at (40,16) 4x12x4, right leg at (0,16) 4x12x4 (left limbs mirror the right).
Everything is original pixel art drawn here; no vanilla textures are used.
usage: python armor_looks.py
"""
import json
import random
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "pack/assets/elytro"
W, H = 64, 32


# ------------------------------------------------------------------ geometry

def faces(u, v, w, h, d):
    """Box UV rectangles (x0, y0, x1, y1) by face."""
    return {
        "top": (u + d, v, u + d + w, v + d),
        "bottom": (u + d + w, v, u + d + 2 * w, v + d),
        "right": (u, v + d, u + d, v + d + h),
        "front": (u + d, v + d, u + d + w, v + d + h),
        "left": (u + d + w, v + d, u + 2 * d + w, v + d + h),
        "back": (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
    }


HEAD = faces(0, 0, 8, 8, 8)
BODY = faces(16, 16, 8, 12, 4)
ARM = faces(40, 16, 4, 12, 4)
LEG = faces(0, 16, 4, 12, 4)
SIDES = ("right", "front", "left", "back")


def hexc(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def shade(c, f):
    return tuple(max(0, min(255, int(x * f))) for x in c[:3]) + (255,)


class Sheet:
    def __init__(self, seed):
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.px = self.img.load()
        self.rng = random.Random(seed)

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.px[x, y] = c

    def fill(self, rect, c, noise=.06, rows=None):
        x0, y0, x1, y1 = rect
        for y in range(y0, y1):
            if rows and not (rows[0] <= y - y0 < rows[1]):
                continue
            for x in range(x0, x1):
                f = 1 + self.rng.uniform(-noise, noise)
                self.put(x, y, shade(c, f))

    def outline(self, rect, c, rows=None):
        x0, y0, x1, y1 = rect
        ys = range(y0, y1) if not rows else range(y0 + rows[0], y0 + rows[1])
        for y in ys:
            self.put(x0, y, c)
            self.put(x1 - 1, y, c)
        for y in (ys[0], ys[-1]):
            for x in range(x0, x1):
                self.put(x, y, c)

    def row(self, rect, r, c):
        x0, y0, x1, _ = rect
        for x in range(x0, x1):
            self.put(x, y0 + r, c)

    def at(self, rect, x, y, c):
        self.put(rect[0] + x, rect[1] + y, c)


# ------------------------------------------------------------------ the sets

SETS = {
    # mining
    "mining_prospector": dict(base="#8a5a2b", dark="#4a2e16", light="#b47a42", accent="#2f2a26", trim="#c8a05a", eye="#ffd27a",
                              helm="hood", motif="braces", glow="#ffcf6a", seed=11),
    "mining_aquanaut": dict(base="#1f8a9e", dark="#0f4651", light="#4fc4d6", accent="#b8862e", trim="#e0b04a", eye="#bff6ff",
                            helm="diver", motif="rivets", glow="#9ff3ff", seed=12),
    "mining_golemforged": dict(base="#6f6f72", dark="#3c3c40", light="#97979b", accent="#4f7a3a", trim="#55555a", eye="#7fe6ff",
                               helm="visor", motif="rune", glow="#6fe0ff", seed=13),
    "mining_titan": dict(base="#2a2530", dark="#141118", light="#463f50", accent="#9b59d6", trim="#e0b84a", eye="#e9c8ff",
                         helm="crown", motif="gem", glow="#c58bff", seed=14),
    # fishing
    "fishing_anglers": dict(base="#e0b62c", dark="#8f6c10", light="#f4d35e", accent="#22364f", trim="#2f4a66", eye="#f6e7b0",
                            helm="hood", motif="slicker", glow="#ffe58a", seed=21),
    "fishing_coral": dict(base="#e0707e", dark="#8e3442", light="#f6a3ad", accent="#fff1e6", trim="#ffd1d6", eye="#fff1e6",
                          helm="hood", motif="coral", glow="#fff1e6", seed=22),
    "fishing_abyssal": dict(base="#16264a", dark="#0a1226", light="#2a3f72", accent="#3fe0e0", trim="#1d3a5c", eye="#6ff7ff",
                            helm="visor", motif="biolum", glow="#6ff7ff", seed=23),
    "fishing_leviathan": dict(base="#2f6e4e", dark="#173a28", light="#4c9c70", accent="#d6a838", trim="#e8c25a", eye="#ffe27a",
                              helm="fin", motif="scales", glow="#ffd95a", seed=24),
    "fishing_kraken": dict(base="#5a2a72", dark="#2e1340", light="#7f45a0", accent="#d79ae8", trim="#3d1a52", eye="#ff5a5a",
                           helm="hood", motif="suckers", glow="#ff6a6a", seed=25),
    "fishing_tidal": dict(base="#1f8f8a", dark="#0e4a48", light="#45bdb6", accent="#e8fbff", trim="#bff3f0", eye="#e8fbff",
                          helm="fin", motif="waves", glow="#e8fbff", seed=26),
    "fishing_poseidon": dict(base="#e6e0d0", dark="#9c947e", light="#fffaf0", accent="#d4a82c", trim="#f0c94a", eye="#5ff0ff",
                             helm="crown", motif="trident", glow="#5ff0ff", seed=27),
    # pvp
    "pvp_juggernaut": dict(base="#3b383b", dark="#1e1c1e", light="#5a565a", accent="#b3262b", trim="#6e6a6e", eye="#ff3b3b",
                           helm="visor", motif="plate", glow="#ff4040", seed=31),
    "pvp_phantom": dict(base="#2a2236", dark="#130f1a", light="#3f3452", accent="#b9a6e8", trim="#4a3d61", eye="#e6ddff",
                        helm="hood", motif="wisps", glow="#e6ddff", seed=32),
    "pvp_pyroclast": dict(base="#c99a2a", dark="#5a3a10", light="#efc75a", accent="#ff5a1a", trim="#2a1a0c", eye="#ffb03a",
                          helm="visor", motif="lava", glow="#ff7a2a", seed=33),
    "pvp_glacier": dict(base="#a9d8ee", dark="#4f86a8", light="#e6f7ff", accent="#ffffff", trim="#7fb6d6", eye="#e6fbff",
                        helm="crown", motif="frost", glow="#ffffff", seed=34),
}


def draw(sid, s):
    base, dark, light, accent, trim = (hexc(s[k]) for k in ("base", "dark", "light", "accent", "trim"))
    eye, glow = hexc(s["eye"]), hexc(s["glow"])
    outline = shade(dark, .8)
    shadow = (12, 10, 14, 255)

    # ============ humanoid layer: helmet, chestplate (body + arms), boots ============
    a = Sheet(s["seed"])
    for k, r in HEAD.items():
        a.fill(r, base)
        a.outline(r, outline)
    for k in SIDES:   # rim around the bottom of the helmet
        a.row(HEAD[k], 7, dark)
    f = HEAD["front"]
    helm = s["helm"]
    if helm == "hood":
        for y in range(2, 8):
            for x in range(1, 7):
                if not (y == 2 and x in (1, 6)):
                    a.at(f, x, y, shadow)
        a.at(f, 2, 4, eye); a.at(f, 5, 4, eye)
        for x in range(0, 8):
            a.at(f, x, 1, light)
        for k in ("top",):
            for x in range(1, 7):
                a.at(HEAD[k], x, 3, light)
    elif helm == "visor":
        for x in range(1, 7):
            a.at(f, x, 3, shadow); a.at(f, x, 4, shadow)
        a.at(f, 2, 3, eye); a.at(f, 5, 3, eye)
        for y in range(4, 7):
            a.at(f, 3, y, light); a.at(f, 4, y, light)
        for x in range(0, 8):
            a.at(f, x, 1, trim)
    elif helm == "diver":
        for y in range(1, 7):
            for x in range(1, 7):
                edge = (x in (1, 6) or y in (1, 6)) and not ((x, y) in ((1, 1), (6, 1), (1, 6), (6, 6)))
                if (x, y) in ((1, 1), (6, 1), (1, 6), (6, 6)):
                    continue
                a.at(f, x, y, hexc(s["trim"]) if edge else shade(glow, .55))
        a.at(f, 2, 2, glow); a.at(f, 3, 2, glow); a.at(f, 2, 3, glow)
        for k in ("left", "right"):
            a.at(HEAD[k], 3, 3, accent); a.at(HEAD[k], 4, 3, accent); a.at(HEAD[k], 3, 4, accent); a.at(HEAD[k], 4, 4, accent)
    elif helm == "crown":
        for x in range(1, 7):
            a.at(f, x, 3, shadow); a.at(f, x, 4, shadow)
        a.at(f, 2, 3, eye); a.at(f, 5, 3, eye)
        for k in SIDES:   # crown band with points
            for x in range(8):
                a.at(HEAD[k], x, 1, trim)
                if x % 2 == 0:
                    a.at(HEAD[k], x, 0, trim)
        a.at(f, 3, 2, accent); a.at(f, 4, 2, accent)
    elif helm == "fin":
        for x in range(1, 7):
            a.at(f, x, 3, shadow); a.at(f, x, 4, shadow)
        a.at(f, 2, 3, eye); a.at(f, 5, 3, eye)
        for y in range(0, 5):   # a fin down the middle of the crown
            a.at(HEAD["top"], 3, y + 1, trim); a.at(HEAD["top"], 4, y + 1, trim)
        for k in ("back",):
            for y in range(0, 4):
                a.at(HEAD[k], 3, y, trim); a.at(HEAD[k], 4, y, trim)
        for k in ("left", "right"):   # gill slits
            for y in (3, 5):
                for x in (2, 3, 4):
                    a.at(HEAD[k], x, y, dark)
    if sid == "mining_prospector":   # the miner's lamp
        a.at(f, 3, 0, glow); a.at(f, 4, 0, glow); a.at(f, 3, 1, glow); a.at(f, 4, 1, glow)
        a.at(f, 2, 1, trim); a.at(f, 5, 1, trim)

    for k, r in BODY.items():
        a.fill(r, base)
        a.outline(r, outline)
    for k, r in ARM.items():
        a.fill(r, base)
        a.outline(r, outline)
    # shoulder pads and cuffs on the arms
    for k in SIDES:
        r = ARM[k]
        for y in range(0, 3):
            a.row(r, y, light if y == 0 else trim)
        a.row(r, 10, dark); a.row(r, 11, outline)
    a.fill(ARM["top"], trim, noise=.03)
    # chest: collar, belt, motif
    bf = BODY["front"]
    for k in SIDES:
        a.row(BODY[k], 0, dark)
        a.row(BODY[k], 9, trim); a.row(BODY[k], 10, shade(trim, .8))
    a.at(bf, 3, 9, accent); a.at(bf, 4, 9, accent); a.at(bf, 3, 10, accent); a.at(bf, 4, 10, accent)   # buckle
    motif(a, s, sid, bf, BODY["back"], ARM, base, dark, light, accent, trim, glow)

    # boots: the lower legs
    for k, r in LEG.items():
        if k in ("top",):
            continue
        rr = r if k == "bottom" else (r[0], r[1] + 7, r[2], r[3])
        a.fill(rr, dark if k == "bottom" else base)
        if k in SIDES:
            a.row(r, 7, trim)
            a.row(r, 11, outline)
            a.put(r[0], r[1] + 8, outline); a.put(r[2] - 1, r[1] + 8, outline)
    a.fill(LEG["bottom"], shade(dark, .7), noise=.02)

    # ============ humanoid_leggings layer: waist + legs ============
    b = Sheet(s["seed"] + 100)
    for k in SIDES:
        r = BODY[k]
        b.fill((r[0], r[1] + 7, r[2], r[3]), shade(base, .9))
        b.row(r, 7, trim); b.row(r, 8, shade(trim, .8))
        b.put(r[0], r[1] + 11, outline); b.put(r[2] - 1, r[1] + 11, outline)
    for k, r in LEG.items():
        b.fill(r, shade(base, .92))
        b.outline(r, outline)
    for k in SIDES:
        r = LEG[k]
        b.row(r, 5, light); b.row(r, 6, trim)   # knee band
    for y in range(4, 8):   # knee pad on the front
        for x in range(1, 3):
            b.at(LEG["front"], x, y, light if y in (4, 7) else trim)
    if s["motif"] in ("scales", "plate", "frost", "lava", "biolum", "suckers"):
        motif_legs(b, s, base, dark, light, accent, glow)
    return a.img, b.img


def motif(a, s, sid, front, back, arm, base, dark, light, accent, trim, glow):
    m, rng = s["motif"], a.rng
    if m == "braces":   # suspenders over a work shirt
        for y in range(0, 9):
            a.at(front, 1, y, s and hexc(s["accent"])); a.at(front, 6, y, hexc(s["accent"]))
            a.at(back, 1, y, hexc(s["accent"])); a.at(back, 6, y, hexc(s["accent"]))
        a.at(front, 2, 6, trim); a.at(front, 2, 7, trim)   # a pocket
    elif m == "rivets":
        for x in (1, 6):
            for y in (2, 5, 8):
                a.at(front, x, y, trim)
        for y in range(1, 9):   # air tank on the back
            for x in (2, 3, 4, 5):
                a.at(back, x, y, trim if x in (2, 5) else shade(trim, 1.1))
        a.at(front, 3, 3, glow); a.at(front, 4, 3, glow)
    elif m == "rune":
        for (x, y) in ((3, 2), (4, 2), (2, 3), (5, 3), (2, 4), (5, 4), (3, 5), (4, 5)):   # a glowing diamond core
            a.at(front, x, y, glow)
        for (x, y) in ((3, 3), (4, 3), (3, 4), (4, 4)):
            a.at(front, x, y, shade(glow, .6))
        for _ in range(14):   # cracks and moss
            r = (front, back, arm["front"], arm["left"])[rng.randrange(4)]
            x, y = rng.randrange(1, r[2] - r[0] - 1), rng.randrange(1, r[3] - r[1] - 1)
            a.at(r, x, y, accent if rng.random() < .5 else dark)
    elif m == "gem":
        for (x, y) in ((3, 3), (4, 3), (3, 4), (4, 4)):
            a.at(front, x, y, accent)
        a.at(front, 3, 3, glow)
        for y in range(1, 9):
            a.at(front, 0, y, trim); a.at(front, 7, y, trim)
        for x in range(1, 7):
            a.at(front, x, 1, trim)
    elif m == "slicker":   # a raincoat: buttons and a hem
        for y in (2, 4, 6):
            a.at(front, 4, y, accent)
        for y in range(1, 9):
            a.at(front, 3, y, shade(hexc(s["base"]), .8))
    elif m == "coral":
        for (cx, cy) in ((2, 3), (5, 5), (2, 7), (6, 2)):   # polyp clusters
            for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                a.at(front, cx + dx, cy + dy, accent if (dx, dy) != (0, 0) else shade(hexc(s["dark"]), 1.2))
        for _ in range(10):
            r = (back, arm["front"], arm["left"])[rng.randrange(3)]
            a.at(r, rng.randrange(1, r[2] - r[0] - 1), rng.randrange(3, r[3] - r[1] - 2), accent)
    elif m == "biolum":
        for (x, y) in ((1, 2), (6, 3), (2, 5), (5, 6), (3, 8), (6, 8)):
            a.at(front, x, y, glow)
        for y in range(1, 9):
            a.at(front, 3, y, shade(glow, .45)); a.at(front, 4, y, shade(glow, .45))
        for r in (arm["front"], arm["left"], arm["right"]):
            for y in (4, 7):
                a.at(r, 1, y, glow)
    elif m == "scales":
        for r in (front, back, arm["front"], arm["left"], arm["right"]):
            w, h = r[2] - r[0], r[3] - r[1]
            for y in range(1, min(h - 1, 9)):
                for x in range(1, w - 1):
                    if (x + (y // 2) * 1) % 3 == 0 and y % 2 == 0:
                        a.at(r, x, y, light)
                    elif (x + (y // 2)) % 3 == 1 and y % 2 == 1:
                        a.at(r, x, y, dark)
        for y in range(1, 9):
            a.at(front, 3, y, trim); a.at(front, 4, y, trim)
    elif m == "suckers":
        for r in (arm["front"], arm["left"], arm["right"], arm["back"]):
            for y in (4, 6, 8):
                a.at(r, 1, y, accent); a.at(r, 2, y, accent)
        for y in range(3, 7):   # the great eye
            for x in range(1, 7):
                if (x, y) not in ((1, 3), (6, 3), (1, 6), (6, 6)):
                    a.at(front, x, y, accent)
        for (x, y) in ((3, 4), (4, 4), (3, 5), (4, 5)):
            a.at(front, x, y, glow)
        a.at(front, 3, 4, (20, 6, 8, 255))
    elif m == "waves":
        for r in (front, back):
            for x in range(8):
                for y0 in (3, 7):
                    y = y0 + (0 if x % 4 < 2 else 1)
                    a.at(r, x, y, accent)
                    a.at(r, x, y + 1, light)
    elif m == "trident":
        for y in range(2, 9):
            a.at(front, 3, y, trim); a.at(front, 4, y, trim)
        for (x, y) in ((1, 2), (1, 3), (6, 2), (6, 3), (2, 4), (5, 4), (3, 1), (4, 1)):
            a.at(front, x, y, trim)
        a.at(front, 3, 5, glow); a.at(front, 4, 5, glow)
    elif m == "plate":
        for y in (3, 6):
            a.row(front, y, dark); a.row(back, y, dark)
        for x in (1, 6):
            a.at(front, x, 1, accent); a.at(front, x, 2, accent)
        for r in (arm["front"], arm["left"], arm["right"], arm["back"]):
            a.row(r, 3, dark)
            a.row(r, 1, accent)
    elif m == "wisps":
        for (x, y) in ((1, 3), (2, 2), (5, 5), (6, 4), (3, 7), (4, 8), (2, 6)):
            a.at(front, x, y, accent)
        for r in (back, arm["front"], arm["left"]):
            for _ in range(4):
                a.at(r, rng.randrange(1, r[2] - r[0] - 1), rng.randrange(3, r[3] - r[1] - 2), shade(hexc(s["accent"]), .75))
    elif m == "lava":
        for r in (front, back, arm["front"], arm["left"], arm["right"]):
            w, h = r[2] - r[0], r[3] - r[1]
            x, y = rng.randrange(1, w - 1), 1
            for _ in range(h + 2):
                a.at(r, x, y, glow)
                if rng.random() < .3:
                    a.at(r, min(w - 2, x + 1), y, hexc(s["accent"]))
                y += 1
                x = max(1, min(w - 2, x + rng.choice((-1, 0, 0, 1))))
                if y >= min(h - 1, 9):
                    break
    elif m == "frost":
        for r in (front, back, arm["front"], arm["left"], arm["right"]):
            w, h = r[2] - r[0], r[3] - r[1]
            for _ in range(5):
                x, y = rng.randrange(1, w - 1), rng.randrange(1, min(h - 1, 9))
                a.at(r, x, y, accent)
        for (x, y) in ((3, 2), (4, 3), (3, 4), (2, 3), (4, 5), (3, 6), (5, 4)):
            a.at(front, x, y, hexc(s["accent"]))


def motif_legs(b, s, base, dark, light, accent, glow):
    rng = b.rng
    m = s["motif"]
    for k in ("front", "left", "right", "back"):
        r = LEG[k]
        w, h = r[2] - r[0], r[3] - r[1]
        for _ in range(3):
            x, y = rng.randrange(1, w - 1), rng.randrange(8, h - 1)
            c = {"scales": light, "plate": dark, "frost": accent, "lava": glow, "biolum": glow, "suckers": accent}[m]
            b.at(r, x, y, c)


def main():
    (PACK / "textures/entity/equipment/humanoid").mkdir(parents=True, exist_ok=True)
    (PACK / "textures/entity/equipment/humanoid_leggings").mkdir(parents=True, exist_ok=True)
    (PACK / "equipment").mkdir(parents=True, exist_ok=True)
    for sid, s in SETS.items():
        top, legs = draw(sid, s)
        top.save(PACK / f"textures/entity/equipment/humanoid/{sid}.png")
        legs.save(PACK / f"textures/entity/equipment/humanoid_leggings/{sid}_legs.png")
        asset = {"layers": {"humanoid": [{"texture": f"elytro:{sid}"}],
                            "humanoid_leggings": [{"texture": f"elytro:{sid}_legs"}]}}
        (PACK / f"equipment/{sid}.json").write_text(json.dumps(asset, indent=2))
    print(len(SETS), "armor looks written to", PACK)


if __name__ == "__main__":
    main()
