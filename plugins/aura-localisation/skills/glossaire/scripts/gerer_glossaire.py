#!/usr/bin/env python3
"""Créer, importer, fusionner, modifier et sauvegarder un glossaire au standard v3.

PAR DÉFAUT RIEN N'EST ÉCRIT : chaque commande affiche ce qu'elle ferait. On relance avec --ecrire
après l'accord d'Hervé. Avant d'écrire un glossaire existant, une sauvegarde datée est faite dans
Core/Archives (jamais écrasée). Aucun terme n'entre validé par import : tout arrive en Brouillon.
Le classeur est réécrit en entier : ce que le programme ne sait pas réécrire fait REFUSER l'écriture
(onglet ou colonne hors standard dans Termes ou CHANGELOG, commentaire Excel hors des lignes de
termes) ; un commentaire Excel posé sur un terme est repris dans ses NOTES, avec sa ligne de
CHANGELOG ; le texte tapé à la main dans Tableau de bord ou Notice (onglets que le programme
régénère) est listé à chaque essai et à chaque écriture comme « non gardé ».

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
def textes_non_repris(chemin, gamme, termes, changelog):
    """Le texte des onglets Tableau de bord et Notice qu'aucune écriture du programme ne produit (tapé
    à la main, par exemple) : la réécriture ne le reproduira pas. On régénère le classeur, tel qu'il est
    et tel qu'il sera, dans un dossier temporaire, et on compare ; la liste est affichée, jamais tue."""
    import tempfile
    avant = M.textes_onglets(chemin)
    actuel = M.lire_glossaire(chemin)
    produits = {}
    with tempfile.TemporaryDirectory() as d:
        for nom, (ts, ch) in {"actuel": (actuel["termes"], actuel["changelog"]), "futur": (termes, changelog)}.items():
            f = Path(d) / nom / Path(chemin).name
            M.ecrire_glossaire(f, gamme, ts, ch)
            for o, xs in M.textes_onglets(f).items():
                produits.setdefault(o, set()).update(xs)
    perdus = [(o, x) for o in avant for x in avant[o] if x not in produits.get(o, set())]
    for o, x in perdus:
        dire(f"NON GARDÉ à la réécriture (onglet {o}, régénéré par le programme) : « {x} »")
    return perdus


def ecrire_ou_essai(args, chemin, gamme, termes, changelog, existe):
    if not args.ecrire:
        if existe:
            textes_non_repris(chemin, gamme, termes, changelog)
            dire("À savoir : les couleurs, largeurs de colonne et mises en forme ajoutées à la main dans Excel ne "
                 "sont pas gardées à la réécriture ; la sauvegarde datée, elle, les garde.")
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
        textes_non_repris(chemin, gamme, termes, changelog)
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
    if g["changelog_hors_standard"]:
        pb.append("colonnes hors standard dans CHANGELOG (le script ne sait pas les réécrire) : "
                  + ", ".join(g["changelog_hors_standard"]) + " ; à porter dans RAISON, ou dans un autre classeur")
    if g["changelog_hors_entete"]:
        pb.append(f"{g['changelog_hors_entete']} cellule(s) remplie(s) sans en-tête dans CHANGELOG")
    for onglet, ref, texte in M.commentaires_hors_termes(g):
        pb.append(f"commentaire Excel que le script ne peut reprendre nulle part ({onglet}!{ref}) : « {texte} » — "
                  "à recopier ailleurs par Hervé (dans NOTES d'un terme, par exemple), puis à supprimer dans Excel")
    return pb


def reprendre_commentaires(g):
    """Au moment d'écrire : chaque commentaire Excel posé sur un terme passe à la fin de ses NOTES (le
    programme ne sait pas réécrire un commentaire). Renvoie les lignes de CHANGELOG (sans date ni
    version) de ces reprises."""
    lignes = []
    par_ligne = {t["_ligne"]: t for t in g["termes"] if "_ligne" in t}
    for onglet, ref, texte in g["commentaires"]:
        j, n = M.ref_cellule(ref)
        t = par_ligne.get(n) if onglet == "Termes" else None
        if t is None or not texte:
            continue
        colonne = g["entetes"][j] if j is not None and j < len(g["entetes"]) and g["entetes"][j] else f"cellule {ref}"
        avant = t["NOTES"]
        t["NOTES"] = joindre_notes(avant, f"Commentaire Excel ({colonne}) : {texte}")
        lignes.append({"ID": t["ID"], "EN": t["EN"], "CHAMP": "NOTES", "AVANT": avant, "APRÈS": t["NOTES"],
                       "RAISON": f"commentaire Excel de la cellule {ref} repris dans NOTES (le programme ne garde pas "
                                 "les commentaires)", "DÉCIDÉ PAR": ""})
        dire(f"Commentaire Excel sur {t['ID']} {t['EN']} ({colonne}) : repris dans ses NOTES à l'écriture — « {texte} »")
    return lignes


def charger_maitre(chemin):
    g = M.lire_glossaire(chemin)
    pb = maitre_conforme(g)
    if pb:
        dire(f"Refus : {chemin} n'est pas au standard, le réécrire ferait perdre des données.")
        for p in pb:
            dire("  - " + p)
        dire("Ce fichier n'est pas un glossaire maître au standard : ne le modifie pas pour l'y mettre. S'il s'agit "
             "d'une source (ancien glossaire, démonstration), importe-le comme source : « importer <ce fichier> "
             "--sortie Glossaires/Glossaire_<Gamme>.xlsx » (version 2.0 : « migrer »). S'il s'agit bien du maître, "
             "montre ces points à Hervé (controle_glossaire.py) ; c'est lui qui décide.")
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
                    if cible not in forcees:   # une colonne désignée par --colonne passe avant toute autre
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
        # Le séparateur et la ligne de titre au-dessus du tableau : une seule règle, celle du lecteur commun
        return {p.name: lecture.lignes_csv(p)}
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
        i = None
    # une colonne désignée par Hervé doit exister telle quelle : jamais remplacée en silence par une autre
    if i is None:
        nom, lignes = next(((n, l) for n, l in feuilles.items() if any(any(str(c).strip() for c in x) for x in l)),
                           (next(iter(feuilles), "?"), []))
        tete = next((x for x in lignes if sum(1 for c in x if str(c).strip()) >= 2), [])
    else:
        tete = lignes[i]
    lus = [M.cle_entete(c) for c in tete]
    absentes = [f"{cible}=« {entete} »" for cible, entete in forcees.items() if M.cle_entete(entete) not in lus]
    if absentes:
        dire("Refus : --colonne " + ", ".join(absentes) + " : aucun en-tête de ce nom dans la feuille « " + nom
             + " » (en-têtes lus : " + (", ".join(str(c).strip() for c in tete if str(c).strip()) or "aucun") + ").")
        sys.exit(2)
    if i is None:
        dire("Refus : aucune ligne d'en-tête avec une colonne anglaise ET une colonne française n'a été trouvée.")
        dire("Indiquer les colonnes : --colonne EN=<en-tête anglais> --colonne FR=<en-tête français>.")
        sys.exit(2)
    termes, rapport = termes_de_feuille(nom, lignes, i, corresp, args, Path(source).name)
    # Les AUTRES feuilles ne sont pas lues par l'import : on les nomme, avec leur taille, au lieu de les
    # taire (un onglet EXTENSION disparaissait sans un mot). Pour un glossaire v2.0 : commande migrer.
    rapport["feuilles_ignorees"] = [(n, sum(1 for l in ls if any(str(c).strip() for c in l)))
                                    for n, ls in feuilles.items() if n != nom]
    return termes, rapport


def termes_de_feuille(nom, lignes, i, corresp, args, nom_src):
    """Les termes d'UNE feuille dont l'en-tête est à la ligne i (statut d'origine gardé dans _statut_src)."""
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
        t["_statut_src"] = st
        t["NOTES"] = joindre_notes(*notes)
        t["DATE"] = date
        t["_ligne_source"] = n
        termes.append(t)
    return termes, rapport


def afficher_rapport(rapport, termes, source):
    dire(f"Source : {source} — feuille « {rapport['feuille']} », en-tête trouvé ligne {rapport['ligne_entete']}.")
    for n, nb in rapport.get("feuilles_ignorees", []):
        dire(f"  FEUILLE NON LUE : « {n} » ({nb} lignes remplies). Glossaire v2.0 à plusieurs onglets → commande migrer.")
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
        # le fichier qu'on importe n'est pas un second maître, même s'il est rangé dans Glossaires/ (la démo)
        voisins = [v for v in maitres_voisins(sortie, args.gamme) if v.resolve() != Path(args.source).resolve()]
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
    reprises = [dict(l, DATE=M.aujourdhui(), VERSION=v) for l in reprendre_commentaires(g)]
    ch = g["changelog"] + reprises + [{"DATE": M.aujourdhui(), "VERSION": v, "ID": f"{ajouts[0]['ID']} à {ajouts[-1]['ID']}",
                            "EN": "—", "CHAMP": "import (fusion)", "AVANT": "",
                            "APRÈS": f"{len(ajouts)} termes ajoutés en Brouillon",
                            "RAISON": f"Import de {Path(args.source).name}" + (f" ({args.provenance})" if args.provenance else ""),
                            "DÉCIDÉ PAR": args.par or ""}]
    return ecrire_ou_essai(args, maitre, M.gamme_depuis_nom(maitre), tous, ch, existe=True)


# ------------------------------------------------------------------ migrer (glossaire v2.0 → v3)
# Un glossaire fait AVEC Hervé en v2.0 (GLOSSAIRE_<GAMME>_vN.xlsx, onglets GLOSSAIRE_X, EN_ATTENTE,
# HÉRITÉ, EXTENSION, CHANGELOG, LISEZMOI). Ses statuts ont été validés avec lui : on les GARDE (au
# contraire d'un import, où rien n'entre validé). On lit TOUS les onglets, on compte par onglet, on
# reprend son CHANGELOG, et l'ancien fichier n'est jamais déplacé ni modifié.
ONGLETS_HISTOIRE = {"CHANGELOG", "HISTORIQUE"}
ONGLETS_SANS_TERMES = {"LISEZMOI", "LISEZ MOI", "NOTICE", "TABLEAU DE BORD", "README"}


def cmd_migrer(args):
    source = Path(args.source)
    if not source.is_file():
        sys.exit(f"Fichier introuvable : {source}")
    gamme = args.gamme
    sortie = Path(args.sortie) if args.sortie else source.parent / f"Glossaire_{gamme}.xlsx"
    if sortie.exists():
        dire(f"Refus : {sortie.name} existe déjà. Un seul maître par gamme : fusionner avec "
             f"« importer {source.name} --dans {sortie.name} », onglet par onglet (--feuille).")
        return 2
    voisins = [v for v in maitres_voisins(sortie, gamme) if v.resolve() != source.resolve()]
    if voisins:
        dire("Refus : un autre glossaire de cette gamme existe déjà : " + ", ".join(v.name for v in voisins))
        return 2
    feuilles = lire_source(source, None)
    termes, compte, histoire, ignorees, doublons = [], [], [], [], 0
    vus = {}
    for nom, lignes in feuilles.items():
        k = M.cle_entete(nom)
        remplies = sum(1 for l in lignes if any(str(c).strip() for c in l))
        if k in ONGLETS_HISTOIRE:
            for l in lignes[1:]:
                cel = [M.nfc(str(c)).strip() for c in l] + ["", "", "", ""]
                if any(cel[:4]):
                    histoire.append({"DATE": M.date_texte(cel[0]) or cel[0], "VERSION": cel[1], "ID": "—", "EN": "—",
                                     "CHAMP": "historique v2.0", "AVANT": "", "APRÈS": cel[2],
                                     "RAISON": cel[3], "DÉCIDÉ PAR": ""})
            compte.append((nom, f"historique : {len(histoire)} lignes reprises au CHANGELOG"))
            continue
        if k in ONGLETS_SANS_TERMES:
            ignorees.append((nom, remplies, "notice, pas de termes"))
            continue
        i, corresp = detecter(lignes, {})
        if i is None:
            ignorees.append((nom, remplies, "pas d'en-tête anglais/français"))
            continue
        ts, _ = termes_de_feuille(nom, lignes, i, corresp, args, source.name)
        repris = 0
        for t in ts:
            st = M.valeur_canonique("STATUT", t.get("_statut_src", "")) if t.get("_statut_src") else None
            if M.cle_entete(nom) == "EN ATTENTE":
                st = "À confirmer"
            t["STATUT"] = st or "Brouillon"
            t["SOURCE"] = f"glossaire v2.0 {source.name}, onglet {nom}" + (" (statut repris)" if st else "")
            if M.cle_entete(nom) in ("HERITE",):
                t["NOTES"] = joindre_notes("Repris de l'onglet HÉRITÉ (glossaire de la boîte de base)", t["NOTES"])
            cle = (M.cle(t["EN"]), M.cle(t["FR"]))
            if cle in vus:
                doublons += 1
                vus[cle]["NOTES"] = joindre_notes(vus[cle]["NOTES"], f"aussi dans l'onglet {nom}")
                continue
            vus[cle] = t
            termes.append(t)
            repris += 1
        compte.append((nom, f"{repris} termes repris (en-tête ligne {i + 1})"))
    for k, t in enumerate(termes, start=1):
        t["ID"] = f"T-{k:04d}"
    dire(f"Migration de {source.name} (glossaire v2.0) vers {sortie.name} :")
    for nom, txt in compte:
        dire(f"  onglet « {nom} » : {txt}")
    for nom, nb, pourquoi in ignorees:
        dire(f"  onglet « {nom} » : non lu ({nb} lignes remplies) — {pourquoi}")
    dire(f"  doublons exacts entre onglets (même anglais, même français), gardés une fois : {doublons}")
    par_statut = {}
    for t in termes:
        par_statut[t["STATUT"]] = par_statut.get(t["STATUT"], 0) + 1
    dire("  statuts après migration : " + ", ".join(f"{s} {n}" for s, n in sorted(par_statut.items())))
    dire(f"  L'ancien fichier {source.name} n'est ni modifié ni déplacé. Une fois le nouveau vérifié, Hervé le range "
         f"lui-même dans Core/Archives/ (deux maîtres pour une gamme, c'est deux vérités).")
    ch = histoire + [{"DATE": M.aujourdhui(), "VERSION": "3.0", "ID": f"T-0001 à T-{len(termes):04d}" if termes else "—",
                      "EN": "—", "CHAMP": "migration v2.0 → v3", "AVANT": source.name,
                      "APRÈS": f"{len(termes)} termes, statuts repris", "RAISON": "mise à jour d'AURA",
                      "DÉCIDÉ PAR": args.par or ""}]
    return ecrire_ou_essai(args, sortie, gamme, termes, ch, existe=False)


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
    nouvelles = nouvelles + reprendre_commentaires(g)
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
    # ---- migration d'un glossaire v2.0 (6 onglets, statuts validés avec Hervé)
    with tempfile.TemporaryDirectory() as d:
        gl = Path(d) / "HERVÉ WORLD" / "Glossaires"
        gl.mkdir(parents=True)
        v2 = gl / "GLOSSAIRE_TG_v2.3.xlsx"
        tete = ["TERME_EN", "TERME_FR", "CATÉGORIE", "CONTEXTE", "STATUT", "PROJET_ORIGINE", "VERSION", "NOTES"]
        _xlsx_simple(v2, {
            "GLOSSAIRE_TG": [tete, ["Shard", "Éclat", "OBJET", "Gain 1 Shard", "Confirmé", "base", "v1", ""],
                             ["Exhaust", "Épuiser", "MÉCANIQUE", "Exhaust a card", "Gelé", "base", "v2", ""],
                             ["Rest", "Repos", "MÉCANIQUE", "", "Brouillon", "base", "v1", ""]],
            "EN_ATTENTE": [tete, ["Wyrm", "Guivre", "LORE", "", "Brouillon", "ext1", "v1", "attente éditeur"]],
            "EXTENSION": [tete, ["Sanctum", "Sanctuaire", "LIEU", "", "Confirmé", "ext1", "v1", ""],
                          ["Dread", "Effroi", "MÉCANIQUE", "", "À confirmer", "ext1", "v1", ""]],
            "HÉRITÉ": [tete, ["Shard", "Éclat", "OBJET", "", "Confirmé", "base", "v1", ""]],
            "CHANGELOG": [["Date", "Version", "Nature", "Raison"], ["2026-06-02", "v2.2", "Shard validé", "Hervé"],
                          ["2026-06-09", "v2.3", "Exhaust gelé", "impression"]],
            "LISEZMOI": [["Glossaire de la gamme TG — à lire avant tout partage"]],
        })
        octets_v2 = v2.read_bytes()
        cible = gl / "Glossaire_TG.xlsx"
        code, out = lancer("migrer", str(v2), "--gamme", "TG", "--ecrire")
        verifier(code == 0 and cible.exists(), f"migration v2.0 refusée : {out[-300:]}")
        verifier(v2.read_bytes() == octets_v2, "la migration a modifié l'ancien glossaire v2.0")
        if cible.exists():
            lu = M.lire_glossaire(cible)
            st = {t["EN"]: t["STATUT"] for t in lu["termes"]}
            verifier(M.nombre_termes(lu["termes"]) == 6, f"migration : 6 termes attendus, {M.nombre_termes(lu['termes'])} lus")
            verifier(st.get("Shard") == "Confirmé" and st.get("Exhaust") == "Gelé" and st.get("Sanctum") == "Confirmé",
                     f"migration : statuts validés perdus {st}")
            verifier(st.get("Wyrm") == "À confirmer", "migration : terme EN_ATTENTE pas « À confirmer »")
            verifier("Sanctum" in st and "Dread" in st, "migration : l'onglet EXTENSION a été perdu")
            verifier(len(lu["changelog"]) == 3, f"migration : historique v2.0 non repris ({len(lu['changelog'])} lignes)")
        verifier("doublons exacts entre onglets (même anglais, même français), gardés une fois : 1" in out,
                 "migration : doublon HÉRITÉ non signalé")
        verifier("« LISEZMOI » : non lu" in out, "migration : onglet sans termes non déclaré")
        code, out = lancer("migrer", str(v2), "--gamme", "TG", "--ecrire")
        verifier(code == 2, "migration rejouée par-dessus un maître existant acceptée")
        # l'import ordinaire nomme les feuilles qu'il ne lit pas
        code, out = lancer("importer", str(v2), "--gamme", "Autre", "--sortie", str(Path(d) / "x.xlsx"))
        verifier("FEUILLE NON LUE : « EXTENSION »" in out, "l'import tait les feuilles qu'il ne lit pas")
    # ---- colonne désignée à l'import : jamais remplacée en silence par une autre
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "source.csv"
        src.write_text("EN;Traduction;Terme FR retenu\nHealth;Santé;Vie\n", encoding="utf-8")
        code, out = lancer("importer", str(src), "--gamme", "Col", "--sortie", str(Path(d) / "Glossaire_Col.xlsx"),
                           "--colonne", "FR=Terme FR final")
        verifier(code == 2 and "aucun en-tête de ce nom" in out, f"--colonne vers un en-tête absent acceptée (code {code})")
        sortie = Path(d) / "Glossaire_Col.xlsx"
        code, out = lancer("importer", str(src), "--gamme", "Col", "--sortie", str(sortie),
                           "--colonne", "FR=Terme FR retenu", "--ecrire")
        lu = M.lire_glossaire(sortie)["termes"] if sortie.exists() else []
        verifier(code == 0 and lu and lu[0]["FR"] == "Vie",
                 f"--colonne FR=« Terme FR retenu » : FR « Vie » attendu, lu {[x['FR'] for x in lu]}")
    # ---- ce que la réécriture ne sait pas garder : refusé, repris dans NOTES, ou montré — jamais perdu en silence
    with tempfile.TemporaryDirectory() as d:
        gl = Path(d) / "HERVÉ WORLD" / "Glossaires"
        gl.mkdir(parents=True)
        termes = []
        for i, (en, fr) in enumerate((("Rest", "Repos"), ("Draw", "Piocher")), start=1):
            x = {c: "" for c in M.COLONNES}
            x.update({"ID": f"T-{i:04d}", "EN": en, "FR": fr, "CATÉGORIE": "MÉCANIQUE", "GENRE": "—",
                      "STATUT": "Brouillon", "DATE": "2026-01-01"})
            termes.append(x)
        ch0 = [{"DATE": "2026-01-01", "VERSION": "1.0", "ID": "—", "EN": "—", "CHAMP": "création", "AVANT": "",
                "APRÈS": "", "RAISON": "auto-test", "DÉCIDÉ PAR": "auto-test"}]
        rels = ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship '
                'Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" '
                'Target="../comments{n}.xml"/></Relationships>')
        com = ('<comments xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><authors><author>H</author>'
               '</authors><commentList><comment ref="{ref}" authorId="0"><text><r><t>{txt}</t></r></text></comment>'
               '</commentList></comments>')
        # (a) une colonne ajoutée à la main dans CHANGELOG : refus, fichier intact
        a_ = gl / "Glossaire_A.xlsx"
        M.ecrire_glossaire(a_, "A", termes, ch0)
        def colonne_en_plus(x):   # en-tête J1 « MA NOTE » et sa valeur J2, en fin de ligne, dans CHANGELOG
            for n, v in ((1, "MA NOTE"), (2, "à garder")):
                debut = x.index(f'<row r="{n}">')
                fin = x.index("</row>", debut)
                x = x[:fin] + f'<c r="J{n}" t="inlineStr"><is><t>{v}</t></is></c>' + x[fin:]
            return x
        M._retoucher(a_, changer={"xl/worksheets/sheet3.xml": colonne_en_plus})
        octets = a_.read_bytes()
        code, out = lancer("modifier", str(a_), "--id", "T-0001", "--champ", "DÉFINITION MÉCANIQUE=se reposer", "--ecrire")
        verifier(code == 2 and a_.read_bytes() == octets and "MA NOTE" in out,
                 f"colonne ajoutée dans CHANGELOG non refusée (code {code}) : elle aurait disparu à l'écriture")
        # (b) un commentaire Excel sur un terme : repris dans ses NOTES, tracé ; un texte tapé dans Notice : montré
        b_ = gl / "Glossaire_B.xlsx"
        M.ecrire_glossaire(b_, "B", termes, ch0)
        M._retoucher(b_, changer={"xl/worksheets/sheet4.xml": lambda x: x.replace(
            "</sheetData>", '<row r="60"><c r="A60" t="inlineStr"><is><t>Ma note perso</t></is></c></row></sheetData>')},
            ajouter={"xl/worksheets/_rels/sheet2.xml.rels": rels.format(n=1),
                     "xl/comments1.xml": com.format(ref="C2", txt="vérifier avec l'éditeur")})
        code, out = lancer("modifier", str(b_), "--id", "T-0002", "--champ", "DÉFINITION MÉCANIQUE=prendre une carte")
        verifier(code == 0 and "NON GARDÉ" in out and "Ma note perso" in out,
                 "texte tapé dans la Notice non signalé à l'essai")
        code, out = lancer("modifier", str(b_), "--id", "T-0002", "--champ", "DÉFINITION MÉCANIQUE=prendre une carte",
                           "--ecrire")
        lu = M.lire_glossaire(b_)
        notes = {x["ID"]: x["NOTES"] for x in lu["termes"]}
        trace = [l for l in lu["changelog"] if l["CHAMP"] == "NOTES" and "commentaire Excel" in l["RAISON"]]
        verifier(code == 0 and notes.get("T-0001") == "Commentaire Excel (FR) : vérifier avec l'éditeur" and trace,
                 f"commentaire Excel sur un terme perdu à l'écriture (NOTES lues : {notes}, trace : {len(trace)})")
        verifier("NON GARDÉ" in out and "Ma note perso" in out, "texte tapé dans la Notice non signalé à l'écriture")
        # (e) Excel 365 : un commentaire « à thread » sur C2 (et son double de remplacement dans comments) et une
        # note classique sur C3, dans la même feuille : les deux sont repris, aucun n'est perdu
        e_ = gl / "Glossaire_E.xlsx"
        M.ecrire_glossaire(e_, "E", termes, ch0)
        rels_e = ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="../comments3.xml"/>'
                  '<Relationship Id="rId2" Type="http://schemas.microsoft.com/office/2017/10/relationships/threadedComment" Target="../threadedComments/threadedComment1.xml"/>'
                  '</Relationships>')
        com_e = ('<comments xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><authors><author>H</author></authors><commentList>'
                 '<comment ref="C2" authorId="0"><text><r><t>[Threaded comment] Your version of Excel allows you to read this threaded comment</t></r></text></comment>'
                 '<comment ref="C3" authorId="0"><text><r><t>note classique</t></r></text></comment></commentList></comments>')
        fil_e = ('<ThreadedComments xmlns="http://schemas.microsoft.com/office/spreadsheetml/2018/threadedcomments">'
                 '<threadedComment ref="C2" id="{1}"><text>à valider avec l\'éditeur</text></threadedComment></ThreadedComments>')
        M._retoucher(e_, ajouter={"xl/worksheets/_rels/sheet2.xml.rels": rels_e, "xl/comments3.xml": com_e,
                                  "xl/threadedComments/threadedComment1.xml": fil_e})
        code, out = lancer("modifier", str(e_), "--id", "T-0002", "--champ", "DÉFINITION MÉCANIQUE=prendre une carte", "--ecrire")
        notes_e = {x["ID"]: x["NOTES"] for x in M.lire_glossaire(e_)["termes"]}
        verifier(code == 0 and "à valider avec l'éditeur" in notes_e.get("T-0001", "") and "note classique" in notes_e.get("T-0002", "")
                 and "Threaded comment" not in " ".join(notes_e.values()),
                 f"commentaire à thread et note dans la même feuille : une des deux perdue (NOTES : {notes_e})")
        # (g) le glossaire de démonstration rangé par Hervé dans Glossaires/ (nom voisin, hors standard) :
        # importé comme source, sans refus « nom voisin », et jamais modifié
        demo = gl / "Glossaire_Essai2_EN-FR.xlsx"
        _xlsx_simple(demo, {"Démo": [["Terme (EN)", "Terme (FR)"], ["Rest", "Repos"], ["Flee", "Fuite"]]})
        avant_demo = demo.read_bytes()
        code, out = lancer("importer", str(demo), "--gamme", "Essai2", "--sortie", str(gl / "Glossaire_Essai2.xlsx"), "--ecrire")
        verifier(code == 0 and (gl / "Glossaire_Essai2.xlsx").exists() and demo.read_bytes() == avant_demo,
                 f"démo rangée dans Glossaires/ : import refusé ou démo modifiée (code {code}) — {out[-200:]}")
        # (f) un glossaire demandé dans le dossier du plugin (commande lancée depuis le dossier du skill, chemin
        # relatif) : refus, rien n'est écrit là où il se perdrait à la synchronisation
        dans_plugin = Path(__file__).resolve().parent / "Glossaires" / "Glossaire_Essai.xlsx"
        code, out = lancer("creer", "--gamme", "Essai", "--sortie", str(dans_plugin), "--ecrire")
        verifier(code == 2 and "REFUS" in out and not dans_plugin.exists() and not dans_plugin.parent.exists(),
                 f"glossaire écrit dans le dossier du plugin (code {code}) : il s'y perdrait")
        # (d) un classeur jamais retouché : rien à signaler (0 fausse alerte), même quand le produit change
        p_ = gl / "Glossaire_P.xlsx"
        M.ecrire_glossaire(p_, "P", termes, ch0)
        code, out = lancer("modifier", str(p_), "--id", "T-0001", "--champ", "PUBLIÉ DANS=Boîte de base")
        verifier(code == 0 and "NON GARDÉ" not in out, "fausse alerte « NON GARDÉ » sur un classeur jamais retouché")
        # (c) un commentaire sur la Notice : nulle part où le reprendre → refus, fichier intact
        c_ = gl / "Glossaire_C.xlsx"
        M.ecrire_glossaire(c_, "C", termes, ch0)
        M._retoucher(c_, ajouter={"xl/worksheets/_rels/sheet4.xml.rels": rels.format(n=2),
                                  "xl/comments2.xml": com.format(ref="A1", txt="à relire")})
        octets = c_.read_bytes()
        code, out = lancer("modifier", str(c_), "--id", "T-0001", "--champ", "DÉFINITION MÉCANIQUE=se reposer", "--ecrire")
        verifier(code == 2 and c_.read_bytes() == octets and "Notice!A1" in out,
                 f"commentaire Excel sur la Notice non refusé (code {code}) : il aurait disparu à l'écriture")
    if echecs:
        print("AUTO-TEST ÉCHEC : " + " ; ".join(echecs))
        return 1
    print("AUTO-TEST OK — import en Brouillon, essai sans écriture, 5 refus, validation, CHANGELOG, sauvegarde, verrou ; "
          "migration v2.0 : 6 onglets, statuts repris, historique repris, ancien fichier intact, feuilles non lues nommées ; "
          "colonne désignée à l'import respectée ou refusée ; colonne ajoutée au CHANGELOG et commentaire hors terme "
          "refusés, commentaire sur un terme repris dans NOTES et tracé, texte tapé dans la Notice signalé, 0 fausse "
          "alerte sur un classeur jamais retouché")
    return 0


def _xlsx_simple(chemin, feuilles):
    """Un .xlsx minimal (texte en ligne) pour les essais — bibliothèque standard seulement."""
    import zipfile
    from xml.sax.saxutils import escape
    noms = list(feuilles)
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/></Types>')
        z.writestr("xl/workbook.xml", '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + "".join(f'<sheet name="{escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(noms, 1)) + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/s{i}.xml"/>' for i in range(1, len(noms) + 1)) + "</Relationships>")
        for i, n in enumerate(noms, 1):
            lignes = "".join(f'<row r="{r}">' + "".join(f'<c r="{chr(65 + c)}{r}" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>'
                                                          for c, v in enumerate(l) if str(v) != "") + "</row>"
                             for r, l in enumerate(feuilles[n], 1))
            z.writestr(f"xl/worksheets/s{i}.xml", f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{lignes}</sheetData></worksheet>')


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
    mg = sp.add_parser("migrer", parents=[commun], help="convertir un glossaire v2.0 (tous ses onglets) au format v3")
    mg.add_argument("source")
    mg.add_argument("--gamme", required=True)
    mg.add_argument("--sortie")
    mg.set_defaults(garder_seuls=False, provenance=None, feuille=None, colonne=None)
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
        return {"creer": cmd_creer, "importer": cmd_importer, "migrer": cmd_migrer, "modifier": cmd_modifier, "exporter": cmd_exporter,
                "retours": cmd_retours, "comparer": cmd_comparer, "sauvegarder": cmd_sauvegarder}[a.cmd](a)
    except (FileExistsError, PermissionError, ValueError, FileNotFoundError) as e:
        dire(f"Refus : {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
