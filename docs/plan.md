# Plan

## Podsumowanie

Python stdlib, zero zależności. Przepływ: transkrypcja → `claude -p` (jedno wywołanie, JSON Schema) → walidacja w Pythonie (enumy, daty, cytaty dosłowne) → `wyniki.json` → szablony → `raport.html` (wszystkie szkice jako sekcje) → `ewaluacja` na `oczekiwane.json`. Całość uruchamia `./uruchom.sh <transkrypcja.md>`.

Kontrakt `wyniki.json` jest ustalony niżej, więc ekstrakcja, raport i ewaluacja idą równolegle w fali 1. Fala 2 skleja całość: jedna komenda, prawdziwe uruchomienie, wynik ewaluacji i README.

## Kontrakt `wyniki.json`

```json
{
  "zrodlo": "samples/transkrypcja-spotkanie.md",
  "data_spotkania": "2026-10-06",
  "elementy": [
    {
      "id": "E01",
      "typ": "błąd | zmiana konfiguracji | zadanie | prośba o funkcję | zakaz | informacja handlowa",
      "status": "teraz | czeka na klienta | wstrzymane | backlog | zakaz",
      "tytul": "krótki tytuł",
      "opis": "stan końcowy po nadpisaniach, z liczbami i szczegółami",
      "wlasciciel": "Marek | null",
      "zatwierdza": "Paweł | null",
      "termin": "2026-10-08 | null",
      "termin_do": "2026-10-16 | null",
      "termin_opis": "do czwartku | null",
      "warunek": "tylko jeśli Kasia nie wyśle tekstów do 8.10 | null",
      "przypomnienie": { "data": "2026-10-08", "tresc": "...", "maks_razy": 1 },
      "kategoria_crm": "ryzyko | sukces | null",
      "do_klienta": true,
      "cytaty": ["dosłowny fragment transkrypcji", "..."],
      "cytaty_zweryfikowane": true
    }
  ]
}
```

- `przypomnienie` może być `null`. `termin_do` służy tylko przedziałom (np. urlop 19–23.10, korekta 12–16.10).
- `cytaty`: min. 1. Pierwszy to wypowiedź rozstrzygająca (najpóźniejsza). `cytaty_zweryfikowane` ustawia Python, nie model.
- `do_klienta = false` dla treści wewnętrznych (ryzyko VoiceDesk, „nie piszę do Oli”, „jak Paweł napisze o Oplu, dzwonię do Kasi”). Mail do klienta bierze tylko `true`.

**Definicje statusów (do promptu):**
- `teraz`: Rinvo robi od razu, bez czekania na nikogo.
- `czeka na klienta`: ruszy, gdy klient coś dostarczy (tekst, plik, potwierdzenie, wiadomość).
- `wstrzymane`: świadomie odłożone do zdarzenia albo decyzji klienta (np. „jak pójdą świeże leady”).
- `backlog`: prośba o funkcję produktu, bez terminu.
- `zakaz`: czego nie robić na tym koncie. Typ `zakaz` ma zawsze status `zakaz`.

**Reguły dat:** Python wyznacza datę spotkania z nagłówka (polskie nazwy miesięcy, fallback `--data RRRR-MM-DD`) i wkleja do promptu kalendarz od dnia spotkania na 3 tygodnie (data + dzień tygodnia). „Do końca tygodnia” = piątek. Przypomnienie warunkowe ma datę dnia granicznego (8.10, 12.10). Brak terminu w rozmowie → `null`, bez zgadywania.

## Decyzje

- **Python stdlib** (obie opinie). Testy: `python3 -m unittest` z katalogu głównego. Moduły w `rinvo/` bez `__init__.py` (namespace package), żeby tickety z fali 1 nie konfliktowały.
- **Etap 2 tylko szablonami**, bez drugiego wywołania modelu (obie). Jeden `raport.html` z sekcjami zamiast siedmiu plików (obie). Dane wklejone w HTML, bez `fetch` i CDN (Claude).
- **Ewaluacja deterministyczna**, bez LLM-judge (obie). Każdy fakt to lista atomów sprawdzanych na polach strukturalnych. Sprawdzenia negatywne (np. sobota do 14) nigdy po `cytaty` (Claude). „Jedno przypomnienie” liczy elementy, a nie szuka słowa „raz” (Claude).
- **Weryfikacja cytatów** jako podciągów transkrypcji po normalizacji białych znaków i cudzysłowów (Claude). Daje najmocniejszy argument w demo.
- **Wywołanie `claude -p`** izolowane: `cwd` w katalogu tymczasowym, transkrypcja przez stdin, `--system-prompt`, `--tools ""`, `--output-format json`, `--json-schema`, `--no-session-persistence`. Bez `--bare` (może wymagać klucza API). Builder sprawdza to na początku (spike) (Claude: ryzyko wczytania `CLAUDE.md`).
- **Fakt 1 rozbity** (obie): godziny dzwonienia pn–pt 9–19, sob 9–15, nd brak; godziny salonu podawane przez agenta: sobota do 15 dla obu salonów. Bez „salon 9–19”.
- **Fakt 12** (Claude): oba elementy zablokowane do wiadomości od Kasi, ale z różnych powodów. Akceptujemy status `czeka na klienta` albo `wstrzymane`.
- **Cena SMS: 9.10 (piątek)** (obie). Korekta faktury: przedział 12–16.10.
- **Przykładowy wynik commitowany** (`wyniki.json`, `raport.html` w katalogu głównym), żeby demo i ewaluacja działały bez modelu (obie).
- **Proces skrócony** (Claude): 4 tickety, 2 fale. Worktree zostają, bo wymaga ich workflow, ale tickety z fali 1 idą równolegle.
- **Odrzucone:** LLM-judge, drugie wywołanie modelu, eksport .ics, osobne pliki na każdy szkic.
- **Prompt bez wiedzy o Auto Tama** (Claude): żadnych marek, imion ani godzin w prompcie, tylko reguły ogólne.

## Poprawki użytkownika przy akceptacji

1. Testy jednostkowe minimalne: walidacja, weryfikacja cytatów, `ocen` na zepsutych wynikach.
2. T-002: wygląd prosty, funkcja ważniejsza niż design.
3. Po fali 1 od razu scalić i usunąć worktree, potem T-004.
4. Test na `transkrypcja-test-2.md` (lista faktów na jej końcu) obowiązkowy, wynik w README.
5. Limit: wszystko gotowe do 14:30; opóźnienia zgłaszać od razu.

## Ryzyka

- `claude -p` zwraca prozę albo czyta kontekst repo → izolacja i spike na początku T-001.
- Niedeterminizm: dwa uruchomienia dają 14/15 i 15/15 → commitujemy wynik referencyjny i w README podajemy wynik uczciwie.
- Przeuczenie na jednej transkrypcji → prompt bez szczegółów klienta; README mówi, że 15/15 ≠ kompletność (pomija m.in. ściągę statusów, A/B, raport tygodniowy, kolumnę nazwiska).
- Budżet 2 h → jeśli w T-004 ewaluacja nie da 15/15 po 2 poprawkach promptu, oddajemy uczciwy wynik.

## Lista ticketów

| ID | Tytuł | Specjalista | Zależności | Fala |
|---|---|---|---|---|
| T-001 | Ekstrakcja transkrypcji do `wyniki.json` | backend | brak | 1 |
| T-002 | `raport.html` ze szkicami z `wyniki.json` | frontend | brak (kontrakt) | 1 |
| T-003 | `oczekiwane.json` i skrypt ewaluacji | tester | brak (kontrakt) | 1 |
| T-004 | Jedna komenda, przebieg demo i README | backend | T-001, T-002, T-003 | 2 |
