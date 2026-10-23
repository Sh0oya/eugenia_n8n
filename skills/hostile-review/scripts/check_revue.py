#!/usr/bin/env python3
"""
check_revue.py — contrôle d'un fichier de revue hostile (skill hostile-review).

Usage :
    python check_revue.py revues/REVUE_AAAA-MM-JJ.md

Ce que ce script fait foi :

  1. Gabarit       aucun {placeholder} résiduel
  2. Verdict       un des trois : à reprendre · tient, avec réserves · rien de cassé
  3. Affirmations  statut connu ; une affirmation confirmée ou démentie cite sa preuve
  4. Coups         gravité et statut connus ; endroit, scénario et correction renseignés ;
                   aucun coup « non reproduit » dans le tableau
  5. Cohérence     bloquant confirmé ⇒ « à reprendre » ; sinon majeur ⇒ « avec réserves » ;
                   sinon « rien de cassé »
  6. Mérite        « rien de cassé » exige les attaques tentées et l'hypothèse la plus fragile
  7. Reprise       des coups au rapport ⇒ un plan de reprise
  8. Ton           aucune formule de complaisance (LGTM, « ça a l'air bon »…)

Code retour : 1 s'il reste au moins une erreur, 0 sinon. Bibliothèque standard seule.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

VERDICTS = {"a reprendre": "reprendre", "tient, avec reserves": "reserves", "tient avec reserves": "reserves",
            "rien de casse": "rien"}
GRAVITES = {"bloquant", "majeur", "mineur"}
STATUTS_COUP = {"confirme", "incertain"}
STATUTS_AFF = {"confirmee", "dementie", "invérifiable", "inverifiable"}
COMPLAISANCE = r"\bLGTM\b|[çc]a a l'air bon|globalement solide|bon travail|quelques petits points|beau travail|looks good"


def norm(texte: str) -> str:
    t = unicodedata.normalize("NFKD", texte)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip().lower().strip("*").strip()


def section(texte: str, titre: str) -> str:
    m = re.search(rf"^## {titre}.*?$(.*?)(?=^## |\Z)", texte, flags=re.M | re.S | re.I)
    return m.group(1) if m else ""


def table(bloc: str) -> list[dict[str, str]]:
    lignes = [l.strip() for l in bloc.splitlines() if l.strip().startswith("|")]
    if len(lignes) < 2:
        return []
    entetes = [norm(c) for c in lignes[0].strip("|").split("|")]
    out = []
    for brute in lignes[2:]:
        cellules = [c.strip() for c in brute.strip("|").split("|")]
        cellules += [""] * (len(entetes) - len(cellules))
        out.append(dict(zip(entetes, cellules)))
    return out


def col(ligne: dict[str, str], mot: str) -> str:
    return next((v for k, v in ligne.items() if mot in k), "")


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
    texte = re.sub(r"```.*?```", "", chemin.read_text(encoding="utf-8"), flags=re.S)
    erreurs: list[str] = []
    alertes: list[str] = []

    for residu in re.findall(r"\{[^{}\n]{1,160}\}", re.sub(r"`[^`\n]*`", "", texte))[:5]:
        erreurs.append(f"[gabarit] placeholder résiduel : {residu[:70]}")

    m = re.search(r"\*\*(À reprendre|A reprendre|Tient,? avec réserves|Rien de cassé)\.?\*\*", section(texte, "Verdict"), re.I)
    verdict = VERDICTS.get(norm(m.group(1)).rstrip(".")) if m else None
    if not verdict:
        erreurs.append("[verdict] absent ou inconnu (à reprendre · tient, avec réserves · rien de cassé)")

    affirmations = table(section(texte, "Affirmations"))
    dementies = 0
    for a in affirmations:
        statut = norm(col(a, "statut"))
        if statut not in STATUTS_AFF:
            erreurs.append(f"[affirmations] {col(a, '#')} : statut « {statut} » inconnu")
        if statut in ("confirmee", "dementie") and not col(a, "preuve"):
            erreurs.append(f"[affirmations] {col(a, '#')} : {statut} sans preuve")
        dementies += statut == "dementie"

    coups = table(section(texte, "Coups"))
    bloquants = majeurs = 0
    for c in coups:
        ident, gravite, statut = col(c, "#"), norm(col(c, "gravit")), norm(col(c, "statut"))
        if gravite not in GRAVITES:
            erreurs.append(f"[coups] {ident} : gravité « {gravite} » inconnue")
        if statut not in STATUTS_COUP:
            erreurs.append(f"[coups] {ident} : statut « {statut} » — seuls les coups confirmés ou incertains entrent au rapport")
        for champ, mot in (("endroit", "endroit"), ("scénario", "scenario"), ("correction", "correction")):
            if not col(c, mot):
                erreurs.append(f"[coups] {ident} : {champ} vide")
        bloquants += gravite == "bloquant" and statut == "confirme"
        majeurs += gravite == "majeur" or (gravite == "bloquant" and statut == "incertain")

    attendu = "reprendre" if bloquants else "reserves" if majeurs else "rien"
    if verdict and verdict != attendu:
        if not (verdict == "reprendre" and dementies):
            erreurs.append(f"[cohérence] verdict « {m.group(1)} » alors que les coups donnent « "
                           f"{ {'reprendre': 'à reprendre', 'reserves': 'tient, avec réserves', 'rien': 'rien de cassé'}[attendu]} »")
    if verdict == "rien" and dementies:
        alertes.append(f"[cohérence] « rien de cassé » avec {dementies} affirmation(s) démentie(s) : est-ce vraiment sans conséquence ?")

    attaques = section(texte, "Attaques tentées").strip()
    fragile = section(texte, "Hypothèse la plus fragile").strip()
    if verdict == "rien":
        items = len(re.findall(r"^\s*[-*\d]", attaques, flags=re.M)) + attaques.count(",") + attaques.count(";")
        if items < 3:
            erreurs.append("[mérite] « rien de cassé » sans la liste des attaques tentées")
        if not fragile:
            erreurs.append("[mérite] « rien de cassé » sans l'hypothèse la plus fragile")
    elif not attaques:
        alertes.append("[mérite] attaques tentées non listées")

    if coups and not section(texte, "Plan de reprise").strip():
        erreurs.append("[reprise] des coups au rapport, mais aucun plan de reprise")

    for formule in sorted({x.group(0) for x in re.finditer(COMPLAISANCE, texte, flags=re.I)}):
        erreurs.append(f"[ton] formule de complaisance : « {formule} »")

    print(f"Contrôle de {chemin.name}\n")
    for e in erreurs:
        print(f"✗ {e}")
    for a in alertes:
        print(f"⚠ {a}")
    print(f"\nVerdict : {m.group(1) if m else '—'} · coups : {len(coups)} ({bloquants} bloquant(s) confirmé(s))"
          f" · affirmations : {len(affirmations)} ({dementies} démentie(s))")
    if erreurs:
        print(f"\n✗ {len(erreurs)} erreur(s) — à corriger avant de présenter la revue.")
        return 1
    print(f"\n✓ 0 erreur · {len(alertes)} avertissement(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
