# Plan — workflow n8n « Relances factures »

Construit à partir de la spec `specs/relances-factures-impayees/`.

1. **Déclencheur Schedule** : tous les jours à 9 h 00 (instance n8n, fuseau par défaut du serveur : UTC).
2. **Pennylane — lister les factures** au statut « à payer » (première page de résultats, 100 factures max).
3. **Code** : pour chaque facture, `jours_retard = aujourd'hui - date_echeance` (en jours calendaires).
4. **IF** : `jours_retard == 3` → relance 1 ; `== 10` → relance 2 ; `== 20` → relance 3. Sinon rien.
5. **Gmail — envoyer l'email** depuis compta@ au contact de facturation, avec le numéro, l'échéance, le montant de la facture et le lien de paiement. L'associée en copie pour qu'elle suive.
6. **Google Sheets — tracer** : une ligne par envoi (numéro de facture, numéro de relance, date).
7. **Erreurs** : comportement par défaut de n8n (le workflow s'arrête au premier nœud en erreur).

Mise en service : j'active le workflow demain matin après l'avoir construit.
