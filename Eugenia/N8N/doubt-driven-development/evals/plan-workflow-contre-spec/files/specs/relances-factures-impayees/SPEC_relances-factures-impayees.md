---
slug: relances-factures-impayees
titre: Relances automatiques des factures impayées
date: 2026-10-22
statut: proposé
solidite_besoin: déclaré
profondeur: béton
lecteur: agent de code qui construit le workflow n8n
---

# Spec — Relances automatiques des factures impayées

> Preuves : `[observé]` constaté dans une source datée · `[déclaré]` rapporté, non recoupé · `[hypothèse]` conviction ou proposition non prouvée.

---

## 0 - Cadrage

**Relancer par email, sans intervention humaine, les clients dont une facture du studio est échue et impayée, trois fois au plus, puis remettre le dossier à l'associée chargée de la facturation.**

- **Lecteur** : l'agent de code qui construit le workflow n8n. La spec doit lui permettre de construire sans revenir poser une seule question métier.
- **Profondeur** : béton — le workflow écrit à des clients au nom du studio : une erreur se voit tout de suite et coûte une relation.

## 1 - Problème

### Premier cas d'usage

**En tant que** associée chargée de la facturation
**Lorsque je** fais le point mensuel sur la trésorerie
**Ce qui compte pour moi est** d'être payée à temps sans passer mes soirées à relancer
**Mais** je découvre des factures en retard de 30 à 60 jours que personne n'a relancées
**Et donc aujourd'hui** je relance à la main depuis ma boîte mail, une fois par mois, quand j'y pense

**Cas d'usage suivants, non traités en premier :** relance des devis non signés, relance des acomptes.

### Preuves

| Ce qui est affirmé | Source (qui ou quoi + date) | Statut |
| --- | --- | --- |
| 11 factures sur 38 émises en septembre étaient échues et impayées | Export Pennylane du 2026-10-01 | [observé] |
| Les relances manuelles prennent environ 3 h par mois | Claire M., associée, entretien du 2026-10-20 | [déclaré] |
| Une relance rapide suffit à faire payer la plupart des retards | Conviction de l'équipe | [hypothèse] |

### Coût du contournement actuel

Environ 3 h par mois `[déclaré]` et 18 450,00 € d'encours en retard au 2026-10-01 `[observé]`.

## 2 - Objectifs & succès

### Indicateurs de succès

| # | Indicateur | Définition exacte | Valeur de départ | Cible | Garde-fou |
| --- | --- | --- | --- | --- | --- |
| I1 | Délai moyen de paiement | Moyenne, sur les factures payées dans le mois, de (date de paiement − date d'émission), en jours | 41 jours (septembre 2026) | ≤ 30 jours | Aucune plainte client liée aux relances |
| I2 | Temps passé en relances manuelles | Temps déclaré par l'associée en fin de mois | 3 h | ≤ 30 min | Aucun dossier escaladé non traité après 7 jours |

### Ce qui nous ferait renoncer

Plus d'un client sur dix qui se plaint du ton ou de la fréquence des relances sur les deux premiers mois.

### Risques

| Risque | Conséquence | Parade |
| --- | --- | --- |
| Relancer une facture déjà payée mais pas encore rapprochée | Client agacé, image dégradée | Premier envoi à J+3 (H1) et statut lu au moment de l'envoi (R05) |
| Le workflow tombe en silence | Plus aucune relance, personne ne s'en aperçoit | Alerte sur résultat suspect (R10) |

## 3 - Périmètre

### Dans le périmètre

- Les factures clients émises dans Pennylane, en euros.
- Trois relances par email, puis l'escalade à l'associée.

### Hors périmètre

- Relance par SMS ou téléphone : le studio garde le téléphone comme canal humain.
- Mise en demeure et recouvrement : décision d'une associée, jamais automatique.

### Renvoyé à plus tard

- Relance des devis non signés — revient si les relances de factures tournent deux mois sans incident.
- Factures en devise étrangère — revient quand le studio facture un premier client hors zone euro.

### Contraintes imposées

- Le workflow tourne sur l'instance n8n déjà hébergée par le studio.
- Pennylane reste la source de vérité des factures et de leur statut de paiement.
- Les emails partent de l'adresse de comptabilité du studio, jamais d'une adresse personnelle.

### Dépendances & adjacences

- Le rapprochement bancaire de Pennylane fait passer une facture à « payée », avec 1 à 3 jours ouvrés de décalage `[déclaré]`.

## 4 - Acteurs & vocabulaire

### Acteurs

| Acteur | Ce qu'il fait dans le projet | Volume / fréquence |
| --- | --- | --- |
| Client du studio | Reçoit les relances, paie | 25 à 40 factures par mois |
| Associée facturation | Allume les relances, suspend une facture, traite les escalades | 1 personne |
| Workflow de relance | Détecte les factures échues, envoie, trace, alerte | 1 passage par jour ouvré |

### Glossaire

| Terme | Définition dans ce projet |
| --- | --- |
| Facture échue | Facture dont la date d'échéance est passée et dont le statut Pennylane n'est ni « payée » ni « annulée » |
| Relance | Email envoyé au contact de facturation d'un client au sujet d'une seule facture échue |
| Escalade | Remise du dossier à l'associée : plus aucune relance automatique ensuite |
| Jour ouvré | Du lundi au vendredi, hors jours fériés de France métropolitaine |

## 5 - Domaines transverses balayés

| Domaine | Verdict | Règles ou raison |
| --- | --- | --- |
| Acteurs, rôles & droits | impacté | R08 |
| Paramétrage & activation | impacté | R01 |
| Données : création, modification, suppression, conservation | non impacté | Le workflow lit les factures, il n'en crée ni n'en modifie aucune |
| Données personnelles & confidentialité | impacté | R04 |
| Erreurs, indisponibilités & mode dégradé | impacté | R09, R10, R12 |
| Notifications & communication | impacté | R03, R07 |
| Historique, traçabilité & effet sur le passé | impacté | R06 |
| Volume, fréquence & délais | non impacté | Moins de 50 factures par passage : aucun enjeu de volume ; le délai est fixé par N1 |
| Reprise de l'existant | impacté | R11 |

## 6 - Parcours & règles

### 6.1 Prérequis & activation

> **Acteur** : associée facturation · **Moment** : avant le premier envoi

**R01 — Aucune relance ne part tant que l'interrupteur « relances actives » est éteint.** Éteint, le workflow continue de détecter et de tracer les factures échues, sans rien envoyer. → **NOUVEAU**.
- L'interrupteur est éteint à la mise en service ; l'associée l'allume après avoir relu les trois modèles d'email.

### 6.2 Parcours nominal

> **Acteur** : workflow de relance · **Moment** : chaque jour ouvré à 9 h 00, heure de Paris

**R02 — Une facture échue reçoit au plus trois relances, dues à J+3, J+10 et J+20 jours calendaires après son échéance (H1).** Une relance due un jour non ouvré part le jour ouvré suivant. Exemple : échéance le jeudi 29 octobre 2026 → J+3 tombe le dimanche 1er novembre, férié, la relance 1 part le lundi 2 novembre ; J+10 tombe le dimanche 8 novembre, la relance 2 part le lundi 9 ; la relance 3 part le mercredi 18 novembre. → **NOUVEAU**.

**R03 — Chaque relance indique le numéro de la facture, sa date d'échéance, le montant restant dû et son lien de paiement.** Le ton monte d'un cran à chaque relance ; les trois textes sont validés par l'associée avant activation (R01). → **NOUVEAU**.
- Le montant affiché est le restant dû, pas le montant initial : une facture de 2 340,00 € déjà réglée à hauteur de 1 000,00 € affiche 1 340,00 €.

**R04 — Une relance part uniquement vers le contact de facturation du client, sans aucune autre personne en copie.** → **NOUVEAU**.

#### Cas limites

**R05 — Une facture payée ou annulée après sa détection ne reçoit pas la relance prévue.** Le statut qui compte est celui du moment de l'envoi, pas celui du début du passage. → **NOUVEAU**.

**R12 — Une facture sans adresse email de facturation valide ne reçoit aucune relance et figure, avec son motif, dans l'alerte du jour envoyée à l'associée.** → **NOUVEAU**.

**R09 — Si Pennylane est injoignable, le passage n'envoie rien et alerte l'associée ; le passage suivant rattrape les relances dues sans en envoyer aucune deux fois.** Exemple : Pennylane injoignable le mardi ; le mercredi, une facture arrivée à J+3 la veille reçoit sa relance 1, une seule fois. → **NOUVEAU**.

**R10 — Un passage qui trouve zéro facture échue alors que le précédent en trouvait au moins 5 alerte l'associée d'un résultat suspect.** Un zéro silencieux est le défaut le plus coûteux : plus rien ne part et personne ne le voit. → **NOUVEAU**.

### 6.3 Résultat

> **Acteur** : associée facturation · **Moment** : après chaque passage

**R06 — Chaque relance envoyée laisse une trace consultable : facture, numéro de relance (1, 2 ou 3), date et heure d'envoi, destinataire.** → **NOUVEAU**.

**R07 — Une facture toujours impayée 7 jours après sa relance 3 passe en escalade : l'associée reçoit un récapitulatif et plus aucune relance automatique ne part pour cette facture.** → **NOUVEAU**.

**R08 — L'associée suspend les relances d'une facture en lui ajoutant l'étiquette « pas de relance » dans Pennylane ; retirer l'étiquette les réactive au point où elles s'étaient arrêtées.** → **NOUVEAU**.

### 6.4 Reprise de l'existant

> **Acteur** : workflow de relance · **Moment** : premier passage après activation

**R11 — Au premier passage, une facture échue depuis plus de 20 jours passe directement en escalade, sans email ; les autres reçoivent la seule relance due ce jour-là selon R02.** Exemple : échue depuis 12 jours → elle reçoit la relance 2, jamais les relances 1 et 2 le même jour. → **NOUVEAU**.

## 7 - Données & états

### Facture, vue du workflow

| Champ | Obligatoire | Format / bornes | Valeur par défaut | Source |
| --- | --- | --- | --- | --- |
| Numéro | oui | texte, par exemple F-2026-0142 | — | Pennylane |
| Date d'échéance | oui | date | — | Pennylane |
| Restant dû | oui | euros, 2 décimales, strictement positif | — | Pennylane |
| Email de facturation | oui | adresse email valide | — | Pennylane, fiche client |
| Étiquette « pas de relance » | non | présente ou absente | absente | Pennylane |

### États d'une facture suivie

| État | Ce qui est visible | Ce qu'on peut faire | Transitions possibles |
| --- | --- | --- | --- |
| À relancer | rien côté client | suspendre (R08) | vers Relancée 1 au premier envoi |
| Relancée 1, 2 ou 3 | la trace de chaque envoi (R06) | suspendre | vers la relance suivante, vers Escaladée (R07), vers Close au paiement |
| Escaladée | le récapitulatif reçu par l'associée | traiter à la main | vers Close au paiement |
| Suspendue | l'étiquette dans Pennylane | réactiver en retirant l'étiquette | vers l'état d'avant la suspension |
| Close | — | — | aucune |

## 8 - Exigences non fonctionnelles

| # | Exigence | Seuil mesurable | Comment on le vérifie |
| --- | --- | --- | --- |
| N1 | Les relances du jour sont parties avant 10 h 00 | 100 % des jours ouvrés | Horodatage des traces R06 sur un mois |
| N2 | Aucune relance en double | 0 couple (facture, numéro de relance) envoyé deux fois | Contrôle des traces R06 |

## 9 - Synthèse des règles

| # | Règle | Lot | Type |
| --- | --- | --- | --- |
| R01 | Rien ne part tant que l'interrupteur est éteint | nominal | NOUVEAU |
| R02 | Trois relances au plus, à J+3, J+10, J+20, décalées au jour ouvré | nominal | NOUVEAU |
| R03 | Contenu obligatoire d'une relance, montant restant dû | nominal | NOUVEAU |
| R04 | Destinataire unique : le contact de facturation | nominal | NOUVEAU |
| R05 | Pas de relance si payée ou annulée au moment de l'envoi | limite | NOUVEAU |
| R06 | Trace consultable de chaque envoi | nominal | NOUVEAU |
| R07 | Escalade 7 jours après la relance 3 | nominal | NOUVEAU |
| R08 | Suspension et réactivation par étiquette | limite | NOUVEAU |
| R09 | Pennylane injoignable : rien n'est envoyé, rattrapage sans doublon | limite | NOUVEAU |
| R10 | Alerte sur un zéro suspect | limite | NOUVEAU |
| R11 | Premier passage : escalade au-delà de 20 jours, une seule relance sinon | limite | NOUVEAU |
| R12 | Email de facturation absent ou invalide : signalé, pas envoyé | limite | NOUVEAU |

## 10 - Hypothèses posées par défaut

| # | Hypothèse | Si elle est fausse | Qui peut confirmer |
| --- | --- | --- | --- |
| H1 | Le rapprochement bancaire ne prend jamais plus de 3 jours ouvrés | Des clients ayant payé reçoivent la relance 1 : décaler J+3 à J+5 dans R02 | Claire M., sur deux mois d'historique Pennylane |

## 11 - Points ouverts

| # | Sujet | Criticité | À trancher | Qui tranche |
| --- | --- | --- | --- | --- |
| P1 | Signature des emails | modalité | « L'équipe du studio » ou le prénom de l'associée ? Recommandé : l'équipe, qui survit à un départ | Claire M. |
