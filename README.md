# nirureaper-noir

A **noir theme for REAPER**: near-black, stripped down, one restrained accent —
built to stay readable during long sessions.

The generator reads an existing REAPER theme, remaps every colour onto the Niru
Noir palette, and writes a new `.ReaperThemeZip` with the images carried over
untouched.

## Two variants

Same palette, two bases. The variant only decides which theme REAPER's images
come from.

| Variant | Base | Output | Images |
| --- | --- | --- | --- |
| `noir` | [Reapertips](https://reapertips.com/products/reapertips-theme) | `Niru Noir` | ~3030 |
| `noir-default` | REAPER's stock Default 7.0 | `Niru Noir Default` | ~1435 |
| `auto` | Reapertips if installed, else Default | either | — |

**Why two?** The two bases have different lightness thinking, not just different
tints — 93 of their 110 shared colour keys differ (for example the item
background is `#9e9e9e` in Reapertips and `#818989` in Default). Reapertips also
ships 10 extra keys (`col_mi_left`, `col_mi_note`, `col_peaksfade1`, …) that
Default simply does not have.

Because the generator maps colours **semantically** and leaves keys a base does
not have alone, both variants come out identical wherever the keys overlap, and
a missing key keeps the base's own sensible default. So:

- **`Niru Noir`** — Reapertips' stronger item edges and HiDPI images. Needs the
  Reapertips theme.
- **`Niru Noir Default`** — works for anyone, using only what ships with REAPER.

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

# Build, picking the base automatically (Reapertips, else Default)
python3 nirureaper-noir.py --variant auto --install

# Build a specific variant and install it
python3 nirureaper-noir.py --variant noir --install
python3 nirureaper-noir.py --variant noir-default --install
```

Then pick it in REAPER under **Options → Themes**.

Other flags:

| Flag | What it does |
| --- | --- |
| `--variant auto\|noir\|noir-default` | Which base to build on (`auto` by default) |
| `--base THEME` | Use a specific `.ReaperThemeZip` instead of a variant's base |
| `--out DIR` | Where to write the result (default `./dist`) |
| `--name NAME` | Override the theme name |
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
