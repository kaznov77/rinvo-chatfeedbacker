# Pomysł

<!-- Przy każdym nowym zadaniu wypełniasz tylko sekcję „Opis zadania” i zaznaczasz typ.
     Pozostałe sekcje mają domyślne wartości dobre dla każdego projektu. Dopisz coś tylko wtedy,
     gdy to zadanie ma dodatkowe wymagania. Puste pola są OK: krytyk i Codex wskażą, czego brakuje. -->

## Opis zadania

Zadanie rekrutacyjne dla Rinvo (agent głosowy AI dla dealerów samochodowych), budżet czasu: **2 godziny**.
Wejście: transkrypcja rozmowy statusowej z klientem (`samples/transkrypcja-spotkanie.md`, spotkanie 6.10.2026, wtorek).
Cel: system, który automatycznie zajmuje się tym, co wynika z rozmowy. Priorytet: **działa i jest proste**. Najpierw wersja minimalna, potem rozwijanie.

**Etap 1: ekstrakcja** przez `claude -p` (CLI, bez klucza API). Każdy element ma:
- typ: błąd / zmiana konfiguracji / zadanie / prośba o funkcję / zakaz / informacja handlowa,
- status: teraz / czeka na klienta / wstrzymane / backlog / zakaz,
- właściciela,
- termin jako konkretną datę, liczoną od daty spotkania z nagłówka transkrypcji,
- warunek (np. „tylko jeśli klient nie wyśle do X”),
- dosłowny cytat jako dowód.

Późniejsze wypowiedzi nadpisują wcześniejsze. Nie wolno opierać się na podsumowaniu z końca rozmowy (jest niepełne). Wynik: `wyniki.json`.

**Etap 2: generowanie wyników** z `wyniki.json`: szkice zgłoszeń błędów, lista zmian konfiguracji, przypomnienia warunkowe z datami, lista zakazów dla konta klienta, wpisy do backlogu produktowego, notatka do CRM (ryzyka i sukcesy), szkic maila podsumowującego do klienta. Nic nie jest wysyłane automatycznie, człowiek zatwierdza. Na koniec `raport.html` do przejrzenia.

**Etap 3: ewaluacja.** `oczekiwane.json` z 15 faktami i skrypt sprawdzający, czy wynik je zawiera:
1. Sobota 9–15 (nie 14) dla dzwonienia i godzin salonu obu salonów, tydzień 9–19, niedziela wcale.
2. Adres Włocławek: Toruńska 120, po poprawce napisać do Kasi.
3. Błąd ponownego dzwonienia po rozłączeniu w 3 s: 6 przypadków, 5.10 16:40, numer na 14; limit 5 prób bez zmian.
4. Filtr statusu „zainteresowany” zepsuty; klikalny kafelek to osobna prośba o funkcję.
5. Korekta faktury na Auto Tama Toruń sp. z o.o., właściciel Michał.
6. Zwrot za podwójne połączenia i informacja do Kasi, ile ich było.
7. Cena SMS do końca tygodnia; treść pisze Kasia, zatwierdza Paweł.
8. Jedno przypomnienie o tekstach wstępu, jeśli nie przyjdą do 8.10.
9. Jeden mail, jeśli plik leadów nie przyjdzie 12.10; bez wzoru pliku, bez starej bazy.
10. Spotkanie z Pawłem 15.10 10:00, zaproszenie dopiero po potwierdzeniu Kasi; case Peugeot 208 bez nazwy firmy.
11. Zakazy: Opel, agent po godzinach, nowy mail dla handlowców, sprzedawanie i auta używane, kontakt z Olą.
12. Zablokowane do wiadomości od Kasi: podwójne pytanie o model, lead serwisowy Oli.
13. Urlop Kasi 19–23.10, nic nowego nie startuje.
14. Ryzyko odejścia: VoiceDesk (integracja, ok. 30% taniej).
15. Klientka na urlopie to lead do oddzwonienia, nie odmowa.

**Etap 4: README** z opisem problemu, schematem procesu w Mermaid, opisem demo, instrukcją uruchomienia na innej transkrypcji jedną komendą, założeniami i planem rozwoju.

## Cel

Typ zadania (zaznacz jeden, wpisując `x`):

- [x] **Nowe oprogramowanie / funkcja:** dostarczyć działający kod, który robi to, co opisano wyżej.
- [ ] **Rozwiązanie problemu:** znaleźć przyczynę błędu i usunąć ją tak, żeby nie wróciła.
- [ ] **Optymalizacja:** poprawić coś mierzalnego (szybkość, koszt, wygoda, czytelność kodu) bez zmiany działania.

## Kontekst

- Stack i sposób uruchamiania projektu: patrz `AGENTS.md` (sekcja „Stack” jest jeszcze pusta; repo nie ma kodu).
- Repo zawiera tylko pliki workflow, `README.md` (szablon) i `samples/transkrypcja-spotkanie.md`.
- Dostępne lokalnie: `claude` (CLI, zalogowane), `python3` (systemowy), `node`. Brak klucza API.
- Daty z transkrypcji (spotkanie wt. 6.10.2026): „do czwartku” = 8.10, „poniedziałek” = 12.10, „przyszły czwartek” = 15.10, „do końca tygodnia” = 9.10 (pt) lub 11.10, „korekta w przyszłym tygodniu” = 12–16.10, urlop 19–23.10.

## Ograniczenia

Domyślne (obowiązują zawsze):

- Nie psuć istniejących funkcji. Wszystko, co działało przed zmianą, działa po niej.
- Trzymać się obecnego stacku z `AGENTS.md`. Nowe biblioteki i usługi tylko za moją zgodą.
- Zmiany małymi krokami (tickety), każdy możliwy do sprawdzenia osobno.
- Żadnych sekretów w kodzie i żadnych zmian w danych produkcyjnych bez mojej zgody.
- Najprostsze rozwiązanie, które spełnia cel. Bez dokładania funkcji „na zapas”.

Dodatkowe dla tego zadania:

- Budżet: 2 godziny pracy łącznie.
- Ekstrakcja tylko przez `claude -p`, bez klucza API.
- Nic nie jest wysyłane automatycznie (maile, zgłoszenia, CRM to szkice do zatwierdzenia).

## Kryteria sukcesu

Domyślne:

- Opisane zadanie działa i da się to pokazać (krok po kroku, jak to sprawdzić).
- Testy (albo skrypty sprawdzające z `AGENTS.md`) przechodzą, a nowa logika ma testy.
- Lint i build przechodzą.
- Dla **rozwiązania problemu**: znana przyczyna i test, który odtwarzał błąd, a teraz przechodzi.
- Dla **optymalizacji**: pomiar przed i po, z wyraźną poprawą.

Dodatkowe dla tego zadania:

- Skrypt ewaluacji pokazuje wynik dla 15 faktów z `oczekiwane.json` (cel: 15/15).
- Uruchomienie na innej transkrypcji jedną komendą.
- `raport.html` otwiera się w przeglądarce bez serwera.

## Otwarte pytania

- Język implementacji: Python stdlib (bez zależności) czy Node? Propozycja: Python stdlib.
- Etap 2: generować szablonami (deterministycznie) z `wyniki.json`, czy drugim wywołaniem `claude -p` (np. tylko mail i notatka CRM)?
- Jak sprawdzać fakty w ewaluacji: dopasowanie słów kluczowych / regex (szybkie, deterministyczne, kruche) czy LLM-as-judge przez `claude -p` (elastyczne, wolne, niedeterministyczne)?
- Czy `wyniki.json` z prawdziwego uruchomienia commitować jako przykład (demo bez czekania na model)?
- „Do końca tygodnia” dla ceny SMS: piątek 9.10 czy niedziela 11.10?
