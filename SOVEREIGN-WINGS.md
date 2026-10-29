# Sovereign Wings — Elytro-rank chestplate skin

Sovereign Wings now follows the existing Bug Net / Key to the City / Singularity / Eureka skin workflow. It is a physical skin voucher with a colored name, rank/type line, italic quote, flavor text, application instructions and a real serial or an explicit **Test copy - no serial** label.

> Some inherit a crown. Others earn their wings.

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
