# Douter d'un chiffre, d'un indicateur, d'une analyse

Un chiffre faux est pire qu'un chiffre absent : on décide dessus, et il a l'air
précis. Avant de douter de la conclusion, doute de la **mesure**.

## Comment prouver

- **Recalcule toi-même** depuis les données brutes, avec un script ou à la
  main, et compare au chiffre annoncé. Montre le calcul.
- **Recalcule à la main sur trois à cinq lignes** pour vérifier la formule.
- **Compte les lignes à chaque étape** : avant et après chaque filtre, chaque
  jointure, chaque dédoublonnage. Une jointure qui multiplie les lignes ou un
  filtre qui en jette en silence se voit là.
- **Regarde les valeurs absolues** à côté des taux : un taux qui double alors
  que le numérateur ne bouge pas, c'est le dénominateur qui a changé.
- **Cherche une source indépendante** qui mesure la même chose autrement.
- En base de production : requêtes en lecture seule, uniquement.

## Doutes typiques

- **La définition a changé** entre les deux périodes : outil de mesure, filtre
  (robots, tests, comptes internes), périmètre, mode de calcul.
- **Périodes non comparables** : saisonnalité, mois incomplet, jours fériés,
  données du jour pas encore arrivées.
- **Le dénominateur** : par visiteur ou par visite, par commande ou par client.
- **Jointure qui duplique**, doublons dans la source.
- **Filtre qui exclut en silence** : une valeur vide écartée par une condition
  « différent de ».
- **Moyenne de moyennes** au lieu du ratio des totaux.
- **Effet de composition** : chaque segment baisse mais le total monte, parce
  que le mélange a changé.
- **Petits effectifs** : 4 conversions contre 2, ce n'est pas « doublé ».
- **Date de référence et fuseau** : création, paiement, livraison.
- **Unités** : HT ou TTC, devise, milliers ou unités.
- **Corrélation prise pour une cause** : la refonte a eu lieu, la hausse aussi —
  rien ne dit encore que l'une explique l'autre.
