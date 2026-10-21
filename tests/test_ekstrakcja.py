import unittest

from rinvo import ekstrakcja as ek


def el(**kw):
    e = {"id": "E01", "typ": "zadanie", "status": "teraz", "termin": None, "termin_do": None,
         "przypomnienie": None, "do_klienta": True, "cytaty": ["abc"]}
    e.update(kw)
    return e


class Waliduj(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ek.waliduj({"elementy": [el(termin="2026-10-08")]}), [])

    def test_zly_enum(self):
        self.assertTrue(ek.waliduj({"elementy": [el(typ="x")]}))
        self.assertTrue(ek.waliduj({"elementy": [el(status="x")]}))

    def test_zla_data(self):
        self.assertTrue(ek.waliduj({"elementy": [el(termin="8.10.2026")]}))
        self.assertTrue(ek.waliduj({"elementy": [el(termin_do="2026-13-40")]}))

    def test_zakaz_wymaga_statusu(self):
        self.assertTrue(ek.waliduj({"elementy": [el(typ="zakaz", status="teraz")]}))
        self.assertEqual(ek.waliduj({"elementy": [el(typ="zakaz", status="zakaz")]}), [])

    def test_puste_cytaty(self):
        self.assertTrue(ek.waliduj({"elementy": [el(cytaty=[])]}))


class Cytaty(unittest.TestCase):
    T = "**Marek:** Zadzwonię w „czwartek” – do Kasi.\n\nPotem   napiszę."

    def sprawdz(self, cytaty):
        w = {"elementy": [el(cytaty=cytaty)]}
        ek.zweryfikuj_cytaty(w, self.T)
        return w["elementy"][0]["cytaty_zweryfikowane"]

    def test_roznice_formatowania(self):
        self.assertTrue(self.sprawdz(['Zadzwonię w "czwartek" - do kasi.']))
        self.assertTrue(self.sprawdz(["Potem napiszę."]))

    def test_zmyslony(self):
        self.assertFalse(self.sprawdz(["Zadzwonię w piątek"]))

    def test_sklejony(self):
        self.assertFalse(self.sprawdz(["do Kasi. napiszę"]))


if __name__ == "__main__":
    unittest.main()
