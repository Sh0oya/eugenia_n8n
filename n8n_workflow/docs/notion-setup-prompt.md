# Prompt à coller dans ChatGPT

> Copie tout le bloc ci-dessous dans ChatGPT (de préférence avec le connecteur Notion activé). Sans connecteur, ChatGPT te rendra le contenu à coller ou à importer toi-même.

---

Tu connais mes échanges passés, ma configuration et mes projets. J'ai besoin que tu prépares dans Notion le contexte personnel d'un workflow n8n appelé « Ça tourne sur mon PC ? ». Ce workflow lit ces pages automatiquement : **respecte exactement les noms, les types et les formats ci-dessous**, sinon il ne pourra pas les lire.

## Règles de contenu

- N'écris que ce qui sert à diagnostiquer l'installation d'outils sur mon PC : matériel, systèmes, noms et versions de logiciels, usages, retours d'expérience, objectifs, contraintes de temps. Pas de secret, pas de clé, pas d'information personnelle sans rapport.
- Pour chaque information, indique sa **provenance et sa date** (ex. « échange du 7 octobre 2026 », « déclaration du 20 octobre 2026 ») et ce qui reste **incertain**. Les déclarations récentes priment sur les souvenirs anciens.
- Ne transforme jamais une ancienne suggestion en installation. « Abandonné » décrit l'usage, pas la désinstallation : la présence technique reste « présente », « absente » ou « inconnue ».
- Si tu ne sais pas, écris-le. N'invente ni version ni outil.

## 1. Page racine

Crée une page **« Ça tourne sur mon PC ? »**. Les trois éléments suivants sont ses enfants.

## 2. Page « Profil machine et contexte »

Contenu dans cet ordre, **sans tableau, sans bloc repliable et sans bloc imbriqué** (uniquement titres, paragraphes et listes à puces) :

1. Un **bloc de code de langage JSON**, exactement de cette forme (garde `null` quand c'est inconnu) :

```json
{
  "revision": "2026-10-21",
  "machine": {
    "systemes": ["Windows 11", "Ubuntu via WSL"],
    "cpu": "Intel Core Ultra 7 255H",
    "gpu": "Intel Arc 140T (graphique intégré)",
    "vramGo": null,
    "ramGo": 32,
    "stockageEssaisGo": 100,
    "environnements": ["Windows", "WSL", "Conda/Miniforge"],
    "aPreserver": ["LeRobot et ses dépendances (environnement Conda lerobot)"],
    "nonRenseigne": ["mémoire graphique dédiée", "versions actuelles détaillées des dépendances"]
  }
}
```

   Complète ou corrige les valeurs avec ce que tu sais de ma machine. `revision` est la date du jour : je la changerai à chaque modification importante du matériel ou des objectifs (cela déclenche le réexamen des rapports).

2. Puis ces sections de titre 2, chacune avec des puces courtes (provenance + date + incertitude) :
   - `## Activités`
   - `## Projets et intérêts` (sans présumer de priorité)
   - `## Historique technique` (versions connues, environnements, essais et difficultés)
   - `## Objectifs`
   - `## Contraintes` (temps, budget de 5 €/mois hors n8n, préférences)

## 3. Base de données « Inventaire des outils »

Propriétés, avec ces noms exacts (sans accent) et ces types :

| Propriété | Type | Valeurs |
|---|---|---|
| Nom | Titre | nom usuel de l'outil |
| Etat | Sélection | `installé`, `abandonné`, `désinstallé` |
| Presence | Sélection | `présente`, `absente`, `inconnue` |
| Usage | Texte | usage prévu, raison d'installation |
| Retour | Texte | réussites, lenteurs, erreurs, avantages |
| Raison Abandon | Texte | si abandonné |
| Environnement | Texte | Windows, WSL, nom de l'environnement Conda… |
| Version | Texte | version connue, sinon vide |
| Date Info | Date | date de l'information |
| Source | Texte | provenance (échange, déclaration…) |
| Incertitudes | Texte | ce qui reste à confirmer |

Remplis une ligne par outil que j'ai installé, essayé, abandonné ou désinstallé (50 au maximum) : LeRobot, Conda/Miniforge, éditeurs, outils de robotique, d'IA, d'automatisation, etc. Un dépôt seulement analysé n'est **pas** un outil de l'inventaire.

## 4. Base de données « Analyses » (vide)

Le workflow y écrit ses rapports. Crée-la vide avec ces propriétés :

| Propriété | Type | Options |
|---|---|---|
| Nom | Titre | |
| Statut | Sélection | `en attente`, `échec`, `terminé`, `historique`, `à réexaminer`, `repris`, `annulé` |
| Diagnostic Id | Texte | |
| Mode | Sélection | `un`, `plusieurs`, `comparer` |
| Depots | Texte | |
| Cle | Texte | |
| Version | Texte | |
| TLDR | Texte | |
| Cout EUR | Nombre | format euro |
| Livraison | Sélection | `en cours`, `complète`, `e-mail en échec` |
| Contexte Ids | Texte | |
| Profil Revision | Texte | |
| Moteur | Texte | |
| Demande JSON | Texte | |
| Precedent | URL | |
| Remplacee Par | URL | |
| Decision | Sélection | `installé`, `ignoré`, `désinstallé` (rempli à la main : l'IA en tient compte aux analyses suivantes) |

## 5. À me rendre à la fin

- le lien de la page « Profil machine et contexte » ;
- les liens des deux bases ;
- la liste des informations que tu as marquées incertaines, pour que je les confirme.
