# Douter d'une automatisation

Workflow n8n, Make, Zapier, script planifié, synchronisation entre outils. Une
automatisation agit sans témoin : ses erreurs ne se voient pas, elles se
découvrent. Les doutes qui comptent portent sur ce qui se passe **quand rien ne
se passe comme prévu**.

## Comment prouver

- **Exécute sur des données d'essai**, jamais chez de vrais clients : données
  épinglées sur le déclencheur (pinData dans n8n), copie du formulaire, canal
  de test. Lis l'exécution étape par étape, avec le nombre d'éléments à chaque
  étape.
- **Rejoue le même événement deux fois**, puis compte les effets : fiches
  créées, emails envoyés, lignes écrites. Un de trop, c'est un doublon.
- **Simule la panne** : identifiants invalides sur une étape, adresse injoignable.
  Vérifie la branche d'erreur, l'alerte, et ce que devient l'élément.
- **Envoie les cas limites** : champ vide, format inattendu, plus d'éléments
  qu'une page de l'API n'en renvoie.
- **Simule un jour sauté** : que deviennent les traitements dus le jour où
  l'automatisation n'a pas tourné ? Une condition « date = aujourd'hui » les
  perd pour toujours ; « date ≤ aujourd'hui et pas encore fait » les rattrape.
- **Valide le fichier** avec l'outil de l'éditeur ou le validateur du projet
  quand il en existe un.

## Doutes typiques

- **Rejeu et doublons** : quelle clé reconnaît un élément déjà traité ?
- **Rattrapage** : les éléments arrivés pendant une panne, ou dus un jour où
  rien n'a tourné, sont-ils traités au redémarrage — une seule fois ?
- **Fuseau** : un déclenchement « à 9 h » sur un serveur réglé en UTC ; une
  comparaison de dates sans fuseau ; jours fériés et week-ends.
- **Zéro silencieux** : un passage qui ne trouve plus rien « réussit ». Une
  alerte sur un volume anormal le rend visible.
- **Un élément en erreur bloque-t-il tout le lot**, ou seulement lui ?
- **Types** : une valeur texte « false » ou « 0 » testée comme un booléen ; un
  nombre comparé à du texte ; une expression qui renvoie vide sans erreur.
- **Volume** : pagination, quotas d'appels, délais d'attente, pic de charge.
- **Accès** : identifiants rattachés au compte d'une personne, qui expirent ou
  partent avec elle.
- **Données personnelles** visibles dans l'historique des exécutions.
- **Effets irréversibles** : un email client part-il avant que le statut soit
  relu ? Un interrupteur général existe-t-il pour tout couper ?
