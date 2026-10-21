"""Generuje samodzielny raport.html ze szkicami na podstawie wyniki.json."""
import argparse
import html
import json
import sys

e = html.escape

SEKCJE = [
    ("teraz", "Do zrobienia teraz"),
    ("bledy", "Zgłoszenia błędów"),
    ("konfiguracja", "Zmiany konfiguracji"),
    ("przypomnienia", "Przypomnienia warunkowe"),
    ("zakazy", "Zakazy dla konta klienta"),
    ("czeka", "Czeka na klienta / wstrzymane"),
    ("backlog", "Backlog produktowy"),
    ("crm", "Notatka do CRM"),
    ("kalendarz", "Kalendarz"),
    ("mail", "Szkic maila do klienta"),
]

ETYKIETY = {
    "teraz": "teraz",
    "czeka na klienta": "czeka na klienta",
    "wstrzymane": "wstrzymane",
    "backlog": "backlog",
    "zakaz": "zakaz",
}

CSS = """
body{margin:0;background:#faf8f4;color:#1f2328;font:15px/1.5 system-ui,sans-serif}
main{max-width:880px;margin:0 auto;padding:16px}
h1,h2,h3{font-family:ui-serif,Georgia,serif}
h2{border-bottom:1px solid #d8d2c4;padding-bottom:4px;margin-top:32px}
.baner{background:#d9480f;color:#fff;padding:10px 16px;font-weight:600}
nav ul{columns:2;padding-left:18px}
.karta{background:#fff;border:1px solid #e3ddd0;padding:10px 14px;margin:10px 0}
.karta h3{margin:0 0 4px;font-size:1.05em}
.meta{color:#5c636a;font-size:.88em}
.et{display:inline-block;font:600 .75em system-ui;padding:1px 7px;border-radius:3px;color:#fff;background:#777;margin-right:6px;text-transform:uppercase}
.et-teraz{background:#d9480f}.et-czeka{background:#1c6ea4}.et-wstrzymane{background:#777}
.et-backlog{background:#7b5ea7}.et-zakaz{background:#c92a2a}
blockquote{margin:6px 0;padding:4px 10px;border-left:3px solid #d9480f;background:#f3efe6;font:.85em ui-monospace,monospace}
.ostrz{color:#c92a2a;font-weight:600;font-size:.88em}
.brak{color:#8a8f94;font-style:italic}
textarea{width:100%;min-height:320px;font:13px ui-monospace,monospace;box-sizing:border-box}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #e3ddd0;padding:4px 8px;text-align:left}
@media print{.baner{color:#000;background:none;border:2px solid #000}nav{display:none}.karta{break-inside:avoid}}
"""


def _wybierz(wyniki, klucz):
    el = wyniki.get("elementy", [])
    if klucz == "teraz":
        return [x for x in el if x.get("status") == "teraz"]
    if klucz == "bledy":
        return [x for x in el if x.get("typ") == "błąd"]
    if klucz == "konfiguracja":
        return [x for x in el if x.get("typ") == "zmiana konfiguracji"]
    if klucz == "przypomnienia":
        return [x for x in el if x.get("przypomnienie")]
    if klucz == "zakazy":
        return [x for x in el if x.get("status") == "zakaz"]
    if klucz == "czeka":
        return [x for x in el if x.get("status") in ("czeka na klienta", "wstrzymane")]
    if klucz == "backlog":
        return [x for x in el if x.get("typ") == "prośba o funkcję"]
    return el


def _daty(x):
    """Zwraca listę (data, rodzaj) elementu."""
    wyn = []
    if x.get("termin"):
        wyn.append((x["termin"], "termin"))
    if x.get("termin_do"):
        wyn.append((x["termin_do"], "termin do"))
    p = x.get("przypomnienie")
    if p and p.get("data"):
        wyn.append((p["data"], "przypomnienie"))
    return wyn


def _etykieta(status):
    klasa = {"czeka na klienta": "czeka"}.get(status, status)
    return '<span class="et et-%s">%s</span>' % (e(str(klasa)), e(str(ETYKIETY.get(status, status))))


def _meta(x):
    czesci = []
    if x.get("wlasciciel"):
        czesci.append("właściciel: " + e(x["wlasciciel"]))
    if x.get("zatwierdza"):
        czesci.append("zatwierdza: " + e(x["zatwierdza"]))
    if x.get("termin"):
        czesci.append("termin: " + e(x["termin"]) + (" (" + e(x["termin_opis"]) + ")" if x.get("termin_opis") else ""))
    if x.get("termin_do"):
        czesci.append("do: " + e(x["termin_do"]))
    if x.get("warunek"):
        czesci.append("warunek: " + e(x["warunek"]))
    return " · ".join(czesci)


def _karta(x, rozszerzona=False):
    out = ['<div class="karta">']
    out.append("<h3>%s%s <small>(%s)</small></h3>" % (_etykieta(x.get("status", "")), e(x.get("tytul", "")), e(x.get("id", ""))))
    if x.get("opis"):
        out.append("<div>%s</div>" % e(x["opis"]))
    m = _meta(x)
    if m:
        out.append('<div class="meta">%s</div>' % m)
    p = x.get("przypomnienie")
    if p:
        out.append('<div class="meta">przypomnienie: %s · %s · maks. %s raz</div>' % (
            e(str(p.get("data", ""))), e(str(p.get("tresc", ""))), e(str(p.get("maks_razy", "?")))))
    if x.get("do_klienta") is False:
        out.append('<div class="meta">wewnętrzne, nie trafia do maila</div>')
    if not x.get("cytaty_zweryfikowane", False):
        out.append('<div class="ostrz">Uwaga: cytaty niezweryfikowane względem transkrypcji.</div>')
    for c in x.get("cytaty", []):
        out.append("<blockquote>%s</blockquote>" % e(c))
    out.append("</div>")
    return "\n".join(out)


def _lista_kart(elementy):
    if not elementy:
        return '<p class="brak">brak</p>'
    return "\n".join(_karta(x) for x in elementy)


def _sekcja_crm(wyniki):
    el = wyniki.get("elementy", [])
    grupy = [
        ("Ryzyka", [x for x in el if x.get("kategoria_crm") == "ryzyko"]),
        ("Sukcesy", [x for x in el if x.get("kategoria_crm") == "sukces"]),
        ("Pozostałe informacje handlowe", [x for x in el if x.get("typ") == "informacja handlowa" and not x.get("kategoria_crm")]),
    ]
    out = []
    for nazwa, lista in grupy:
        out.append("<h3>%s</h3>" % e(nazwa))
        out.append(_lista_kart(lista))
    return "\n".join(out), sum(len(l) for _, l in grupy)


def _sekcja_kalendarz(wyniki):
    wiersze = []
    for x in wyniki.get("elementy", []):
        for data, rodzaj in _daty(x):
            wiersze.append((data, rodzaj, x))
    wiersze.sort(key=lambda w: (w[0], w[2].get("id", "")))
    if not wiersze:
        return '<p class="brak">brak</p>', 0
    out = ["<table><tr><th>Data</th><th>Rodzaj</th><th>Element</th><th>Właściciel</th></tr>"]
    for data, rodzaj, x in wiersze:
        out.append("<tr><td>%s</td><td>%s</td><td>%s (%s)</td><td>%s</td></tr>" % (
            e(data), e(rodzaj), e(x.get("tytul", "")), e(x.get("id", "")), e(x.get("wlasciciel") or "")))
    out.append("</table>")
    return "\n".join(out), len(wiersze)


def szkic_maila(wyniki):
    """Tekst maila do klienta. Tylko elementy z do_klienta == True."""
    el = [x for x in wyniki.get("elementy", []) if x.get("do_klienta") is True]
    robimy = [x for x in el if x.get("status") == "teraz"]
    potrzebujemy = [x for x in el if x.get("status") == "czeka na klienta"]
    czeka = [x for x in el if x.get("status") not in ("teraz", "czeka na klienta")]

    def wiersz(x):
        s = "- %s" % x.get("tytul", "")
        if x.get("opis"):
            s += ": " + x["opis"]
        if x.get("termin"):
            s += " (termin: %s)" % x["termin"]
        if x.get("warunek"):
            s += " [warunek: %s]" % x["warunek"]
        return s

    linie = ["Dzień dobry,", "", "poniżej podsumowanie ustaleń ze spotkania z %s." % wyniki.get("data_spotkania", "")]
    for nazwa, lista in (("Co robimy", robimy), ("Czego od Was potrzebujemy", potrzebujemy), ("Co czeka", czeka)):
        linie += ["", nazwa + ":"]
        linie += [wiersz(x) for x in lista] or ["- brak"]
    linie += ["", "W razie pytań jestem do dyspozycji.", "Marek"]
    return "\n".join(linie)


def generuj_html(wyniki):
    tresci = {}
    liczniki = {}
    for klucz, _ in SEKCJE:
        if klucz == "crm":
            tresci[klucz], liczniki[klucz] = _sekcja_crm(wyniki)
        elif klucz == "kalendarz":
            tresci[klucz], liczniki[klucz] = _sekcja_kalendarz(wyniki)
        elif klucz == "mail":
            tresci[klucz] = '<textarea readonly aria-label="Szkic maila">%s</textarea>' % e(szkic_maila(wyniki))
            liczniki[klucz] = sum(1 for x in wyniki.get("elementy", []) if x.get("do_klienta") is True)
        else:
            lista = _wybierz(wyniki, klucz)
            tresci[klucz] = _lista_kart(lista)
            liczniki[klucz] = len(lista)
    spis = "".join('<li><a href="#%s">%s</a> (%d)</li>' % (k, e(n), liczniki[k]) for k, n in SEKCJE)
    sekcje = "".join(
        '<section id="%s"><h2>%s</h2>'
        '<label><input type="checkbox"> zatwierdzam</label>%s</section>' % (k, e(n), tresci[k])
        for k, n in SEKCJE)
    return (
        '<!doctype html><html lang="pl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>Szkice do zatwierdzenia</title><style>%s</style></head><body>"
        '<div class="baner">Szkice do zatwierdzenia. Nic nie zostało wysłane.</div><main>'
        "<h1>Szkice po spotkaniu %s</h1><p class=\"meta\">Źródło: %s</p>"
        "<nav><ul>%s</ul></nav>%s</main></body></html>"
    ) % (CSS, e(str(wyniki.get("data_spotkania", ""))), e(str(wyniki.get("zrodlo", ""))), spis, sekcje)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generuje raport.html z wyniki.json")
    ap.add_argument("wyniki")
    ap.add_argument("--wyjscie", default="raport.html")
    a = ap.parse_args(argv)
    with open(a.wyniki, encoding="utf-8") as f:
        wyniki = json.load(f)
    with open(a.wyjscie, "w", encoding="utf-8") as f:
        f.write(generuj_html(wyniki))
    print("Zapisano " + a.wyjscie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
