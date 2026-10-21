import json
import os
import unittest

from rinvo import raport

DANE = os.path.join(os.path.dirname(__file__), "dane", "raport-przyklad.json")


def wczytaj():
    with open(DANE, encoding="utf-8") as f:
        return json.load(f)


class TestRaport(unittest.TestCase):
    def test_mail_pomija_elementy_wewnetrzne(self):
        w = wczytaj()
        w["elementy"][0]["do_klienta"] = False
        w["elementy"][0]["tytul"] = "TAJNY-WEWNETRZNY"
        w["elementy"][1]["do_klienta"] = True
        w["elementy"][1]["tytul"] = "WIDOCZNY-DLA-KLIENTA"
        mail = raport.szkic_maila(w)
        self.assertNotIn("TAJNY-WEWNETRZNY", mail)
        self.assertIn("WIDOCZNY-DLA-KLIENTA", mail)

    def test_script_w_opisie_jest_escapowany(self):
        w = wczytaj()
        w["elementy"][0]["opis"] = "<script>alert(1)</script>"
        h = raport.generuj_html(w)
        self.assertNotIn("<script>alert(1)</script>", h)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", h)


if __name__ == "__main__":
    unittest.main()
