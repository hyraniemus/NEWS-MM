#!/usr/bin/env python3
"""Neue Projekte via TMDB hinzufügen und credits.json aktualisieren."""

import requests, json, re, time, os

TMDB_KEY   = "31106cd650aedeba650403708be48e9f"
TMDB_BASE  = "https://api.themoviedb.org/3"
IMG_BASE   = "https://image.tmdb.org/t/p/w500"
POSTER_DIR = "images/posters"
HEADERS    = {"User-Agent": "MaxMittelbach-Website/1.0"}
CU_PROFILE = "https://www.crew-united.com/de/Max-Mittelbach_93100.html"

NEW_PROJECTS = [
    {"title": "Olivia",                             "year": 2025, "role": "Schnitt",                  "type": "Serie",         "production": "Florida Film GmbH",                    "director": "Till Endemann"},
    {"title": "Songs for Joy",                      "year": 2025, "role": "Grading, Mastering, DCP",  "type": "Dokumentation", "production": "Funky Chicken Film",                   "director": "Jan Becker"},
    {"title": "Amrum",                              "year": 2025, "role": "Schnitt",                  "type": "Kinofilm",      "production": "Bombero International GmbH & Co KG",   "director": "Fatih Akin"},
    {"title": "Intimate.",                          "year": 2024, "role": "Schnitt",                  "type": "Serie",         "production": "Kleine Brüder GmbH",                   "director": "diverse"},
    {"title": "Legend of Wacken",                   "year": 2023, "role": "Schnitt",                  "type": "Serie",         "production": "Florida Film GmbH",                    "director": "diverse"},
    {"title": "SaFahri - Eine Reise zu den Elementen","year": 2021,"role": "Schnitt",                 "type": "Dokumentation", "production": "Bon Voyage Films GmbH",                "director": "diverse"},
    {"title": "Tagundnachtgleiche",                 "year": 2020, "role": "Schnitt",                  "type": "Kinofilm",      "production": "Tamtam Film GmbH",                     "director": "Lena Knauss"},
    {"title": "Der Goldene Handschuh",              "year": 2019, "role": "Schnitt",                  "type": "Kinofilm",      "production": "Bombero International GmbH & Co KG",   "director": "Fatih Akin"},
    {"title": "Tabaluga - Der Film",                "year": 2018, "role": "Schnitt",                  "type": "Kinofilm",      "production": "Tempest Film Produktion und Verleih GmbH","director": "Sven Unterwaldt"},
    {"title": "Aus dem Nichts",                     "year": 2017, "role": "Schnitt",                  "type": "Kinofilm",      "production": "Bombero International GmbH & Co KG",   "director": "Fatih Akin"},
    {"title": "Simpel",                             "year": 2016, "role": "Schnitt",                  "type": "Kinofilm",      "production": "LETTERBOX FILMPRODUKTION GmbH",         "director": "Markus Goller"},
]

def slugify(text):
    text = text.lower()
    for a, b in [("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss")]:
        text = text.replace(a, b)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"\s+", "-", text.strip())

def tmdb_search(title, year, media):
    params = {"api_key": TMDB_KEY, "query": title, "language": "de-DE"}
    if media == "movie": params["primary_release_year"] = year
    else: params["first_air_date_year"] = year
    r = requests.get(f"{TMDB_BASE}/search/{media}", params=params, headers=HEADERS, timeout=10)
    results = r.json().get("results", [])
    if not results:
        params.pop("primary_release_year", None); params.pop("first_air_date_year", None)
        r = requests.get(f"{TMDB_BASE}/search/{media}", params=params, headers=HEADERS, timeout=10)
        results = r.json().get("results", [])
    return results

def find_best(title, year, ptype):
    if ptype in ("Serie", "Dokumentation"):
        r = tmdb_search(title, year, "tv")
        if r: return r[0], "tv"
        r = tmdb_search(title, year, "movie")
        if r: return r[0], "movie"
    else:
        r = tmdb_search(title, year, "movie")
        if r: return r[0], "movie"
        r = tmdb_search(title, year, "tv")
        if r: return r[0], "tv"
    return None, None

def download_poster(poster_path, slug):
    dest = os.path.join(POSTER_DIR, f"{slug}.jpg")
    r = requests.get(f"{IMG_BASE}{poster_path}", headers=HEADERS, timeout=20, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(8192): f.write(chunk)
    return f"/images/posters/{slug}.jpg"

def main():
    with open("data/credits.json", encoding="utf-8") as f:
        data = json.load(f)

    existing_titles = {p["title"].lower() for p in data["projects"]}
    added, skipped, missing = [], [], []

    for p in NEW_PROJECTS:
        title = p["title"]
        slug  = slugify(title)

        # Intimate. bereits vorhanden → Jahr + Produktion aktualisieren
        if title.lower() == "intimate.":
            for ex in data["projects"]:
                if ex["title"].lower() == "intimate.":
                    ex["year"] = p["year"]
                    ex["production"] = p["production"]
                    print(f"  ↻ Intimate. aktualisiert → {p['year']}")
            skipped.append(title)
            continue

        if title.lower() in existing_titles:
            print(f"  – übersprungen (existiert): {title}")
            skipped.append(title)
            continue

        print(f"\n► {title} ({p['year']}) [{p['type']}]")
        result, media = find_best(title, p["year"], p["type"])
        time.sleep(0.4)

        tmdb_id = None; poster_web = "/images/posters/placeholder.svg"; poster_missing = True

        if result:
            tmdb_id = result.get("id")
            found   = result.get("title") or result.get("name","?")
            print(f"    TMDB: {found} (id={tmdb_id}, {media})")
            if result.get("poster_path"):
                try:
                    poster_web    = download_poster(result["poster_path"], slug)
                    poster_missing = False
                    print(f"    ✓ {poster_web}")
                except Exception as e:
                    print(f"    ✗ Download-Fehler: {e}")
                    missing.append(title)
            else:
                print("    ⚠ Kein Poster in TMDB")
                missing.append(title)
        else:
            print("    ✗ Kein TMDB-Treffer")
            missing.append(title)

        entry = {
            "title":          title,
            "year":           p["year"],
            "role":           p["role"],
            "type":           p["type"],
            "production":     p["production"],
            "poster":         poster_web,
            "tmdb_id":        tmdb_id,
            "poster_missing": poster_missing,
            "crewUnited":     CU_PROFILE,
        }
        data["projects"].append(entry)
        added.append(title)
        existing_titles.add(title.lower())
        time.sleep(0.4)

    # Bestehende Projekte: production-Feld ergänzen wo noch nicht vorhanden
    for p in data["projects"]:
        p.setdefault("production", "")

    # Nach Jahr absteigend sortieren
    data["projects"].sort(key=lambda x: x["year"], reverse=True)

    with open("data/credits.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # missing_posters.txt aktualisieren
    all_missing = [p["title"] + f" ({p['year']})" for p in data["projects"] if p.get("poster_missing")]
    with open("data/missing_posters.txt", "w", encoding="utf-8") as f:
        f.write("Projekte ohne Poster (manuelle Nacharbeit):\n\n")
        for m in all_missing:
            f.write(f"- {m}\n")

    print(f"\n{'='*55}")
    print(f"  Hinzugefügt: {len(added)}   Aktualisiert/Skip: {len(skipped)}   Poster fehlend: {len(missing)}")
    if missing: print("  Fehlende Poster:", ", ".join(missing))
    print(f"{'='*55}")

if __name__ == "__main__":
    main()
