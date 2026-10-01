#!/usr/bin/env python3
"""Fiches d'univers (Obsidian) contre le glossaire de LEUR gamme : le glossaire fait foi.

Une fiche d'univers (personnage, lieu, faction, objet) porte en propriétés `gamme`, `id_glossaire`, `nom_en` et
`nom_fr`. Le nom français n'y est qu'un REFLET du glossaire, comme le nom affiché des liens vers une fiche
(`[[…/Univers/<Gamme>/<fichier>|<nom affiché>]]`). Ce programme ne modifie rien ; il liste ce qui ne suit pas.

  python3 fiches.py verifier --glossaire Glossaires/Glossaire_<Gamme>.xlsx --dossier "Références/Narration/Univers" \
                             [--gamme "<Gamme>"] [--liens-dans Core/Gammes --liens-dans Core/Suivi.md …]
  python3 fiches.py --auto-test

Seules les fiches de la gamme du glossaire sont contrôlées (propriété `gamme`, ou sous-dossier de la gamme) : les
identifiants se répètent d'un glossaire à l'autre. La gamme se lit dans le nom du glossaire (`Glossaire_<Gamme>.xlsx`,
aussi `…_NOUVEAU_AAAA-MM-JJ.xlsx`) ; sinon, `--gamme`. Un dossier introuvable ou sans fiche de la gamme est une
ERREUR (code 2) : « 0 écart » ne se dit qu'après avoir lu des fiches.

Code de sortie : 0 = tout suit le glossaire ; 1 = au moins un point à corriger (ÉCART, À RELIER, REMPLACÉ,
ID INCONNU, DOUBLON, NOM DE FICHIER, LIEN) ; 2 = rien à contrôler (dossier, gamme ou glossaire introuvable).
SANS ID (nom introuvable dans ce glossaire) et PROVISOIRE (terme pas encore Confirmé) sont des informations.
"""
import argparse, re, sys, tempfile, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

INTERDITS = r'[\\/:*?"<>|]'                     # caractères refusés par Windows dans un nom de fichier
LIEN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?\\?\|([^\]]+)\]\]")


def nfc(s):
    return unicodedata.normalize("NFC", str(s)).strip()


def cle(s):
    """Comparaison de noms de gamme : sans accents, espaces, tirets ni casse (« Tainted Grail » = « TaintedGrail »)."""
    s = unicodedata.normalize("NFD", str(s))
    return re.sub(r"[\W_]+", "", "".join(c for c in s if not unicodedata.combining(c))).casefold()


def valeur_yaml(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return re.sub(r'\\(["\\])', r"\1", v[1:-1])
    return re.sub(r"\s+#.*$", "", v)


def proprietes(chemin):
    """Les propriétés de l'en-tête --- … --- d'une note. Une propriété écrite en liste donne la liste de ses valeurs."""
    lignes = lecture._decoder(Path(chemin).read_bytes()).splitlines()
    if not lignes or lignes[0].strip() != "---":
        return {}
    out, cle_liste = {}, None
    for l in lignes[1:]:
        if l.strip() == "---":
            break
        if cle_liste and re.match(r"^\s*-\s", l):
            out[cle_liste].append(nfc(valeur_yaml(l.split("-", 1)[1])))
            continue
        if ":" not in l or l.startswith((" ", "\t")):
            continue
        k, v = l.split(":", 1)
        k = k.strip()
        if v.strip() == "":
            out[k], cle_liste = [], k
        else:
            out[k], cle_liste = nfc(valeur_yaml(v)), None
    return {k: ("" if v == [] else v) for k, v in out.items()}


def glossaire(chemin):
    """{ID: {"EN", "FR", "STATUT"}} lu dans l'onglet Termes (ou le premier onglet qui a ID, EN et FR)."""
    feuilles = lecture.feuilles_xlsx(chemin)
    for nom in sorted(feuilles, key=lambda n: n != "Termes"):
        for i, ligne in enumerate(feuilles[nom][:15]):
            entetes = [nfc(c).upper() for c in ligne]
            if {"ID", "EN", "FR"} <= set(entetes):
                col = {c: entetes.index(c) for c in ("ID", "EN", "FR", "STATUT") if c in entetes}
                termes = {}
                for l in feuilles[nom][i + 1:]:
                    val = lambda c: nfc(l[col[c]]) if c in col and col[c] < len(l) else ""
                    if val("ID"):
                        termes[val("ID")] = {"EN": val("EN"), "FR": val("FR"), "STATUT": val("STATUT")}
                return termes
    raise SystemExit(f"ERREUR — aucun onglet avec les colonnes ID, EN et FR dans {chemin}")


def gamme_du_glossaire(chemin):
    m = re.match(r"^Glossaire_(.+?)(?:_NOUVEAU_\d{4}-\d{2}-\d{2}.*)?$", Path(chemin).stem)
    return m.group(1) if m else None


def noms_de_fichier(nom_en, typ):
    base = re.sub(INTERDITS, "-", nom_en).strip()
    return {cle(base), cle(f"{base} ({typ})")}


def verifier(gl, dossier, gamme=None, liens_dans=()):
    dossier = Path(dossier)
    gamme = gamme or gamme_du_glossaire(gl)
    if not gamme:
        print(f"ERREUR — la gamme ne se lit pas dans le nom « {Path(gl).name} » : précise --gamme")
        return None
    if not dossier.is_dir():
        print(f"ERREUR — dossier introuvable : {dossier}. Le programme voit-il le dossier d'Hervé ? (règle du skill noyau)")
        return None
    termes = glossaire(gl)
    actifs_par_en = {}
    for i, t in termes.items():
        if t["STATUT"] != "Archivé":
            actifs_par_en.setdefault(t["EN"].casefold(), []).append(i)
    toutes = sorted(p for p in dossier.rglob("*.md") if not p.name.upper().startswith(("LISEZ-MOI", "README")))
    fiches, hors = [], 0
    for f in toutes:
        p = proprietes(f)
        sous = f.relative_to(dossier).parts
        if cle(p.get("gamme", "")) == cle(gamme) or (len(sous) > 1 and cle(sous[0]) == cle(gamme)):
            fiches.append((f, p))
        else:
            hors += 1
    if not fiches:
        print(f"ERREUR — aucune fiche de la gamme « {gamme} » sous {dossier} ({hors} fiche(s) d'autres gammes). "
              "Rien n'a été contrôlé.")
        return None
    b = dict(conformes=0, ecarts=0, a_relier=0, remplaces=0, id_inconnus=0, doublons=0, noms_fichier=0, liens=0, sans_id=0)
    lignes, vus = [], {}
    racine = dossier.parents[2] if len(dossier.parents) > 2 else dossier
    for f, p in fiches:
        nom = f.relative_to(dossier).as_posix()
        ident, nom_en, nom_fr, typ = p.get("id_glossaire", ""), p.get("nom_en", ""), p.get("nom_fr", ""), p.get("type", "")
        if isinstance(nom_fr, list) or isinstance(nom_en, list):
            b["ecarts"] += 1
            lignes.append(f"ÉCART        {nom} — nom_fr ou nom_en écrit en liste : une seule valeur attendue")
            continue
        if nom_en and cle(f.stem) not in noms_de_fichier(nom_en, typ):
            b["noms_fichier"] += 1
            lignes.append(f"NOM DE FICHIER {nom} — le fichier doit porter le nom anglais « {nom_en} » (fiche renommée ?)")
        if not ident:
            cand = actifs_par_en.get(nom_en.casefold(), []) if nom_en else []
            if len(cand) == 1:
                b["a_relier"] += 1
                t = termes[cand[0]]
                ecart = f" ; et nom_fr « {nom_fr} » ≠ glossaire « {t['FR']} »" if nom_fr and nom_fr != t["FR"] else ""
                lignes.append(f"À RELIER     {nom} — « {nom_en} » est au glossaire : id_glossaire {cand[0]}, nom_fr « {t['FR']} »{ecart}")
            elif len(cand) > 1:
                b["a_relier"] += 1
                lignes.append(f"À RELIER     {nom} — plusieurs termes actifs pour « {nom_en} » : {', '.join(cand)} (Hervé choisit)")
            else:
                b["sans_id"] += 1
                lignes.append(f"SANS ID      {nom} — « {nom_en or f.stem} » introuvable dans ce glossaire : recherche complète à faire (skill glossaire)")
            continue
        if ident in vus:
            b["doublons"] += 1
            lignes.append(f"DOUBLON      {nom} — même identifiant {ident} que {vus[ident]}")
        vus[ident] = nom
        t = termes.get(ident)
        if t is None:
            b["id_inconnus"] += 1
            lignes.append(f"ID INCONNU   {nom} — {ident} n'existe pas dans le glossaire de « {gamme} »")
            continue
        if t["STATUT"] == "Archivé":
            b["remplaces"] += 1
            rempl = [i for i in actifs_par_en.get(t["EN"].casefold(), [])]
            lignes.append(f"REMPLACÉ     {nom} — {ident} est Archivé au glossaire ; "
                          + (f"terme actif de même anglais : {', '.join(rempl)} ({', '.join(termes[i]['FR'] for i in rempl)})" if rempl
                             else "aucun terme actif de même anglais : demander à Hervé"))
            continue
        fautes = []
        if nom_fr != t["FR"]:
            fautes.append(f"nom_fr « {nom_fr} » ≠ glossaire « {t['FR']} »")
        if nom_en and nom_en != t["EN"]:
            fautes.append(f"nom_en « {nom_en} » ≠ glossaire « {t['EN']} »")
        if fautes:
            b["ecarts"] += 1
            lignes.append(f"ÉCART        {nom} — " + " ; ".join(fautes))
        else:
            b["conformes"] += 1
            if t["STATUT"] and t["STATUT"] not in ("Confirmé", "Gelé"):
                lignes.append(f"PROVISOIRE   {nom} — « {t['FR']} » est encore « {t['STATUT']} » au glossaire")
    # Le nom affiché des liens vers une fiche est lui aussi une copie du nom français
    a_lire = [f for f, _ in fiches]
    for x in liens_dans:
        x = Path(x)
        a_lire += sorted(x.rglob("*.md")) if x.is_dir() else ([x] if x.exists() else [])
    for f in a_lire:
        for cible, affiche in LIEN.findall(lecture._decoder(f.read_bytes())):
            cible = nfc(cible.strip())
            if "Univers/" not in cible:
                continue
            fc = racine / (cible if cible.endswith(".md") else cible + ".md")
            if not fc.exists():
                b["liens"] += 1
                lignes.append(f"LIEN         {f.name} — la fiche visée n'existe pas : {cible}")
                continue
            pc = proprietes(fc)                       # le glossaire fait foi ; la fiche visée seulement à défaut
            t = termes.get(pc.get("id_glossaire", "")) if cle(pc.get("gamme", "")) == cle(gamme) or cle(fc.parent.name) == cle(gamme) else None
            attendu = t["FR"] if t and t["STATUT"] != "Archivé" else pc.get("nom_fr", "")
            if attendu and nfc(affiche) != attendu:
                b["liens"] += 1
                lignes.append(f"LIEN         {f.name} — affiche « {nfc(affiche)} » au lieu de « {attendu} » ({fc.stem})")
    for l in lignes:
        print(l)
    print(f"Gamme « {gamme} » : {len(fiches)} fiche(s) contrôlée(s) ({hors} d'autres gammes laissée(s) de côté) · "
          f"{b['conformes']} conforme(s) · {b['ecarts']} écart(s) · {b['a_relier']} à relier · {b['remplaces']} remplacé(s) · "
          f"{b['id_inconnus']} id inconnu(s) · {b['doublons']} doublon(s) · {b['noms_fichier']} nom(s) de fichier · "
          f"{b['liens']} lien(s) · {b['sans_id']} sans id")
    return b


def a_corriger(b):
    return any(b[k] for k in ("ecarts", "a_relier", "remplaces", "id_inconnus", "doublons", "noms_fichier", "liens"))


def _xlsx(chemin, lignes):
    """Un .xlsx minimal à un onglet « Termes », pour l'auto-test (bibliothèque standard seulement)."""
    import zipfile
    from xml.sax.saxutils import escape
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/></Types>')
        z.writestr("xl/workbook.xml", '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Termes" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/s1.xml"/></Relationships>')
        rangs = "".join(f'<row r="{r}">' + "".join(f'<c r="{chr(65 + c)}{r}" t="inlineStr"><is><t>{escape(v)}</t></is></c>'
                                                   for c, v in enumerate(l) if v) + "</row>" for r, l in enumerate(lignes, 1))
        z.writestr("xl/worksheets/s1.xml", f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{rangs}</sheetData></worksheet>')


def auto_test():
    """[EXEMPLE FICTIF] Deux gammes aux identifiants qui se répètent, chaque cas dans sa case, puis un glossaire saboté."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        gl = d / "Glossaires/Glossaire_RoyaumeFictif.xlsx"
        gl.parent.mkdir()
        tete = ["ID", "EN", "FR", "CATÉGORIE", "GENRE", "STATUT"]
        termes = [tete, ["T-0001", "Grey Warden", "Gardien gris", "PERSONNAGE", "m", "Confirmé"],
                  ["T-0002", "Hollow Keep", "Donjon creux", "LIEU", "m", "Brouillon"],
                  ["T-0003", "Ashen Order", "Ordre des Cendres", "FACTION", "m", "Gelé"],
                  ["T-0004", "Pale Crown", "Couronne pâle", "OBJET", "f", "Archivé"],
                  ["T-0005", "Pale Crown", "Couronne blême", "OBJET", "f", "Confirmé"],
                  ["T-0006", "Iron Maw", "Gueule de fer", "LIEU", "f", "Confirmé"],
                  ["T-0007", "The Order's Oath", "L'Ordre", "LORE", "m", "Confirmé"]]
        _xlsx(gl, termes)
        U = d / "Références/Narration/Univers"

        def fiche(dossier, fichier, corps="", crlf=False, bom=False, **p):
            f = U / dossier / f"{fichier}.md"
            f.parent.mkdir(parents=True, exist_ok=True)
            t = "---\n" + "".join(f"{k}: {v}\n" for k, v in p.items()) + "tags:\n  - univers\n---\n\n" + corps
            if crlf:
                t = t.replace("\n", "\r\n")
            f.write_bytes((b"\xef\xbb\xbf" if bom else b"") + t.encode("utf-8"))
        R = "Royaume fictif"
        fiche(R, "Grey Warden", type="personnage", gamme=f'"{R}"', id_glossaire='"T-0001"', nom_en='"Grey Warden"', nom_fr='"Gardien gris"',
              corps="Garde [[Références/Narration/Univers/Royaume fictif/Hollow Keep|Donjon creux]].\n", crlf=True, bom=True)
        fiche(R, "Hollow Keep", type="lieu", gamme=R, id_glossaire="T-0002", nom_en="Hollow Keep", nom_fr="Donjon creux # commentaire")
        fiche(R, "Ashen Order", type="faction", gamme=R, id_glossaire="T-0003", nom_en="Ashen Order", nom_fr='"Ordre de la Cendre"')
        fiche(R, "Pale Crown", type="objet", gamme=R, id_glossaire="T-0004", nom_en="Pale Crown", nom_fr="Couronne pâle")
        fiche(R, "Iron Maw", type="lieu", gamme=R, id_glossaire='""', nom_en="Iron Maw", nom_fr='""')
        fiche(R, "Pale Rider", type="personnage", gamme=R, id_glossaire='""', nom_en="Pale Rider", nom_fr='""')
        fiche(R, "Lost Crown", type="objet", gamme=R, id_glossaire="T-0099", nom_en="Lost Crown", nom_fr="Couronne perdue")
        fiche(R, "Gardien gris (copie)", type="personnage", gamme=R, id_glossaire="T-0001", nom_en="Grey Warden", nom_fr="Gardien gris")
        fiche(R, "The Order's Oath", type="lore", gamme=R, id_glossaire="T-0007", nom_en="\"The Order's Oath\"", nom_fr="'L''Ordre'",
              corps="Lié à [[Références/Narration/Univers/Royaume fictif/Ashen Order|Ordre des Cendres]] et à "
                    "[[Références/Narration/Univers/Royaume fictif/Grey Warden|Gardien grisé]] et à [[Références/Narration/Univers/Royaume fictif/Nulle part|X]].\n")
        # Une autre gamme, dont les identifiants recoupent ceux du Royaume : jamais comparée à ce glossaire
        fiche("Autre gamme", "Arthur", type="personnage", gamme='"Autre gamme"', id_glossaire="T-0001", nom_en="Arthur", nom_fr="Arthur")
        (U / R / "LISEZ-MOI.md").write_text("Pas une fiche.\n", encoding="utf-8")
        b = verifier(gl, U)
        attendu = dict(conformes=4, ecarts=1, a_relier=1, remplaces=1, id_inconnus=1, doublons=1, noms_fichier=1, liens=2, sans_id=1)
        assert b == attendu, f"bilan {b}\nattendu {attendu}"
        assert a_corriger(b)
        termes[1][2] = "Gardienne grise"                 # sabotage : le glossaire change, la fiche ne suit pas
        _xlsx(gl, termes)
        b2 = verifier(gl, U)
        assert b2["ecarts"] == 3 and b2["conformes"] == 2 and b2["liens"] == 2, f"sabotage non détecté : {b2}"
        assert verifier(gl, U / "Inexistant") is None, "dossier introuvable pris pour conforme"
        assert verifier(d / "Glossaires/GLOSSAIRE_TG_v2.3.xlsx", U) is None, "gamme illisible acceptée sans --gamme"
        assert verifier(gl, U, gamme="Gamme absente") is None, "gamme sans fiche prise pour conforme"
    print("AUTO-TEST OK — deux gammes aux mêmes identifiants séparées ; conforme (fin de ligne Windows, BOM, apostrophes doublées), "
          "écart, à relier, remplacé, id inconnu, doublon, nom de fichier, lien faux et lien cassé, sans id ; sabotage détecté ; "
          "dossier, gamme ou fiches introuvables = erreur")


def main():
    if "--auto-test" in sys.argv:
        return auto_test()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    v = sp.add_parser("verifier")
    v.add_argument("--glossaire", required=True)
    v.add_argument("--dossier", required=True)
    v.add_argument("--gamme")
    v.add_argument("--liens-dans", action="append", default=[], help="fichier ou dossier de Core où vérifier aussi les liens vers les fiches")
    a = ap.parse_args()
    b = verifier(a.glossaire, a.dossier, a.gamme, a.liens_dans)
    sys.exit(2 if b is None else (1 if a_corriger(b) else 0))


if __name__ == "__main__":
    main()
