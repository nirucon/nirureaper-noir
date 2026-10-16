# nirureaper-noir

A **noir theme for REAPER**: near-black, stripped down, one restrained accent —
built to stay readable during long sessions.

The generator reads an existing REAPER theme, remaps every colour onto the Niru
Noir palette, and writes a new `.ReaperThemeZip` with the images carried over
untouched. It is designed to sit on top of the
[Reapertips theme](https://reapertips.com/products/reapertips-theme), which has
already solved the hard readability work — this project only changes the colours.

It works with the stock **Default 7.0** theme too.

## What "readable" means here

Dark themes usually fail for one reason: the muted text and the divider lines
are set by eye, not measured. So the palette is **checked with WCAG contrast**,
and the check is part of the tool (`--palette`).

Everything that carries text clears **4.5:1**. Body text clears **15:1**.

| Role | Colour | Contrast |
| --- | --- | --- |
| Surfaces | `#0a0a09` … `#1c1c19` | — |
| Dividers | `#3a3a36` | 1.6:1 vs panel (deliberately quiet) |
| Body text | `#f1f0ec` | **16.2:1** |
| Secondary text | `#c9c8c2` | **11.0:1** |
| Muted text | `#a8a7a0` | **7.6:1** |
| Accent (active/selected) | `#8aa88f` | 7.1:1 |
| Record | `#d9544a` | 4.7:1 |
| Solo | `#c9a86a` | 8.2:1 |
| Mute | `#8a8a86` | 5.3:1 |

A few deliberate choices:

- **The muted tone is brighter than usual.** REAPER paints track names and ruler
  labels with it at 9–10 px, where a typical dark theme's `#8x` grey fails.
- **Three greys, not one, for surfaces.** Track list, mixer and arrange sit a
  step apart so a 40-channel session still separates cleanly.
- **Exactly one hue.** Dov salvia for active and selected state. Record, solo
  and mute keep their conventional colours because they are status, not
  decoration — a greyscale record button is a usability bug, not a style.

## Requirements

- Python 3.10 or newer. Standard library only.
- A REAPER theme to base on, in `~/.config/REAPER/ColorThemes/`:
  - the **Reapertips theme** (recommended), or
  - **Default 7.0** (ships with REAPER).

## Use

```sh
# See the palette with its contrast ratios, change nothing
python3 nirureaper-noir.py --palette

# Preview the colours in a browser
python3 preview.py > palette.html && xdg-open palette.html

# Build it (picks Reapertips if present, else Default 7.0)
python3 nirureaper-noir.py

# Build and install straight into REAPER
python3 nirureaper-noir.py --install
```

Then pick it in REAPER under **Options → Themes → Niru Noir**.

Other flags:

| Flag | What it does |
| --- | --- |
| `--base THEME` | Use a specific `.ReaperThemeZip` as the starting point |
| `--out DIR` | Where to write the result (default `./dist`) |
| `--name NAME` | Theme name (default `Niru Noir`) |
| `--install` | Also copy it into `~/.config/REAPER/ColorThemes` |
| `--palette` | Print the palette and its contrast, then exit |

## How it works

A `.ReaperThemeZip` is two things: a `.ReaperTheme` text file of colour keys,
and a folder of ~3000 images. This tool **only rewrites the colour keys** and
carries the images over as they are, which is what makes it fast enough to be
worth doing.

Colour keys are matched by semantic rules, not by blind substitution: surfaces
go to surfaces, text to text, meter tops to the record red, and so on. Drawing
mode keys (`*_drawmode`) are left alone. See `RULES` in the generator.

## Licence

MIT for the code in this repository.

**This repository contains no theme artwork.** It reads a theme you already
have and writes a modified copy for your own use. The Reapertips theme is a
commercial product by its author — buy it from
[reapertips.com](https://reapertips.com/products/reapertips-theme) if you want
it. The stock Default theme belongs to Cockos Incorporated. Neither is
redistributed here.
