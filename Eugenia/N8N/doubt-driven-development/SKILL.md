---
name: doubt-driven-development
description: >-
  Fait douter Claude de ce qu'il a compris, de ce qu'il décide et des choix déjà en place, avant qu'ils ne
  coûtent : vérifie sa compréhension avant une tâche, prouve par l'exécution plutôt que d'affirmer, fait relire
  les décisions sensibles par un relecteur à froid chargé de les réfuter, et présente chaque erreur avec son
  scénario et sa correction avant d'y toucher. Vaut pour le code, les automatisations (n8n…), les specs et
  les plans, les chiffres et les analyses. Utilise ce skill avant une tâche non triviale, dès qu'une décision
  touche une logique de calcul ou de branchement, une frontière entre systèmes, un effet irréversible, l'argent,
  la sécurité ou des données personnelles, avant d'annoncer qu'un travail non trivial est terminé, et quand
  l'utilisateur demande « t'es sûr ? », « vérifie », « challenge ça », « avocat du diable », « relis à froid ».
  Complète spec-beton, dont la spec sert de contrat, mais fonctionne seul. Pas pour le travail mécanique ni
  la relecture d'un diff terminé (/code-review).
---

# Doubt-driven development

Une longue session fabrique des certitudes : une supposition faite au troisième
message devient un fait au trentième, parce que personne ne l'a revérifiée. Et
l'auteur d'un travail est le plus mal placé pour en douter : il relit son
raisonnement au lieu de relire ce qu'il a produit.

Ce skill organise le doute, sous une contrainte : **ne jamais coûter plus de
temps qu'un test à la main suivi d'un retour**. D'où deux niveaux — un doute
léger, par l'exécution, en deux minutes ; un doute approfondi, avec un
relecteur à froid, réservé à ce qu'un test à la main découvrirait trop tard —
et une règle de posture : **un doute vient toujours avec une issue**. Une
critique sans scénario ni correction ne sert à rien ; elle ne se rapporte pas.

## Quand douter

| Moment | Ce que tu fais |
| --- | --- |
| Avant une tâche non triviale, sans spec | trois lignes « compris / supposé » (étape 0) |
| Une décision à risque est prise | doute léger ; approfondi si elle touche l'irréversible, l'argent ou la sécurité |
| Une tâche s'appuie sur un choix déjà fait | douter de ce choix seulement si un fait constaté le contredit |
| Avant d'annoncer « fini » sur un travail non trivial | chaque exigence a sa preuve (étape 6) |
| L'utilisateur le demande | doute léger ; approfondi s'il demande une relecture (« relis à froid », « avocat du diable », « challenge ») |

Une **décision**, c'est un choix entre plusieurs façons de faire ; plusieurs
lignes qui servent le même choix forment une seule décision. Elle est **à
risque** quand elle touche une logique de calcul ou de branchement, une
frontière entre systèmes, une propriété que rien ne vérifie seul (rejeu, ordre,
concurrence, fuseau, sécurité), un effet irréversible, l'argent ou des données
personnelles ; ou quand tu affirmes un fait non évident, ou que tu travailles
dans un outil que tu connais mal.

**Jamais de toi-même sur le mécanique** : renommer, mettre en forme, déplacer,
lire ou expliquer, changer une ligne à l'effet évident, suivre une instruction
claire sans décision à prendre. À la demande explicite de l'utilisateur, tout
ce qu'il désigne se met en doute.

**Si l'utilisateur demande d'aller vite**, saute les doutes, légers comme
approfondis. Restent : les trois lignes de l'étape 0 (sans t'arrêter, sauf
avant un effet irréversible), l'annonce en une ligne de tout effet
irréversible avant qu'il ait lieu, et, dans le compte rendu, ce qui n'a pas
été vérifié.

**Sur un projet déjà construit**, les parties existantes ne se mettent en
doute que sur demande, ou quand une nouvelle tâche s'appuie sur elles ; les
nouvelles décisions suivent les règles ci-dessus.

**Un diff de code terminé** se relit avec la commande `/code-review` : propose-la
au lieu de refaire une relecture générale. Un doute approfondi reste possible
sur une décision précise de ce code (« ce contrôle d'accès couvre toutes les
routes »), avec l'artefact et le contrat de cette décision seulement.

## La règle de sécurité

**Un doute ne déclenche jamais d'effet réel** : aucun envoi à de vrais
destinataires, aucune écriture en production, aucun paiement. Il s'exécute sur
des données d'essai ou en lecture seule. Sans environnement d'essai, la preuve
reste `[supposé]` et tu proposes comment en obtenir un.

## Le déroulé

Suis ces étapes dans ton suivi de tâches ; ne les recopie pas dans tes
messages.

### 0. Vérifier ce que tu as compris

Avant une tâche non triviale **sans spec**, écris en trois lignes au plus ce
que tu as compris et ce que tu supposes, puis avance. Tu ne t'arrêtes pour
demander que si une supposition touche **un effet irréversible, l'argent, la
sécurité ou des données personnelles**.

> Compris : relancer par email les factures échues depuis plus de 3 jours.
> Supposé : pas d'envoi le week-end ; le montant affiché est le restant dû.

Ici, le montant touche l'argent et part chez des clients : pose la question
avant de construire. Le week-end, non : annonce-le et avance.

**Avec une spec spec-beton**, cette étape saute : la spec tient lieu de
compréhension (voir « Avec spec-beton »).

### 1. Affirmer

Écris la décision en deux ou trois lignes, avec ce qui se passe si elle est
fausse. Si elle ne s'écrit pas aussi court, c'est une impression : précise-la
d'abord.

- ❌ « Le workflow est robuste. »
- ✅ « Une demande reçue deux fois ne crée qu'un seul lead : le dédoublonnage
  porte sur l'identifiant de réponse. Si c'est faux, deux commerciaux
  appellent le même prospect. »

### 2. Le doute léger : prouver

Par défaut, et en **deux minutes au plus, de l'affirmation au verdict**,
écriture de la preuve comprise. Une exécution vaut mieux qu'un avis : lance les
tests, exécute sur un échantillon, rejoue l'événement deux fois, recalcule à la
main. La méthode dépend de ce que tu relis — lis le module **à cette étape** :

| Tu doutes… | Module |
| --- | --- |
| d'un code (fonction, diff, script, appel à un service) | `references/cibles/code.md` |
| d'un workflow n8n, Make, Zapier, d'une intégration entre outils | `references/cibles/automatisation.md` |
| d'une spec, d'un plan, d'un document de décision | `references/cibles/spec.md` |
| d'un chiffre, d'un indicateur, d'une analyse, d'une requête | `references/cibles/donnees.md` |

Chaque preuve porte un statut :

| Statut | Sens | Exigence |
| --- | --- | --- |
| `[prouvé]` | exécuté | la commande et sa sortie |
| `[lu]` | constaté dans la source, pas exécuté | `fichier:ligne`, ou la page de doc et sa date |
| `[supposé]` | raisonné, rien de constaté | le dire |

- « J'ai vérifié » sans commande ni référence vaut `[supposé]`.
- Des tests qui passent ne prouvent que ce qu'ils affirment : compare leurs
  valeurs attendues au contrat. Un test peut graver une erreur.
- Un test écrit pour un doute reste **hors du projet** (dossier temporaire) ;
  son ajout au projet se propose avec la correction, ou dans le compte rendu.
- Une preuve dont tu estimes qu'elle prendra plus de deux minutes ne se lance
  pas d'office : propose-la, et la preuve reste `[supposé]` en attendant.

### 3. Le doute approfondi : un relecteur à froid

Seulement pour une décision qui touche **un effet irréversible, l'argent ou la
sécurité**, ou à la demande — là où un test à la main arriverait trop tard.

**Extrais**, dans des fichiers d'un dossier temporaire :

- **l'artefact** : la plus petite unité relisable (la fonction, la portion du
  workflow, la section de spec, le calcul). Trop gros : découpe.
- **le contrat** : ce que l'artefact doit garantir. Sans spec : la demande de
  l'utilisateur, ce qui a été compris et supposé, les contraintes, réécrits en
  dix lignes au plus. Avec une spec : les règles concernées, copiées telles
  quelles. Pour une spec ou un plan : « un constructeur doit pouvoir agir sans
  poser de question », plus les décisions prises par l'utilisateur.

Sans spec, **si le contrat ne s'écrit pas en dix lignes, ne lance aucun
relecteur** : demande le contrat à l'utilisateur, ou propose de le cadrer avec
spec-beton.

**Ne transmets jamais ton affirmation ni ton raisonnement** : un relecteur à qui
l'on donne la conclusion cherche à l'approuver. L'affirmation te sert seulement
à choisir quoi extraire.

**Lance un sous-agent neuf** (outil Agent ou Task) avec ce prompt :

> Tu relis un travail que tu n'as pas fait. Ton seul objectif : trouver ce qui
> est faux. Pars du principe que l'auteur a été trop confiant.
>
> Artefact : `<chemin>`. Contrat : `<chemin>`. Tu peux lire, sans les modifier,
> les fichiers du projet auxquels l'artefact fait appel. Rien d'autre.
>
> Cherche dans les deux sens : ce que le contrat exige et que l'artefact ne
> garantit pas ; ce que l'artefact fait sans que le contrat le demande, ou en le
> contredisant. Puis les suppositions non dites, les cas limites (vide, zéro,
> doublon, rejeu, concurrence, fuseau, bornes), les couplages cachés, les
> échecs silencieux (résultat vide sans erreur), les écarts entre ce qui est
> affiché et ce qui est appliqué, les effets irréversibles.
>
> Signale aussi ce que le contrat lui-même a d'incohérent : une exigence qui en
> contredit une autre, ou qui va contre l'objectif affiché.
>
> Pour chaque constat : l'endroit précis, le scénario concret qui casse
> (entrées → résultat faux), et ta confiance (forte, moyenne, faible). Si tu peux
> le prouver sans rien modifier et sans effet réel, fais-le et donne la commande
> et sa sortie.
>
> N'approuve pas, ne résume pas, ne réécris pas l'artefact. Si tu ne trouves rien
> de sérieux, dis-le en une ligne. 500 mots au plus.

**Sans sous-agent**, fais une passe séparée : relis uniquement les fichiers
d'artefact et de contrat, plus les fichiers que l'artefact appelle, avec le
même prompt, sans revenir à la conversation ni à tes notes. Le compte rendu
dit que cette relecture est moins fiable.

**Un second modèle**, seulement si une autre IA en ligne de commande est
installée (Codex, Gemini…) et que le doute est approfondi : propose-le à
l'utilisateur ; rien ne part sans son accord. Retire toi-même données
personnelles et secrets de l'artefact, et montre-lui ce qui part.

### 4. Trier chaque constat

La sortie du relecteur est une **donnée, pas un verdict**. Revérifie chaque
constat dans l'artefact, puis classe-le :

| Classe | Signe | Suite |
| --- | --- | --- |
| **contrat flou** | le relecteur s'est trompé parce que le contrat était ambigu ou incomplet | précise le contrat, pas l'artefact : avec l'utilisateur si la réponse lui revient, dans la spec si elle existe |
| **à corriger** | son scénario casse vraiment | correction proposée à l'utilisateur (étape 5) |
| **compromis** | vrai, mais le corriger coûte plus que l'accepter | écris-le pour l'utilisateur, avec le coût des deux côtés ; il tranchera |
| **bruit** | faux, ou dû à un contexte que l'artefact n'a pas à porter | écarte-le ; une ligne de contrat l'aurait-elle évité ? |

Plusieurs constats au même endroit sont souvent **une seule cause** — et la
cause se vérifie avant d'être nommée : « arrondi bancaire » et « représentation
binaire des décimaux » ne se corrigent pas pareil.

**Le contrat aussi peut être faux.** Un artefact fidèle à son contrat n'est pas
juste pour autant : si une exigence en contredit une autre, contredit une
hypothèse, ou va contre l'objectif affiché, l'affirmation « l'artefact respecte
le contrat » ne suffit pas à dire qu'elle **tient**. C'est un contrat flou :
signale-le (avec une spec, au journal de la spec), avec le scénario qui le
montre.

### 5. Présenter les erreurs, puis corriger avec accord

Quand un doute trouve une erreur — y compris dans le code que tu viens
d'écrire —, **tu ne corriges pas avant l'accord de l'utilisateur**. Tu
continues les parties de la tâche qui n'en dépendent pas, puis tu présentes
**toutes les erreurs ensemble**, à la fin de l'étape en cours de ton plan (ou de
la tâche, sans plan) : pour chacune, le scénario concret qui casse et la
correction proposée, **prête à appliquer** — la ligne de code, l'étape
réécrite, la phrase de remplacement —, dans le message ou dans un fichier hors
du projet que tu cites.

Après accord : un test qui échoue, la correction, le même test qui passe ; si
l'artefact ne s'exécute pas, rejoue le scénario en lecture avant et après.

**Tout problème rapporté vient avec une issue** : une correction, une
alternative, ou ce qui permettrait de trancher. Un constat sans issue ne se
rapporte pas.

### 6. Arrêter, et ne rien dire « fini » sans preuve

- Le doute approfondi s'arrête quand un tour ne rend plus que du bruit ou des
  compromis, et **au plus tard au troisième tour**. Un nouveau tour ne part
  qu'après l'accord sur les corrections du précédent. Si le troisième trouve
  encore à corriger, dis-le et propose de découper ou de revoir l'approche.
- Ne relance jamais un relecteur sur un artefact et un contrat tous deux
  inchangés.
- **Avant d'annoncer « fini »**, chaque exigence du contrat a une preuve
  `[prouvé]` ou `[lu]`. Une exigence sans preuve s'annonce comme non vérifiée,
  jamais comme faite.

### 7. Rendre compte

**Un seul compte rendu par tâche**, à sa fin ou à l'arrêt de l'étape 5, qui
couvre tous les doutes lancés, légers compris. **Quinze lignes au plus.** Pour
chaque affirmation, un verdict : **tient** (preuve `[prouvé]` ou `[lu]`, et
aucun constat sérieux restant), **tombe**, ou **incertain** (avec ce qui
trancherait).

```markdown
**Mis en doute** : 3 décisions ; 1 tombe, 1 incertaine, 1 tient.

- **Tombe** : une facture payée en partie était relancée sur son montant total
  (2 340,00 € au lieu de 1 340,00 €). Correction proposée : relancer sur le
  restant dû, test prêt. Je l'applique ?
- **Incertain** : le rattrapage après un jour sans exécution — ce qui
  trancherait : un essai avec un jour sauté, sur données d'essai.
- **Tient** : le dédoublonnage par identifiant de réponse — [prouvé] en rejouant
  le même événement deux fois.
- **Non vérifié** : R09 (pas d'environnement d'essai pour la panne).

Relecture : un relecteur à froid, deux tours ; le second n'a plus rien trouvé.
```

- Au-delà de cinq affirmations, détaille celles qui tombent ou restent
  incertaines et **compte** celles qui tiennent.
- Quand la place manque, garde cet ordre : ce qui tombe, ce qui reste
  incertain, ce qui n'est pas vérifié, ce qui a changé, le reste. Le surplus va
  dans le registre ou un fichier, et le compte rendu y renvoie.
- Vocabulaire technique admis, ainsi que les verdicts et les statuts de
  preuve ; pas les numéros de tour, les noms de classes ni les identifiants du
  registre.
- **Un `[prouvé]` du compte rendu se rejoue** : sa commande est dans le
  registre, ou, sans registre, une dernière ligne « Pour rejouer : `commande` »
  la donne — une seule commande qui rejoue toutes les preuves, si possible.
- Jamais « c'est solide » sans preuve.

## Douter des choix déjà en place

Un choix existant — y compris un choix de l'utilisateur, fait peut-être sans
tout l'historique du projet — **ne se remet en cause que si un fait constaté le
contredit** : le code, un volume mesuré, une documentation datée. Jamais par
préférence.

Présente alors le fait, l'alternative et son coût. **Ne modifie rien**, et
continue sur le choix existant tant que l'utilisateur n'a pas tranché.

> Le workflow interroge Pennylane toutes les 5 minutes ; l'historique montre
> 40 factures par mois [lu]. Un passage par jour suffirait et diviserait par 288
> les appels. Je garde ton réglage tant que tu n'as pas tranché.

## Avec spec-beton

Une spec s'applique quand `specs/<slug>/SPEC_<slug>.md` existe dans le projet et
que la tâche touche ses règles (avec plusieurs specs : celle dont la tâche
touche les règles). Une spec au statut « proposé » sert aussi de contrat, et le
compte rendu rappelle qu'elle n'est pas validée.

- **Le contrat, ce sont ses règles**, copiées telles quelles avec les
  hypothèses qu'elles citent. L'étape 0 saute.
- **Un trou ou une contradiction de la spec ne se comble pas dans
  l'artefact.** Applique l'hypothèse de la spec qui le couvre déjà, sinon ajoute
  à la fin de `specs/<slug>/JOURNAL_<slug>.md` une ligne
  `Qn · criticité · question → en attente` (criticité : BLOQUANT, structurant ou
  modalité) et pose la question à l'utilisateur. Quand il répond, ajoute la
  ligne `Qn · criticité · question → tranché` ; ne modifie pas `SPEC_<slug>.md`
  toi-même : propose de la mettre à jour avec spec-beton.
- **« Fini »** se prouve règle par règle, sur les règles que la tâche couvre.
- Le registre des doutes vit à côté de la spec (voir ci-dessous).

Sans spec-beton, tout fonctionne pareil : le contrat s'écrit en dix lignes.

## Le registre

Tiens un registre quand la tâche touche les règles d'une spec
(`specs/<slug>/DOUTES_<slug>.md`, un seul par spec), ou quand l'utilisateur le
demande (un par sujet, nommé d'après la tâche). Gabarit :
`assets/gabarit-registre.md`. On y **ajoute sans réécrire** : un changement
d'état s'écrit par une ligne datée sous l'entrée. Le registre garde les
preuves et les commandes, il ne recopie pas le compte rendu : une entrée tient
en une quinzaine de lignes. Contrôle-le avant chaque compte rendu :

```bash
python scripts/check_doutes.py chemin/vers/DOUTES_<sujet>.md
```

(`python3` selon la machine ; chemin relatif au dossier de ce skill.) Le script
vérifie les champs obligatoires, les classes et les verdicts, qu'un « tient »
repose sur une preuve, et signale le théâtre du doute : un tour où au moins deux
constats de confiance forte ont tous été rangés en « bruit » ou « compromis ».

## Les erreurs à ne pas reproduire

- **Demander « est-ce que c'est bon ? »** au lieu de « trouve ce qui est faux ».
- **Donner au relecteur ta conclusion** ou ton raisonnement.
- **Croire le relecteur sur parole** au lieu de revérifier chaque constat.
- **Corriger sans accord**, même une erreur dans ton propre travail du moment.
- **La critique sans issue** : « ce choix est discutable » sans scénario ni
  alternative. Elle coûte du temps et n'apporte rien.
- **Remettre en cause un choix de l'utilisateur par goût**, sans fait constaté.
- **Douter de tout** : le mécanique n'a pas besoin de doute ; le doute
  approfondi n'est pas le réglage par défaut.
- **Exécuter pour de vrai** pour prouver : un email de test parti chez un vrai
  client est un incident.
- **Annoncer « testé », « vérifié » ou `[prouvé]`** sans la commande et sa
  sortie.
- **Déclarer « tient » parce que l'artefact suit le contrat**, sans regarder si
  le contrat se contredit.
- **Nommer une cause plausible** au lieu de la cause vérifiée.
- **Faire confiance aux tests existants** sans lire ce qu'ils affirment.
- **Boucler au-delà de trois tours**, ou relancer sur un artefact inchangé.
- **Le compte rendu-fleuve** ou en jargon : l'utilisateur veut ce qui tombe, ce
  qui a changé, et ce qui reste à sa charge.

| Ce que tu te dis | Pourquoi ça ne tient pas |
| --- | --- |
| « Je suis sûr de moi. » | La confiance de l'auteur est précisément ce que l'on met en doute. |
| « Les tests passent. » | Ils testent ce que l'auteur a pensé à tester. |
| « Le relecteur n'a pas le contexte. » | C'est voulu. S'il lui manque un contexte nécessaire, c'est le contrat qui est incomplet. |
| « C'est une petite erreur, je corrige vite fait. » | L'utilisateur a demandé à valider avant toute correction. Présente-la avec les autres. |
