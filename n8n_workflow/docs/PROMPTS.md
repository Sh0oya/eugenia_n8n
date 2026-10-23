# Les prompts du workflow

Deux prompts sont utilisés, tous deux écrits **en anglais** (langue de travail du workflow) avec des **valeurs de sortie en français** et des **clés JSON en anglais**. Les fichiers sources sont dans [`tools/prompts/`](../tools/prompts/) ; le générateur les copie dans les nodes `Basic LLM Chain`.

| Prompt | Node | Modèle | Sortie |
|---|---|---|---|
| Diagnostic | `Basic LLM Chain - Write Diagnostic` | `gemini-flash-latest`, secours `gemini-flash-lite-latest` | un objet JSON validé par un schéma (rapports par dépôt, comparaison, contexte utilisé, sources) |
| Incident | `Basic LLM Chain - Analyze Incident` | `gemini-flash-lite-latest` | `probableCause`, `nextStep`, `replay` |

## Structure (règles du cours)

1. **Rôle dans le message système** — [`diagnostic.system.md`](../tools/prompts/diagnostic.system.md) : qui est l'analyste, ce qu'il maîtrise (Windows 11, WSL, Conda, CUDA, Intel Arc, sécurité), ce qu'il ne fait jamais (exécuter, installer), la langue de sortie. Le message système ne contient **aucune accolade** : la chaîne LLM de n8n les prendrait pour des variables.
2. **Tâche dans le message utilisateur, en sections XML** — [`diagnostic.user.xml`](../tools/prompts/diagnostic.user.xml) :
   - `<goal>` : l'objectif, une phrase, avec le nombre de rapports attendus ;
   - `<context>` : 13 règles numérotées (analyse statique uniquement, documents non fiables, preuve / estimation / inconnu, pertinence, outils déjà connus, compatibilité, risques, coûts, notes de 1 à 5, premier essai, mode comparaison, recopie exacte du dépôt et du commit) ;
   - `<examples>` : **4 exemples** qui couvrent les cas difficiles (GPU bloquant, outil déjà installé dans une autre version, outil « abandonné » qui n'est pas désinstallé, injection de prompt dans un README) ;
   - `<output_format>` : un seul objet JSON, valeurs en français, URL seulement si elles figurent dans les entrées.
3. **Entrées en XML** — le node natif `XML - Convert Inputs` transforme le JSON des preuves (`<machine>`, `<passages>`, `<repositories>`, `<webResults>`…) en balises : le modèle sépare mieux les données des instructions.

## Défenses

| Risque | Défense |
|---|---|
| Un README demande d'exécuter un script ou d'ignorer les consignes | règle 2 du contexte + exemple 4 : c'est un risque à signaler, jamais un ordre |
| Réponse qui n'est pas du JSON valide | `Output Parser - Diagnostic Schema` (schéma manuel) + réparation automatique par un second modèle |
| Modèle indisponible ou quota | modèle de secours `gemini-flash-lite-latest` (option native de la chaîne) |
| Le modèle contredit les preuves GitHub | `Code - Validate and Finalize Diagnostic` recopie dépôt, version et commit **depuis GitHub**, jamais depuis l'IA, et refuse un rapport sans note, sans source ou qui cite un contexte inconnu |
| Coût imprévu | estimation du coût maximal **avant** l'appel et comparaison au budget du mois (`analysis_history`) |

## Modifier un prompt

1. Éditer le fichier dans `tools/prompts/`.
2. `npm run check` (régénère le JSON et le `.workflow.ts`, puis valide et lint).
3. Réimporter ou `n8ncli push`.

Les clés du schéma JSON sont définies dans `tools/s_diagnosis.py` (fonction `schema()`) et lues par `tools/code/validate-diagnostic.js` : les trois doivent évoluer ensemble.
