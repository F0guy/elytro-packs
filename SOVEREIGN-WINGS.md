# Sovereign Wings — Elytro-rank chestplate skin

Sovereign Wings now follows the existing Bug Net / Key to the City / Singularity / Eureka skin workflow. It is a physical skin voucher with a colored name, rank/type line, italic quote, flavor text, application instructions and a real serial or an explicit **Test copy - no serial** label.

> No bird soars too high if he soars with his own wings.
> — William Blake, [The Marriage of Heaven and Hell](https://www.gutenberg.org/files/45315/45315-h/45315-h.htm)

- `/skin` or `/skins`: existing staff catalog. The wing voucher is in slot 22, beneath the other four skins. Clicking it gives a test copy without consuming an issuance number.
- `/sovereign test`: direct staff test copy.
- `/sovereign give <player>`: issue a numbered skin with a hidden issuance stamp.
- `/sovereign inspect <serial>`, `/sovereign revoke <serial>`, `/sovereign clearserial`: the same issuance/revocation/test tools used by other reward skins.
- Pick up the voucher with the inventory cursor, left-click a chestplate in your own inventory, then confirm. Apply in Survival, matching the other skins. It consumes exactly one voucher only after checking the item snapshot and rechecking that voucher's serial/stamp.
- Wear the chestplate and use `/wings` to choose from fourteen colors, or `/wings color #AABBCC` for a custom color.
- `/wings toggle`, `/wings on`, `/wings off`, `/wings remove` control visibility/removal. `/wings apply` explains the voucher workflow; it does not bypass the skin.
- Staff can use `/wings preview` without editing armor, and `/wings status [player]` for diagnostics.

The skin is restricted to the `elytro.wings` permission, granted to the Elytro rank. Staff can test it. Armor keeps its original model, material, name, lore, durability, enchants, attributes, foreign plugin data and serials. The wing layer adds its own keys and one lore label. Revoking a wing skin removes only that layer; it never deletes or downgrades the chestplate. Existing unnumbered attachments from the first wing build remain valid test attachments.

Tests do not use real serial numbers. Numbered copies use a hidden stamp; reusing a revoked serial cannot make an old voucher valid again. Preserve the sovereign serial/state/token/log/free/revoked Skript variables along with other reward-skin issuance registries when wiping player progression.

## Animation and visibility

The four hinged feather pieces flap gently at rest, more while walking/sprinting, and strongly during flight. They are cosmetic, non-persistent ItemDisplays, with no passengers, collision, damage or flight permission. They clean up on unequip, death, quit, invisibility/vanish, world changes and script reload.

The original invisible-wing defect was a Skript enum-format mismatch. The pack had loaded and four wing displays existed, but Skript converted the resource-pack status to `successfully load`. The visibility code compared that formatted value to `SUCCESSFULLY_LOADED`, hiding every display. The renderer now compares the enum's `.name()` instead. Live diagnosis verified 4/4 of the owner's wing pieces were visible after the correction. This fix needs no additional pack download or new pack hash.

## Installation

Place `rank_wings.sk`, `sovereign_skin.sk` and `skins.sk` in `plugins/Skript/scripts/`. Reload rank_wings, then sovereign_skin, then skins. The deployed source was compared against the live skin menu before merging, so the other four skin entries and unrelated menu behavior remain intact. Menu click and drag guards prevent extracting fake UI items.

The five native wing assets are already in `skin-pack.zip` and `skin-sources.zip`. Existing pack assets remain unchanged by this script-only revision.

Verification: 40 original wing checks and 21 additional voucher/visibility checks passed. The additional tests checked quote/name/instructions, test serial isolation, armor-model/metadata preservation, stable lore, stamp validation, spent-voucher rejection, revocation behavior and 4/4 live wing pieces visible. Player inventories and real issuance counters were not changed by the tests.


## V3: curved feathers, client attachment and refundable skin

The wing meshes were rebuilt with overlapping tapered alpha-cut feathers and a larger inward-sweeping silhouette. Left models are genuinely mirrored, instead of rotating the same curved mesh 180 degrees. Both shoulder and wrist transforms use the same body coordinate frame, so turning doesn't move the roots off the back.

A small reloadable **transport library** (`sovereign-rig-v3.1.jar`, ~9 KB) goes in `plugins/Skript/wing-lib/`. It isn't a Bukkit plugin and needs no restart. `rank_wings.sk` loads and closes it itself. ProtocolLib mounts the wing pieces only in viewers' clients, merging existing nametags and real passengers and suppressing stale movement packets. The server has no wing passengers, so player teleports remain available. Skin issuance, menus, colors and flap animation remain in Skript. This helper is the part that removes network trailing while retaining normal teleports.

The physical skin now uses a visible vanilla feather in both the menu and hand. Older paper vouchers are upgraded without changing serial/stamp/color. The quote has a verified William Blake attribution.

`/wings remove` returns the same physical skin with its existing serial, hidden stamp and color. Full storage blocks removal cleanly; no item is voided or dropped. The attached serial is preserved when recoloring. Removing a legacy unnumbered attachment returns a test skin, without consuming a real issuance number. Applying over an existing attachment asks you to remove and reclaim it first.

Install/update: upload the transport JAR into the wing-lib folder, reload `sovereign_skin`, then `rank_wings`. Publish and verify the updated pack, reload ElyEmojis, and enable effects with `/wingsadmin on`. The full native assets, editable Blender file, preview and transport source are in `Sovereign-Wings-v3-Sources.zip`.

V3 verification: 18/18 isolated checks passed, including the actual removal controller against a proxy inventory, full-inventory refusal, no repeated refund, same serial/stamp/color returned, complete original chestplate preservation, visible voucher, attributed quote and a complete turn of both mirrored hinges, with explicit back-offset checks. No real player's inventory or issuance counter changed.

## V3.2: stable turning and corrected back placement (29 October 2026)

Body yaw belongs outside the four independently interpolated local poses. The versioned v3.1 transport library sends all segments the same native entity yaw, while shoulder/wrist animation stays local. No real passengers are added.

The fixed-billboard branch of Minecraft 1.21.11 DisplayRenderer applies negative entity yaw with NO extra half-turn. The camera-facing billboard branches use a different orientation. V3.1 mistakenly applied that camera correction to fixed displays, putting the wings in front. V3.2 explicitly selects FIXED and removes the extra pose rotation. Only the separate item-render half-turn is canceled by right_rotation.

Install sovereign-rig-v3.1.jar into plugins/Skript/wing-lib/, replace rank_wings.sk, then /sk reload rank_wings. No pack assets, checksum, server restart or pack download change.

Verification uses the FIXED renderer branch, not camera-facing billboard math: 1,450 pose/turn samples passed for joined wrists and correct back offsets across idle/walk/fly/glide/crouch and -360 to +360 degrees. Live owner diagnosis confirmed negative local-Z shoulder/wrist offsets, identical body yaw and zero real passengers. Actual client appearance still requires visual confirmation.
