#!/usr/bin/env python3
"""Write an HTML swatch sheet for the Niru Noir palette.

This is a quick way to look at the colours before installing the theme: open
the file in a browser and see the palette as surfaces, text and status marks,
with the measured contrast ratios printed next to each pairing.

Run: python3 preview.py > palette.html
"""

from __future__ import annotations

import html
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_generator():
    """Import the generator module by path, so no package layout is required."""
    spec = importlib.util.spec_from_file_location(
        "nirureaper_noir", HERE / "nirureaper-noir.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    gen = load_generator()
    p = gen.PALETTE
    contrast = gen.contrast

    def swatch(name: str, value: str, note: str = "") -> str:
        return (
            f'<div class="sw"><div class="chip" style="background:{value}"></div>'
            f'<div class="swlabel"><strong>{html.escape(name)}</strong>'
            f'<code>{value}</code>{f"<span>{html.escape(note)}</span>" if note else ""}'
            f'</div></div>'
        )

    surfaces = "".join(
        swatch(n, p[n], f"text {contrast(p['text'], p[n]):.1f}:1")
        for n in ("bg", "panel", "track", "arrange", "raised", "edit"))
    lines = "".join(
        swatch(n, p[n], f"vs panel {contrast(p[n], p['panel']):.2f}:1")
        for n in ("line", "line2", "grid"))
    texts = "".join(
        swatch(n, p[n], f"on panel {contrast(p[n], p['panel']):.1f}:1")
        for n in ("text", "text2", "muted", "muted2"))
    status = "".join(
        swatch(n, p[n], f"on panel {contrast(p[n], p['panel']):.1f}:1")
        for n in ("accent", "rec", "solo", "mute"))
    media = "".join(
        swatch(n, p[n], "")
        for n in ("item", "item_sel", "peaks", "peaks_rms", "cursor"))

    print(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Niru Noir - palette</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; padding:40px; background:{p['bg']}; color:{p['text']};
         font:15px/1.5 Arial,Helvetica,sans-serif; }}
  h1 {{ font-size:2rem; letter-spacing:-.03em; margin:0 0 4px; }}
  h2 {{ font-size:.7rem; letter-spacing:.16em; text-transform:uppercase;
        color:{p['muted']}; margin:38px 0 14px;
        border-bottom:1px solid {p['line']}; padding-bottom:10px; }}
  p.lead {{ color:{p['muted']}; max-width:60ch; margin:0 0 12px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr));
           gap:1px; background:{p['line']}; border:1px solid {p['line']}; }}
  .sw {{ background:{p['panel']}; padding:0; display:flex; gap:0; }}
  .chip {{ width:74px; min-height:74px; flex:0 0 auto; }}
  .swlabel {{ padding:11px 12px; display:grid; gap:2px; align-content:center; }}
  .swlabel strong {{ font-size:.82rem; }}
  .swlabel code {{ color:{p['muted']}; font-size:.72rem; }}
  .swlabel span {{ color:{p['muted2']}; font-size:.68rem; }}
  .demo {{ border:1px solid {p['line']}; background:{p['arrange']}; padding:0; }}
  .tcp {{ display:flex; }}
  .track {{ background:{p['track']}; border-right:1px solid {p['line']};
            padding:10px 12px; width:190px; }}
  .track.sel {{ background:{p['raised']}; box-shadow:inset 3px 0 0 {p['accent']}; }}
  .track .name {{ font-size:.8rem; }}
  .track .num {{ color:{p['muted2']}; font-size:.66rem; }}
  .arr {{ flex:1; padding:12px; }}
  .item {{ background:{p['item']}; border:1px solid {p['line2']};
           height:34px; margin-bottom:6px; display:flex; align-items:center;
           padding:0 8px; font-size:.72rem; }}
  .item.sel {{ background:{p['item_sel']}; border-color:{p['accent']}; }}
  .meter {{ width:10px; background:{p['edit']}; border:1px solid {p['line']};
            height:150px; display:flex; flex-direction:column-reverse;
            margin-left:auto; }}
  .meter i {{ display:block; }}
  .status {{ display:flex; gap:8px; margin-top:14px; }}
  .tag {{ border:1px solid {p['line']}; padding:5px 9px; font-size:.68rem;
          letter-spacing:.08em; }}
  .rec {{ background:{p['rec']}; color:{p['bg']}; border-color:{p['rec']}; }}
  .solo {{ background:{p['solo']}; color:{p['bg']}; border-color:{p['solo']}; }}
  .mute {{ background:{p['mute']}; color:{p['bg']}; border-color:{p['mute']}; }}
</style></head><body>
<h1>Niru Noir</h1>
<p class="lead">The palette, with measured WCAG contrast. Everything that is
text clears 4.5:1; body text clears 15:1.</p>

<h2>Surfaces</h2><div class="grid">{surfaces}</div>
<h2>Lines</h2><div class="grid">{lines}</div>
<h2>Text</h2><div class="grid">{texts}</div>
<h2>Status</h2><div class="grid">{status}</div>
<h2>Media</h2><div class="grid">{media}</div>

<h2>How it looks</h2>
<div class="demo"><div class="tcp">
  <div class="track"><div class="num">01</div><div class="name">Drums</div>
    <div class="meter"><i style="height:58%;background:{p['accent']}"></i>
      <i style="height:22%;background:{p['solo']}"></i></div></div>
  <div class="track sel"><div class="num">02</div><div class="name">Bass</div></div>
  <div class="track"><div class="num">03</div><div class="name">Guitar L</div></div>
  <div class="arr">
    <div class="item">drums take 4</div>
    <div class="item sel">bass - verse</div>
    <div class="item">gtr L comp</div>
    <div class="status">
      <span class="tag rec">REC</span><span class="tag solo">SOLO</span>
      <span class="tag mute">MUTE</span><span class="tag">recorded 00:03:41</span>
    </div>
  </div>
</div></div>
</body></html>""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
