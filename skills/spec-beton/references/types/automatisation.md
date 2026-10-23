# Module — automatisation & intégration

Workflows n8n, Make, Zapier, scripts planifiés, synchronisation entre outils.
Une automatisation agit **sans témoin** : personne ne regarde quand elle se
trompe. Les défauts qui comptent sont ceux qu'on ne voit pas.

## Questions qu'on oublie

**Déclencheur**
- Événement reçu, planifié, ou lancé à la main ? À quelle heure, dans quel fuseau ?
- Que deviennent les événements arrivés **pendant une panne** : perdus, ou
  rattrapés au redémarrage ?
- En interrogation périodique : quelle fenêtre de lecture ? Une fenêtre qui se
  chevauche crée des doublons, une fenêtre trop courte en perd.

**Rejeu et doublons**
- Lancer deux fois le même traitement donne-t-il le même résultat ? Quelle
  **clé** identifie un élément déjà traité (identifiant source, numéro de
  facture, email) ?
- Un élément modifié à la source après traitement : on le retraite, on
  l'ignore, on le met à jour ?

**Volume et limites**
- Combien d'éléments par passage, en moyenne et en pic ? Le 101ᵉ élément est-il
  traité (pagination) ?
- Les outils tiers ont-ils des quotas d'appels ? Que se passe-t-il quand on les
  atteint ?
- Ordre de traitement : les éléments peuvent-ils arriver dans le désordre (mise
  à jour reçue avant la création) ?

**Échecs**
- Combien de nouvelles tentatives, espacées de combien, puis quoi ?
- Un élément en erreur bloque-t-il les autres, ou le passage continue-t-il ?
- **Qui est prévenu**, par quel canal, avec quelle information pour agir ?
- Un passage qui traite **zéro** élément alors que d'habitude il en traite des
  dizaines : succès ou alerte ?

**Données**
- Source de vérité : quand deux outils portent la même donnée et divergent,
  lequel gagne ? Synchronisation dans un sens ou dans les deux ?
- Une suppression à la source se propage-t-elle ?
- Correspondance **champ par champ** : format des dates, des téléphones, des
  montants ; que faire d'un champ vide à la source ?
- Quelles données personnelles transitent, et restent-elles visibles dans
  l'historique d'exécution de l'outil ?

**Exploitation**
- Avec le compte de qui l'automatisation se connecte-t-elle ? Que se passe-t-il
  quand cette personne part, change son mot de passe, ou que l'accès expire ?
- Comment la tester sans écrire chez de vrais clients ? Faut-il un interrupteur
  général ?
- Qui la maintient, avec quelles compétences ? Quel coût mensuel maximal
  (exécutions, abonnements, appels d'API) ?
- Messages sortants vers des clients : qui valide les modèles, depuis quelle
  adresse, avec quel moyen de se désinscrire ?

## Pièges

- **Le zéro silencieux** : un identifiant qui change, un filtre trop strict, et
  l'automatisation « réussit » chaque jour en ne faisant rien. Prévois une règle
  d'alerte sur un volume anormal.
- **Le doublon au rejeu** : sans clé de dédoublonnage, chaque reprise après
  panne renvoie les emails, recrée les fiches, refacture.
- **Le fuseau du serveur** : « tous les jours à 9 h » sur un serveur en UTC, c'est
  8 h ou 7 h à Paris selon la saison.
- **Le compte personnel** : l'automatisation branchée sur le compte d'un salarié
  s'arrête le jour de son départ.

## Zones à ajouter à la carte de couverture

Déclencheur · rejeu et doublons · volume et quotas · échecs et alertes ·
correspondance des champs · accès et exploitation.
