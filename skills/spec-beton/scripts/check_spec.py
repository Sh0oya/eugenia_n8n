#!/usr/bin/env python3
"""
check_spec.py — contrôle mécanique d'une spec produite avec le skill spec-beton.

Usage :
    python check_spec.py specs/<slug>/SPEC_<slug>.md [specs/<slug>/JOURNAL_<slug>.md]

Ce que ce script fait foi — l'agent ne l'affirme pas, il le fait vérifier :

   1. Frontmatter   champs présents, valeurs connues
   2. Structure     sections `## 0 -` à `## 11 -`, dans l'ordre, sans trou
   3. Gabarit       aucun {placeholder} résiduel hors code
   4. Bandeau       présent si et seulement si solidite_besoin = hypothétique
   5. Preuves       chaque preuve du §1 porte un statut ; tout [observé] est daté
   6. Règles        ancre **Rn — …** et marqueur → **TYPE** dans le même paragraphe,
                    identifiants uniques, types connus, aucune règle posée en puce
   7. Synthèse      corps et §9 désignent les mêmes règles, avec le même type ;
                    lot nominal ou limite
   8. Phases        chaque phase du §6 ouvre par sa ligne Acteur · Moment et porte
                    au moins une règle
   9. Transverses   verdicts connus, `impacté` cite une règle, socle complet
  10. Renvois       les R et H cités existent
  11. Indicateurs   1 à 5, valeur de départ et cible renseignées
  12. Reports       chaque élément « Renvoyé à plus tard » porte sa condition de retour
  13. Statut        `validé` ⇒ ni À TRANCHER, ni point BLOQUANT ou structurant
                    ouvert, ni TODO
  14. Journal       chaque question Qn a sa destination, et ce qu'elle cite existe

Les avertissements n'échouent pas le contrôle : ils se traitent ou s'assument.
Code retour : 1 s'il reste au moins une erreur, 0 sinon. Bibliothèque standard seule.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

SECTIONS = [
    (0, "cadrage"),
    (1, "probleme"),
    (2, "objectif"),
    (3, "perimetre"),
    (4, "acteur"),
    (5, "transverse"),
    (6, "parcours"),
    (7, "donnee"),
    (8, "non fonctionnel"),
    (9, "synthese"),
    (10, "hypothese"),
    (11, "points ouverts"),
]

STATUTS = {"brouillon", "propose", "valide"}
SOLIDITES = {"etabli", "declare", "hypothetique"}
PROFONDEURS = {"beton", "express"}
TYPES = {"NOUVEAU", "EXISTANT (INVARIANT)", "EXISTANT (PERIMETRE)", "DEPENDANCE", "A TRANCHER"}
LOTS = {"nominal", "limite", "edge"}
VERDICTS = {"impacte", "non impacte", "hors-lot", "hors lot"}
CRITICITES = {"bloquant", "structurant", "modalite"}

# Domaines du socle, balayés sur tout projet : un motif par domaine.
SOCLE = {
    "acteurs, rôles & droits": r"droit|role|permission",
    "paramétrage & activation": r"parametrage|activation|configuration",
    "cycle de vie des données": r"creation|suppression|conservation|modification",
    "données personnelles": r"personnel|confidential|rgpd",
    "erreurs & mode dégradé": r"erreur|degrade|indisponib|panne",
    "notifications": r"notification|communication|alerte",
    "historique & effet sur le passé": r"historique|tracabilite|passe|audit",
    "volume & délais": r"volume|frequence|delai|charge",
    "reprise de l'existant": r"reprise|migration|existant",
}

MOTS_TECHNIQUES = (
    r"\b(API|endpoint|base de donn[ée]es|SQL|JSON|cache|soft[- ]?delete|cron|microservice|"
    r"framework|React|Vue|Supabase|Postgres(?:QL)?|MongoDB|Redis|Lambda|Docker|"
    r"requ[êe]te HTTP|HTTP|POST|GET|table [a-z_]+|colonne|cl[ée] [ée]trang[èe]re|index)\b"
)
MOTS_VAGUES = (
    r"\b(rapide(?:ment)?|simple(?:ment)?|intuiti(?:f|ve)|facile(?:ment)?|convivial|optimal|"
    r"etc\.?|si possible|[ée]ventuellement|appropri[ée]e?s?|correctement|user[- ]friendly|"
    r"ergonomique|performant|robuste|fluide)\b"
)
MOTS_CALCUL = r"\b(calcul|arrondi|total|montant|somme|moyenne|pourcentage|taux|prorata|remise|tva)\b|%"
MOTS_A_FINIR = r"\b(TODO|TBD|FIXME|à définir|à préciser|à compléter)\b|\?\?\?"
CONDITION_RETOUR = r"revient si|\bsi\b|quand|d[èe]s que|lorsque|condition|apr[èe]s|une fois"


def norm(texte: str) -> str:
    """Minuscules, sans accents, espaces compactés."""
    t = unicodedata.normalize("NFKD", texte)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip().lower()


def sans_code(texte: str) -> str:
    """Retire les blocs de code et le code en ligne, qui ne sont pas contrôlés."""
    texte = re.sub(r"```.*?```", "", texte, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", texte)


def id_norm(ident: str) -> str:
    """R01 et R1 désignent la même règle ; R3b reste R3b."""
    m = re.fullmatch(r"([RHPIN])0*(\d+)([a-z]?)", ident)
    return f"{m.group(1)}{m.group(2)}{m.group(3)}" if m else ident


def frontmatter(texte: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", texte, flags=re.S)
    if not m:
        return {}, texte
    champs = {}
    for ligne in m.group(1).splitlines():
        if ":" in ligne:
            cle, val = ligne.split(":", 1)
            champs[cle.strip()] = val.split(" #", 1)[0].strip()
    return champs, texte[m.end():]


def decouper(corps: str) -> dict[int, tuple[str, str]]:
    """{numéro: (titre, contenu)} pour chaque section `## n - titre`."""
    sections: dict[int, tuple[str, str]] = {}
    reperes = list(re.finditer(r"^## (\d+)\s*[-—–.]\s*(.+)$", corps, flags=re.M))
    for i, m in enumerate(reperes):
        fin = reperes[i + 1].start() if i + 1 < len(reperes) else len(corps)
        sections[int(m.group(1))] = (m.group(2).strip(), corps[m.end():fin])
    return sections


def sous_bloc(contenu: str, mot_cle: str) -> str | None:
    """Contenu d'un `### …` dont le titre contient mot_cle (normalisé)."""
    reperes = list(re.finditer(r"^### (.+)$", contenu, flags=re.M))
    for i, m in enumerate(reperes):
        if mot_cle in norm(m.group(1)):
            fin = reperes[i + 1].start() if i + 1 < len(reperes) else len(contenu)
            return contenu[m.end():fin]
    return None


def tables(bloc: str) -> list[list[dict[str, str]]]:
    """Chaque tableau markdown du bloc, en lignes indexées par en-tête normalisé."""
    resultat, courant = [], []
    for ligne in bloc.splitlines() + [""]:
        if ligne.strip().startswith("|"):
            courant.append(ligne.strip())
            continue
        if len(courant) >= 2:
            entetes = [norm(c) for c in courant[0].strip("|").split("|")]
            lignes = []
            for brute in courant[2:]:
                cellules = [c.strip() for c in brute.strip("|").split("|")]
                cellules += [""] * (len(entetes) - len(cellules))
                lignes.append(dict(zip(entetes, cellules)))
            resultat.append(lignes)
        courant = []
    return resultat


def colonne(ligne: dict[str, str], *mots: str) -> str:
    """Valeur de la première colonne dont l'en-tête contient l'un des mots."""
    for entete, valeur in ligne.items():
        if any(mot in entete for mot in mots):
            return valeur
    return ""


def famille(type_brut: str) -> str:
    t = norm(type_brut).upper().rstrip(".")
    for connu in sorted(TYPES, key=len, reverse=True):
        if t.startswith(connu):
            return connu
    return t


class Rapport:
    def __init__(self) -> None:
        self.erreurs: list[str] = []
        self.alertes: list[str] = []

    def err(self, controle: str, message: str) -> None:
        self.erreurs.append(f"[{controle}] {message}")

    def alerte(self, controle: str, message: str) -> None:
        self.alertes.append(f"[{controle}] {message}")


def analyser_spec(texte: str, r: Rapport) -> dict:
    fm, corps = frontmatter(texte)
    propre = sans_code(corps)

    # 1. Frontmatter
    if not fm:
        r.err("frontmatter", "absent : la spec commence par un bloc --- … ---")
    for champ in ("slug", "titre", "date", "statut", "solidite_besoin", "profondeur", "lecteur"):
        if not fm.get(champ):
            r.err("frontmatter", f"champ `{champ}` manquant ou vide")
    statut = norm(fm.get("statut", ""))
    solidite = norm(fm.get("solidite_besoin", ""))
    profondeur = norm(fm.get("profondeur", ""))
    if fm.get("statut") and statut not in STATUTS:
        r.err("frontmatter", f"statut `{fm['statut']}` inconnu (brouillon · proposé · validé)")
    if fm.get("solidite_besoin") and solidite not in SOLIDITES:
        r.err("frontmatter", f"solidite_besoin `{fm['solidite_besoin']}` inconnue (établi · déclaré · hypothétique)")
    if fm.get("profondeur") and profondeur not in PROFONDEURS:
        r.err("frontmatter", f"profondeur `{fm['profondeur']}` inconnue (béton · express)")
    valide = statut == "valide"

    # 2. Structure
    sections = decouper(corps)
    attendus = [n for n, _ in SECTIONS]
    trouves = list(sections)
    if trouves != sorted(trouves) or sorted(trouves) != attendus:
        manquants = [n for n in attendus if n not in sections]
        if manquants:
            r.err("structure", f"sections manquantes : {', '.join(f'§{n}' for n in manquants)}")
        if trouves != sorted(trouves):
            r.err("structure", "sections dans le désordre")
    for n, mot in SECTIONS:
        if n in sections and mot not in norm(sections[n][0]):
            r.err("structure", f"§{n} « {sections[n][0]} » : le titre doit contenir « {mot} » (contrat machine)")

    # 3. Gabarit
    residus = [m.group(0) for m in re.finditer(r"\{[^{}\n]{1,160}\}", propre)]
    for residu in residus[:5]:
        r.err("gabarit", f"placeholder résiduel : {residu[:70]}")
    if len(residus) > 5:
        r.err("gabarit", f"… et {len(residus) - 5} autre(s) placeholder(s) résiduel(s)")
    if "<!--" in propre:
        r.alerte("gabarit", "commentaire HTML résiduel : le retirer")

    # 4. Bandeau
    bandeau = re.search(r"^>\s*⚠️.*hypoth", propre, flags=re.M | re.I)
    if solidite == "hypothetique" and not bandeau:
        r.err("bandeau", "solidite_besoin = hypothétique : le bandeau ⚠️ doit ouvrir le document")
    if solidite in {"etabli", "declare"} and bandeau:
        r.err("bandeau", "bandeau « besoin hypothétique » présent alors que le besoin est " + fm["solidite_besoin"])

    def contenu(n: int) -> str:
        return sans_code(sections.get(n, ("", ""))[1])

    # 5. Preuves
    preuves = sous_bloc(contenu(1), "preuve")
    lignes_preuves = [l for t in tables(preuves or "") for l in t]
    if preuves is None or not lignes_preuves:
        r.err("preuves", "§1 « Preuves » absent ou vide : au moins une ligne, même `[hypothèse]`")
    for ligne in lignes_preuves:
        brut = " ".join(ligne.values())
        if not re.search(r"\[(observé|déclaré|hypothèse)\]", brut):
            r.err("preuves", f"ligne sans statut de preuve : {brut[:70]}")
        if "[observé]" in brut and not re.search(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}", brut):
            r.err("preuves", f"`[observé]` sans date : {brut[:70]}")
    if solidite == "etabli" and not any("[observé]" in " ".join(l.values()) for l in lignes_preuves):
        r.err("preuves", "besoin `établi` sans aucune preuve `[observé]` : passer à `déclaré`")

    # 6. Règles du corps
    corps_regles: dict[str, str] = {}
    texte_regles: dict[str, str] = {}
    for n, (titre, cont) in sections.items():
        cont = sans_code(cont)
        for para in re.split(r"\n\s*\n", cont):
            for m in re.finditer(r"^\s*[-*]\s+\*\*(R\d{1,3}[a-z]?)\s*[—–-]", para, flags=re.M):
                r.err("règles", f"{m.group(1)} posée en puce : une règle est un paragraphe")
            ancres = re.findall(r"\*\*(R\d{1,3}[a-z]?)\s*[—–-]\s+[^*]+\*\*", para)
            if not ancres:
                continue
            if n != 6:
                r.alerte("règles", f"{', '.join(ancres)} ancrée(s) hors du §6")
            marqueurs = re.findall(r"(?:→|->)\s*\*\*([^*]+)\*\*", para)
            if len(ancres) > 1:
                r.err("règles", f"{', '.join(ancres)} dans le même paragraphe : une règle par paragraphe")
            for ident in ancres:
                cle = id_norm(ident)
                if cle in corps_regles:
                    r.err("règles", f"{ident} ancrée deux fois")
                if not marqueurs:
                    r.err("règles", f"{ident} sans marqueur `→ **TYPE**.` dans son paragraphe")
                    corps_regles[cle] = "?"
                else:
                    fam = famille(marqueurs[-1])
                    if fam not in TYPES:
                        r.err("règles", f"{ident} : type « {marqueurs[-1]} » inconnu")
                    corps_regles[cle] = fam
                texte_regles[cle] = para

    # 8. Phases du §6
    cont6 = contenu(6)
    phases = list(re.finditer(r"^### (.+)$", cont6, flags=re.M))
    if not phases:
        r.err("phases", "§6 sans aucune phase `### …`")
    for i, m in enumerate(phases):
        fin = phases[i + 1].start() if i + 1 < len(phases) else len(cont6)
        bloc = cont6[m.end():fin]
        premiere = next((l for l in bloc.splitlines() if l.strip()), "")
        if not re.search(r"\*\*Acteur\*\*.*\*\*Moment\*\*", premiere):
            r.err("phases", f"« {m.group(1)} » n'ouvre pas par `> **Acteur** : … · **Moment** : …`")
        if not re.search(r"\*\*R\d{1,3}[a-z]?\s*[—–-]", bloc):
            r.err("phases", f"« {m.group(1)} » ne porte aucune règle : supprimer la phase")
    for m in re.finditer(r"^#### (.+)$", cont6, flags=re.M):
        if "cas limite" not in norm(m.group(1)) and not re.match(r"[a-z]\)", m.group(1).strip()):
            r.alerte("phases", f"titre `#### {m.group(1)}` : seuls « Cas limites » et les blocs a), b)… sont prévus")

    # 7. Synthèse
    synthese: dict[str, tuple[str, str]] = {}
    for t in tables(contenu(9)):
        for ligne in t:
            ident = colonne(ligne, "#").strip("* ")
            if not re.fullmatch(r"R\d{1,3}[a-z]?", ident):
                continue
            cle = id_norm(ident)
            lot = norm(colonne(ligne, "lot"))
            fam = famille(colonne(ligne, "type"))
            if lot not in LOTS:
                r.err("synthèse", f"{ident} : lot « {lot} » inconnu (nominal · limite)")
            if fam not in TYPES:
                r.err("synthèse", f"{ident} : type « {colonne(ligne, 'type')} » inconnu")
            if cle in synthese:
                r.err("synthèse", f"{ident} figure deux fois")
            synthese[cle] = (lot, fam)
    if not synthese:
        r.err("synthèse", "§9 sans tableau de règles (# · Règle · Lot · Type)")
    for cle, fam in corps_regles.items():
        if cle not in synthese:
            r.err("synthèse", f"{cle} ancrée dans le corps mais absente du §9")
        elif fam != "?" and synthese[cle][1] != fam:
            r.err("synthèse", f"{cle} : type {fam} dans le corps, {synthese[cle][1]} au §9")
    for cle, (_, fam) in synthese.items():
        if cle not in corps_regles and not fam.startswith("EXISTANT"):
            r.err("synthèse", f"{cle} au §9 sans ancre dans le corps (seul un EXISTANT qualifié peut s'en passer)")

    # Identifiants définis
    hypotheses = {}
    for t in tables(contenu(10)):
        for ligne in t:
            ident = colonne(ligne, "#").strip("* ")
            if re.fullmatch(r"H\d{1,3}", ident):
                hypotheses[id_norm(ident)] = ligne
                if not colonne(ligne, "fausse"):
                    r.err("hypothèses", f"{ident} : « Si elle est fausse » vide")
    points = {}
    for t in tables(contenu(11)):
        for ligne in t:
            ident = colonne(ligne, "#").strip("* ")
            if not re.fullmatch(r"P\d{1,3}", ident):
                continue
            crit = norm(colonne(ligne, "critic"))
            points[id_norm(ident)] = crit
            if crit not in CRITICITES:
                r.err("points ouverts", f"{ident} : criticité « {crit} » inconnue (BLOQUANT · structurant · modalité)")
            if not colonne(ligne, "qui"):
                r.err("points ouverts", f"{ident} : « Qui tranche » vide")

    # 10. Renvois
    regles_connues = set(corps_regles) | set(synthese)
    for m in set(re.findall(r"\b(R\d{1,3}[a-z]?)\b", propre)):
        if id_norm(m) not in regles_connues:
            r.err("renvois", f"{m} citée mais définie nulle part")
    for m in set(re.findall(r"\b(H\d{1,3})\b", propre)):
        if id_norm(m) not in hypotheses:
            r.err("renvois", f"{m} citée mais absente du §10")
    for m in set(re.findall(r"\b(P\d{1,3})\b", propre)):
        if id_norm(m) not in points:
            r.alerte("renvois", f"{m} citée mais absente du §11")

    # 9. Transverses
    lignes5 = [l for t in tables(contenu(5)) for l in t]
    domaines = " ".join(norm(colonne(l, "domaine")) for l in lignes5)
    for nom, motif in SOCLE.items():
        if not re.search(motif, domaines):
            r.err("transverses", f"domaine du socle absent du §5 : {nom}")
    for ligne in lignes5:
        dom, verdict, quoi = colonne(ligne, "domaine"), norm(colonne(ligne, "verdict")), colonne(ligne, "regle", "raison")
        if verdict not in VERDICTS:
            r.err("transverses", f"« {dom} » : verdict « {verdict} » inconnu (impacté · non impacté · hors-lot)")
        elif verdict == "impacte":
            cites = [id_norm(x) for x in re.findall(r"R\d{1,3}[a-z]?", quoi)]
            if not cites:
                r.err("transverses", f"« {dom} » impacté sans règle citée")
        elif not quoi:
            r.err("transverses", f"« {dom} » {verdict} sans raison")

    # 11. Indicateurs
    indicateurs = [l for t in tables(sous_bloc(contenu(2), "indicateur") or "") for l in t
                   if re.fullmatch(r"I\d{1,2}", colonne(l, "#").strip("* "))]
    if not indicateurs:
        r.err("indicateurs", "§2 sans indicateur de succès (I1…)")
    if len(indicateurs) > 5:
        r.alerte("indicateurs", f"{len(indicateurs)} indicateurs : au-delà de 5, plus personne ne les suit")
    for ligne in indicateurs:
        ident = colonne(ligne, "#")
        if not colonne(ligne, "depart"):
            r.err("indicateurs", f"{ident} : valeur de départ vide (« inconnue — mesurée par Rn » est admis)")
        if not colonne(ligne, "cible"):
            r.err("indicateurs", f"{ident} : cible vide")

    # 12. Reports
    reports = sous_bloc(contenu(3), "renvoye")
    if reports is None:
        r.err("reports", "§3 sans sous-section « Renvoyé à plus tard »")
    else:
        for ligne in reports.splitlines():
            if re.match(r"\s*[-*]\s+", ligne) and not re.search(CONDITION_RETOUR, norm(ligne)):
                r.err("reports", f"report sans condition de retour : {ligne.strip()[:70]}")

    # 13. Statut et finition
    a_trancher = [c for c, fam in {**{k: v[1] for k, v in synthese.items()}, **corps_regles}.items()
                  if fam == "A TRANCHER"]
    ouverts_lourds = [p for p, crit in points.items() if crit in {"bloquant", "structurant"}]
    a_finir = re.findall(MOTS_A_FINIR, propre, flags=re.I)
    if valide:
        for c in a_trancher:
            r.err("statut", f"spec validée avec {c} encore À TRANCHER")
        for p in ouverts_lourds:
            r.err("statut", f"spec validée avec {p} ({points[p]}) encore ouvert")
        if a_finir:
            r.err("statut", f"spec validée avec des marqueurs à finir ({len(a_finir)}) : TODO, à préciser…")
    else:
        for c in a_trancher:
            if not any(c in " ".join(l.values()) for t in tables(contenu(11)) for l in t):
                r.alerte("statut", f"{c} À TRANCHER sans point ouvert au §11 qui la cite")
        if a_finir:
            r.alerte("statut", f"{len(a_finir)} marqueur(s) à finir (TODO, à préciser…)")

    # Avertissements de rédaction, règle par règle
    for cle, para in texte_regles.items():
        techniques = sorted({m.group(0) for m in re.finditer(MOTS_TECHNIQUES, para)})
        if techniques:
            r.alerte("rédaction", f"{cle} : vocabulaire technique ({', '.join(techniques)}) — une autre "
                     "implémentation au même comportement observable violerait-elle la règle ?")
        vagues = sorted({m.group(0).lower() for m in re.finditer(MOTS_VAGUES, para, flags=re.I)})
        if vagues:
            r.alerte("rédaction", f"{cle} : terme non vérifiable ({', '.join(vagues)}) — le remplacer par un seuil")
        if re.search(MOTS_CALCUL, norm(para)) and not re.search(r"\d+[,.]\d+|\d{2,}", para):
            r.alerte("rédaction", f"{cle} : règle de calcul sans exemple chiffré non rond")

    lots = [v[0] for v in synthese.values()]
    return {
        "statut": statut,
        "profondeur": profondeur,
        "regles": len(regles_connues),
        "nominal": lots.count("nominal"),
        "limite": lots.count("limite") + lots.count("edge"),
        "hypotheses": len(hypotheses),
        "points": points,
        "regles_ids": regles_connues,
        "hypotheses_ids": set(hypotheses),
        "points_ids": set(points),
        "lignes": len(corps.splitlines()),
    }


def analyser_journal(texte: str, spec: dict, r: Rapport) -> dict:
    # Une question peut apparaître deux fois (« en attente », puis sa réponse) : la dernière ligne fait foi.
    dernieres: dict[str, str] = {}
    for ident, reste in re.findall(r"^\s*[-*]?\s*(Q\d+[a-z]?)\b(.*)$", texte, flags=re.M):
        dernieres[ident] = reste
    questions = list(dernieres.items())
    stats = {"questions": len(questions), "bloquant": 0, "structurant": 0, "modalite": 0}
    for ident, reste in questions:
        # La criticité est le premier champ après l'identifiant : « Q4 · structurant · … ».
        champs = [norm(c) for c in re.split(r"[·|]", reste) if c.strip()]
        crit = next((c for c in ("bloquant", "structurant", "modalite") if champs and champs[0].startswith(c)), None)
        if crit:
            stats[crit] += 1
        if "→" not in reste and "->" not in reste:
            r.err("journal", f"{ident} sans destination (`→ tranché`, `→ hypothèse Hn`, `→ point ouvert Pn`…)")
            continue
        dest = norm(re.split(r"→|->", reste, maxsplit=1)[1])
        if dest.startswith("en attente"):
            message = f"{ident} encore en attente de réponse"
            (r.err if spec["statut"] == "valide" else r.alerte)("journal", message)
            continue
        if not re.search(r"tranch|hypoth|point ouvert|hors perim|renvoy|abandon|sans objet|\b[rhp]\d", dest):
            r.err("journal", f"{ident} : destination non reconnue « {dest[:50]} »")
        for cible in re.findall(r"\b([RHP]\d{1,3}[a-z]?)\b", reste):
            c = id_norm(cible)
            connus = {"R": spec["regles_ids"], "H": spec["hypotheses_ids"], "P": spec["points_ids"]}[c[0]]
            if c not in connus:
                r.err("journal", f"{ident} renvoie à {cible}, absent de la spec")
    if spec["profondeur"] == "beton" and "## champ des possibles explore" not in norm(texte):
        r.err("journal", "profondeur béton sans « ## Champ des possibles exploré » : l'ouverture n'a pas été archivée")
    carte = re.search(r"## Carte de couverture(.*?)(?=\n## )", texte, flags=re.S)
    if carte:
        trous = [l for l in carte.group(1).splitlines() if l.startswith("|") and ("❓" in l or "⛔" in l)]
        for l in trous:
            zone = l.strip("|").split("|")[0].strip()
            message = f"zone « {zone} » encore ❓ ou ⛔ dans la carte de couverture"
            (r.err if spec["statut"] == "valide" else r.alerte)("journal", message)
    else:
        r.alerte("journal", "pas de « ## Carte de couverture »")
    return stats


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        return 2
    chemin_spec = Path(sys.argv[1])
    if not chemin_spec.exists():
        print(f"✗ fichier introuvable : {chemin_spec}")
        return 2
    r = Rapport()
    spec = analyser_spec(chemin_spec.read_text(encoding="utf-8"), r)
    journal = None
    if len(sys.argv) == 3:
        chemin_journal = Path(sys.argv[2])
        if chemin_journal.exists():
            journal = analyser_journal(chemin_journal.read_text(encoding="utf-8"), spec, r)
        else:
            r.err("journal", f"fichier introuvable : {chemin_journal}")

    print(f"Contrôle de {chemin_spec.name}\n")
    for e in r.erreurs:
        print(f"✗ {e}")
    for a in r.alertes:
        print(f"⚠ {a}")
    ouverts = spec["points"]
    print(
        f"\nRègles : {spec['regles']} ({spec['nominal']} nominal · {spec['limite']} limite)"
        f" · {spec['lignes'] / max(spec['regles'], 1):.1f} lignes par règle"
        f" · hypothèses : {spec['hypotheses']}"
        f" · points ouverts : {len(ouverts)}"
        f" ({sum(c == 'bloquant' for c in ouverts.values())} bloquant)"
    )
    if journal:
        print(
            f"Questions posées : {journal['questions']} ({journal['bloquant']} bloquantes · "
            f"{journal['structurant']} structurantes · {journal['modalite']} modalités)"
        )
    if r.erreurs:
        print(f"\n✗ {len(r.erreurs)} erreur(s) — à corriger avant de présenter la spec.")
        return 1
    print(f"\n✓ 0 erreur · {len(r.alertes)} avertissement(s) à traiter ou assumer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
