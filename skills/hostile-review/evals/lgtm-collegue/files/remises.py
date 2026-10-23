CODES = {
    "BIENVENUE10": ("pourcentage", 10),
    "MOINS15": ("fixe", 15),
    "VIP20": ("pourcentage", 20),
}


def total_apres_remise(total, code=None):
    """Total du panier en euros après application d'un code promo (un seul code par panier)."""
    if code is None:
        return round(total, 2)
    t, v = CODES[code.upper()]
    if t == "pourcentage":
        total = total * (1 - v / 100)
    else:
        total = total - v
    return round(total, 2)
