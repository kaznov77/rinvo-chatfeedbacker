# T-002: raport.html ze szkicami z wyniki.json

- **ID:** T-002
- **Tytuł:** generowanie `raport.html` (wszystkie szkice) z `wyniki.json`
- **Typ:** funkcja
- **Specjalista:** frontend
- **Status:** review
- **Zależności:** brak (pracuje na kontrakcie z `docs/plan.md`)
- **Gałąź:** ticket/T-002-raport

## Cel

`python3 -m rinvo.raport wyniki.json [--wyjscie raport.html]` tworzy jeden samodzielny plik HTML (dane wpisane w środku, bez `fetch`, bez CDN, działa z `file://`). Szkice powstają szablonami, bez modelu. Sekcje:

1. **Do zrobienia teraz** (status `teraz`).
2. **Zgłoszenia błędów** (typ `błąd`): tytuł, opis/kroki, dowód (cytaty), właściciel, termin.
3. **Zmiany konfiguracji** (typ `zmiana konfiguracji`).
4. **Przypomnienia warunkowe** (elementy z `przypomnienie`): data, warunek, treść, „maks. N raz”.
5. **Zakazy dla konta klienta** (status `zakaz`).
6. **Czeka na klienta / wstrzymane** (z warunkiem odblokowania).
7. **Backlog produktowy** (typ `prośba o funkcję`).
8. **Notatka do CRM**: ryzyka i sukcesy (`kategoria_crm`) + pozostałe informacje handlowe.
9. **Kalendarz**: wszystkie elementy z datą (`termin`, `termin_do`, `przypomnienie.data`) posortowane.
10. **Szkic maila do klienta**: tylko elementy z `do_klienta: true`, pogrupowane (co robimy, czego od Was potrzebujemy, co czeka), w `<textarea>` do skopiowania. **Nigdy** elementy z `do_klienta: false`.

Na górze baner: „Szkice do zatwierdzenia. Nic nie zostało wysłane.” Przy każdym szkicu checkbox „zatwierdzam” (tylko wizualny, bez akcji). Przy każdym elemencie cytaty jako dowód i ostrzeżenie, gdy `cytaty_zweryfikowane` jest `false`. Wszystkie wartości escapowane (`html.escape`).


**Limit czasu:** wszystko (łącznie z T-004) ma być gotowe do 14:30. Nie dopracowuj. Jeśli coś się przeciąga, zatrzymaj się i opisz to w notatkach.

## Zakres plików

- `rinvo/raport.py`
- `tests/test_raport.py`
- `tests/dane/raport-*.json` (własny ręcznie napisany przykład zgodny z kontraktem)

Nie twórz `rinvo/__init__.py`. Nie commituj `raport.html` (zrobi to T-004).

## Miejsca testów

- Testy minimalne (uzgodnione z użytkownikiem): jeden test `raport.szkic_maila(wyniki)`, że element `do_klienta: false` nie trafia do maila, i jeden, że `<script>` w opisie jest escapowany w `generuj_html`. Nic więcej.
- Wygląd: ręcznie, otwarcie pliku w przeglądarce (opisz w notatkach).

## Kierunek wizualny

**Prosto, bez dopieszczania: funkcja ważniejsza niż design.** Jeden blok CSS, kilkadziesiąt linii. Charakter: **rzeczowy dokument roboczy do zatwierdzenia**, coś między notatką z odprawy a kartą zlecenia w serwisie. Spokojny, gęsty informacyjnie, bez ozdobników.
- Kolory: tło ciepła biel / papier (#faf8f4), tekst grafitowy (#1f2328), jeden akcent (głęboki pomarańcz #d9480f) dla „teraz” i banera. Statusy jako małe etykiety: teraz = pomarańcz, czeka na klienta = niebieski, wstrzymane = szary, backlog = fiolet stonowany, zakaz = czerwony (#c92a2a).
- Czcionki: systemowe (bez CDN). Nagłówki `ui-serif, Georgia`, tekst `system-ui`, cytaty `ui-monospace` na jasnym tle z lewą krawędzią.
- Układ: wąska kolumna do czytania (max ~880 px), spis sekcji na górze z licznikami, karty elementów z metadanymi w jednej linii (właściciel · termin · warunek). Czytelny wydruk (`@media print`).

## Kryteria ukończenia

- [x] `python3 -m rinvo.raport tests/dane/raport-przyklad.json --wyjscie /tmp/raport.html` tworzy plik, który otwiera się z dysku.
- [x] Wszystkie 10 sekcji są obecne; puste sekcje pokazują „brak”.
- [x] Mail nie zawiera elementów `do_klienta: false` (test).
- [x] `python3 -m unittest` przechodzi.

## Notatki z realizacji
- Zrobiono: `rinvo/raport.py` (CLI + `generuj_html`, `szkic_maila`), 2 testy, ręczny przykład `tests/dane/raport-przyklad.json` (18 elementów, wszystkie typy i statusy).
- Decyzje: dodano pusty `tests/__init__.py` (bez niego `python3 -m unittest` nie znajduje testów, 0 testów); to drobne wyjście poza listę plików, ale w `tests/`. `rinvo/__init__.py` nie istnieje. Checkbox „zatwierdzam” jest per sekcja (szkic). Sekcje „teraz”, błędy itd. mogą dublować element (filtry po statusie/typie). Mail grupuje: teraz = co robimy, czeka na klienta = czego potrzebujemy, reszta = co czeka. Ostrzeżenie o cytatach pokazywane przy `cytaty_zweryfikowane: false`.
- Sprawdzono: `python3 -m unittest` (2 testy OK), generacja do `/tmp/raport.html` (10 sekcji). Wyglądu w przeglądarce NIE oglądano; HTML tylko sprawdzony strukturalnie.
- Nie zrobiono: ręczne obejrzenie w przeglądarce i wydruku.
