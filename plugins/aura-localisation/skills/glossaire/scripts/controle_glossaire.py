#!/usr/bin/env python3
"""Contrôle d'un ou plusieurs glossaires au standard v3 (lecture seule : rien n'est modifié).

Usage : python3 controle_glossaire.py Glossaire_<Gamme>.xlsx [AUTRE.xlsx ...] [--attente-jours 30]

Signale, avec des comptes exacts :
  ANOMALIE   onglets ou colonnes manquants, statut / catégorie / genre / nombre / élision hors liste,
             ID vide ou en double, ligne sans EN, EN en double (doublon probable), GENRE vide là où il est
             obligatoire, Gelé sans PUBLIÉ DANS, Confirmé ou Gelé sans FR ; ce qu'une écriture par le
             programme perdrait, et qu'elle refuse donc : colonne hors standard ou cellule sans en-tête
             dans CHANGELOG, commentaire Excel posé ailleurs que sur une ligne de terme.
  À VÉRIFIER même FR pour deux EN différents, même EN à deux sens (définitions différentes), FR à
             plusieurs propositions (« / »), GENRE « — » sur un PERSONNAGE / LIEU / OBJET / LORE,
             et, entre plusieurs glossaires, même EN traduit autrement (à rapprocher par la définition).
  INFO       termes « À confirmer » depuis plus de N jours (colonne DATE) ; commentaire Excel posé sur
             un terme (repris dans ses NOTES à la prochaine écriture par le programme).
Code de sortie : 0 sans anomalie, 1 s'il y a au moins une anomalie, 2 si le fichier est illisible.
--auto-test : vérifie le programme lui-même sur des glossaires fabriqués (aucun fichier réel touché).
"""
import argparse
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modele_glossaire as M  # noqa: E402

ANOMALIE, VERIF, INFO = "ANOMALIE", "À VÉRIFIER", "INFO"


def ref(t):
    return f"{t['ID'] or '(sans ID)'} · ligne {t['_ligne']} · {t['EN'] or '(EN vide)'} → {t['FR'] or '(FR vide)'}"


def controler(chemin, attente_jours):
    constats = defaultdict(list)   # (niveau, intitulé) -> [détails]

    def note(niveau, intitule, detail=""):
        constats[(niveau, intitule)].append(detail)

    g = M.lire_glossaire(chemin)
    # ---- structure
    manquants = [o for o in M.ONGLETS if o not in g["onglets"]]
    for o in manquants:
        note(ANOMALIE, "onglet manquant", o)
    if g["onglets"] and g["onglets"][0] != "Tableau de bord" and "Tableau de bord" in g["onglets"]:
        note(ANOMALIE, "le Tableau de bord n'est pas le premier onglet", " > ".join(g["onglets"]))
    for o in g["onglets"]:
        if o not in M.ONGLETS:
            note(INFO, "onglet hors standard (une écriture par le programme est refusée tant qu'il est là)", o)
    if "Termes" not in g["onglets"]:
        note(ANOMALIE, "fichier hors format v3 : à passer par l'import (gerer_glossaire.py importer)",
             "onglets trouvés : " + ", ".join(g["onglets"]))
        return g, constats
    canon = [M.colonne_canonique(e) for e in g["entetes"]]
    for c in M.COLONNES:
        if c not in canon:
            note(ANOMALIE, "colonne manquante", c)
    for e, c in zip(g["entetes"], canon):
        if c and e != c:
            note(ANOMALIE, "colonne mal nommée", f"« {e} » → écrire « {c} »")
        elif e and not c:
            note(INFO, "colonne hors standard (une écriture par le programme est refusée tant qu'elle est là)", e)
        elif not e:
            note(INFO, "colonne sans en-tête", "")
    ordre = [c for c in canon if c]
    if ordre != [c for c in M.COLONNES if c in ordre]:
        note(ANOMALIE, "colonnes dans le désordre", " | ".join(ordre))
    for c in sorted({c for c in canon if c and canon.count(c) > 1}):
        note(ANOMALIE, "colonne en double", c)
    if g["cellules_hors_entete"]:
        note(ANOMALIE, "cellules remplies à droite de la dernière colonne", str(g["cellules_hors_entete"]))
    if "CHANGELOG" in g["onglets"]:
        manq = [c for c in M.CHANGELOG_COLONNES if c not in g["changelog_entetes"]]
        if manq:
            note(ANOMALIE, "colonne manquante au CHANGELOG", ", ".join(manq))
        for e in g["changelog_hors_standard"]:
            note(ANOMALIE, "colonne hors standard au CHANGELOG (une écriture par le programme la perdrait : refusée)", e)
        if g["changelog_hors_entete"]:
            note(ANOMALIE, "cellules remplies sans en-tête au CHANGELOG", str(g["changelog_hors_entete"]))
    hors = M.commentaires_hors_termes(g)
    for o, r, x in hors:
        note(ANOMALIE, "commentaire Excel hors des lignes de termes (une écriture par le programme le perdrait : refusée)",
             f"{o}!{r} : « {x} »")
    for o, r, x in g["commentaires"]:
        if (o, r, x) not in hors:
            note(INFO, "commentaire Excel sur un terme (repris dans ses NOTES à la prochaine écriture par le programme)",
                 f"{o}!{r} : « {x} »")
    # ---- lignes
    termes = g["termes"]
    ids = defaultdict(list)
    aujourd = dt.date.today()
    for t in termes:
        if not t["EN"]:
            note(ANOMALIE, "ligne remplie sans EN", ref(t))
            continue
        if not t["ID"]:
            note(ANOMALIE, "ID vide", ref(t))
        else:
            ids[t["ID"]].append(t)
        for col, liste in M.LISTES.items():
            v = t[col]
            if not v:
                if col in ("STATUT", "CATÉGORIE"):
                    note(ANOMALIE, f"{col} vide", ref(t))
                continue
            if v not in liste:
                exact = M.valeur_canonique(col, v)
                aide = f" (écrire « {exact} »)" if exact else f" (admis : {', '.join(liste)})"
                note(ANOMALIE, f"{col} hors liste", f"{ref(t)} · « {v} »{aide}")
        actif = t["STATUT"] in M.ACTIFS
        if actif and t["CATÉGORIE"] in M.GENRE_OBLIGATOIRE and not t["GENRE"]:
            note(ANOMALIE, "GENRE vide là où il est obligatoire (Hervé le déclare, AURA ne le devine pas)",
                 f"{ref(t)} · {t['CATÉGORIE']}")
        if actif and t["CATÉGORIE"] in ("PERSONNAGE", "LIEU", "OBJET", "LORE") and t["GENRE"] == "—":
            note(VERIF, "GENRE « — » sur un nom propre ou un nom d'univers", f"{ref(t)} · {t['CATÉGORIE']}")
        if t["STATUT"] == "Gelé" and not t["PUBLIÉ DANS"]:
            note(ANOMALIE, "Gelé sans PUBLIÉ DANS", ref(t))
        if t["STATUT"] in M.EN_VIGUEUR and not t["FR"]:
            note(ANOMALIE, "Confirmé ou Gelé sans FR", ref(t))
        if actif and " / " in t["FR"]:
            note(VERIF, "FR avec plusieurs propositions (« / ») : à trancher", ref(t))
        if t["DATE"] and not t["DATE"][:4].isdigit():
            note(INFO, "DATE illisible (format attendu AAAA-MM-JJ)", f"{ref(t)} · « {t['DATE']} »")
        if t["STATUT"] == "À confirmer" and attente_jours:
            try:
                age = (aujourd - dt.date.fromisoformat(t["DATE"])).days
                if age > attente_jours:
                    note(INFO, f"« À confirmer » depuis plus de {attente_jours} jours", f"{ref(t)} · {age} jours")
            except ValueError:
                pass
    for i, lst in ids.items():
        if len(lst) > 1:
            note(ANOMALIE, "ID en double", f"{i} : lignes " + ", ".join(str(t["_ligne"]) for t in lst))
    actifs = [t for t in termes if t["EN"] and t["STATUT"] in M.ACTIFS]
    par_en, par_fr = defaultdict(list), defaultdict(list)
    for t in actifs:
        par_en[M.cle(t["EN"])].append(t)
        if t["FR"]:
            par_fr[M.cle(t["FR"])].append(t)
    for lst in par_en.values():
        if len(lst) < 2:
            continue
        defs = [M.cle(t["DÉFINITION MÉCANIQUE"]) for t in lst]
        detail = " ; ".join(f"{t['ID']} {t['FR'] or '(FR vide)'}" for t in lst)
        if all(defs) and len(set(defs)) == len(defs):
            note(VERIF, "même EN à plusieurs sens (définitions différentes) : vérifier que NOTES l'explique",
                 f"{lst[0]['EN']} : {detail}")
        else:
            note(ANOMALIE, "EN en double (non archivé, sans définitions qui distinguent les sens)",
                 f"{lst[0]['EN']} : {detail}")
    for lst in par_fr.values():
        ens = {M.cle(t["EN"]) for t in lst}
        if len(ens) > 1:
            note(VERIF, "même FR pour plusieurs EN différents",
                 f"{lst[0]['FR']} ← " + " ; ".join(f"{t['ID']} {t['EN']}" for t in lst))
    return g, constats


def afficher(chemin, g, constats):
    termes = [t for t in g["termes"] if t["EN"]]
    print(f"\n=== {chemin}")
    print(f"Onglets : {', '.join(g['onglets']) or '(aucun)'}")
    print(f"Termes (lignes avec un EN) : {len(termes)}")
    if termes:
        parts = [f"{s} {sum(1 for t in termes if t['STATUT'] == s)}" for s in M.STATUTS]
        hors = sum(1 for t in termes if t["STATUT"] not in M.STATUTS)
        print("Par statut : " + " · ".join(parts) + f" · vide ou hors liste {hors}")
        cats = [f"{c} {n}" for c in M.CATEGORIES for n in [sum(1 for t in termes if t['CATÉGORIE'] == c)] if n]
        print("Par catégorie : " + (" · ".join(cats) or "(aucune)"))
    for niveau in (ANOMALIE, VERIF, INFO):
        bloc = [(k[1], v) for k, v in constats.items() if k[0] == niveau]
        if not bloc:
            continue
        total = sum(len(v) for _, v in bloc)
        print(f"\n{niveau} — {total}")
        for intitule, details in bloc:
            print(f"  [{len(details)}] {intitule}")
            for d in details[:60]:
                if d:
                    print(f"      {d}")
            if len(details) > 60:
                print(f"      … et {len(details) - 60} de plus")
    na = sum(len(v) for k, v in constats.items() if k[0] == ANOMALIE)
    nv = sum(len(v) for k, v in constats.items() if k[0] == VERIF)
    print(f"\nBilan : {na} anomalie(s), {nv} point(s) à vérifier.")
    return na


def croiser(resultats):
    """Même EN dans deux glossaires (deux gammes) : jamais le même terme par le seul mot."""
    par_en = defaultdict(list)
    for chemin, g in resultats:
        for t in g["termes"]:
            if t["EN"] and t["STATUT"] in M.ACTIFS:
                par_en[M.cle(t["EN"])].append((Path(chemin).name, t))
    lignes = []
    for occ in par_en.values():
        fichiers = {f for f, _ in occ}
        frs = {M.cle(t["FR"]) for _, t in occ if t["FR"]}
        if len(fichiers) > 1 and len(frs) > 1:
            lignes.append(occ)
    print(f"\n=== Entre glossaires : {len(lignes)} mot(s) anglais traduit(s) autrement d'un glossaire à l'autre")
    if lignes:
        print("Ce n'est pas une erreur en soi : on compare la DÉFINITION MÉCANIQUE. Même définition → incohérence "
              "à trancher ; définitions différentes → deux termes distincts ; définition vide → à remplir d'abord.")
    for occ in lignes:
        print(f"  {occ[0][1]['EN']}")
        for f, t in occ:
            d = t["DÉFINITION MÉCANIQUE"] or "(définition vide)"
            print(f"      {f} · {t['ID']} · {t['FR']} ({t['STATUT']}) · {d}")


def auto_test():
    """Glossaire fabriqué avec des défauts posés exprès : chacun doit être trouvé ; un glossaire propre, aucun."""
    import tempfile
    def t(i, en, fr, cat, genre, statut, publie="", definition=""):
        d = {c: "" for c in M.COLONNES}
        d.update({"ID": i, "EN": en, "FR": fr, "CATÉGORIE": cat, "GENRE": genre, "STATUT": statut,
                  "PUBLIÉ DANS": publie, "DÉFINITION MÉCANIQUE": definition, "DATE": "2026-01-01"})
        return d
    ch = [{"DATE": "2026-01-01", "VERSION": "1.0", "ID": "—", "EN": "—", "CHAMP": "création", "AVANT": "",
           "APRÈS": "", "RAISON": "auto-test", "DÉCIDÉ PAR": "auto-test"}]
    propres = [t("T-0001", "Wyrm", "Guivre", "PERSONNAGE", "f", "Confirmé"),
               t("T-0002", "Exhaust", "Épuiser", "MÉCANIQUE", "—", "Gelé", "Boîte de base")]
    sales = propres + [t("T-0003", "Wyrm", "Ver", "PERSONNAGE", "m", "Brouillon"),        # EN en double
                       t("T-0004", "Gloom", "Ver", "LORE", "", "Brouillon"),             # même FR + genre vide
                       t("T-0004", "Rest", "Repos", "MÉCANIQUE", "", "Validé"),          # ID double + statut
                       t("T-0006", "Frozen", "Gelé", "MÉCANIQUE", "", "Gelé"),           # gelé sans produit
                       t("T-0007", "Travel", "Voyage / Trajet", "MÉCANIQUE", "", "Brouillon")]
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d) / "Glossaire_Propre.xlsx", Path(d) / "Glossaire_Sale.xlsx"
        M.ecrire_glossaire(a, "Propre", propres, ch)
        M.ecrire_glossaire(b, "Sale", sales, ch)
        _, ca = controler(a, 30)
        _, cb = controler(b, 30)
        # ce qu'une réécriture perdrait : colonne ajoutée au CHANGELOG, commentaires Excel (Termes, Notice)
        c = Path(d) / "Glossaire_Retouche.xlsx"
        M.ecrire_glossaire(c, "Retouche", propres, ch)

        def colonne_en_plus(x):
            for n, v in ((1, "MA NOTE"), (2, "à garder")):
                fin = x.index("</row>", x.index(f'<row r="{n}">'))
                x = x[:fin] + f'<c r="J{n}" t="inlineStr"><is><t>{v}</t></is></c>' + x[fin:]
            return x
        rels = ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship '
                'Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" '
                'Target="../comments{n}.xml"/></Relationships>')
        com = ('<comments xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><commentList>'
               '<comment ref="{ref}" authorId="0"><text><t>{txt}</t></text></comment></commentList></comments>')
        M._retoucher(c, changer={"xl/worksheets/sheet3.xml": colonne_en_plus},
                     ajouter={"xl/worksheets/_rels/sheet2.xml.rels": rels.format(n=1),
                              "xl/comments1.xml": com.format(ref="C2", txt="vérifier"),
                              "xl/worksheets/_rels/sheet4.xml.rels": rels.format(n=2),
                              "xl/comments2.xml": com.format(ref="A1", txt="à relire")})
        _, cc = controler(c, 30)
    na = sum(len(v) for k, v in ca.items() if k[0] == ANOMALIE)
    attendus = ["EN en double (non archivé, sans définitions qui distinguent les sens)", "STATUT hors liste",
                "ID en double", "Gelé sans PUBLIÉ DANS",
                "GENRE vide là où il est obligatoire (Hervé le déclare, AURA ne le devine pas)"]
    manquants = [x for x in attendus if (ANOMALIE, x) not in cb]
    manquants += [x for x in ("même FR pour plusieurs EN différents", "FR avec plusieurs propositions (« / ») : à trancher")
                  if (VERIF, x) not in cb]
    retouches = {(ANOMALIE, "colonne hors standard au CHANGELOG (une écriture par le programme la perdrait : refusée)"):
                 "MA NOTE",
                 (ANOMALIE, "commentaire Excel hors des lignes de termes (une écriture par le programme le perdrait : "
                            "refusée)"): "Notice!A1",
                 (INFO, "commentaire Excel sur un terme (repris dans ses NOTES à la prochaine écriture par le "
                        "programme)"): "Termes!C2"}
    manquants += [k[1] for k, v in retouches.items() if not any(v in x for x in cc.get(k, []))]
    # la documentation (SKILL.md) et le programme portent les mêmes listes : une règle, une seule écriture
    import re
    doc = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    sec = doc.split("**Colonnes de `Termes`**")[1].split("**Les 5 statuts**")[0]
    cols = [c for c in re.findall(r"^\| ([A-ZÉÈ ]+?) \|", sec, re.M) if c != "Colonne"]
    stats = re.findall(r"^\| (" + "|".join(M.STATUTS) + r") \|", doc, re.M)
    cats = re.search(r"\| CATÉGORIE \| (.+?) \|", doc).group(1).split(", ")
    ecarts = [n for n, a, b in (("colonnes", cols, M.COLONNES), ("statuts", stats, M.STATUTS),
                                 ("catégories", cats, M.CATEGORIES)) if a != b]
    if na or manquants or ecarts:
        print(f"AUTO-TEST ÉCHEC : anomalies sur le glossaire propre = {na} ; défauts non trouvés = {manquants} ; "
              f"SKILL.md et programme discordants sur : {ecarts}")
        return 1
    print(f"AUTO-TEST OK — glossaire propre : 0 anomalie ; glossaire saboté : {len(attendus) + 2} défauts posés, "
          "tous trouvés ; glossaire retouché à la main : colonne ajoutée au CHANGELOG et commentaires Excel (sur un "
          "terme, sur la Notice) tous signalés ; SKILL.md et programme concordent (colonnes, statuts, catégories)")
    return 0


def main():
    if "--auto-test" in sys.argv:
        return auto_test()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("glossaires", nargs="+")
    p.add_argument("--attente-jours", type=int, default=30)
    a = p.parse_args()
    code, resultats = 0, []
    for chemin in a.glossaires:
        try:
            g, constats = controler(chemin, a.attente_jours)
        except Exception as e:  # fichier illisible : on le dit, on ne conclut rien
            print(f"\n=== {chemin}\nILLISIBLE : {e}")
            code = 2
            continue
        if afficher(chemin, g, constats):
            code = max(code, 1)
        resultats.append((chemin, g))
    if len(resultats) > 1:
        croiser(resultats)
    return code


if __name__ == "__main__":
    sys.exit(main())
