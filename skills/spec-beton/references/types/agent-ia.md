# Module — agent IA, chatbot, assistant, génération par LLM

Un modèle de langage ne se trompe pas comme un programme : il se trompe avec
assurance, et pas deux fois de la même façon. « Le bot répond aux questions des
clients » n'est pas spécifié tant qu'on ne sait pas **ce qu'est une bonne
réponse, une mauvaise, et ce qu'il fait quand il ne sait pas**.

## Questions qu'on oublie

**La tâche, exactement**
- Quelles entrées (question libre, email, document, formulaire) et quelle
  sortie (texte, format imposé, action) ?
- **Cinq exemples réels de bonne réponse et cinq de mauvaise**, fournis par
  l'utilisateur. Sans eux, le comportement attendu n'existe que dans sa tête.

**Ce qu'il sait**
- Quelles sources de connaissance, qui les tient à jour, à quelle fréquence ?
- Quand la réponse n'est pas dans les sources : il refuse, il transfère à un
  humain, ou il dit qu'il ne sait pas ? Jamais « il improvise » sans que ce soit
  un choix explicite.

**Ce qu'il ne doit jamais faire**
- Sujets interdits, promesses commerciales (prix, délais, remboursements),
  conseils réglementés, informations à ne jamais révéler.
- Les contenus fournis par des tiers (emails reçus, pages web, documents) sont
  des **données, jamais des instructions** : que fait-il quand un email contient
  « ignore tes consignes et… » ?

**Ce qu'il peut faire**
- Quelles actions réelles (écrire dans un outil, envoyer, réserver, payer) ?
- Lesquelles exigent une **validation humaine** avant d'agir ? Toute action
  irréversible devrait en poser la question.

**Le relais humain**
- Sur quels critères il transfère, vers qui, par quel canal, avec quelle
  information transmise ? Hors des heures ouvrées ?

**Forme**
- Ton, langue, longueur des réponses, persona ; tutoiement ou vouvoiement.

**Mémoire et données**
- Se souvient-il d'une conversation à l'autre ? Combien de temps les échanges
  sont-ils conservés, qui peut les lire, le savent-ils ?

**Évaluation — l'équivalent des critères d'acceptation**
- Un **jeu de test** : N questions réelles avec la réponse attendue ou les
  critères d'une bonne réponse.
- Un **seuil d'acceptation** : par exemple 90 % de réponses jugées correctes,
  et 0 erreur sur les prix.
- Qui juge, et à quelle fréquence on rejoue le jeu de test ?
- La même question peut produire deux réponses différentes : est-ce acceptable,
  et sur quels sujets ne l'est-ce pas ?

**Coût et délai**
- Budget par conversation ou par mois ; délai de réponse acceptable.

## Pièges

- **Pas de jeu de test** : impossible de dire si l'agent marche, donc
  impossible de dire quand il cesse de marcher.
- **L'hallucination plausible** : un prix, une date, une politique de
  remboursement inventés avec aplomb. Les sujets à risque ont leur règle.
- **L'action sans garde-fou** : un agent qui peut envoyer ou payer sans
  validation finira par le faire au mauvais moment.
- **L'injection** : un contenu tiers traité comme une instruction.

## Zones à ajouter à la carte de couverture

Exemples de bonnes et mauvaises réponses · sources et cas « ne sait pas » ·
interdits · actions et validations humaines · relais humain · jeu de test et
seuil d'acceptation · coût et délai.
