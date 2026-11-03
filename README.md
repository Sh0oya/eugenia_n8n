# Ça tourne sur mon PC ? — un workflow n8n

Livrable de Mathieu Haye pour le cours « n8n x Eugenia » (Lucas Peyrin).

> Je colle l'URL d'un dépôt GitHub public dans un formulaire. Le workflow lit sa dernière release, la croise avec **mon PC** et **mes outils** (Notion), demande un diagnostic à Gemini, puis m'envoie un rapport en français par e-mail et dans Notion. **Rien n'est installé ni exécuté** : c'est une analyse de documents.

## Par où commencer

1. ▶ **[Regarder la vidéo](video/explication-n8n.mp4)** (5 min 23)
2. 📄 **[Lire la transcription](video/transcript.md)** (automatique, non relue)
3. 🧩 **[Ouvrir le workflow](workflow/can-my-pc-run-it.workflow.ts)**

## Le dépôt en 3 dossiers

```
eugenia_n8n/
├── workflow/   ← 1 workflow : can-my-pc-run-it.workflow.ts
├── skills/     ← 3 skills Claude Code
└── video/      ← la vidéo compressée + sa transcription
```

| Dossier | Contenu |
|---|---|
| [`workflow/`](workflow/) | **1 seul fichier** : [`can-my-pc-run-it.workflow.ts`](workflow/can-my-pc-run-it.workflow.ts), le workflow `Can My PC Run It` au format SDK de n8n-cli. 40 nodes, 7 blocs, 11 sticky notes, publié sur l'instance n8n de l'auteur le 28 octobre 2026 |
| [`skills/`](skills/) | **3 skills** : [`spec-beton`](skills/spec-beton/SKILL.md) (cadrer une spec), [`doubt-driven-development`](skills/doubt-driven-development/SKILL.md) (douter et prouver), [`hostile-review`](skills/hostile-review/SKILL.md) (revue à froid). Le détail est dans [`skills/README.md`](skills/README.md) |
| [`video/`](video/) | [`explication-n8n.mp4`](video/explication-n8n.mp4) (vidéo d'explication compressée, 10 Mo) et [`transcript.md`](video/transcript.md) (sa transcription) |

## Le workflow en 7 blocs

| Bloc | Rôle |
|---|---|
| 1. Entrée | Formulaire protégé par Basic Auth (URL GitHub, objectif, « refaire l'analyse »), nœud `CONFIGURATION`, vérification : un seul dépôt par demande |
| 2. Preuves GitHub | Nodes GitHub natifs : dernière release stable (ou branche par défaut), `README.md`, `pyproject.toml` |
| 3. Réutilisation | Si le même dépôt, la même version et le même objectif ont déjà été analysés, l'ancien rapport est renvoyé par e-mail, sans appel IA |
| 4. Contexte Notion | Mon profil machine, mon inventaire d'outils et mes décisions passées (installé, ignoré, désinstallé) |
| 5. Diagnostic IA | Gemini Flash (secours Flash-Lite), prompt en XML, sortie JSON stricte, puis un contrôle par code : les preuves GitHub l'emportent sur l'IA |
| 6. Livraison | Page Notion, e-mail HTML, ligne dans la Data Table `analysis_history` |
| 7. Erreurs | Le workflow est son propre Error workflow : incident dans `error_incidents` et alerte Gmail |

## Pour l'utiliser dans n8n

Le fichier est la version **portable** : identifiants Notion fictifs, aucun credential réel. Il faut :

- créer les credentials avec ces noms : `Google Gemini - Free Tier`, `Gmail - Mathieu`, `Notion - Eugenia Workspace`, `Basic Auth - Diagnostic Form`, `GitHub - Public Repositories Read` ;
- créer les 2 Data Tables `analysis_history` et `error_incidents` ;
- renseigner dans le nœud `CONFIGURATION` les 3 identifiants Notion et l'adresse e-mail.

Envoi avec n8n-cli : `npx n8ncli push` (l'instance se déclare d'abord avec `npx n8ncli envs edit PROD --url … --access-token …`).

## Projet complet

Le README détaillé (règles du cours une par une, tests, limites), le JSON importable, le générateur Python, les 48 tests et les documents de transfert sont sur la branche [`archive/projet-complet`](https://github.com/Sh0oya/eugenia_n8n/tree/archive/projet-complet).
