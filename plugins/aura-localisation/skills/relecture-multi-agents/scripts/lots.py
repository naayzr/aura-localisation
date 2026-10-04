#!/usr/bin/env python3
"""Découpe un texte à relire en lots, et écrit le plan de la relecture AVANT qu'elle commence.

Usage :
  python3 lots.py FICHIER [--taille 30000] [--relecteurs 0] [--angles logique,style,renvois]
                          [--plan DOSSIER] [--controles typographie,longueur,glossaire,comptage,renvois]

  --taille      nombre maximal de caractères par lot (espaces comprises). Défaut : 30 000.
  --relecteurs  0 = relecture standard (AURA lit les lots elle-même, l'un après l'autre) ;
                N = relecture à N relecteurs en parallèle (un relecteur par angle et par lot).
  --angles      les angles des relecteurs parallèles (autant que --relecteurs). Défaut : logique,style,renvois.
  --plan        dossier où écrire PLAN.txt : la liste des rapports attendus. Le plan s'écrit AVANT la
                relecture et ne se réécrit pas (si PLAN.txt existe, le script refuse : prends un autre dossier).
  --controles   les contrôles automatiques prévus (un rapport chacun). Défaut : les cinq.

Le découpage suit les segments (paragraphes Word, lignes, cellules) et coupe de préférence juste avant
un titre (segment court sans ponctuation finale, ou qui commence par un numéro de règle, « Chapitre »…).
Un segment plus long que --taille forme un lot à lui seul (signalé).

Le nombre de caractères sert à découper et à annoncer un ordre de grandeur. Le compte qui part sur un
devis ou une facture vient du skill comptage-caracteres, pas d'ici.

Formats lus : .docx .xlsx .csv .tsv .txt .md (par lecture.py, copie identique dans ce dossier).

  python3 lots.py --auto-test
      découpe un texte fabriqué dont les lots ont été calculés à la main (coupe avant un titre, segment
      trop long seul et signalé), écrit puis refuse de réécrire un PLAN.txt, et vérifie l'annonce des
      relecteurs parallèles (plus de 3 lancements signalés, 3 ou moins sans alerte).

Codes de sortie : 0 = plan produit ; 1 = auto-test en échec ; 2 = fichier illisible, ou plan refusé
(PLAN.txt existe déjà).
"""
import argparse
import contextlib
import io
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

TITRE = re.compile(r"^\s*(?:(?:chapitre|chapter|partie|part|section|annexe|appendix)\b|\d{1,3}(?:\.\d{1,3})*\.?\s+\S)",
                   re.IGNORECASE)
# Ordre de grandeur annoncé à Hervé : en français, de l'ordre de 3 à 4 caractères par jeton.
# C'est une estimation, pas une mesure : elle sert à dire « environ », jamais à facturer.
CAR_PAR_JETON = (4, 3)


def est_titre(texte):
    t = texte.strip()
    return bool(TITRE.match(t)) or (len(t) <= 80 and not re.search(r"[.!?:;…»)]$", t) and len(t.split()) <= 10)


def decouper(segments, taille):
    lots, courant, taille_courante = [], [], 0
    for seg in segments:
        n = len(seg[1])
        while courant and taille_courante + n > taille:
            # Couper juste avant le dernier titre de la 2e moitié du lot, s'il y en a un ; sinon ici.
            coupe, cumul = None, 0
            for i, (_, t) in enumerate(courant):
                if i > 0 and cumul >= taille_courante / 2 and est_titre(t):
                    coupe = i
                cumul += len(t)
            if coupe:
                lots.append(courant[:coupe])
                courant = courant[coupe:]
            else:
                lots.append(courant)
                courant = []
            taille_courante = sum(len(t) for _, t in courant)
        courant.append(seg)
        taille_courante += n
    if courant:
        lots.append(courant)
    return lots


def fourchette(caracteres):
    bas, haut = (round(caracteres / c) for c in CAR_PAR_JETON)
    return f"{bas:,} à {haut:,}".replace(",", " ")


def nombre(n):
    return f"{n:,}".replace(",", " ")


# ------------------------------------------------------------------ auto-test
def _lancer(argv):
    """Lance le vrai programme (main) avec ces options ; renvoie (code de sortie, texte affiché)."""
    ancien, sortie = sys.argv, io.StringIO()
    sys.argv = ["lots.py"] + argv
    try:
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            try:
                main()
                code = 0
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = ancien
    return code, sortie.getvalue()


def auto_test():
    """Texte fabriqué : 10 segments de longueur connue. Les lots attendus ont été calculés à la main
    pour une taille de 1 000 caractères, jamais recalculés par le programme qu'on vérifie."""
    def para(n):  # paragraphe de n caractères exactement, terminé par un point (donc pas un titre)
        return ("Le joueur actif pioche une carte, puis la défausse. " * 40)[:n - 1] + "."
    segments = ["Chapitre 1", para(400), para(400), "Chapitre 2", para(400), para(400),
                "Chapitre 3", para(400), para(1500), para(300)]
    echecs = []
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        f = d / "livret é.txt"
        f.write_text("\n".join(segments) + "\n", encoding="utf-8")
        code, texte = _lancer([str(f), "--taille", "1000"])
        attendus = ["10 segments · 3 830 caractères (espaces comprises) · 5 lot(s) de 1 000 caractères au plus",
                    "lot-01 : L1 → L3 · 3 segment(s) · 810 caractères\n",       # coupé juste avant « Chapitre 2 »
                    "lot-02 : L4 → L6 · 3 segment(s) · 810 caractères\n",       # coupé juste avant « Chapitre 3 »
                    "lot-03 : L7 → L8 · 2 segment(s) · 410 caractères\n",
                    "lot-04 : L9 → L9 · 1 segment(s) · 1 500 caractères  ← un seul segment, plus long que la taille de lot",
                    "lot-05 : L10 → L10 · 1 segment(s) · 300 caractères\n",
                    "Relecture STANDARD (sans relecteur parallèle)"]
        manquent = [a.strip() for a in attendus if a not in texte] + ([f"code 0 (vu {code})"] if code != 0 else [])
        if texte.count("← un seul segment") != 1:
            manquent.append(f"un seul lot signalé trop long (vu {texte.count('← un seul segment')})")
        print(f"  découpage : {'OK' if not manquent else 'ÉCHEC'}")
        if manquent:
            echecs.append(f"découpage — non trouvé : {manquent}")

        dossier = d / "relecture"
        code, texte = _lancer([str(f), "--taille", "1000", "--plan", str(dossier)])
        plan = dossier / "PLAN.txt"
        prevus = [l for l in plan.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")] \
            if plan.exists() else []
        attendu_plan = ["controle-typographie", "controle-longueur", "controle-glossaire", "controle-comptage",
                        "controle-renvois", "lot-01", "lot-02", "lot-03", "lot-04", "lot-05"]
        manquent = [] if (code == 0 and prevus == attendu_plan) else [f"PLAN.txt : attendu {attendu_plan}, vu {prevus} (code {code})"]
        avant = plan.read_bytes() if plan.exists() else b""
        code2, texte2 = _lancer([str(f), "--taille", "500", "--plan", str(dossier)])
        if code2 != 2 or "PLAN REFUSÉ" not in texte2 or (plan.read_bytes() if plan.exists() else b"") != avant:
            manquent.append("second plan dans le même dossier : refus attendu (code 2), PLAN.txt inchangé")
        print(f"  plan écrit, puis jamais réécrit : {'OK' if not manquent else 'ÉCHEC'}")
        if manquent:
            echecs.append(" ; ".join(manquent))

        manquent = []
        code, texte = _lancer([str(f), "--taille", "1000", "--relecteurs", "2"])      # 2 × 5 lots = 10
        if "2 relecteurs en même temps × 5 lot(s) = 10 lancement(s)" not in texte or "10 LANCEMENTS, PLUS DE 3" not in texte:
            manquent.append("2 relecteurs × 5 lots : 10 lancements annoncés, avec l'alerte « plus de 3 »")
        code, texte = _lancer([str(f), "--taille", "100000", "--relecteurs", "3"])    # 3 × 1 lot = 3
        if "3 relecteurs en même temps × 1 lot(s) = 3 lancement(s)" not in texte or "PLUS DE 3" in texte:
            manquent.append("3 relecteurs × 1 lot : 3 lancements, sans alerte (fausse alerte ou compte faux)")
        code, texte = _lancer([str(f), "--relecteurs", "4"])                          # 3 angles par défaut
        if code != 2 or "Il faut 4 angles" not in texte:
            manquent.append("4 relecteurs pour 3 angles : refus attendu (code 2)")
        dans_plugin = Path(__file__).resolve().parent / "plan_essai"           # le dossier du plugin
        code, texte = _lancer([str(f), "--plan", str(dans_plugin)])
        if code != 2 or "REFUS" not in texte or dans_plugin.exists():
            manquent.append(f"--plan dans le dossier du plugin : refus attendu (code 2), vu le code {code}")
        for args, quoi in ((["--taille", "0"], "--taille 0"), (["--relecteurs", "-1"], "--relecteurs -1")):
            code, texte = _lancer([str(f)] + args)                                     # valeurs absurdes
            if code != 2 or "Valeur refusée" not in texte:
                manquent.append(f"{quoi} : refus attendu (code 2), vu le code {code}")
        print(f"  annonce des relecteurs parallèles : {'OK' if not manquent else 'ÉCHEC'}")
        if manquent:
            echecs.append(" ; ".join(manquent))
    if echecs:
        print("AUTO-TEST ÉCHOUÉ — " + " ; ".join(echecs) + ". Ne pas se fier à ce plan de relecture.")
        return 1
    print("AUTO-TEST OK — 5 lots calculés à la main retrouvés (coupes avant les titres, segment trop long seul et "
          "signalé) ; PLAN.txt écrit puis refusé en réécriture ; plus de 3 lancements signalés ; 0 fausse alerte "
          "(un seul lot signalé, 3 lancements sans alerte)")
    return 0


def main():
    if "--auto-test" in sys.argv[1:]:
        sys.exit(auto_test())
    ap = argparse.ArgumentParser(description="Découpe en lots et plan de relecture.",
                                 epilog="--auto-test : essai sur un texte fabriqué par le programme.")
    ap.add_argument("fichier")
    ap.add_argument("--taille", type=int, default=30000)
    ap.add_argument("--relecteurs", type=int, default=0)
    ap.add_argument("--angles", default="logique,style,renvois")
    ap.add_argument("--plan")
    ap.add_argument("--controles", default="typographie,longueur,glossaire,comptage,renvois")
    a = ap.parse_args()
    if a.taille < 1 or a.relecteurs < 0:
        print(f"Valeur refusée : --taille doit être au moins 1 (reçu {a.taille}), --relecteurs au moins 0 (reçu {a.relecteurs}).")
        sys.exit(2)

    try:
        segments = lecture.textes(a.fichier)
    except Exception as e:  # fichier absent, zip abîmé, format non pris en charge
        print(f"Fichier illisible : {e}")
        sys.exit(2)
    if not segments:
        print("Le fichier ne contient aucun texte lisible.")
        sys.exit(2)

    angles = [x.strip() for x in a.angles.split(",") if x.strip()]
    if a.relecteurs:
        angles = angles[: a.relecteurs]
        if len(angles) < a.relecteurs:
            print(f"Il faut {a.relecteurs} angles (--angles), {len(angles)} donnés.")
            sys.exit(2)
    controles = [x.strip() for x in a.controles.split(",") if x.strip()]

    lots = decouper(segments, a.taille)
    total = sum(len(t) for _, t in segments)
    print(f"PLAN DE RELECTURE — {Path(a.fichier).name}")
    print(f"{len(segments)} segments · {nombre(total)} caractères (espaces comprises) · "
          f"{len(lots)} lot(s) de {nombre(a.taille)} caractères au plus")
    print()
    lignes_plan = []
    for i, lot in enumerate(lots, 1):
        c = sum(len(t) for _, t in lot)
        ligne = f"lot-{i:02d} : {lot[0][0]} → {lot[-1][0]} · {len(lot)} segment(s) · {nombre(c)} caractères"
        alerte = "  ← un seul segment, plus long que la taille de lot" if len(lot) == 1 and c > a.taille else ""
        print(ligne + alerte)
        lignes_plan.append("# " + ligne)
    print()

    if a.relecteurs:
        lecture_totale = total * len(angles)
        lancements = len(angles) * len(lots)
        print(f"Relecture À {len(angles)} RELECTEURS EN PARALLÈLE ({', '.join(angles)}) :")
        print(f"  {len(angles)} relecteurs en même temps × {len(lots)} lot(s) = {lancements} lancement(s) d'agent au total ;")
        print(f"  chaque relecteur lit son lot en entier : {nombre(lecture_totale)} caractères lus au total,")
        print(f"  soit de l'ordre de {fourchette(lecture_totale)} jetons pour la seule lecture (estimation),")
        print("  sans compter les consignes, le glossaire transmis et les rapports écrits.")
        if lancements > 3:
            print(f"  {lancements} LANCEMENTS, PLUS DE 3 : annoncer ces chiffres et attendre l'accord explicite d'Hervé.")
    else:
        print("Relecture STANDARD (sans relecteur parallèle) : AURA lit les lots l'un après l'autre.")
        print(f"  Lecture totale : {nombre(total)} caractères, de l'ordre de {fourchette(total)} jetons (estimation).")
    print()

    attendus = [f"controle-{c}" for c in controles]
    if a.relecteurs:
        attendus += [f"{ang}-lot-{i:02d}" for i in range(1, len(lots) + 1) for ang in angles]
    else:
        attendus += [f"lot-{i:02d}" for i in range(1, len(lots) + 1)]

    if a.plan:
        dossier = Path(lecture.hors_du_plugin(a.plan))
        plan = dossier / "PLAN.txt"
        if plan.exists():
            print(f"PLAN REFUSÉ : {plan} existe déjà. Un plan ne se réécrit pas après coup ;")
            print("prends un nouveau dossier (ex. relecture-2) pour une nouvelle relecture.")
            sys.exit(2)
        dossier.mkdir(parents=True, exist_ok=True)
        entete = [
            f"# Plan de relecture — {Path(a.fichier).name}",
            f"# {len(segments)} segments · {nombre(total)} caractères · lots de {nombre(a.taille)} au plus",
            "# Mode : " + (f"{len(angles)} relecteurs en parallèle ({', '.join(angles)})" if a.relecteurs else "standard"),
            "# Chaque ligne sans # = un rapport attendu, dans ce dossier, sous le nom <ligne>.md",
        ]
        plan.write_text("\n".join(entete + lignes_plan + attendus) + "\n", encoding="utf-8")
        print(f"Plan écrit : {plan} — {len(attendus)} rapports attendus.")
    else:
        print(f"Rapports attendus ({len(attendus)}) : {', '.join(attendus)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
