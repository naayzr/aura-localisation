#!/usr/bin/env python3
"""Créer, importer, fusionner, modifier et sauvegarder un glossaire au standard v3.

PAR DÉFAUT RIEN N'EST ÉCRIT : chaque commande affiche ce qu'elle ferait. On relance avec --ecrire
après l'accord d'Hervé. Avant d'écrire un glossaire existant, une sauvegarde datée est faite dans
Core/Archives (jamais écrasée). Aucun terme n'entre validé par import : tout arrive en Brouillon.

  creer       --gamme NOM --sortie Glossaires/Glossaire_NOM.xlsx --par QUI
  importer    SOURCE (.xlsx/.csv) --gamme NOM (--sortie NOUVEAU.xlsx | --dans MAITRE.xlsx)
              [--provenance TEXTE] [--feuille NOM] [--colonne CIBLE=EN-TÊTE ...] [--par QUI]
  modifier    MAITRE (--id T-0001 | --ajouter) --champ COLONNE=VALEUR [...] [--raison R] [--par QUI]
              [--erratum REF] [--second-sens] [--accepter-fr-partage]
  modifier    MAITRE --lot changements.csv   (colonnes ID;CHAMP;VALEUR;RAISON;PAR;ERRATUM)
  exporter    MAITRE --sortie Livrables/<Projet>/Glossaire_<Gamme>_<Produit>_AAAA-MM-JJ.xlsx
              [--pour traducteur|relecteur] [--avec-archives]
  retours     EXPORT_RENVOYÉ_PAR_LE_RELECTEUR.xlsx   (liste les remarques par code ; ne modifie rien)
  comparer    ANCIEN.xlsx NOUVEAU.xlsx   (ce qui a changé, et si c'est tracé au CHANGELOG ; ne modifie rien)
  sauvegarder MAITRE [--archives DOSSIER]
Option commune : --ecrire (sinon essai), --archives DOSSIER (si le glossaire n'est pas dans Glossaires/).
--auto-test : vérifie le programme lui-même sur un dossier fabriqué (aucun fichier réel touché).
"""
import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402
import modele_glossaire as M  # noqa: E402

ALIAS = {
    "ID": {"ID", "IDENTIFIANT", "REF", "N", "NO", "NUMERO"},
    "EN": {"EN", "TERME EN", "TERME ANGLAIS", "ANGLAIS", "ENGLISH", "SOURCE TERM", "TERM", "VO", "TERME VO",
           "TERME SOURCE"},
    "FR": {"FR", "TERME FR", "TERME FRANCAIS", "FRANCAIS", "FRENCH", "TARGET TERM", "TRADUCTION", "VF",
           "TERME VF", "TERME CIBLE", "TERME FR RETENU"},
    "CATÉGORIE": {"CATEGORIE", "CATEGORY", "CATEGORIES"},
    "_TYPE": {"TYPE", "NATURE"},
    "GENRE": {"GENRE", "GENDER"},
    "NOMBRE": {"NOMBRE"},
    "ÉLISION": {"ELISION"},
    "FORMES ACCORDÉES": {"FORMES ACCORDEES", "FORMES"},
    "RAPPEL STANDARD": {"RAPPEL STANDARD", "RAPPEL", "REMINDER", "REMINDER TEXT"},
    "DÉFINITION MÉCANIQUE": {"DEFINITION MECANIQUE", "DEFINITION"},
    "STATUT": {"STATUT", "STATUS", "ETAT"},
    "SOURCE": {"SOURCE", "ORIGINE", "PROJET ORIGINE"},
    "PUBLIÉ DANS": {"PUBLIE DANS", "PRODUITS"},
    "NOTES": {"NOTES", "NOTE", "COMMENTAIRE", "COMMENTAIRES", "REMARQUES", "NOTES CONTEXTE", "CONTEXTE",
              "JUSTIFICATION"},
    "DATE": {"DATE", "MODIFIE LE", "DERNIERE MODIFICATION"},
}
GENRES_LIBRES = {"M": "m", "MASC": "m", "MASCULIN": "m", "F": "f", "FEM": "f", "FEMININ": "f"}


def dire(*l):
    print(*l)


# ------------------------------------------------------------------ outils communs
def ecrire_ou_essai(args, chemin, gamme, termes, changelog, existe):
    if not args.ecrire:
        dire("\nESSAI : rien n'a été écrit. Après l'accord d'Hervé, relancer la même commande avec --ecrire.")
        return 0
    v = M.verrou_excel(chemin)
    if v:
        dire(f"Refus : le fichier semble ouvert dans Excel ({v.name} présent). Le fermer, puis relancer. "
             "Si Excel est déjà fermé, ce petit fichier est un reste : Hervé peut le supprimer.")
        return 2
    if existe:
        sauv, deja = M.sauvegarder(chemin, args.archives)
        dire(f"Sauvegarde avant modification : {sauv}" + (" (identique, déjà présente)" if deja else ""))
    M.ecrire_glossaire(chemin, gamme, termes, changelog, remplacer=existe)
    relu = M.lire_glossaire(chemin)
    n = M.nombre_termes(relu["termes"])
    dire(f"Écrit : {chemin} — relu après écriture : {n} termes, {len(relu['changelog'])} lignes de CHANGELOG.")
    if n != M.nombre_termes(termes):
        dire("ATTENTION : le nombre relu diffère du nombre écrit. Ne pas utiliser ce fichier ; revenir à la sauvegarde.")
        return 2
    return 0


def maitre_conforme(g):
    pb = []
    if "Termes" not in g["onglets"]:
        pb.append("onglet Termes absent")
    canon = [M.colonne_canonique(e) for e in g["entetes"]]
    manquantes = [c for c in M.COLONNES if c not in canon]
    if manquantes:
        pb.append("colonnes manquantes : " + ", ".join(manquantes))
    doubles = sorted({c for c in canon if c and canon.count(c) > 1})
    if doubles:
        pb.append("colonnes en double : " + ", ".join(doubles))
    autres = [e for e in g["entetes"] if e and M.colonne_canonique(e) is None]
    if autres:
        pb.append("colonnes hors standard (le script ne sait pas les réécrire) : " + ", ".join(autres))
    inconnus = [o for o in g["onglets"] if o not in M.ONGLETS]
    if inconnus:
        pb.append("onglets hors standard (le script ne sait pas les réécrire) : " + ", ".join(inconnus))
    if g["cellules_hors_entete"]:
        pb.append(f"{g['cellules_hors_entete']} cellule(s) remplie(s) à droite de la dernière colonne")
    return pb


def charger_maitre(chemin):
    g = M.lire_glossaire(chemin)
    pb = maitre_conforme(g)
    if pb:
        dire(f"Refus : {chemin} n'est pas au standard, le réécrire ferait perdre des données.")
        for p in pb:
            dire("  - " + p)
        dire("Passer d'abord controle_glossaire.py, régler ces points (ou les faire régler par Hervé), puis relancer.")
        sys.exit(2)
    return g


def index_actifs(termes):
    par_en, par_fr = {}, {}
    for t in termes:
        if t["STATUT"] in M.ACTIFS and t["EN"]:
            par_en.setdefault(M.cle(t["EN"]), []).append(t)
            if t["FR"]:
                par_fr.setdefault(M.cle(t["FR"]), []).append(t)
    return par_en, par_fr


def joindre_notes(*morceaux):
    return " | ".join(m for m in morceaux if m and str(m).strip())


# ------------------------------------------------------------------ créer
def cmd_creer(args):
    sortie = Path(args.sortie)
    if sortie.exists():
        dire(f"Refus : {sortie} existe déjà. Un seul glossaire par gamme : on le complète, on ne le recrée pas.")
        return 2
    voisin = maitres_voisins(sortie, args.gamme)
    if voisin:
        dire("Refus : un glossaire de cette gamme semble déjà exister : " + ", ".join(str(v) for v in voisin))
        return 2
    ch = [{"DATE": M.aujourdhui(), "VERSION": "1.0", "ID": "—", "EN": "—", "CHAMP": "création", "AVANT": "",
           "APRÈS": "glossaire vide", "RAISON": args.raison or "nouvelle gamme", "DÉCIDÉ PAR": args.par or ""}]
    dire(f"Création de {sortie} (gamme « {args.gamme} », 0 terme, 4 onglets au standard).")
    return ecrire_ou_essai(args, sortie, args.gamme, [], ch, existe=False)


def maitres_voisins(sortie, gamme):
    """Autres Glossaire_*.xlsx du même dossier dont le nom ressemble à la gamme (jamais 2 maîtres)."""
    d = Path(sortie).parent
    if not d.exists():
        return []
    k = M.cle_entete(gamme).replace(" ", "")
    return [p for p in d.glob("*.xlsx") if p.resolve() != Path(sortie).resolve()
            and not p.name.startswith(("~$", ".ecriture_"))
            and k and k in M.cle_entete(p.stem).replace(" ", "")]


# ------------------------------------------------------------------ importer
def detecter(lignes, forcees):
    for i, ligne in enumerate(lignes[:25]):
        cles = [M.cle_entete(c) for c in ligne]
        corresp = {}
        for j, k in enumerate(cles):
            for cible, entete in forcees.items():
                if k and k == M.cle_entete(entete):
                    corresp.setdefault(j, cible)
            if j in corresp or not k:
                continue
            for cible, alias in ALIAS.items():
                if k in alias:
                    corresp[j] = cible
                    break
        cibles = list(corresp.values())
        if "EN" in cibles and "FR" in cibles:
            return i, corresp
    return None, None


def lire_source(chemin, feuille):
    p = Path(chemin)
    if p.suffix.lower() == ".xlsx":
        feuilles = {M.nfc(k): v for k, v in lecture.feuilles_xlsx(p).items()}
        if feuille:
            if feuille not in feuilles:
                sys.exit(f"Feuille « {feuille} » absente. Feuilles : {', '.join(feuilles)}")
            return {feuille: feuilles[feuille]}
        return feuilles
    if p.suffix.lower() in (".csv", ".tsv", ".txt"):
        lignes = lecture.lignes_csv(p)
        if sum(1 for l in lignes if len(l) > 1) < max(1, len(lignes) // 2):
            # une ligne de titre au-dessus de l'en-tête trompe la détection du séparateur : on essaie chacun
            import csv
            import io
            texte = lecture._decoder(p.read_bytes())
            essais = [list(csv.reader(io.StringIO(texte), delimiter=d)) for d in (";", "\t", ",", "|")]
            lignes = max(essais, key=lambda e: sum(1 for l in e if len(l) > 1))
        return {p.name: lignes}
    sys.exit(f"Format non pris en charge pour l'import : {p.suffix} (accepté : .xlsx .csv .tsv)")


def construire_termes(source, args):
    forcees = {}
    for c in args.colonne or []:
        cible, _, entete = c.partition("=")
        cible = M.colonne_canonique(cible) or ("_TYPE" if M.cle_entete(cible) == "TYPE" else None)
        if not cible or not entete:
            sys.exit(f"--colonne « {c} » : écrire CIBLE=En-tête, par ex. EN=Terme anglais")
        forcees[cible] = entete
    feuilles = lire_source(source, args.feuille)
    for nom, lignes in feuilles.items():
        i, corresp = detecter(lignes, forcees)
        if i is not None:
            break
    else:
        dire("Refus : aucune ligne d'en-tête avec une colonne anglaise ET une colonne française n'a été trouvée.")
        dire("Indiquer les colonnes : --colonne EN=<en-tête anglais> --colonne FR=<en-tête français>.")
        sys.exit(2)
    entetes = [M.nfc(x).strip() for x in lignes[i]]
    rapport = {"feuille": nom, "ligne_entete": i + 1, "preambule": [" ".join(str(c) for c in l if str(c).strip())
                                                                    for l in lignes[:i] if any(str(c).strip() for c in l)],
               "corresp": corresp, "entetes": entetes, "sections": [], "sans_en": [], "statuts": {},
               "cat": {}, "doubles_fr": [], "genres_repris": 0, "seuls": []}
    j_par = {}
    for j, cible in corresp.items():
        j_par.setdefault(cible, []).append(j)
    termes = []
    date = M.aujourdhui()
    nom_src = Path(source).name
    for n, ligne in enumerate(lignes[i + 1:], start=i + 2):
        val = [M.nfc(v).strip() for v in ligne] + [""] * (len(entetes) - len(ligne))

        def premier(cible):
            return next((val[j] for j in j_par.get(cible, []) if val[j]), "")
        remplies = [v for v in val if v]
        en = premier("EN")
        if not en:
            if len(remplies) == 1:
                rapport["sections"].append(remplies[0])
            elif remplies:
                rapport["sans_en"].append((n, " ; ".join(remplies)))
            continue
        if len(remplies) == 1 and not args.garder_seuls:
            rapport["seuls"].append((n, en))   # titre de section dans la colonne anglaise, ou terme sans rien ?
            continue
        t = {c: "" for c in M.COLONNES}
        t["EN"], t["FR"] = en, premier("FR")
        notes = [f"Import du {date} depuis {nom_src}, ligne {n}"]
        st = premier("STATUT")
        rapport["statuts"][st or "(vide)"] = rapport["statuts"].get(st or "(vide)", 0) + 1
        if st:
            notes.append(f"Statut d'origine : {st}")
        typ, cat_src = premier("_TYPE"), premier("CATÉGORIE")
        cat, exacte = M.proposer_categorie(typ, cat_src)
        t["CATÉGORIE"] = cat
        cle_cat = f"{typ or '—'} / {cat_src or '—'}"
        rapport["cat"].setdefault((cle_cat, cat, exacte), 0)
        rapport["cat"][(cle_cat, cat, exacte)] += 1
        if cat_src and not exacte:
            notes.append(f"Catégorie d'origine : {cat_src}")
        if typ:
            notes.append(f"Type d'origine : {typ}")
        if not exacte:
            notes.append("CATÉGORIE proposée à l'import, à valider")
        g = premier("GENRE")
        if g:
            gv = M.valeur_canonique("GENRE", g) or GENRES_LIBRES.get(M.cle_entete(g))
            if gv:
                t["GENRE"] = gv
                rapport["genres_repris"] += 1
            else:
                notes.append(f"Genre d'origine illisible : {g}")
        for c in ("NOMBRE", "ÉLISION"):
            v = premier(c)
            if v:
                vv = M.valeur_canonique(c, v)
                if vv:
                    t[c] = vv
                else:
                    notes.append(f"{c} d'origine : {v}")
        for c in ("FORMES ACCORDÉES", "RAPPEL STANDARD", "DÉFINITION MÉCANIQUE", "PUBLIÉ DANS"):
            t[c] = premier(c)
        if premier("ID"):
            notes.append(f"ID d'origine : {premier('ID')}")
        if premier("SOURCE"):
            notes.append(f"Source d'origine : {premier('SOURCE')}")
        for j in j_par.get("NOTES", []):
            if val[j]:
                notes.append(val[j] if len(j_par["NOTES"]) == 1 else f"{entetes[j]} : {val[j]}")
        for j in range(len(val)):
            if j not in corresp and val[j]:
                e = entetes[j] if j < len(entetes) and entetes[j] else f"colonne {j + 1}"
                notes.append(f"{e} : {val[j]}")
        if " / " in t["FR"]:
            rapport["doubles_fr"].append((n, en, t["FR"]))
        t["SOURCE"] = args.provenance or f"Import de {nom_src}"
        t["STATUT"] = "Brouillon"
        t["NOTES"] = joindre_notes(*notes)
        t["DATE"] = date
        t["_ligne_source"] = n
        termes.append(t)
    return termes, rapport


def afficher_rapport(rapport, termes, source):
    dire(f"Source : {source} — feuille « {rapport['feuille']} », en-tête trouvé ligne {rapport['ligne_entete']}.")
    if rapport["preambule"]:
        dire("Lignes au-dessus de l'en-tête (à reprendre dans --provenance si elles disent d'où vient le glossaire) :")
        for l in rapport["preambule"]:
            dire("  « " + l + " »")
    dire("\nCorrespondance des colonnes :")
    for j, e in enumerate(rapport["entetes"]):
        if not e:
            continue
        c = rapport["corresp"].get(j)
        if c == "_TYPE":
            c = "sert à proposer la CATÉGORIE, valeur gardée en NOTES"
        elif c == "STATUT":
            c = "NOTES (« Statut d'origine »), le STATUT devient Brouillon"
        elif c in ("ID", "SOURCE"):
            c = f"NOTES (« {c} d'origine »)"
        dire(f"  {e:28} → {c or 'NOTES (colonne non reconnue, valeur gardée)'}")
    dire(f"\nTermes trouvés (lignes avec un terme anglais) : {len(termes)}")
    dire(f"Lignes de section ignorées : {len(rapport['sections'])}" +
         (f" ({', '.join(rapport['sections'])})" if rapport["sections"] else ""))
    if rapport["seuls"]:
        dire(f"Lignes où seul l'anglais est rempli, ignorées : {len(rapport['seuls'])} — titres de section, ou termes "
             "sans traduction ? Si ce sont des termes : relancer avec --garder-seuls.")
        for n, en in rapport["seuls"]:
            dire(f"  ligne {n} : {en}")
    if rapport["sans_en"]:
        dire(f"Lignes remplies SANS terme anglais, ignorées : {len(rapport['sans_en'])}")
        for n, l in rapport["sans_en"]:
            dire(f"  ligne {n} : {l}")
    dire("\nStatuts d'origine (tous deviennent Brouillon ; l'origine est gardée en NOTES) :")
    for s, n in sorted(rapport["statuts"].items(), key=lambda x: -x[1]):
        dire(f"  {s:20} {n}")
    dire("\nCatégories proposées (type / catégorie d'origine → CATÉGORIE) — à faire valider par Hervé :")
    for (src, cat, exacte), n in sorted(rapport["cat"].items(), key=lambda x: (x[0][1], x[0][0])):
        dire(f"  {src:40} → {cat:11} {n:3}" + ("" if exacte else "  (proposition)"))
    if rapport["doubles_fr"]:
        dire(f"\nCellules FR avec plusieurs propositions (« / ») : {len(rapport['doubles_fr'])} — Hervé tranche")
        for n, en, fr in rapport["doubles_fr"]:
            dire(f"  ligne {n} : {en} → {fr}")
    sans_fr = [t for t in termes if not t["FR"]]
    if sans_fr:
        dire(f"\nTermes sans FR : {len(sans_fr)} — " + ", ".join(t["EN"] for t in sans_fr))
    vus, doubles = {}, []
    for t in termes:
        k = M.cle(t["EN"])
        if k in vus:
            doubles.append((vus[k], t))
        else:
            vus[k] = t
    if doubles:
        dire(f"\nEN en double dans la source : {len(doubles)}")
        for a, b in doubles:
            dire(f"  {a['EN']} : ligne {a['_ligne_source']} ({a['FR']}) et ligne {b['_ligne_source']} ({b['FR']})")
    n_obl = sum(1 for t in termes if t["CATÉGORIE"] in M.GENRE_OBLIGATOIRE and not t["GENRE"])
    dire(f"\nGenre à déclarer par Hervé (catégories {', '.join(M.GENRE_OBLIGATOIRE)}) : {n_obl} terme(s) ; "
         f"genres repris de la source : {rapport['genres_repris']}.")


def cmd_importer(args):
    if bool(args.sortie) == bool(args.dans):
        sys.exit("Préciser soit --sortie NOUVEAU.xlsx (premier glossaire de la gamme), soit --dans MAITRE.xlsx (fusion).")
    termes, rapport = construire_termes(args.source, args)
    afficher_rapport(rapport, termes, args.source)
    if args.sortie:
        sortie = Path(args.sortie)
        if sortie.exists():
            dire(f"\nRefus : {sortie} existe déjà. Pour l'enrichir : --dans {sortie} (fusion, avec sauvegarde).")
            return 2
        voisins = maitres_voisins(sortie, args.gamme)
        if voisins:
            dire("\nRefus : un glossaire de cette gamme semble déjà exister : " + ", ".join(p.name for p in voisins)
                 + ". Jamais deux glossaires maîtres pour une gamme : fusionner avec --dans.")
            return 2
        for k, t in enumerate(termes, start=1):
            t["ID"] = f"T-{k:04d}"
        ch = [{"DATE": M.aujourdhui(), "VERSION": "1.0", "ID": f"T-0001 à T-{len(termes):04d}" if termes else "—",
               "EN": "—", "CHAMP": "import", "AVANT": "", "APRÈS": f"{len(termes)} termes en Brouillon",
               "RAISON": f"Import de {Path(args.source).name}" + (f" ({args.provenance})" if args.provenance else ""),
               "DÉCIDÉ PAR": args.par or ""}]
        dire(f"\nÀ écrire : {sortie} — {len(termes)} termes, tous en Brouillon.")
        return ecrire_ou_essai(args, sortie, args.gamme, termes, ch, existe=False)
    # ---- fusion dans un maître existant
    maitre = Path(args.dans)
    g = charger_maitre(maitre)
    par_en, par_fr = index_actifs(g["termes"])
    ajouts, identiques, conflits, sens, fr_pris = [], [], [], [], []
    tous = list(g["termes"])
    for t in termes:
        k = M.cle(t["EN"])
        existants = par_en.get(k, [])
        if existants:
            if any(M.cle(e["FR"]) == M.cle(t["FR"]) for e in existants):
                identiques.append((t, existants[0]))
                continue
            defs = [M.cle(e["DÉFINITION MÉCANIQUE"]) for e in existants]
            dt_ = M.cle(t["DÉFINITION MÉCANIQUE"])
            if dt_ and all(defs) and dt_ not in defs:
                t["NOTES"] = joindre_notes(f"Autre sens de « {t['EN']} » que " +
                                           ", ".join(e["ID"] for e in existants) + " (définitions différentes)",
                                           t["NOTES"])
                sens.append(t)
            else:
                conflits.append((t, existants))
                continue
        for e in par_fr.get(M.cle(t["FR"]), []) if t["FR"] else []:
            if M.cle(e["EN"]) != k:
                fr_pris.append((t, e))
        t["ID"] = M.prochain_id(tous)
        tous.append(t)
        ajouts.append(t)
        par_en.setdefault(k, []).append(t)
    dire(f"\nFusion dans {maitre.name} ({M.nombre_termes(g['termes'])} termes) :")
    dire(f"  à ajouter en Brouillon : {len(ajouts)} (dont {len(sens)} second(s) sens d'un mot déjà présent)")
    dire(f"  déjà présents à l'identique (EN et FR), non repris : {len(identiques)}")
    dire(f"  CONFLITS non appliqués (même EN, autre FR, sans définitions qui les distinguent) : {len(conflits)}")
    for t, ex in conflits:
        dire(f"    {t['EN']} : maître " + " ; ".join(f"{e['ID']} {e['FR']} ({e['STATUT']})" for e in ex)
             + f" — import : {t['FR']}")
    for t, e in fr_pris:
        dire(f"  À VÉRIFIER : le FR « {t['FR']} » ({t['EN']}) est déjà pris par {e['ID']} ({e['EN']})")
    if conflits:
        dire("  → Hervé tranche chaque conflit ; la décision s'applique avec la commande modifier.")
    if not ajouts:
        dire("\nRien à ajouter.")
        return 0
    v = M.version_suivante(M.version_courante(g["changelog"]), False)
    ch = g["changelog"] + [{"DATE": M.aujourdhui(), "VERSION": v, "ID": f"{ajouts[0]['ID']} à {ajouts[-1]['ID']}",
                            "EN": "—", "CHAMP": "import (fusion)", "AVANT": "",
                            "APRÈS": f"{len(ajouts)} termes ajoutés en Brouillon",
                            "RAISON": f"Import de {Path(args.source).name}" + (f" ({args.provenance})" if args.provenance else ""),
                            "DÉCIDÉ PAR": args.par or ""}]
    return ecrire_ou_essai(args, maitre, M.gamme_depuis_nom(maitre), tous, ch, existe=True)


# ------------------------------------------------------------------ modifier
class Refus(Exception):
    pass


def appliquer(g, ident, champs, raison, par, erratum, opts, nouveau=False):
    """Applique des changements à UNE ligne. Renvoie (ligne modifiée, lignes de CHANGELOG, gravité 0/1/2)."""
    termes = g["termes"]
    if nouveau:
        t = {c: "" for c in M.COLONNES}
        t["STATUT"] = "Brouillon"
        avant = None
    else:
        cand = [x for x in termes if x["ID"] == ident]
        if not cand:
            raise Refus(f"{ident} : identifiant introuvable")
        t = cand[0]
        avant = copy.deepcopy(t)
    apres = copy.deepcopy(t)
    for champ, valeur in champs:
        col = M.colonne_canonique(champ)
        if not col or col in ("ID", "DATE"):
            raise Refus(f"{ident or 'ajout'} : colonne « {champ} » non modifiable (ID et DATE sont tenus par le script)")
        if col in M.LISTES and valeur.strip():
            vv = M.valeur_canonique(col, valeur)
            if not vv:
                raise Refus(f"{ident or 'ajout'} : {col} « {valeur} » hors liste ({', '.join(M.LISTES[col])})")
            valeur = vv
        apres[col] = valeur.strip()
    s0, s1 = (avant or {}).get("STATUT", ""), apres["STATUT"]
    qui = ident or apres.get("EN") or "ajout"
    if not apres["EN"]:
        raise Refus(f"{qui} : EN vide")
    touche_en_fr = avant is not None and (M.cle(avant["EN"]) != M.cle(apres["EN"]) or avant["FR"] != apres["FR"])
    gravite = 0
    if s0 == "Gelé" and (touche_en_fr or s1 not in ("Gelé", "Archivé")) and not erratum:
        raise Refus(f"{qui} : terme Gelé (imprimé). Changer EN/FR ou le dégeler exige --erratum <référence de "
                    "l'erratum ou de l'accord éditeur>. Sinon : l'archiver et ajouter le nouveau terme.")
    if (s0 in M.EN_VIGUEUR or s1 in M.EN_VIGUEUR) and avant != apres:
        if not raison or not par:
            raise Refus(f"{qui} : un terme Confirmé ou Gelé ne change qu'avec --raison et --par (qui a décidé)")
        gravite = 2 if (s0 == "Gelé" and (touche_en_fr or s1 != "Gelé")) else 1
    if s1 in M.EN_VIGUEUR and s0 != s1:
        if not apres["FR"] or " / " in apres["FR"]:
            raise Refus(f"{qui} : FR vide ou avec plusieurs propositions — à trancher avant de valider")
        if apres["CATÉGORIE"] in M.GENRE_OBLIGATOIRE and not apres["GENRE"]:
            raise Refus(f"{qui} : GENRE non déclaré pour un terme {apres['CATÉGORIE']}. Le demander à Hervé "
                        "(jamais deviné) ; « — » pour un mot-clé non nominal.")
    if s1 == "Gelé" and not apres["PUBLIÉ DANS"]:
        raise Refus(f"{qui} : Gelé exige PUBLIÉ DANS (le produit où le terme est imprimé)")
    if s1 == "Archivé" and s0 != "Archivé" and not raison:
        raise Refus(f"{qui} : archiver exige --raison (par quoi le terme est remplacé, à partir de quel produit)")
    # doublons (I-38 / D-33) et FR déjà pris (I-35)
    if s1 in M.ACTIFS:
        autres = [x for x in termes if x is not t and x["STATUT"] in M.ACTIFS]
        memes = [x for x in autres if M.cle(x["EN"]) == M.cle(apres["EN"])]
        if memes and (nouveau or M.cle(avant["EN"]) != M.cle(apres["EN"]) or s0 not in M.ACTIFS):
            dfs = [M.cle(x["DÉFINITION MÉCANIQUE"]) for x in memes]
            d = M.cle(apres["DÉFINITION MÉCANIQUE"])
            if not (opts.second_sens and d and all(dfs) and d not in dfs):
                raise Refus(f"{qui} : « {apres['EN']} » existe déjà ({', '.join(x['ID'] + ' ' + x['FR'] for x in memes)}). "
                            "Second sens mécanique ? --second-sens avec une DÉFINITION MÉCANIQUE différente, "
                            "remplie des deux côtés.")
        if apres["FR"] and (nouveau or (avant and avant["FR"] != apres["FR"])):
            pris = [x for x in autres if x["FR"] and M.cle(x["FR"]) == M.cle(apres["FR"])
                    and M.cle(x["EN"]) != M.cle(apres["EN"])]
            if pris and not opts.accepter_fr_partage:
                raise Refus(f"{qui} : le FR « {apres['FR']} » est déjà pris par "
                            + ", ".join(f"{x['ID']} ({x['EN']})" for x in pris)
                            + ". Si Hervé le veut ainsi : --accepter-fr-partage.")
    lignes = []
    if nouveau:
        apres["ID"] = M.prochain_id(termes)
        apres["DATE"] = M.aujourdhui()
        lignes.append({"ID": apres["ID"], "EN": apres["EN"], "CHAMP": "ajout", "AVANT": "",
                       "APRÈS": f"{apres['FR']} ({apres['STATUT']})", "RAISON": raison or "", "DÉCIDÉ PAR": par or ""})
        termes.append(apres)
        return apres, lignes, gravite
    for c in M.COLONNES:
        if avant[c] != apres[c]:
            lignes.append({"ID": apres["ID"], "EN": apres["EN"], "CHAMP": c, "AVANT": avant[c], "APRÈS": apres[c],
                           "RAISON": joindre_notes(raison, f"erratum : {erratum}" if erratum else ""),
                           "DÉCIDÉ PAR": par or ""})
    if lignes:
        apres["DATE"] = M.aujourdhui()
        t.update(apres)
    return t, lignes, gravite


def cmd_modifier(args):
    maitre = Path(args.maitre)
    g = charger_maitre(maitre)
    operations = []
    if args.lot:
        lignes = lecture.lignes_csv(args.lot)
        ent = [M.cle_entete(x) for x in lignes[0]]
        need = ["ID", "CHAMP", "VALEUR"]
        if not all(n in ent for n in need):
            sys.exit("Le lot doit avoir les colonnes ID;CHAMP;VALEUR (puis RAISON;PAR;ERRATUM, facultatives).")
        idx = {n: ent.index(n) for n in ent}
        groupes = {}
        for l in lignes[1:]:
            if not any(x.strip() for x in l):
                continue
            def v(n):
                return l[idx[n]].strip() if n in idx and idx[n] < len(l) else ""
            gr = groupes.setdefault(v("ID"), {"champs": [], "raison": v("RAISON"), "par": v("PAR"), "erratum": v("ERRATUM")})
            gr["champs"].append((v("CHAMP"), v("VALEUR")))
            for n, k in (("RAISON", "raison"), ("PAR", "par"), ("ERRATUM", "erratum")):
                gr[k] = gr[k] or v(n)
        for ident, gr in groupes.items():
            operations.append((ident, gr["champs"], gr["raison"], gr["par"], gr["erratum"], False))
    else:
        champs = []
        for c in args.champ or []:
            col, sep, val = c.partition("=")
            if not sep:
                sys.exit(f"--champ « {c} » : écrire COLONNE=valeur")
            champs.append((col, val))
        if not champs:
            sys.exit("Rien à modifier : ajouter au moins un --champ COLONNE=valeur")
        if not args.ajouter and not args.id:
            sys.exit("Préciser --id T-0001 (modifier) ou --ajouter (nouveau terme)")
        operations.append((args.id, champs, args.raison, args.par, args.erratum, bool(args.ajouter)))
    nouvelles, erreurs, gravite = [], [], 0
    for ident, champs, raison, par, erratum, nouveau in operations:
        try:
            _, lignes, gr = appliquer(g, ident, champs, raison, par, erratum, args, nouveau)
            nouvelles += lignes
            gravite = max(gravite, gr)
        except Refus as e:
            erreurs.append(str(e))
    if erreurs:
        dire(f"REFUS — rien n'est appliqué ({len(erreurs)} problème(s)) :")
        for e in erreurs:
            dire("  - " + e)
        return 2
    if not nouvelles:
        dire("Aucun changement : les valeurs demandées sont déjà celles du glossaire.")
        return 0
    v0 = M.version_courante(g["changelog"])
    v = M.version_suivante(v0, gravite == 2) if gravite else v0
    for l in nouvelles:
        l["DATE"], l["VERSION"] = M.aujourdhui(), v
    dire(f"Changements prévus ({len(nouvelles)}) — " + (f"version {v0} → {v} :" if v != v0 else f"version {v0} inchangée (aucun terme validé touché) :"))
    for l in nouvelles:
        dire(f"  {l['ID']} {l['EN']} · {l['CHAMP']} : « {l['AVANT']} » → « {l['APRÈS']} »")
    return ecrire_ou_essai(args, maitre, M.gamme_depuis_nom(maitre), g["termes"], g["changelog"] + nouvelles, existe=True)


def cmd_exporter(args):
    g = M.lire_glossaire(args.maitre)
    garder = M.STATUTS if args.avec_archives else M.ACTIFS
    n = sum(1 for t in g["termes"] if t["EN"] and t["STATUT"] in garder)
    dire(f"Export pour un {args.pour} : {n} terme(s) ({', '.join(garder)}), sans NOTES ni SOURCE, "
         f"avec un onglet Lisez-moi" + (" et deux colonnes de retour." if args.pour == "relecteur" else "."))
    dire(f"Fichier : {args.sortie} — le glossaire de référence n'est pas modifié.")
    if not args.ecrire:
        dire("\nESSAI : rien n'a été écrit. Relancer avec --ecrire.")
        return 0
    n = M.ecrire_export(args.sortie, M.gamme_depuis_nom(args.maitre), g["termes"], args.pour, args.avec_archives)
    dire(f"Écrit : {args.sortie} ({n} termes).")
    return 0


def cmd_retours(args):
    """Liste les remarques d'un relecteur, par code, avec des comptes exacts. Ne modifie rien."""
    feuilles = {M.nfc(k): v for k, v in lecture.feuilles_xlsx(args.fichier).items()}
    t = feuilles.get("Termes")
    if not t:
        sys.exit("Onglet Termes introuvable : est-ce bien un export du glossaire ?")
    ent = [M.nfc(x).strip() for x in t[0]]
    if "RETOUR RELECTEUR" not in ent:
        sys.exit("Colonne RETOUR RELECTEUR introuvable : ce fichier n'est pas un export pour relecteur.")
    j, jen, jfr = ent.index("RETOUR RELECTEUR"), ent.index("EN"), ent.index("FR")
    jref = ent.index("RÉF.") if "RÉF." in ent else None
    groupes = {}
    for n, l in enumerate(t[1:], start=2):
        r = l[j].strip() if j < len(l) else ""
        if not r:
            continue
        code = r.split("]")[0] + "]" if r.startswith("[") and "]" in r else "(sans code)"
        groupes.setdefault(code.upper(), []).append((n, l[jref] if jref is not None and jref < len(l) else "",
                                                     l[jen], l[jfr], r))
    total = sum(len(v) for v in groupes.values())
    dire(f"Retours du relecteur : {total} remarque(s) sur {len(t) - 1} ligne(s).")
    for code in ["[ERR]", "[MOD]", "[?]", "[OK]"] + sorted(c for c in groupes if c not in ("[ERR]", "[MOD]", "[?]", "[OK]")):
        if code in groupes:
            dire(f"\n{code} — {len(groupes[code])}")
            for n, ref_, en, fr, r in groupes[code]:
                dire(f"  ligne {n} · {ref_} · {en} → {fr} : {r}")
    dire("\nOrdre de traitement : [ERR] d'abord (glossaire ET texte, et les autres projets où le terme apparaît), "
         "puis [MOD] et [?] ; Hervé décide, la décision s'applique avec la commande modifier.")
    return 0


def cmd_comparer(args):
    """Ce qui a changé entre deux états du glossaire (ex. dernière sauvegarde → fichier actuel). Lecture seule."""
    a_, b_ = M.lire_glossaire(args.ancien), M.lire_glossaire(args.nouveau)
    ia = {t["ID"] or f"(ligne {t['_ligne']})": t for t in a_["termes"]}
    ib = {t["ID"] or f"(ligne {t['_ligne']})": t for t in b_["termes"]}
    ajoutes = [k for k in ib if k not in ia]
    retires = [k for k in ia if k not in ib]
    modifs = [(k, c, ia[k][c], ib[k][c]) for k in ib if k in ia for c in M.COLONNES if ia[k][c] != ib[k][c]]
    dire(f"Comparaison : {Path(args.ancien).name} ({M.nombre_termes(a_['termes'])} termes) → "
         f"{Path(args.nouveau).name} ({M.nombre_termes(b_['termes'])} termes)")
    dire(f"  lignes ajoutées : {len(ajoutes)} · lignes disparues : {len(retires)} · valeurs changées : {len(modifs)}")
    for k in ajoutes:
        dire(f"  + {k} {ib[k]['EN']} → {ib[k]['FR']} ({ib[k]['STATUT']})")
    for k in retires:
        dire(f"  − {k} {ia[k]['EN']} → {ia[k]['FR']} ({ia[k]['STATUT']})  ← une ligne ne disparaît jamais : l'archiver")
    for k, c, x, y in modifs:
        dire(f"  ~ {k} {ib[k]['EN']} · {c} : « {x} » → « {y} »")
    nouv_ch = len(b_["changelog"]) - len(a_["changelog"])
    dire(f"  lignes de CHANGELOG ajoutées entre les deux : {nouv_ch}")
    if (modifs or ajoutes or retires) and nouv_ch <= 0:
        dire("  → Des changements sans trace au CHANGELOG (modification à la main ?) : les montrer à Hervé et, "
             "avec son accord, les tracer (commande modifier, ou ligne ajoutée au CHANGELOG).")
    return 0


def cmd_sauvegarder(args):
    sauv, deja = M.sauvegarder(args.maitre, args.archives)
    dire(f"Sauvegarde : {sauv}" + (" (identique, déjà présente : rien de recopié)" if deja else ""))
    return 0


def auto_test():
    """Joue import, refus et modifications sur un dossier fabriqué (aucun fichier réel touché)."""
    import contextlib
    import io
    import tempfile
    echecs = []

    def lancer(*argv):
        sys.argv = ["gerer_glossaire.py", *argv]
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            try:
                code = main()
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 2
        return code, sortie.getvalue()

    def verifier(cond, msg):
        if not cond:
            echecs.append(msg)

    with tempfile.TemporaryDirectory() as d:
        racine = Path(d) / "HERVÉ WORLD"
        (racine / "Glossaires").mkdir(parents=True)
        (racine / "IMPORT").mkdir()
        src = racine / "IMPORT" / "ancien.csv"
        src.write_text("Glossaire de test\nTerme (EN);Terme (FR);Type;Statut;Notes\nRESSOURCES\n"
                       "Health;Santé;Ressource;Validé;points de vie\nTravel;Voyage / Trajet;Action;Validé;\n"
                       "Wyrm Lord;Seigneur Guivre;Personnage;À voir;\n", encoding="utf-8")
        g = racine / "Glossaires" / "Glossaire_Test.xlsx"
        code, out = lancer("importer", str(src), "--gamme", "Test", "--sortie", str(g))
        verifier(code == 0 and not g.exists(), "l'essai a écrit un fichier")
        verifier("Termes trouvés (lignes avec un terme anglais) : 3" in out, "compte des termes importés faux")
        code, out = lancer("importer", str(src), "--gamme", "Test", "--sortie", str(g), "--ecrire")
        lu = M.lire_glossaire(g)
        verifier(code == 0 and M.nombre_termes(lu["termes"]) == 3, "import écrit : 3 termes attendus")
        verifier(all(t["STATUT"] == "Brouillon" for t in lu["termes"]), "un terme importé n'est pas en Brouillon")
        verifier(all("Statut d'origine" in t["NOTES"] for t in lu["termes"]), "statut d'origine perdu")
        octets = g.read_bytes()
        code, out = lancer("modifier", str(g), "--id", "T-0003", "--champ", "STATUT=Confirmé", "--par", "Hervé",
                           "--raison", "test", "--ecrire")
        verifier(code == 2 and g.read_bytes() == octets, "validation sans genre acceptée")
        code, out = lancer("modifier", str(g), "--id", "T-0002", "--champ", "STATUT=Confirmé", "--par", "Hervé",
                           "--raison", "test", "--ecrire")
        verifier(code == 2, "validation d'un FR à double proposition acceptée")
        code, out = lancer("modifier", str(g), "--id", "T-0003", "--champ", "STATUT=Confirmé", "--champ", "GENRE=m",
                           "--par", "Hervé", "--raison", "test", "--ecrire")
        lu = M.lire_glossaire(g)
        verifier(code == 0 and lu["termes"][2]["STATUT"] == "Confirmé", "validation avec genre refusée")
        verifier(len(lu["changelog"]) == 3 and M.version_courante(lu["changelog"]) == "1.1", "CHANGELOG ou version faux")
        archives = list((racine / "Core" / "Archives").glob("Glossaire_Test_avant_*_3termes*.xlsx"))
        verifier(len(archives) == 1, "sauvegarde datée absente")
        code, _ = lancer("modifier", str(g), "--id", "T-0003", "--champ", "STATUT=Gelé", "--par", "Hervé", "--raison", "t")
        verifier(code == 2, "gel sans PUBLIÉ DANS accepté")
        code, _ = lancer("modifier", str(g), "--ajouter", "--champ", "EN=health", "--champ", "FR=Vie", "--ecrire")
        verifier(code == 2, "doublon d'anglais accepté")
        code, _ = lancer("importer", str(src), "--gamme", "Test", "--sortie", str(racine / "Glossaires" / "Glossaire_Test2.xlsx"))
        verifier(code == 2, "second glossaire maître accepté")
        verrou = racine / "Glossaires" / "~$Glossaire_Test.xlsx"
        verrou.write_text("")
        avant = len(list((racine / "Core" / "Archives").iterdir()))
        code, _ = lancer("modifier", str(g), "--id", "T-0001", "--champ", "NOTES=x", "--ecrire")
        verifier(code == 2 and len(list((racine / "Core" / "Archives").iterdir())) == avant, "fichier ouvert dans Excel non détecté")
    if echecs:
        print("AUTO-TEST ÉCHEC : " + " ; ".join(echecs))
        return 1
    print("AUTO-TEST OK — import en Brouillon, essai sans écriture, 5 refus, validation, CHANGELOG, sauvegarde, verrou")
    return 0


def main():
    if "--auto-test" in sys.argv:
        return auto_test()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    commun = argparse.ArgumentParser(add_help=False)
    commun.add_argument("--ecrire", action="store_true", help="écrire pour de bon (sinon : essai)")
    commun.add_argument("--archives", help="dossier des sauvegardes (défaut : <HERVÉ WORLD>/Core/Archives)")
    commun.add_argument("--par", help="qui a décidé (Hervé, éditeur + date…)")
    commun.add_argument("--raison", help="pourquoi")
    c = sp.add_parser("creer", parents=[commun])
    c.add_argument("--gamme", required=True)
    c.add_argument("--sortie", required=True)
    i = sp.add_parser("importer", parents=[commun])
    i.add_argument("source")
    i.add_argument("--gamme", required=True)
    i.add_argument("--sortie")
    i.add_argument("--dans")
    i.add_argument("--provenance", help="d'où vient ce glossaire (va dans SOURCE de chaque terme)")
    i.add_argument("--feuille")
    i.add_argument("--colonne", action="append", help="CIBLE=En-tête source (ex. EN=Terme anglais)")
    i.add_argument("--garder-seuls", action="store_true", help="importer aussi les lignes où seul l'anglais est rempli")
    m = sp.add_parser("modifier", parents=[commun])
    m.add_argument("maitre")
    m.add_argument("--id")
    m.add_argument("--ajouter", action="store_true")
    m.add_argument("--champ", action="append", help="COLONNE=valeur")
    m.add_argument("--erratum")
    m.add_argument("--second-sens", action="store_true")
    m.add_argument("--accepter-fr-partage", action="store_true")
    m.add_argument("--lot")
    e = sp.add_parser("exporter", parents=[commun])
    e.add_argument("maitre")
    e.add_argument("--sortie", required=True)
    e.add_argument("--pour", choices=["traducteur", "relecteur"], default="traducteur")
    e.add_argument("--avec-archives", action="store_true")
    rt = sp.add_parser("retours", parents=[commun])
    rt.add_argument("fichier")
    cp = sp.add_parser("comparer", parents=[commun])
    cp.add_argument("ancien")
    cp.add_argument("nouveau")
    s = sp.add_parser("sauvegarder", parents=[commun])
    s.add_argument("maitre")
    a = p.parse_args()
    try:
        return {"creer": cmd_creer, "importer": cmd_importer, "modifier": cmd_modifier, "exporter": cmd_exporter,
                "retours": cmd_retours, "comparer": cmd_comparer, "sauvegarder": cmd_sauvegarder}[a.cmd](a)
    except (FileExistsError, PermissionError, ValueError, FileNotFoundError) as e:
        dire(f"Refus : {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
