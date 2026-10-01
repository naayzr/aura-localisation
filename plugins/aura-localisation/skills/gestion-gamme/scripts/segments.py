#!/usr/bin/env python3
"""Mémoire de traduction de la gamme : Références/Segments/Segments_<Gamme>.csv (EN;FR;produit;date).

Bibliothèque standard uniquement ; lecture par lecture.py, règles communes dans commun.py.

Deux commandes :
  chercher : pour chaque passage d'un fichier source, les segments déjà traduits identiques ou proches.
      python3 segments.py chercher regles_extension.docx --memoire Segments_Gamme.csv --sortie reprise.md
      python3 segments.py chercher cartes.xlsx --col-en Text --memoire Segments_Gamme.csv
  aligner : transforme un fichier bilingue validé (une colonne EN, une colonne FR) en lignes de mémoire,
            sans doublon avec la mémoire existante. Le fichier produit est à AJOUTER à la mémoire.
      python3 segments.py aligner cartes_validees.xlsx --col-en Text --col-fr "Texte FR" \\
          --produit "Extension 1" --date 2026-11-20 --memoire Segments_Gamme.csv --sortie a_ajouter.csv

Une correspondance n'est qu'une proposition : le glossaire fait foi sur chaque terme, et un même texte
anglais peut demander une autre traduction si la mécanique diffère.

  python3 segments.py --auto-test
      fabrique une mémoire, une source et un fichier bilingue où des cas connus ont été glissés exprès
      (identique, proche, sans correspondance, déjà en mémoire, conflit, ligne incomplète) ; les deux
      commandes doivent les classer tous juste, sans proposer de traduction à un passage sans antécédent,
      et refuser d'écraser un fichier existant.

Codes de sortie : 0 fait ; 1 auto-test en échec ; 2 erreur d'usage ou fichier illisible.
"""
import argparse
import contextlib
import csv
import io
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402
from commun import (arret, normaliser, diff_mots, ressemblance, colonne, lire_table, cellule,  # noqa: E402
                    charger_memoire, decrire_traductions)


def passages_source(chemin, col_en, feuille):
    ext = Path(chemin).suffix.lower()
    if col_en:
        tete, corps = lire_table(chemin, feuille, [col_en])
        i = colonne(tete, col_en)
        return [(f"ligne {k}", cellule(l, i)) for k, l in corps if cellule(l, i)]
    if ext in (".xlsx", ".csv", ".tsv"):
        print("Attention : sans --col-en, toutes les cellules du tableau sont lues (identifiants et colonnes FR compris).",
              file=sys.stderr)
    return lecture.textes(chemin)


def chercher(a):
    memo = charger_memoire(a.memoire)
    if not memo:
        arret("Mémoire vide ou illisible : vérifie le chemin du CSV (EN;FR;produit;date).")
    source = passages_source(a.source, a.col_en, a.feuille)
    cles = list(memo)
    longueurs = [len(c) for c in cles]
    identiques, proches, sans, ignores = [], [], [], 0
    for rep, texte in source:
        t = normaliser(texte)
        if len(t) < a.min_car or not any(ch.isalpha() for ch in t):
            ignores += 1
            continue
        if t in memo:
            identiques.append((rep, texte, memo[t]))
            continue
        # le ratio difflib vaut au plus 2·min(la, lb)/(la + lb) : hors de ces longueurs, le seuil est inatteignable
        lo, hi = len(t) * a.seuil / (2 - a.seuil), len(t) * (2 - a.seuil) / a.seuil
        cands = []
        for c, n in zip(cles, longueurs):
            if lo <= n <= hi:
                r = ressemblance(t, c, a.seuil)
                if r >= a.seuil:
                    cands.append((r, c))
        if cands:
            cands.sort(reverse=True)
            proches.append((rep, texte, cands[:a.max]))
        else:
            sans.append((rep, texte))

    def car(liste):
        return sum(len(x[1]) for x in liste)

    R = [f"# Segments déjà traduits — {Path(a.source).name} — {date.today().isoformat()}", "",
         f"Mémoire : {', '.join(Path(m).name for m in a.memoire)} ({len(cles)} segments anglais distincts). "
         f"Seuil de ressemblance : {a.seuil:.0%}.", "",
         f"**Résumé :** passages lus : {len(source)} ; identiques : {len(identiques)} ({car(identiques)} caractères) ; "
         f"proches : {len(proches)} ({car(proches)} caractères) ; sans correspondance : {len(sans)} ({car(sans)} caractères) ; "
         f"ignorés (moins de {a.min_car} caractères ou sans lettre) : {ignores}.", "",
         "Rappel : le glossaire fait foi sur chaque terme ; vérifier que la mécanique est la même avant de reprendre.", "",
         f"## Identiques — à reprendre après vérification du contexte ({len(identiques)})", ""]
    R += [f"- {rep} : {texte}\n  - mémoire : {decrire_traductions(e)}" for rep, texte, e in identiques] or ["Aucun."]
    R += ["", f"## Proches — modèle à adapter ({len(proches)})", ""]
    for rep, texte, cands in proches:
        R.append(f"- {rep} : {texte}")
        for r, c in cands:
            en_memo = memo[c][0][3]
            R.append(f"  - {r:.0%} — mémoire : {en_memo} → {decrire_traductions(memo[c])}")
            R.append(f"    - écart avec la source : {diff_mots(en_memo, normaliser(texte))}")
    if not proches:
        R.append("Aucun.")
    R += ["", f"## Sans correspondance ({len(sans)})", "",
          ", ".join(rep for rep, _ in sans) if sans else "Aucun."]
    texte = "\n".join(R)
    print(texte)
    if a.sortie:
        Path(a.sortie).write_text(texte + "\n", encoding="utf-8")
        print(f"\nRapport écrit dans {a.sortie}")
    return 0


def aligner(a):
    try:
        date.fromisoformat(a.date)
    except ValueError:
        arret(f"--date « {a.date} » : format AAAA-MM-JJ attendu.")
    tete, corps = lire_table(a.bilingue, a.feuille, [a.col_en, a.col_fr])
    i_en, i_fr = colonne(tete, a.col_en), colonne(tete, a.col_fr)
    memo = charger_memoire(a.memoire)
    deja = {(cle, normaliser(fr_)) for cle, e in memo.items() for fr_, *_ in e}
    nouveaux, doublons, incomplets, conflits = [], 0, 0, []
    vus = set()
    for k, l in corps:
        en, fr_ = cellule(l, i_en), cellule(l, i_fr)
        if not en or not fr_:
            incomplets += bool(en or fr_)
            continue
        cle = (normaliser(en), normaliser(fr_))
        if cle in deja or cle in vus:
            doublons += 1
            continue
        vus.add(cle)
        autres = [x[0] for x in memo.get(cle[0], []) if normaliser(x[0]) != cle[1]]
        if autres:
            conflits.append((k, en, fr_, autres))
        nouveaux.append([en, fr_, a.produit, a.date])
    sortie = Path(a.sortie)
    if sortie.exists():
        arret(f"{sortie} existe déjà : choisis un autre nom (on n'écrase jamais un fichier).")
    with open(sortie, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["EN", "FR", "produit", "date"])
        w.writerows(nouveaux)
    print(f"Segments nouveaux : {len(nouveaux)} écrits dans {sortie} (à ajouter à la fin de la mémoire, sans la ligne d'en-tête).")
    print(f"Déjà en mémoire ou en double : {doublons} ; lignes incomplètes (EN ou FR vide) : {incomplets}.")
    if conflits:
        print(f"Même texte anglais déjà traduit autrement : {len(conflits)} (à montrer à Hervé, rien n'est remplacé) :")
        for k, en, fr_, autres in conflits:
            print(f"- ligne {k} : {en} → « {fr_} » ; en mémoire : " + " / ".join(f"« {x} »" for x in autres))
    return 0


def _lancer(argv):
    """Lance le vrai programme (main) avec ces options ; renvoie (code de sortie, texte affiché)."""
    ancien, sortie = sys.argv, io.StringIO()
    sys.argv = ["segments.py"] + argv
    try:
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            try:
                code = main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = ancien
    return code, sortie.getvalue()


def _xlsx_minimal(chemin, lignes):
    """Classeur .xlsx d'un onglet, cellules en texte (pour l'auto-test seulement)."""
    import zipfile
    from xml.sax.saxutils import escape
    rangs = "".join(
        f'<row r="{i}">' + "".join(f'<c r="{chr(65 + j)}{i}" t="inlineStr"><is><t>{escape(v)}</t></is></c>'
                                   for j, v in enumerate(l) if v) + "</row>"
        for i, l in enumerate(lignes, 1))
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    nsr = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr("xl/workbook.xml", f'<workbook {ns} {nsr}><sheets><sheet name="Cartes" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                   'Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr("xl/worksheets/sheet1.xml", f"<worksheet {ns}><sheetData>{rangs}</sheetData></worksheet>")


def auto_test():
    """Cas connus glissés exprès ; les résultats attendus sont écrits à la main."""
    nb = " "
    echecs = []
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        memoire = d / "Segments_Essai.csv"
        memoire.write_text(
            "EN;FR;produit;date\n"
            "Move up to 2 spaces.;Déplacez-vous de 2 cases maximum.;Base;2026-04-15\n"
            "Draw 1 card.;Piochez 1 carte.;Base;2026-04-15\n"
            '"Gain 1 gold, then rest.";"Gagnez 1 or, puis reposez-vous.";Base;2026-04-15\n',
            encoding="utf-8")
        source = d / "regles_extension.txt"
        source.write_text(
            f"Draw  1{nb}card.\n"                        # identique (espaces seulement)
            "Move up to 3 spaces.\n"                      # proche de « Move up to 2 spaces. »
            "Gain 1 gold, then rest.\n"                   # identique (virgule dans un champ entre guillemets)
            "The fog rolls over the marsh at dusk.\n"     # sans correspondance
            "OK\n"                                        # ignoré (moins de 4 caractères)
            "12 / 14\n",                                  # ignoré (sans lettre)
            encoding="utf-8")
        code, texte = _lancer(["chercher", str(source), "--memoire", str(memoire)])
        attendus = ["passages lus : 6 ; identiques : 2", "proches : 1", "sans correspondance : 1",
                    "ignorés (moins de 4 caractères ou sans lettre) : 2",
                    "mémoire : « Piochez 1 carte. » (Base, 2026-04-15)",
                    "mémoire : « Gagnez 1 or, puis reposez-vous. » (Base, 2026-04-15)",
                    "→ « Déplacez-vous de 2 cases maximum. »",
                    "écart avec la source : Move up to [-2-]{+3+} spaces."]
        manquent = [a for a in attendus if a not in texte] + ([f"code 0 (vu {code})"] if code != 0 else [])
        sans = texte.split("## Sans correspondance", 1)[-1]
        if "The fog" in texte.split("## Sans correspondance", 1)[0] or "L4" not in sans:
            manquent.append("le passage sans antécédent (L4) rangé seul, sans traduction proposée")
        print(f"  chercher : {'OK' if not manquent else 'ÉCHEC'}")
        if manquent:
            echecs.append(f"chercher — non trouvé : {manquent}")

        bilingue = d / "cartes_validées.xlsx"
        _xlsx_minimal(bilingue, [
            ["Liste des cartes validées"], [],                                  # titre au-dessus du tableau
            ["ID", "Text", "Texte FR"],
            ["C1", "Draw 1 card.", "Piochez 1 carte."],                         # déjà en mémoire
            ["C2", "Shuffle the deck.", "Mélangez la pioche."],                 # nouveau
            ["C3", "Shuffle the deck.", "Mélangez la pioche."],                 # en double dans le fichier
            ["C4", "Move up to 2 spaces.", "Déplacez-vous d’au plus 2 cases."], # conflit avec la mémoire
            ["C5", "Rest.", ""]])                                               # incomplet
        sortie = d / "a_ajouter.csv"
        argv = ["aligner", str(bilingue), "--col-en", "Text", "--col-fr", "Texte FR", "--produit", "Extension",
                "--date", "2026-11-20", "--memoire", str(memoire), "--sortie", str(sortie)]
        code, texte = _lancer(argv)
        attendus = ["Segments nouveaux : 2 écrits", "Déjà en mémoire ou en double : 2",
                    "lignes incomplètes (EN ou FR vide) : 1", "Même texte anglais déjà traduit autrement : 1",
                    "« Déplacez-vous de 2 cases maximum. »"]
        manquent = [a for a in attendus if a not in texte] + ([f"code 0 (vu {code})"] if code != 0 else [])
        lignes = sortie.read_text(encoding="utf-8-sig").splitlines() if sortie.exists() else []
        attendu_fichier = ["EN;FR;produit;date", "Shuffle the deck.;Mélangez la pioche.;Extension;2026-11-20",
                           "Move up to 2 spaces.;Déplacez-vous d’au plus 2 cases.;Extension;2026-11-20"]
        if lignes != attendu_fichier:
            manquent.append(f"contenu du fichier écrit : {lignes}")
        avant = sortie.read_bytes() if sortie.exists() else b""
        code2, texte2 = _lancer(argv)
        if code2 != 2 or "existe déjà" not in texte2 or (sortie.read_bytes() if sortie.exists() else b"") != avant:
            manquent.append("refus d'écraser un fichier existant (code 2, fichier inchangé)")
        print(f"  aligner : {'OK' if not manquent else 'ÉCHEC'}")
        if manquent:
            echecs.append(f"aligner — non trouvé : {manquent}")
    if echecs:
        print("AUTO-TEST ÉCHOUÉ — " + " ; ".join(echecs) + ". Ne pas se fier à cette mémoire de traduction.")
        return 1
    print("AUTO-TEST OK — chercher : 2 identiques, 1 proche, 1 sans correspondance, 2 ignorés, tous bien classés ; "
          "aligner : 2 nouveaux, 2 déjà connus, 1 conflit, 1 incomplet, fichier exact et jamais écrasé ; "
          "0 traduction proposée à tort")
    return 0


def main():
    if "--auto-test" in sys.argv[1:]:
        return auto_test()
    ap = argparse.ArgumentParser(description="Mémoire de traduction de la gamme (Références/Segments/).",
                                 epilog="--auto-test : essai sur des fichiers fabriqués par le programme.")
    sub = ap.add_subparsers(dest="commande", required=True)
    c = sub.add_parser("chercher", help="segments identiques ou proches pour un fichier source")
    c.add_argument("source")
    c.add_argument("--memoire", nargs="+", required=True, help="CSV EN;FR;produit;date")
    c.add_argument("--col-en", help="colonne du texte anglais si la source est un tableau")
    c.add_argument("--feuille", help="onglet du .xlsx")
    c.add_argument("--seuil", type=float, default=0.75, help="ressemblance minimale d'un segment proche (défaut 0,75)")
    c.add_argument("--max", type=int, default=2, help="segments proches affichés par passage (défaut 2)")
    c.add_argument("--min-car", type=int, default=4, help="passages plus courts ignorés (défaut 4 caractères)")
    c.add_argument("--sortie", help="écrit le rapport dans ce fichier .md")
    al = sub.add_parser("aligner", help="fichier bilingue validé → lignes à ajouter à la mémoire")
    al.add_argument("bilingue")
    al.add_argument("--col-en", required=True)
    al.add_argument("--col-fr", required=True)
    al.add_argument("--produit", required=True)
    al.add_argument("--date", required=True, help="date de validation ou de publication, AAAA-MM-JJ")
    al.add_argument("--feuille")
    al.add_argument("--memoire", nargs="*", default=[], help="mémoire existante, pour ne pas créer de doublon")
    al.add_argument("--sortie", required=True, help="nouveau fichier .csv (jamais écrasé)")
    a = ap.parse_args()
    if a.commande == "chercher" and not 0 < a.seuil <= 1:
        arret("--seuil doit être entre 0 et 1.")
    try:
        return chercher(a) if a.commande == "chercher" else aligner(a)
    except (OSError, KeyError, ValueError) as e:
        arret(f"Lecture impossible : {e}")


if __name__ == "__main__":
    sys.exit(main())
