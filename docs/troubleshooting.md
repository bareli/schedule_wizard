# Troubleshooting and FAQ

## Troubleshooting

**The integration does not load.**
: Open Settings → System → Logs and filter for `schedule_wizard`. The minimum Home Assistant version is 2024.7.

**Calendar events do not start anything.**
: Check that a calendar is selected in Settings. Check that the event summary contains the zone label as whole words (a 1 or 2 character label must be the whole summary). All-day events are ignored. Then enable debug logging:

```yaml
logger:
  default: warning
  logs:
    custom_components.schedule_wizard: debug
```

**A valve stays on after a restart.**
: Expected if the stored active run was lost (fresh install) or the entity was turned off by hand during the downtime. Normal runs persist and are closed at their planned end.

**"Unsupported domain" from a service call.**
: Only `switch`, `valve`, `cover`, `input_boolean` and `light` are allowed.

**A warning appears in Settings → Repairs.**
: A zone's switch or a sensor used in Settings has disappeared (renamed, removed, or its integration is not loading). The warning names the entity and clears itself once it is fixed.

**Reporting a bug.**
: Use **Download diagnostics** (Settings → Devices & Services → Schedule Wizard → ⋮). The JSON has zones, plans, schedules, state and recent history, with the webhook ID and notify targets removed. Attach it to the issue on [GitHub](https://github.com/bareli/schedule_wizard/issues).

## FAQ

**Can I use it for things other than irrigation, such as outdoor lights for N minutes?**
: Yes. Any `switch`, `light`, `input_boolean`, `cover` or `valve` works.

**Can two schedules run on the same zone at the same time?**
: No. A second run on an already active zone replaces the first; the older run is logged as `cancelled`.

**What happens if a calendar event spans midnight?**
: The run starts at the event start. The length comes from the description, or the event length. Midnight has no special meaning.

**Does the panel work in the Companion app and on a phone?**
: Yes. The layout collapses to a single column on narrow screens.

**Where is the data stored, and can I back it up?**
: In `<config>/.storage/schedule_wizard.data`, plain JSON. It is included in any full Home Assistant backup.

**How do I start over?**
: Delete the integration (Settings → Devices & Services → Schedule Wizard → ⋮ → Delete), then add it again. Or delete `<config>/.storage/schedule_wizard.data` and restart.

**Does the integration add flow, pressure or season entities?**
: It adds the entities listed in the [Reference](reference.md#entities). Flow, rain and temperature come from sensors you pick in Settings.
