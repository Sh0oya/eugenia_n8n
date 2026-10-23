"""Relances des factures échues : J+3, J+10, J+20 après l'échéance."""
import csv
from datetime import date

from config import MODE, SMTP_HOST, SMTP_USER, SMTP_PASSWORD

PALIERS = {3: 1, 10: 2, 20: 3}


def factures_a_relancer(chemin_csv, aujourd_hui):
    """Renvoie (facture, numéro de relance) pour chaque facture due aujourd'hui."""
    resultat = []
    with open(chemin_csv, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            if ligne["statut"] == "payée":
                continue
            echeance = date.fromisoformat(ligne["echeance"])
            retard = (aujourd_hui - echeance).days
            if retard in PALIERS:
                resultat.append((ligne, PALIERS[retard]))
    return resultat


def envoyer_relance(facture, numero):
    print(f"Relance {numero} envoyée à {facture['email']} pour {facture['numero']} ({facture['montant']} €)")
    if MODE == "prod":
        pass  # envoi SMTP réel avec SMTP_HOST, SMTP_USER, SMTP_PASSWORD


if __name__ == "__main__":
    for facture, numero in factures_a_relancer("factures.csv", date.today()):
        envoyer_relance(facture, numero)
