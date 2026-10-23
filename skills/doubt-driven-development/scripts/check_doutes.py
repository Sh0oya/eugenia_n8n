#!/usr/bin/env python3
"""
check_doutes.py — contrôle d'un registre des doutes (skill doubt-driven-development).

Usage :
    python check_doutes.py chemin/vers/DOUTES_<sujet>.md

Ce que ce script fait foi — l'agent ne l'affirme pas, il le fait vérifier :

  1. Gabarit       aucun {placeholder} résiduel hors code
  2. Champs        chaque entrée `## Dn — …` porte « Si c'est faux », « Contrat »,
                   « Artefact » et au moins une preuve avec son statut
  3. Preuves       un `[prouvé]` cite sa commande entre accents graves
  4. Tours         trois au plus par entrée ; chaque constat a une confiance et
                   une classe connues
  5. Verdict       valeur connue ; « tient » repose sur une preuve [prouvé] ou [lu] ;
                   « incertain » dit ce qui trancherait
  6. Théâtre       un tour où au moins deux constats de confiance forte ont tous
                   été rangés en « bruit » ou « compromis » est signalé

Une entrée sans verdict est un doute encore ouvert ou en attente : elle est
signalée, pas refusée. Les avertissements n'échouent pas le contrôle.
Code retour : 1 s'il reste au moins une erreur, 0 sinon. Bibliothèque standard seule.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

CLASSES = {"contrat flou", "a corriger", "compromis", "bruit"}
CONFIANCES = {"forte", "moyenne", "faible"}
VERDICTS = {"tient", "tombe", "incertain"}
TOURS_MAX = 3


def norm(texte: str) -> str:
    t = unicodedata.normalize("NFKD", texte)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip().lower()


def sans_code(texte: str) -> str:
    return re.sub(r"```.*?```", "", texte, flags=re.S)


def lignes_de_table(bloc: str) -> list[dict[str, str]]:
    """Lignes du premier tableau du bloc, indexées par en-tête normalisé."""
    lignes = [l.strip() for l in bloc.splitlines() if l.strip().startswith("|")]
    if len(lignes) < 2:
        return []
    entetes = [norm(c) for c in lignes[0].strip("|").split("|")]
    resultat = []
    for brute in lignes[2:]:
        cellules = [c.strip() for c in brute.strip("|").split("|")]
        cellules += [""] * (len(entetes) - len(cellules))
        resultat.append(dict(zip(entetes, cellules)))
    return resultat


def colonne(ligne: dict[str, str], mot: str) -> str:
    return next((v for k, v in ligne.items() if mot in k), "")


def champ(bloc: str, nom: str) -> str | None:
    """Valeur d'un champ « **Nom** : valeur » (la suite de la ligne)."""
    m = re.search(rf"^\*\*{nom}\*\*\s*:\s*(.*)$", bloc, flags=re.M | re.I)
    return m.group(1).strip() if m else None


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    chemin = Path(sys.argv[1])
    if not chemin.exists():
        print(f"✗ fichier introuvable : {chemin}")
        return 2
    texte = sans_code(chemin.read_text(encoding="utf-8"))
    erreurs: list[str] = []
    alertes: list[str] = []

    residus = re.findall(r"\{[^{}\n]{1,160}\}", re.sub(r"`[^`\n]*`", "", texte))
    for residu in residus[:5]:
        erreurs.append(f"[gabarit] placeholder résiduel : {residu[:70]}")
    if len(residus) > 5:
        erreurs.append(f"[gabarit] … et {len(residus) - 5} autre(s)")

    reperes = list(re.finditer(r"^## (D\d+)\s*[—–-]\s*(.+)$", texte, flags=re.M))
    if not reperes:
        erreurs.append("[registre] aucune entrée `## D1 — …`")
    stats = {"entrees": len(reperes), "tient": 0, "tombe": 0, "incertain": 0, "ouverts": 0, "tours": 0}

    for i, m in enumerate(reperes):
        ident, affirmation = m.group(1), m.group(2).strip()
        fin = reperes[i + 1].start() if i + 1 < len(reperes) else len(texte)
        bloc = texte[m.end():fin]

        # 2. Champs obligatoires
        if len(affirmation) < 15:
            erreurs.append(f"[champs] {ident} : affirmation trop courte pour être mise en doute")
        for nom in ("Si c'est faux", "Contrat", "Artefact"):
            valeur = champ(bloc, nom)
            if not valeur:
                erreurs.append(f"[champs] {ident} : « {nom} » absent ou vide")

        # 3. Preuves
        preuves = re.findall(r"^\s*[-*]\s*\[(prouvé|lu|supposé)\](.*)$", bloc, flags=re.M)
        if not preuves:
            erreurs.append(f"[preuves] {ident} : aucune preuve avec son statut ([prouvé], [lu] ou [supposé])")
        for statut, reste in preuves:
            if statut == "prouvé" and "`" not in reste:
                erreurs.append(f"[preuves] {ident} : un [prouvé] sans sa commande entre accents graves")
            if not reste.strip():
                erreurs.append(f"[preuves] {ident} : une preuve [{statut}] vide")
        solides = [s for s, _ in preuves if s in ("prouvé", "lu")]

        # 4. Tours
        tours = list(re.finditer(r"^### Tour (\d+)", bloc, flags=re.M))
        stats["tours"] += len(tours)
        if len(tours) > TOURS_MAX:
            erreurs.append(f"[tours] {ident} : {len(tours)} tours, trois au plus")
        for j, t in enumerate(tours):
            fin_tour = tours[j + 1].start() if j + 1 < len(tours) else len(bloc)
            constats = lignes_de_table(bloc[t.end():fin_tour])
            if not constats:
                alertes.append(f"[tours] {ident} tour {t.group(1)} : aucun constat consigné")
            fortes = []
            for c in constats:
                classe = norm(colonne(c, "classe"))
                confiance = norm(colonne(c, "confiance"))
                if classe not in CLASSES:
                    erreurs.append(f"[tours] {ident} tour {t.group(1)} : classe « {classe} » inconnue "
                                   "(contrat flou · à corriger · compromis · bruit)")
                if confiance not in CONFIANCES:
                    erreurs.append(f"[tours] {ident} tour {t.group(1)} : confiance « {confiance} » inconnue "
                                   "(forte · moyenne · faible)")
                if confiance == "forte":
                    fortes.append(classe)
            # 6. Théâtre du doute
            if len(fortes) >= 2 and all(c in ("bruit", "compromis") for c in fortes):
                alertes.append(f"[théâtre] {ident} tour {t.group(1)} : {len(fortes)} constats de confiance forte, "
                               "tous rangés en bruit ou compromis — revérifie-les dans l'artefact")

        # 5. Verdict : la dernière ligne datée fait foi
        verdicts = re.findall(r"Verdict\s*\**\s*:\s*\**\s*([^\s—–-]+)\s*[—–-]?\s*(.*)$", bloc, flags=re.M | re.I)
        if not verdicts:
            stats["ouverts"] += 1
            alertes.append(f"[verdict] {ident} : pas encore de verdict (doute ouvert ou en attente)")
            continue
        valeur, explication = norm(verdicts[-1][0]), verdicts[-1][1]
        if valeur not in VERDICTS:
            erreurs.append(f"[verdict] {ident} : « {valeur} » inconnu (tient · tombe · incertain)")
            continue
        stats[valeur] += 1
        if valeur == "tient" and not solides:
            erreurs.append(f"[verdict] {ident} : « tient » sans aucune preuve [prouvé] ou [lu]")
        if valeur == "incertain" and not re.search(r"tranch", norm(explication)):
            alertes.append(f"[verdict] {ident} : « incertain » sans dire ce qui trancherait")

    print(f"Contrôle de {chemin.name}\n")
    for e in erreurs:
        print(f"✗ {e}")
    for a in alertes:
        print(f"⚠ {a}")
    print(
        f"\nDoutes : {stats['entrees']} · tient {stats['tient']} · tombe {stats['tombe']}"
        f" · incertain {stats['incertain']} · ouverts {stats['ouverts']} · tours de relecture {stats['tours']}"
    )
    if erreurs:
        print(f"\n✗ {len(erreurs)} erreur(s) — à corriger avant le compte rendu.")
        return 1
    print(f"\n✓ 0 erreur · {len(alertes)} avertissement(s) à traiter ou assumer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
