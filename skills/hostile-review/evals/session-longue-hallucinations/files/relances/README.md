# Relances factures

Script quotidien qui relance les clients dont une facture est échue : J+3, J+10, J+20.

- Dédoublonnage : une facture ne reçoit jamais deux fois la même relance.
- Jours fériés et week-ends gérés : une relance due un jour non ouvré part le jour ouvré suivant.
- Mode test : en dehors de `MODE = "prod"`, rien n'est envoyé.

Lancer : `python relances.py`
