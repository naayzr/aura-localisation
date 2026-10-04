#!/usr/bin/env python3
"""Mémoire de traduction de la gamme : Références/Segments/Segments_<Gamme>.csv (EN;FR;produit;date).

Bibliothèque standard uniquement ; lecture par lecture.py, règles communes dans commun.py.

Trois commandes :
  chercher : pour chaque passage d'un fichier source, les segments déjà traduits identiques ou proches.
      python3 segments.py chercher regles_extension.docx --memoire Segments_Gamme.csv --sortie reprise.md
      python3 segments.py chercher cartes.xlsx --col-en Text --memoire Segments_Gamme.csv
  aligner : transforme un fichier bilingue validé (une colonne EN, une colonne FR) en lignes de mémoire,
            sans doublon avec la mémoire existante. Le fichier produit est à AJOUTER à la mémoire.
      python3 segments.py aligner cartes_validees.xlsx --col-en Text --col-fr "Texte FR" \\
          --produit "Extension 1" --date 2026-11-20 --memoire Segments_Gamme.csv --sortie a_ajouter.csv
  ajouter : ajoute à la FIN de la mémoire les lignes du fichier produit par « aligner » (une fois
            qu'Hervé a vu les conflits). Copie datée de la mémoire dans Core/Archives d'abord ; l'ajout
            se fait dans une copie, recomptée : la mémoire n'est remplacée que si « avant + ajoutés =
            après » et si ses lignes d'avant sont restées identiques. Une ligne déjà en mémoire n'est pas
            reprise ; rien n'est jamais effacé ni remplacé.
      python3 segments.py ajouter a_ajouter.csv --memoire "Références/Segments/Segments_Gamme.csv"

Une correspondance n'est qu'une proposition : le glossaire fait foi sur chaque terme, et un même texte
anglais peut demander une autre traduction si la mécanique diffère.

  python3 segments.py --auto-test
      fabrique une mémoire, une source et un fichier bilingue où des cas connus ont été glissés exprès
      (identique, proche, sans correspondance, déjà en mémoire, conflit, ligne incomplète) ; les
      commandes doivent les classer tous juste, sans proposer de traduction à un passage sans antécédent,
      refuser d'écraser un fichier existant et une colonne absente, et « ajouter » doit allonger la
      mémoire du compte exact, après une sauvegarde identique à l'original, sans jamais doubler une ligne.

Codes de sortie : 0 fait ; 1 auto-test en échec ; 2 erreur d'usage ou fichier illisible.
"""
import argparse
import contextlib
import csv
import io
import os
import shutil
import sys
import tempfile
import unicodedata
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402
from commun import (arret, normaliser, diff_mots, ressemblance, colonne, lire_table, cellule,  # noqa: E402
                    charger_memoire, decrire_traductions, sortie_libre, ecrire_sortie)


def passages_source(chemin, col_en, feuille):
    ext = Path(chemin).suffix.lower()
    if col_en:
        tete, corps = lire_table(chemin, feuille, [col_en])
        i = colonne(tete, col_en, corps)
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
        ecrire_sortie(a.sortie, texte + "\n")
        print(f"\nRapport écrit dans {a.sortie}")
    return 0


def aligner(a):
    try:
        date.fromisoformat(a.date)
    except ValueError:
        arret(f"--date « {a.date} » : format AAAA-MM-JJ attendu.")
    tete, corps = lire_table(a.bilingue, a.feuille, [a.col_en, a.col_fr])
    i_en, i_fr = colonne(tete, a.col_en, corps), colonne(tete, a.col_fr, corps)
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
    sortie = Path(sortie_libre(a.sortie))
    with open(sortie, "x", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["EN", "FR", "produit", "date"])
        w.writerows(nouveaux)
    print(f"Segments nouveaux : {len(nouveaux)} écrits dans {sortie}. Après qu'Hervé a vu les conflits ci-dessous, "
          f"ils s'ajoutent à la mémoire par « segments.py ajouter {sortie.name} --memoire … » (jamais à la main).")
    print(f"Déjà en mémoire ou en double : {doublons} ; lignes incomplètes (EN ou FR vide) : {incomplets}.")
    if conflits:
        print(f"Même texte anglais déjà traduit autrement : {len(conflits)} (à montrer à Hervé, rien n'est remplacé) :")
        for k, en, fr_, autres in conflits:
            print(f"- ligne {k} : {en} → « {fr_} » ; en mémoire : " + " / ".join(f"« {x} »" for x in autres))
    return 0


def lignes_memoire(texte):
    """(en-tête ou None, lignes non vides) d'une mémoire déjà décodée."""
    d = lecture.separateur(texte) or ";"
    lignes = [l for l in csv.reader(io.StringIO(texte), delimiter=d) if any(c.strip() for c in l)]
    if lignes and {"en", "fr"} <= {c.strip().lower() for c in lignes[0]}:
        return lignes[0], lignes[1:]
    return None, lignes


def dossier_archives(memoire):
    """<HERVÉ WORLD>/Références/Segments/X.csv → <HERVÉ WORLD>/Core/Archives ; sinon None."""
    p = Path(memoire).resolve()
    noms = [unicodedata.normalize("NFC", x.name) for x in (p.parent, p.parent.parent)]
    return p.parent.parent.parent / "Core" / "Archives" if noms == ["Segments", "Références"] else None


def ajouter(a):
    """Ajoute à la FIN de la mémoire les lignes d'un fichier produit par « aligner ». Sauvegarde datée
    d'abord ; ajout dans une copie recomptée ; la mémoire n'est remplacée que si le compte tombe juste."""
    memoire = Path(a.memoire)
    source = [l for l in lecture.lignes_csv(a.lignes) if any(c.strip() for c in l)]
    tete = [c.strip().lower() for c in source[0]] if source else []
    if "en" not in tete or "fr" not in tete:
        arret(f"{Path(a.lignes).name} : en-tête EN;FR;produit;date attendu (le fichier produit par « aligner »).")
    i = {k: (tete.index(k) if k in tete else None) for k in ("en", "fr", "produit", "date")}
    existe = memoire.exists()
    octets = memoire.read_bytes() if existe else b""
    try:
        texte = octets.decode("utf-8-sig")
    except UnicodeDecodeError:
        texte = None
    if texte is None or "\x00" in texte:
        arret(f"{memoire.name} n'est pas un CSV en UTF-8 : AURA ne l'allonge pas (deux encodages dans un fichier "
              "le rendraient illisible). L'enregistrer d'abord en « CSV UTF-8 » depuis Excel, puis relancer.")
    neuf = not texte.strip()   # mémoire absente ou vide : elle reçoit son en-tête
    entete, avant = lignes_memoire(texte) if not neuf else (None, [])
    deja = {(normaliser(cellule(l, 0)), normaliser(cellule(l, 1))) for l in avant}
    if entete:
        b = [c.strip().lower() for c in entete]
        deja = {(normaliser(cellule(l, b.index("en"))), normaliser(cellule(l, b.index("fr")))) for l in avant}
    nouvelles, doublons, incompletes = [], 0, 0
    for l in source[1:]:
        en, fr_ = cellule(l, i["en"]), cellule(l, i["fr"])
        if not en or not fr_:
            incompletes += 1
            continue
        cle = (normaliser(en), normaliser(fr_))
        if cle in deja:
            doublons += 1
            continue
        deja.add(cle)
        valeurs = {"en": en, "fr": fr_, "produit": cellule(l, i["produit"]), "date": cellule(l, i["date"])}
        ordre = [c.strip().lower() for c in entete] if entete else ["en", "fr", "produit", "date"]
        nouvelles.append([valeurs.get(c, "") for c in ordre])
    print(f"Mémoire : {memoire.name} — avant : {len(avant)} segments ; à ajouter : {len(nouvelles)} ; déjà en mémoire "
          f"(non repris) : {doublons} ; lignes incomplètes ignorées : {incompletes}.")
    if not nouvelles:
        print("Rien à ajouter : la mémoire n'a pas été touchée.")
        return 0
    lecture.hors_du_plugin(memoire)
    archives = Path(a.archives) if a.archives else dossier_archives(memoire)
    if archives is not None:
        lecture.hors_du_plugin(archives)
    if not neuf and archives is None:
        arret("Dossier des sauvegardes inconnu : la mémoire n'est pas dans Références/Segments/. "
              "Préciser --archives <HERVÉ WORLD>/Core/Archives.")
    if not neuf:   # copie datée AVANT l'ajout, jamais écrasée
        archives.mkdir(parents=True, exist_ok=True)
        base = f"{memoire.stem}_avant_{datetime.now():%Y-%m-%d_%Hh%M}_{len(avant)}segments"
        cible, k = archives / f"{base}.csv", 1
        while cible.exists() and cible.read_bytes() != octets:
            k += 1
            cible = archives / f"{base}_{k}.csv"
        if not cible.exists():
            shutil.copy2(memoire, cible)
        print(f"Sauvegarde avant ajout : {cible}")
    d = ";" if neuf else (lecture.separateur(texte) or ";")
    fin = "\r\n" if "\r\n" in texte else "\n"
    tampon = io.StringIO()
    w = csv.writer(tampon, delimiter=d, lineterminator=fin)
    if neuf:
        w.writerow(["EN", "FR", "produit", "date"])
    w.writerows(nouvelles)
    ajout = ("" if neuf or texte.endswith(("\n", "\r")) else fin) + tampon.getvalue()
    copie = memoire.parent / f".ajout_{memoire.name}"
    memoire.parent.mkdir(parents=True, exist_ok=True)
    copie.write_bytes(("\ufeff".encode("utf-8") if neuf else octets) + ajout.encode("utf-8"))
    _, apres = lignes_memoire(copie.read_bytes().decode("utf-8-sig"))
    juste = len(apres) == len(avant) + len(nouvelles) and apres[:len(avant)] == avant and \
        [[c.strip() for c in l] for l in apres[len(avant):]] == nouvelles
    if not juste:
        copie.unlink()
        arret(f"Compte faux après l'ajout (avant {len(avant)} + {len(nouvelles)} ≠ après {len(apres)}, ou lignes "
              "d'avant modifiées) : la mémoire n'a PAS été touchée.")
    os.replace(copie, memoire)
    print(f"Ajouté : {len(nouvelles)} segments à la fin de {memoire.name} — après : {len(apres)} segments "
          f"(recompté sur le fichier écrit : {len(avant)} + {len(nouvelles)}).")
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
        # une colonne absente (« FR ») n'est jamais lue comme la colonne Excel FR, vide : refus, rien d'écrit
        vide = d / "vide.csv"
        code3, texte3 = _lancer(["aligner", str(bilingue), "--col-en", "Text", "--col-fr", "FR", "--produit", "Extension",
                                 "--date", "2026-11-20", "--sortie", str(vide)])
        if code3 != 2 or "introuvable" not in texte3 or vide.exists():
            manquent.append(f"--col-fr FR absent des en-têtes : refus attendu sans fichier écrit (vu code {code3})")
        print(f"  aligner : {'OK' if not manquent else 'ÉCHEC'}")
        if manquent:
            echecs.append(f"aligner — non trouvé : {manquent}")

        # chercher --sortie sur un fichier existant : refus, fichier intact
        notes = d / "notes.md"
        notes.write_text("NOTES D'HERVÉ\n", encoding="utf-8")
        code4, texte4 = _lancer(["chercher", str(source), "--memoire", str(memoire), "--sortie", str(notes)])
        ok4 = code4 == 2 and "existe déjà" in texte4 and notes.read_text(encoding="utf-8") == "NOTES D'HERVÉ\n"
        print(f"  chercher, fichier existant jamais remplacé : {'OK' if ok4 else 'ÉCHEC'}")
        if not ok4:
            echecs.append(f"chercher --sortie sur un fichier existant : refus attendu, fichier intact (vu code {code4})")

        # ajouter : les lignes d'« aligner » vont à la FIN de la mémoire, après une sauvegarde identique
        racine = d / "HERVÉ WORLD"
        seg = racine / "Références" / "Segments"
        seg.mkdir(parents=True)
        mem = seg / "Segments_Essai.csv"
        mem.write_bytes(memoire.read_bytes())
        original = mem.read_bytes()
        manquent = []
        code5, texte5 = _lancer(["ajouter", str(sortie), "--memoire", str(mem)])
        for m in ("avant : 3 segments ; à ajouter : 2 ; déjà en mémoire (non repris) : 0",
                  "après : 5 segments (recompté sur le fichier écrit : 3 + 2)"):
            if m not in texte5:
                manquent.append(m)
        attendu_mem = original.decode("utf-8").splitlines() + [
            "Shuffle the deck.;Mélangez la pioche.;Extension;2026-11-20",
            "Move up to 2 spaces.;Déplacez-vous d’au plus 2 cases.;Extension;2026-11-20"]
        if code5 != 0 or mem.read_bytes().decode("utf-8").splitlines() != attendu_mem:
            manquent.append(f"mémoire allongée des 2 lignes exactes, rien d'autre touché (code {code5})")
        sauvegardes = list((racine / "Core" / "Archives").glob("Segments_Essai_avant_*_3segments*.csv"))
        if len(sauvegardes) != 1 or sauvegardes[0].read_bytes() != original:
            manquent.append("sauvegarde datée identique à la mémoire d'avant")
        apres_un = mem.read_bytes()
        code6, texte6 = _lancer(["ajouter", str(sortie), "--memoire", str(mem)])
        if code6 != 0 or "déjà en mémoire (non repris) : 2" not in texte6 or mem.read_bytes() != apres_un \
                or len(list((racine / "Core" / "Archives").iterdir())) != 1:
            manquent.append("relancé avec les mêmes lignes : rien ajouté, rien sauvegardé de plus (pas de doublon)")
        hors = d / "Segments_Hors.csv"
        hors.write_bytes(original)
        code7, _ = _lancer(["ajouter", str(sortie), "--memoire", str(hors)])
        if code7 != 2 or hors.read_bytes() != original:
            manquent.append("mémoire hors de Références/Segments sans --archives : refus attendu, mémoire intacte")
        print(f"  ajouter : {'OK' if not manquent else 'ÉCHEC'}")
        if manquent:
            echecs.append(f"ajouter — non trouvé : {manquent}")
    if echecs:
        print("AUTO-TEST ÉCHOUÉ — " + " ; ".join(echecs) + ". Ne pas se fier à cette mémoire de traduction.")
        return 1
    print("AUTO-TEST OK — chercher : 2 identiques, 1 proche, 1 sans correspondance, 2 ignorés, tous bien classés, "
          "fichier existant jamais remplacé ; aligner : 2 nouveaux, 2 déjà connus, 1 conflit, 1 incomplet, fichier "
          "exact et jamais écrasé, colonne absente refusée ; ajouter : 3 + 2 = 5 segments, sauvegarde identique, "
          "aucun doublon au second passage, refus sans dossier d'archives ; 0 traduction proposée à tort")
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
    aj = sub.add_parser("ajouter", help="ajoute à la fin de la mémoire les lignes produites par « aligner »")
    aj.add_argument("lignes", help="le fichier .csv produit par « aligner » (EN;FR;produit;date)")
    aj.add_argument("--memoire", required=True, help="Références/Segments/Segments_<Gamme>.csv (créée si absente)")
    aj.add_argument("--archives", help="dossier des sauvegardes (défaut : <HERVÉ WORLD>/Core/Archives)")
    a = ap.parse_args()
    if a.commande == "chercher" and not 0 < a.seuil <= 1:
        arret("--seuil doit être entre 0 et 1.")
    if a.commande == "chercher":
        sortie_libre(a.sortie)
    try:
        return {"chercher": chercher, "aligner": aligner, "ajouter": ajouter}[a.commande](a)
    except (OSError, KeyError, ValueError) as e:
        arret(f"Lecture impossible : {e}")


if __name__ == "__main__":
    sys.exit(main())
