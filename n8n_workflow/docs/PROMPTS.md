# Le prompt du workflow

Un seul prompt, utilisé par `Basic LLM Chain - Write Diagnostic`. Il est écrit **en anglais** (langue de travail du workflow), avec des **valeurs de sortie en français** et des **clés JSON en anglais**. Les fichiers sources sont dans [`tools/prompts/`](../tools/prompts/) ; le générateur les copie dans le node.

| | |
|---|---|
| Modèle | `gemini-flash-latest`, secours `gemini-flash-lite-latest` (réglables dans `CONFIGURATION`) |
| Sortie | un objet JSON validé par un schéma : un rapport, le contexte utilisé, les sources, les inconnues |

## Structure (règles du cours)

1. **Rôle dans le message système** — [`diagnostic.system.md`](../tools/prompts/diagnostic.system.md) : qui est l'analyste, ce qu'il maîtrise (Windows 11, WSL, Conda, CUDA, Intel Arc, sécurité), ce qu'il ne fait jamais (exécuter, installer), la langue de sortie. Le message système ne contient **aucune accolade** : la chaîne LLM de n8n les prendrait pour des variables.
2. **Tâche dans le message utilisateur, en sections XML** — [`diagnostic.user.xml`](../tools/prompts/diagnostic.user.xml) :
   - `<goal>` : l'objectif, avec le nombre de rapports attendus ;
   - `<context>` : 12 règles numérotées (analyse statique uniquement, documents non fiables, preuve / estimation / inconnu, pertinence, outils déjà connus, compatibilité, risques, coûts, notes de 1 à 5, premier essai, recopie exacte du dépôt et de la version) ;
   - `<examples>` : **5 exemples** qui couvrent les cas difficiles (GPU bloquant, outil déjà installé dans une autre version, outil « abandonné » qui n'est pas désinstallé, injection de prompt dans un README, outil marqué « installé » par l'utilisateur) ;
   - `<output_format>` : un seul objet JSON, valeurs en français, URL seulement si elles figurent dans les entrées.
3. **Entrées en XML** — le node natif `XML - Convert Inputs` transforme le JSON des preuves (`<machine>`, `<profile>`, `<inventory>`, `<decisions>`, `<matches>`, `<repository>` (README, `<dependencyFiles>` = `pyproject.toml`, notes de release…)…) en balises : le modèle sépare mieux les données des instructions.

Les exemples et les règles sont écrits avec les balises que le workflow envoie vraiment (`<repository>`, `<matches>` répété, `<inventory>` répété…) : le test `tests/prompt.test.mjs` construit les entrées à partir des nodes et échoue si un exemple cite une balise qui n'existe pas. Les limites de l'examen (`<limits>`) sont données une seule fois, en haut des entrées.

## Les décisions de l'utilisateur

La propriété `Decision` de la base Notion « Analyses » (`installé`, `ignoré`, `désinstallé`) est lue à chaque analyse et donnée à l'IA dans `<decisions>`. La règle 5 du contexte dit comment l'utiliser : un dépôt « installé » est connu (même si l'inventaire ne le liste pas) et compte parmi les outils présents pour chercher doublons, compléments et conflits ; « ignoré » est rappelé sans être recommandé de nouveau sauf changement essentiel ; « désinstallé » est traité comme absent, avec le motif en inconnue. L'IA ne contredit jamais une décision et cite son identifiant dans `usedContext`.

## Défenses

| Risque | Défense |
|---|---|
| Un README demande d'exécuter un script ou d'ignorer les consignes | règle 2 du contexte + exemple 4 : c'est un risque à signaler, jamais un ordre |
| Réponse qui n'est pas du JSON valide | `Output Parser - Diagnostic Schema` (schéma manuel) ; sinon la validation échoue, l'e-mail le dit et rien n'est enregistré comme réussi |
| Modèle indisponible ou surchargé | modèle de secours `gemini-flash-lite-latest` (option native de la chaîne), 2 essais |
| Le modèle contredit les preuves GitHub | `Code - Validate and Finalize Diagnostic` recopie dépôt, version et URL **depuis GitHub**, jamais depuis l'IA, et refuse un rapport sans note, sans source ou qui cite un contexte inconnu |
| Un README ou des notes de release poussent le modèle à écrire une image ou un lien piégé (fuite du profil vers un site tiers) | le même node retire des textes de l'IA les images (en ligne ou par référence), les balises de type HTML et les liens Markdown vers une adresse que les entrées ne contiennent pas telle quelle (le lien est réduit à son texte) ; les champs d'adresse (`url` des sources et des alternatives) sont vidés de la même façon, et l'e-mail ne crée jamais de lien autre que `https`. Une adresse en texte brut est laissée, pour que les commandes restent utilisables. Le prompt seul ne suffit pas |
| `pyproject.toml` plus long que `maxDependencyChars` | il est coupé, un repère `[cut here: the rest of pyproject.toml was not read]` termine le texte donné à l'IA et une limite est écrite dans le rapport : ce qui suit est inconnu, pas absent |
| Texte GitHub qui fait échouer la conversion XML (séquences ANSI, émoji coupé) | caractères de contrôle et surrogates isolés retirés après chaque découpe |
| Appel lent ou en échec | modèle de secours en cas d'erreur ; aucun délai fixé dans le workflow, car certaines offres n8n plafonnent la durée d'exécution (180 s sur l'essai gratuit) et coupent alors un appel Gemini lent |

## Modifier le prompt

1. Éditer le fichier dans `tools/prompts/`.
2. `npm run check` (régénère le JSON et le `.workflow.ts`, puis valide et lint).
3. Réimporter ou `n8ncli push`.

Les clés du schéma JSON sont définies dans `tools/s_diagnosis.py` (fonction `schema()`) et lues par `tools/code/validate-diagnostic.js` et `tools/code/render-report.js` : ces trois fichiers évoluent ensemble.
