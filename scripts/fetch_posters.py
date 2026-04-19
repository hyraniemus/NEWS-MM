#!/usr/bin/env python3
"""
Schritt 2 & 3: TMDB Poster laden + credits.json erzeugen.
"""

import requests
import json
import re
import time
import os

TMDB_KEY   = "31106cd650aedeba650403708be48e9f"
TMDB_BASE  = "https://api.themoviedb.org/3"
IMG_BASE   = "https://image.tmdb.org/t/p/w500"
POSTER_DIR = "images/posters"
OUT_JSON   = "data/credits.json"
MISSING_TXT = "data/missing_posters.txt"

HEADERS = {"User-Agent": "MaxMittelbach-Website/1.0"}

# ── Type mapping to German labels ────────────────────────────────────
TYPE_MAP = {
    "Kinofilm":    "Kinofilm",
    "Serie":       "Serie",
    "Dokumentation": "Dokumentation",
}

def slugify(text):
    text = text.lower()
    text = re.sub(r"[äÄ]", "ae", text)
    text = re.sub(r"[öÖ]", "oe", text)
    text = re.sub(r"[üÜ]", "ue", text)
    text = re.sub(r"ß",    "ss", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text

def tmdb_search(title, year, media="movie"):
    endpoint = f"{TMDB_BASE}/search/{media}"
    params = {
        "api_key":  TMDB_KEY,
        "query":    title,
        "language": "de-DE",
    }
    if media == "movie":
        params["primary_release_year"] = year
    else:
        params["first_air_date_year"] = year
    try:
        r = requests.get(endpoint, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            # retry without year constraint
            params.pop("primary_release_year", None)
            params.pop("first_air_date_year", None)
            r = requests.get(endpoint, params=params, headers=HEADERS, timeout=10)
            r.raise_for_status()
            results = r.json().get("results", [])
        return results
    except Exception as e:
        print(f"    TMDB-Fehler ({media}): {e}")
        return []

def find_best_match(title, year, project_type):
    """Suche zuerst als Film, dann als TV-Serie."""
    # TV-Projekte direkt als tv suchen
    if project_type in ("Serie",):
        results = tmdb_search(title, year, "tv")
        if results:
            return results[0], "tv"
        results = tmdb_search(title, year, "movie")
        if results:
            return results[0], "movie"
    else:
        results = tmdb_search(title, year, "movie")
        if results:
            return results[0], "movie"
        results = tmdb_search(title, year, "tv")
        if results:
            return results[0], "tv"
    return None, None

def download_poster(poster_path, slug):
    url  = f"{IMG_BASE}{poster_path}"
    dest = os.path.join(POSTER_DIR, f"{slug}.jpg")
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"    ✓ Poster gespeichert: {dest}")
        return f"/images/posters/{slug}.jpg"
    except Exception as e:
        print(f"    ✗ Download-Fehler: {e}")
        return None

def main():
    os.makedirs(POSTER_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    with open("data/raw_credits.json", encoding="utf-8") as f:
        raw = json.load(f)
    projects_in = raw["projects"]

    print("=" * 62)
    print(f"TMDB Poster-Suche für {len(projects_in)} Projekte")
    print("=" * 62)

    projects_out = []
    missing = []

    for p in projects_in:
        title = p["title"]
        year  = p["year"]
        role  = p["role"]
        ptype = p["type"]
        slug  = slugify(title)

        print(f"\n► {title} ({year}) [{ptype}]")

        result, media_type = find_best_match(title, year, ptype)
        time.sleep(0.4)  # rate limiting

        tmdb_id      = None
        poster_web   = "/images/posters/placeholder.svg"
        poster_missing = True

        if result:
            tmdb_id = result.get("id")
            poster_path = result.get("poster_path")
            found_title = result.get("title") or result.get("name", "?")
            print(f"    TMDB-Treffer: {found_title} (id={tmdb_id}, media={media_type})")

            if poster_path:
                dl = download_poster(poster_path, slug)
                if dl:
                    poster_web    = dl
                    poster_missing = False
            else:
                print("    ⚠ Kein Poster in TMDB vorhanden")
        else:
            print("    ✗ Kein TMDB-Treffer")
            missing.append(f"{title} ({year})")

        if poster_missing and result is None:
            missing.append(f"{title} ({year})")  # already added above for no-result

        entry = {
            "title":          title,
            "year":           year,
            "role":           role,
            "type":           ptype,
            "poster":         poster_web,
            "tmdb_id":        tmdb_id,
            "poster_missing": poster_missing,
            "crewUnited":     p.get("crewUnited", ""),
        }
        projects_out.append(entry)
        time.sleep(0.6)

    # Sort by year descending
    projects_out.sort(key=lambda x: x["year"], reverse=True)

    # Write credits.json
    output = {"projects": projects_out}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] credits.json gespeichert: {OUT_JSON}")

    # Deduplicate missing list
    missing_unique = sorted(set(missing))
    with open(MISSING_TXT, "w", encoding="utf-8") as f:
        f.write("Projekte ohne Poster (manuelle Nacharbeit):\n\n")
        for m in missing_unique:
            f.write(f"- {m}\n")
    print(f"[OK] missing_posters.txt gespeichert: {MISSING_TXT}")

    # Summary
    total    = len(projects_out)
    ok_count = sum(1 for p in projects_out if not p["poster_missing"])
    miss_count = len(missing_unique)

    print("\n" + "=" * 62)
    print("ZUSAMMENFASSUNG")
    print("=" * 62)
    print(f"  Projekte gesamt:          {total}")
    print(f"  Poster erfolgreich:       {ok_count}")
    print(f"  Poster fehlend:           {miss_count}")
    if missing_unique:
        print("\n  Fehlende Poster:")
        for m in missing_unique:
            print(f"    · {m}")
    print("=" * 62)

if __name__ == "__main__":
    main()
