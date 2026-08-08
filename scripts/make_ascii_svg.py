#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, os
from pathlib import Path
from PIL import Image, ImageEnhance
ROOT=Path(__file__).resolve().parents[1]; COLS=88; ROWS=42; CELL_W=7.4; CELL_H=15.0; RAMP=' .`:-=+*cs#%@'; W=740; H=800; ART_X=44; ART_Y=70; ART_W=COLS*CELL_W
BG='#050508'; BORDER='#24243a'; MUTED='#8b8b9b'; INK='#d8d8df'; ACCENT='#69acc2'
def main():
    p=argparse.ArgumentParser(); p.add_argument('input',type=Path,nargs='?',default=ROOT/'source-prepped.png'); p.add_argument('output',type=Path,nargs='?',default=ROOT/'aashu-ascii.svg'); a=p.parse_args()
    im=ImageEnhance.Contrast(Image.open(a.input).convert('L')).enhance(1.06).resize((COLS,ROWS),Image.Resampling.LANCZOS); px=im.load(); lines=[]
    for y in range(ROWS):
        line=[]
        for x in range(COLS):
            lum=(px[x,y]/255.0)**1.16
            line.append(' ' if lum>=.82 else RAMP[max(0,min(len(RAMP)-1,round((1-lum)*(len(RAMP)-1))))])
        lines.append(''.join(line))
    static=bool(os.environ.get('STATIC')); out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" rx="18" fill="{BG}"/><rect x=".5" y=".5" width="739" height="799" rx="18" fill="none" stroke="{BORDER}"/><line x1="0" y1="44" x2="740" y2="44" stroke="{BORDER}"/><circle cx="22" cy="22" r="6" fill="#ff5f56"/><circle cx="41" cy="22" r="6" fill="#ffbd2e"/><circle cx="60" cy="22" r="6" fill="#27c93f"/><text x="370" y="27" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="15" text-anchor="middle">aashu@github: ~$ ./portrait.sh</text>']
    for row,line in enumerate(lines):
        y=ART_Y+row*CELL_H+CELL_H*.76; text=f'<text xml:space="preserve" x="{ART_X}" y="{y:.1f}" fill="{INK}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="12.9" textLength="{ART_W:.1f}" lengthAdjust="spacing">{html.escape(line)}</text>'
        if static: out.append(text); continue
        delay=row*.095; dur=.11
        out.append(f'<clipPath id="r{row}"><rect x="{ART_X}" y="{ART_Y+row*CELL_H:.1f}" width="0" height="{CELL_H}"><animate attributeName="width" from="0" to="{ART_W:.1f}" begin="{delay:.3f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath><g clip-path="url(#r{row})">{text}</g>')
    out.append(f'<line x1="0" y1="724" x2="740" y2="724" stroke="{BORDER}"/><text x="44" y="765" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="14">aashu@github:~$ whoami <tspan fill="{INK}">Saiaashish Vadapalli</tspan></text></svg>'); a.output.write_text(''.join(out),encoding='utf-8'); print(f'Wrote {a.output}')
if __name__=='__main__': main()
