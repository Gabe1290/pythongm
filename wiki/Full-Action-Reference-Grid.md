# Grid

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### If On Grid

| Property | Value |
|----------|-------|
| **Name** | `if_on_grid` |
| **Icon** | ▦ |
| **Category** | Grid |

Check if object is aligned to grid

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `grid_size` | Number | `32` | Grid cell size in pixels |
| `then_actions` | Action list | — | Actions if on grid |
| `else_actions` | Action list | — | Actions if not on grid |

### Snap to Grid

| Property | Value |
|----------|-------|
| **Name** | `snap_to_grid` |
| **Icon** | ▦ |
| **Category** | Grid |

Align instance position to grid

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `grid_size` | Number | `32` | Grid cell size in pixels |

### Stop If No Keys Pressed

| Property | Value |
|----------|-------|
| **Name** | `stop_if_no_keys` |
| **Icon** | ▦ |
| **Category** | Grid |

Stop movement on grid when no movement keys are pressed (perfect for smooth grid snapping)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `grid_size` | Number | `32` | Grid cell size in pixels |

### Test Grid Alignment

| Property | Value |
|----------|-------|
| **Name** | `test_alignment` |
| **Icon** | ❓▦ |
| **Category** | Grid |

Conditional: true if the instance is aligned to a grid

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `hsnap` | Number | `32` | Horizontal grid spacing in pixels |
| `vsnap` | Number | `32` | Vertical grid spacing in pixels |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (2)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (20)
- [Control](Full-Action-Reference-Control) (19)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (4)

[← Back to Full Action Reference](Full-Action-Reference)
