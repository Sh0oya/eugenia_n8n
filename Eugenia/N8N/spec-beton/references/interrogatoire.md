# Interroger branche par branche

Phase 4 : c'est ici que se pose l'essentiel des questions. Le cadrage dit
**quoi** construire ; l'interrogatoire bouche les trous que le constructeur
comblerait sinon en devinant. Chaque trou non posé ici devient une décision
prise par défaut, en silence, par celui qui code.

## La carte de couverture

Elle vit en tête du JOURNAL et pilote l'ordre des lots. Une zone par ligne,
un état par zone :

| État | Sens |
| --- | --- |
| ✅ | clair : tranché, écrit ou prêt à l'être |
| 🟡 | hypothèse posée par défaut (Hn), à confirmer au gate |
| ❓ | pas encore couvert |
| ⛔ | bloquant : impossible d'écrire la zone sans une réponse |
| — | sans objet, avec la raison |

Parcours l'arbre de décision **de l'amont vers l'aval** : une question dont la
réponse dépend d'une décision non prise attend cette décision. « Qui peut
annuler une commande ? » attend « Y a-t-il des rôles ? ». Poser l'aval d'abord
fait répondre deux fois.

## Le squelette de parcours

Les règles s'écrivent dans l'ordre d'un parcours ; les questions aussi. Chaque
phase est **un moment** — qui fait quoi, quand. Une phase sans règle disparaît
de la spec ; une phase propre au projet s'ajoute à sa place.

| Phase | Ce qu'elle porte | Questions qu'on oublie |
| --- | --- | --- |
| Prérequis & activation | ce qui doit être vrai avant, qui active, à quel niveau | état initial (allumé ou éteint ?) ; activation globale, par client, par utilisateur ? ; comptes et accès à obtenir avant |
| Paramétrage | ce qui se règle, et par qui | ce qui est figé vs réglable ; valeurs par défaut ; effet d'un changement de réglage sur ce qui est **déjà en cours** |
| Mise à disposition | comment ça arrive aux utilisateurs | délai avant que ce soit visible ; qui est prévenu ; ce que voient ceux qui n'y ont pas droit |
| Parcours nominal | le chemin principal, une sous-section par surface ou canal | le **déclencheur exact** (geste ou événement) ; ce que voit ou reçoit chaque acteur à chaque étape |
| Résultat | ce qu'il en reste | document, email, ligne, export, trace : qui le consulte, sous quelle forme, combien de temps |
| Cycle de vie | modifier, désactiver, supprimer | **effet sur le passé** : un objet modifié change-t-il ce qui a déjà été produit ? archivage ; conservation |
| Reprise de l'existant | ce qui est en place au démarrage | données ou process existants ; bascule d'un coup ou progressive ; coexistence de l'ancien et du nouveau |

Un thème transverse — droits, notifications, erreurs — ne devient jamais une
phase : il se répartit dans les phases où il se manifeste.

## Les investigations qui trouvent les vrais défauts

À mener sur chaque règle candidate, pas comme un rituel : seulement les blocs
qui s'appliquent.

- **Données** : absent, vide, zéro, doublon, trop long, format inattendu ;
  valeur par défaut ; bornes ; unicité.
- **Action** : qui peut la faire ; son **geste déclencheur** (bouton, étiquette,
  réponse à un email, événement) ; l'état avant et après ; réversible ou non ;
  confirmation demandée ou non.
- **Échec** : chaque branche d'échec — ce que voit l'utilisateur, qui est
  prévenu, ce que devient la donnée, peut-on rejouer sans doublon ?
- **Temps** : fuseau horaire ; jours ouvrés et fériés ; changement d'heure ;
  ordre d'arrivée ; deux événements simultanés ; ce qui se passe à minuit.
- **Concurrence** : deux personnes modifient la même chose ; double clic ;
  événement rejoué.
- **Calcul** : un exemple **non rond** (8,50 € réparti sur 7 lignes, pas 100 €
  sur 4) ; où et comment on arrondit ; unité ; devise ; ordre des opérations.
  Sans exemple, l'arrondi se découvre en production.
- **Défaillance silencieuse** : pour tout filtre, ciblage ou limite, le cas où
  le résultat est **vide sans erreur**. Une relance qui ne trouve plus aucune
  facture, un formulaire qui écrit dans une boîte que personne ne lit : invisible
  à la configuration, découvert des semaines plus tard. C'est le défaut le plus
  coûteux ; il mérite presque toujours sa règle.
- **Affiché ≠ appliqué** : un compteur, un quota ou un solde montré à l'écran et
  celui qui contraint réellement sont-ils le même calcul ? Deux calculs, c'est un
  suivi trompeur.
- **Messages** : l'information que le message doit porter est une règle (« le
  refus indique le montant manquant ») ; sa formulation exacte n'en est pas une.

## Les domaines transverses

Le §5 de la spec rend visible ce qui a été **regardé et jugé sans impact**, par
opposition à **pas regardé**. Un verdict par domaine : `impacté` (les règles),
`non impacté` (la raison, une ligne), `hors-lot` (la décision et qui la porte).

**Le socle, balayé sur tout projet** — le script vérifie qu'il est complet :

| Domaine | La question à se poser |
| --- | --- |
| Acteurs, rôles & droits | qui peut faire quoi ; que voit celui qui n'a pas le droit |
| Paramétrage & activation | qui allume, qui règle, à quel niveau |
| Données : création, modification, suppression, conservation | ce qui est créé, par qui ; suppression définitive ou non ; durée de conservation |
| Données personnelles & confidentialité | quelles données personnelles, où elles transitent, qui y accède, droit à l'effacement |
| Erreurs, indisponibilités & mode dégradé | un service tiers en panne, une saisie invalide, un délai dépassé |
| Notifications & communication | qui est prévenu de quoi, par quel canal, à quel moment |
| Historique, traçabilité & effet sur le passé | ce qu'on garde comme trace ; ce que devient le passé quand on modifie |
| Volume, fréquence & délais | combien, à quelle fréquence, quel pic, quel délai acceptable |
| Reprise de l'existant | données, utilisateurs et habitudes déjà en place |

**Les domaines conditionnels**, ajoutés seulement si le projet les touche :
paiement et facturation · multi-langue, multi-devise, multi-fuseau ·
IA générative · intégrations tierces · mobile et hors-ligne · accessibilité ·
légal, fiscal ou sectoriel · fichiers et médias · recherche et filtres ·
import et export · planification · acquisition et référencement.

## Les exigences non fonctionnelles

Seulement mesurables, chacune avec son seuil et sa méthode de vérification :
volume (par jour, en pic) · délai de réponse · comportement pendant une panne
d'une heure · durée de conservation · accès et sécurité · **coût de
fonctionnement mensuel maximal** (abonnements, API, appels à un modèle d'IA) ·
qui maintient, avec quelles compétences.

« Rapide » n'est pas une exigence ; « la liste s'affiche en moins de 2 s pour
95 % des chargements » en est une.

## Quand s'arrêter

- **En béton** : plus aucune zone ❓ ni ⛔ ; chaque point BLOQUANT ou structurant
  est tranché ou assumé comme point ouvert ; les modalités restantes sont des
  hypothèses.
- **Fatigue** : tous les trois lots, ou dès qu'il ne reste que des modalités,
  propose le choix — continuer (en disant combien de zones restent) ou passer
  le reste en hypothèses. L'utilisateur décide.
- **Rendement décroissant** : un lot qui n'a produit que des modalités est le
  signal de passer à la rédaction.
- **Le test de prédiction** : si tu peux prédire sans hésiter la réponse de
  l'utilisateur à tes trois prochaines questions, tu as compris — arrête de
  demander et écris, en posant ces trois réponses comme hypothèses.
