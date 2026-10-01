#!/usr/bin/env python3
"""Contrôle des renvois internes et des numéros de règle d'un texte (traduction, et sa VO si fournie).

Usage :
  python3 renvois.py TEXTE_FR [--source TEXTE_EN] [--regles LIVRET_FR]
  python3 renvois.py --auto-test    (essai sur une copie sabotée : doit trouver les 6 fautes glissées)

  --source  la VO : compare les règles et le nombre de renvois de chaque côté.
  --regles  un autre fichier qui contient les règles visées (ex. : les cartes renvoient au livret).

Formats lus : .docx .xlsx .csv .tsv .txt .md (par lecture.py, copie identique dans ce dossier).

Ce que le script relève, avec le repère de chaque segment (§12 = 12e paragraphe Word,
L5 = 5e ligne, Cartes!L5C3 = cellule) :
  1. les règles numérotées : un segment qui COMMENCE par un numéro à plusieurs niveaux
     (« 5.2 Déplacement », « Règle 5.2 », « § 5.2 », « Rule 5.2 ») ;
  2. les renvois : un numéro à plusieurs niveaux précédé de près par « voir », « cf. », « règle »,
     « section », « paragraphe », « § » (« see », « rule », « section » en anglais), ou écrit entre
     parenthèses « (5.2) » ;
  3. ANOMALIES : renvoi vers une règle absente ; numéro défini deux fois ; trou dans une suite
     (5.1, 5.2, 5.4) ; numéro écrit avec une virgule (« règle 5,2 ») ;
  4. renvois de PAGE (« page 12 », « p. 12 ») : à confirmer sur l'épreuve mise en page, jamais sur Word ;
  5. avec --source : règles de la VO absentes de la traduction, et renvois en nombre différent.

Ce que le script NE fait PAS : juger le contenu (que la règle 5.2 parle bien de ce que le renvoi
promet se vérifie en lisant), ni voir une numérotation AUTOMATIQUE de Word (listes numérotées) : ces
numéros ne sont pas dans le texte. Dans ce cas il le dit et compare aux règles de --regles ou de la VO.

Codes de sortie : 0 = aucune anomalie ; 1 = anomalies à voir, ou contrôle incomplet ; 2 = fichier illisible.
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

NUM = r"\d{1,3}(?:\.\d{1,3})+[a-z]?"
NUM_VIRGULE = r"\d{1,3},\d{1,3}"
ESP = r"[ \u00a0\u202f\t]"  # espace ordinaire, insécable U+00A0, fine insécable U+202F, tabulation
MOTS = (r"voir|cf\.?|consultez|reportez-vous|se reporter|r[èe]gles?|sections?|paragraphes?|"
        r"see|refer(?:\s+to)?|rules?")
CLE = rf"(?:(?<!\w)(?:{MOTS})|§)"

DEFINITION = re.compile(
    rf"^{ESP}*(?:(?:r[èe]gle|rule|section|paragraphe|§){ESP}*)?({NUM})\.?(?:{ESP}|[—–:-]|$)", re.IGNORECASE)
# Mot-clé, puis au plus 25 caractères sans ponctuation forte, puis le numéro (« voir la règle 5.2 »).
RENVOI_MOT = re.compile(rf"{CLE}(?P<entre>[^.;:!?\n]{{0,25}}?)(?P<num>{NUM})(?!\d)", re.IGNORECASE)
RENVOI_PAREN = re.compile(rf"\({ESP}*(?P<num>{NUM}){ESP}*\)")
# « règles 5.2 et 5.3 » : le 2e numéro suit le 1er sans mot-clé.
SUITE = re.compile(rf"(?P<num>{NUM}){ESP}*(?:et|ou|and|or|,|à|to){ESP}*(?P<num2>{NUM})(?!\d)")
VIRGULE = re.compile(rf"{CLE}{ESP}*(?P<num>{NUM_VIRGULE})(?!\d)", re.IGNORECASE)
PAGE = re.compile(rf"(?<!\w)(?:pages?|pg\.|p\.){ESP}*(?P<num>\d{{1,3}})(?!\d)", re.IGNORECASE)
MARQUEUR_PAGE = re.compile(r"\[PAGE À CONFIRMER[^\]]*\]", re.IGNORECASE)


def extrait(texte, span, large=35):
    a, b = max(0, span[0] - large), min(len(texte), span[1] + large)
    return ("…" if a else "") + texte[a:b].replace("\n", " ") + ("…" if b < len(texte) else "")


def analyser(chemin):
    segments = lecture.textes(chemin)
    definitions = defaultdict(list)   # numéro -> [repères]
    renvois = []                      # (repère, numéro, extrait)
    virgules = []                     # (repère, texte trouvé)
    pages = []                        # (repère, numéro, marqueur [PAGE À CONFIRMER] présent ?)
    for repere, texte in segments:
        m = DEFINITION.match(texte)
        span_def = m.span(1) if m else None
        if m:
            definitions[m.group(1)].append(repere)
        vus = set()
        for rx in (RENVOI_MOT, RENVOI_PAREN):
            for r in rx.finditer(texte):
                span = r.span("num")
                if span == span_def or span in vus:
                    continue
                vus.add(span)
                renvois.append((repere, r.group("num"), extrait(texte, span)))
        for r in SUITE.finditer(texte):
            if r.span("num") in vus and r.span("num2") not in vus:
                vus.add(r.span("num2"))
                renvois.append((repere, r.group("num2"), extrait(texte, r.span("num2"))))
        virgules += [(repere, r.group(0).strip()) for r in VIRGULE.finditer(texte)]
        marque = bool(MARQUEUR_PAGE.search(texte))
        pages += [(repere, r.group("num"), marque) for r in PAGE.finditer(texte)]
    return segments, definitions, renvois, virgules, pages


def cle_tri(num):
    return [(0, int(p)) if p.isdigit() else (1, p) for p in re.findall(r"\d+|[a-z]", num)]


def trous(definitions):
    """Suites interrompues : 5.1, 5.2, 5.4 -> 5.3 manque (dernier niveau numérique seulement)."""
    par_parent = defaultdict(set)
    for n in definitions:
        parent, _, dernier = n.rpartition(".")
        if dernier.isdigit():
            par_parent[parent].add(int(dernier))
    manques = [f"{p}.{i}" for p, vus in par_parent.items() if len(vus) > 1
               for i in range(min(vus), max(vus)) if i not in vus]
    return sorted(manques, key=cle_tri)


def controler(res, src=None, ext=None):
    """Toutes les vérifications, sans rien afficher : (rubriques, avertissements, incomplet)."""
    _, defs, renv, virg, pages = res
    rubriques, avertissements, incomplet = [], [], False
    trie = lambda d: sorted(d.items(), key=lambda kv: cle_tri(kv[0]))  # noqa: E731

    # Les règles qui existent : celles du texte, plus celles de --regles.
    reference = set(defs) | (set(ext[1]) if ext else set())
    if not reference:
        avertissements.append("Aucune règle numérotée trouvée : soit le texte n'a pas de numéros, soit Word les génère "
                              "par numérotation automatique (invisible pour le script).")
        if src and src[1]:
            avertissements.append("Les renvois sont comparés aux règles de la VO (la structure est en général la même).")
            reference = set(src[1])
        else:
            avertissements.append("L'existence des règles visées n'est PAS vérifiée : à contrôler en lisant, "
                                  "ou relancer avec --regles.")
            reference = None
            incomplet = bool(renv)

    if reference is not None:
        rubriques.append(("Renvoi vers une règle introuvable",
                          [f"{r} : « {n} » — {x}" for r, n, x in renv if n not in reference]))
    rubriques.append(("Numéro de règle défini plusieurs fois",
                      [f"{n} : {', '.join(rs)}" for n, rs in trie(defs) if len(rs) > 1]))
    rubriques.append(("Trou dans la numérotation (règle manquante ou numéro glissé ?)",
                      [f"{n} absent entre ses voisins" for n in trous(defs)]))
    rubriques.append(("Numéro écrit avec une virgule (le livret utilise-t-il le point ?)",
                      [f"{r} : « {x} »" for r, x in virg]))
    if src:
        _, sdefs, srenv, _, spages = src
        if defs:
            rubriques.append(("Règle présente dans la VO, absente de la traduction",
                              [f"{n} (VO : {', '.join(rs)})" for n, rs in trie(sdefs) if n not in defs]))
            rubriques.append(("Règle présente dans la traduction, absente de la VO",
                              [f"{n} ({', '.join(rs)})" for n, rs in trie(defs) if n not in sdefs]))
        c_fr, c_en = Counter(n for _, n, _ in renv), Counter(n for _, n, _ in srenv)
        rubriques.append(("Renvois en nombre différent entre la VO et la traduction",
                          [f"vers {n} : VO {c_en[n]} · traduction {c_fr[n]}"
                           for n in sorted(set(c_fr) | set(c_en), key=cle_tri) if c_fr[n] != c_en[n]]))
        if len(pages) != len(spages):
            rubriques.append(("Renvois de page en nombre différent", [f"VO {len(spages)} · traduction {len(pages)}"]))
    return [(titre, lignes) for titre, lignes in rubriques if lignes], avertissements, incomplet


def auto_test():
    """Copie sabotée : un livret et sa VO où des fautes connues ont été glissées exprès."""
    import tempfile
    fr = ["1.1 Mise en place", "Prenez 3 jetons (voir 5.1).", "5.1 Déplacement", "Voir la règle 8.2.",
          "5.2 Combat", "Voir la règle 5,2, page 14.", "5.4 Terrain", "6.1 Fin de manche", "6.1 Fin de partie"]
    en = ["1.1 Setup", "Take 3 tokens (see 5.1).", "5.1 Movement", "See rule 5.3.", "5.2 Combat",
          "See rule 5.2, page 14.", "5.3 Wounds", "5.4 Terrain", "6.1 End of round", "6.2 End of game", "7.3 Ties"]
    attendus = {
        "Renvoi vers une règle introuvable": "8.2",
        "Numéro de règle défini plusieurs fois": "6.1",
        "Trou dans la numérotation (règle manquante ou numéro glissé ?)": "5.3",
        "Numéro écrit avec une virgule (le livret utilise-t-il le point ?)": "5,2",
        "Règle présente dans la VO, absente de la traduction": "7.3",
    }
    with tempfile.TemporaryDirectory() as d:
        f_fr, f_en = Path(d) / "fr.txt", Path(d) / "en.txt"
        f_fr.write_text("\n".join(fr), encoding="utf-8")
        f_en.write_text("\n".join(en), encoding="utf-8")
        res, src = analyser(f_fr), analyser(f_en)
        trouvees = dict(controler(res, src)[0])
        pages = res[4]
    ok = True
    for titre, cle in attendus.items():
        vu = any(cle in l for l in trouvees.get(titre, []))
        print(f"  {titre} — {cle} : {'trouvé' if vu else 'NON TROUVÉ'}")
        ok &= vu
    vu = any(n == "14" and not m for _, n, m in pages)
    print(f"  Renvoi de page sans marqueur — page 14 : {'trouvé' if vu else 'NON TROUVÉ'}")
    ok &= vu
    print("AUTO-TEST " + ("OK — les 6 fautes glissées sont trouvées." if ok else "ÉCHOUÉ : ne pas se fier à ce contrôle."))
    sys.exit(0 if ok else 1)


def main():
    if "--auto-test" in sys.argv:
        auto_test()
    ap = argparse.ArgumentParser(description="Renvois internes et numéros de règle.")
    ap.add_argument("texte", help="la traduction (.docx .xlsx .csv .tsv .txt .md)")
    ap.add_argument("--source", help="la VO, pour comparer les règles et les renvois")
    ap.add_argument("--regles", help="fichier qui contient les règles visées (ex. : le livret, pour un fichier de cartes)")
    ap.add_argument("--max", type=int, default=40, help="nombre maximal de lignes affichées par rubrique")
    a = ap.parse_args()

    try:
        res = analyser(a.texte)
        src = analyser(a.source) if a.source else None
        ext = analyser(a.regles) if a.regles else None
    except Exception as e:  # fichier absent, zip abîmé, format non pris en charge
        print(f"Fichier illisible : {e}")
        sys.exit(2)
    seg, defs, renv, _, pages = res

    print(f"RENVOIS ET NUMÉROS DE RÈGLE — {Path(a.texte).name}")
    print(f"Segments lus : {len(seg)} · règles numérotées trouvées : {len(defs)} · "
          f"renvois : {len(renv)} · renvois de page : {len(pages)}")
    if src:
        print(f"VO {Path(a.source).name} : règles numérotées {len(src[1])} · renvois {len(src[2])} · "
              f"renvois de page {len(src[4])}")
    if ext:
        print(f"Règles lues dans {Path(a.regles).name} : {len(ext[1])}")
    print()

    rubriques, avertissements, incomplet = controler(res, src, ext)
    for i, av in enumerate(avertissements):
        print(("! " if i == 0 else "  ") + av)
    if avertissements:
        print()
    anomalies = 0
    for titre, lignes in rubriques:
        anomalies += len(lignes)
        print(f"{titre} ({len(lignes)})")
        for l in lignes[: a.max]:
            print("  " + l)
        if len(lignes) > a.max:
            print(f"  … et {len(lignes) - a.max} de plus (--max pour tout afficher)")
        print()

    if pages:
        sans = sum(1 for p in pages if not p[2])
        print(f"Renvois de page à confirmer sur l'épreuve mise en page : {len(pages)} "
              f"(dont {sans} sans le marqueur [PAGE À CONFIRMER])")
        for r, n, m in pages[: a.max]:
            print(f"  {r} : page {n}" + ("" if m else " — marqueur absent"))
        print()

    if renv:
        print(f"Renvois trouvés ({len(renv)}) — leur CONTENU reste à vérifier en lisant :")
        for r, n, x in renv[: a.max]:
            print(f"  {r} → {n} : {x}")
        if len(renv) > a.max:
            print(f"  … et {len(renv) - a.max} de plus (--max pour tout afficher)")
        print()

    print(f"BILAN : {anomalies} anomalie(s) de renvoi ou de numérotation."
          + (" CONTRÔLE INCOMPLET : l'existence des règles visées n'a pas été vérifiée." if incomplet else ""))
    sys.exit(1 if anomalies or incomplet else 0)


if __name__ == "__main__":
    main()
