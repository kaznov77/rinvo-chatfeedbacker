# Opinia Codex (GPT)

_Wygenerowano: 2026-10-21 13:20, codex-cli 0.163.0_

## Streszczenie (jak rozumiesz cel, 2-3 zdania)

Celem jest lokalny prototyp, który przekształca transkrypcję w uporządkowane ustalenia oraz szkice działań do zatwierdzenia przez człowieka. Najtrudniejsza część to zachowanie warunków, zakazów i późniejszych korekt bez dopisywania zobowiązań. W dwie godziny można zbudować przekonujące demo, ale deklaracja kompletności wymaga lepszej ewaluacji niż samo 15/15.

## Luki (czego brakuje w opisie, niejasności)

- **Pierwszy fakt ewaluacji jest niejednoznaczny.** Transkrypcja ustala dzwonienie w tygodniu 9–19, ale godziny salonu we Włocławku wcześniej określa jako 9–18. Końcowa korekta godzin salonów dotyczy soboty, do 15. Nie ma podstaw, aby wszystkim salonom przypisać w tygodniu 9–19 albo niedzielne zamknięcie. Trzeba osobno zapisać godziny dzwonienia i godziny salonów.
- **Obowiązkowa konkretna data wymusi zmyślanie.** Backlog nie ma terminu, korekta faktury ma przedział 12–16.10, a część zadań zależy od zdarzenia. Potrzebne są data, przedział albo `null`, z zachowaniem oryginalnego określenia.
- **Nie każdy właściciel jest wskazany.** Trzeba rozróżnić wykonawcę, osobę zatwierdzającą i odbiorcę informacji. Michał wystawia korektę, Marek przekazuje sprawę, Kasia przekazuje lub zatwierdza materiały. Nie należy przypisywać wszystkiego jednej osobie.
- **„Późniejsze wypowiedzi nadpisują wcześniejsze” jest zbyt szerokie.** Korekta powinna dotyczyć tego samego ustalenia i zakresu. Końcowe podsumowanie można traktować jako dodatkowy dowód, ale nie jako pełną listę ani podstawę usuwania wcześniejszych zobowiązań.
- **Brakuje granic warunków.** Zwrot zależy od potwierdzenia błędu Rinvo. Nowy mail jest wstrzymany do świeżych leadów, a nie zakazany bezterminowo. Opel wymaga powrotu do Kasi, również po deklaracji Pawła.
- **Nie wiadomo, kiedy wysłać przypomnienie.** „Jeśli nie przyjdą do 8.10” określa granicę oczekiwania, ale nie godzinę przypomnienia. Warto oddzielić termin dostarczenia od daty proponowanego kontaktu.
- **Lista 15 faktów nie obejmuje całego zadania.** Pomija m.in. samodzielne testy A/B w backlogu, raport tygodniowy, warunkową zmianę kolumn, ściągę statusów i szkolenie. Wynik 15/15 nie dowodzi kompletności ekstrakcji.

## Ryzyka (techniczne, produktowe, czasowe; przy każdym: prawdopodobieństwo i jak je ograniczyć)

| Ryzyko | Prawdopodobieństwo | Jak ograniczyć |
|---|---|---|
| Przekroczenie dwóch godzin przez liczbę artefaktów, workflow i poprawianie promptu | Wysokie | Jeden model danych, jeden generator HTML, minimum osobnych plików wynikowych. Wliczyć konsultacje, plan i review do budżetu. |
| Pozorny sukces ewaluacji: wynik zawiera poprawną informację obok sprzecznej | Wysokie | Oprócz obecności faktów sprawdzać zakazane wyniki, np. sobotę do 14, zaproszenie bez potwierdzenia i start agenta po godzinach. |
| Zamiana warunku lub hipotezy w zobowiązanie | Wysokie | Osobne pola warunku, zatwierdzenia i statusu; pokazywać je przy każdym szkicu. Zwrot opisywać warunkowo. |
| Niedeterministyczna ekstrakcja lub niepoprawny JSON | Średnie | Walidacja struktury, czytelny błąd, zachowanie surowej odpowiedzi i ograniczona liczba ponowień. Nie generować raportu z niezwalidowanych danych. |
| Rozbieżne ustalenia między raportem, CRM i mailem | Średnie przy drugim wywołaniu modelu | Generować wszystkie widoki deterministycznie z tego samego JSON. |
| Nadmierne dopasowanie rozwiązania do jednej transkrypcji | Wysokie | Dodać małe testy: późniejsza korekta, brak terminu, warunkowy zwrot, brak zgody. Oddzielić dane oczekiwane od promptu ekstrakcji. |
| HTML interpretuje treść transkrypcji jako znaczniki | Średnie | Escapować wszystkie wartości pochodzące z transkrypcji i modelu. |
| „Jedna komenda” działa tylko na komputerze autora | Średnie | Sprawdzać dostępność `claude`, logowanie i błędy procesu; opisać wymagania. Nie obiecywać uruchomienia bez konfiguracji środowiska. |

## Alternatywy (inne podejścia, z plusami i minusami)

1. **Python stdlib, jedna ekstrakcja, szablony wyników — rekomendowane.**  
   Plusy: brak nowych zależności, łatwa walidacja i jeden spójny zestaw ustaleń. Minus: mail będzie bardziej schematyczny, ale to rozsądny kompromis w prototypie.

2. **Drugie wywołanie modelu do maila i CRM.**  
   Plusy: naturalniejszy język i lepsza synteza. Minusy: dodatkowy czas, koszt i możliwość zmiany znaczenia ustaleń. Odłożyłbym to poza pierwsze dwie godziny.

3. **LLM jako sędzia ewaluacji.**  
   Plusy: rozpoznaje parafrazy. Minusy: sam może przeoczyć sprzeczność, a ocena jest zmienna. Przy ustrukturyzowanym JSON prostsze i bardziej wiarygodne będą asercje na polach; regex jedynie pomocniczo.

4. **Jeden raport zamiast siedmiu osobnych dokumentów.**  
   Plusy: wszystkie wymagane szkice można pokazać jako sekcje HTML, co skraca implementację i przegląd. Minus: eksport do narzędzi pozostaje przyszłym rozszerzeniem.

## Rekomendacja (co konkretnie zrobić, w jakiej kolejności; czy w ogóle warto)

**Warto, jako demonstrator wspomagający człowieka.** Największą wartością będzie poprawne rozpoznanie, czego nie wolno uruchamiać i od czego zależy następny krok.

1. **Najpierw poprawić kontrakt danych i oczekiwania.** Rozdzielić godziny dzwonienia od godzin salonów; dopuścić brak daty i przedziały. Dla „końca tygodnia” zachować cytat oraz jawną konwencję, np. piątek 9.10 jako przyjęty termin roboczy, bez przedstawiania go jako jednoznacznej wypowiedzi klienta.
2. **Uzgodnić małą listę ticketów zgodnie z workflow.** Nie dzielić pracy osobno na każdy rodzaj dokumentu. Wystarczą pionowe zakresy: ekstrakcja z walidacją, raport ze szkicami, ewaluacja i instrukcja.
3. **Zbudować minimalną ścieżkę:** plik wejściowy → `claude -p` → walidowany `wyniki.json` → `raport.html`. Każdy element powinien mieć stabilne ID, cytat oraz wskazanie miejsca w źródle. Nie wymagać terminu ani właściciela tam, gdzie rozmowa ich nie ustala.
4. **Generować szkice szablonami.** Raport ma wyraźnie pokazywać działania bieżące, oczekiwanie, blokady i backlog. Przypomnienia pozostają propozycjami kontaktu — prototyp nie sprawdzi sam, czy klient później przesłał plik.
5. **Sprawdzić 15 grup faktów oraz sprzeczności.** Osobno raportować brakujące fakty i błędne zobowiązania. Dodać kilka krótkich testów niezależnych od tej transkrypcji.
6. **Zakończyć README i zapisanym przykładem demo.** Przykład warto dołączyć jako rezultat konkretnego uruchomienia, z informacją o pochodzeniu; transkrypcja deklaruje fikcyjne dane. Zapisanie pliku nie oznacza zgody na commit.

Proponowany podział 120 minut: 15 na kontrakt i uzgodnienia, 45 na ekstrakcję, 25 na raport, 20 na ewaluację, 15 na README i demo. Jeśli zabraknie czasu, ograniczyć dopracowanie wizualne i stylistykę maila; zachować walidację, warunki i kontrolę sprzeczności.