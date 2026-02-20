import json, urllib.request
from datetime import datetime, UTC
from pathlib import Path

COUNTRIES = ["us","gb","de","fr","br","jp","kr","in","id","au"]
DATA_DIR = Path("data/snapshots")

def fetch_top_apps(country):
    url = f"https://itunes.apple.com/{country}/rss/topfreeapplications/limit=200/genre=6008/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        apps = []
        for rank, entry in enumerate(data.get("feed",{}).get("entry",[]), start=1):
            apps.append({
                "rank": rank,
                "id": entry["id"]["attributes"]["im:id"],
                "name": entry["im:name"]["label"],
                "developer": entry["im:artist"]["label"]
            })
        return apps
    except Exception as e:
        print(f"  ✗ {country.upper()}: {e}")
        return []

def main():
    print("🔍 Парсим топ Photo & Video apps...\n")
    snapshot = {"date": datetime.now(UTC).strftime("%Y-%m-%d"), "countries": {}}
    for country in COUNTRIES:
        print(f"  {country.upper()}...", end=" ", flush=True)
        apps = fetch_top_apps(country)
        if apps:
            snapshot["countries"][country] = apps
            print(f"✓ {len(apps)} приложений")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{snapshot['date']}.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    print(f"\n✅ Готово! Сохранено: {path}")

if __name__ == "__main__":
    main()
