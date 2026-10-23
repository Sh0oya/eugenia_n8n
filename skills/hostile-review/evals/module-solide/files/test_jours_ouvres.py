from datetime import date

from jours_ouvres import jours_ouvres

FERIES = frozenset({date(2026, 11, 11), date(2026, 12, 25)})


def tests():
    assert jours_ouvres(date(2026, 11, 2), date(2026, 11, 6)) == 5          # lundi → vendredi
    assert jours_ouvres(date(2026, 11, 7), date(2026, 11, 8)) == 0          # week-end
    assert jours_ouvres(date(2026, 11, 9), date(2026, 11, 13), FERIES) == 4  # 11 novembre férié
    assert jours_ouvres(date(2026, 11, 10), date(2026, 11, 10)) == 1        # un seul jour ouvré
    assert jours_ouvres(date(2026, 11, 8), date(2026, 11, 8)) == 0          # un seul jour, dimanche
    assert jours_ouvres(date(2026, 12, 21), date(2027, 1, 1), FERIES) == 9  # fin d'année, 25/12 férié
    try:
        jours_ouvres(date(2026, 11, 10), date(2026, 11, 9))
        raise AssertionError("ValueError attendue")
    except ValueError:
        pass


if __name__ == "__main__":
    tests()
    print("7 assertions OK")
