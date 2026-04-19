#!/usr/bin/env python3
"""
Schritt 1: Crew United Profil scrapen und Filmografie extrahieren.
Speichert Ergebnisse als raw_credits.json.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys

PROFILE_URL = "https://www.crew-united.com/de/Max-Mittelbach_93100.html"
OUTPUT_FILE = "data/raw_credits.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def slugify(text):
    text = text.lower()
    text = re.sub(r"[äÄ]", "ae", text)
    text = re.sub(r"[öÖ]", "oe", text)
    text = re.sub(r"[üÜ]", "ue", text)
    text = re.sub(r"ß", "ss", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text.strip())
    return text

def fetch_page(url):
    print(f"  GET {url}")
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_filmography(html):
    soup = BeautifulSoup(html, "html.parser")
    projects = []

    # ── Strategie 1: Tabelle mit Klasse die "filmography" o.ä. enthält ──
    # Crew United nutzt verschiedene Strukturen – wir probieren mehrere.

    # Suche nach typischen Abschnitt-Überschriften
    sections = soup.find_all(["section", "div"], class_=re.compile(r"filmograph|credit|project|work", re.I))

    # Fallback: alle Tabellen
    if not sections:
        sections = soup.find_all("table")

    for section in sections:
        rows = section.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            texts = [c.get_text(strip=True) for c in cells]
            # Heuristik: Zeile enthält Jahr (4-stellige Zahl)
            year_match = None
            for t in texts:
                m = re.search(r"\b(19|20)\d{2}\b", t)
                if m:
                    year_match = int(m.group())
                    break
            if not year_match:
                continue

            # Link zum Projekt?
            link = row.find("a", href=True)
            crew_link = ""
            if link:
                href = link["href"]
                if not href.startswith("http"):
                    href = "https://www.crew-united.com" + href
                crew_link = href

            title = texts[0] if texts else ""
            if not title and link:
                title = link.get_text(strip=True)

            projects.append({
                "title": title,
                "year": year_match,
                "raw_cells": texts,
                "crewUnited": crew_link,
            })

    return projects, soup

def extract_structured(html):
    """Versucht strukturiertere Extraktion aus typischen Crew-United-Elementen."""
    soup = BeautifulSoup(html, "html.parser")
    projects = []

    # Crew United zeigt Projekte häufig als Liste von .project-item, .list-item o.ä.
    candidates = soup.find_all(
        lambda tag: tag.name in ["li", "div", "article"]
        and any(
            cls in " ".join(tag.get("class", []))
            for cls in ["project", "film", "credit", "item", "entry", "work"]
        )
    )

    for item in candidates:
        text = item.get_text(" ", strip=True)
        year_m = re.search(r"\b(19|20)\d{2}\b", text)
        if not year_m:
            continue
        year = int(year_m.group())

        # Titel: erstes <a> oder <strong>/<h3>/<h4>
        title_tag = item.find(["h2", "h3", "h4", "strong", "a"])
        title = title_tag.get_text(strip=True) if title_tag else text[:60]

        link = item.find("a", href=True)
        crew_link = ""
        if link:
            href = link["href"]
            if not href.startswith("http"):
                href = "https://www.crew-united.com" + href
            crew_link = href

        # Rolle: suche nach Schlüsselwörtern
        role = ""
        role_keywords = [
            "Schnittassistenz", "Schnitt", "DI Producer", "Colorist",
            "Postproduction", "Editor", "VFX", "Regie", "Kamera"
        ]
        for kw in role_keywords:
            if kw.lower() in text.lower():
                role = kw
                break

        projects.append({
            "title": title,
            "year": year,
            "role": role,
            "crewUnited": crew_link,
            "raw_text": text[:200],
        })

    return projects

def save_page_debug(html, path="data/debug_crew_united.html"):
    """Speichert die rohe HTML zur manuellen Inspektion."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [debug] HTML gespeichert: {path}")

def main():
    import os
    os.makedirs("data", exist_ok=True)

    print("=" * 60)
    print("Crew United Profil-Scraper")
    print("=" * 60)
    print(f"\nProfil: {PROFILE_URL}\n")

    try:
        html = fetch_page(PROFILE_URL)
    except Exception as e:
        print(f"  FEHLER beim Laden: {e}")
        sys.exit(1)

    save_page_debug(html)

    print("\n── Strategie 1: Tabellen-Extraktion ──")
    tab_projects, soup = parse_filmography(html)
    print(f"  Gefunden: {len(tab_projects)} Einträge")

    print("\n── Strategie 2: Element-basierte Extraktion ──")
    elem_projects = extract_structured(html)
    print(f"  Gefunden: {len(elem_projects)} Einträge")

    # Seitenstruktur analysieren
    print("\n── Seitenstruktur-Analyse ──")
    page_title = soup.title.get_text(strip=True) if soup.title else "?"
    print(f"  Seitentitel: {page_title}")

    # Alle Texte die nach Projekten aussehen
    all_years = re.findall(r"\b(20[0-1]\d|199\d)\b", soup.get_text())
    year_counts = {}
    for y in all_years:
        year_counts[y] = year_counts.get(y, 0) + 1
    print(f"  Jahre auf der Seite: {sorted(year_counts.items(), key=lambda x: -x[1])[:10]}")

    # Alle Links die nach Projekten aussehen
    project_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/de/" in href and re.search(r"_\d{4,}", href):
            project_links.append({
                "text": a.get_text(strip=True),
                "href": href if href.startswith("http") else "https://www.crew-united.com" + href
            })
    project_links = [l for l in project_links if l["text"]]
    print(f"  Projekt-Links gefunden: {len(project_links)}")
    for pl in project_links[:15]:
        print(f"    · {pl['text'][:50]:50s}  {pl['href']}")

    # Alle sichtbaren Überschriften
    print("\n  Überschriften auf der Seite:")
    for h in soup.find_all(["h1","h2","h3","h4"])[:20]:
        t = h.get_text(strip=True)
        if t:
            print(f"    <{h.name}> {t[:80]}")

    # Rohdaten speichern
    raw = {
        "profile_url": PROFILE_URL,
        "page_title": page_title,
        "project_links": project_links,
        "table_projects": tab_projects,
        "element_projects": elem_projects,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    print(f"\n  [OK] Rohdaten gespeichert: {OUTPUT_FILE}")
    print("\n" + "=" * 60)
    print("Bitte analysiere die Ausgabe und bestätige Schritt 2.")
    print("=" * 60)

if __name__ == "__main__":
    main()
