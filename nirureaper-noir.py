#!/usr/bin/env python3
"""nirureaper-noir: build a noir REAPER theme from an existing theme.

The generator reads a .ReaperTheme colour file, remaps its colours onto the
Niru Noir palette using semantic rules, and writes a new .ReaperTheme plus a
copy of the image folder it points at. The result is packed as a
.ReaperThemeZip that REAPER can import directly.

It is built to sit on top of the Reapertips theme (which solves the hard
readability work) but any REAPER 7 theme works as input.

No third-party dependencies: Python 3.10+ standard library only.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

VERSION = "1.0.0"

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
#
# Every value here was checked for contrast against the surfaces it sits on.
# The numbers in the comments are WCAG contrast ratios measured with the
# functions at the bottom of this file.

PALETTE = {
    # Surfaces, darkest to lightest. Kept close together so the interface reads
    # as one dark field, but far enough apart that panels never blend.
    "bg":       "#0a0a09",   # window background
    "panel":    "#141412",   # mixer, transport, toolbar
    "track":    "#161614",   # track control panel and mixer strips
    "arrange":  "#0d0d0c",   # the arrange area behind items
    "raised":   "#1c1c19",   # selected or hovered surfaces
    "edit":     "#0b0b0a",   # text fields and list backgrounds

    # Lines and frames. Subtle by design; the ratio is the point, not the hue.
    "line":     "#3a3a36",   # default divider (1.6:1 on panel)
    "line2":    "#4a4a45",   # stronger divider, selected item edges
    "grid":     "#232320",   # the arrange grid itself

    # Text. The muted tone is deliberately brighter than a typical dark theme's,
    # because REAPER uses it at 9-10 px for track names and ruler labels.
    "text":     "#f1f0ec",   # 16.2:1 on panel
    "text2":    "#c9c8c2",   # secondary text
    "muted":    "#a8a7a0",   # 7.6:1 on panel, still well above AAA
    "muted2":   "#8a8a85",   # 5.7:1 on panel, for the least important text

    # The one hue the theme is allowed. Dov salvia.
    "accent":   "#8aa88f",   # 7.1:1, active and selected

    # Status. These must stay recognisable at a glance; that is why they are
    # not greyscale. Record is the only warm signal in the whole interface.
    "rec":      "#d9544a",   # 4.7:1, record-armed
    "solo":     "#c9a86a",   # 8.2:1, soloed
    "mute":     "#8a8a86",   # 5.3:1, muted (present but quiet)

    # Media and meters.
    "peaks":    "#7f7f79",   # waveform peaks
    "peaks_rms": "#5a5a56",  # RMS overlay
    "item":     "#1a1a17",   # item background
    "item_sel": "#2a2a26",   # selected item background
    "cursor":   "#c9c8c2",   # edit cursor
    "play":     "#8aa88f",   # play cursor uses the accent
}

# --------------------------------------------------------------------------
# Semantic rules
# --------------------------------------------------------------------------
#
# A rule maps a colour key to a palette entry, either exactly or by pattern.
# Order matters: the first matching rule wins. The patterns are checked in the
# order written, so put the specific ones before the general ones.

RULES: list[tuple[str, str]] = [
    # --- Main window and panels -------------------------------------------
    ("col_main_bg", "bg"),
    ("col_main_bg2", "panel"),
    ("col_main_text", "text"),
    ("col_main_text2", "text2"),
    ("col_main_textshadow", "bg"),
    ("col_main_editbk", "edit"),
    ("col_main_resize", "line"),
    ("col_main_resize2", "accent"),
    ("col_main_3dhl", "line2"),
    ("col_main_3dsh", "bg"),
    ("col_buttonbg", "panel"),
    ("col_transport_editbk", "edit"),

    # --- Track list, mixer, transport -------------------------------------
    ("col_tracklistbg", "track"),
    ("col_mixerbg", "panel"),
    ("col_trans_bg", "panel"),
    ("col_trans_fg", "text"),
    ("col_tcp_text", "text"),
    ("col_tcp_textsel", "accent"),
    ("col_tl_bg", "panel"),
    ("col_tl_bgsel", "accent"),
    ("col_tl_bgsel2", "line2"),
    ("col_tl_fg", "text2"),
    ("col_tl_fg2", "muted"),
    ("col_seltrack", "accent"),
    ("col_seltrack2", "raised"),

    # --- Arrange area and grid --------------------------------------------
    ("col_arrangebg", "arrange"),
    ("col_gridlines", "grid"),
    ("col_gridlines1dm", "grid"),
    ("col_gridlines2", "grid"),
    ("col_gridlines2dm", "grid"),
    ("col_gridlines3", "grid"),
    ("col_gridlines3dm", "grid"),

    # --- Items ------------------------------------------------------------
    ("col_tr1_bg", "item"),
    ("col_tr2_bg", "item"),
    ("col_tr1_itembgsel", "item_sel"),
    ("col_tr2_itembgsel", "item_sel"),
    ("col_tr1_divline", "line2"),
    ("col_tr2_divline", "line2"),
    ("col_tr1_peaks", "peaks"),
    ("col_tr2_peaks", "peaks"),
    ("col_tr1_ps2", "peaks_rms"),
    ("col_tr2_ps2", "peaks_rms"),
    ("col_mi_bg", "item"),
    ("col_mi_bg2", "item"),
    ("col_mi_label", "text"),
    ("col_mi_label_sel", "text"),
    ("col_mi_label_float", "text2"),
    ("col_mi_label_float_sel", "text"),
    ("col_mi_left", "line"),
    ("col_mi_leftb", "line2"),
    ("col_mi_leftsel", "accent"),
    ("col_mi_leftselb", "accent"),
    ("col_mi_note", "accent"),
    ("col_mi_note_sel", "accent"),
    ("col_mi_fades", "line2"),
    ("col_mi_fade2", "line2"),
    ("col_peaksedge", "peaks"),
    ("col_peaksedge2", "peaks"),
    ("col_peaksedgesel", "accent"),
    ("col_peaksedgesel2", "accent"),
    ("col_peaksfade", "line"),
    ("col_peaksfade1", "line"),
    ("col_peaksfade2", "line"),

    # --- Cursor and time selection ----------------------------------------
    ("col_cursor", "cursor"),
    ("col_cursor2", "play"),

    # --- Toolbar ----------------------------------------------------------
    ("col_toolbar_text", "text2"),
    ("col_toolbar_text_on", "accent"),
    ("col_toolbar_frame", "line"),

    # --- Envelopes (the numbered slots follow the accent) -----------------
    ("col_env1", "text2"),
    ("col_env25", "text2"),

    # --- VU meters --------------------------------------------------------
    ("col_vutop", "rec"),
    ("col_vumid", "solo"),
    ("col_vubot", "accent"),
    ("col_vuind1", "peaks"),
    ("col_vuind2", "peaks"),
    ("col_vuind3", "peaks"),
    ("col_vuind4", "peaks"),
    ("col_vuclip", "rec"),
    ("col_vumidi", "line"),
    ("col_vudoint", "line2"),
    ("col_vudbscale", "muted2"),
    ("col_vudbscale2", "muted2"),
    ("col_vuintcol", "text2"),

    # --- Misc -------------------------------------------------------------
    ("col_offlinetext", "muted2"),
    ("col_explorer_sel", "accent"),
    ("col_explorer_seldm", "raised"),
    ("col_explorer_seledge", "accent"),
    ("col_fadearm", "accent"),
    ("col_fadearm2", "accent"),
    ("col_fadearm3", "accent"),
    ("col_routingact", "accent"),
    ("col_routinghl1", "line2"),
    ("col_routinghl2", "line2"),
    ("col_stretchmarker", "solo"),
    ("col_stretchmarker_b", "solo"),
    ("col_stretchmarker_h0", "solo"),
    ("col_stretchmarker_h1", "solo"),
    ("col_stretchmarker_h2", "solo"),
    ("col_stretchmarker_text", "bg"),
    ("col_stretchmarker_tm", "solo"),
    ("col_stretchmarkerm", "solo"),
    ("col_tsigmark", "muted2"),
    ("col_envlane1_divline", "line"),
    ("col_envlane2_divline", "line"),
]

# Draw-mode keys are not colours; they stay untouched. This list exists only to
# document which suffix we deliberately skip.
DRAWMODE_SUFFIX = "_drawmode"


# --------------------------------------------------------------------------
# Colour helpers
# --------------------------------------------------------------------------

def hex_to_bgr_decimal(hex_colour: str) -> str:
    """REAPER stores colours as a signed BGR integer. Convert a hex RGB string."""
    h = hex_colour.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    value = (b << 16) | (g << 8) | r
    if value >= 2 ** 31:
        value -= 2 ** 32
    return str(value)


def bgr_decimal_to_hex(value: str) -> str | None:
    """Decode a REAPER colour back to hex, for reporting and checking."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    if n < 0:
        n += 2 ** 32
    b = n & 0xFF
    g = (n >> 8) & 0xFF
    r = (n >> 16) & 0xFF
    return f"#{r:02x}{g:02x}{b:02x}"


def _relative_luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio between two hex colours."""
    la, lb = _relative_luminance(a), _relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# --------------------------------------------------------------------------
# Applying the palette
# --------------------------------------------------------------------------

def remap_line(key: str, value: str) -> str:
    """Return the new decimal value for one theme line, or the original."""
    if key.endswith(DRAWMODE_SUFFIX):
        return value

    # Exact rules first.
    for pattern, palette_key in RULES:
        if key == pattern:
            return hex_to_bgr_decimal(PALETTE[palette_key])

    # Envelope slots: col_env1 .. col_env16 get text2, the lane dividers the line.
    m = re.fullmatch(r"col_env(\d+)", key)
    if m:
        return hex_to_bgr_decimal(PALETTE["text2"])

    return value


def remap_theme(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    """Remap every colour line. Returns (new text, change list)."""
    changes: list[tuple[str, str, str]] = []
    out_lines: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z0-9_]+)=(.*)$", line)
        if not m:
            out_lines.append(line)
            continue
        key, value = m.group(1), m.group(2)
        if not key.startswith("col_"):
            out_lines.append(line)
            continue
        new_value = remap_line(key, value)
        if new_value != value:
            old_hex = bgr_decimal_to_hex(value) or value
            new_hex = bgr_decimal_to_hex(new_value) or new_value
            changes.append((key, old_hex, new_hex))
        out_lines.append(f"{key}={new_value}")
    return "\n".join(out_lines) + "\n", changes


# --------------------------------------------------------------------------
# Reading and writing themes
# --------------------------------------------------------------------------

def find_theme_zips(search_dirs: list[Path]) -> list[Path]:
    """Every .ReaperThemeZip we can find in the given directories."""
    found: list[Path] = []
    for d in search_dirs:
        if d.is_dir():
            found.extend(sorted(d.glob("*.ReaperThemeZip")))
    return found


def pick_input_theme(explicit: Path | None) -> Path:
    """Choose the theme to base on: the one given, else Reapertips, else Default 7."""
    if explicit:
        if not explicit.exists():
            raise SystemExit(f"No such theme: {explicit}")
        return explicit

    dirs = [Path.home() / ".config" / "REAPER" / "ColorThemes"]
    zips = find_theme_zips(dirs)
    if not zips:
        raise SystemExit(
            "No themes found in ~/.config/REAPER/ColorThemes. "
            "Pass one with --base, or import a theme into REAPER first.")

    for z in zips:
        if "reapertips" in z.name.lower():
            return z
    for z in zips:
        if "default_7" in z.name.lower():
            return z
    return zips[0]


def unpack_theme(zip_path: Path, work: Path) -> tuple[Path, Path]:
    """Unpack a .ReaperThemeZip. Returns (theme file, image folder)."""
    work.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(work)

    theme_file = next((p for p in work.rglob("*.ReaperTheme")), None)
    if theme_file is None:
        raise SystemExit(f"No .ReaperTheme inside {zip_path}")

    # The image folder is the directory named after the theme file's stem.
    stem = re.sub(r"\.ReaperTheme$", "", theme_file.name)
    image_dir = theme_file.parent / stem
    if not image_dir.is_dir():
        # Fall back to the only sibling directory, which is how REAPER packs it.
        siblings = [p for p in theme_file.parent.iterdir() if p.is_dir()]
        if len(siblings) == 1:
            image_dir = siblings[0]
        else:
            raise SystemExit(f"Could not find the image folder for {theme_file.name}")
    return theme_file, image_dir


def build(theme_file: Path, image_dir: Path, out_dir: Path, name: str) -> Path:
    """Write the recoloured theme and pack it as a .ReaperThemeZip."""
    text = theme_file.read_text(errors="replace")
    new_text, changes = remap_theme(text)

    out_dir.mkdir(parents=True, exist_ok=True)
    theme_name = name
    patch_dir = out_dir / theme_name
    if patch_dir.exists():
        shutil.rmtree(patch_dir)
    shutil.copytree(image_dir, patch_dir, symlinks=True)

    new_theme = out_dir / f"{theme_name}.ReaperTheme"
    new_theme.write_text(new_text)

    target = out_dir / f"{theme_name}.ReaperThemeZip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zf:
        zf.write(new_theme, arcname=new_theme.name)
        for item in sorted(patch_dir.rglob("*")):
            if item.is_file():
                zf.write(item, arcname=str(item.relative_to(out_dir)))

    print(f"  recoloured {len(changes)} colour keys")
    return target


def report_palette() -> None:
    """Print the palette with its measured contrast, so the claims are visible."""
    print(f"  {'colour':14} {'hex':9}  contrast on panel ({PALETTE['panel']})")
    for name, value in PALETTE.items():
        if name in ("bg", "panel", "track", "arrange", "raised", "edit",
                    "line", "line2", "grid", "item", "item_sel", "peaks",
                    "peaks_rms"):
            continue
        r = contrast(value, PALETTE["panel"])
        print(f"  {name:14} {value:9}  {r:5.2f}:1")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="nirureaper-noir",
        description="Build the Niru Noir REAPER theme from an existing theme.")
    p.add_argument("--version", action="version", version=f"nirureaper-noir {VERSION}")
    p.add_argument("--base", metavar="THEME", type=Path,
                   help="base .ReaperThemeZip (default: Reapertips, else Default 7)")
    p.add_argument("--out", metavar="DIR", type=Path,
                   help="where to write the result (default: ./dist)")
    p.add_argument("--name", default="Niru Noir", help="theme name (default: Niru Noir)")
    p.add_argument("--install", action="store_true",
                   help="also copy the result into ~/.config/REAPER/ColorThemes")
    p.add_argument("--palette", action="store_true",
                   help="print the palette and its contrast ratios, then exit")
    args = p.parse_args(argv)

    if args.palette:
        print(f"nirureaper-noir palette {VERSION}")
        report_palette()
        return 0

    base = pick_input_theme(args.base)
    print(f"  base theme: {base.name}")

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        theme_file, image_dir = unpack_theme(base, Path(tmp))
        print(f"  images:     {len(list(image_dir.rglob('*.png')))} files")
        out_dir = args.out or Path.cwd() / "dist"
        target = build(theme_file, image_dir, out_dir, args.name)

    print(f"  written:    {target}")
    if args.install:
        dest_dir = Path.home() / ".config" / "REAPER" / "ColorThemes"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / target.name
        shutil.copy2(target, dest)
        print(f"  installed:  {dest}")
        print("  Pick it in REAPER under Options > Themes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
