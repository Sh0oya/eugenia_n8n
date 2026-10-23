---
slug: {kebab-case}
titre: {Nom du projet}
date: {AAAA-MM-JJ}
statut: brouillon
solidite_besoin: {établi · déclaré · hypothétique}
profondeur: {béton · express}
lecteur: {qui construira à partir de cette spec}
---

# Spec — {Nom du projet}

> Preuves : `[observé]` constaté dans une source datée · `[déclaré]` rapporté, non recoupé · `[hypothèse]` conviction ou proposition non prouvée.

> ⚠️ **Besoin hypothétique.** Personne n'a encore observé ce problème chez un utilisateur réel : cette spec décrit une intention, pas un besoin établi. Les preuves à réunir sont au §11. Construire maintenant, c'est accepter ce risque.

---

## 0 - Cadrage

**{La phrase de cadrage validée en fin de fermeture, mot pour mot.}**

- **Lecteur** : {qui construit, et ce que la spec doit lui permettre : construire sans revenir poser de question, chiffrer, sous-traiter…}
- **Profondeur** : {béton · express} — {pourquoi ce niveau}

## 1 - Problème

### Premier cas d'usage

**En tant que** {acteur}
**Lorsque je** {situation déclenchante}
**Ce qui compte pour moi est** {besoin}
**Mais** {obstacle rencontré}
**Et donc aujourd'hui** {contournement actuel}

**Cas d'usage suivants, non traités en premier :** {une ligne}

### Preuves

| Ce qui est affirmé | Source (qui ou quoi + date) | Statut |
| --- | --- | --- |
| {fait} | {source} | {`[observé]` · `[déclaré]` · `[hypothèse]`} |

### Coût du contournement actuel

{Temps, erreurs, argent, frustration : un ordre de grandeur et son statut.}

## 2 - Objectifs & succès

### Indicateurs de succès

| # | Indicateur | Définition exacte | Valeur de départ | Cible | Garde-fou |
| --- | --- | --- | --- | --- | --- |
| I1 | {nom} | {comment on le calcule, sur quelle période} | {valeur mesurée, ou « inconnue — mesurée par R.. »} | {cible} | {ce qui ne doit pas se dégrader} |

### Ce qui nous ferait renoncer

{Le fait qui, s'il était établi, invaliderait le projet.}

### Risques

| Risque | Conséquence | Parade |
| --- | --- | --- |
| {risque} | {conséquence} | {parade} |

## 3 - Périmètre

### Dans le périmètre

{Ce que la première version fait, en une liste courte.}

### Hors périmètre

{Ce qu'elle ne fera pas, et pourquoi.}

### Renvoyé à plus tard

{Chaque élément porte sa condition de retour : « … — revient si … ».}

### Contraintes imposées

{Budget, délai, outils ou technos imposés, légal, compétences de qui maintiendra. Seulement ce qui est imposé, jamais ce qui est un choix de conception.}

### Dépendances & adjacences

{Systèmes, équipes, projets voisins dont celui-ci dépend ou qu'il touche.}

## 4 - Acteurs & vocabulaire

### Acteurs

| Acteur | Ce qu'il fait dans le projet | Volume / fréquence |
| --- | --- | --- |
| {acteur} | {rôle} | {combien, à quelle fréquence} |

### Glossaire

| Terme | Définition dans ce projet |
| --- | --- |
| {terme} | {définition} |

## 5 - Domaines transverses balayés

| Domaine | Verdict | Règles ou raison |
| --- | --- | --- |
| Acteurs, rôles & droits | {impacté · non impacté · hors-lot} | {R.. si impacté, sinon la raison en une ligne} |
| Paramétrage & activation | | |
| Données : création, modification, suppression, conservation | | |
| Données personnelles & confidentialité | | |
| Erreurs, indisponibilités & mode dégradé | | |
| Notifications & communication | | |
| Historique, traçabilité & effet sur le passé | | |
| Volume, fréquence & délais | | |
| Reprise de l'existant | | |

## 6 - Parcours & règles

### 6.1 Prérequis & activation

> **Acteur** : {qui} · **Moment** : {quand, dans le parcours}

**R01 — {Énoncé : un comportement observable}.** {Précisions, exemple chiffré si calcul.} → **NOUVEAU**.
- {détail de la règle, en puce collée au paragraphe}

#### Cas limites

**R02 — {Énoncé du cas limite}.** {Précisions.} → **NOUVEAU**.

### 6.2 Paramétrage

> **Acteur** : {qui} · **Moment** : {quand}

### 6.3 Mise à disposition

> **Acteur** : {qui} · **Moment** : {quand}

### 6.4 Parcours nominal

> **Acteur** : {qui} · **Moment** : {quand}

### 6.5 Résultat

> **Acteur** : {qui} · **Moment** : {quand}

### 6.6 Cycle de vie

> **Acteur** : {qui} · **Moment** : {quand}

### 6.7 Reprise de l'existant

> **Acteur** : {qui} · **Moment** : {quand}

## 7 - Données & états

### {Objet manipulé}

| Champ | Obligatoire | Format / bornes | Valeur par défaut | Source |
| --- | --- | --- | --- | --- |
| {champ} | {oui · non} | {format, min, max} | {défaut} | {d'où vient la valeur} |

### États de {objet}

| État | Ce qui est visible | Ce qu'on peut faire | Transitions possibles |
| --- | --- | --- | --- |
| {état} | {affichage} | {actions} | {vers quel état, par quelle action} |

## 8 - Exigences non fonctionnelles

| # | Exigence | Seuil mesurable | Comment on le vérifie |
| --- | --- | --- | --- |
| N1 | {exigence} | {seuil chiffré} | {méthode de vérification} |

## 9 - Synthèse des règles

| # | Règle | Lot | Type |
| --- | --- | --- | --- |
| R01 | {la règle en une douzaine de mots} | nominal | NOUVEAU |
| R02 | {…} | limite | NOUVEAU |

## 10 - Hypothèses posées par défaut

| # | Hypothèse | Si elle est fausse | Qui peut confirmer |
| --- | --- | --- | --- |
| H1 | {ce qu'on a supposé sans le demander} | {ce qui change dans la spec} | {qui} |

## 11 - Points ouverts

| # | Sujet | Criticité | À trancher | Qui tranche |
| --- | --- | --- | --- | --- |
| P1 | {sujet} | {BLOQUANT · structurant · modalité} | {la question, avec les options} | {qui} |
