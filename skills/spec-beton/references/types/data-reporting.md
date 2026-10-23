# Module — dashboard, reporting, pipeline de données

Un indicateur faux est pire qu'un indicateur absent : on décide dessus. Les
trous d'une spec de reporting sont presque toujours dans **la définition exacte
des chiffres**, rarement dans les graphiques.

## Questions qu'on oublie

**La décision d'abord**
- Quelle décision chaque vue aide-t-elle à prendre, qui la prend, à quelle
  fréquence ? Un indicateur qui ne déclenche aucune décision est décoratif :
  hors périmètre.

**Chaque indicateur, défini au centime près**
- La formule exacte, et ce qu'elle inclut ou exclut : remboursements,
  annulations, commandes de test, comptes internes, taxes.
- La **date de référence** : création, paiement, livraison ? Dans quel fuseau ?
- Un **exemple recalculé à la main** sur des données réelles, avec le résultat
  attendu : c'est le test de recette de l'indicateur.

**Sources**
- D'où vient chaque donnée, qui en est responsable, quelle qualité (doublons,
  trous, saisies manuelles) ?
- Deux sources qui divergent sur le même chiffre : laquelle fait foi ?

**Fraîcheur**
- Temps réel, chaque heure, chaque nuit ? À quelle heure les chiffres de la
  veille sont-ils complets ? Comment le lecteur sait-il de quand datent les
  données affichées ?

**Lecture**
- Granularité (jour, semaine, mois), filtres, comparaisons (période
  précédente, année précédente, objectif), détail au clic.
- **Zéro** et **pas de donnée** s'affichent-ils différemment ?

**Accès**
- Qui voit quoi : un commercial voit-il ses chiffres seulement, ou ceux de
  toute l'équipe ?

**Dans le temps**
- Quand une définition change, recalcule-t-on l'historique ou garde-t-on les
  anciens chiffres ? Le lecteur le sait-il ?
- Alertes sur seuil : lesquelles, vers qui ?
- Exports : format, qui, à quelle fréquence.

## Pièges

- **Le même mot, deux chiffres** : « chiffre d'affaires » calculé hors taxes ici,
  toutes taxes là. Le glossaire de la spec tranche une définition par terme.
- **Affiché ≠ appliqué** : le même indicateur calculé à deux endroits dérive.
- **La donnée incomplète prise pour une baisse** : les chiffres de ce matin ne
  sont pas encore tous arrivés.
- **Le zéro qui ment** : une source coupée affiche 0 au lieu d'une erreur.

## Zones à ajouter à la carte de couverture

Décisions servies · définition de chaque indicateur · sources et source de
vérité · fraîcheur · accès · évolution des définitions.
