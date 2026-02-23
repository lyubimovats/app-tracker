import json
from pathlib import Path
from datetime import date

data = json.loads(Path("data/rising_apps.json").read_text())
apps = data.get("rising", [])

# Группируем по стране
by_country = {}
for app in apps:
    c = app["country"]
    if c not in by_country:
        by_country[c] = []
    by_country[c].append(app)

# Генерируем отчёт
lines = [f"📱 Rising Apps — {date.today().strftime('%b %d, %Y')}\n"]

for country, country_apps in by_country.items():
    lines.append(f"{country}:")
    for app in country_apps:
        lines.append(f"  • {app['name']} (+{app['delta']}, #{app['prev_rank']} → #{app['curr_rank']})")
    lines.append("")

report = "\n".join(lines)
print(report)

Path("data/report.txt").write_text(report)
print("💾 Сохранено: data/report.txt")
