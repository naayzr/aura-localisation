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
  --max-col NOM  colonne qui donne la longueur maximale ligne par ligne (si l'éditeur la fournit) ;
                 une case qui n'est pas un nombre est signalée et ignorée
Une colonne demandée (--en, --fr, --id, --max-col) qui n'est pas dans les en-têtes arrête le programme :
jamais de colonne lue vide en silence.
Deux Word : comparés paragraphe par paragraphe seulement s'ils ont le même nombre de paragraphes.

Contrôles : (L) longueur au-delà du seuil ou du maximum ; (B) balises ou icônes différentes entre EN et FR ;
(N) nombres différents entre EN et FR, séparateurs de milliers ignorés (1,000 = 1 000) ; (V) traduction vide.
Tout le fichier est lu.
"""
import argparse, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

BALISE = lecture.BALISE      # écrit une seule fois, dans lecture.py (le même pour comptage-caracteres)
NOMBRE = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?(?![\w])")
MOTS_NOMBRES = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6"}
# Séparateur de milliers, retiré avant de comparer : virgule en anglais (1,000), espace ordinaire ou
# insécable en français (1 000) ; seulement entre un chiffre et un groupe d'exactement 3 chiffres
MILLIERS_EN = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")
MILLIERS_FR = re.compile(r"(?<=\d)[ \u00a0\u202f](?=\d{3}(?!\d))")


def nombres(texte, anglais):
    sans = (MILLIERS_EN if anglais else MILLIERS_FR).sub("", BALISE.sub(" ", texte))
    vus = [n.replace(",", ".") for n in NOMBRE.findall(sans)]
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
    """(paires (repère, EN, FR, maximum), avertissements). Une colonne demandée absente arrête tout."""
    p = Path(chemin)
    feuilles = lecture.feuilles_xlsx(p) if p.suffix.lower() == ".xlsx" else {"": lecture.lignes_csv(p)}
    paires, avertissements, vue = [], [], False
    for feuille, lignes in feuilles.items():
        for i, ligne in enumerate(lignes):
            norm = [str(c).strip().lower() for c in ligne]
            if col_en.lower() in norm and col_fr.lower() in norm:
                vue = True
                absentes = [c for c in (col_id, col_max) if c and c.lower() not in norm]
                if absentes:
                    raise SystemExit(f"Colonne « {absentes[0]} » introuvable dans les en-têtes de {p.name} "
                                     f"(en-têtes lus : {', '.join(c for c in ligne if str(c).strip())}). "
                                     "Rien n'a été contrôlé.")
                ie, if_ = norm.index(col_en.lower()), norm.index(col_fr.lower())
                ii = norm.index(col_id.lower()) if col_id else None
                im = norm.index(col_max.lower()) if col_max else None
                for j, l in enumerate(lignes[i + 1:], i + 2):
                    get = lambda k: str(l[k]) if k is not None and k < len(l) else ""
                    rep = get(ii) or (f"{feuille}!L{j}" if feuille else f"L{j}")
                    mx, maxi = get(im).strip(), None
                    if mx:
                        try:
                            maxi = int(float(mx.replace(",", ".")))
                        except ValueError:
                            avertissements.append(f"  {rep}  maximum illisible « {mx} » (ligne {j}) : ignoré pour cette ligne")
                    paires.append((rep, get(ie), get(if_), maxi))
                break
    if not vue:
        lues = []
        for feuille, lignes in feuilles.items():
            premiere = next((l for l in lignes if any(str(c).strip() for c in l)), [])
            lues.append(f"{feuille or p.name} : {', '.join(str(c).strip() for c in premiere if str(c).strip())[:120] or '(vide)'}")
        raise SystemExit(f"Colonnes « {col_en} » et « {col_fr} » introuvables ensemble dans {p.name}. "
                         f"Premières lignes lues — {' ; '.join(lues)}. Rien n'a été contrôlé.")
    if not paires:
        raise SystemExit(f"{p.name} : aucune ligne sous les en-têtes « {col_en} » et « {col_fr} ». Rien n'a été contrôlé.")
    return paires, avertissements


def auto_test():
    cas = [
        ("c1", "Draw 2 cards.", "Piochez 2 cartes.", None),                         # propre
        ("c2", "Gain {gold} 3.", "Gagnez 3.", None),                                # balise perdue
        ("c3", "Discard 1 card.", "Défaussez 2 cartes.", None),                     # nombre changé
        ("c4", "Rest.", "Reposez-vous complètement et longuement.", None),          # débord
        ("c5", "Flee.", "", None),                                                  # vide
    ]
    cas += [
        ("c6", "Gain 10,000 gold.", "Gagnez 10\u202f000 or.", None),                  # propre : milliers
        ("c7", "Draw 1,000 cards.", "Piochez 1 000 cartes.", None),                   # propre : milliers
        ("c8", "If your score is < 3 and B's is > 5, you win.",
               "Si votre score est < 3 et celui de B > 5, vous gagnez.", None),        # propre : pas une balise
        ("c9", "Gain [b]2[/b] {gold}.", "Gagnez [b]2[/b].", None),                     # balise perdue
    ]
    attendu = {"c2": {"B"}, "c3": {"N"}, "c4": {"L"}, "c5": {"V"}, "c9": {"B"}}
    obtenu = {}
    for rep, en, fr, mx in cas:
        a = {x[0] for x in controler_paire(en, fr, 1.25, mx)}
        if a:
            obtenu[rep] = a
    if obtenu != attendu:
        print(f"AUTO-TEST ÉCHOUÉ — obtenu {obtenu}, attendu {attendu}")
        return 1
    echecs = auto_test_tableur()
    if echecs:
        print(f"AUTO-TEST ÉCHOUÉ — tableur piégé : {echecs}")
        return 1
    print(f"AUTO-TEST OK — {len(attendu)} fautes glissées exprès (balise, nombre, débord, vide) trouvées ; "
          f"0 fausse alerte sur les {len(cas) - len(attendu)} cartes propres (milliers, « < 3 … > ») ; "
          "tableur piégé bien traité (maximum illisible signalé, colonne absente refusée)")
    return 0


def auto_test_tableur():
    """Un CSV avec une case « N/A » dans la colonne des maximums, et des noms de colonnes absents."""
    import tempfile
    echecs = []
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "cartes.csv"
        f.write_text("Carte;EN;FR;Max\nC1;Rest.;Reposez-vous.;N/A\nC2;Flee.;Fuyez à toutes jambes.;10\n", encoding="utf-8")
        try:
            paires, avert = depuis_tableur(f, "EN", "FR", "Carte", "Max")
        except (SystemExit, ValueError) as e:
            return [f"case « N/A » dans --max-col : le programme s'arrête ({e!r}) au lieu de la signaler"]
        if len(avert) != 1 or "C1" not in avert[0] or paires[1][3] != 10:
            echecs.append(f"case « N/A » : avertissements {avert}, maximums {[x[3] for x in paires]}")
        for col_id, col_max in (("Carte", "Maximum"), ("ID", "Max")):
            try:
                depuis_tableur(f, "EN", "FR", col_id, col_max)
                echecs.append(f"colonne absente (--id {col_id} --max-col {col_max}) lue vide sans arrêt")
            except SystemExit:
                pass
    return echecs


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
        try:
            paires, avertissements = depuis_tableur(a.fichiers[0], a.en, a.fr, a.id, a.max_col)
        except ValueError as e:                   # format non pris en charge, octets nuls
            raise SystemExit(f"{Path(a.fichiers[0]).name} : {e} Rien n'a été contrôlé.")
        titre = Path(a.fichiers[0]).name
    elif len(a.fichiers) == 2:
        pe = [t for t in lecture.paragraphes_docx(a.fichiers[0]) if t.strip()]
        pf = [t for t in lecture.paragraphes_docx(a.fichiers[1]) if t.strip()]
        if len(pe) != len(pf):
            print(f"Les deux fichiers n'ont pas le même nombre de paragraphes non vides (EN {len(pe)}, FR {len(pf)}) : "
                  "je ne peux pas les aligner sans risque d'erreur. Contrôle impossible en l'état.")
            sys.exit(1)
        paires = [(f"§{i}", e, f, None) for i, (e, f) in enumerate(zip(pe, pf), 1)]
        titre, avertissements = f"{Path(a.fichiers[0]).name} → {Path(a.fichiers[1]).name}", []
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
    if avertissements:
        print(f"Maximums illisibles ({len(avertissements)}), lignes contrôlées sans maximum propre :")
        print("\n".join(avertissements))


if __name__ == "__main__":
    main()
