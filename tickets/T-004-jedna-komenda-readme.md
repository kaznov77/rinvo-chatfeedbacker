# T-004: Jedna komenda, przebieg demo i README

- **ID:** T-004
- **Tytuł:** `uruchom.sh`, prawdziwy przebieg na transkrypcji, wynik ewaluacji i README
- **Typ:** funkcja
- **Specjalista:** backend
- **Status:** w trakcie
- **Zależności:** T-001, T-002, T-003
- **Gałąź:** ticket/T-004-jedna-komenda-readme

## Cel

`./uruchom.sh <transkrypcja.md> [--data RRRR-MM-DD]` robi całość: ekstrakcja → `wyniki.json` → `raport.html` → ewaluacja (tylko gdy podano `--oczekiwane plik` albo transkrypcja to `samples/transkrypcja-spotkanie.md`; w innym wypadku wypisuje, że ewaluację pominięto). Na końcu podaje ścieżkę raportu. Dodatkowo `./uruchom.sh --bez-modelu` generuje raport i ewaluację z zacommitowanego `wyniki.json` (demo bez `claude`).

Kroki:
1. Prawdziwy przebieg na `samples/transkrypcja-spotkanie.md`. Jeśli ewaluacja < 15/15, najwyżej **2 poprawki** `rinvo/prompt_ekstrakcji.md` (reguły ogólne, bez wiedzy o kliencie). Potem oddać uczciwy wynik.
2. **Obowiązkowo:** przebieg na `transkrypcja-test-2.md` (patrz Miejsca testów), wynik do README; wyniki tego przebiegu zapisz w `wyniki-test-2/` (nie nadpisuj głównego `wyniki.json`).
3. Zacommitować końcowe `wyniki.json` i `raport.html`.
4. README (po polsku): problem; schemat procesu w Mermaid (transkrypcja → `claude -p` → walidacja i cytaty → `wyniki.json` → szablony → `raport.html` → człowiek zatwierdza; ewaluacja z boku); opis demo (co pokazać w raporcie, krok po kroku); uruchomienie jedną komendą na innej transkrypcji (wymagania: `python3`, zalogowany `claude`); założenia (perspektywa Rinvo, reguły dat, statusy, nic nie jest wysyłane, ewaluacja 15 faktów ≠ kompletność, niedeterminizm); faktyczny wynik ewaluacji na obu transkrypcjach; plan rozwoju.
5. Uzupełnić sekcję „Stack projektu” w `AGENTS.md` (Python 3 stdlib, `./uruchom.sh`, `python3 -m unittest`, brak lintera: `python3 -m py_compile rinvo/*.py`).


**Limit czasu:** wszystko (łącznie z T-004) ma być gotowe do 14:30. Nie dopracowuj. Jeśli coś się przeciąga, zatrzymaj się i opisz to w notatkach.

## Zakres plików

- `uruchom.sh`
- `README.md`
- `AGENTS.md` (tylko sekcja „Stack projektu”)
- `wyniki.json`, `raport.html` (wygenerowane)
- `rinvo/prompt_ekstrakcji.md` (tylko poprawki z kroku 1)
- `wyniki-test-2/`, `oczekiwane-test-2.json` (opcjonalnie)

## Miejsca testów

- `./uruchom.sh --bez-modelu`: wyłapie złe sklejenie modułów i ścieżek; nie wyłapie problemów z `claude`.
- `./uruchom.sh samples/transkrypcja-spotkanie.md`: pełny przebieg z modelem, ręcznie (wynik i czas w notatkach).
- **Obowiązkowo:** `./uruchom.sh transkrypcja-test-2.md` na drugiej transkrypcji od użytkownika (w katalogu głównym). Na jej końcu jest lista faktów: porównaj z wynikiem ręcznie albo przez krótki `oczekiwane-test-2.json`, a wynik (X/N, co nie wyszło) dopisz do README.
- `python3 -m unittest`: regresja modułów.

## Kryteria ukończenia

- [ ] `./uruchom.sh --bez-modelu` działa i kończy się wynikiem ewaluacji.
- [ ] Pełny przebieg z modelem wykonany; wynik X/15 wpisany do README i notatek.
- [ ] Przebieg na `transkrypcja-test-2.md` wykonany, porównanie z listą faktów w README.
- [ ] README ma wszystkie sekcje z etapu 4, Mermaid renderuje się na GitHubie (składnia `flowchart`).
- [ ] `python3 -m unittest` i `python3 -m py_compile rinvo/*.py` przechodzą.

## Notatki z realizacji

