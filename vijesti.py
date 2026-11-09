
import json
import re
import html
from datetime import datetime, timezone
from pathlib import Path

import feedparser

IZVORI = [
    {
        "naziv": "Klix.ba",
        "url": "https://www.klix.ba/rss",
        "kategorija": "BiH"
    },
    {
        "naziv": "Radio Sarajevo",
        "url": "https://radiosarajevo.ba/rss",
        "kategorija": "BiH"
    }
]

DATOTEKA = Path("vijesti.json")
MAKSIMALNO_VIJESTI = 60


def ocisti_tekst(tekst):
    tekst = re.sub(r"<[^>]+>", " ", tekst or "")
    tekst = html.unescape(tekst)
    return re.sub(r"\s+", " ", tekst).strip()


def ucitaj_postojece():
    if not DATOTEKA.exists():
        return []

    try:
        podaci = json.loads(DATOTEKA.read_text(encoding="utf-8"))
        return podaci if isinstance(podaci, list) else []
    except (ValueError, OSError):
        return []


def prikupi_vijesti():
    postojece = ucitaj_postojece()
    rezultat = []
    vidjeni = set()

    for izvor in IZVORI:
        print("Provjeravam:", izvor["naziv"])

        feed = feedparser.parse(izvor["url"])

        for stavka in feed.entries[:20]:
            naslov = ocisti_tekst(stavka.get("title", ""))
            opis = ocisti_tekst(
                stavka.get("summary", "")
            )[:350]
            link = stavka.get("link", "")

            if not naslov or not link:
                continue

            if link in vidjeni:
                continue

            vidjeni.add(link)

            rezultat.append({
                "naslov": naslov,
                "opis": opis,
                "link": link,
                "izvor": izvor["naziv"],
                "kategorija": izvor["kategorija"],
                "datum": datetime.now(
                    timezone.utc
                ).isoformat()
            })

    for vijest in postojece:
        link = vijest.get("link")

        if link and link not in vidjeni:
            vidjeni.add(link)
            rezultat.append(vijest)

    rezultat = rezultat[:MAKSIMALNO_VIJESTI]

    DATOTEKA.write_text(
        json.dumps(
            rezultat,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("Ukupno sacuvanih vijesti:", len(rezultat))


if __name__ == "__main__":
    prikupi_vijesti()
