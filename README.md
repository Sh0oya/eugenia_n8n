# eugenia_n8n

Livrable de Mathieu Haye pour le cours « n8n x Eugenia » (Lucas Peyrin) : **un seul workflow n8n qui dit si un outil GitHub tournera sur mon PC avant que je l'installe.** Je colle l'URL d'un dépôt dans un formulaire ; je reçois un rapport en français par e-mail et dans Notion. Rien n'est installé ni exécuté.

![Canvas du workflow Can My PC Run It](n8n_workflow/docs/img/canvas-plan.svg)

*1 workflow, 40 nodes en 7 blocs, 11 sticky notes. Publié sur l'instance n8n de l'auteur le 28 octobre 2026.*

## Par où commencer

| Je veux… | J'ouvre |
|---|---|
| comprendre le workflow en 2 minutes (schéma, captures) | [`n8n_workflow/README.md`](n8n_workflow/README.md) |
| vérifier les règles du cours, une par une | [Les règles du cours](n8n_workflow/README.md#les-règles-du-cours) |
| voir ce qui a été testé, et ce qui ne l'a pas été | [Tests effectués](n8n_workflow/README.md#tests-effectués) |
| lire le prompt de l'IA | [`n8n_workflow/docs/PROMPTS.md`](n8n_workflow/docs/PROMPTS.md) |
| voir le document de transfert | [`n8n_workflow/docs/HANDOVER.md`](n8n_workflow/docs/HANDOVER.md) |
| importer le workflow dans n8n | [`n8n_workflow/exports/can-my-pc-run-it.json`](n8n_workflow/exports/can-my-pc-run-it.json) |
| relancer les contrôles (lint, validation, 48 tests) | `cd n8n_workflow && npm install && npm run check` |

## Contenu du dépôt

```
eugenia_n8n/
├── n8n_workflow/      ← le livrable
│   ├── README.md      ← à lire d'abord
│   ├── exports/       ← le workflow en JSON, à importer dans n8n
│   ├── n8n/           ← le même workflow en .workflow.ts (n8n-cli) et la configuration du lint
│   ├── docs/          ← prompt, document de transfert, mise en place Notion, captures
│   └── tools/, tests/ ← le générateur du workflow et ses 48 tests (inutile à la première lecture)
└── skills/            ← trois skills Claude Code personnels, sans lien avec le fonctionnement du workflow
```
