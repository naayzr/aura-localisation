#!/usr/bin/env python3
"""Contrôle de la typographie française d'un texte traduit (charte : references/charte.md).

Usage :
  python3 typo.py FICHIER [--colonne NOM] [--corriger] [--max N]
  python3 typo.py --auto-test

FICHIER : .docx, .xlsx, .csv, .tsv, .txt, .md
--colonne NOM : pour un tableur, ne contrôler que la colonne dont l'en-tête est NOM (ex. FR)
--corriger    : pour .txt/.md/.csv seulement, écrit une COPIE corrigée « <nom>_typo<ext> » à côté
                (les règles sûres seulement ; l'original n'est jamais modifié)
--auto-test   : passe le contrôle sur un extrait saboté de fautes connues ; doit toutes les trouver

Chaque règle porte l'identifiant de la charte (T01…). Les comptes sont exacts : tout le fichier est lu.
"""
import argparse, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

NB = "  "           # espaces insécables admises
E_INV = "[" + NB + "]"

# Mots courants qui prennent une majuscule accentuée en tête (T08). Liste volontairement prudente.
MAJ_ACCENT = {
    "etat": "État", "etats": "États", "etape": "Étape", "etapes": "Étapes", "egalement": "Également",
    "element": "Élément", "elements": "Éléments", "equipe": "Équipe", "equipement": "Équipement",
    "epuise": "Épuisé", "epuisee": "Épuisée", "epuisez": "Épuisez", "evenement": "Événement",
    "evenements": "Événements", "ecran": "Écran", "echange": "Échange", "echangez": "Échangez",
    "eliminez": "Éliminez", "elimine": "Éliminé", "evitez": "Évitez", "etoile": "Étoile",
    "eclat": "Éclat", "energie": "Énergie", "enigme": "Énigme", "epee": "Épée", "eveil": "Éveil",
    "a": "À", "etre": "Être", "ete": "Été",
}

# Chaque règle : (id, libellé, motif, remplacement sûr ou None)
REGLES = [
    ("T01", "espace insécable avant ; ! ?",
     re.compile(r"(?:(?<=\S) |(?<=[^\s" + NB + r"]))([;!?])(?![;!?])"), None),
    ("T02", "espace insécable avant :",
     re.compile(r"(?:(?<=\S) |(?<=[^\s" + NB + r"\d]))(:)(?!//)"), None),
    ("T03", "guillemets français « » avec espaces insécables",
     re.compile(r"\"|«(?!" + E_INV + r")|(?<!" + E_INV + r")»"), None),
    ("T04", "apostrophe typographique ’",
     re.compile(r"(?<=[A-Za-zÀ-ÿ])'(?=[A-Za-zÀ-ÿ])"), "’"),
    ("T05", "points de suspension en un caractère …", re.compile(r"\.\.\."), "…"),
    ("T06", "pas d'espace avant , et .", re.compile(r"(?<=\S)[ " + NB + r"]+(?=[,.](?!\.))"), ""),
    ("T07", "pas de double espace", re.compile(r"(?<=\S) {2,}(?=\S)"), " "),
    ("T08", "majuscule accentuée", re.compile(r"\b(E[a-zé]+|A)\b"), None),
    ("T09", "ordinal abrégé (1er, 2e)", re.compile(r"\b\d+(?:ème|eme|ième|è|nd|nde)\b", re.I), None),
    ("T10", "séparateur de milliers (à partir de 10 000)", re.compile(r"(?<![\d.,/#\w])\d{5,}(?![\d\w])|\b\d{1,3}(?:,\d{3})+\b"), None),
    ("T11", "incise : tiret demi-cadratin –, pas un trait d'union", re.compile(r"(?<=\w) - (?=\w)"), None),
    ("T12", "espace insécable après n° et avant une unité", re.compile(r"n° (?=\d)|(?<=\d) (?=(?:PV|PA|PM|%|€|cm|mm|kg|g)\b)"), None),
]
IDS = [r[0] for r in REGLES]


def candidats_t08(texte):
    for m in re.finditer(r"(?<![\w])([EA][a-zé]*)\b", texte):
        mot = m.group(1)
        cle = mot.lower().replace("é", "e")
        if mot in ("A",):
            # « A » isolé en début de phrase ou après ponctuation forte = « À »
            avant = texte[:m.start()].rstrip()
            if avant == "" or avant[-1] in ".!?:»\n":
                yield m.start(), mot, "À"
        elif cle in MAJ_ACCENT and mot[0] == "E" and mot != MAJ_ACCENT[cle]:
            yield m.start(), mot, MAJ_ACCENT[cle]


def controler_texte(texte):
    """Liste de (id, position, extrait, suggestion)."""
    trouve = []
    for rid, _lib, motif, remp in REGLES:
        if rid == "T08":
            for pos, mot, sugg in candidats_t08(texte):
                trouve.append((rid, pos, mot, sugg))
            continue
        for m in motif.finditer(texte):
            if rid == "T10" and re.fullmatch(r"(19|20)\d{2}", m.group(0)):
                continue
            debut = max(0, m.start() - 15)
            extrait = texte[debut:m.end() + 15].replace("\n", " ")
            trouve.append((rid, m.start(), extrait, remp))
    return trouve


def corriger_texte(texte):
    for rid, _lib, motif, remp in REGLES:
        if remp is not None:
            texte = motif.sub(remp, texte)
    return texte


def colonne_filtree(chemin, nom_col):
    p = Path(chemin)
    if p.suffix.lower() == ".xlsx":
        feuilles = lecture.feuilles_xlsx(p)
    else:
        feuilles = {"": lecture.lignes_csv(p)}
    out = []
    for feuille, lignes in feuilles.items():
        idx = None
        for i, ligne in enumerate(lignes):
            norm = [str(c).strip().lower() for c in ligne]
            if nom_col.lower() in norm:
                idx = norm.index(nom_col.lower())
                for j, l2 in enumerate(lignes[i + 1:], i + 2):
                    if idx < len(l2) and str(l2[idx]).strip():
                        out.append((f"{feuille}!L{j}" if feuille else f"L{j}", str(l2[idx])))
                break
        if idx is None and len(feuilles) == 1:
            raise SystemExit(f"Colonne « {nom_col} » introuvable dans les en-têtes.")
    return out


def rapport(segments, maxi):
    total = Counter()
    lignes = []
    for repere, texte in segments:
        for rid, _pos, extrait, sugg in controler_texte(texte):
            total[rid] += 1
            if sum(total.values()) <= maxi:
                s = f" → {sugg!r}" if sugg not in (None, "") else ""
                lignes.append(f"  {repere}  [{rid}] « {extrait.strip()} »{s}")
    return total, lignes


def auto_test():
    sabote = ("Défaussez une carte! Effet: piochez \"Éclat\" puis l'action... "
              "Etape 2  : la 2ème manche rapporte 10000 points - sauf si n° 3.")
    attendus = {"T01", "T02", "T03", "T04", "T05", "T07", "T08", "T09", "T10", "T11", "T12"}
    trouves = {r[0] for r in controler_texte(sabote)}
    propre = ("Défaussez une carte ! Effet : piochez « Éclat » puis l’action… "
              "Étape 2 : la 2e manche rapporte 10 000 points – sauf si n° 3.")
    faux_positifs = [r for r in controler_texte(propre) if r[0] != "T02"]
    # « Étape 2 : » : l'espace avant « : » est ordinaire exprès dans le texte propre → T02 attendu, rien d'autre
    manquants = attendus - trouves
    if manquants or faux_positifs:
        print(f"AUTO-TEST ÉCHOUÉ — fautes non trouvées : {sorted(manquants)} ; fausses alertes : {faux_positifs}")
        return 1
    print(f"AUTO-TEST OK — {len(attendus)} fautes glissées exprès, toutes trouvées ; 0 fausse alerte sur le texte propre")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier", nargs="?")
    ap.add_argument("--colonne")
    ap.add_argument("--corriger", action="store_true")
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--auto-test", action="store_true")
    a = ap.parse_args()
    if a.auto_test:
        sys.exit(auto_test())
    if not a.fichier:
        ap.error("donne un fichier, ou --auto-test")
    p = Path(a.fichier)
    segments = colonne_filtree(p, a.colonne) if a.colonne else lecture.textes(p)
    total, lignes = rapport(segments, a.max)
    print(f"Typographie — {p.name} — {len(segments)} segments lus en entier")
    if not total:
        print("0 alerte. (Vérifie quand même avec --auto-test que le contrôle trouve bien des fautes glissées exprès.)")
    else:
        print(f"{sum(total.values())} alerte(s) :")
        for rid in IDS:
            if total[rid]:
                lib = next(r[1] for r in REGLES if r[0] == rid)
                print(f"  {rid} {lib} : {total[rid]}")
        print(f"Détail ({min(sum(total.values()), a.max)} premières) :")
        print("\n".join(lignes))
    if a.corriger:
        if p.suffix.lower() not in (".txt", ".md", ".csv", ".tsv"):
            print("--corriger : seulement pour .txt/.md/.csv ; pour Word et Excel, voir la charte (Rechercher/Remplacer sur une copie).")
        else:
            texte = lecture._decoder(p.read_bytes())
            sortie = p.with_name(p.stem + "_typo" + p.suffix)
            if sortie.exists():
                raise SystemExit(f"{sortie.name} existe déjà : je n'écrase pas. Renomme-le ou supprime-le d'abord.")
            sortie.write_text(corriger_texte(texte), encoding="utf-8")
            print(f"Copie corrigée (règles sûres T04 T05 T06 T07) : {sortie.name}. L'original n'est pas modifié.")


if __name__ == "__main__":
    main()
