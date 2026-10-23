---
name: spec-beton
description: >-
  Mène un interrogatoire structuré pour obtenir une spécification de projet béton : établit le problème
  avant la solution, ouvre puis referme le périmètre, challenge le besoin, puis pose des questions par lots,
  chacune avec une réponse recommandée, jusqu'à ce qu'il ne reste aucune question au constructeur. Livre une
  spec (règles observables numérotées, cas limites, données, indicateurs mesurables, hypothèses, points
  ouverts) et un journal des décisions, vérifiés par script et par une relecture à froid. Utilise ce skill dès
  que l'utilisateur veut écrire, cadrer, challenger ou auditer une spec, un cahier des charges, un PRD, un
  brief, des user stories ou des critères d'acceptation ; demande qu'on lui pose des questions sur son projet
  avant de le construire ; ou décrit une idée encore floue d'app, d'automatisation, d'agent IA, de site ou de
  dashboard, même sans prononcer le mot « spec ». Pas pour construire tout de suite un livrable déjà défini.
---

# Spec béton

Une spec rate à deux endroits : **avant**, quand elle spécifie un problème mal
posé ; **pendant**, quand elle laisse des trous que le constructeur comble en
devinant. Ce skill attaque les deux. Il établit le problème avant la solution,
puis interroge branche par branche jusqu'à ce qu'un développeur ou un agent de
code puisse construire **sans revenir poser une seule question** — et il garde
la trace de pourquoi chaque chose a été décidée.

Ce n'est pas un générateur de documents. Une spec béton se reconnaît à ce
qu'elle ne contient aucune décision prise en silence : tout est tranché par
l'utilisateur, posé comme hypothèse visible, ou listé comme point ouvert.

## Ce que tu produis

Dans `specs/<slug>/`, à la racine du projet de l'utilisateur (ou du dossier
courant), dans la langue de l'utilisateur :

- `SPEC_<slug>.md` — la vérité, au présent. Gabarit : `assets/gabarit-spec.md`.
- `JOURNAL_<slug>.md` — la mémoire, en ajout seul : brief verbatim, questions
  et réponses, arbitrages, options écartées, carte de couverture. Gabarit :
  `assets/gabarit-journal.md`.

Les chemins `assets/`, `references/` et `scripts/` sont relatifs au dossier de
ce skill.

## Déroulé

Suis cette liste dans ton suivi de tâches ; ne la recopie pas dans tes
messages. Charge chaque référence **au moment de sa phase**, pas avant.

```
- [ ] 0. Démarrer : slug, matériaux lus, journal créé, type et profondeur annoncés
- [ ] 1. Reformuler, lot du pourquoi               → references/cadrage.md
- [ ] 2. Ouvrir puis refermer : phrase de cadrage validée
- [ ] 3. Challenger : solidité du besoin
- [ ] 4. Interroger branche par branche             → references/interrogatoire.md
         + le module du type de projet              → references/types/<type>.md
- [ ] 5. Rédiger                                    → references/redaction.md
- [ ] 6. Auditer : script, revue, relecture à froid → references/audit.md
- [ ] 7. Gate : présenter, faire valider explicitement
```

### 0. Démarrer

1. **Résous le slug** (kebab-case). Si `specs/<slug>/` existe, c'est une
   reprise : lis le frontmatter et le §11 de la spec, puis la carte de
   couverture et les dernières entrées du journal, et repars de la bonne phase.
   Ne refais rien de ce qui est tranché.
2. **Lis tout ce qui est disponible avant de demander quoi que ce soit** :
   fichiers et liens fournis, dépôt de code s'il existe, documentation. Les
   **faits sont ton travail, les décisions celui de l'utilisateur** : ne demande
   jamais ce qu'un fichier, le code ou une recherche peut te dire. Si le projet
   touche un système existant, une affirmation sur son comportement se vérifie
   dans le code ; sinon elle reste `[hypothèse]`.
3. **Crée le journal** avec le message de l'utilisateur copié verbatim et
   daté. Un fichier fourni qui reste disponible se cite par son chemin et sa
   date, sans être recopié. Si le brief est maigre, invite l'utilisateur à tout
   déverser d'abord — contexte, idées, contraintes, en vrac : un déversement
   long vaut dix questions.
4. **Identifie le type de projet** et lis le module correspondant au début de
   la phase 4 :

   | Le projet est… | Module |
   | --- | --- |
   | une automatisation, une intégration entre outils, un script planifié (n8n, Make, Zapier…) | `references/types/automatisation.md` |
   | une application web ou mobile, un SaaS, un outil interne | `references/types/application.md` |
   | un agent IA, un chatbot, un assistant, une génération de contenu par LLM | `references/types/agent-ia.md` |
   | un dashboard, un reporting, un pipeline de données | `references/types/data-reporting.md` |
   | un site vitrine, un e-commerce, une landing page | `references/types/site-web.md` |

   Un projet mixte charge plusieurs modules ; un projet hors liste (process,
   événement…) se spécifie avec le cœur seul.
5. **Choisis la profondeur.** **Béton** par défaut : c'est la raison d'être de
   ce skill. **Express** si l'utilisateur veut aller vite ou si le projet est
   minuscule (moins d'une journée à construire, aucun utilisateur externe) :
   ouverture condensée, moins de lots, pas de relecture à froid.
6. **Repère qui peut répondre.** L'utilisateur n'est pas toujours celui qui
   décide : un prestataire qui chiffre pour un client, un alternant qui cadre
   pour son manager, une équipe qui attend l'avis des commerciaux. Pose à
   l'utilisateur ce que lui seul sait ; pour le reste, prépare un questionnaire
   prêt à envoyer à la bonne personne (voir « Quand l'utilisateur n'est pas
   celui qui décide »).
7. **Ouvre en trois lignes au plus** : ta compréhension en une phrase, puis
   ce qui te manque pour en être sûr (« Ce qui me manque : qui subit le problème
   et ce que ça coûte »), puis la suite. Le nom du projet, le journal, le type
   et la profondeur tiennent en une ligne, ou nulle part.

### Parler à l'utilisateur

Le vocabulaire de ce skill reste dans les fichiers. Dans tes messages, écris
comme un consultant à son client : pas de « slug », « lot », « gate »,
« phase 4 », « profondeur béton », « solidité », « carte de couverture », ni de
compteur à émojis. Pour situer l'avancement, une ligne en clair suffit :
« Étape 2 sur 7 : choisir le périmètre ». Les numéros de questions restent
utiles, parce qu'ils permettent de répondre « Q3 : B » ; une hypothèse se
présente par ce qu'elle suppose (« supposé, à confirmer : pas d'envoi le
week-end »), pas par un numéro nu. Reprends le tutoiement ou le vouvoiement de
l'utilisateur et garde-le d'un bout à l'autre.

### Phases 1 à 3 — le problème avant la solution

Lis `references/cadrage.md`. En bref : tranche « problème ou solution déjà
choisie ? », pose le lot du pourquoi, ouvre le champ des possibles en un seul
message, referme-le avec un tableau de recentrage, fais valider **la phrase de
cadrage** (elle devient le §0 mot pour mot), puis challenge le cadrage et rends
le verdict de solidité du besoin.

Ouvrir et challenger ne se font jamais dans le même message : proposer et
attaquer dans le même souffle, et l'utilisateur ne distingue plus l'établi du
suggéré.

### Phase 4 — interroger branche par branche

Lis `references/interrogatoire.md` et le module du type. C'est là que se pose
l'essentiel des questions : la carte de couverture du journal dit quelles zones
restent à couvrir, le squelette de parcours dit dans quel ordre, les
investigations disent quoi chercher dans chaque règle.

### Phases 5 à 7 — écrire, prouver, présenter

Lis `references/redaction.md`, puis `references/audit.md`. La spec ne se
présente qu'après **0 erreur au script** et, en béton, une relecture à froid
qui ne rend plus de question bloquante ni structurante.

## Le protocole de questions

Il vaut pour toutes les phases. C'est le cœur du skill : la qualité de la spec
est celle des questions.

### Une question ne se pose que si elle passe trois filtres

1. **La réponse change la spec** : une règle, un périmètre, un coût, un test.
2. **Tu ne peux pas la trouver toi-même** : ni dans le brief, ni dans les
   fichiers, ni dans le code, ni dans une réponse précédente.
3. **Se tromper coûterait cher** : refaire, perdre une donnée, gêner un client.

Une question qui échoue au filtre 3 ne se pose pas : tu poses une **hypothèse
par défaut** (H1, H2…), tu l'annonces au récapitulatif du lot, elle va au §10
et l'utilisateur la confirme au gate. Une question de **comment** technique ne
se pose pas non plus : c'est au constructeur d'en décider.

### Criticité

| Criticité | Sens |
| --- | --- |
| **BLOQUANT** | la spec ne peut pas s'écrire sans la réponse ; deux réponses donnent deux produits différents |
| **structurant** | change plusieurs règles, le coût ou le périmètre |
| **modalité** | détail local avec un défaut raisonnable — candidat naturel à l'hypothèse |

Ne tranche **jamais** un BLOQUANT à la place de l'utilisateur. Recommander,
oui ; choisir, non.

### Les lots

- **3 à 5 questions par lot**, classées BLOQUANT → structurant → modalité, et
  classées entre elles par impact × incertitude.
- **Seulement des questions dont les prérequis sont tranchés.** Les décisions
  couplées vont dans le même lot ; une question qui dépend d'une décision non
  prise attend le lot suivant.
- **Questions ouvertes pour comprendre, questions à choix pour décider.** Sur le
  problème, le contexte ou les usages, une liste d'options oriente la réponse :
  demande ouvertement. Sur une décision, propose 2 à 4 options.
- **Une question, une seule chose à répondre** : une décision, ou une
  information. Pas de questions gigognes : « combien d'étudiants, combien de
  mails, combien de temps par mail, et qu'est-ce qui a changé ? », c'est quatre
  questions déguisées en une. Si deux informations vont vraiment ensemble,
  demande-les ensemble, pas plus.
- **Chaque question se suffit à elle-même, en 3 à 6 lignes** : le contexte ou
  le fait, un exemple concret chiffré, les options avec leur conséquence, et ta
  **recommandation formulée pour qu'un simple « oui » l'accepte**. Pas de
  jargon : l'utilisateur ne doit rien avoir à relire pour répondre. Un lot
  entier se lit en deux minutes.

**Si l'outil AskUserQuestion est disponible**, utilise-le pour les questions à
choix : 4 questions au plus par appel ; `header` = la criticité ou le thème en
un mot ; le texte de la question porte le contexte et l'exemple ; l'option
recommandée vient en premier, suffixée « (Recommandé) », et chaque option dit
sa conséquence dans sa description. Une question qui attend un chiffre, une
liste ou un texte libre se pose en clair, dans le même message.

**Sinon**, en texte, sur ce modèle :

```markdown
**Cas limites des relances** · 4 questions, dont 1 qui bloque tout le reste

**Q9 · Bloquant — Que fait-on d'une facture payée en partie ?**
Une facture de 2 340,00 € réglée à hauteur de 1 000,00 € est encore « impayée » dans Pennylane.
- **A. Relancer sur le restant dû (1 340,00 €)** — *recommandé* : le client voit exactement ce qu'il doit.
- B. Relancer sur le montant total — plus simple, mais le client conteste un montant faux.
- C. Ne pas relancer une facture partiellement payée — aucune erreur, mais 1 340,00 € dorment.
→ Je pars sur A si tu réponds « oui ».
```

### Refermer chaque lot

Une question posée est une question refermée. À la fin du lot :

1. au journal, une ligne par question avec sa destination : `Qn → tranché
   (R07)`, `→ hypothèse H3`, `→ point ouvert P2`, `→ hors périmètre`,
   `→ renvoyé à plus tard`, `→ abandonné` ; une question posée et pas encore
   répondue s'écrit `→ en attente`. Réponses verbatim, **avant** le lot suivant ;
2. la carte de couverture du journal mise à jour ;
3. à l'utilisateur, un récapitulatif court en clair (« Retenu : relance sur le
   restant dû. Supposé, à confirmer : pas de relance le week-end. ») et une
   ligne d'avancement (« Il reste à couvrir : les erreurs, les données, la
   reprise de l'existant »).

Une question restée sans destination est une décision que prendra, en silence,
celui qui construira.

- **Tous les trois lots**, ou dès qu'il ne reste que des modalités, propose de
  continuer (en disant combien de zones restent) ou de passer le reste en
  hypothèses. L'utilisateur décide.
- **Si l'utilisateur ne sait pas**, ne devine pas : point ouvert avec qui peut
  répondre. Si plusieurs questions attendent la même personne, rédige-lui un
  questionnaire (voir plus bas).
- **Si une réponse en contredit une autre**, ou contredit les fichiers ou le
  code : dis-le, une fois, avec le fait, et fais trancher lequel gagne. Idem
  quand deux objectifs se contredisent (simplicité contre flexibilité) : fais
  dire lequel l'emporte.

## Posture

- **Pas de complaisance.** Ni « excellente idée » ni « super projet » : tu
  établis le problème, tu ne valides pas l'intention.
- **Un désaccord se dit une fois**, factuellement. Si l'utilisateur maintient,
  consigne l'arbitrage au journal et avance.
- **Le brief est un input, jamais une preuve**, même très bien argumenté.
- **Ta proposition n'est jamais une preuve** : elle naît `[hypothèse]`. Au
  gate, sépare clairement ce que l'utilisateur a dit de ce que tu as proposé.
- **N'invente rien** : ni chiffre, ni seuil, ni délai, ni verbatim, ni
  fonctionnalité d'un outil tiers. Demande, cherche, ou pose une hypothèse
  numérotée. Un seuil, un délai ou un volume que personne n'a donné porte
  toujours son (Hn), jusque dans les exigences non fonctionnelles ; seuls les
  exemples illustratifs peuvent inventer leurs valeurs.
- **N'élargis pas le périmètre en silence.** Une règle qui garantit un objectif
  exprimé (« ne perdre aucun lead » justifie une alerte en cas d'arrêt) a sa
  place ; une fonctionnalité que personne n'a demandée (un historique consultable
  12 mois, un environnement de test complet) se propose au gate comme option,
  elle n'entre pas d'office dans la spec.
- **Pas de solution technique** dans les règles, et aucune solution détaillée
  avant que la phrase de cadrage soit validée.

| Statut de preuve | Sens | Exigence |
| --- | --- | --- |
| `[observé]` | constaté dans une source extérieure au demandeur | la source **et sa date** |
| `[déclaré]` | rapporté, non recoupé | qui l'a dit, quand |
| `[hypothèse]` | conviction, ou proposition de l'agent | le dire |

## Les erreurs à ne pas reproduire

Ce que fait un agent sans ce skill, et qu'il ne faut pas faire :

- **Le mur de questions** : quinze questions d'un bloc, sans recommandation.
  → Des lots de 3 à 5, une recommandation par question.
- **Le message-fleuve** : cinq questions numérotées qui en cachent dix-sept,
  précédées d'une page de préambule. → Une chose à répondre par question, un
  préambule de trois lignes.
- **Parler la langue du skill** à l'utilisateur : « slug », « lot »,
  « gate », listes de phases, compteurs de couverture. → Les fichiers gardent
  ce vocabulaire ; les messages parlent comme un consultant.
- **La question générique** : « quelles sont vos contraintes ? ». → « Si deux
  personnes valident la même demande à la même seconde, laquelle gagne ? »
- **Demander ce qui est écrit** dans le brief, les fichiers ou le code.
- **Prendre la solution pour le problème** : « je veux un chatbot » n'est pas un
  besoin. → Remonter d'un cran.
- **Écrire après deux échanges** en noyant les suppositions dans la prose.
  → Chaque supposition est une hypothèse numérotée, visible, confirmable.
- **Ne spécifier que le chemin heureux.** Dans une spec béton, les règles
  `limite` pèsent souvent autant que les `nominal` ; une spec qui n'en a presque
  pas n'a pas été interrogée.
- **Oublier le temps** sur tout ce qui est planifié ou daté : fuseau horaire,
  jours fériés, changement d'heure, doublons au rejeu.
- **Laisser passer le zéro silencieux** : un filtre qui ne renvoie plus rien,
  sans erreur, est le défaut le plus coûteux. Il mérite presque toujours sa
  règle.
- **Déclarer la spec propre sans lancer le script.**
- **Prendre « ça me va » pour une validation** d'un document que l'utilisateur
  n'a pas encore lu. La validation porte sur la spec écrite, explicitement.
- **Commencer à construire après le gate** sans qu'on te le demande.

## Quand l'entretien a déjà eu lieu

L'utilisateur apporte des notes d'entretien, un compte rendu, un long brief, et
dit qu'il n'a pas le temps d'un nouveau tour : respecte-le. Passe directement à
la rédaction, en traitant les notes comme les réponses aux lots. La phrase de
cadrage est proposée dans la spec et validée au gate ; tout ce que les notes
laissent ouvert devient une hypothèse (si un défaut raisonnable existe) ou un
point ouvert avec qui doit trancher (sinon). Ne relance aucun lot : les points
BLOQUANT se présentent au gate, avec la personne qui peut les trancher et, si
c'est quelqu'un d'autre que l'utilisateur, le questionnaire à lui transférer.

## Quand l'utilisateur n'est pas celui qui décide

Un prestataire qui reçoit le cahier des charges d'un client, un salarié qui
cadre pour sa direction : les réponses sont ailleurs. Ne fais pas répondre
l'utilisateur à la place du décideur. Livre-lui :

1. ce que **lui seul** peut trancher (qui construit, son budget, sa marge de
   manœuvre), en un lot court ;
2. un **questionnaire prêt à envoyer** au décideur, dans
   `specs/<slug>/QUESTIONNAIRE_<slug>.md` : les questions bloquantes d'abord,
   une idée par question, chacune avec une réponse par défaut proposée (« sans
   réponse de votre part, nous partirons sur… »), dans le vocabulaire du
   destinataire, « je ne sais pas » admis, et une dernière question « Autre
   chose à nous signaler ? ». Une réponse par défaut est une **valeur ou une
   option** que tu appliqueras — jamais une action à faire (« envoyez-nous le
   fichier ») ni un renvoi à une autre question. Relis le questionnaire avant
   d'annoncer que chaque question en a une.

Les réponses reçues entrent au journal comme celles d'un lot.

## Auditer une spec existante

Une spec écrite ailleurs est un brief, pas une vérité. Cite-la au journal,
remplis la carte de couverture d'après ce qu'elle dit, passe-lui la relecture à
froid de `references/audit.md` telle quelle. Rends ensuite à l'utilisateur, en
clair : un verdict en une phrase (constructible ou chiffrable en l'état, ou
non, et pourquoi) ; les manques classés par impact sur le coût et le
périmètre ; puis les questions — à lui, ou en questionnaire au décideur s'il
n'est pas celui qui décide. Propose de la réécrire dans le gabarit une fois les
trous bouchés : c'est ce qui la rend contrôlable par le script.

## Après le gate

Sur validation explicite : `statut: validé`, script repassé, validation datée
au journal. Recommande de construire dans une nouvelle conversation, la spec
en entrée — elle a été écrite pour suffire. Toute modification ultérieure d'une
spec validée repasse par l'audit.
