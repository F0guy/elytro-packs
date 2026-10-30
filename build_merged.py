"""Build skin-pack.zip: ElyBosses' boss pack + the ElyEmojis pack, as ONE reproducible zip.

Why: Minehut's proxy only allows packs from hosts like GitHub raw, and ElyBosses re-stamps its own
zip on every boot (new SHA-1 each restart), so a GitHub copy of it always drifts. This zip is built
from the sources with fixed timestamps and a fixed order, so the same content always has the same
SHA-1. ElyEmojis sends it (url + sha1 in plugins/ElyEmojis/config.yml); ElyBosses runs pack.mode: none.

Inputs (fetched by rebuild.ps1):
  src/build.zip       plugins/BetterModel/build.zip            (boss models)
  src/pack/           plugins/ElyBosses/pack/                  (boss sounds, fonts, orange portal...)
  src/emojis.zip      ElyEmojis pack-site/elytro-emojis.zip    (emoji font + menu icons)
  extra/assets/       kept in this repo                        (skript items, e.g. the bug net)
Usage: python build_merged.py [--check-boss reference.zip]
"""
import hashlib, io, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.join(HERE, 'skin-pack.zip')
STAMP = (2026, 1, 1, 0, 0, 0)

def boss_files():
    """Same result as ElyBosses' PackService.merge(): BetterModel's build, then the pack/ folder on top."""
    files = {}
    with zipfile.ZipFile(os.path.join(SRC, 'build.zip')) as z:
        for n in z.namelist():
            if not n.endswith('/'):
                files[n] = z.read(n)
    root = os.path.join(SRC, 'pack')
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            files[os.path.relpath(p, root).replace(os.sep, '/')] = open(p, 'rb').read()
    # ElyBosses adds this filter so OptiFine horse models from lower packs don't fight the Dullahan's steed
    meta = json.loads(files['pack.mcmeta'])
    meta['filter'] = {'block': [{'namespace': 'minecraft',
                                 'path': 'optifine/cem/(horse|skeleton_horse|zombie_horse)([0-9]*\\.(jem|properties)|/.*)'}]}
    files['pack.mcmeta'] = json.dumps(meta, separators=(',', ':')).encode()
    return files

def merged():
    files = boss_files()
    with zipfile.ZipFile(os.path.join(SRC, 'emojis.zip')) as z:
        emoji = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
    clash = sorted(n for n in emoji if n in files and n not in ('pack.mcmeta', 'pack.png') and emoji[n] != files[n])
    if clash:
        sys.exit('Boss and emoji packs both define: %s' % clash)
    files.update({n: b for n, b in emoji.items() if n not in ('pack.mcmeta',)})   # emoji pack.png (Elytro icon) wins
    # Optional source fallback for cosmetic uploads; normal extra/ files win.
    skin_fallback = set()
    for source_name in ('skin-sources.zip', 'music-sources.zip'):
        source_path = os.path.join(HERE, source_name)
        if not os.path.isfile(source_path):
            continue
        with zipfile.ZipFile(source_path) as source:
            for name in source.namelist():
                if name.endswith('/'):
                    continue
                if not name.startswith(('assets/elytro/', 'assets/elytromusic/')) or '..' in name.split('/'):
                    sys.exit('Invalid source path: ' + name)
                body = source.read(name)
                if name in files and files[name] != body:
                    sys.exit('Source conflicts with boss/emoji asset: ' + name)
                files[name] = body
                skin_fallback.add(name)
    root = os.path.join(HERE, 'extra')
    for d, _, fs in os.walk(os.path.join(root, 'assets')):
        for f in fs:
            p = os.path.join(d, f)
            n = os.path.relpath(p, root).replace(os.sep, '/')
            b = open(p, 'rb').read()
            if n in files and files[n] != b and n not in skin_fallback:
                sys.exit('extra/ and the boss/emoji packs both define: %s' % n)
            files[n] = b
    bm, em = json.loads(files['pack.mcmeta']), json.loads(emoji['pack.mcmeta'])
    lo = max(bm['pack']['min_format'], em['pack']['min_format'])
    hi = min(bm['pack']['max_format'], em['pack']['max_format'])
    bm['pack'].update({'description': '§dElytro §fpack', 'min_format': lo, 'max_format': hi,
                       'supported_formats': [lo, hi]})
    files['pack.mcmeta'] = json.dumps(bm, indent=2).encode()
    return files

def write(files, path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(files):
            info = zipfile.ZipInfo(n, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, files[n])
    open(path, 'wb').write(buf.getvalue())
    return hashlib.sha1(buf.getvalue()).hexdigest()

if __name__ == '__main__':
    if '--check-boss' in sys.argv:
        ref = zipfile.ZipFile(sys.argv[sys.argv.index('--check-boss') + 1])
        mine = boss_files()
        theirs = {n: ref.read(n) for n in ref.namelist() if not n.endswith('/')}
        bad = sorted(n for n in set(mine) | set(theirs) if mine.get(n) != theirs.get(n))
        print('boss rebuild vs server build: %d files, %d differ %s' % (len(theirs), len(bad), bad[:5]))
    files = merged()
    print('skin-pack.zip', len(files), 'files, sha1', write(files, OUT))
