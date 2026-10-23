"""Nombre de jours ouvrés entre deux dates."""
from datetime import date, timedelta


def jours_ouvres(debut: date, fin: date, feries: frozenset[date] = frozenset()) -> int:
    """Nombre de jours ouvrés (lundi à vendredi, hors fériés) de debut à fin, bornes incluses.

    Lève ValueError si fin est antérieure à debut.
    """
    if fin < debut:
        raise ValueError("fin antérieure à debut")
    total = 0
    jour = debut
    while jour <= fin:
        if jour.weekday() < 5 and jour not in feries:
            total += 1
        jour += timedelta(days=1)
    return total
