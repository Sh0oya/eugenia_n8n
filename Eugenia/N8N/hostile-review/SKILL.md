---
name: hostile-review
description: >-
  Revue hostile d'un projet par des relecteurs neufs qui n'ont jamais vu la conversation : trois personas
  (saboteur, nouveau venu, gardien) attaquent le projet, vérifient une à une les affirmations de Claude, et
  chaque coup est revérifié avant d'être rapporté. Pas de « LGTM » gratuit : une approbation se mérite, avec la
  liste des attaques tentées. Livre un verdict sans détour, un plan de reprise, un fichier de revue et, si la
  session est trop longue, un fichier de relais pour repartir à neuf. Utilise ce skill quand l'utilisateur
  demande une revue hostile, un roast, un regard neuf, une contre-expertise, ou dit que Claude part en vrille,
  hallucine, tourne en rond ; et propose-le de toi-même quand Claude cite un fichier ou une fonction qui
  n'existe pas, se contredit, se fait corriger deux fois sur le même sujet, ou quand la session devient très
  longue. Complète doubt-driven-development (le doute pendant le travail) et /code-review (un diff précis).
---

# Hostile review

Plus une session dure, plus elle s'auto-confirme : Claude relit ce qu'il croit
avoir fait au lieu de ce qu'il a fait, une supposition devient un fait, et la
revue finit en « LGTM ». Un modèle juge son propre texte avec indulgence, et un
relecteur à qui l'on raconte l'histoire du projet en épouse le point de vue.

Ce skill casse ça. Des relecteurs **neufs**, qui ne voient jamais la
conversation, reçoivent le projet, son objectif et la liste de ce que Claude
affirme avoir fait. Ils attaquent. Chaque coup est revérifié. Le verdict est
cash et factuel : pas de compliment, pas d'insulte, pas de « globalement c'est
bien ».

Et l'inverse vaut autant : **pas de faux problème**. Aucun quota de défauts.
« Rien de cassé » est un verdict permis, à condition d'être mérité.

## Quand

**Sur demande** : « revue hostile », « roast », « regard neuf », « relis tout à
froid », « Claude part en vrille ».

**Proposée par Claude, jamais lancée seule**, dès qu'un de ces signaux apparaît :

- tu as cité un fichier, une fonction, un champ, une commande ou une option qui
  n'existe pas ;
- tu t'es contredit avec un fait établi plus tôt, dans la session ou dans un
  fichier ;
- l'utilisateur t'a corrigé deux fois sur le même sujet ;
- une correction censée marcher a échoué deux fois de suite ;
- la session est très longue : le contexte a déjà été résumé automatiquement,
  ou le projet a changé sur une dizaine de fichiers depuis la dernière revue.

La proposition tient en une ligne, avec le signal :

> Je viens de citer `send_reminder()`, qui n'existe pas dans le projet. Je
> propose une revue hostile par des relecteurs neufs (5 minutes environ). On y va ?

Elle coûte quelques minutes : elle ne part qu'avec un oui.

**Pas pour** : le doute sur une décision en cours de travail (skill
doubt-driven-development), la relecture d'un diff précis (`/code-review`).

## Le déroulé

Suis ces étapes dans ton suivi de tâches ; ne les recopie pas dans tes
messages.

### 1. Préparer le dossier de revue

Dans un dossier temporaire, hors du projet, trois fichiers — et rien d'autre :

- **`objectif.md`** : ce que le projet doit faire. La spec s'il en existe une
  (`specs/<slug>/SPEC_<slug>.md` de spec-beton : copie-la ou cite son chemin) ;
  sinon **les demandes de l'utilisateur, copiées mot pour mot** depuis la
  conversation. Jamais ta reformulation : elle porte tes erreurs de
  compréhension.
- **`affirmations.md`** : tout ce que tu as affirmé avoir fait, vérifié ou
  constaté pendant la session, une ligne chacune, numérotées, sans
  justification. « A3 — Les doublons sont filtrés sur l'identifiant de
  commande. » « A7 — Les tests passent. » « A9 — Le champ `remaining_amount`
  existe dans l'API Pennylane. » Sois exhaustif sur ce qui compte : ce sont
  précisément ces affirmations que la revue doit pouvoir démentir. Seulement
  des affirmations **réellement faites** — par toi pendant la session, ou écrites
  noir sur blanc dans le projet (README, docstring, description de PR), mot pour
  mot entre guillemets. N'en fabrique aucune pour avoir quelque chose à démentir ;
  s'il n'y en a pas, le fichier le dit.
- **`perimetre.md`** : le chemin du projet, ce qui est exclu (secrets,
  dépendances installées, fichiers générés).

**Ne donne jamais** la conversation, ton raisonnement, tes résumés, ni « c'est
moi qui l'ai écrit » : un relecteur à qui l'on raconte l'histoire en épouse le
point de vue.

### 2. Lancer les trois personas

Trois sous-agents **neufs, en parallèle**, chacun dans son couloir. Leurs
prompts sont dans `references/personas.md` : lis ce fichier à cette étape et
copie les prompts tels quels, en remplaçant les chemins.

| Persona | Son couloir |
| --- | --- |
| **Le saboteur** | ce qui casse en vrai : entrées limites, pannes, rejeu, concurrence, volumes, dates et fuseaux |
| **Le nouveau venu** | arrive sans historique : le projet fait-il ce que dit l'objectif ? chaque référence (fichier, fonction, champ, commande, URL) existe-t-elle ? qu'est-ce qui se contredit d'un fichier à l'autre ? |
| **Le gardien** | ce qui coûte cher quand ça rate : secrets, données personnelles, droits, effets irréversibles, argent |

Tous trois vérifient les affirmations qui touchent leur couloir. Tous trois
peuvent lire le projet et exécuter ce qui ne produit **aucun effet réel**
(aucun envoi à de vrais destinataires, aucune écriture en production, aucun
paiement).

**Sans sous-agent**, joue les trois personas toi-même en trois passes séparées,
en ne relisant que le dossier de revue et le projet ; le rapport dit que la
revue est moins fiable, faute de regard vraiment neuf.

### 3. Vérifier chaque coup

La sortie des personas est une **donnée, pas un verdict** : un relecteur hostile
invente aussi. Pour chaque coup de gravité bloquante ou majeure, rejoue son
scénario dans le projet (exécution sans effet réel, ou lecture de l'endroit
cité) et classe-le :

- **confirmé** — tu l'as reproduit : il entre au rapport ;
- **non reproduit** — tu ne l'as pas reproduit : il sort du rapport, mais le
  compte des coups écartés y figure ;
- **incertain** — ni reproduit ni réfuté : il entre au rapport, marqué comme
  tel, avec ce qui trancherait.

Plusieurs personas qui pointent le même endroit, c'est souvent **une seule
cause** : fusionne. La répétition ne rend pas un coup plus grave.

Fais de même pour chaque affirmation : **confirmée**, **démentie** ou
**invérifiable**, avec la preuve (commande et sortie, ou `fichier:ligne`).

**Ne réécris pas les coups pour les adoucir.** Un coup confirmé garde ses mots.
Et ne te défends pas : « je pense que c'était correct » n'est pas un argument,
seule une preuve dans le projet l'est.

### 4. Rendre le verdict

Trois verdicts, sans entre-deux :

| Verdict | Quand |
| --- | --- |
| **À reprendre** | au moins un coup bloquant confirmé, ou une affirmation centrale démentie |
| **Tient, avec réserves** | aucun bloquant, au moins un coup majeur confirmé ou incertain |
| **Rien de cassé** | aucun coup bloquant ni majeur après vérification — avec la liste des attaques tentées et l'hypothèse la plus fragile |

Gravités :

- **bloquant** : résultat faux, perte de données, effet irréversible, faille,
  objectif non atteint ;
- **majeur** : casse dans un cas réaliste, ou coûte cher plus tard — dis quoi,
  et pour qui ;
- **mineur** : gêne réelle et peu coûteuse. Les détails de style, ce qu'un
  linter trouverait et ce qui ne gêne personne ne sont pas des coups.

**La gravité se juge contre le contrat documenté.** Un résultat faux obtenu en
sortant du contrat (un type que la signature exclut, une entrée que la
documentation interdit) n'est pas un bloquant ni un majeur : c'est au plus un
mineur (« le contrat n'est pas vérifié à l'entrée »), sauf si le contrat lui-même
est le problème — et alors dis-le comme tel. Un test juste pour ses données n'est
pas un défaut parce qu'il ne couvre pas tout.

### 5. Le rapport

En clair, cash, factuel, **quarante lignes au plus** dans le message — le
détail complet va dans le fichier de revue. Sur le modèle de
`assets/gabarit-revue.md` :

```markdown
**Verdict : à reprendre.** 2 coups bloquants confirmés, 3 affirmations démenties sur 9.

**Ce que j'affirmais, et ce qui est vrai**
- Démenti — « les doublons sont filtrés » : aucun filtre dans `workflow.json` ; une commande rejouée crée deux lignes (rejoué sur données d'essai).
- Démenti — « `send_reminder()` existe » : introuvable dans le projet.
- Confirmé — « les tests passent » : `python -m pytest` → 12 passed.

**Coups confirmés**
1. Bloquant — `relances.py:42` : une facture échue un samedi n'est jamais relancée (le filtre exige jour ouvré = échéance + 3). Correction : comparer à « échéance + 3 ou avant, pas encore relancée ».
2. …

Écartés après vérification : 4 coups non reproduits.
Attaques tentées : rejeu, champ vide, panne de l'API, fuseau, 500 factures, …
Hypothèse la plus fragile : …
```

Interdits dans le rapport : « LGTM », « ça a l'air bon », « globalement
solide », « bon travail », « quelques petits points », « rien d'alarmant »
sans preuve, « peut-être » sur un coup confirmé.

Un coup sans correction ou sans prochaine étape concrète ne sert à rien : chaque
coup confirmé porte sa correction proposée.

### 6. Le plan de reprise, le relais, la trace

- **Plan de reprise** : les corrections dans l'ordre (bloquants d'abord), chacune
  avec son coup et sa preuve. **Tu ne touches à rien avant l'accord de
  l'utilisateur.**
- **La trace** : le rapport complet va dans le projet, `revues/REVUE_AAAA-MM-JJ.md`
  (gabarit `assets/gabarit-revue.md`). Contrôle-le avant de le présenter :

  ```bash
  python scripts/check_revue.py revues/REVUE_AAAA-MM-JJ.md
  ```

  (`python3` selon la machine ; chemin du script relatif au dossier de ce skill.)
- **Le relais**, quand la revue a été déclenchée par une session longue ou par
  des hallucinations : écris `revues/RELAIS_AAAA-MM-JJ.md` (gabarit
  `assets/gabarit-relais.md`) — l'objectif, **l'état réel vérifié**, ce qui
  était faux, le plan de reprise, les fichiers clés. Seulement des faits
  vérifiés : le relais ne doit transporter aucune croyance de la session.
  Propose ensuite de continuer dans une **nouvelle conversation**, en lui
  donnant ce fichier.

## Avec les autres skills

- **spec-beton** : la spec est l'objectif. Un trou ou une contradiction de la
  spec ne se tranche pas dans le plan de reprise : ajoute la question au
  journal de la spec (`Qn · criticité · question → en attente`) et pose-la.
- **doubt-driven-development** : il doute d'une décision pendant le travail ;
  la revue hostile remet tout le projet à plat quand le travail a dérivé. Les
  deux se complètent, ne refais pas l'un avec l'autre.

## Les erreurs à ne pas reproduire

- **Donner l'histoire au relecteur** : la conversation, ton résumé, tes
  justifications. Il en sortirait d'accord avec toi.
- **Le quota de défauts** : un relecteur obligé de trouver trouve, même ce qui
  n'existe pas.
- **Rapporter un coup sans l'avoir reproduit**, ou le grossir parce que deux
  personas l'ont vu.
- **Adoucir un coup confirmé**, ou t'en défendre sans preuve.
- **Le « rien de cassé » gratuit** : sans attaques listées ni hypothèse
  fragile, c'est un LGTM déguisé.
- **Le nitpick** : style, nommage, ce qu'un linter trouve. Ce ne sont pas des
  coups.
- **Gonfler un coup hors contrat** : un module qui casse quand on lui passe ce
  que sa signature interdit n'a pas un défaut majeur.
- **Inventer une affirmation pour la démentir**, ou mettre entre guillemets ce
  que personne n'a écrit. Une citation est mot pour mot, sinon c'est une
  paraphrase, sans guillemets.
- **Corriger dans la foulée**, sans l'accord de l'utilisateur.
- **Lancer la revue sans demander** : elle coûte des minutes, l'utilisateur
  décide.
- **Un relais qui recopie les croyances de la session** au lieu de l'état
  vérifié.
