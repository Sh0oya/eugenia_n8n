# Auditer, puis présenter

Phases 6 et 7. Une spec non auditée n'est jamais présentée comme prête.

## 1. Le contrôle mécanique

```bash
python scripts/check_spec.py specs/<slug>/SPEC_<slug>.md specs/<slug>/JOURNAL_<slug>.md
```

(`python3` selon la machine ; le chemin du script est relatif au dossier du
skill.) Corrige jusqu'à **0 erreur**. Chaque avertissement se traite ou
s'assume explicitement : dis lequel tu gardes, et pourquoi.

« Toutes les règles sont ancrées », « aucun placeholder », « chaque question a
sa destination » sont des **sorties du script**, jamais des phrases de l'agent.

## 2. Consolider

Avant la revue de fond, réduis la spec à ses règles réelles :

- deux règles qui disent la même chose → une disparaît, son numéro n'est pas
  réutilisé ;
- un chapeau → introduction de section ; une conséquence → puce ;
- un fait ne s'énonce qu'une fois : ailleurs, un renvoi à sa règle.

## 3. La revue fonctionnelle

Une fois, explicitement, point par point :

1. **Incohérences** entre règles, entre règles et tableau d'états, entre règles
   et exemples chiffrés.
2. **Décisions renversées** : chaque arbitrage du journal qui en annule un autre
   est propagé partout — règles, synthèse, états, exemples, hypothèses.
3. **Dérive** : relis le journal en entier. Rien de tranché n'est perdu, rien
   n'est entré dans la spec sans avoir été décidé.
4. **Terminologie** : un concept, un nom.
5. **Technique déguisée** : chaque règle passe le test « une autre implémentation
   au même comportement observable la violerait-elle ? ». Signaux : un outil,
   une table, un champ technique, un protocole nommé dans l'énoncé.
6. **Défaillance silencieuse** et **affiché ≠ appliqué** (cf.
   `interrogatoire.md`) sur toute règle de filtre, de limite ou de compteur.
7. **Cas limites** : chaque phase du §6 a les siens, ou une bonne raison de ne
   pas en avoir.
8. **Hypothèses** : chacune dit ce qui change si elle est fausse, et qui peut
   la confirmer.

## 4. La relecture à froid

C'est le test qui compte : **la spec suffit-elle à quelqu'un qui n'a pas
assisté à la conversation ?** En profondeur béton, il est obligatoire.

Si tu peux lancer un sous-agent (outil Agent ou Task), donne-lui **seulement le
chemin de la spec** — ni le journal, ni la conversation — et ce prompt :

> Tu vas construire ce projet à partir de cette seule spec : `<chemin>`. Lis-la
> en entier. Liste les questions que tu devrais poser avant de pouvoir
> construire sans rien deviner, classées BLOQUANT, structurant ou modalité,
> chacune avec la règle ou la section concernée. Liste ensuite les
> contradictions que tu vois. Ne propose aucune solution, ne réécris rien.
> Réponds en moins de 600 mots.

Sans sous-agent, fais-le toi-même, en relisant la spec comme un constructeur
qui découvre le projet : pas de souvenir de la conversation.

Traite chaque question rendue :

- la réponse est **dans le journal** → la spec n'était pas autonome : corrige-la ;
- la réponse **n'existe nulle part** et la question est BLOQUANT ou
  structurante → un lot de questions à l'utilisateur, la plus importante
  d'abord ;
- c'est une **modalité** → décide toi-même, et écris-la comme hypothèse Hn :
  ta décision reste visible et l'utilisateur la confirme au gate ;
- c'est une question **de comment** → le constructeur décidera : rien à faire.

Repasse le script, puis une nouvelle relecture. **Convergence** : une relecture
qui ne rend plus aucune question BLOQUANT ni structurante. Chaque relecture
coûte plusieurs minutes : **deux au plus** par défaut, une troisième seulement
si la deuxième a encore trouvé un BLOQUANT. Sans convergence, présente la spec
en le disant, statut maintenu à `proposé`, et propose de découper le projet.

## 5. Le gate

Présente en clair, en une quarantaine de lignes au plus — le détail est dans
la spec, le message n'a pas à la répéter :

1. la phrase de cadrage, et si le besoin est hypothétique, le dire en une phrase ;
2. le chemin de la spec et du journal ;
3. une ligne de chiffres : nombre de règles dont cas limites, hypothèses,
   points ouverts, et « contrôle automatique et relecture indépendante : OK »
   (ou ce qui ne l'est pas) ;
4. **les cinq hypothèses les plus risquées**, une ligne chacune, en séparant
   ce que l'utilisateur a dit de ce que tu as supposé ; les autres renvoient
   au §10 ;
5. les points ouverts BLOQUANT ou structurants, chacun avec la personne qui
   doit trancher et, si ce n'est pas l'utilisateur, le questionnaire prêt à
   lui transférer ;
6. les options proposées hors périmètre, s'il y en a, en une ligne chacune.

Demande la validation. Sur un oui explicite, et seulement s'il ne reste aucun
point BLOQUANT ni structurant : passe le frontmatter à `statut: validé`, repasse
le script, consigne la validation datée au journal.

**Ne commence pas à construire.** Recommande de le faire dans une nouvelle
conversation, la spec en entrée : elle a été écrite pour suffire. Toute
modification d'une spec validée repasse par l'audit.
