"""Ekstrakcja transkrypcji rozmowy do wyniki.json przez `claude -p`."""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from rinvo import daty

TYPY = ["błąd", "zmiana konfiguracji", "zadanie", "prośba o funkcję", "zakaz", "informacja handlowa"]
STATUSY = ["teraz", "czeka na klienta", "wstrzymane", "backlog", "zakaz"]
PROMPT = Path(__file__).with_name("prompt_ekstrakcji.md")

_NULL_STR = {"type": ["string", "null"]}
SCHEMAT = {
    "type": "object",
    "required": ["elementy"],
    "properties": {"elementy": {"type": "array", "items": {
        "type": "object",
        "required": ["id", "typ", "status", "tytul", "skrot", "opis", "wlasciciel", "zatwierdza", "termin",
                     "termin_do", "termin_opis", "warunek", "przypomnienie", "kategoria_crm",
                     "do_klienta", "cytaty"],
        "properties": {
            "id": {"type": "string"},
            "typ": {"type": "string", "enum": TYPY},
            "status": {"type": "string", "enum": STATUSY},
            "tytul": {"type": "string"},
            "skrot": {"type": "string"},
            "opis": {"type": "string"},
            "wlasciciel": _NULL_STR, "zatwierdza": _NULL_STR, "termin": _NULL_STR,
            "termin_do": _NULL_STR, "termin_opis": _NULL_STR, "warunek": _NULL_STR,
            "przypomnienie": {"type": ["object", "null"],
                              "required": ["data", "tresc", "maks_razy"],
                              "properties": {"data": {"type": "string"}, "tresc": {"type": "string"},
                                             "maks_razy": {"type": ["integer", "null"]}}},
            "kategoria_crm": {"type": ["string", "null"], "enum": ["ryzyko", "sukces", None]},
            "do_klienta": {"type": "boolean"},
            "cytaty": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        }}}},
}

DATA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class BladEkstrakcji(Exception):
    pass


def _data_ok(s):
    if not isinstance(s, str) or not DATA_RE.match(s):
        return False
    try:
        date.fromisoformat(s)
        return True
    except ValueError:
        return False


def waliduj(wyniki):
    """Zwraca listę błędów (pusta = OK)."""
    bledy = []
    elementy = wyniki.get("elementy") if isinstance(wyniki, dict) else None
    if not isinstance(elementy, list) or not elementy:
        return ["brak listy 'elementy'"]
    for i, e in enumerate(elementy):
        k = e.get("id", f"#{i}")
        if e.get("typ") not in TYPY:
            bledy.append(f"{k}: zły typ {e.get('typ')!r}")
        if e.get("status") not in STATUSY:
            bledy.append(f"{k}: zły status {e.get('status')!r}")
        if e.get("typ") == "zakaz" and e.get("status") != "zakaz":
            bledy.append(f"{k}: typ 'zakaz' wymaga statusu 'zakaz'")
        for p in ("termin", "termin_do"):
            if e.get(p) is not None and not _data_ok(e[p]):
                bledy.append(f"{k}: zła data w '{p}': {e[p]!r}")
        prz = e.get("przypomnienie")
        if prz is not None and not (isinstance(prz, dict) and _data_ok(prz.get("data"))):
            bledy.append(f"{k}: zła data przypomnienia")
        c = e.get("cytaty")
        if not isinstance(c, list) or not c or not all(isinstance(x, str) and x.strip() for x in c):
            bledy.append(f"{k}: 'cytaty' puste")
        if not isinstance(e.get("do_klienta"), bool):
            bledy.append(f"{k}: 'do_klienta' nie jest bool")
    return bledy


def normalizuj(t):
    t = t.replace("**", "")
    t = re.sub(r"[„”“‟\"«»'’‘]", "", t)
    t = re.sub(r"[–—‑-]", "-", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


def zweryfikuj_cytaty(wyniki, transkrypcja):
    """Ustawia cytaty_zweryfikowane; zwraca listę niezweryfikowanych (id, cytat)."""
    pelny = normalizuj(transkrypcja)
    zle = []
    for e in wyniki["elementy"]:
        ok = True
        for c in e.get("cytaty", []):
            n = normalizuj(c)
            if not n or n not in pelny:
                ok = False
                zle.append((e.get("id"), c))
        e["cytaty_zweryfikowane"] = ok and bool(e.get("cytaty"))
    return zle


def zloz_prompt(data):
    return (PROMPT.read_text(encoding="utf-8")
            .replace("{{DATA_SPOTKANIA}}", f"{data.isoformat()} ({daty.DNI[data.weekday()]})")
            .replace("{{KALENDARZ}}", "\n".join(daty.kalendarz(data))))


def wyciagnij_json(tekst):
    t = tekst.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.DOTALL)
    if m:
        t = m.group(1).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        a, b = t.find("{"), t.rfind("}")
        if a < 0 or b <= a:
            raise
        return json.loads(t[a:b + 1])


def wywolaj_claude(transkrypcja, prompt, timeout=600):
    """Jedno izolowane wywołanie claude -p. Zwraca (obiekt|None, surowy tekst)."""
    cmd = ["claude", "-p", "--tools", "", "--system-prompt", prompt, "--output-format", "json",
           "--json-schema", json.dumps(SCHEMAT), "--no-session-persistence"]
    with tempfile.TemporaryDirectory() as tmp:
        try:
            p = subprocess.run(cmd, input=transkrypcja, capture_output=True, text=True,
                               cwd=tmp, timeout=timeout)
        except FileNotFoundError:
            raise BladEkstrakcji("Nie znaleziono polecenia 'claude'. Zainstaluj Claude Code i zaloguj się.")
        except subprocess.TimeoutExpired:
            raise BladEkstrakcji(f"claude -p przekroczył limit {timeout} s")
    surowy = p.stdout
    try:
        koperta = json.loads(surowy)
    except json.JSONDecodeError:
        raise BladEkstrakcji(f"claude zwrócił nie-JSON (kod {p.returncode}): {(p.stderr or surowy)[:300]}")
    if koperta.get("is_error"):
        tekst = str(koperta.get("result", ""))
        if re.search(r"log ?in|auth|api key|401", tekst, re.I):
            raise BladEkstrakcji(f"claude nie jest zalogowany: {tekst[:200]} (uruchom 'claude' i zaloguj się)")
        raise BladEkstrakcji(f"claude zgłosił błąd: {tekst[:300]}")
    if isinstance(koperta.get("structured_output"), dict):
        return koperta["structured_output"], surowy
    try:
        return wyciagnij_json(str(koperta.get("result", ""))), surowy
    except json.JSONDecodeError:
        return None, surowy


def ekstrahuj(sciezka, data_cli=None, wyjscie="wyniki.json"):
    transkrypcja = Path(sciezka).read_text(encoding="utf-8")
    data = daty.data_z_naglowka(transkrypcja)
    if data is None and data_cli:
        data = date.fromisoformat(data_cli)
    if data is None:
        raise BladEkstrakcji("Nie znaleziono daty spotkania w nagłówku. Podaj --data RRRR-MM-DD.")
    prompt = zloz_prompt(data)
    surowe = []
    wynik = None
    for proba in (1, 2):
        wynik, surowy = wywolaj_claude(transkrypcja, prompt)
        surowe.append(surowy)
        if wynik is not None:
            break
        print(f"Błąd parsowania JSON (próba {proba}).", file=sys.stderr)
    out = Path(wyjscie)
    out.with_suffix(".raw.txt").write_text("\n\n=====\n\n".join(surowe), encoding="utf-8")
    if wynik is None:
        raise BladEkstrakcji("Nie udało się odczytać JSON z odpowiedzi (patrz wyniki.raw.txt).")
    bledy = waliduj(wynik)
    if bledy:
        raise BladEkstrakcji("Walidacja nie przeszła:\n  " + "\n  ".join(bledy))
    for e in wynik["elementy"]:
        e.setdefault("cytaty_zweryfikowane", False)
    zle = zweryfikuj_cytaty(wynik, transkrypcja)
    for id_, c in zle:
        print(f"OSTRZEŻENIE: cytat niezweryfikowany w {id_}: {c[:100]!r}", file=sys.stderr)
    pelny = {"zrodlo": str(sciezka), "data_spotkania": data.isoformat(), "elementy": wynik["elementy"]}
    out.write_text(json.dumps(pelny, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Zapisano {out}: {len(wynik['elementy'])} elementów, niezweryfikowanych cytatów: {len(zle)}")
    return pelny


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ekstrakcja transkrypcji do wyniki.json")
    ap.add_argument("transkrypcja")
    ap.add_argument("--data", help="RRRR-MM-DD, gdy brak daty w nagłówku")
    ap.add_argument("--wyjscie", default="wyniki.json")
    a = ap.parse_args(argv)
    try:
        ekstrahuj(a.transkrypcja, a.data, a.wyjscie)
    except (BladEkstrakcji, OSError, ValueError) as e:
        print(f"BŁĄD: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
