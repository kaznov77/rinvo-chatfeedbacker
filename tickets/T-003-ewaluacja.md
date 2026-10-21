# T-003: oczekiwane.json i skrypt ewaluacji

- **ID:** T-003
- **Tytuł:** `oczekiwane.json` z 15 faktami i deterministyczny skrypt ewaluacji
- **Typ:** funkcja
- **Specjalista:** tester
- **Status:** review
- **Zależności:** brak (pracuje na kontrakcie z `docs/plan.md`)
- **Gałąź:** ticket/T-003-ewaluacja

## Cel

`python3 -m rinvo.ewaluacja wyniki.json [oczekiwane.json]` wypisuje dla każdego z 15 faktów ✅/❌ i które atomy nie przeszły, na końcu `Wynik: X/15`. Kod wyjścia 0 tylko przy 15/15.

`oczekiwane.json`: lista faktów `{id, opis, atomy: [...]}`. Atom to proste, deterministyczne sprawdzenie, np.:
- `istnieje`: istnieje element spełniający warunki na polach (`typ`, `status` jako lista dozwolonych, `termin`, `wlasciciel`, `zatwierdza`, `przypomnienie.maks_razy`, regex po tekście `tytul+opis+warunek+termin_opis+przypomnienie.tresc`), **nigdy po `cytaty`**;
- `liczba`: liczba elementów spełniających warunki (np. dokładnie 1 przypomnienie o tekstach wstępu);
- `brak`: żaden element nie zawiera wzorca w polach strukturalnych (np. sobota do 14).

Regexy bez wielkości liter, tolerancyjne na odmianę i zapis (np. `15(:00)?|piętnast`, `toru[ńn]sk\w* 120`).

Fakty (zgodnie z `docs/pomysl.md`, z poprawkami z planu):
1. Godziny dzwonienia: pn–pt 9–19, sobota 9–15, niedziela nie; godziny salonu podawane przez agenta: sobota do 15 dla obu salonów; `brak` soboty do 14 w polach strukturalnych.
2. Adres Włocławek Toruńska 120; po poprawce napisać do Kasi.
3. Błąd: ponowne dzwonienie po rozłączeniu w 3 s; 6 przypadków, 5.10 16:40 (albo „wczoraj 16:40”), numer kończy się na 14; limit 5 prób bez zmian.
4. Filtr statusu „zainteresowany” jako `błąd`; klikalny kafelek jako osobny element `prośba o funkcję`.
5. Korekta faktury na Auto Tama Toruń sp. z o.o., właściciel Michał.
6. Zwrot/odjęcie podwójnych połączeń i informacja do Kasi, ile ich było.
7. Cena SMS z terminem 2026-10-09 (dopuszczalnie do 2026-10-11); treść pisze Kasia; zatwierdza Paweł.
8. Dokładnie jedno przypomnienie o tekstach wstępu, termin/data 2026-10-08, `maks_razy` 1.
9. Dokładnie jedno przypomnienie o pliku leadów, data 2026-10-12, `maks_razy` 1; bez wzoru pliku; bez ponownej starej bazy.
10. Spotkanie z Pawłem 2026-10-15 10:00, zaproszenie dopiero po potwierdzeniu Kasi; case Peugeot 208 bez nazwy firmy.
11. Zakazy (status `zakaz`): Opel, agent po godzinach, nowy mail dla handlowców, sprzedawanie/auta używane, kontakt z Olą.
12. Zablokowane do wiadomości od Kasi (status `czeka na klienta` albo `wstrzymane`): podwójne pytanie o model; lead serwisowy Oli.
13. Urlop Kasi 2026-10-19 – 2026-10-23, nic nowego nie startuje.
14. Ryzyko odejścia: VoiceDesk, integracja, ok. 30% taniej (`kategoria_crm: ryzyko`).
15. Klientka na urlopie to lead do oddzwonienia, nie odmowa.

Dodatkowo (poza 15 faktami, jako ostrzeżenie, nie wpływa na wynik): liczba elementów z `cytaty_zweryfikowane: false`.


**Limit czasu:** wszystko (łącznie z T-004) ma być gotowe do 14:30. Nie dopracowuj. Jeśli coś się przeciąga, zatrzymaj się i opisz to w notatkach.

## Zakres plików

- `oczekiwane.json`
- `rinvo/ewaluacja.py`
- `tests/test_ewaluacja.py`
- `tests/dane/ewaluacja-*.json` (własne ręcznie napisane wyniki: jeden „dobry”, kilka zepsutych)

Nie twórz `rinvo/__init__.py`.

## Miejsca testów

- `ewaluacja.ocen(wyniki, oczekiwane) -> lista wyników faktów`: na ręcznie napisanym „dobrym” wyniku daje 15/15; na zepsutych wyłapuje: sobotę do 14 w opisie, dwa przypomnienia zamiast jednego, brak zakazu Opla, filtr i kafelek sklejone w jeden element, VoiceDesk bez `kategoria_crm: ryzyko`. Nie wyłapie parafraz spoza regexów (fałszywe ❌) ani kompletności poza 15 faktami.
- **Testy minimalne:** jeden „dobry” wynik (15/15) i jeden plik z kilkoma zepsuciami naraz (sobota do 14, dwa przypomnienia, brak zakazu Opla) sprawdzający, że te fakty dają ❌. Nie rozbudowuj.

## Kryteria ukończenia

- [x] `oczekiwane.json` ma 15 faktów, każdy z min. 1 atomem.
- [x] Testy na wynikach dobrym i zepsutych przechodzą zgodnie z opisem.
- [x] `python3 -m unittest` przechodzi.

## Notatki z realizacji

- Zrobione: `rinvo/ewaluacja.py` (atomy `istnieje`/`liczba`/`brak`, warunki na polach strukturalnych, `cytaty` nigdy nie są sprawdzane; tekst i wzorce są składane do ASCII, więc ogonki i wielkość liter nie mają znaczenia), `oczekiwane.json` (15 faktów, 1-5 atomów każdy), `tests/test_ewaluacja.py`, `tests/dane/ewaluacja-dobry.json` i `ewaluacja-zepsuty.json`. Dodatkowo ostrzeżenie o `cytaty_zweryfikowane: false`.
- Wyniki: `python3 -m unittest` daje 3 testy OK, 0 błędów. Dobry plik daje 15/15 (kod 0). Zepsuty (sobota do 14, dwa przypomnienia o wstępie, brak zakazu Opla) daje dokładnie ❌ dla faktów 1, 8, 11 (kod 1). Ręcznie sprawdzone regexy „sobota do 14” na zapisach: „do 14:00”, „9.00 do 14.00”, „9-14”, „od dziewiątej do czternastej”, „do czternastej” (łapie), „9–15” i „9:00-15:00” (nie łapie).
- Decyzje:
  - Dodałem pusty `tests/__init__.py`, bo bez niego `python3 -m unittest` nie znajduje testów (0 testów). Jest spoza listy zakresu. Pusty plik, więc przy scaleniu z innymi biletami nie powinno być konfliktu.
  - Dane „dobre” napisałem ja sam na podstawie faktów, więc test pokazuje spójność atomów z kontraktem, a nie to, że prawdziwy LLM zmieści się w regexach. Prawdziwą walidację da dopiero T-004 na wyjściu modelu.
  - Atom `brak` dla filtra i kafelka: ❌, jeśli jeden element typu `błąd` zawiera zarówno „filtr”, jak i „kafelek/klikalny”. Może dać fałszywe ❌, gdy model w opisie błędu wspomni, że kafelek to osobna sprawa. W razie potrzeby poluzować w `oczekiwane.json` (fakt 4, 3. atom).
  - Fakt 12 i 15 używają szerokich regexów, więc łatwo je spełnić (ryzyko fałszywych ✅ zamiast ❌). Fakt 1 nie wymusza typu elementu.
  - Nie testowane w osobnych testach: zepsucia „filtr+kafelek” i „VoiceDesk bez ryzyka” (ticket mówi: testy minimalne). Logika jest ta sama (`brak`/`kategoria_crm`).
- Nie przeczytałem skilli TDD z `~/.agents/skills/` (limit czasu).
- Znalezione błędy kodu produkcyjnego: brak (kod produkcyjny nie istnieje w tym worktree).

### Poprawki po review (rundy 1-2)

- Runda 1: zawężone i doprecyzowane regexy w `oczekiwane.json` po uwagach reviewera (szczegóły w historii gita).
- Runda 2: fakt 9 (atomy „bez wzoru” i „bez starej bazy”) używa negacji z granicą słowa `\b(?:nie|bez)\b`, więc „ponownie” nie spełnia negacji. Fakt 2: czasownik pisania `\b(?:na|od)?pis(?:z|a|ac|ze|zemy|ania)\w*` (nie łapie „opis/wpis/zapis”), adresat tylko `kasi\w*`. Fakt 15: przywrócony wymóg zaprzeczenia `\b(?:nie|a nie)\b\W+(?:\w+\W+){0,3}?(?:odmow|niezainteres)`.
- Sondy: „Zapytać ponownie o starą bazę” (fakt 9, atom starej bazy) -> ❌; „Agent podaje klientom stary adres; wpisać nowy do bazy wiedzy” (fakt 2, atom Kasi) -> ❌; „Klientka na urlopie odmówiła – lead zamknięty, nie dzwonić” (fakt 15) -> ❌.
- Wyniki: `python3 -m unittest` 3/3 OK; dobry plik testowy 15/15; prawdziwe `wyniki.json` 14/15 (nie przechodzi tylko fakt 11, atom „zakaz: nowy mail dla handlowców”; fakt 2 przechodzi). Fakt 11 do poprawy w prompcie ekstrakcji lub regexie.
