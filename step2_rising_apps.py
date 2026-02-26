import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

MIN_DELTA = 10

AI_KEYWORDS = [
    'ai', 'a.i.',
    'generator', 'generate', 'generative',
    'face swap', 'reface', 'avatar',
    'photo editor', 'video editor',
    'aura', 'glam', 'remini', 'toonapp', 'retake', 'pose',
    'photoroom', 'faceapp', 'facelab', 'prettyup', 'visio',
    'ageroom', 'reface', 'facetune', 'lensa', 'meitu',
    'dreamina', 'midjourney', 'stable', 'diffusion',
]

EXCLUDE = [
    'instagram', 'youtube', 'tiktok', 'snapchat', 'meta', 'google',
    'apple', 'canva', 'capcut', 'netflix', 'spotify', 'pinterest',
    'twitter', 'whatsapp', 'telegram', 'facebook', 'messenger',
]

def is_ai_app(name):
    name_lower = name.lower()
    if any(ex in name_lower for ex in EXCLUDE):
        return False
    return any(kw in name_lower for kw in AI_KEYWORDS)

def find_snapshot(files, days_ago):
    target_date = datetime.today().date() - timedelta(days=days_ago)
    candidates = []
    for f in files:
        try:
            d = datetime.strptime(f.stem, "%Y-%m-%d").date()
            if d <= target_date:
                candidates.append((d, f))
        except ValueError:
            continue
    if candidates:
        return max(candidates, key=lambda x: x[0])[1]
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Сравнить с N дней назад (по умолчанию 1)"
    )
    args = parser.parse_args()

    snapshots_dir = Path("data/snapshots")
    files = sorted(snapshots_dir.glob("*.json"))

    if len(files) < 2:
        print("❌ Нужно минимум 2 снапшота")
        return

    curr_file = files[-1]
    prev_file = find_snapshot(files[:-1], days_ago=args.days)

    if not prev_file:
        print(f"❌ Нет снапшота за {args.days} дней назад, используем ближайший")
        prev_file = files[-2]

    window_label = f"{args.days} {'день' if args.days == 1 else 'дней'}"

    prev_raw = json.loads(prev_file.read_text())
    curr_raw = json.loads(curr_file.read_text())
    prev = {k.upper(): v for k, v in prev_raw.get("countries", prev_raw).items()}
    curr = {k.upper(): v for k, v in curr_raw.get("countries", curr_raw).items()}

    print(f"🚀 Сравниваем {prev_file.stem} → {curr_file.stem} (окно: {window_label})\n")

    rising = []
    for country in curr:
        if country not in prev:
            continue
        prev_map = {a["name"]: a["rank"] for a in prev[country]}
        for app in curr[country]:
            name = app["name"]
            if name not in prev_map:
                continue
            delta = prev_map[name] - app["rank"]
            if delta >= MIN_DELTA and is_ai_app(name):
                rising.append({
                    "country": country,
                    "name": name,
                    "developer": app.get("developer", ""),
                    "prev_rank": prev_map[name],
                    "curr_rank": app["rank"],
                    "delta": delta,
                })

    rising.sort(key=lambda x: x["delta"], reverse=True)

    by_country = {}
    for app in rising:
        c = app["country"]
        if c not in by_country:
            by_country[c] = []
        by_country[c].append(app)

    print(f"{'Страна':<6} {'Приложение':<35} {'Было':>5}  {'Стало':>6}  {'Δ':>4}")
    print("─" * 60)
    for app in rising:
        print(f"{app['country']:<6} {app['name'][:34]:<35} {app['prev_rank']:>5} → #{app['curr_rank']:<5} +{app['delta']}")

    print(f"\n✅ Найдено {len(rising)} AI приложений растущих на {MIN_DELTA}+ позиций (за {window_label})\n")

    app_markets = {}
    for app in rising:
        n = app["name"]
        if n not in app_markets:
            app_markets[n] = []
        app_markets[n].append(app["country"])

    multi_market = {n: m for n, m in app_markets.items() if len(m) > 1}
    if multi_market:
        print("🌍 Растут на нескольких рынках:")
        for name, markets in multi_market.items():
            print(f"  • {name[:40]} → {', '.join(markets)}")
        print()

    output_file = "data/rising_apps.json" if args.days == 1 else f"data/rising_apps_{args.days}d.json"
    Path(output_file).write_text(
        json.dumps({
            "rising": rising,
            "by_country": by_country,
            "meta": {
                "prev_date": prev_file.stem,
                "curr_date": curr_file.stem,
                "days": args.days
            }
        }, ensure_ascii=False, indent=2)
    )
    print(f"💾 Сохранено: {output_file}")

if __name__ == "__main__":
    main()
