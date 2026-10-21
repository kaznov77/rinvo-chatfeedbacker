"""Daty: wyciąganie daty spotkania z nagłówka i kalendarz po polsku."""
import re
from datetime import date, timedelta

MIESIACE = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6,
    "lipca": 7, "sierpnia": 8, "września": 9, "października": 10, "listopada": 11, "grudnia": 12,
}
DNI = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]


def data_z_naglowka(tekst):
    """Zwraca date z pierwszego wystąpienia 'D <miesiąc> RRRR' w pierwszych 2000 znakach, albo None."""
    wzor = r"\b(\d{1,2})\s+(" + "|".join(MIESIACE) + r")\s+(\d{4})\b"
    m = re.search(wzor, tekst[:2000], re.IGNORECASE)
    if not m:
        return None
    try:
        return date(int(m.group(3)), MIESIACE[m.group(2).lower()], int(m.group(1)))
    except ValueError:
        return None


def kalendarz(start, dni=21):
    """Lista linii 'RRRR-MM-DD dzień' od start przez `dni` dni włącznie."""
    return [f"{(start + timedelta(days=i)).isoformat()} {DNI[(start + timedelta(days=i)).weekday()]}"
            for i in range(dni + 1)]
