# T-001: Ekstrakcja transkrypcji do wyniki.json

- **ID:** T-001
- **Tytuł:** ekstrakcja transkrypcji przez `claude -p` do `wyniki.json`
- **Typ:** funkcja
- **Specjalista:** backend
- **Status:** do zrobienia
- **Zależności:** brak
- **Gałąź:** ticket/T-001-ekstrakcja

## Cel

`python3 -m rinvo.ekstrakcja samples/transkrypcja-spotkanie.md [--data RRRR-MM-DD] [--wyjscie wyniki.json]` czyta transkrypcję, jednym wywołaniem `claude -p` wyciąga elementy według kontraktu z `docs/plan.md` (sekcja „Kontrakt `wyniki.json`”), waliduje je i zapisuje `wyniki.json`. Każdy cytat jest sprawdzony jako dosłowny fragment transkrypcji.

Wymagania:
- **Najpierw spike (≤10 min):** sprawdź, że izolowane wywołanie zwraca czysty JSON i nie czyta kontekstu repo: `cwd` w katalogu tymczasowym, transkrypcja przez stdin, `--system-prompt`, `--tools ""`, `--output-format json`, `--json-schema`, `--no-session-persistence`. Bez `--bare`. Zanotuj, które flagi zadziałały.
- Data spotkania z nagłówka (polskie nazwy miesięcy, np. „6 października 2026”), fallback `--data`. Python generuje kalendarz (dzień spotkania + 21 dni, data i dzień tygodnia po polsku) i wkleja go do promptu.
- Prompt w `rinvo/prompt_ekstrakcji.md`: definicje typów i statusów z planu, reguła „późniejsze wypowiedzi nadpisują wcześniejsze”, „nie opieraj się na podsumowaniu z końca rozmowy”, „brak terminu → null”, „do końca tygodnia = piątek”, „przypomnienie warunkowe: data dnia granicznego, maks_razy zgodnie z rozmową”, perspektywa Rinvo, `do_klienta`, `kategoria_crm`. **Bez wiedzy o tym kliencie** (żadnych marek, imion, godzin).
- Walidacja w Pythonie: enumy `typ`/`status`, format dat, typ `zakaz` ⇒ status `zakaz`, `cytaty` niepuste. Weryfikacja cytatów: podciąg transkrypcji po normalizacji (białe znaki, cudzysłowy „”"', myślniki –-, wielkość liter, usunięcie `**`). Ustaw `cytaty_zweryfikowane`, a niezweryfikowane wypisz jako ostrzeżenie (nie przerywaj).
- Odporność: zdejmij płotki ```json, przy błędzie JSON jedna ponowna próba; czytelny błąd, gdy brak `claude` albo nie jest zalogowany. Surowa odpowiedź zapisana obok (`wyniki.raw.txt`, w `.gitignore`).
- Uruchom raz naprawdę na `samples/transkrypcja-spotkanie.md` i zacommituj `wyniki.json`.


**Limit czasu:** wszystko (łącznie z T-004) ma być gotowe do 14:30. Nie dopracowuj. Jeśli coś się przeciąga, zatrzymaj się i opisz to w notatkach.

## Zakres plików

- `rinvo/ekstrakcja.py`
- `rinvo/daty.py`
- `rinvo/prompt_ekstrakcji.md`
- `tests/test_ekstrakcja.py`
- `tests/dane/ekstrakcja-*.{md,json}`
- `wyniki.json`
- `.gitignore` (tylko dopisanie `wyniki.raw.txt` i `__pycache__/`)

Nie twórz `rinvo/__init__.py` ani `tests/__init__.py` (namespace package).

## Miejsca testów

- `ekstrakcja.waliduj(wyniki)`: wyłapie zły enum, złą datę, `zakaz` ze złym statusem; nie wyłapie merytorycznych błędów modelu.
- `ekstrakcja.zweryfikuj_cytaty(wyniki, transkrypcja)`: wyłapie cytat zmyślony lub sklejony, przepuści różnice w cudzysłowach i białych znakach; nie wyłapie cytatu prawdziwego, ale z niewłaściwego miejsca.
- **Testy minimalne:** tylko `waliduj` i `zweryfikuj_cytaty`, po kilka przypadków. Nie rozbudowuj.
- Prawdziwe uruchomienie `claude -p`: tylko ręcznie (spike + generowanie `wyniki.json`), nie w testach.

## Kryteria ukończenia

- [ ] `python3 -m rinvo.ekstrakcja samples/transkrypcja-spotkanie.md` tworzy `wyniki.json` zgodny z kontraktem.
- [ ] W zacommitowanym `wyniki.json` wszystkie cytaty mają `cytaty_zweryfikowane: true` (albo ostrzeżenia opisane w notatkach).
- [ ] Prompt nie zawiera nazw z tej transkrypcji (`grep -iE 'tama|peugeot|kasia|opel' rinvo/prompt_ekstrakcji.md` pusty).
- [ ] `python3 -m unittest` przechodzi.
- [ ] W notatkach: flagi `claude -p`, które zadziałały, i czas wywołania.

## Notatki z realizacji

