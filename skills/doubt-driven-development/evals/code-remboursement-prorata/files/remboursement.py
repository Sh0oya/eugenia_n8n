"""Remboursement au prorata lors de la résiliation d'un abonnement."""
from datetime import date


def jours_restants(fin_periode: date, date_resiliation: date) -> int:
    """Jours non consommés entre la résiliation et la fin de la période."""
    return (fin_periode - date_resiliation).days


def remboursement(montant_periode: float, debut_periode: date, fin_periode: date,
                  date_resiliation: date) -> float:
    """Montant à rembourser pour les jours non consommés de la période en cours."""
    jours_periode = (fin_periode - debut_periode).days
    restant = jours_restants(fin_periode, date_resiliation)
    return round(montant_periode * restant / jours_periode, 2)
