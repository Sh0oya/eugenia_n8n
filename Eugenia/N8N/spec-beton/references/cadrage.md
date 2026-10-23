# Cadrage — reformuler, ouvrir, refermer, challenger

Phases 1 à 3. Le but : que le problème soit établi et le périmètre choisi
**avant** qu'une seule règle soit écrite. Spécifier un problème mal posé est la
première des deux façons de rater une spec ; la seconde, les trous, se traite
en phase 4.

## Phase 1 — Reformuler

Reformule le sujet en **une phrase**, puis tranche : **est-ce un problème, ou
une solution déjà choisie ?**

« Je veux un chatbot sur mon site », « un CRUD pour gérer les stocks », « un
workflow n8n qui envoie les leads dans Notion » décrivent une solution. Ils ne
disent pas quel comportement est empêché aujourd'hui, pour qui, ni ce que ça
coûte. Remonte d'un cran : *qu'est-ce que ces personnes n'arrivent pas à faire,
et que font-elles à la place ?* Tant que la réponse manque, il n'y a pas de spec
possible — seulement la description d'un outil.

Ne rejette pas la solution du demandeur : elle devient une option parmi
d'autres à l'ouverture, souvent la bonne. Ce qui compte, c'est qu'elle soit
**choisie** et non **subie**.

### Le lot du pourquoi

Premier lot de questions, sur ce que le brief ne dit pas encore :

- **qui** subit le problème, combien de personnes, à quelle fréquence ;
- le **contournement actuel**, et pourquoi il ne suffit plus ;
- ce qu'il **coûte** (temps, argent, erreurs, clients perdus), en ordre de grandeur ;
- **pourquoi maintenant** ;
- à quoi on reconnaîtra le **succès**, en chiffre — et ce qui serait un
  **échec même si tout marche techniquement** (le contre-objectif, qui devient
  souvent le garde-fou d'un indicateur) ;
- **qui construira** à partir de la spec (toi, un dev, un agent de code, un
  prestataire) — ça règle le niveau de détail ;
- les **contraintes imposées** : budget, échéance, outils déjà en place.

Ce sont des **thèmes**, pas sept questions à recopier : saute ce qui est déjà
dans le brief, choisis les 3 à 5 qui manquent le plus, et pose-les une chose
à la fois. Le reste attend le lot suivant. Un problème sans contournement
observé est souvent un problème qui n'existe pas encore : dis-le.

## Phase 2 — Ouvrir, en un seul message

Objectif : que l'utilisateur ait vu le champ avant de choisir, et que ce qu'il
écarte soit écarté sciemment. La valeur n'est pas dans le nombre d'idées, elle
est dans **les cadrages auxquels il n'avait pas pensé**.

**Cherche avant de proposer.** Fichiers fournis, dépôt, docs, et le web si tu
y as accès : une option adossée à un outil existant ou à un précédent réel vaut
dix intuitions. Ce que tu n'as pas cherché, dis-le, n'invente pas.

La carte des possibles tient en cinq axes, cinq propositions au plus par axe,
chacune marquée `[hypothèse]` :

1. **Trois altitudes du problème** — plus étroit, tel que posé, plus large.
   Une ligne chacune : ce qu'elle inclut, ce qu'elle coûte. C'est l'axe le plus
   important : l'altitude choisie décide de tout le reste.
2. **Acteurs non envisagés** — qui d'autre subit, touche ou reçoit : le client
   final qui reçoit l'email, le comptable qui lit l'export, la personne qui
   maintiendra l'outil dans un an.
3. **Cas d'usage voisins** — trois à cinq candidats au « premier cas d'usage »,
   pour que le premier soit choisi, pas subi.
4. **Options de réponse**, au niveau produit, jamais technique : ne rien faire ·
   changer le process sans outil · utiliser autrement un outil déjà payé ·
   un outil du marché · une automatisation ou du no-code · construire sur mesure.
   **« Ne rien faire » est toujours présent et argumenté.**
5. **Précédents et signaux** — ce qui existe déjà, chez l'utilisateur ou sur le
   marché. Chaque signal porte sa source et sa date, sinon il ne figure pas.

Range : dis ce que tu retiendrais, ce que tu écarterais, et pourquoi. Ne propose
aucune solution détaillée avant que le cadrage soit choisi : une solution
énoncée trop tôt ancre la discussion et referme le champ. L'ouverture tient en
**un aller-retour** ; au second, on converge.

## Phase 2b — Refermer

Ouvrir sans refermer remplace un cadrage étroit par un cadrage flou. La
fermeture est un livrable : le **tableau de recentrage**, un axe par ligne.

| Axe | Retenu | Écarté | Destination |
| --- | --- | --- | --- |
| Altitude du problème | la formulation retenue | les deux autres | Hors périmètre |
| Acteurs | les deux qui comptent | le troisième — motif | Renvoyé à plus tard, revient si… |
| Cas d'usage | le premier | les suivants | Renvoyé à plus tard, revient si… |
| Options de réponse | automatiser | ne rien faire, outil du marché | Abandonné — motif |

Quatre destinations, et seulement quatre :

- **Hors périmètre** (§3) — écarté pour ce projet, définitivement ;
- **Renvoyé à plus tard** (§3) — avec **la condition qui le ferait revenir**.
  Sans condition, ce n'est pas un report, c'est un oubli ;
- **Reste à prouver** (§11) — non tranchable faute d'information : qui peut la
  fournir, et ce que la réponse changerait ;
- **Abandonné — motif** — consigné au journal seulement.

Archive le tableau dans le JOURNAL sous le titre exact
`## Champ des possibles exploré — AAAA-MM-JJ` (le script le cherche). Il répond,
six mois plus tard, à « pourquoi on n'a pas fait X ».

**La sortie de la fermeture est une phrase** : le cadrage retenu, que
l'utilisateur valide explicitement. Elle deviendra le §0, mot pour mot. Une
bonne phrase dit le verbe, pour qui, quoi, et sa limite :

- ❌ « Un outil pour mieux gérer les factures. »
- ✅ « Relancer par email, sans intervention humaine, les clients dont une
  facture est échue et impayée, trois fois au plus, puis remettre le dossier à
  l'associée chargée de la facturation. »

Tant que la phrase n'est pas validée, la phase 3 n'a pas commencé.

## Phase 3 — Challenger

Le cadrage est validé ; on cherche maintenant à le **casser**. Mène ces
attaques dans l'ordre, et soumets tes propres propositions de la phase 2 aux
mêmes attaques : une idée de l'agent n'a aucun privilège.

1. **Problème, ou solution déjà choisie ?** Revérifie après la fermeture.
2. **Le problème existe-t-il au-delà de celui qui le demande ?** Combien de
   personnes, lesquelles, depuis quand.
3. **Quel est le contournement actuel, et pourquoi est-il insuffisant ?** Quelqu'un
   qui subit vraiment un problème a toujours bricolé quelque chose.
4. **Falsification** : qu'est-ce qui, s'il était vrai, ferait conclure que ça
   ne vaut pas le coup ? La réponse va au §2 « Ce qui nous ferait renoncer ».
5. **Pourquoi maintenant ?** Si rien n'a changé, pourquoi pas dans six mois.
6. **Ça n'existe pas déjà ?** Une fonction d'un outil déjà payé, un service à
   20 € par mois, un modèle prêt à l'emploi. Construire ce qui s'achète est la
   dépense la plus fréquente et la plus évitable.
7. **Le coût de l'inaction se chiffre-t-il ?** Sinon le gain annoncé est une
   intuition, et la spec le dit en toutes lettres.
8. **Les contraintes tiennent-elles ensemble ?** Budget × échéance × périmètre ;
   légal (données personnelles, secteur réglementé) ; et qui maintiendra, avec
   quelles compétences.

Les questions qui en sortent suivent le protocole de `SKILL.md`. **Deux lots,
trois au maximum** : si le problème n'est toujours pas établi après trois lots,
ce n'est pas une question de plus qu'il faut, c'est un verdict.

### Le verdict : solidité du besoin

| Solidité | Critère | Effet |
| --- | --- | --- |
| **établi** | au moins une preuve `[observé]` venue d'ailleurs que du demandeur, un coût en ordre de grandeur, un périmètre borné | — |
| **déclaré** | rapporté par le demandeur ou les utilisateurs, non recoupé | — |
| **hypothétique** | conviction, rien d'observé | bandeau ⚠️ en tête de spec, preuves à réunir au §11 |

Le verdict n'interdit pas de spécifier : il interdit de le faire sans l'avoir
vu. L'utilisateur peut passer outre — c'est sa décision, consignée au journal ;
le verdict, lui, ne change pas pour faire disparaître le bandeau.

## En profondeur express

Phase 1 complète, puis une ouverture réduite à cinq lignes (les trois altitudes
et les options de réponse, « ne rien faire » compris), la phrase de cadrage
validée, et seulement les attaques 1, 3 et 6.
