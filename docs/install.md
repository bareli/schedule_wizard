# Install

Minimum Home Assistant version: **2024.7.0**.

## With HACS (recommended)

=== "Search in HACS"

    1. Open **HACS** and search for **Schedule Wizard**.
    2. Open it and press **Download**.

=== "Custom repository (fallback)"

    Use this if the search does not find it.

    1. HACS → ⋮ → **Custom repositories**.
    2. Add `https://github.com/bareli/schedule_wizard` as category **Integration**.
    3. Search for **Schedule Wizard** in HACS and press **Download**.

Then:

1. **Restart Home Assistant.**
2. Go to **Settings → Devices & Services → + Add Integration → Schedule Wizard**.
3. A **Schedule Wizard** entry (sprinkler icon) appears in the sidebar. Open it and start the setup wizard.

## Manual install

1. Copy the folder `custom_components/schedule_wizard/` from the repository into `<config>/custom_components/`.
2. Restart Home Assistant.
3. Add the integration from the UI, as in step 2 above.

## Notes

- Only one instance can be added.
- The Lovelace card is registered automatically; you do not add a resource by hand.
- Data is stored in `<config>/.storage/schedule_wizard.data` as plain JSON, so it is part of any full Home Assistant backup.
