# Rédiger la spec

Phase 5. Pars de `assets/gabarit-spec.md`. Avant ta première spec, lis
`assets/exemple-spec.md` une fois : il montre le niveau attendu mieux que
n'importe quelle consigne.

Les sections `## 0 -` à `## 11 -` sont un **contrat machine** : le script les
trouve par numéro et par mot-clé. Renuméroter les phases du §6 est sûr ;
supprimer une section ne l'est pas. Une section sans matière porte une ligne
qui le dit (« Aucun — le projet ne crée aucune donnée ») : une section vide et
assumée bat une section remplie pour faire bien.

## Ce qu'est une règle

Un **comportement observable** et un **cas de test distinct**. Trois choses y
ressemblent sans en être :

- le **chapeau**, qui annonce les règles suivantes sans exigence propre → une
  phrase d'introduction de section ;
- le **doublon**, déjà énoncé ailleurs → supprimé ;
- la **conséquence**, dérivable d'une autre règle → une puce sous cette règle.

### Le quoi, jamais le comment

Une règle dit **ce qui doit être vrai**, jamais **par quel moyen**. Le test,
avant d'écrire : *une autre implémentation, au comportement observable
identique, violerait-elle cette règle ?* Si oui, la règle surspécifie : réécris
l'exigence et laisse le moyen au constructeur.

Un choix technique **imposé** par le contexte (l'outil déjà en place, la
plateforme exigée par le client) va au §3 « Contraintes imposées », pas dans
les règles. Un choix technique **non imposé** ne va nulle part dans la spec.

### Format

```markdown
**R07 — Une facture toujours impayée 7 jours après sa relance 3 passe en escalade.** Précisions. → **NOUVEAU**.
- détail de la règle, en puce collée au paragraphe
```

L'ancre ouvre, le type ferme, toujours au même endroit. Une règle par
paragraphe, jamais en puce.

- **Numérotation plate et append-only** : `R01`, `R02`… Une règle insérée
  après coup prend un suffixe (`R03b`) ; un numéro retiré ne se réutilise
  jamais, il désignerait une autre règle dans les tests déjà écrits.
- **Type**, un parmi cinq :

| Type | Sens pour le constructeur |
| --- | --- |
| `NOUVEAU` | à construire |
| `EXISTANT (invariant)` | existe déjà et doit rester vrai après le changement |
| `EXISTANT (périmètre)` | existe déjà, ne pas y toucher |
| `DÉPENDANCE` | assuré par un tiers ou un autre système : la règle dit ce qu'on attend de lui |
| `À TRANCHER` | décision attendue — un point ouvert du §11 la cite |

Un `EXISTANT` qualifié tient en une ligne de synthèse, sans paragraphe : on ne
re-spécifie pas ce qu'on ne touche pas.

- **Lot**, décidé en écrivant la règle : `nominal` (acteur bien configuré,
  données valides, tout disponible) ou `limite` (absent, vide, refus, conflit,
  concurrence, panne, droit manquant). Un cas limite reste **dans la phase de sa
  règle**, sous `#### Cas limites`, jamais regroupé en fin de document. Une spec
  presque sans règle `limite` n'a pas été interrogée, elle a été recopiée.

## Écrire

Quatre tournures couvrent presque toutes les règles et forcent à nommer le
déclencheur ou la condition :

- **Quand** {déclencheur}, {résultat observable}.
- **Si** {situation indésirable}, **alors** {résultat observable}.
- **Tant que** {état}, {résultat observable}.
- {Acteur ou objet} {résultat observable}, sans condition.

Ensuite :

- **Chaque action nomme son geste déclencheur** : bouton, étiquette posée,
  réponse à un email, événement reçu. Geste non tranché ⇒ point ouvert.
- **Chaque calcul porte un exemple non rond** avec son arrondi : 2 340,00 € dont
  1 000,00 € réglés affiche 1 340,00 €.
- **Chaque seuil, délai ou volume a un chiffre.** « Rapide », « simple »,
  « intuitif », « correctement », « si possible » ne se vérifient pas : le
  script les signale.
- **Un objet à cycle de vie a son tableau d'états** au §7 : état, ce qui est
  visible, ce qu'on peut faire, transitions. Les règles y renvoient.
- **Un terme se définit au glossaire avant d'être employé**, et un concept garde
  un seul nom d'un bout à l'autre : « client », « compte » et « utilisateur »
  pour la même chose, c'est trois objets pour le lecteur.
- **Une hypothèse se cite** : une règle qui repose sur une hypothèse par défaut
  la nomme, « (H1) », et H1 figure au §10 avec ce qui change si elle est fausse.
- **Une hypothèse comble un trou, elle n'en crée pas.** Elle se justifie quand
  une supposition fausse changerait un comportement observable. Ce que le
  constructeur peut décider seul sans changer ce que voit l'utilisateur (l'heure
  exacte d'un traitement de nuit, le nom d'une propriété) n'en est pas une ; une
  fonctionnalité nouvelle non plus. Au-delà d'une quinzaine d'hypothèses, relis
  la liste : la moitié est souvent du comment ou du périmètre ajouté.
- **Les messages se scindent** : l'information à porter est une règle, la
  formulation exacte est du contenu.

### Ce qui ne s'écrit pas

- **L'implicite** : « la fiche est enregistrée quand on clique sur Enregistrer ».
- **Le standard des outils** : un champ obligatoire refuse le vide, une liste se
  trie, une fenêtre se ferme avec Échap. Les écrire gonfle le périmètre et fait
  tester deux fois ce que personne ne va coder.
- **Le pourquoi justificatif.** Le pourquoi **normatif**, qui conditionne
  l'exigence, se replie dans l'énoncé. Le pourquoi **justificatif**, qui défend
  une décision ou l'alternative écartée, va au JOURNAL. Test : *si je retire ce
  paragraphe, la règle devient-elle moins exigeante, ou seulement moins
  argumentée ?*
- **L'historique** : « corrigé le », « anciennement », « suite à la remarque
  de » appartiennent au journal. La spec dit la vérité au présent.
- **La dérivée d'un autre objet** : « calqué sur l'écran X », « comme le
  formulaire actuel ». Le lecteur ne doit pas avoir à connaître autre chose pour
  comprendre ceci : décris la cible pour elle-même.

## Avant / après

Un agent reproduit un exemple mieux qu'il ne respecte une interdiction.

| ❌ | ✅ |
| --- | --- |
| L'application doit être rapide et intuitive. | La liste des 200 derniers tickets s'affiche en moins de 2 s. |
| Stocker les leads dans une table Supabase avec un champ `status`. | Chaque lead garde son état (nouveau, contacté, gagné, perdu) et l'historique de ses changements d'état. |
| Gérer les erreurs d'envoi correctement. | Après trois échecs d'envoi, le lead passe « à traiter » et le commercial référent reçoit un email qui nomme le lead et l'erreur. |
| Le bot répond aux questions des clients. | Le bot répond uniquement à partir de la FAQ fournie ; une question hors FAQ reçoit une réponse de transfert et crée un ticket pour l'équipe. |
| Reprendre le formulaire du site actuel. | Le formulaire demande nom, email, entreprise (facultative) et besoin (texte libre, 1 000 caractères au plus). |
| *Pourquoi J+3 : on a hésité avec J+5 parce que…* | *(rien dans la spec : le justificatif va au journal)* |

## Les options écartées s'archivent

Toute option envisagée puis écartée — alternative, périmètre plus large,
proposition de l'agent refusée — va au JOURNAL sous
`## Options écartées — AAAA-MM-JJ`, avec son motif et qui a tranché. Ce qui est
retenu vit dans la spec ; ce qui est refusé ne vit nulle part ailleurs, et un
lecteur qui n'a pas assisté à la discussion le reproposera.
