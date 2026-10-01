#!/usr/bin/env python3
"""Compare deux versions d'un texte source (erratum, règles révisées, fichier de cartes mis à jour)
et sort les passages modifiés, ajoutés, supprimés ou déplacés : on ne retraduit que ceux-là.

Bibliothèque standard uniquement. Les fichiers sont lus par lecture.py (copie identique, même dossier).
Formats : .docx .xlsx .csv .tsv .txt .md

Deux modes :
  - par passage (défaut) : paragraphes Word, lignes de texte, cellules dans l'ordre du fichier ;
  - par identifiant (--cle) : fichiers de cartes .xlsx/.csv, une ligne par carte, comparées par leur
    identifiant (une carte insérée ne décale pas tout le reste).

Exemples :
  python3 comparer_versions.py regles_v1.0.docx regles_v1.1.docx --sortie comparaison.md
  python3 comparer_versions.py cartes_v1.xlsx cartes_v2.xlsx --cle ID --colonnes "Title,Text"
  python3 comparer_versions.py ancien.docx nouveau.docx --memoire Segments_Gamme.csv
  python3 comparer_versions.py ancien.docx nouveau.docx --controle-a-vide
  python3 comparer_versions.py --auto-test

--auto-test : compare deux versions fabriquées dans le programme (passages, puis cartes par
identifiant) où des changements connus ont été glissés exprès ; il doit tous les trouver, et ne
rien signaler pour un simple écart d'espaces.

Codes de sortie : 0 comparaison faite (avec ou sans différence) ; 1 contrôle à vide ou auto-test en
échec ; 2 erreur d'usage ou fichier illisible.
"""
import argparse
import difflib
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402
from commun import (normaliser, raccourcir, diff_mots, ressemblance, empreinte, colonne,  # noqa: E402
                    lire_table, charger_memoire, decrire_traductions)

AFFICHAGE_MAX = 30000  # au-delà, l'affichage est tronqué ; les comptes restent faits sur tout le fichier


def traduction_existante(memo, texte):
    entrees = memo.get(normaliser(texte)) if memo else None
    return decrire_traductions(entrees) if entrees else None


# ------------------------------------------------------------------ mode par passage
def apparier(A, B, idx_a, idx_b, seuil):
    """Dans un bloc remplacé, associe chaque nouveau passage à l'ancien le plus proche (≥ seuil)."""
    paires, libres = [], list(idx_a)
    fenetre = None if len(idx_a) * len(idx_b) <= 250000 else 30
    for k, j in enumerate(idx_b):
        candidats = libres
        if fenetre is not None:
            centre = idx_a[0] + int(k * len(idx_a) / max(1, len(idx_b)))
            candidats = [i for i in libres if abs(i - centre) <= fenetre]
        meilleur = None
        for i in candidats:
            r = ressemblance(A[i], B[j], seuil)
            if r >= seuil and (meilleur is None or r > meilleur[1]):
                meilleur = (i, r)
        if meilleur:
            paires.append((meilleur[0], j, meilleur[1]))
            libres.remove(meilleur[0])
    pris_b = {j for _, j, _ in paires}
    return paires, libres, [j for j in idx_b if j not in pris_b]


def comparer_passages(ua, ub, strict, seuil):
    """ua, ub : listes de (repère, texte). Renvoie un dict de résultats."""
    A = [normaliser(t, strict) for _, t in ua]
    B = [normaliser(t, strict) for _, t in ub]
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    modifies, ajoutes, supprimes, identiques = [], [], [], 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            identiques += i2 - i1
        elif op == "delete":
            supprimes += list(range(i1, i2))
        elif op == "insert":
            ajoutes += list(range(j1, j2))
        else:
            paires, restes_a, restes_b = apparier(A, B, list(range(i1, i2)), list(range(j1, j2)), seuil)
            modifies += paires
            supprimes += restes_a
            ajoutes += restes_b
    # un passage supprimé ici et ajouté là, au texte identique, est seulement déplacé
    stock = Counter(A[i] for i in supprimes)
    deplaces, vrais_ajouts = [], []
    for j in ajoutes:
        if stock[B[j]] > 0:
            stock[B[j]] -= 1
            deplaces.append(j)
        else:
            vrais_ajouts.append(j)
    textes_deplaces = Counter(B[j] for j in deplaces)
    vrais_supprimes = []
    for i in supprimes:
        if textes_deplaces[A[i]] > 0:
            textes_deplaces[A[i]] -= 1
        else:
            vrais_supprimes.append(i)
    # seconde passe : un passage modifié ET déplacé tombe dans deux blocs différents ; on le rapparie
    paires, vrais_supprimes, vrais_ajouts = apparier(A, B, sorted(vrais_supprimes), sorted(vrais_ajouts), seuil)
    modifies += paires
    return {
        "modifies": sorted(modifies, key=lambda p: p[1]),
        "ajoutes": sorted(vrais_ajouts),
        "supprimes": sorted(vrais_supprimes),
        "deplaces": sorted(deplaces),
        "identiques": identiques,
        "n_a": len(ua), "n_b": len(ub),
    }


def rapport_passages(res, ua, ub, memo):
    L = []
    for n, (i, j, r) in enumerate(res["modifies"], 1):
        (ra, ta), (rb, tb) = ua[i], ub[j]
        L.append(f"### M{n}. ancien {ra} → nouveau {rb} (ressemblance {r:.0%})")
        L.append(f"- Avant : {ta}")
        L.append(f"- Après : {tb}")
        L.append(f"- Ce qui change : {diff_mots(ta, tb)}")
        ex = traduction_existante(memo, ta) if memo else None
        if ex:
            L.append(f"- Traduction existante de l'ancien passage : {ex}")
        L.append("")
    sections = [("## Passages modifiés", L)]
    L2 = []
    for n, j in enumerate(res["ajoutes"], 1):
        L2.append(f"- A{n}. nouveau {ub[j][0]} : {ub[j][1]}")
    sections.append(("## Passages ajoutés", L2))
    L3 = []
    for n, i in enumerate(res["supprimes"], 1):
        ligne = f"- S{n}. ancien {ua[i][0]} : {ua[i][1]}"
        ex = traduction_existante(memo, ua[i][1]) if memo else None
        if ex:
            ligne += f"\n  - Traduction existante à retirer de la VF : {ex}"
        L3.append(ligne)
    sections.append(("## Passages supprimés", L3))
    L4 = [f"- D{n}. nouveau {ub[j][0]} : {raccourcir(ub[j][1], 60)}" for n, j in enumerate(res["deplaces"], 1)]
    sections.append(("## Passages déplacés (texte identique : rien à retraduire, vérifier l'ordre en VF)", L4))
    return sections


# ------------------------------------------------------------------ mode par identifiant
def indexer(tete, corps, i_cle, nom):
    """Lignes indexées par identifiant. Une ligne sans identifiant (titre de section, ligne vide)
    n'est pas une carte : elle est comptée à part, jamais comparée."""
    index, doublons, sans_id = {}, [], 0
    for k, l in corps:
        cle = l[i_cle].strip() if i_cle < len(l) else ""
        if not cle:
            sans_id += 1
            continue
        if cle in index:
            doublons.append(cle)
            cle = f"{cle} (doublon ligne {k})"
        index[cle] = (k, l)
    return index, doublons, sans_id


def comparer_tables(ta, ca, tb, cb, spec_cle, spec_cols, strict):
    i_cle_a, i_cle_b = colonne(ta, spec_cle), colonne(tb, spec_cle)
    if spec_cols:
        noms = [c.strip() for c in spec_cols.split(",") if c.strip()]
    else:
        noms = [e for k, e in enumerate(ta) if e and k != i_cle_a and e.lower() in [x.lower() for x in tb]]
    cols = [(nom, colonne(ta, nom), colonne(tb, nom)) for nom in noms]
    ia, dbl_a, sans_a = indexer(ta, ca, i_cle_a, "ancien")
    ib, dbl_b, sans_b = indexer(tb, cb, i_cle_b, "nouveau")

    def val(l, i):
        return l[i] if i < len(l) else ""

    modifiees, ajoutees, supprimees, identiques = [], [], [], 0
    for cle, (kb, lb) in ib.items():
        if cle not in ia:
            ajoutees.append((cle, kb, {nom: val(lb, jb) for nom, _, jb in cols}))
            continue
        ka, la = ia[cle]
        ecarts = {nom: (val(la, iac), val(lb, jb)) for nom, iac, jb in cols
                  if normaliser(val(la, iac), strict) != normaliser(val(lb, jb), strict)}
        if ecarts:
            modifiees.append((cle, ka, kb, ecarts))
        else:
            identiques += 1
    for cle, (ka, la) in ia.items():
        if cle not in ib:
            supprimees.append((cle, ka, {nom: val(la, iac) for nom, iac, _ in cols}))
    seulement_a = [e for e in ta if e and e.lower() not in [x.lower() for x in tb]]
    seulement_b = [e for e in tb if e and e.lower() not in [x.lower() for x in ta]]
    return {"modifiees": modifiees, "ajoutees": ajoutees, "supprimees": supprimees,
            "identiques": identiques, "colonnes": [c[0] for c in cols],
            "doublons": (dbl_a, dbl_b), "colonnes_seules": (seulement_a, seulement_b),
            "sans_id": (sans_a, sans_b),
            "n_a": len(ia), "n_b": len(ib)}


def rapport_tables(res, memo):
    L = []
    for n, (cle, ka, kb, ecarts) in enumerate(res["modifiees"], 1):
        L.append(f"### M{n}. {cle} (ancienne ligne {ka}, nouvelle ligne {kb})")
        for nom, (a, b) in ecarts.items():
            L.append(f"- {nom} — avant : {a}")
            L.append(f"- {nom} — après : {b}")
            L.append(f"- {nom} — ce qui change : {diff_mots(a, b)}")
            ex = traduction_existante(memo, a) if memo else None
            if ex:
                L.append(f"- {nom} — traduction existante de l'ancien texte : {ex}")
        L.append("")
    L2 = []
    for n, (cle, kb, vals) in enumerate(res["ajoutees"], 1):
        L2.append(f"- A{n}. {cle} (ligne {kb}) : " + " | ".join(f"{k} : {v}" for k, v in vals.items() if v.strip()))
    L3 = []
    for n, (cle, ka, vals) in enumerate(res["supprimees"], 1):
        L3.append(f"- S{n}. {cle} (ancienne ligne {ka}) : " + " | ".join(f"{k} : {v}" for k, v in vals.items() if v.strip()))
    return [("## Cartes ou lignes modifiées", L), ("## Cartes ou lignes ajoutées", L2),
            ("## Cartes ou lignes supprimées", L3)]


# ------------------------------------------------------------------ contrôle à vide
def controle_a_vide(args):
    """Le comparateur doit VOIR une modification glissée exprès, sinon on ne le croit pas."""
    if args.cle:
        ta, ca = lire_table(args.ancien, args.feuille, [args.cle])
        if not ca:
            print("CONTRÔLE À VIDE : ÉCHEC — aucune ligne de données dans l'ancien fichier.")
            return 1
        res0 = comparer_tables(ta, ca, ta, ca, args.cle, args.colonnes, args.strict)
        if not res0["colonnes"]:
            print("CONTRÔLE À VIDE : ÉCHEC — aucune colonne comparée (vérifie --colonnes).")
            return 1
        i_col, i_cle = colonne(ta, res0["colonnes"][0]), colonne(ta, args.cle)
        sabote = [(k, list(l)) for k, l in ca]
        portant_id = [l for _, l in sabote if i_cle < len(l) and l[i_cle].strip()]
        if not portant_id:
            print("CONTRÔLE À VIDE : ÉCHEC — aucune ligne ne porte d'identifiant dans la colonne-clé.")
            return 1
        l0 = portant_id[0]  # une ligne de section (sans identifiant) n'est jamais comparée : on sabote une vraie carte
        while len(l0) <= i_col:
            l0.append("")
        l0[i_col] = l0[i_col] + " [CONTRÔLE]"
        res = comparer_tables(ta, ca, ta, sabote, args.cle, args.colonnes, args.strict)
        ok = len(res["modifiees"]) == 1 and not res["ajoutees"] and not res["supprimees"]
        trouve = f"modifiées : {len(res['modifiees'])}, ajoutées : {len(res['ajoutees'])}, supprimées : {len(res['supprimees'])}"
    else:
        ua = lecture.textes(args.ancien)
        if len(ua) < 2:
            print("CONTRÔLE À VIDE : ÉCHEC — moins de 2 passages lus dans l'ancien fichier.")
            return 1
        cible = max(range(len(ua)), key=lambda i: len(ua[i][1]))
        sabote = list(ua)
        sabote[cible] = (ua[cible][0], ua[cible][1] + " [CONTRÔLE]")
        sabote.insert(1, ("(inséré)", "Passage inséré pour le contrôle à vide, absent de la source."))
        res = comparer_passages(ua, sabote, args.strict, args.seuil)
        ok = len(res["modifies"]) == 1 and len(res["ajoutes"]) == 1 and not res["supprimes"]
        trouve = f"modifiés : {len(res['modifies'])}, ajoutés : {len(res['ajoutes'])}, supprimés : {len(res['supprimes'])}"
    attendu = ("modifiées : 1, ajoutées : 0, supprimées : 0" if args.cle
               else "modifiés : 1, ajoutés : 1, supprimés : 0")
    print(f"CONTRÔLE À VIDE : {'OK' if ok else 'ÉCHEC'} — attendu ({attendu}) ; trouvé ({trouve}).")
    return 0 if ok else 1


# ------------------------------------------------------------------ auto-test
def auto_test():
    """Deux versions fabriquées ici, avec des changements connus glissés exprès.

    Le comparateur doit voir chacun d'eux, et rien d'autre : un écart d'espaces (double espace,
    espace insécable) n'est pas une modification du texte. Les valeurs attendues sont écrites à la
    main, jamais recalculées par le programme qu'on vérifie."""
    import tempfile
    nb = " "
    # -- mode par passage, lu depuis de vrais fichiers .txt (le chemin de lecture est vérifié aussi)
    ancien = ["1. Mise en place", "Each player takes 3 tokens.", "Shuffle the deck.", "Move up to 2 spaces.",
              "Draw 1 card.", "Combat is resolved with dice.", "Optional rule: play with 5 players."]
    nouveau = ["1. Mise en place", f"Each player  takes{nb}3 tokens.",   # espaces seulement : identique
               "Move up to 3 spaces.",                                    # modifié (2 → 3)
               "Draw 1 card.", "Combat is resolved with dice.",
               "Ties are broken by initiative order.",                    # ajouté
               "Shuffle the deck."]                                       # déplacé à la fin
    # « Optional rule… » est supprimé.
    with tempfile.TemporaryDirectory() as d:
        fa, fb = Path(d) / "regles_v1.txt", Path(d) / "regles_v2.txt"
        fa.write_text("\n".join(ancien) + "\n", encoding="utf-8")
        fb.write_text("\n".join(nouveau) + "\n", encoding="utf-8")
        ua, ub = lecture.textes(fa), lecture.textes(fb)
    res = comparer_passages(ua, ub, False, 0.5)
    vus = {
        "modifiés": [(ua[i][1], ub[j][1]) for i, j, _ in res["modifies"]],
        "ajoutés": [ub[j][1] for j in res["ajoutes"]],
        "supprimés": [ua[i][1] for i in res["supprimes"]],
        "déplacés": [ub[j][1] for j in res["deplaces"]],
    }
    attendus = {
        "modifiés": [("Move up to 2 spaces.", "Move up to 3 spaces.")],
        "ajoutés": ["Ties are broken by initiative order."],
        "supprimés": ["Optional rule: play with 5 players."],
        "déplacés": ["Shuffle the deck."],
    }
    echecs = [f"passages {k} : attendu {attendus[k]}, vu {vus[k]}" for k in attendus if vus[k] != attendus[k]]
    if res["identiques"] != 4:   # mise en place, tokens (espaces seulement), draw, combat
        echecs.append(f"passages identiques : attendu 4, vu {res['identiques']} (un écart d'espaces compté comme modification ?)")
    diff = diff_mots("Move up to 2 spaces.", "Move up to 3 spaces.")
    if diff != "Move up to [-2-]{+3+} spaces.":
        echecs.append(f"marques mot à mot : vu « {diff} »")
    # -- mode par identifiant (une ligne de section sans identifiant ne doit jamais être comparée)
    tete = ["ID", "Title", "Text"]
    ca = [(2, ["", "— Faction du Nord —", ""]), (3, ["C001", "Guard", "Block 2 damage."]),
          (4, ["C002", "Thief", "Steal 1 gold."]), (5, ["C003", "Mage", "Deal 3 damage."])]
    cb = [(2, ["", "— Faction du Nord (révisée) —", ""]), (3, ["C001", "Guard", "Block 3 damage."]),
          (4, ["C002", "Thief", f"Steal{nb}1  gold."]), (5, ["C004", "Bard", "Heal 1."])]
    rt = comparer_tables(tete, ca, tete, cb, "ID", None, False)
    vus_t = {
        "modifiées": [(c, sorted(e)) for c, _, _, e in rt["modifiees"]],
        "ajoutées": [c for c, _, _ in rt["ajoutees"]],
        "supprimées": [c for c, _, _ in rt["supprimees"]],
        "identiques": rt["identiques"],
        "sans identifiant": rt["sans_id"],
    }
    attendus_t = {
        "modifiées": [("C001", ["Text"])],
        "ajoutées": ["C004"],
        "supprimées": ["C003"],
        "identiques": 1,          # C002 : écart d'espaces seulement
        "sans identifiant": (1, 1),
    }
    echecs += [f"cartes {k} : attendu {attendus_t[k]}, vu {vus_t[k]}" for k in attendus_t if vus_t[k] != attendus_t[k]]
    for k in attendus:
        print(f"  passages {k} : {len(vus[k])} vu(s), {len(attendus[k])} attendu(s)")
    for k in ("modifiées", "ajoutées", "supprimées"):
        print(f"  cartes {k} : {len(vus_t[k])} vue(s), {len(attendus_t[k])} attendue(s)")
    if echecs:
        print("AUTO-TEST ÉCHOUÉ — " + " ; ".join(echecs) + ". Ne pas se fier à ce comparateur.")
        return 1
    print("AUTO-TEST OK — 7 changements glissés exprès (passages : modifié, ajouté, supprimé, déplacé ; "
          "cartes : modifiée, ajoutée, supprimée), tous trouvés ; 0 fausse alerte sur les écarts d'espaces "
          "et la ligne de section")
    return 0


# ------------------------------------------------------------------ programme
def main():
    if "--auto-test" in sys.argv[1:]:
        return auto_test()
    ap = argparse.ArgumentParser(description="Passages modifiés entre deux versions d'un texte source.")
    ap.add_argument("ancien", help="version déjà traduite (.docx .xlsx .csv .tsv .txt .md)")
    ap.add_argument("nouveau", nargs="?", help="nouvelle version (erratum, révision)")
    ap.add_argument("--cle", help="colonne identifiant des cartes (nom d'en-tête, lettre ou numéro) : mode par identifiant")
    ap.add_argument("--colonnes", help="colonnes de texte à comparer, séparées par des virgules (défaut : toutes)")
    ap.add_argument("--feuille", help="onglet à lire dans un .xlsx (défaut : le premier non vide)")
    ap.add_argument("--memoire", nargs="*", help="CSV de mémoire de traduction (EN;FR;produit;date) : affiche la traduction existante")
    ap.add_argument("--seuil", type=float, default=0.5, help="ressemblance minimale pour dire « modifié » plutôt que supprimé + ajouté (défaut 0,5)")
    ap.add_argument("--strict", action="store_true", help="compare le texte brut (sans réduire les espaces)")
    ap.add_argument("--sortie", help="écrit le rapport complet dans ce fichier .md")
    ap.add_argument("--controle-a-vide", action="store_true", help="vérifie que le comparateur voit une modification glissée exprès")
    ap.add_argument("--auto-test", action="store_true",
                    help="essai sur deux versions fabriquées dans le programme (aucun fichier à donner)")
    args = ap.parse_args()

    try:
        if args.controle_a_vide:
            return controle_a_vide(args)
        if not args.nouveau:
            ap.error("il faut deux fichiers : l'ancienne version et la nouvelle")
        memo = charger_memoire(args.memoire)
        identiques_octets = empreinte(args.ancien) == empreinte(args.nouveau)
        tete = [f"# Comparaison de deux versions du texte source — {date.today().isoformat()}", "",
                f"- Ancienne version : {Path(args.ancien).name}",
                f"- Nouvelle version : {Path(args.nouveau).name}"]
        if args.cle:
            ta, ca = lire_table(args.ancien, args.feuille, [args.cle])
            tb, cb = lire_table(args.nouveau, args.feuille, [args.cle])
            res = comparer_tables(ta, ca, tb, cb, args.cle, args.colonnes, args.strict)
            sections = rapport_tables(res, memo)
            a_retraduire = sum(len(b) for _, _, _, e in res["modifiees"] for _, b in e.values()) + \
                sum(len(v) for _, _, vals in res["ajoutees"] for v in vals.values())
            resume = (f"lignes avant : {res['n_a']}, après : {res['n_b']} — modifiées : {len(res['modifiees'])}, "
                      f"ajoutées : {len(res['ajoutees'])}, supprimées : {len(res['supprimees'])}, identiques : {res['identiques']}. "
                      f"Colonnes comparées : {', '.join(res['colonnes']) or 'aucune'}.")
            dbl_a, dbl_b = res["doublons"]
            if dbl_a or dbl_b:
                tete.append(f"- ATTENTION identifiants en double — ancien : {', '.join(dbl_a) or 'aucun'} ; nouveau : {', '.join(dbl_b) or 'aucun'}")
            na, nb = res["sans_id"]
            if na or nb:
                tete.append(f"- Lignes sans identifiant écartées (titres de section, lignes vides) — ancien : {na} ; nouveau : {nb}")
            sa, sb = res["colonnes_seules"]
            if sa or sb:
                tete.append(f"- Colonnes présentes d'un seul côté — ancien seulement : {', '.join(sa) or 'aucune'} ; nouveau seulement : {', '.join(sb) or 'aucune'}")
        else:
            ua, ub = lecture.textes(args.ancien), lecture.textes(args.nouveau)
            res = comparer_passages(ua, ub, args.strict, args.seuil)
            sections = rapport_passages(res, ua, ub, memo)
            a_retraduire = sum(len(ub[j][1]) for _, j, _ in res["modifies"]) + sum(len(ub[j][1]) for j in res["ajoutes"])
            resume = (f"passages avant : {res['n_a']}, après : {res['n_b']} — modifiés : {len(res['modifies'])}, "
                      f"ajoutés : {len(res['ajoutes'])}, supprimés : {len(res['supprimes'])}, "
                      f"déplacés : {len(res['deplaces'])}, identiques : {res['identiques']}.")
    except (OSError, KeyError, ValueError) as e:
        print(f"Lecture impossible : {e}", file=sys.stderr)
        return 2

    tete += ["", f"**Résumé :** {resume}",
             f"**À retraduire :** {a_retraduire} caractères (espaces comprises), comptés sur le texte de la nouvelle version "
             f"des passages modifiés et ajoutés.",
             "Normalisation : " + ("aucune (--strict)." if args.strict else
                                   "espaces multiples et insécables réduites à une espace avant comparaison (--strict pour comparer le brut)."),
             "Marques : [-texte retiré-] {+texte ajouté+}.", ""]
    if identiques_octets:
        tete.append("Les deux fichiers sont identiques octet pour octet : vérifie qu'il s'agit bien de deux versions différentes.\n")
    corps = []
    for titre, lignes in sections:
        corps.append(f"{titre} ({sum(1 for l in lignes if re.match(r'(### M|- [ASD])[0-9]', l))})")
        corps.append("")
        corps += lignes if lignes else ["Aucun."]
        corps.append("")
    rapport = "\n".join(tete + corps)
    print(f"Résumé : {resume}")
    print(f"À retraduire : {a_retraduire} caractères (espaces comprises).")
    if args.sortie:
        Path(args.sortie).write_text(rapport, encoding="utf-8")
        print(f"Rapport complet écrit dans {args.sortie}")
    elif len(rapport) > AFFICHAGE_MAX:
        print(rapport[:AFFICHAGE_MAX])
        print(f"\n[Affichage tronqué à {AFFICHAGE_MAX} caractères sur {len(rapport)} ; les comptes ci-dessus portent "
              f"sur tout le fichier. Relance avec --sortie rapport.md pour lire le rapport entier.]")
    else:
        print(rapport)
    return 0


if __name__ == "__main__":
    sys.exit(main())
