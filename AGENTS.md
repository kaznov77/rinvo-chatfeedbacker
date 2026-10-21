<!-- WORKFLOW-AI:START -->
# Zasady pracy agentów AI

Ten plik czytają Codex (bezpośrednio) i Claude Code (przez `@AGENTS.md` w `CLAUDE.md`).
Obaj pracują według tych samych zasad.

## Pierwszeństwo zasad

Przy pracy nad ticketem (w `.worktrees/`, na gałęzi `ticket/…`) zasady tego workflow mają pierwszeństwo przed innymi zasadami gita w tym pliku (np. auto-commit i push do głównej gałęzi). Te inne zasady dotyczą tylko drobnych zadań poza ticketami.

## Stack projektu

- Język / framework: Python 3, tylko biblioteka standardowa; ekstrakcję robi `claude -p` (zalogowany Claude Code)
- Jak uruchomić projekt: `./uruchom.sh TRANSKRYPCJA [--data RRRR-MM-DD]` albo `./uruchom.sh --bez-modelu` (demo bez `claude`)
- Jak uruchomić testy: `python3 -m unittest`
- Linter / formatter: brak; sprawdzenie składni `python3 -m py_compile rinvo/*.py`
- Ważne katalogi: `rinvo/` (moduły i prompt), `tests/`, `samples/` (transkrypcja przykładowa), `tickets/`, `docs/`

## Workflow

1. **Pomysł:** użytkownik opisuje cel, pomysł albo dylemat w `docs/pomysl.md`.
2. **Konsultacja:** pomysł oceniają dwa modele niezależnie:
   - Claude Opus (agent `krytyk`) → `docs/opinie/claude.md`
   - Codex (`scripts/konsultuj-codex.sh`) → `docs/opinie/codex.md`
3. **Plan:** orkiestrator czyta pomysł i obie opinie i tworzy jeden plan w `docs/plan.md`.
4. **Tickety:** plan jest dzielony na tickety w `tickets/`, jeden plik = jedno zadanie.
   Użytkownik akceptuje listę ticketów, zanim cokolwiek zostanie zrealizowane.
5. **Realizacja:** każdy ticket realizuje jeden specjalista (`frontend`, `backend`, `tester`, …)
   w osobnym git worktree i na osobnej gałęzi.
6. **Review:** agent `reviewer` sprawdza wynik względem kryteriów ukończenia z ticketu.
   Scalenie do głównej gałęzi robi użytkownik (albo agent za jego wyraźną zgodą).

## Konwencja ticketów

- Plik: `tickets/T-001-krotki-opis.md` (numeracja rosnąca, 3 cyfry, opis kebab-case bez polskich znaków).
- Szablon: `tickets/_szablon.md`. Każdy ticket ma wypełnione wszystkie pola.
- Statusy: `do zrobienia` → `w trakcie` → `review` → `gotowe`.
- Ticket ma być mały: do zrobienia w jednej sesji, z jasno określonym zakresem plików
  i sprawdzalnymi kryteriami ukończenia.
- Zależności podaje się przez ID (np. `T-002`). Ticketu nie zaczyna się, dopóki jego zależności nie są `gotowe`.
- **Pionowe plasterki:** ticket dostarcza wąską, ale kompletną ścieżkę przez warstwy (dane, API, UI, testy), którą da się pokazać osobno. Nie dzielimy na „cały backend”, a potem „cały frontend”. Ewentualne porządki w kodzie, które ułatwiają zmianę, idą jako pierwszy ticket. Specjalista to dominująca warstwa plasterka.
- **Miejsca testów i kierunek wizualny** ustala orkiestrator w tickecie, a użytkownik akceptuje je razem z planem. Builderzy traktują je jako uzgodnione i nie pytają o nie ponownie.

## Skille używane przez builderów

Builderzy czytają te pliki i stosują je w swojej pracy:

- `~/.agents/skills/tdd/SKILL.md`: pętla czerwony → zielony, testy w „Miejscach testów” z ticketu.
- `~/.agents/skills/diagnosing-bugs/SKILL.md`: przy tickecie typu **problem** (najpierw powtarzalna pętla pokazująca błąd, potem hipotezy, poprawka i test regresji).
- `~/.agents/skills/frontend-design/SKILL.md`: przy UI, według „Kierunku wizualnego” z ticketu.

## Praca w osobnych worktree

- Każdy ticket ma własną gałąź `ticket/T-001-krotki-opis` i worktree w `.worktrees/T-001/`.
- `.worktrees/` jest w `.gitignore`.
- Agent pracuje **wyłącznie** w katalogu swojego worktree. Nie dotyka głównego katalogu ani worktree innych ticketów.
- Status i notatki agent aktualizuje w kopii ticketu wewnątrz swojego worktree. Trafiają do głównej gałęzi razem z kodem przy scaleniu.
- Po scaleniu worktree usuwa się poleceniem `git worktree remove .worktrees/T-001`.

## Zasady jakości

- **Zakres:** zmieniaj tylko pliki wymienione w „Zakresie plików” ticketu. Jeśli trzeba ruszyć coś spoza zakresu, zatrzymaj się, opisz to w notatkach ticketu i zapytaj.
- **Małe commity:** jeden logiczny krok = jeden commit. Wiadomość zaczyna się od ID ticketu, np. `T-003: dodaj walidację formularza`.
- **Testy:** każda zmiana logiki ma test. Przed oddaniem do review testy muszą przechodzić. Jeśli nie da się ich uruchomić, napisz to wprost.
- **Uczciwy raport:** nie deklaruj, że coś działa, jeśli tego nie sprawdziłeś. Niezrobione rzeczy wypisz w notatkach.
- **Bez niespodzianek:** nie instaluj zależności globalnie, nie zmieniaj konfiguracji poza projektem, nie rób `push` ani scalania bez zgody użytkownika.
- Dokumenty i notatki pisz po polsku.
<!-- WORKFLOW-AI:END -->
