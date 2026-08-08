#!/usr/bin/env python3
"""Fetch public GitHub contribution-calendar data without a PAT."""
from __future__ import annotations
import argparse, datetime as dt, json, re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "contributions.json"
def parse_count(text: str) -> int | None:
    cleaned = " ".join(text.split())
    if re.search(r"\bno contributions?\b", cleaned, re.I): return 0
    m = re.search(r"([\d,]+)\s+contribution", cleaned, re.I)
    return int(m.group(1).replace(",", "")) if m else None
def fetch_days(username: str) -> list[dict]:
    r = requests.get(f"https://github.com/users/{username}/contributions", headers={"User-Agent":"Aashu-Github-profile-art/1.0","Accept":"text/html,application/xhtml+xml"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date], td[data-date][data-level]")
    if not cells: raise RuntimeError("GitHub contribution cells were not found; public markup may have changed.")
    days = {}
    for cell in cells:
        date = cell.get("data-date")
        if not date: continue
        try: level = int(cell.get("data-level") or 0)
        except ValueError: level = 0
        count = None
        for attr in ("data-count","aria-label","title"):
            value = cell.get(attr)
            if value:
                count = parse_count(str(value))
                if count is not None: break
        if count is None and cell.get("id"):
            tip = soup.find("tool-tip", attrs={"for": cell.get("id")})
            if tip: count = parse_count(tip.get_text(" ", strip=True))
        days[date] = {"date": date, "count": count or 0, "github_level": max(0,min(level,4))}
    result = sorted(days.values(), key=lambda x: x["date"])
    if not result: raise RuntimeError("No dated contribution cells were parsed.")
    return result
def current_streak(days: list[dict]) -> dict:
    today = dt.date.today().isoformat(); i = len(days)-1
    if i >= 0 and days[i]["date"] == today and days[i]["count"] == 0: i -= 1
    end = i
    while i >= 0 and days[i]["count"] > 0: i -= 1
    start = i+1; length = max(0,end-start+1)
    return {"length":length,"start":days[start]["date"] if length else None,"end":days[end]["date"] if length else None}
def longest_streak(days: list[dict]) -> dict:
    best = run = 0; best_start = best_end = run_start = None
    for item in days:
        if item["count"] > 0:
            if run == 0: run_start = item["date"]
            run += 1
            if run > best: best, best_start, best_end = run, run_start, item["date"]
        else: run = 0; run_start = None
    return {"length":best,"start":best_start,"end":best_end}
def build_payload(username: str, days: list[dict]) -> dict:
    total = sum(x["count"] for x in days); active = sum(1 for x in days if x["count"] > 0); best = max(days,key=lambda x:x["count"])
    monthly = {}
    for item in days: monthly[item["date"][:7]] = monthly.get(item["date"][:7],0)+item["count"]
    return {"username":username,"generated_at":dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),"range":{"start":days[0]["date"],"end":days[-1]["date"]},"total_contributions":total,"active_days":active,"average_per_active_day":round(total/active,1) if active else 0,"current_streak":current_streak(days),"longest_streak":longest_streak(days),"best_day":{"date":best["date"],"count":best["count"]},"monthly":[{"month":k,"total":v} for k,v in sorted(monthly.items())],"days":days}
def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--username",default="Aashu-Github"); p.add_argument("--out",type=Path,default=DEFAULT_OUT); a = p.parse_args()
    payload = build_payload(a.username, fetch_days(a.username)); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8"); print(f"Wrote {a.out}: {payload['total_contributions']} contributions.")
if __name__ == "__main__": main()
