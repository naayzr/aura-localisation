#!/usr/bin/env python3
"""Chercher un terme (et ses variantes) dans TOUT le dossier HERVÉ WORLD, avec des comptes exacts.

Sert à deux choses :
  - avant de proposer un terme : l'anglais existe-t-il déjà quelque part (tous les glossaires, segments,
    livrables) ? le français candidat est-il déjà pris ? « Absent » ne se dit qu'après cette recherche ;
  - avant de corriger un terme : où l'ancien français apparaît-il, et combien de fois ? La liste est
    montrée à Hervé AVANT tout remplacement.

Usage : python3 chercher_terme.py <dossier HERVÉ WORLD> "terme" ["autre forme" ...] [--langue en|fr]
        [--exact] [--tout] [--avec-archives]
Lit .xlsx .docx .csv .tsv .txt .md. Ne modifie rien. Les fichiers qu'il ne sait pas lire (PDF…) sont
listés comme NON FOUILLÉS : l'absence n'est jamais conclue sur eux.
--auto-test : vérifie le programme lui-même sur un dossier fabriqué (aucun fichier réel touché).
"""
import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402
import modele_glossaire as M  # noqa: E402

LISIBLES = {".xlsx", ".docx", ".csv", ".tsv", ".txt", ".md", ".base", ".canvas"}
# .base et .canvas : fichiers texte d'Obsidian (tableau, toile), lus ligne à ligne comme du texte
ZONES = [  # (préfixe du chemin relatif, nom affiché) — dans l'ordre d'affichage
    ("Glossaires", "Glossaires"),
    ("Références/Segments", "Segments réutilisables"),
    ("Références/Narration", "Références de narration"),
    ("Références", "Autres références"),
    ("Livrables", "Livrables (copies de travail)"),
    ("Core/Preferences.md", "Preferences (ne doit contenir AUCUN terme)"),
    ("Core/evas.md", "evas (registre des inventions : trace, ne se réécrit pas)"),
    ("Core/Journal.md", "Journal (trace, ne se réécrit pas)"),
    ("Core/Archives", "Archives (sauvegardes : ne se modifient jamais)"),
    ("Core", "Autres fichiers de Core"),
    ("IMPORT", "IMPORT (dépôts)"),
    ("", "Ailleurs dans le dossier"),
]


def _plat(c):
    d = "".join(x for x in unicodedata.normalize("NFD", c) if not unicodedata.combining(x)).lower()
    return d if len(d) == 1 else c.lower() if len(c.lower()) == 1 else c


def aplatir(texte):
    """Minuscules, sans accents, apostrophes et espaces unifiés — même longueur que le texte d'origine."""
    texte = M.nfc(texte).translate(M._APOS)
    return "".join(_plat(c) for c in texte)


def variantes(terme, langue, exact):
    t = M.nfc(terme).strip()
    if exact:
        return {t}
    mots = t.split()
    out = {t}

    def formes(m):
        f = {m}
        if langue == "en":
            f |= {m + "s", m + "es", m + "'s", m + "ed", m + "ing"}
            if m.endswith("y"):
                f.add(m[:-1] + "ies")
            if m.endswith("e"):
                f |= {m + "d", m[:-1] + "ing"}
        elif not m.lower().endswith(("er", "ir", "ez", "s", "x", "z")):  # verbe, ou mot déjà invariable
            f |= {m + "s", m + "e", m + "es"}
            if m.lower().endswith(("au", "eu", "ou")):
                f.add(m + "x")
            if m.lower().endswith("al"):
                f.add(m[:-2] + "aux")
            if m.lower().endswith("ail"):
                f.add(m[:-3] + "aux")
        return f
    if langue == "en":
        for f in formes(mots[-1]):
            out.add(" ".join(mots[:-1] + [f]))
    else:
        for f in formes(mots[0]):
            out.add(" ".join([f] + mots[1:]))
            if len(mots) > 1:
                for g in formes(mots[-1]):
                    out.add(" ".join([f] + mots[1:-1] + [g]))
    return out


def motif(formes):
    morceaux = []
    for f in sorted(formes, key=len, reverse=True):
        mots = [re.escape(aplatir(m)) for m in re.split(r"[\s\-\u2011]+", f) if m]
        morceaux.append(r"[\s\-\u2011]+".join(mots))
    return re.compile(r"(?<!\w)(?:" + "|".join(morceaux) + r")(?!\w)")


def zone_de(rel):
    for pref, nom in ZONES:
        if rel == pref or rel.startswith(pref + "/") or pref == "":
            return nom
    return ZONES[-1][1]


def est_glossaire(feuilles):
    t = feuilles.get("Termes")
    return bool(t) and "EN" in [M.colonne_canonique(x) for x in t[0]] and "FR" in [M.colonne_canonique(x) for x in t[0]]


def chercher(racine, rx, avec_archives):
    trouve = defaultdict(list)     # chemin relatif -> [(repère, extrait ou ligne de glossaire)]
    non_fouilles, fouilles = [], 0
    for p in sorted(Path(racine).rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(racine).as_posix()
        if p.name.startswith(("~$", ".")) or "/." in "/" + rel:
            continue
        if not avec_archives and rel.startswith("Core/Archives/"):
            continue
        if p.suffix.lower() not in LISIBLES:
            non_fouilles.append((rel, f"format {p.suffix or 'sans extension'} non lu"))
            continue
        try:
            if p.suffix.lower() == ".xlsx":
                feuilles = {M.nfc(k): v for k, v in lecture.feuilles_xlsx(p).items()}
                if est_glossaire(feuilles):
                    for t in M.lire_glossaire(p)["termes"]:
                        for col in ("EN", "FR", "NOTES", "DÉFINITION MÉCANIQUE", "FORMES ACCORDÉES", "RAPPEL STANDARD"):
                            n = len(rx.findall(aplatir(t[col])))
                            if n:
                                trouve[rel].append((f"{t['ID']} ligne {t['_ligne']} [{col}] ×{n}",
                                                    f"{t['EN']} → {t['FR']} ({t['STATUT']})"
                                                    + (f" · déf. : {t['DÉFINITION MÉCANIQUE']}" if t['DÉFINITION MÉCANIQUE'] else ""),
                                                    n))
                    fouilles += 1
                    continue
            if p.suffix.lower() in (".base", ".canvas"):
                textes = [(f"L{i}", l) for i, l in enumerate(lecture._decoder(p.read_bytes()).splitlines(), 1) if l.strip()]
            else:
                textes = lecture.textes(p)
            fouilles += 1
        except Exception as e:  # illisible : listé, jamais compté comme « absent »
            non_fouilles.append((rel, f"illisible ({e.__class__.__name__})"))
            continue
        for rep, texte in textes:
            plat = aplatir(texte)
            ms = list(rx.finditer(plat))
            if ms:
                m = ms[0]
                a, b = max(0, m.start() - 45), min(len(texte), m.end() + 45)
                extrait = ("…" if a else "") + texte[a:b].replace("\n", " ") + ("…" if b < len(texte) else "")
                trouve[rel].append((f"{rep} ×{len(ms)}", extrait, len(ms)))
    return trouve, non_fouilles, fouilles


def auto_test():
    """Dossier fabriqué : chaque occurrence posée doit être comptée, le PDF déclaré non fouillé."""
    import tempfile
    import zipfile
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        for sous in ("Core/Archives", "Glossaires", "Références/Segments", "Livrables/Projet"):
            (r / sous).mkdir(parents=True)
        (r / "Core/Preferences.md").write_text("- On garde Épuiser pour Exhaust.\n", encoding="utf-8")
        (r / "Core/Archives/vieux.md").write_text("Exhaust\n", encoding="utf-8")
        (r / "Références/Segments/s.csv").write_text('EN;FR\n"Exhausted cards";"Cartes épuisées"\n"exhausting";"x"\n',
                                                      encoding="utf-8")
        (r / "Livrables/Projet/epreuve.pdf").write_bytes(b"%PDF-1.4")
        corps = "".join(f'<w:p><w:r><w:t xml:space="preserve">{t}</w:t></w:r></w:p>'
                        for t in ("L’Épuiser.", "Exhaust’s rule, EXHAUST again."))
        with zipfile.ZipFile(r / "Livrables/Projet/r.docx", "w") as z:
            z.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/'
                       f'wordprocessingml/2006/main"><w:body>{corps}</w:body></w:document>')
        t = {c: "" for c in M.COLONNES}
        t.update({"ID": "T-0001", "EN": "Exhaust", "FR": "Épuiser", "STATUT": "Confirmé", "CATÉGORIE": "MÉCANIQUE"})
        M.ecrire_glossaire(r / "Glossaires/Glossaire_Test.xlsx", "Test", [t], [])
        rx = motif(variantes("Exhaust", "en", False))
        trouve, non_fouilles, _ = chercher(r, rx, False)
    comptes = {k: sum(n for *_, n in v) for k, v in trouve.items()}
    attendu = {"Core/Preferences.md": 1, "Références/Segments/s.csv": 2, "Livrables/Projet/r.docx": 2,
               "Glossaires/Glossaire_Test.xlsx": 1}
    pdf_ok = any(rel.endswith("epreuve.pdf") for rel, _ in non_fouilles)
    if comptes != attendu or not pdf_ok:
        print(f"AUTO-TEST ÉCHEC : comptes {comptes} au lieu de {attendu} ; PDF déclaré non fouillé : {pdf_ok}")
        return 1
    print("AUTO-TEST OK — 6 occurrences posées dans 4 fichiers, toutes comptées ; archives exclues ; PDF déclaré non fouillé")
    return 0


def main():
    if "--auto-test" in sys.argv:
        return auto_test()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("racine", help="le dossier HERVÉ WORLD (celui qui contient Core/ et Glossaires/)")
    p.add_argument("termes", nargs="+")
    p.add_argument("--langue", choices=["en", "fr"], default="en", help="pour les variantes (défaut : en)")
    p.add_argument("--exact", action="store_true", help="sans variantes (casse et accents restent ignorés)")
    p.add_argument("--tout", action="store_true", help="toutes les occurrences (défaut : 12 par fichier)")
    p.add_argument("--avec-archives", action="store_true", help="fouiller aussi Core/Archives")
    a = p.parse_args()
    racine = Path(a.racine)
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine}")
    if not (racine / "Core").is_dir():
        print(f"ATTENTION : {racine} ne contient pas Core/ — est-ce bien le dossier HERVÉ WORLD ?")
    formes = set()
    for t in a.termes:
        formes |= variantes(t, a.langue, a.exact)
    rx = motif(formes)
    trouve, non_fouilles, fouilles = chercher(racine, rx, a.avec_archives)
    print(f"Recherche : {' / '.join(a.termes)} — formes cherchées ({len(formes)}) : {', '.join(sorted(formes))}")
    print("Casse, accents, apostrophes et tirets ignorés ; mots entiers seulement."
          + (" Pour un verbe français, donner ses formes (épuiser épuise épuisé épuisez…)." if a.langue == "fr" else ""))
    total = sum(n for v in trouve.values() for *_, n in v)
    par_zone = defaultdict(list)
    for rel, occ in trouve.items():
        par_zone[zone_de(rel)].append((rel, occ))
    for _, nom in ZONES:
        if nom not in par_zone:
            continue
        nz = sum(n for _, occ in par_zone[nom] for *_, n in occ)
        print(f"\n## {nom} — {nz} occurrence(s) dans {len(par_zone[nom])} fichier(s)")
        for rel, occ in par_zone[nom]:
            print(f"  {rel} — {sum(n for *_, n in occ)}")
            for rep, extrait, _ in (occ if a.tout else occ[:12]):
                print(f"      {rep} : {extrait}")
            if not a.tout and len(occ) > 12:
                print(f"      … {len(occ) - 12} autre(s) emplacement(s) (--tout pour tout voir)")
    print(f"\nTOTAL : {total} occurrence(s) dans {len(trouve)} fichier(s) ; {fouilles} fichier(s) fouillé(s).")
    if not a.avec_archives and (racine / "Core" / "Archives").is_dir():
        print("Core/Archives non fouillé (sauvegardes, jamais modifiées) : --avec-archives pour les inclure.")
    if non_fouilles:
        print(f"NON FOUILLÉS ({len(non_fouilles)}) — l'absence n'est pas prouvée pour ces fichiers :")
        for rel, raison in non_fouilles:
            print(f"  {rel} : {raison}")
    if total == 0 and not non_fouilles:
        print("Aucune occurrence dans les fichiers lisibles du dossier.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
