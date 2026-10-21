# Opinia Claude (krytyk)

## Streszczenie

Celem jest zadanie rekrutacyjne na 2 godziny: skrypt, który z transkrypcji rozmowy statusowej (Auto Tama × Rinvo, 6.10.2026) wyciąga przez `claude -p` ustrukturyzowane elementy (typ, status, właściciel, termin, warunek, cytat) do `wyniki.json`. Z tego pliku deterministycznie powstają szkice (zgłoszenia, zmiany konfiguracji, przypomnienia, zakazy, backlog, CRM, mail) i `raport.html`. Do tego dochodzi ewaluacja na 15 faktach i README. Pomysł jest dobrze przemyślany merytorycznie. Fakty w ewaluacji trafiają w naprawdę podchwytliwe miejsca transkrypcji (nadpisanie soboty, „jeden mail”, „nie zgadujcie kampanii”, urlop jako lead). Największy problem nie leży w pomyśle, tylko w tym, że zakres jest za szeroki na 2 godziny, a narzut workflow (konsultacja, plan, tickety, worktree, review) zjada ten budżet.

## Luki

**Schemat danych**

1. **„Termin jako konkretna data” nie pasuje do części elementów.** W transkrypcji są przedziały („korekta w przyszłym tygodniu” = 12–16.10, urlop 19–23.10), terminy bez daty (prośby o funkcje: „terminu ci nie dam”) i terminy względne wobec zdarzenia („szkolenie, jak pójdą świeże leady”). Schemat musi mieć `termin_od`, `termin_do` (oba nullable) i ewentualnie `termin_opis`. Inaczej model zacznie zmyślać daty.
2. **„Zakaz” występuje jednocześnie jako typ i jako status.** To redundancja. Do tego granica między „czeka na klienta” a „wstrzymane” jest nieostra. Po godzinach i Opel są wstrzymane, ale odblokowuje je wyłącznie Kasia. Trzeba spisać jednozdaniowe definicje statusów w promptcie, bo bez nich wynik będzie się zmieniał między uruchomieniami.
3. **Brak pola „widoczność / dla kogo”.** Szkic maila do klienta nie może zawierać ryzyka VoiceDesk, notatki CRM ani wewnętrznych ustaleń (np. „nie piszę do Oli”, „jak Paweł napisze o Oplu, dzwonię do Kasi”). Bez flagi `do_klienta: true/false` mail generowany szablonem z `wyniki.json` przecieknie z treścią wewnętrzną. To realny błąd merytoryczny, który rekruter zauważy.
4. **Kto jest „my”.** Notatka zakłada perspektywę Rinvo, ale tego nie mówi. Ma to znaczenie dla właściciela (Marek / Michał / Kasia / Paweł) i dla tonu maila. Warto to zapisać w promptcie.

**Pokrycie ewaluacji**

5. **15 faktów nie pokrywa wszystkich zobowiązań.** Brakuje ich w ewaluacji (fakt: sprawdziłem w transkrypcji):
   - ściąga ze statusami dla handlowców, którą Marek obiecał wysłać (bez terminu); szkolenie dopiero po świeżych leadach, termin ustala Kasia;
   - kolumna „nazwisko po statusie”, warunkowo: tylko jeśli ruszana jest lista przy filtrze;
   - prośby o funkcje: A/B testy w panelu (metryka: pełne rozmowy, nie rozłączenia) i tygodniowy raport mailowy dla Pawła;
   - odłożone: przesunięcie prób na porę obiadową;
   - numery assistance: przechować, nie podpinać; „Kasia mówiła, że po godzinach od wtorku” ma być zignorowane;
   - test wstępu: dwie wersje, dwa dni albo dwa miasta, nie w tym tygodniu, wybiera Kasia;
   - Opel: nawet polecenie od Pawła nie wystarcza; w czasie urlopu Paweł nie zatwierdza ani Opla, ani wstępu.

   Nie trzeba ich wszystkich dodawać do ewaluacji. README powinno jednak uczciwie mówić, że 15/15 nie oznacza kompletności.
6. **Fakt 1 miesza dwie różne rzeczy.** „Tydzień 9–19” to godziny dzwonienia. Godziny salonu we Włocławku w tygodniu to 9–18, a Toruń jest „bez zmian” i nieznany. Ewaluacja zbudowana na tym fakcie może nagrodzić błędny wynik („salon 9–19”). Fakt trzeba rozbić na: godziny dzwonienia (pn–pt 9–19, sob 9–15, nd brak) oraz godziny salonu w bazie wiedzy (sobota 15 dla obu salonów, Włocławek w tygodniu 9–18).
7. **Fakt 12 jest przeinaczony.** Przy „podwójnym pytaniu o model” Kasia nie obiecała niczego przesłać. Marek mówi, że bez numeru tego nie znajdzie. Obietnica „jak znajdzie, prześlę” dotyczy leada serwisowego Oli. Oba elementy są zablokowane, ale z innych powodów. Status „czeka na klienta” dla pierwszego to interpretacja, a nie fakt z rozmowy.

**Daty i reguły**

8. **Daty przypomnień są niejednoznaczne.** „Jak do czwartku nie wyślę, przypomnij”: przypomnienie przypada na 8.10 wieczorem czy 9.10 rano? „Plik w poniedziałek, jak nie wyślę, napisz”: mail 12.10 po południu czy 13.10? Trzeba przyjąć jedną regułę (proponuję: przypomnienie następnego dnia roboczego rano, czyli 9.10 i 13.10, a termin graniczny 8.10 i 12.10 zapisać osobno) i opisać ją w README.
9. **„Do końca tygodnia” dla ceny SMS** (otwarte pytanie): w kontekście B2B to piątek 9.10. Marek mówi „w tym tygodniu”, a nie „do niedzieli”. Rozstrzygnąć na 9.10 i nie tracić na to czasu.
10. **Interakcje między regułami są pominięte.** Test wstępu nie może ruszyć w tym tygodniu, a od 19.10 nic nowego nie startuje. Realne okno to więc 12–16.10, i to tylko jeśli teksty przyjdą. To samo dotyczy świeżych leadów. To najciekawszy wniosek z transkrypcji, a ani ekstrakcja, ani ewaluacja go nie wymagają. Warto dodać jedną linijkę w raporcie albo jeden fakt.

**Kryteria i uruchamianie**

11. **„Lint i build przechodzą”** nie ma odniesienia, bo nie ma stacku. Przy Pythonie stdlib wystarczy `python3 -m py_compile` plus ewaluacja. Trzeba to wpisać do `AGENTS.md` (sekcja Stack jest pusta).
12. **„Jedną komendą na innej transkrypcji”**: data spotkania jest parsowana z nagłówka po polsku („6 października 2026 (wtorek)”). Inna transkrypcja może mieć inny format. Potrzebny jest fallback w postaci argumentu `--data RRRR-MM-DD`. Ewaluacja na innej transkrypcji nie ma sensu, więc trzeba ją wtedy pominąć i powiedzieć to wprost.

## Ryzyka

1. **Narzut procesu zjada budżet.** Prawdopodobieństwo: **wysokie**. Konsultacja dwóch modeli, plan, tickety, worktree na każdy ticket, review i scalanie łatwo zabiorą 40–60 minut z 2 godzin. Skutek: brak README albo ewaluacji w chwili oddania. Jak ograniczyć: maksymalnie 3 tickety w jednym worktree albo bez worktree, review raz na końcu, a plan to jedna strona.

2. **`claude -p` wczytuje kontekst projektu i globalny `CLAUDE.md`.** Prawdopodobieństwo: **średnie–wysokie** (przypuszczenie, sprawdzić). Uruchomienie w katalogu repo dołączy `AGENTS.md` i globalną instrukcję „gdy opisuję nowy pomysł, przeprowadź proces /pomysl”. Model może zacząć „pracować nad projektem”, czytać pliki albo odpowiadać prozą zamiast JSON-em. Jak ograniczyć:
   - wywoływać z `cwd` w katalogu tymczasowym;
   - transkrypcję podawać przez stdin;
   - wyłączyć narzędzia i ograniczyć tury (sprawdzić w `claude --help` dostępne flagi: `--tools`/`--disallowedTools`, `--max-turns`, `--system-prompt`, `--output-format json`, ewentualnie `--json-schema` lub tryb bez ładowania ustawień);
   - zrobić to w pierwszych 10 minutach, przed pisaniem czegokolwiek innego.

3. **Niepoprawny JSON z modelu.** Prawdopodobieństwo: **średnie**. Model doda ```json, komentarz albo urwie odpowiedź przy długim wyjściu (ok. 30–40 elementów z cytatami to kilka tysięcy tokenów). Jak ograniczyć: `--output-format json` i wyciąganie pola `result`, zdejmowanie płotków kodu, `json.loads` z jedną ponowną próbą, w której model dostaje błąd parsowania. Poza tym walidacja enumów (typ, status) w Pythonie i surowe odrzucanie nieznanych wartości.

4. **Halucynowane cytaty.** Prawdopodobieństwo: **średnie**. Model „wygładzi” cytat albo skleja dwie wypowiedzi. Jak ograniczyć: deterministyczne sprawdzenie, że każdy `cytat` jest podciągiem transkrypcji po normalizacji (białe znaki, cudzysłowy „” vs "). To kilkanaście linii kodu, a daje najmocniejszy argument w demo („każdy element ma zweryfikowane źródło”). Mocno rekomenduję.

5. **Błędne daty.** Prawdopodobieństwo: **średnie**. LLM-y często mylą dni tygodnia przy „przyszły czwartek”. Jak ograniczyć: Python generuje kalendarz (np. „wt 2026-10-06, śr 2026-10-07 … nd 2026-10-25”) i wkleja go do promptu z regułami („do końca tygodnia” = piątek). Opcjonalnie można sprawdzić w Pythonie, że każda data mieści się w tym oknie.

6. **Ewaluacja słowami kluczowymi daje fałszywe wyniki przy negacjach.** Prawdopodobieństwo: **wysokie**, jeśli nie zostanie to przemyślane. Fakt 1 wymaga „nie 14”, ale cytat z wcześniejszej wypowiedzi zawiera „czternastej”. Naiwny regex po całym pliku albo przepuści błąd, albo zgłosi fałszywy alarm. Jak ograniczyć:
   - sprawdzenia negatywne puszczać tylko po polach strukturalnych (opis, termin, warunek), nigdy po `cytat`;
   - sprawdzenia liczbowe („jedno przypomnienie”) robić jako liczenie elementów o danym typie i temacie, a nie jako szukanie słowa „raz”.

7. **Przeuczenie promptu pod 15 faktów.** Prawdopodobieństwo: **wysokie**. Autor pisze fakty i stroi prompt na tej samej transkrypcji, więc 15/15 nic nie mówi o innej rozmowie. Jak ograniczyć: nie wpisywać do promptu niczego specyficznego dla Auto Tama (marek, imion, „sobota”) i powiedzieć to wprost w README. Jeśli zostanie czas, dorzucić 5-minutowy test na krótkiej, ręcznie napisanej drugiej transkrypcji, tylko jako smoke test.

8. **Niedeterminizm ekstrakcji.** Prawdopodobieństwo: **wysokie**. Dwa uruchomienia dadzą 14/15 i 15/15. Jak ograniczyć: commitować wynik referencyjnego uruchomienia (`samples/wyniki-przyklad.json`), żeby demo i ewaluacja działały bez modelu, a w README podać wynik z kilku uruchomień, jeśli będzie czas.

9. **`raport.html` nie ładuje danych z `file://`.** Prawdopodobieństwo: **średnie**. Chrome blokuje `fetch()` lokalnego JSON-a. Jak ograniczyć: generować HTML z danymi wklejonymi do środka (Python `html.escape`, zero JS albo minimalny JS), bez zewnętrznych CDN.

## Alternatywy

**A. Wszystko w jednym wywołaniu `claude -p`** (ekstrakcja i od razu gotowe szkice/markdown).
- Plusy: najszybsze.
- Minusy: brak `wyniki.json` jako jednego źródła prawdy, ewaluacja na wolnym tekście, brak walidacji. Odrzucić. Podział ekstrakcja → JSON → deterministyczny render jest właściwy i to jest najmocniejsza decyzja w tym pomyśle.

**B. Etap 2 drugim wywołaniem `claude -p` (mail, CRM).**
- Plusy: ładniejszy mail.
- Minusy: kolejne 1–3 minuty na uruchomienie, kolejne ryzyko przecieku treści wewnętrznych do maila, druga rzecz do debugowania. **Na 2 godziny: szablony.** Ewentualnie mail przez LLM jako punkt w „planie rozwoju”.

**C. Ewaluacja LLM-as-judge.**
- Plusy: elastyczna.
- Minusy: Claude ocenia Claude'a (cyrkularne), jest wolna i niedeterministyczna, a rekruter tego nie powtórzy w ten sam sposób. **Odrzucić.** Lepiej hybrydowo i deterministycznie: każdy fakt to lista atomów sprawdzanych na polach strukturalnych (np. `termin_od == "2026-10-15"`, `"Toruńska 120" in opis`, `status == "zakaz" and "Opel" in opis`), z dopasowaniem bez wielkości liter i polskich końcówek tam, gdzie trzeba.

**D. Node zamiast Pythona.**
- Bez przewagi. Python stdlib ma `json`, `subprocess`, `datetime`, `html` i nic nie trzeba instalować. **Python stdlib.**

**E. Prościej: bez osobnych plików dla każdego rodzaju wyniku.**
- Jeden `raport.html` z sekcjami (zgłoszenia, konfiguracja, przypomnienia, zakazy, backlog, CRM, mail), a obok ewentualnie `raport.md`.
- Plusy: jeden renderer, mniej kodu.
- Minusy: brak. Siedem osobnych plików to dokładanie „na zapas”.

**F. Nie robić workflow wieloagentowego dla tego zadania.**
- Plusy: odzyskane 30–50 minut.
- Minusy: rekruter może chcieć zobaczyć proces. Kompromis: proces w wersji skróconej (opinie i plan zostają jako artefakty, tickety najwyżej 3, bez osobnych worktree).

## Rekomendacja

Robić, ale ciąć zakres i proces. Odpowiedzi na otwarte pytania:

- **Język:** Python stdlib.
- **Etap 2:** wyłącznie szablony z `wyniki.json`, zero drugiego wywołania LLM.
- **Ewaluacja:** deterministyczne atomy na polach strukturalnych plus sprawdzenie cytatów jako podciągów transkrypcji. Bez LLM-judge.
- **`wyniki.json`:** tak, commitować jako `samples/wyniki-przyklad.json`, a ewaluacja i raport mają tryb bez modelu.
- **Cena SMS:** 9.10 (piątek).

Kolejność (około 115 minut, bez zapasu na rozbudowany proces):

1. **(0:00–0:10) Spike `claude -p`.** Jedno wywołanie z tymczasowego `cwd`, bez narzędzi, z `--output-format json`, na pełnej transkrypcji. Sprawdzić: czas, czy wraca czysty JSON, czy nie wciąga `CLAUDE.md`. Jeśli to nie działa, nic dalej nie ma sensu.
2. **(0:10–0:45) `extract.py`:**
   - schemat z przedziałem dat, `do_klienta` i definicjami statusów;
   - kalendarz generowany w Pythonie i wklejony do promptu;
   - reguła „późniejsze nadpisuje, ignoruj podsumowanie końcowe”;
   - walidacja enumów i weryfikacja cytatów;
   - zapis `wyniki.json` i kopii referencyjnej.
3. **(0:45–1:10) `oczekiwane.json` i `eval.py`.** Poprawić fakt 1 (rozdzielić godziny dzwonienia i salonu) i fakt 12 (dwa różne powody blokady). Negacje sprawdzać tylko poza `cytat`. Wynik X/15 z listą, co nie przeszło.
4. **(1:10–1:35) `render.py`:** jeden `raport.html` z danymi w środku, sekcjami według typu, mailem z wyłącznie `do_klienta == true` i wyróżnionym oknem 12–16.10.
5. **(1:35–1:55) README i `run.sh` / `python3 main.py transkrypcja.md [--data RRRR-MM-DD]`:** Mermaid, założenia (reguły dat, perspektywa Rinvo, ograniczenia ewaluacji, przeuczenie) i plan rozwoju.

**Co uciąć od razu:**
- drugie wywołanie LLM;
- LLM-judge;
- osobne pliki dla każdego rodzaju wyniku;
- eksport .ics / do kalendarza;
- osobne worktree dla każdego ticketu;
- testy jednostkowe poza ewaluacją i weryfikacją cytatów (jeden test kalendarza dat jest tani, reszta zbędna).

Jeśli o 1:30 ewaluacja nie daje 15/15, nie stroić promptu dalej. Oddać uczciwy wynik z opisem przyczyny. Rekruter oceni to wyżej niż 15/15 uzyskane przez wklejenie odpowiedzi do promptu.
