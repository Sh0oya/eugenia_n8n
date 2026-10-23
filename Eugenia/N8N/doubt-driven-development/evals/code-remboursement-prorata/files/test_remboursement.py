from datetime import date

from remboursement import remboursement


def test_resiliation_en_milieu_de_mois():
    assert remboursement(29.90, date(2026, 1, 1), date(2026, 1, 31), date(2026, 1, 16)) == 14.95


def test_resiliation_le_dernier_jour():
    assert remboursement(29.90, date(2026, 1, 1), date(2026, 1, 31), date(2026, 1, 31)) == 0.0


if __name__ == "__main__":
    test_resiliation_en_milieu_de_mois()
    test_resiliation_le_dernier_jour()
    print("2 tests OK")
