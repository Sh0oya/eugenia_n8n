# Douter d'un code

Fonction, diff, script, appel d'API. Le code a un avantage sur tous les autres
artefacts : presque tout doute s'y prouve en l'exécutant.

## Comment prouver

- **Lance les tests existants**, puis **lis ce qu'ils affirment** : un test vert
  qui attend la mauvaise valeur grave l'erreur au lieu de la détecter. Compare
  chaque valeur attendue au contrat, pas au code.
- **Écris le test du doute** avant toute correction : le cas limite, l'entrée
  piège, le rejeu. Il doit échouer si le doute est fondé. Range-le dans un
  dossier temporaire, hors du projet ; son ajout au projet se propose avec la
  correction.
- **Exécute la fonction sur le scénario** du relecteur, dans un script jetable
  rangé dans un dossier temporaire, jamais dans le projet.
- **Cherche les appelants** du code modifié (recherche du nom de la fonction) :
  un changement de sens ou de signature les touche tous, et le diff ne les
  montre pas.
- **Un comportement existant se lit sur chaque chemin** : deux appelants, deux
  canaux, deux rôles peuvent diverger. Lu sur un seul, il n'est pas uniforme.
- Typage et linter prouvent la forme, jamais le comportement.

## Doutes typiques

- **Bornes** : décalage d'un, inclus ou exclu, liste vide, premier et dernier
  élément, une seule entrée.
- **Absent** : `None`, `null`, `undefined`, chaîne vide, zéro, champ manquant
  dans une réponse d'API.
- **Argent** : flottants pour des montants, arrondi à chaque ligne ou au total,
  arrondi « bancaire » (au pair) là où le métier attend l'arrondi au-dessus,
  division par zéro, devise et taxes.
- **Dates** : fuseau implicite, dates sans fuseau mélangées à des dates avec,
  changement d'heure, fin de mois, 29 février, jour inclus ou exclu dans une
  durée.
- **Concurrence et rejeu** : vérifier-puis-agir sans verrou, double soumission,
  traitement appelé deux fois avec le même message.
- **Erreurs avalées** : `except: pass`, `catch {}` vide, un retour vide pris pour
  un succès, une erreur journalisée mais pas remontée.
- **Frontières** : format exact de l'API tierce, pagination, codes d'erreur,
  limites de débit, délai d'attente, version.
- **Sécurité** : entrée non validée, injection, secret dans le code ou les
  journaux, droit vérifié seulement côté client.
- **Volume** : requête dans une boucle, tout charger en mémoire, absence de
  limite.
