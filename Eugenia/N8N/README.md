# Skills Claude — Eugenia / N8N

Trois skills Claude Code, en français, qui se complètent et fonctionnent aussi
chacun seul.

| Skill | Rôle | Quand |
| --- | --- | --- |
| [`spec-beton`](spec-beton/SKILL.md) | Interroge par lots de questions (chacune avec une réponse recommandée) jusqu'à une spec sans trou : problème avant solution, cas limites, hypothèses visibles, contrôle par script et relecture à froid. | Avant de construire |
| [`doubt-driven-development`](doubt-driven-development/SKILL.md) | Fait douter Claude de sa compréhension et de ses décisions à risque, prouve par l'exécution, présente chaque erreur avec sa correction avant d'y toucher. | Pendant le travail |
| [`hostile-review`](hostile-review/SKILL.md) | Revue par trois relecteurs neufs qui n'ont pas vu la conversation : vérifie les affirmations de Claude, refuse le « LGTM » gratuit, livre verdict, plan de reprise et fichier de relais. | Quand la session dérive, ou sur demande |

## Installer

Copier chaque dossier dans `~/.claude/skills/` (sans le dossier `evals/`, qui ne
sert qu'aux tests) :

```bash
cp -r spec-beton doubt-driven-development hostile-review ~/.claude/skills/
```

Les scripts de contrôle (`scripts/*.py`) n'utilisent que la bibliothèque
standard de Python 3.9 ou plus.

## Tests

Chaque skill a ses cas de test dans `evals/`, au format de
`claude plugin eval`. Le mot de passe présent dans
`hostile-review/evals/session-longue-hallucinations/files/relances/config.py`
est **faux** : c'est l'un des défauts plantés que la revue doit trouver.
