# Elytro Music Manager

Double-click **Open Music Manager.cmd**, or open http://127.0.0.1:5719 while it is running. On a fresh copy, run **Setup Music Manager.cmd** first.

1. Import a local audio file or paste a direct audio/media link. Enter a title, creator and permanent track ID. Imports are converted to normalized mono OGG Vorbis for positional Minecraft audio. Preview the converted result in the library.
2. Click **Prepare update**. The manager downloads and verifies the currently active server pack and preserves it while adding your music. It also preserves music already in the live catalog.
3. Click **Open upload folder**, then **Open GitHub upload**. Upload the listed root files (`skin-pack.zip`, `music-sources.zip`, `build_merged.py`) and commit them. The GitHub integration cannot upload on this account, so this explicit browser upload step uses your existing login; no GitHub password or token is stored.
4. Click **Activate published update**. It verifies the published ZIP against the prepared bytes, checks for concurrent server changes, uploads the catalog and Skript, and updates the matching pack URL/hash. The pack is re-sent to online players. No server restart or data-registry reload is used.

In Minecraft:

- `/music` opens the paginated track library. Clicking a disc previews it personally; `/music stop` stops the preview.
- `/music play <id>` previews a track by ID.
- `/music give <id> <player>` gives a custom physical disc (operator or `elytro.music.admin`).
- `/music reload` refreshes the library (operator).
- Insert a custom disc into a jukebox by right-clicking it with the disc. Normal right-click ejection and breaking the jukebox retain the physical record. Custom playback stops when the record is removed, the block is broken, the chunk unloads, the track ends, or the script is unloaded.

The record's custom sound is handled by Skript, rather than adding new frozen Minecraft registries or replacing a vanilla song. Ordinary discs are unchanged. Custom insertion is manual; vanilla hopper automation for custom records is not provided. Up to 32 independent jukebox channels can play, including multiple boxes with the same track. Players approaching an active box hear it from the beginning until that box's remaining play time runs out. Script reload stops active custom tracks; eject and reinsert their discs to restart them.

All audio is merged into the existing single resource pack. `music-sources.zip` and the additive rebuild-script change preserve tracks on future pack rebuilds. Track IDs are permanent and duplicates are rejected to avoid changing discs already in players' inventories. Existing server files are re-read, compared and backed up outside the plugin loader before activation.

Connections use the existing private `%USERPROFILE%/.elytro-rcon.json` and `.elytro-sftp.json` files and the SFTP key. Credentials are never part of exported uploads. The UI binds only to loopback and uses a per-run token to protect write actions. The import cap is 150 MB and 30 minutes; media downloads do not fetch playlists.

The library includes an original eight-second Elytro Sound Check. Verification covers real file conversion, a real URL download, OGG format/duration, UI/API, write protection, valid archive references, and published-pack hashes. No online player's inventory was changed by tests.

Verification: 20 manager/API/conversion checks, one real URL download-and-convert check, and 11 live jukebox/controller checks passed. Jukebox tests used a proxy inventory and two temporary empty sky blocks, restored afterward.
