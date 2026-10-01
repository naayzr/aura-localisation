#!/usr/bin/env python3
"""Recherche globale d'un ou plusieurs mots dans un fichier, avec l'endroit de chaque occurrence.

Remplace la recherche Word quand il faut vérifier UN point partout : « est-ce que "Bouger" traîne
encore quelque part ? », « combien de fois "Exhaust" est-il resté en anglais ? », « où est écrit
"Point de Victoire" avec une majuscule ? ».

Usage :
  python3 chercher.py FICHIER MOT [MOT ...] [--liste mots.txt] [--debut] [--strict] [--max 30]
  python3 chercher.py FICHIER --liste Glossaire.xlsx --colonne EN [--si STATUT=Archivé]
  python3 chercher.py --auto-test

  MOT        un mot ou une expression (« point de victoire »), entre guillemets s'il y a des espaces.
  --liste    un fichier texte : un mot ou une expression par ligne (ex. : les noms anglais des icônes) ;
             ou un tableur (.xlsx, .csv) avec --colonne.
  --colonne  avec --liste sur un tableur : ne prendre que la colonne dont l'en-tête est NOM
             (ex. EN = les termes anglais du glossaire, pour trouver ceux restés en anglais).
  --si       avec --colonne : ne garder que les lignes où COLONNE vaut VALEUR
             (ex. STATUT=Archivé = les formes refusées, qui ne doivent plus apparaître).
  --auto-test  essai sur un texte saboté de fautes connues : la recherche doit toutes les trouver.
  --debut    trouve aussi les mots qui COMMENCENT par MOT (« déplac » → déplacer, déplacez, déplacement).
  --racine   comme --debut, mais AURA coupe d'abord la terminaison de chaque mot (« Bouger » → « boug »,
             qui trouve bougez, bouge, bougeant… et aussi « bougie » : chaque occurrence se regarde).
  --strict   respecte la casse et les accents (sinon : « deplacer » trouve « Déplacer »).
  --max      nombre maximal d'occurrences affichées par mot (le total est toujours compté en entier).

Formats lus : .docx .xlsx .csv .tsv .txt .md (par lecture.py, copie identique dans ce dossier).
Repères : §12 = 12e paragraphe Word (tableaux compris), L5 = 5e ligne, Cartes!L5C3 = cellule.
Apostrophes droite et courbe, espaces ordinaire et insécables sont traitées comme identiques pour la
recherche (leur contrôle relève du skill typographie-fr).

Code de sortie : 0 = recherche faite (même avec 0 occurrence) ; 2 = fichier illisible.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

EQUIVALENTS = {
    chr(0x2019): "'", chr(0x2018): "'", chr(0x02BC): "'",            # apostrophes
    chr(0xA0): " ", chr(0x202F): " ", chr(0x2009): " ", "\t": " ",    # espaces
}


def normaliser(texte, strict):
    """Un caractère donne exactement un caractère : les positions restent celles du texte d'origine."""
    sortie = []
    for c in texte:
        c = EQUIVALENTS.get(c, c)
        if not strict:
            bas = unicodedata.normalize("NFD", c)[0].lower()
            c = bas if len(bas) == 1 else c
        sortie.append(c)
    return "".join(sortie)


TERMINAISONS = ("ent", "ez", "er", "ir", "re", "es", "e", "s", "x")


def racine(morceau):
    """Coupe une terminaison courante (verbe, pluriel), en gardant au moins 3 lettres."""
    for fin in TERMINAISONS:
        if morceau.endswith(fin) and len(morceau) - len(fin) >= 3:
            return morceau[: -len(fin)]
    return morceau


def motif(mot, strict, debut, par_racine=False):
    morceaux = normaliser(mot.strip(), strict).split()
    if par_racine:
        m = " +".join(re.escape(racine(x)) + r"\w*" for x in morceaux)
        return re.compile(rf"(?<!\w){m}")
    m = " +".join(re.escape(x) for x in morceaux)
    fin = r"\w*" if debut else r"(?!\w)"
    return re.compile(rf"(?<!\w){m}{fin}")


def liste_depuis_tableur(chemin, colonne, condition):
    """Valeurs d'une colonne (repérée par son en-tête) d'un .xlsx ou .csv, filtrées par --si."""
    ext = Path(chemin).suffix.lower()
    feuilles = lecture.feuilles_xlsx(chemin) if ext == ".xlsx" else {"": lecture.lignes_csv(chemin)}
    cle = lambda s: str(s).strip().lower()  # noqa: E731
    filtre_col, filtre_val = (condition.split("=", 1) + [""])[:2] if condition else (None, None)
    for lignes in feuilles.values():
        for i, ligne in enumerate(lignes):
            entetes = [cle(c) for c in ligne]
            if cle(colonne) not in entetes:
                continue
            j = entetes.index(cle(colonne))
            k = entetes.index(cle(filtre_col)) if filtre_col and cle(filtre_col) in entetes else None
            if filtre_col and k is None:
                raise ValueError(f"colonne « {filtre_col} » absente à côté de « {colonne} »")
            valeurs = []
            for l in lignes[i + 1:]:
                if j < len(l) and str(l[j]).strip():
                    if k is None or (k < len(l) and cle(l[k]) == cle(filtre_val)):
                        valeurs.append(str(l[j]).strip())
            return valeurs
    raise ValueError(f"aucune colonne d'en-tête « {colonne} » dans {Path(chemin).name}")


def auto_test():
    """Texte saboté : 3 fautes connues glissées exprès ; la recherche doit les trouver toutes."""
    import tempfile
    texte = ("Déplacez-vous de 3 cases maximum.\n"
             "Puis bougez encore d'une case.\n"           # faute 1 : variante refusée « Bouger », conjuguée
             "Le joueur actif peut Exhaust une carte.\n"   # faute 2 : nom anglais oublié
             "Deplacez votre pion.\n")                     # faute 3 : accent manquant, doit être trouvée
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "sabote.txt"
        f.write_text(texte, encoding="utf-8")
        segs = [(r, t, normaliser(t, False)) for r, t in lecture.textes(f)]
        def compte(mot, debut=False, par_racine=False):
            rx = motif(mot, False, debut, par_racine)
            return sum(len(list(rx.finditer(n))) for _, _, n in segs)
        essais = [("Bouger", False, True, 1), ("exhaust", False, False, 1), ("déplac", True, False, 2)]
        ok = True
        for mot, debut, par_racine, attendu in essais:
            n = compte(mot, debut, par_racine)
            print(f"  « {mot} » : {n} trouvé(s), {attendu} attendu(s) — {'OK' if n == attendu else 'ÉCHEC'}")
            ok &= n == attendu
    print("AUTO-TEST " + ("OK — les 3 fautes glissées sont trouvées." if ok else "ÉCHOUÉ : ne pas se fier à cette recherche."))
    sys.exit(0 if ok else 1)


def main():
    if "--auto-test" in sys.argv:
        auto_test()
    ap = argparse.ArgumentParser(description="Recherche globale avec l'endroit de chaque occurrence.")
    ap.add_argument("fichier")
    ap.add_argument("mots", nargs="*")
    ap.add_argument("--liste", help="fichier texte (un mot par ligne) ou tableur avec --colonne")
    ap.add_argument("--colonne", help="tableur : en-tête de la colonne à prendre comme liste")
    ap.add_argument("--si", help="tableur : COLONNE=VALEUR, ne garder que ces lignes")
    ap.add_argument("--debut", action="store_true", help="mots qui commencent par MOT")
    ap.add_argument("--racine", action="store_true", help="couper la terminaison puis chercher le début de mot")
    ap.add_argument("--strict", action="store_true", help="respecter la casse et les accents")
    ap.add_argument("--max", type=int, default=30)
    a = ap.parse_intermixed_args()  # les options peuvent venir entre les mots

    mots = list(a.mots)
    try:
        if a.liste and a.colonne:
            mots += liste_depuis_tableur(a.liste, a.colonne, a.si)
        elif a.liste:
            mots += [l for _, l in lecture.textes(a.liste)]
        segments = lecture.textes(a.fichier)
    except Exception as e:  # fichier absent, zip abîmé, format non pris en charge
        print(f"Fichier illisible : {e}")
        sys.exit(2)
    mots = list(dict.fromkeys(m.strip() for m in mots if m.strip() and not m.strip().startswith("#")))
    if not mots:
        print("Aucun mot à chercher : donne au moins un MOT ou --liste.")
        sys.exit(2)

    normes = [(rep, txt, normaliser(txt, a.strict)) for rep, txt in segments]
    mode = ("casse et accents respectés" if a.strict else "sans tenir compte de la casse ni des accents") + \
           (", par racine" if a.racine else ", début de mot" if a.debut else ", mot entier")
    print(f"RECHERCHE — {Path(a.fichier).name} — {len(segments)} segments lus — {mode}")
    print()
    bilan = []
    for mot in mots:
        rx = motif(mot, a.strict, a.debut, a.racine)
        trouves = []
        formes = {}
        for rep, txt, norm in normes:
            for m in rx.finditer(norm):
                s, e = m.span()
                forme = txt[s:e]
                formes[forme] = formes.get(forme, 0) + 1
                g, d = max(0, s - 40), min(len(txt), e + 40)
                ctx = ("…" if g else "") + txt[g:s] + "[[" + forme + "]]" + txt[e:d] + ("…" if d < len(txt) else "")
                trouves.append((rep, ctx.replace("\n", " ")))
        bilan.append((mot, len(trouves), formes))
        print(f"« {mot} » : {len(trouves)} occurrence(s)"
              + (" — formes : " + ", ".join(f"{f} ({n})" for f, n in sorted(formes.items(), key=lambda x: -x[1])) if formes else ""))
        for rep, ctx in trouves[: a.max]:
            print(f"  {rep} : {ctx}")
        if len(trouves) > a.max:
            print(f"  … et {len(trouves) - a.max} de plus (--max pour tout afficher)")
        print()
    print("BILAN")
    for mot, n, formes in bilan:
        print(f"  {n:>6}  {mot}" + (f"  ({len(formes)} forme(s) différente(s))" if len(formes) > 1 else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
