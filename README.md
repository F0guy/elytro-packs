# elytro-packs

Resource packs for the Elytro Minecraft server. Players reach the server
through Minehut, whose proxy only lets packs through from allowed hosts
(GitHub raw is one), so the packs are served from here.

- `elytro-pack.zip` - THE pack players get: ElyBosses' boss pack (BetterModel boss models,
  boss sounds, merchant art, orange Hallows gate portal + particles) merged with the ElyEmojis
  pack (chat emoji font, server-menu icons). Built by `build_merged.py` with fixed timestamps,
  so the same content always has the same SHA-1. ElyEmojis sends it (url + sha1 in its
  config); ElyBosses runs `pack.mode: none` and counts it as the boss pack.
- `extra/assets/` - assets that live only in this repo and are merged in last (no overrides
  allowed): the bug net (`elytro:bug_net` item model, given by bugnet.sk on the server;
  `extra/bug_net_draw.py` redraws its 32x32 sprite).
- After ANY pack change (boss models, plugins/ElyBosses/pack/, or the emoji pack-site zip) run
  `rebuild.ps1`: it rebuilds, pushes, waits for GitHub to serve the new file, then updates the
  SHA-1 in the ElyEmojis config and runs /emojis reload.
- `elytro-boss-pack.zip`, `elytro-emojis.zip`, `sync.ps1` - the earlier two-pack setup, kept
  for reference; nothing points at them any more.
