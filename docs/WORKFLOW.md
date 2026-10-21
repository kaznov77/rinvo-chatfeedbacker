# Workflow AI: instrukcja

Agenci i komendy Claude są zainstalowani globalnie w `~/.claude/` i działają w każdym projekcie.
Pliki projektu (ten folder `docs/`, `tickets/`, `scripts/`, `AGENTS.md`) wgrywa się komendą
`/wdroz-workflow` albo poleceniem `~/.ai-workflow/wdroz.sh <katalog>`.

## Najprościej: jeden wątek, jedna wiadomość

W T3 Code otwórz **wątek Claude** w projekcie i opisz pomysł zwykłym tekstem albo przez `/pomysl <opis>`.
Orkiestrator (Claude) sam przechodzi cały proces:

1. zapisuje pomysł do `docs/pomysl.md`,
2. konsultuje go równolegle z Claude Opus (`krytyk`) i Codexem,
3. zestawia opinie w finalny wynik i tworzy plan i tickety,
4. **★ pyta Cię o akceptację planu**,
5. rozdziela tickety między builderów (`frontend`, `backend`, `tester`), każdy w swoim worktree, niezależne równolegle,
6. puszcza `reviewer` na każdy ticket i zleca poprawki (najwyżej 2 rundy),
7. **★ pyta Cię o zgodę na scalenie**, scala, uruchamia lint, build i testy i podsumowuje.

Odpowiadasz tylko dwa razy: „tak” przy planie i „tak” przy scaleniu.
Wątek musi być wątkiem **Claude**. Codex jest wywoływany w tle przez skrypt. W wątku Codexa agenci Claude nie działają.

## Krok po kroku (gdy chcesz sterować każdym etapem)

1. **Opisz pomysł** w `docs/pomysl.md` (Cel, Kontekst, Ograniczenia, Kryteria sukcesu, Otwarte pytania).
2. **`/konsultuj`**: agent `krytyk` (Claude Opus) i Codex niezależnie oceniają pomysł.
   Opinie trafiają do `docs/opinie/claude.md` i `docs/opinie/codex.md`, a na ekranie
   pojawia się zestawienie: gdzie się zgadzają, a gdzie różnią.
3. **`/planuj`**: powstaje `docs/plan.md` i tickety w `tickets/`. Przejrzyj listę i zaakceptuj
   ją albo popraw.
4. **Zacommituj plan i tickety** (np. `git add docs tickets && git commit -m "plan"`).
   Worktree tworzy się z ostatniego commita, więc bez tego ticket nie będzie w nim widoczny.
5. **`/realizuj T-001`**: powstaje gałąź `ticket/T-001-…` i worktree `.worktrees/T-001/`,
   a ticket dostaje odpowiedni specjalista. Niezależne tickety możesz realizować równolegle
   w osobnych wątkach.
6. **`/review T-001`**: reviewer porównuje zmiany z kryteriami ukończenia i wypisuje problemy.
   Jeśli są problemy, uruchom `/realizuj T-001` ponownie: specjalista poprawi je w tym samym worktree.
7. **Scal gotowy ticket:**
   ```bash
   git merge ticket/T-001-krotki-opis
   git worktree remove .worktrees/T-001
   git branch -d ticket/T-001-krotki-opis
   ```

## Ręcznie w T3 Code (gdy komendy nie są dostępne w wątku)

**Konsultacja**: otwórz dwa osobne wątki:
- Wątek Claude: „Przeczytaj `docs/pomysl.md` i oceń go krytycznie: luki, ryzyka, alternatywy,
  rekomendacja. Nie przytakuj. Zapisz opinię do `docs/opinie/claude.md`.”
- Wątek Codex: to samo, z zapisem do `docs/opinie/codex.md`. Możesz też w terminalu uruchomić
  `scripts/konsultuj-codex.sh`.

**Plan**: w wątku Claude (lub Codex): „Przeczytaj `docs/pomysl.md`, `docs/opinie/claude.md`
i `docs/opinie/codex.md`. Uzupełnij `docs/plan.md` i rozbij plan na tickety w `tickets/`
według `tickets/_szablon.md` i zasad z `AGENTS.md`. Pokaż mi listę do akceptacji.”

**Realizacja**: w terminalu:
```bash
git worktree add -b ticket/T-001-krotki-opis .worktrees/T-001
```
Potem otwórz w T3 Code nowy wątek z katalogiem `.worktrees/T-001` i napisz:
„Zrealizuj ticket `tickets/T-001-….md` zgodnie z `AGENTS.md`. Pracuj tylko w jego zakresie plików,
aktualizuj status i notatki w tickecie.”

**Review**: nowy wątek (najlepiej innym modelem niż ten, który pisał kod):
„Sprawdź zmiany na gałęzi `ticket/T-001-…` (`git diff main...HEAD`) względem kryteriów ukończenia
w tickecie. Niczego nie poprawiaj, tylko wypisz problemy.”
