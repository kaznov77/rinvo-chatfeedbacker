import json
import unittest
from pathlib import Path

from rinvo import ewaluacja

KORZEN = Path(__file__).resolve().parent.parent
DANE = Path(__file__).resolve().parent / "dane"


def wczytaj(sciezka):
    return json.loads(Path(sciezka).read_text(encoding="utf-8"))


class OcenaTest(unittest.TestCase):
    def setUp(self):
        self.oczekiwane = wczytaj(KORZEN / "oczekiwane.json")

    def test_oczekiwane_ma_15_faktow_z_atomami(self):
        self.assertEqual(len(self.oczekiwane), 15)
        self.assertTrue(all(f["atomy"] for f in self.oczekiwane))

    def test_dobry_wynik_daje_15_z_15_i_kod_0(self):
        rez = ewaluacja.ocen(wczytaj(DANE / "ewaluacja-dobry.json"), self.oczekiwane)
        self.assertEqual([r["id"] for r in rez if not r["ok"]], [])
        self.assertEqual(ewaluacja.main([str(DANE / "ewaluacja-dobry.json")]), 0)

    def test_zepsuty_wynik_lapie_sobote_do_14_dwa_przypomnienia_i_brak_opla(self):
        rez = ewaluacja.ocen(wczytaj(DANE / "ewaluacja-zepsuty.json"), self.oczekiwane)
        niezaliczone = {r["id"] for r in rez if not r["ok"]}
        self.assertEqual(niezaliczone, {1, 8, 11})
        self.assertEqual(ewaluacja.main([str(DANE / "ewaluacja-zepsuty.json")]), 1)


if __name__ == "__main__":
    unittest.main()
