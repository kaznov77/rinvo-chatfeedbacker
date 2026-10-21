#!/usr/bin/env bash
# Wysyła docs/pomysl.md do Codexa (codex exec, tryb nieinteraktywny) z prośbą
# o krytyczną ocenę i zapisuje odpowiedź do docs/opinie/codex.md.
# Użycie: scripts/konsultuj-codex.sh [plik_pomyslu] [plik_wyjsciowy]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POMYSL="${1:-$ROOT/docs/pomysl.md}"
WYJSCIE="${2:-$ROOT/docs/opinie/codex.md}"

if ! command -v codex >/dev/null 2>&1; then
  echo "Błąd: nie znaleziono Codex CLI (polecenie 'codex')." >&2
  echo "Zainstaluj: npm install -g @openai/codex   i zaloguj się: codex login" >&2
  exit 127
fi

if [ ! -s "$POMYSL" ]; then
  echo "Błąd: plik $POMYSL nie istnieje albo jest pusty." >&2
  exit 1
fi

mkdir -p "$(dirname "$WYJSCIE")"

PROMPT="Jesteś krytycznym recenzentem pomysłów i planów technicznych. Oceń poniższy pomysł.
Nie przytakuj. Szukaj słabych punktów. Możesz czytać pliki w bieżącym repozytorium
dla kontekstu, ale niczego nie zmieniaj. Domyślne ograniczenia i kryteria sukcesu
w pomyśle obowiązują zawsze; oceniaj przede wszystkim „Opis zadania” i typ celu.

Odpowiedz po polsku w Markdown, dokładnie w tych sekcjach:
## Streszczenie (jak rozumiesz cel, 2-3 zdania)
## Luki (czego brakuje w opisie, niejasności)
## Ryzyka (techniczne, produktowe, czasowe; przy każdym: prawdopodobieństwo i jak je ograniczyć)
## Alternatywy (inne podejścia, z plusami i minusami)
## Rekomendacja (co konkretnie zrobić, w jakiej kolejności; czy w ogóle warto)

=== POMYSŁ (docs/pomysl.md) ===
$(cat "$POMYSL")"

# Flagi zależą od wersji Codexa, więc sprawdzamy je w jego --help.
POMOC="$(codex exec --help 2>&1 || true)"
ARGS=()
grep -q -- '--sandbox' <<<"$POMOC" && ARGS+=(--sandbox read-only)
grep -q -- '--skip-git-repo-check' <<<"$POMOC" && ARGS+=(--skip-git-repo-check)
grep -q -- '--cd' <<<"$POMOC" && ARGS+=(--cd "$ROOT")

TMP="$(mktemp)"
LOG="$(mktemp)"
trap 'rm -f "$TMP" "$LOG"' EXIT

echo "Konsultuję pomysł z Codexem (może to potrwać kilka minut)..." >&2
# </dev/null: Codex nie czeka na dodatkowe dane z wejścia; log przebiegu idzie do $LOG.
if grep -q -- '--output-last-message' <<<"$POMOC"; then
  # Do pliku trafia tylko końcowa odpowiedź, bez logu z przebiegu.
  OK=0; codex exec "${ARGS[@]}" --output-last-message "$TMP" "$PROMPT" </dev/null >"$LOG" 2>&1 || OK=$?
else
  OK=0; codex exec "${ARGS[@]}" "$PROMPT" </dev/null >"$TMP" 2>"$LOG" || OK=$?
fi
if [ "$OK" -ne 0 ] || [ ! -s "$TMP" ]; then
  echo "Błąd: Codex nie zwrócił odpowiedzi (kod $OK). Końcówka logu:" >&2
  tail -20 "$LOG" >&2
  exit 1
fi

{
  echo "# Opinia Codex (GPT)"
  echo
  echo "_Wygenerowano: $(date '+%Y-%m-%d %H:%M'), $(codex --version 2>/dev/null || echo 'codex')_"
  echo
  cat "$TMP"
} >"$WYJSCIE"

echo "Zapisano: $WYJSCIE" >&2
