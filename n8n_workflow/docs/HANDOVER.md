# Document de transfert — Can My PC Run It

Sections imposées par le cours (module « Livraison »). Le détail de mise en service est dans le [README](../README.md).

## Fiche d'identité

| | |
|---|---|
| Workflow | `Can My PC Run It`, version 3.1 (schéma du diagnostic 3.1) |
| Rôle | dire, avant d'installer un outil GitHub public, s'il tournera sur le PC de Mathieu et avec ses outils (rapport en français : e-mail et page Notion) |
| Propriétaire métier | Mathieu Haye |
| Propriétaire technique | Mathieu Haye |
| Projet n8n | Personal, dossier Sandbox |
| Déclencheur | formulaire protégé par Basic Auth (`/form/can-my-pc-run-it`) ; l'Error Trigger fait du workflow son propre Error workflow |
| Livrable | 1 page dans la base Notion « Analyses », 1 e-mail HTML, 1 ligne dans `analysis_history` |
| Volume attendu | usage manuel et ponctuel, une demande à la fois, 3 dépôts au plus (hypothèse à confirmer par Mathieu : moins de 20 demandes par mois) |
| Coût par exécution | voir « Coût et quotas » du README (jusqu'à 4 appels Gemini ; aucun budget mensuel automatique) |

## Dépendances et credentials

| Credential (nom exact) | Type n8n | Sert à | Renouvellement |
|---|---|---|---|
| `Google Gemini - Free Tier` | Google Gemini(PaLM) API | diagnostic IA (modèle principal, modèle de secours) | clé Google AI Studio : Mathieu |
| `Gmail - Mathieu` | Gmail OAuth2 | rapport, rapport existant, alerte d'erreur | Mathieu ; à reconnecter si Google révoque le jeton |
| `Notion - Eugenia Workspace` | Notion OAuth2 | lire le profil, l'inventaire et les décisions ; créer la page du rapport | Mathieu ; les 3 pages et bases doivent rester partagées avec l'intégration |
| `Basic Auth - Diagnostic Form` | HTTP Basic Auth | protège le formulaire | Mathieu |
| `GitHub - Public Repositories Read` | GitHub API (token) | lecture des dépôts publics | token fine-grained en lecture seule : Mathieu, à renouveler à son échéance |

Données externes : la base Notion « Profil » (machine, activités, objectifs), la base « Inventaire » des outils, la base « Analyses » (avec la propriété `Decision`). Le profil et l'inventaire sont envoyés à Gemini à chaque analyse.

Data Tables n8n : `analysis_history` et `error_incidents` (colonnes dans le README).

## Surveillance et alertes

- Toute exécution en erreur déclenche le bloc 7 : une ligne dans `error_incidents` et un e-mail « Échec - … » à l'adresse de `CONFIGURATION.notificationEmail`, avec le lien de l'exécution.
- Canal d'alerte : **Gmail, le même que celui de la livraison**. Si le credential Gmail tombe, aucune alerte ne part : regarder la liste des exécutions de n8n et `error_incidents`.
- Une demande invalide (URL refusée, trop de dépôts) est aussi une exécution en erreur, donc un e-mail avec la raison.
- Réglage à faire une fois : `Settings` → `Error workflow` → choisir ce même workflow (possible seulement après la première publication).
- Audit tous les 3 à 6 mois (prochain : avant le 23/04/2027), noté dans la sticky « Journal des Revues » du canvas : nodes obsolètes, modèles `latest`, prompt, credentials à renouveler.

## Kill switch

1. Dépublier le workflow (`Unpublish`) : le formulaire répond 404 et plus rien ne se déclenche.
2. Annuler les exécutions en cours depuis la liste des exécutions.
3. Si une fuite est suspectée : révoquer la clé Gemini, le token GitHub et l'accès de l'intégration Notion, puis changer le mot de passe du credential Basic Auth.
4. Pour repartir : republier, vérifier le Error workflow, relancer une demande de test.
