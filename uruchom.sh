#!/usr/bin/env bash
# Jedna komenda: transkrypcja -> wyniki.json -> raport.html -> ewaluacja.
# Użycie: ./uruchom.sh TRANSKRYPCJA [--data RRRR-MM-DD] [--oczekiwane PLIK] [--wyjscie-dir KATALOG]
#         ./uruchom.sh --bez-modelu     (raport i ewaluacja z zacommitowanego wyniki.json)
set -euo pipefail
cd "$(dirname "$0")"

TRANSKRYPCJA=""; DATA=""; OCZEKIWANE=""; KAT="."; BEZ_MODELU=0
while [ $# -gt 0 ]; do
  case "$1" in
    --bez-modelu) BEZ_MODELU=1 ;;
    --data) DATA="${2:?brak wartości dla --data}"; shift ;;
    --oczekiwane) OCZEKIWANE="${2:?brak wartości dla --oczekiwane}"; shift ;;
    --wyjscie-dir) KAT="${2:?brak wartości dla --wyjscie-dir}"; shift ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    -*) echo "Nieznana opcja: $1" >&2; exit 2 ;;
    *) TRANSKRYPCJA="$1" ;;
  esac
  shift
done

if [ "$BEZ_MODELU" = 1 ]; then
  OCZEKIWANE="${OCZEKIWANE:-oczekiwane.json}"
else
  [ -n "$TRANSKRYPCJA" ] || { echo "Podaj plik transkrypcji (albo --bez-modelu)." >&2; exit 2; }
  [ -f "$TRANSKRYPCJA" ] || { echo "Brak pliku: $TRANSKRYPCJA" >&2; exit 2; }
  command -v claude >/dev/null || { echo "Brak polecenia claude (zalogowany Claude Code)." >&2; exit 2; }
  if [ -z "$OCZEKIWANE" ] && [ "$TRANSKRYPCJA" = "samples/transkrypcja-spotkanie.md" ]; then
    OCZEKIWANE="oczekiwane.json"
  fi
fi

mkdir -p "$KAT"
WYNIKI="$KAT/wyniki.json"; RAPORT="$KAT/raport.html"

if [ "$BEZ_MODELU" = 0 ]; then
  echo "[1/3] Ekstrakcja (claude -p, ok. 2-3 min)..."
  ARGS=("$TRANSKRYPCJA" --wyjscie "$WYNIKI")
  [ -n "$DATA" ] && ARGS+=(--data "$DATA")
  python3 -m rinvo.ekstrakcja "${ARGS[@]}"
fi

echo "[2/3] Raport..."
python3 -m rinvo.raport "$WYNIKI" --wyjscie "$RAPORT"

CODE=0
if [ -n "$OCZEKIWANE" ]; then
  echo "[3/3] Ewaluacja względem $OCZEKIWANE..."
  python3 -m rinvo.ewaluacja "$WYNIKI" "$OCZEKIWANE" || CODE=$?
else
  echo "[3/3] Ewaluację pominięto (brak --oczekiwane i to nie jest transkrypcja przykładowa)."
fi
echo "Raport: $RAPORT"
exit $CODE
