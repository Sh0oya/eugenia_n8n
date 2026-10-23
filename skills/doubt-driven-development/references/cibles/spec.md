# Douter d'une spec, d'un plan, d'un document de décision

Un document ne s'exécute pas : sa preuve, c'est un lecteur qui n'a pas assisté
à sa rédaction et qui doit pouvoir agir sans rien demander. Son contrat :
« un constructeur peut agir sans poser de question », plus les décisions prises
par l'utilisateur.

## Doute léger — ce que tu prouves toi-même

- **Confronte le plan au contrat dans les deux sens** : chaque exigence du
  contrat a-t-elle son étape ? chaque étape répond-elle à une exigence ? Avec
  une spec spec-beton, passe ses règles une par une : une règle sans étape qui
  la couvre est un oubli.
- **Recoupe chaque chiffre avec sa source.** Un chiffre sans source est une
  supposition, quel que soit son ton.
- **Vérifie chaque affirmation sur l'existant** (« aujourd'hui le système
  fait… ») dans la source elle-même : code, outil, documentation datée.
- **Si le document est une spec au format spec-beton**, lance son script de
  contrôle (`scripts/check_spec.py` du skill spec-beton).

## Doute approfondi — la relecture à froid

Pour un document dont l'erreur coûterait cher (un plan qui part chez un client,
une spec qui engage un budget), ou à la demande. Donne au relecteur le seul
document, avec ce prompt à la place du prompt général :

> Tu vas construire ceci à partir de ce seul document. Liste les questions que
> tu devrais poser avant de pouvoir le faire sans rien deviner, classées par
> gravité, puis les contradictions. Ne propose aucune solution.

Chaque question rendue est un trou. Si le document est une spec spec-beton,
son audit (`references/audit.md` de spec-beton) fait la même chose en plus
complet.

## Doutes typiques

- Une règle qui ne se teste pas (« rapide », « simple », « robuste »).
- Le chemin heureux seul : aucun cas limite, aucune panne, aucun rejeu.
- Deux sections qui se contredisent, ou un exemple chiffré qui contredit sa
  règle.
- Une supposition implicite que personne n'a validée.
- Du périmètre ajouté en silence, que personne n'a demandé.
- Une solution technique déguisée en exigence.
- Un comportement de l'existant affirmé sans avoir été vérifié.
- Un plan qui oublie ce qui se passe **après** : désactivation, suppression,
  reprise de l'existant, maintenance, ou un jour où rien n'a tourné.
