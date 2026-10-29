# Sovereign Wings — Elytro rank chestplate cosmetic

Skript-only implementation, using the existing Skript + skript-reflect installation. No new plugin or restart is needed.

- `/wings` opens the application/color menu.
- Wear your chosen chestplate and click Apply, or use `/wings apply`.
- `/wings color violet` picks a preset; `/wings color #AABBCC` accepts custom RGB.
- `/wings toggle`, `/wings on`, `/wings off`, `/wings remove` control the attachment.
- Staff can use `/wings preview` without editing armor, and `/wings status [player]` for diagnostics.
- Permission: `elytro.wings`, assigned to the Elytro rank. Operators/build staff can test too.

The chestplate's model, name, lore, damage, enchants, attributes, serial and other plugin data stay intact. The attachment uses two namespaced PDC strings; removing it restores the original item exactly. Recoloring only changes the wing displays, including on leather chestplates. Displayed wing colors persist on the chestplate itself; default choices and visibility persist in Skript variables.

Four feather-model pieces form two hinged wings. Gentle idle movement becomes flapping while walking/sprinting and a stronger flap during flight. Wings grant no flight, combat stats or collision. They use independent non-persistent ItemDisplays; players never carry passengers, so teleports remain available. Displays clean up on unequip, death, quit, world changes, invisibility/vanish, permission loss and script reload. Players who haven't loaded a resource pack can't see fallback leather armor displays.

The interface cancels clicks and drags across the entire view; only left-clicking its own buttons does anything. Scroll/number keys, shift-clicks, offhand swaps, drops and double-clicks cannot extract fake menu items.

## Files and updates

`rank_wings.sk` installs to `plugins/Skript/scripts/rank_wings.sk` and reloads with `/sk reload rank_wings`. Native model assets are in `skin-sources.zip` and are included in `skin-pack.zip`. The new model names start with `elytro:sovereign_wing_`; ordinary chestplate models are never overridden. Source files are also available in the local assets/rank-wings/pack/ folder.

The pack remains ONE merged pack. All 5,748 previously active pack assets were preserved byte-for-byte; five wing assets were added. The normal build_merged.py source fallback keeps the new assets on rebuilds.

Publish first, verify the GitHub ZIP bytes, then update BOTH URL and matching SHA-1 in a freshly downloaded ElyEmojis config and run `/emojis reload`. Finally `/wingsadmin on` enables effects. `/wingsadmin off` removes displays and preserves attachments. This avoids showing undefined item models before the pack is available.

## Verification

40/40 isolated live server checks passed: attachment/removal round-trip, complete original metadata preservation, custom RGB validation, preset colors, 72 hinge poses, menu construction, dyed custom item models, renderer reuse/follow/recolor, no passenger changes, entity cleanup, and live Elytro permission assignment. Tests used local item copies and hidden temporary entities; no player's armor, location or serial counter changed. Real-client appearance still requires loading the updated pack.
