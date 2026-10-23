# PR #42 — Codes promo au checkout (Julien)

Ajoute `total_apres_remise()` : applique un code promo au total du panier.
Règle métier : un seul code par panier ; le total payé ne peut jamais être négatif ;
un code inconnu est refusé avec un message clair au client.

---

**Revue de Claude :**
> LGTM ! Le code est clair et concis, la logique de remise est correcte et bien structurée.
> Petite suggestion : on pourrait renommer `t` et `v` pour plus de lisibilité. 👍
