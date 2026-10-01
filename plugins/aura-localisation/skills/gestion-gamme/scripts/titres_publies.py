#!/usr/bin/env python3
"""Contrôle « titre déjà publié » : compare les titres d'un nouveau produit de la gamme aux titres
déjà imprimés (registre de gamme) et aux termes du glossaire de la gamme.

Bibliothèque standard uniquement ; lecture par lecture.py, règles communes dans commun.py.

Sources de référence :
  --registre  Core/Gammes/<Gamme>.md : tableau sous le titre « Titres de cartes publiés »
              (colonnes EN, FR, Produit, Réf. carte, Date — trouvées par leur nom) ;
  --glossaire Glossaires/Glossaire_<Gamme>.xlsx (facultatif) : colonnes EN, FR, STATUT ;
              les lignes « Archivé » sont ignorées.
Nouveaux titres (--nouveaux) : tableau .xlsx/.csv (colonnes --col-en et, si la traduction est
proposée, --col-fr) ou liste .docx/.txt/.md (un titre anglais par ligne).

Ce que le script signale (il ne tranche rien) :
  - titre anglais déjà publié → la traduction publiée à reprendre ;
  - ÉCART : traduction proposée différente de la traduction publiée ;
  - COLLISION : traduction proposée déjà prise par un autre titre anglais ;
  - titre anglais PROCHE d'un titre publié (même carte ? à vérifier, jamais conclu sur le nom seul) ;
  - doublons de la nouvelle liste, incohérences de la référence elle-même, titre présent à la fois
    au registre et au glossaire (deux vérités du même fait).

--auto-test : fabrique un registre, un glossaire et une liste de nouveaux titres où chaque cas
ci-dessus a été glissé exprès ; il doit tous les trouver, ignorer un terme Archivé du glossaire, et ne
rien signaler pour une simple différence de casse ou d'apostrophe.

Codes de sortie : 0 contrôle fait ; 1 auto-test en échec ; 2 erreur d'usage ou fichier illisible.
"""
import argparse
import contextlib
import io
import re
import sys
import tempfile
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402
from commun import (arret, normaliser, cle_titre, sans_accents, ressemblance, colonne,  # noqa: E402
                    deviner_colonne, lire_table, cellule)

SEUIL_PROCHE = 0.85


def lire_registre(chemin):
    """[(EN, FR, origine)] lus dans le tableau qui suit le titre « Titres de cartes publiés »."""
    lignes = Path(chemin).read_text(encoding="utf-8").splitlines()
    debut = next((k for k, l in enumerate(lignes) if l.lstrip().startswith("#") and "titres" in l.lower()), None)
    if debut is None:
        arret(f"{Path(chemin).name} : aucune section « Titres de cartes publiés » trouvée.")
    table = []
    for l in lignes[debut + 1:]:
        s = l.strip()
        if s.startswith("#"):
            break
        if s.startswith("|"):
            table.append([c.strip() for c in s.strip("|").split("|")])
        elif table and s:
            break
    if not table:
        return []
    tete = [c.lower() for c in table[0]]
    i_en, i_fr = deviner_colonne(tete, "en"), deviner_colonne(tete, "fr")
    if i_en is None or i_fr is None:
        arret(f"{Path(chemin).name} : le tableau des titres publiés doit avoir des colonnes EN et FR (lu : {', '.join(table[0])}).")
    i_pr = next((k for k, c in enumerate(tete) if c.startswith("produit")), None)
    i_re = next((k for k, c in enumerate(tete) if c.startswith("réf") or c.startswith("ref")), None)
    i_da = next((k for k, c in enumerate(tete) if c.startswith("date")), None)
    out = []
    for r in table[1:]:
        if all(re.fullmatch(r":?-+:?", c) for c in r if c):
            continue  # ligne de séparation du tableau markdown
        en, fr_ = cellule(r, i_en), cellule(r, i_fr)
        if en and en not in ("—", "-"):
            origine = "registre : " + ", ".join(x for x in (cellule(r, i_pr), cellule(r, i_re), cellule(r, i_da)) if x)
            out.append((en, fr_, origine.rstrip(": ")))
    return out


def lire_glossaire(chemin):
    """[(EN, FR, origine)] du glossaire ; onglet « Termes » s'il existe ; « Archivé » ignoré."""
    feuilles = lecture.feuilles_xlsx(chemin) if Path(chemin).suffix.lower() == ".xlsx" else {}
    feuille = "Termes" if "Termes" in feuilles else None
    tete, corps = lire_table(chemin, feuille, ["en", "terme (en)", "ID"])
    i_en, i_fr = deviner_colonne(tete, "en"), deviner_colonne(tete, "fr")
    if i_en is None or i_fr is None:
        arret(f"{Path(chemin).name} : colonnes EN et FR introuvables (en-têtes : {', '.join(e for e in tete if e)}).")
    i_st = next((k for k, e in enumerate(tete) if "statut" in e.lower()), None)
    i_pu = next((k for k, e in enumerate(tete) if "publi" in e.lower()), None)
    out = []
    for k, l in corps:
        en, fr_, st = cellule(l, i_en), cellule(l, i_fr), cellule(l, i_st)
        if en and fr_ and not st.lower().startswith("archiv"):
            pub = cellule(l, i_pu)
            out.append((en, fr_, f"glossaire ligne {k}, statut {st or '?'}" + (f", publié dans {pub}" if pub else "")))
    return out


def lire_nouveaux(chemin, col_en, col_fr, feuille):
    ext = Path(chemin).suffix.lower()
    if ext in (".xlsx", ".csv", ".tsv"):
        tete, corps = lire_table(chemin, feuille, [c for c in (col_en, col_fr) if c])
        i_en = colonne(tete, col_en) if col_en else deviner_colonne(tete, "en")
        if i_en is None:
            arret(f"Colonne des titres anglais à préciser avec --col-en (en-têtes : {', '.join(e for e in tete if e)}).")
        i_fr = colonne(tete, col_fr) if col_fr else deviner_colonne(tete, "fr")
        return [(f"ligne {k}", cellule(l, i_en), cellule(l, i_fr)) for k, l in corps if cellule(l, i_en)]
    return [(rep, normaliser(t), "") for rep, t in lecture.textes(chemin)]


def _lancer(argv):
    """Lance le vrai programme (main) avec ces options ; renvoie (code de sortie, texte affiché)."""
    ancien, sortie = sys.argv, io.StringIO()
    sys.argv = ["titres_publies.py"] + argv
    try:
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            try:
                code = main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = ancien
    return code, sortie.getvalue()


def _section(texte, debut):
    """Lignes de la section du rapport dont le titre commence par `debut`."""
    bloc = texte.split("\n## " + debut, 1)
    return bloc[1].split("\n## ", 1)[0] if len(bloc) == 2 else ""


def auto_test():
    """Chaque cas glissé exprès, avec le résultat attendu écrit à la main."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        registre = d / "Essai.md"
        registre.write_text(
            "# Registre de gamme — Essai\n\n## Produits\n\n| Réf. | Produit |\n|---|---|\n| P1 | Boîte de base |\n\n"
            "## Titres de cartes publiés\n\n| EN | FR | Produit | Réf. carte | Date |\n|---|---|---|---|---|\n"
            "| Guard | Sentinelle | P1 | C001 | 2026-04-15 |\n"
            "| Thief | Voleur | P1 | C002 | 2026-04-15 |\n"
            "| Watchtower | Tour de guet | P1 | C010 | 2026-04-15 |\n"
            "| Shield | Bouclier | P1 | C020 | 2026-04-15 |\n"
            "| Shield | Écu | P1 | C021 | 2026-04-15 |\n"
            "| Ranger’s Oath | Serment du rôdeur | P1 | C030 | 2026-04-15 |\n\n"
            "## Errata\n\n| N° | Date |\n|---|---|\n", encoding="utf-8")
        glossaire = d / "Glossaire_Essai.csv"
        glossaire.write_text(
            "ID;EN;FR;STATUT;PUBLIÉ DANS\n"
            "T-0001;Exhaust;Épuiser;Gelé;Boîte de base\n"
            "T-0002;Mage;Mage;Archivé;Boîte de base\n"           # archivé : ignoré
            "T-0003;Watchtower;Tour de guet;Gelé;Boîte de base\n",  # aussi au registre : deux foyers
            encoding="utf-8")
        nouveaux = d / "extension.csv"
        nouveaux.write_text(
            "Ref;Title;Titre FR\n"
            "E1;Guard;Garde\n"                         # ÉCART (publié « Sentinelle »)
            "E2;thief;voleur\n"                        # à reprendre (casse seule : pas d'écart)
            "E3;Exhaust;Épuiser\n"                     # à reprendre (glossaire, Gelé)
            "E4;Spy;Voleur\n"                          # COLLISION avec Thief ; sans antécédent
            "E5;Watch Tower;\n"                        # proche de Watchtower
            "E6;Bard;Barde\n"                          # doublon dans la liste…
            "E7;Bard;Ménestrel\n"                      # …même titre, autre traduction
            "E8;Mage;Magicien\n"                       # Mage archivé : sans antécédent, pas d'écart
            "E9;Ranger's Oath;Serment du rôdeur\n",    # apostrophe droite contre courbe : à reprendre
            encoding="utf-8")
        code, texte = _lancer(["--registre", str(registre), "--glossaire", str(glossaire), "--nouveaux", str(nouveaux),
                               "--col-en", "Title", "--col-fr", "Titre FR"])
    attendus = {
        "ÉCARTS": ["ligne 2 : Guard"],
        "COLLISIONS": ["ligne 5 : Spy"],
        "Titres proches": ["ligne 6 : Watch Tower"],
        "Déjà publiés": ["ligne 3 : thief", "ligne 4 : Exhaust", "ligne 10 : Ranger's Oath"],
        "Doublons dans la nouvelle liste": ["- bard :"],
        "Référence incohérente": ["- Shield :"],
        "Titre présent au registre ET au glossaire": ["- Watchtower"],
        "Sans antécédent": ["Spy, Bard, Mage"],
    }
    echecs = []
    if code != 0:
        echecs.append(f"code de sortie 0 attendu, vu {code}")
    resume = ("**Résumé :** déjà publiés à reprendre : 3 ; ÉCARTS : 1 ; COLLISIONS : 1 ; proches à vérifier : 1 ; "
              "sans antécédent : 4 ; doublons dans la liste : 1.")
    if resume not in texte:
        echecs.append("résumé : attendu « déjà publiés 3, écarts 1, collisions 1, proches 1, sans antécédent 4, doublons 1 »")
    if "- Référence : 6 titres au registre" not in texte or "2 termes au glossaire" not in texte:
        echecs.append("référence lue : 6 titres au registre et 2 termes au glossaire (Archivé exclu) attendus")
    for titre, morceaux in attendus.items():
        sec = _section(texte, titre)
        manque = [m for m in morceaux if m not in sec]
        print(f"  {titre} : {'OK' if sec and not manque else 'ÉCHEC'}")
        if not sec or manque:
            echecs.append(f"{titre} : non trouvé {manque or '(section absente)'}")
    # fausses alertes : un titre ne doit pas sortir dans une section qui n'est pas la sienne
    for titre, intrus in (("ÉCARTS", ["thief", "Mage", "Ranger"]), ("COLLISIONS", ["thief", "Exhaust"]),
                          ("Titres proches", ["Ranger", "Guard"])):
        vus = [x for x in intrus if x in _section(texte, titre)]
        if vus:
            echecs.append(f"fausse alerte dans {titre} : {vus}")
    if echecs:
        print("AUTO-TEST ÉCHOUÉ — " + " ; ".join(echecs) + ". Ne pas se fier à ce contrôle.")
        return 1
    print("AUTO-TEST OK — 9 cas glissés exprès (écart, collision, titre proche, 3 titres à reprendre, doublon, "
          "référence incohérente, double foyer), tous trouvés ; terme Archivé ignoré ; 0 fausse alerte sur la "
          "casse et l'apostrophe")
    return 0


def main():
    if "--auto-test" in sys.argv[1:]:
        return auto_test()
    ap = argparse.ArgumentParser(description="Contrôle « titre déjà publié » pour un nouveau produit de la gamme.",
                                 epilog="--auto-test : essai sur un registre et des titres fabriqués par le programme.")
    ap.add_argument("--registre", required=True, help="Core/Gammes/<Gamme>.md")
    ap.add_argument("--glossaire", help="Glossaires/Glossaire_<Gamme>.xlsx (facultatif)")
    ap.add_argument("--nouveaux", required=True, help="titres du nouveau produit (.xlsx .csv .tsv .docx .txt .md)")
    ap.add_argument("--col-en", help="colonne des titres anglais (nom, lettre ou numéro)")
    ap.add_argument("--col-fr", help="colonne des titres français proposés (facultatif)")
    ap.add_argument("--feuille", help="onglet du fichier des nouveaux titres")
    ap.add_argument("--sortie", help="écrit le rapport dans ce fichier .md")
    a = ap.parse_args()
    try:
        reference = lire_registre(a.registre)
        n_registre = len(reference)
        n_glossaire = 0
        if a.glossaire:
            g = lire_glossaire(a.glossaire)
            n_glossaire = len(g)
            reference += g
        nouveaux = lire_nouveaux(a.nouveaux, a.col_en, a.col_fr, a.feuille)
    except (OSError, KeyError, ValueError) as e:
        arret(f"Lecture impossible : {e}")

    par_en = defaultdict(list)    # clé du titre EN → [(EN, FR, origine)]
    par_fr = defaultdict(list)    # clé du titre FR → [(EN, FR, origine)]
    for en, fr_, origine in reference:
        par_en[cle_titre(en)].append((en, fr_, origine))
        if fr_:
            par_fr[cle_titre(fr_)].append((en, fr_, origine))
    cles_ref = list(par_en)
    sans_acc = defaultdict(list)
    for c in cles_ref:
        sans_acc[sans_accents(c)].append(c)

    reprendre, ecarts, collisions, proches, neufs = [], [], [], [], []
    vus = defaultdict(set)
    doublons = []
    for rep, en, fr_ in nouveaux:
        k = cle_titre(en)
        if fr_:
            vus[k].add(fr_)
        connus = par_en.get(k)
        if connus:
            fr_publies = sorted({x[1] for x in connus if x[1]})
            if fr_ and fr_publies and cle_titre(fr_) not in {cle_titre(x) for x in fr_publies}:
                ecarts.append((rep, en, fr_, connus))
            else:
                reprendre.append((rep, en, fr_, connus))
        else:
            # proche : même titre aux accents près, ou ressemblance ≥ seuil
            cands = [(c, 1.0) for c in sans_acc.get(sans_accents(k), []) if c != k]
            if not cands:
                cands = [(c, r) for c in cles_ref if (r := ressemblance(k, c, SEUIL_PROCHE)) >= SEUIL_PROCHE]
            if cands:
                c, r = max(cands, key=lambda x: x[1])
                proches.append((rep, en, fr_, par_en[c], r))
            else:
                neufs.append((rep, en, fr_))
        if fr_:
            autres = [x for x in par_fr.get(cle_titre(fr_), []) if cle_titre(x[0]) != k]
            if autres:
                collisions.append((rep, en, fr_, autres))
    for k, frs in vus.items():
        if len({cle_titre(f) for f in frs}) > 1:
            doublons.append((k, sorted(frs)))

    incoherences = [(v[0][0], sorted({x[1] for x in v})) for v in par_en.values()
                    if len({cle_titre(x[1]) for x in v if x[1]}) > 1]
    double_foyer = [v[0][0] for v in par_en.values()
                    if any(x[2].startswith("registre") for x in v) and any(x[2].startswith("glossaire") for x in v)]

    def ref(connus):
        return " ; ".join(f"« {x[1]} » ({x[2]})" for x in connus)

    R = [f"# Contrôle « titre déjà publié » — {date.today().isoformat()}", "",
         f"- Référence : {n_registre} titres au registre ({Path(a.registre).name})"
         + (f", {n_glossaire} termes au glossaire ({Path(a.glossaire).name}, Archivé exclu)" if a.glossaire else ", glossaire non fourni"),
         f"- Nouveaux titres lus : {len(nouveaux)} ({Path(a.nouveaux).name})", "",
         f"**Résumé :** déjà publiés à reprendre : {len(reprendre)} ; ÉCARTS : {len(ecarts)} ; COLLISIONS : {len(collisions)} ; "
         f"proches à vérifier : {len(proches)} ; sans antécédent : {len(neufs)} ; doublons dans la liste : {len(doublons)}.", ""]
    R += [f"## ÉCARTS — traduction proposée différente de la traduction publiée ({len(ecarts)})", "",
          "Un titre publié ne change pas sans erratum décidé avec l'éditeur.", ""]
    R += [f"- {rep} : {en} → proposé « {fr_} » ; publié {ref(c)}" for rep, en, fr_, c in ecarts] or ["Aucun."]
    R += ["", f"## COLLISIONS — traduction proposée déjà prise par un autre titre ({len(collisions)})", ""]
    R += [f"- {rep} : {en} → « {fr_} », déjà le titre de : " + " ; ".join(f"{x[0]} ({x[2]})" for x in au)
          for rep, en, fr_, au in collisions] or ["Aucune."]
    R += ["", f"## Titres proches d'un titre publié — même carte ? À vérifier sur l'effet, jamais sur le nom seul ({len(proches)})", ""]
    R += [f"- {rep} : {en}" + (f" (proposé « {fr_} »)" if fr_ else "") + f" ~ {c[0][0]} ({r:.0%}) : {ref(c)}"
          for rep, en, fr_, c, r in proches] or ["Aucun."]
    R += ["", f"## Déjà publiés — traduction à reprendre ({len(reprendre)})", ""]
    R += [f"- {rep} : {en} → {ref(c)}" + ("" if not fr_ else " (proposition identique)") for rep, en, fr_, c in reprendre] or ["Aucun."]
    R += ["", f"## Doublons dans la nouvelle liste (même titre anglais, traductions différentes) ({len(doublons)})", ""]
    R += [f"- {k} : " + " / ".join(f"« {f} »" for f in frs) for k, frs in doublons] or ["Aucun."]
    R += ["", f"## Référence incohérente (même titre anglais publié sous plusieurs traductions) ({len(incoherences)})", ""]
    R += [f"- {en} : " + " / ".join(f"« {f} »" for f in frs) for en, frs in incoherences] or ["Aucune."]
    R += ["", f"## Titre présent au registre ET au glossaire — un seul foyer à garder ({len(double_foyer)})", ""]
    R += [f"- {en}" for en in double_foyer] or ["Aucun."]
    R += ["", f"## Sans antécédent ({len(neufs)})", ""]
    R += [", ".join(dict.fromkeys(en for _, en, _ in neufs)) if neufs else "Aucun."]
    texte = "\n".join(R)
    print(texte)
    if a.sortie:
        Path(a.sortie).write_text(texte + "\n", encoding="utf-8")
        print(f"\nRapport écrit dans {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
