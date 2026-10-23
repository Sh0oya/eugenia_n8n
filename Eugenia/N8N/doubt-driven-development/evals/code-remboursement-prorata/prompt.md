---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, Agent]
---

J'ai écrit le calcul du remboursement au prorata pour les résiliations (remboursement.py), les tests sont verts. Règle métier : on rembourse les jours non consommés de la période en cours ; le jour de la résiliation est consommé ; le montant est arrondi au centime le plus proche, le demi-centime arrondi au-dessus. Tu peux vérifier avant que je merge ? Ça part en prod vendredi et ça touche de l'argent.

Input files: remboursement.py, test_remboursement.py
