# Logi z pracy z AI

Narzędzia w kolejności pracy (21.10.2026, ok. 13:10–14:10):

1. **Claude Code (Opus) jako orkiestrator**, komenda `/pomysl`: opis zadania w `docs/pomysl.md`. Sesja główna: `claude-code/<id>.jsonl`.
2. **Konsultacja z dwoma modelami równolegle:**
   - subagent `krytyk` (Claude) ocenił pomysł i zapisał opinię w `docs/opinie/claude.md`,
   - **Codex CLI** (`scripts/konsultuj-codex.sh`, `codex exec` w trybie tylko do odczytu) zapisał opinię w `docs/opinie/codex.md`. Log: `codex/rollout-*.jsonl`.
3. **Plan i tickety** napisał orkiestrator na podstawie obu opinii (`docs/plan.md`, `tickets/T-001…T-004`). Plan zaakceptowałem z poprawkami.
4. **Fala 1, trzy subagenty równolegle, każdy w osobnym git worktree:** `backend` (T-001, ekstrakcja przez `claude -p`), `frontend` (T-002, raport HTML), `tester` (T-003, `oczekiwane.json` i ewaluacja). Logi: `claude-code/<id>/subagents/`.
5. **Review:** subagent `reviewer` sprawdził każdy ticket. T-003 wymagał dwóch rund poprawek u testera. Potem scalenie do `main`.
6. **Fala 2:** subagent `backend` (T-004) przygotował `uruchom.sh`, wykonał przebiegi na obu transkrypcjach i napisał README. Potem review i scalenie.
7. **Dopracowanie przez orkiestratora:** pole `skrot` i rozwijane karty w raporcie, krótszy mail, reguła w prompcie naprawiająca fakt 15, przygotowanie oddania.

Wywołania `claude -p` wykonywane przez sam system (ekstrakcja) działały z `--no-session-persistence`, więc nie zostawiają osobnych logów.
