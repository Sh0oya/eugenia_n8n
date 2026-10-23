from datetime import date

from relances import factures_a_relancer


def test_relance_1_a_j_plus_3(tmp_path=None):
    import os, tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "f.csv")
    with open(p, "w", encoding="utf-8") as f:
        f.write("numero,email,montant,echeance,statut\nF1,a@b.fr,120.00,2026-10-05,à payer\n")
    assert factures_a_relancer(p, date(2026, 10, 8))[0][1] == 1


if __name__ == "__main__":
    test_relance_1_a_j_plus_3()
    print("1 test OK")
