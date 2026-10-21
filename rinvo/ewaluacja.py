"""Deterministyczna ewaluacja wyniki.json względem oczekiwane.json.

Użycie: python3 -m rinvo.ewaluacja wyniki.json [oczekiwane.json]

Atom ma postać {"opis", "rodzaj": "istnieje|liczba|brak", "gdzie": {...}, "ile": N}.
"gdzie" to warunki na jednym elemencie (wszystkie muszą być spełnione):
typ, status (listy dozwolonych), termin, termin_do (listy), data (termin LUB
przypomnienie.data), przypomnienie (bool), maks_razy, wlasciciel, zatwierdza
(regex), kategoria_crm, tekst (lista regexów, każdy musi pasować).
Tekst = tytul+opis+warunek+termin_opis+przypomnienie.tresc, NIGDY cytaty.
Tekst i wzorce są składane do ASCII (bez ogonków), wzorce bez wielkości liter.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

DOMYSLNE_OCZEKIWANE = Path(__file__).resolve().parent.parent / "oczekiwane.json"


def zloz(tekst):
    """Usuwa ogonki, ujednolica myślniki i spacje (nie zmienia wielkości liter)."""
    tekst = tekst.replace("ł", "l").replace("Ł", "L")
    tekst = unicodedata.normalize("NFKD", tekst)
    tekst = "".join(c for c in tekst if not unicodedata.combining(c))
    for kreska in "–—−":
        tekst = tekst.replace(kreska, "-")
    return tekst.replace(" ", " ")


def tekst_elementu(el):
    przyp = el.get("przypomnienie") or {}
    pola = [el.get("tytul"), el.get("opis"), el.get("warunek"),
            el.get("termin_opis"), przyp.get("tresc")]
    return zloz(" ; ".join(str(p) for p in pola if p))


def _regex(wzorzec, tekst):
    return re.search(zloz(wzorzec), tekst, re.IGNORECASE) is not None


def pasuje(el, gdzie):
    przyp = el.get("przypomnienie")
    for klucz, wart in gdzie.items():
        if klucz in ("typ", "status", "termin", "termin_do"):
            if el.get(klucz) not in wart:
                return False
        elif klucz == "data":
            if el.get("termin") not in wart and (przyp or {}).get("data") not in wart:
                return False
        elif klucz == "przypomnienie":
            if (przyp is not None) != wart:
                return False
        elif klucz == "maks_razy":
            if not przyp or przyp.get("maks_razy") != wart:
                return False
        elif klucz in ("wlasciciel", "zatwierdza"):
            if not _regex(wart, zloz(str(el.get(klucz) or ""))):
                return False
        elif klucz == "kategoria_crm":
            if el.get("kategoria_crm") != wart:
                return False
        elif klucz == "tekst":
            t = tekst_elementu(el)
            if not all(_regex(w, t) for w in wart):
                return False
        else:
            raise ValueError(f"nieznany warunek: {klucz}")
    return True


def sprawdz_atom(elementy, atom):
    ile = sum(1 for el in elementy if pasuje(el, atom.get("gdzie", {})))
    rodzaj = atom["rodzaj"]
    if rodzaj == "istnieje":
        return ile >= 1
    if rodzaj == "brak":
        return ile == 0
    if rodzaj == "liczba":
        return ile == atom["ile"]
    raise ValueError(f"nieznany rodzaj atomu: {rodzaj}")


def ocen(wyniki, oczekiwane):
    """Zwraca listę {id, opis, ok, bledne_atomy} dla każdego faktu."""
    elementy = wyniki.get("elementy", [])
    rezultat = []
    for fakt in oczekiwane:
        bledne = [a["opis"] for a in fakt["atomy"] if not sprawdz_atom(elementy, a)]
        rezultat.append({"id": fakt["id"], "opis": fakt["opis"],
                         "ok": not bledne, "bledne_atomy": bledne})
    return rezultat


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("Użycie: python3 -m rinvo.ewaluacja wyniki.json [oczekiwane.json]")
        return 2
    wyniki = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    sciezka = Path(argv[1]) if len(argv) > 1 else DOMYSLNE_OCZEKIWANE
    oczekiwane = json.loads(sciezka.read_text(encoding="utf-8"))
    rez = ocen(wyniki, oczekiwane)
    for r in rez:
        print(f"{'✅' if r['ok'] else '❌'} {r['id']}. {r['opis']}")
        for a in r["bledne_atomy"]:
            print(f"     - nie przeszedł atom: {a}")
    ok = sum(r["ok"] for r in rez)
    niezw = sum(1 for e in wyniki.get("elementy", []) if e.get("cytaty_zweryfikowane") is False)
    if niezw:
        print(f"Ostrzeżenie: {niezw} elementów z cytaty_zweryfikowane: false")
    print(f"Wynik: {ok}/{len(rez)}")
    return 0 if ok == len(rez) == 15 else 1


if __name__ == "__main__":
    sys.exit(main())
