#!/usr/bin/env python3
"""Longueur, débord et intégrité des balises, icônes et nombres entre la source anglaise et la traduction.

Usage :
  python3 longueurs.py TABLEUR --en NOM --fr NOM [--id NOM] [--seuil 1.25] [--max N] [--max-col NOM]
  python3 longueurs.py SOURCE.docx CIBLE.docx [--seuil 1.25]
  python3 longueurs.py --auto-test

Tableur (.xlsx/.csv) : une ligne par carte ou par champ, colonnes EN et FR (en-têtes exacts).
  --id NOM       colonne d'identifiant (n° de carte) pour le rapport
  --seuil R      alerte si longueur FR / longueur EN dépasse R (défaut 1.25 = +25 %) et d'au moins 10 caractères
  --max N        alerte si le texte FR dépasse N caractères (cadre de texte connu)
  --max-col NOM  colonne qui donne la longueur maximale ligne par ligne (si l'éditeur la fournit)
Deux Word : comparés paragraphe par paragraphe seulement s'ils ont le même nombre de paragraphes.

Contrôles : (L) longueur au-delà du seuil ou du maximum ; (B) balises ou icônes différentes entre EN et FR ;
(N) nombres différents entre EN et FR ; (V) traduction vide. Tout le fichier est lu.
"""
import argparse, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

BALISE = re.compile(r"\{[^{}\n]{1,40}\}|<[^<>\n]{1,40}>|\[[^\[\]\n]{1,40}\]")
NOMBRE = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?(?![\w])")
MOTS_NOMBRES = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6"}


def nombres(texte, anglais):
    vus = [n.replace(",", ".") for n in NOMBRE.findall(BALISE.sub(" ", texte))]
    if anglais:
        for mot, chiffre in MOTS_NOMBRES.items():
            vus += [chiffre] * len(re.findall(rf"\b{mot}\b", texte, re.I))
    return Counter(vus)


def controler_paire(en, fr, seuil, maxi):
    alertes = []
    if en.strip() and not fr.strip():
        return [("V", "traduction vide")]
    if not en.strip():
        return []
    le, lf = len(en), len(fr)
    if maxi and lf > maxi:
        alertes.append(("L", f"{lf} caractères pour un maximum de {maxi} (+{lf - maxi})"))
    elif le and lf / le > seuil and lf - le >= 10:
        alertes.append(("L", f"{lf} caractères contre {le} en anglais ({lf / le:.0%})"))
    be, bf = Counter(BALISE.findall(en)), Counter(BALISE.findall(fr))
    if be != bf:
        manque = list((be - bf).elements())
        trop = list((bf - be).elements())
        alertes.append(("B", "balises/icônes " + (f"manquantes {manque} " if manque else "") + (f"en trop {trop}" if trop else "")))
    ne, nf = nombres(en, True), nombres(fr, False)
    if ne != nf:
        # les chiffres écrits en toutes lettres en français (« deux ») ne sont pas des erreurs : on signale, on ne tranche pas
        alertes.append(("N", f"nombres différents : EN {sorted(ne.elements())} / FR {sorted(nf.elements())} — à vérifier"))
    return alertes


def depuis_tableur(chemin, col_en, col_fr, col_id, col_max):
    p = Path(chemin)
    feuilles = lecture.feuilles_xlsx(p) if p.suffix.lower() == ".xlsx" else {"": lecture.lignes_csv(p)}
    paires = []
    for feuille, lignes in feuilles.items():
        for i, ligne in enumerate(lignes):
            norm = [str(c).strip().lower() for c in ligne]
            if col_en.lower() in norm and col_fr.lower() in norm:
                ie, if_ = norm.index(col_en.lower()), norm.index(col_fr.lower())
                ii = norm.index(col_id.lower()) if col_id and col_id.lower() in norm else None
                im = norm.index(col_max.lower()) if col_max and col_max.lower() in norm else None
                for j, l in enumerate(lignes[i + 1:], i + 2):
                    get = lambda k: str(l[k]) if k is not None and k < len(l) else ""
                    rep = get(ii) or (f"{feuille}!L{j}" if feuille else f"L{j}")
                    mx = get(im)
                    paires.append((rep, get(ie), get(if_), int(float(mx)) if mx.strip() else None))
                break
    if not paires:
        raise SystemExit(f"Colonnes « {col_en} » et « {col_fr} » introuvables ensemble dans {p.name}.")
    return paires


def auto_test():
    cas = [
        ("c1", "Draw 2 cards.", "Piochez 2 cartes.", None),                         # propre
        ("c2", "Gain {gold} 3.", "Gagnez 3.", None),                                # balise perdue
        ("c3", "Discard 1 card.", "Défaussez 2 cartes.", None),                     # nombre changé
        ("c4", "Rest.", "Reposez-vous complètement et longuement.", None),          # débord
        ("c5", "Flee.", "", None),                                                  # vide
    ]
    attendu = {"c2": {"B"}, "c3": {"N"}, "c4": {"L"}, "c5": {"V"}}
    obtenu = {}
    for rep, en, fr, mx in cas:
        a = {x[0] for x in controler_paire(en, fr, 1.25, mx)}
        if a:
            obtenu[rep] = a
    if obtenu != attendu:
        print(f"AUTO-TEST ÉCHOUÉ — obtenu {obtenu}, attendu {attendu}")
        return 1
    print("AUTO-TEST OK — 4 fautes glissées exprès (balise, nombre, débord, vide) trouvées ; 0 fausse alerte sur la carte propre")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichiers", nargs="*")
    ap.add_argument("--en"); ap.add_argument("--fr"); ap.add_argument("--id")
    ap.add_argument("--seuil", type=float, default=1.25)
    ap.add_argument("--max", type=int)
    ap.add_argument("--max-col")
    ap.add_argument("--auto-test", action="store_true")
    a = ap.parse_args()
    if a.auto_test:
        sys.exit(auto_test())
    if len(a.fichiers) == 1:
        if not (a.en and a.fr):
            ap.error("pour un tableur, donne --en et --fr (en-têtes exacts des colonnes)")
        paires = depuis_tableur(a.fichiers[0], a.en, a.fr, a.id, a.max_col)
        titre = Path(a.fichiers[0]).name
    elif len(a.fichiers) == 2:
        pe = [t for t in lecture.paragraphes_docx(a.fichiers[0]) if t.strip()]
        pf = [t for t in lecture.paragraphes_docx(a.fichiers[1]) if t.strip()]
        if len(pe) != len(pf):
            print(f"Les deux fichiers n'ont pas le même nombre de paragraphes non vides (EN {len(pe)}, FR {len(pf)}) : "
                  "je ne peux pas les aligner sans risque d'erreur. Contrôle impossible en l'état.")
            sys.exit(1)
        paires = [(f"§{i}", e, f, None) for i, (e, f) in enumerate(zip(pe, pf), 1)]
        titre = f"{Path(a.fichiers[0]).name} → {Path(a.fichiers[1]).name}"
    else:
        ap.error("un tableur, ou deux fichiers Word, ou --auto-test")
    total = Counter()
    lignes = []
    for rep, en, fr, mx in paires:
        for code, msg in controler_paire(en, fr, a.seuil, mx or a.max):
            total[code] += 1
            lignes.append(f"  {rep}  [{code}] {msg}")
    lib = {"L": "longueur / débord", "B": "balises ou icônes", "N": "nombres", "V": "traductions vides"}
    print(f"Longueurs et intégrité — {titre} — {len(paires)} lignes lues en entier (seuil {a.seuil:.0%})")
    if not total:
        print("0 alerte. (Le contrôle se prouve avec --auto-test : il doit trouver les fautes glissées exprès.)")
    else:
        print(", ".join(f"{lib[k]} : {total[k]}" for k in "LBNV" if total[k]))
        print("\n".join(lignes))


if __name__ == "__main__":
    main()
