"""
Fetch essence prices from poe.ninja and write the static site.

    python build_data.py [out_dir]     (default: _site)

Writes out_dir/index.html, out_dir/data/leagues.json and
out_dir/data/essences/<league-slug>.json. The GitHub Pages workflow runs this
on a schedule, because poe.ninja doesn't allow browsers to fetch it directly.
"""
import json
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

NINJA = "https://poe.ninja/poe1/api"
UA = "poe-essence-calc (+https://github.com/treeko11/poe-essence-calc)"
HERE = Path(__file__).resolve().parent


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def get_leagues():
    """Current economy leagues: [{name, url, displayName, ...}]"""
    return [l for l in fetch_json(f"{NINJA}/data/index-state").get("economyLeagues", [])
            if not l.get("isPrivate")]


def get_essences(league_name):
    q = urllib.parse.urlencode({"league": league_name, "type": "Essence"})
    d = fetch_json(f"{NINJA}/economy/exchange/current/overview?{q}")
    d["_fetched"] = time.time()
    return d


def main(out_dir="_site"):
    out = Path(out_dir)
    (out / "data" / "essences").mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / "index.html", out / "index.html")
    leagues = get_leagues()
    ok = []
    for l in leagues:
        try:
            d = get_essences(l["name"])
        except Exception as e:  # one bad league shouldn't break the whole build
            print(f"skip {l['name']}: {e}", file=sys.stderr)
            continue
        if not d.get("lines"):
            print(f"skip {l['name']}: no essence prices")
            continue
        (out / "data" / "essences" / f"{l['url']}.json").write_text(json.dumps(d), encoding="utf-8")
        ok.append(l)
        print(f"{l['name']}: {len(d.get('lines', []))} essences")
        time.sleep(1)  # be polite to poe.ninja
    if not ok:
        sys.exit("no league data fetched")
    (out / "data" / "leagues.json").write_text(json.dumps(ok), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:2])
