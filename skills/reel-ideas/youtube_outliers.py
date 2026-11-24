"""Free outlier search on YouTube Shorts (backup when vidIQ has no credits).
Usage: python3 outliers.py "topic" [N] -> JSON list sorted by outlier score."""
import json, statistics, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
def flat(url, limit):
    out = subprocess.run(["yt-dlp", "--flat-playlist", "-j", "--playlist-end", str(limit), url],
                         capture_output=True, text=True, timeout=120).stdout
    return [json.loads(l) for l in out.splitlines() if l.strip()]
seen, hits = set(), []
for term in [t.strip() for t in q.split("|")]:
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(term) + "&sp=EgIYAQ%3D%3D"
    for h in flat(url, n):
        d = h.get("duration")
        if h["id"] in seen or not h.get("view_count") or d is None or d > 90:
            continue
        seen.add(h["id"]); hits.append(h)
def score(h):
    try:
        vids = flat(f"https://www.youtube.com/channel/{h['channel_id']}/shorts", 30)
        views = [v["view_count"] for v in vids if v.get("view_count")]
        med = statistics.median(views) if len(views) >= 4 else None
    except Exception:
        med = None
    return {"title": h["title"], "channel": h.get("channel"), "views": h["view_count"],
            "channel_median": med, "outlier": round(h["view_count"] / med, 1) if med else None,
            "url": "https://www.youtube.com/shorts/" + h["id"]}
with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(score, hits))
print("searched", len(hits), file=sys.stderr)
rows = [r for r in rows if r["outlier"]]
rows.sort(key=lambda r: -r["outlier"])
print(json.dumps(rows, indent=1, ensure_ascii=False))
