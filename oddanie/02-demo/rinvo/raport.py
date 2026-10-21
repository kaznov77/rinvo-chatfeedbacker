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
:root{--tlo:#E9EDF1;--arkusz:#fff;--atrament:#14213D;--szary:#5B6675;--linia:#D3DAE2;
--teraz:#F2B705;--czeka:#2F6FB3;--wstrzymane:#8A94A3;--backlog:#6B5CA5;--zakaz:#C0392B}
*{box-sizing:border-box}
body{margin:0;background:var(--tlo);color:var(--atrament);font:16px/1.55 "Avenir Next","Segoe UI Variable","Segoe UI",system-ui,sans-serif;font-variant-numeric:tabular-nums}
.uklad{display:grid;grid-template-columns:230px minmax(0,760px);gap:32px;max-width:1060px;margin:0 auto;padding:24px 20px 80px}
nav{position:sticky;top:20px;align-self:start;font-size:.92em}
nav ul{list-style:none;margin:12px 0 0;padding:0}
nav a{display:flex;justify-content:space-between;padding:5px 10px;border-radius:6px;color:var(--atrament);text-decoration:none}
nav a:hover,nav a:focus-visible{background:var(--arkusz)}
nav .ile{color:var(--szary)}
.baner{font-size:.9em;color:var(--szary);margin:0 0 6px}
h1{font-size:1.9em;line-height:1.2;margin:0 0 4px;font-weight:700;letter-spacing:-.01em}
h2{font-size:1.25em;margin:44px 0 12px;display:flex;align-items:baseline;gap:12px}
h2 .ile{font-weight:500;color:var(--szary);font-size:.8em}
h3{font-size:1em;margin:18px 0 8px;color:var(--szary)}
.pasek{display:flex;height:14px;border-radius:7px;overflow:hidden;margin:20px 0 8px;background:var(--linia)}
.pasek span{display:block}
.legenda{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88em;color:var(--szary);margin:0}
.legenda i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}
.postep{margin:18px 0 0;padding:12px 16px;background:var(--atrament);color:#fff;border-radius:8px;font-weight:600}
.karta{background:var(--arkusz);border-left:5px solid var(--wstrzymane);border-radius:4px 8px 8px 4px;margin:8px 0;box-shadow:0 1px 0 var(--linia)}
.k-teraz{border-left-color:var(--teraz)}.k-czeka{border-left-color:var(--czeka)}.k-backlog{border-left-color:var(--backlog)}.k-zakaz{border-left-color:var(--zakaz)}
.karta summary{list-style:none;cursor:pointer;padding:12px 16px 12px 14px;display:grid;grid-template-columns:auto 1fr;gap:2px 12px}
.karta summary::-webkit-details-marker{display:none}
.karta summary:focus-visible,input:focus-visible{outline:3px solid var(--czeka);outline-offset:2px}
.karta input{margin:4px 0 0;width:18px;height:18px;accent-color:var(--atrament);grid-row:span 3}
.tytul{font-weight:600}
.et{font-size:.8em;font-weight:600;padding:1px 8px;border-radius:10px;margin-left:8px;white-space:nowrap;background:var(--tlo);color:var(--szary)}
.et-zakaz{background:#F6DEDB;color:var(--zakaz)}.et-teraz{background:#FDF0C4;color:#6B5200}
.skrot{color:var(--atrament)}
.meta{color:var(--szary);font-size:.88em;display:flex;flex-wrap:wrap;gap:4px 16px}
.karta.ok{opacity:.55}
.wiecej{padding:0 16px 14px 44px;border-top:1px solid var(--tlo)}
.wiecej p{max-width:68ch}
blockquote{margin:8px 0;padding:6px 12px;border-left:2px solid var(--linia);color:var(--szary);font-style:italic}
.ostrz{color:var(--zakaz);font-weight:600;font-size:.88em}
.brak{color:var(--szary)}
table{border-collapse:collapse;width:100%;background:var(--arkusz);border-radius:8px;overflow:hidden;font-size:.92em}
td,th{padding:7px 12px;text-align:left;border-bottom:1px solid var(--tlo)}th{color:var(--szary);font-weight:600}
textarea{width:100%;min-height:360px;padding:16px;border:1px solid var(--linia);border-radius:8px;font:15px/1.6 inherit;color:var(--atrament)}
@media (max-width:820px){.uklad{grid-template-columns:1fr}nav{position:static}}
@media (prefers-reduced-motion:no-preference){.karta{transition:opacity .2s}}
@media print{nav,.postep,.karta input{display:none}.uklad{display:block}details>.wiecej{display:block}.karta{break-inside:avoid}}
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
    return "".join("<span>%s</span>" % c for c in czesci)


def _skrot(x):
    """Krótki opis: pole skrot, a gdy go brak, pierwsze zdanie opisu."""
    if x.get("skrot"):
        return x["skrot"]
    opis = x.get("opis", "")
    return opis.split(". ")[0].rstrip(".") + "." if opis else ""


def _dm(data):
    """2026-10-08 -> 8.10"""
    try:
        r, m, d = data.split("-")
        return "%d.%d" % (int(d), int(m))
    except (ValueError, AttributeError):
        return data or ""


def _karta(x):
    """Zwinięta karta: tytuł i skrót na wierzchu, szczegóły po rozwinięciu."""
    klasa = {"czeka na klienta": "czeka", "wstrzymane": "wstrzymane"}.get(x.get("status"), x.get("status", ""))
    out = ['<details class="karta k-%s"><summary>' % e(str(klasa))]
    out.append('<input type="checkbox" class="zatw" aria-label="Zatwierdź %s" onclick="event.stopPropagation()">' % e(x.get("id", "")))
    out.append('<div><span class="tytul">%s</span>%s</div>' % (e(x.get("tytul", "")), _etykieta(x.get("status", ""))))
    out.append('<div class="skrot">%s</div>' % e(_skrot(x)))
    krotko = []
    if x.get("wlasciciel"):
        krotko.append(e(x["wlasciciel"]))
    if x.get("termin"):
        krotko.append("termin " + e(_dm(x["termin"])) + ("–" + e(_dm(x["termin_do"])) if x.get("termin_do") else ""))
    if x.get("warunek"):
        krotko.append("warunkowe")
    if krotko:
        out.append('<div class="meta">%s</div>' % "".join("<span>%s</span>" % k for k in krotko))
    if not x.get("cytaty_zweryfikowane", False):
        out.append('<div class="ostrz">Uwaga: cytaty niezweryfikowane względem transkrypcji.</div>')
    out.append('</summary><div class="wiecej"><p class="meta">%s</p>' % e(x.get("id", "")))
    if x.get("opis"):
        out.append("<p>%s</p>" % e(x["opis"]))
    m = _meta(x)
    if m:
        out.append('<div class="meta">%s</div>' % m)
    p = x.get("przypomnienie")
    if p:
        out.append('<div class="meta">przypomnienie: %s · %s · maks. %s raz</div>' % (
            e(str(p.get("data", ""))), e(str(p.get("tresc", ""))), e(str(p.get("maks_razy", "?")))))
    if x.get("do_klienta") is False:
        out.append('<div class="meta">wewnętrzne, nie trafia do maila</div>')
    for c in x.get("cytaty", []):
        out.append("<blockquote>%s</blockquote>" % e(c))
    out.append("</div></details>")
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
    """Krótki mail do klienta: same punkty z terminami. Tylko elementy z do_klienta == True."""
    el = [x for x in wyniki.get("elementy", []) if x.get("do_klienta") is True]
    robimy = [x for x in el if x.get("status") == "teraz" and x.get("typ") != "zakaz"]
    potrzebujemy = [x for x in el if x.get("status") == "czeka na klienta"]
    odkladamy = [x for x in el if x.get("status") == "wstrzymane" and x.get("typ") != "zakaz"]
    backlog = [x for x in el if x.get("status") == "backlog"]
    dzis = wyniki.get("data_spotkania")

    def punkt(x):
        data = x.get("termin") or (x.get("przypomnienie") or {}).get("data")
        s = "- " + x.get("tytul", "")
        if data:
            s += " (dziś)" if data == dzis else " (do %s)" % _dm(data)
        return s

    linie = ["Cześć,", "", "dzięki za rozmowę %s. W skrócie, co ustaliliśmy:" % _dm(dzis or "")]
    for naglowek, lista in (("Po naszej stronie:", robimy), ("Potrzebujemy od Ciebie:", potrzebujemy),
                            ("Czeka na Twój sygnał:", odkladamy)):
        if lista:
            linie += ["", naglowek] + [punkt(x) for x in lista]
    if backlog:
        linie += ["", "Zapisane jako prośby o nowe funkcje (bez terminu): "
                  + "; ".join(x.get("tytul", "") for x in backlog) + "."]
    linie += ["", "Daj znać, jeśli coś pominąłem.", "Marek"]
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
    spis = "".join('<li><a href="#%s"><span>%s</span><span class="ile">%d</span></a></li>' % (k, e(n), liczniki[k]) for k, n in SEKCJE)
    sekcje = "".join('<section id="%s"><h2>%s<span class="ile">%d</span></h2>%s</section>' % (k, e(n), liczniki[k], tresci[k])
                     for k, n in SEKCJE)
    el = wyniki.get("elementy", [])
    statusy = [("teraz", "do zrobienia teraz", "teraz"), ("czeka na klienta", "czeka na klienta", "czeka"),
               ("wstrzymane", "wstrzymane", "wstrzymane"), ("backlog", "backlog", "backlog"), ("zakaz", "zakazy", "zakaz")]
    pasek, legenda = [], []
    for st, nazwa, kl in statusy:
        n = sum(1 for x in el if x.get("status") == st)
        if n:
            pasek.append('<span style="flex:%d;background:var(--%s)" title="%s: %d"></span>' % (n, kl, e(nazwa), n))
            legenda.append('<span><i style="background:var(--%s)"></i>%s %d</span>' % (kl, e(nazwa), n))
    js = ("const b=[...document.querySelectorAll('.zatw')],p=document.getElementById('postep');"
          "function o(){let n=0;b.forEach(c=>{c.closest('.karta').classList.toggle('ok',c.checked);n+=c.checked});"
          "p.textContent='Zatwierdzono '+n+' z '+b.length}b.forEach(c=>c.addEventListener('change',o));o()")
    return (
        '<!doctype html><html lang="pl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>Ustalenia po spotkaniu %s</title><style>%s</style></head><body><div class=\"uklad\">"
        "<nav aria-label=\"Sekcje\"><strong>Sekcje</strong><ul>%s</ul></nav><main>"
        '<p class="baner">Szkice do zatwierdzenia. Nic nie zostało wysłane.</p>'
        "<h1>Ustalenia po spotkaniu %s</h1><p class=\"meta\"><span>Źródło: %s</span><span>Elementy: %d</span></p>"
        '<div class="pasek" role="img" aria-label="Podział elementów według statusu">%s</div><p class="legenda">%s</p>'
        '<p class="postep" id="postep" aria-live="polite"></p>'
        "%s</main></div><script>%s</script></body></html>"
    ) % (e(str(wyniki.get("data_spotkania", ""))), CSS, spis, e(str(wyniki.get("data_spotkania", ""))),
         e(str(wyniki.get("zrodlo", ""))), len(el), "".join(pasek), "".join(legenda), sekcje, js)

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
