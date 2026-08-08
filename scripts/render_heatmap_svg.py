#!/usr/bin/env python3
from __future__ import annotations
import argparse, calendar, datetime as dt, html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DEFAULT_IN=ROOT/'data'/'contributions.json'; DEFAULT_OUT=ROOT/'contrib-heatmap.svg'
BG='#050508'; BORDER='#24243a'; TEXT='#f4f4f5'; MUTED='#8b8b9b'; ACCENT='#69acc2'; PALETTE=['#12131b','#17313b','#245466','#397d93','#55a6bd','#79cde2']; CELL=12; GAP=3; STEP=15; LEFT=48; TOP=63; RIGHT=24; BOTTOM=96

def bootstrap(out):
    out.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="230" viewBox="0 0 860 230"><rect width="860" height="230" rx="14" fill="{BG}"/><rect x=".5" y=".5" width="859" height="229" rx="14" fill="none" stroke="{BORDER}"/><circle cx="19" cy="18" r="5" fill="#ff5f56"/><circle cx="36" cy="18" r="5" fill="#ffbd2e"/><circle cx="53" cy="18" r="5" fill="#27c93f"/><text x="430" y="22" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="12" text-anchor="middle">aashu@github: ~/contributions</text><text x="430" y="112" fill="{TEXT}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="18" text-anchor="middle">contribution graph initializes on first workflow run</text><text x="430" y="142" fill="{ACCENT}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="13" text-anchor="middle">Actions → Update profile art → Run workflow</text></svg>''',encoding='utf-8')

def grid_for(days):
    first=dt.date.fromisoformat(days[0]['date']); cur=[None]*((first.weekday()+1)%7); cols=[]
    for item in days:
        cur.append(item)
        if len(cur)==7: cols.append(cur); cur=[]
    if cur: cur += [None]*(7-len(cur)); cols.append(cur)
    return cols

def render(p):
    days=p['days']; grid=grid_for(days); max_count=max((int(d['count']) for d in days),default=0); width=LEFT+len(grid)*STEP+RIGHT; height=TOP+7*STEP+BOTTOM
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><style>@keyframes r{{0%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:1;transform:translateY(0)}}}}.c{{opacity:0;animation:r .42s cubic-bezier(.2,.8,.2,1) both}}@media (prefers-reduced-motion:reduce){{.c{{opacity:1;animation:none}}}}</style><rect width="{width}" height="{height}" rx="14" fill="{BG}"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="14" fill="none" stroke="{BORDER}"/><line x1="0" y1="34" x2="{width}" y2="34" stroke="{BORDER}"/>']
    for i,c in enumerate(('#ff5f56','#ffbd2e','#27c93f')): out.append(f'<circle cx="{19+i*17}" cy="17" r="5" fill="{c}"/>')
    out.append(f'<text x="{width/2}" y="21" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="12" text-anchor="middle">aashu@github: ~/Aashu-Github/contributions</text>')
    seen=set()
    for ci,col in enumerate(grid):
        dates=[dt.date.fromisoformat(x['date']) for x in col if x]
        if dates:
            f=min(dates); key=(f.year,f.month)
            if key not in seen and (f.day<=7 or not seen): seen.add(key); out.append(f'<text x="{LEFT+ci*STEP}" y="51" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="11">{calendar.month_abbr[f.month]}</text>')
    for r,l in ((1,'Mon'),(3,'Wed'),(5,'Fri')): out.append(f'<text x="10" y="{TOP+r*STEP+10}" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="10">{l}</text>')
    for ci,col in enumerate(grid):
        for ri,item in enumerate(col):
            if not item: continue
            count=int(item['count']); gh=int(item.get('github_level',0)); level=0 if count<=0 else (5 if max_count and count==max_count else max(1,min(4,gh or 1))); x=LEFT+ci*STEP; y=TOP+ri*STEP; delay=ci*.018+ri*.042; plural='' if count==1 else 's'
            out.append(f'<g class="c" style="animation-delay:{delay:.3f}s"><rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{PALETTE[level]}"><title>{html.escape(item["date"])}: {count} contribution{plural}</title></rect></g>')
    sep=TOP+7*STEP+38; total=int(p['total_contributions']); active=int(p['active_days']); cur=int(p['current_streak']['length']); longest=int(p['longest_streak']['length']); best=p['best_day']
    out.append(f'<line x1="{LEFT}" y1="{sep}" x2="{width-RIGHT}" y2="{sep}" stroke="{BORDER}"/><text x="{LEFT}" y="{sep+26}" fill="{ACCENT}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="18" font-weight="700">{total:,}</text><text x="{LEFT+58}" y="{sep+26}" fill="{TEXT}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="12">contributions · {active} active days</text><text x="{LEFT}" y="{sep+50}" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="11">current streak <tspan fill="{TEXT}">{cur}d</tspan> · longest <tspan fill="{TEXT}">{longest}d</tspan> · best <tspan fill="{TEXT}">{best["count"]}</tspan> on {html.escape(best["date"])}</text></svg>')
    return ''.join(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',type=Path,default=DEFAULT_IN); ap.add_argument('--out',type=Path,default=DEFAULT_OUT); a=ap.parse_args()
    if not a.input.exists(): bootstrap(a.out); return
    a.out.write_text(render(json.loads(a.input.read_text(encoding='utf-8'))),encoding='utf-8')
if __name__=='__main__': main()
