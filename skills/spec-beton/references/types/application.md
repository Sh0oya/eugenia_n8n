# Module — application web ou mobile, SaaS, outil interne

Une application vit dans la durée : elle sera utilisée par des gens qui n'ont
pas assisté à sa conception, sur des données qui grossissent. Les trous se
trouvent aux bords : premier usage, données en masse, deux personnes en même
temps, suppression.

## Questions qu'on oublie

**Rôles et accès**
- La matrice rôle × action : qui crée, lit, modifie, supprime quoi ? Que voit
  celui qui n'a pas le droit — rien, un bouton grisé, un message ?
- Qui crée les comptes : inscription libre, invitation, création par un admin ?
  Quel rôle par défaut ?
- Le dernier administrateur peut-il se retirer ? Un compte peut-il être partagé ?
- Connexion : par quel moyen, mot de passe oublié, durée de session, appareil
  perdu ?

**Chaque écran a quatre états**
- **Vide** (premier usage : que voit-on, que propose-t-on ?), **chargement**,
  **erreur**, **rempli**. Les spécifier pour chaque écran clé.

**Listes et recherche**
- Tri par défaut, filtres, recherche sur quels champs, pagination.
- Ce qui se passe à 10 000 éléments : la spec dit le volume attendu à un an.

**Formulaires**
- Pour chaque champ : obligatoire ou non, format, bornes, valeur par défaut.
- Saisie perdue si l'on quitte la page ? Brouillon ? Double envoi au double clic ?

**Suppression et historique**
- Suppression définitive ou corbeille, et pendant combien de temps ?
- Effet sur les objets liés : un client supprimé emporte-t-il ses factures ?
- Faut-il savoir qui a modifié quoi, et quand ?

**Concurrence**
- Deux personnes modifient le même objet : la dernière écrase, la seconde est
  prévenue, ou l'objet est verrouillé ?

**Notifications**
- Lesquelles, par quel canal (dans l'app, email, push), réglables par
  l'utilisateur ? Regroupées ou une par événement ?

**Si c'est un SaaS payant**
- Offres, limites par offre, ce qui arrive au dépassement d'une limite, période
  d'essai, carte expirée, résiliation : que deviennent les données ?

**Le reste**
- Appareils : ordinateur, mobile, hors connexion ?
- Langues, accessibilité, export des données, droit à l'effacement.
- Données de départ : import initial, ou l'application démarre vide ?
- Qui administre, modère, répond au support ?

## Pièges

- **L'écran vide oublié** : la spec décrit l'écran rempli, le premier
  utilisateur voit une page blanche et repart.
- **Le droit implicite** : « l'utilisateur modifie sa fiche » sans dire s'il peut
  modifier celle des autres.
- **La suppression en cascade** : supprimer un élément efface des données dont
  quelqu'un d'autre avait besoin.
- **La liste qui ne tient pas l'échelle** : spécifiée avec 20 lignes, utilisée
  avec 20 000.

## Zones à ajouter à la carte de couverture

Rôles et matrice d'accès · états des écrans · listes et recherche ·
formulaires · suppression et historique · concurrence · offres et facturation
(SaaS).
