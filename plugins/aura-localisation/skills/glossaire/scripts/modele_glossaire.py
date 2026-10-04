"""Modèle du glossaire v3 : colonnes, listes fermées, lecture et écriture du classeur au standard.

Une seule écriture de la règle dans le code : controle_glossaire.py, gerer_glossaire.py et
chercher_terme.py importent ce module. SKILL.md (section 1) documente les mêmes listes ;
`python3 modele_glossaire.py` les affiche pour comparaison.

Bibliothèque standard uniquement. La lecture passe par lecture.py (copie identique partagée).
"""
import datetime as dt
import os
import posixpath
import re
import shutil
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

# ------------------------------------------------------------------ le modèle (CONVENTIONS v3)
COLONNES = ["ID", "EN", "FR", "CATÉGORIE", "GENRE", "NOMBRE", "ÉLISION", "FORMES ACCORDÉES",
            "RAPPEL STANDARD", "DÉFINITION MÉCANIQUE", "STATUT", "SOURCE", "PUBLIÉ DANS", "NOTES", "DATE"]
STATUTS = ["Brouillon", "À confirmer", "Confirmé", "Gelé", "Archivé"]
ACTIFS = ["Brouillon", "À confirmer", "Confirmé", "Gelé"]          # défini positivement
EN_VIGUEUR = ["Confirmé", "Gelé"]
CATEGORIES = ["MÉCANIQUE", "MOT-CLÉ", "COMPOSANT", "PERSONNAGE", "LIEU", "OBJET", "LORE", "INTERFACE", "AUTRE"]
GENRES = ["m", "f", "—"]
NOMBRES = ["singulier", "pluriel", "invariable"]
ELISIONS = ["oui", "non"]
GENRE_OBLIGATOIRE = ["PERSONNAGE", "LIEU", "OBJET", "LORE", "MOT-CLÉ"]  # MOT-CLÉ non nominal : « — »
ONGLETS = ["Tableau de bord", "Termes", "CHANGELOG", "Notice"]
CHANGELOG_COLONNES = ["DATE", "VERSION", "ID", "EN", "CHAMP", "AVANT", "APRÈS", "RAISON", "DÉCIDÉ PAR"]
LISTES = {"STATUT": STATUTS, "CATÉGORIE": CATEGORIES, "GENRE": GENRES, "NOMBRE": NOMBRES, "ÉLISION": ELISIONS}
PLAGE_MAX = 20000  # lignes couvertes par les formules, mises en forme et listes déroulantes

# ------------------------------------------------------------------ normalisation
_APOS = {0x2019: "'", 0x2018: "'", 0x02BC: "'", 0x00A0: " ", 0x202F: " ", 0x2009: " "}  # apostrophes, espaces insécables


def nfc(s):
    return unicodedata.normalize("NFC", str(s))


def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if not unicodedata.combining(c))


def cle(s):
    """Clé de comparaison d'un terme : casse, accents, apostrophes et espaces neutralisés."""
    s = sans_accents(nfc(s).translate(_APOS)).casefold()
    return re.sub(r"\s+", " ", s).strip()


def cle_entete(s):
    s = sans_accents(nfc(s)).upper()
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


_PAR_CLE = {cle_entete(c): c for c in COLONNES}


def colonne_canonique(nom):
    """« statut », « Définition mécanique » → nom exact de la colonne, ou None."""
    return _PAR_CLE.get(cle_entete(nom))


def valeur_canonique(colonne, valeur):
    """Valeur d'une liste fermée écrite à peu près (casse, accents) → orthographe exacte, ou None."""
    v = str(valeur).strip()
    if colonne == "GENRE" and v in {"-", "–"}:
        return "—"
    for ok in LISTES.get(colonne, []):
        if cle(ok) == cle(v):
            return ok
    return None


def date_texte(v):
    """Date au format AAAA-MM-JJ ; accepte un numéro de série Excel."""
    v = str(v).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return v
    try:
        n = float(v)
        if 20000 < n < 80000:
            return (dt.date(1899, 12, 30) + dt.timedelta(days=int(n))).isoformat()
    except ValueError:
        pass
    return v


def aujourdhui():
    return dt.date.today().isoformat()


# ------------------------------------------------------------------ lecture d'un glossaire au standard
def lire_glossaire(chemin):
    """Lit un classeur v3. Les en-têtes sont rapprochés de leur nom exact (le contrôle signale l'écart)."""
    feuilles = {nfc(k): v for k, v in lecture.feuilles_xlsx(chemin).items()}
    g = {"chemin": Path(chemin), "onglets": list(feuilles), "entetes": [], "termes": [],
         "changelog": [], "changelog_entetes": [], "cellules_hors_entete": 0,
         "changelog_hors_standard": [], "changelog_hors_entete": 0, "commentaires": commentaires_excel(chemin)}
    termes = feuilles.get("Termes")
    if termes:
        g["entetes"] = [nfc(x).strip() for x in termes[0]]
        cibles = [colonne_canonique(x) for x in g["entetes"]]
        for i, ligne in enumerate(termes[1:], start=2):
            if not any(str(v).strip() for v in ligne):
                continue
            d = {c: "" for c in COLONNES}
            d["_ligne"] = i
            d["_autres"] = {}
            for j, val in enumerate(ligne):
                val = nfc(val).strip()
                if j >= len(cibles):
                    if val:
                        g["cellules_hors_entete"] += 1
                    continue
                if cibles[j]:
                    d[cibles[j]] = val
                elif val:
                    d["_autres"][g["entetes"][j] or f"colonne {j + 1}"] = val
            d["DATE"] = date_texte(d["DATE"])
            g["termes"].append(d)
    ch = feuilles.get("CHANGELOG")
    if ch:
        g["changelog_entetes"] = [nfc(x).strip() for x in ch[0]]
        # ce que le programme ne sait pas réécrire : un en-tête hors liste, une valeur sans en-tête connu
        g["changelog_hors_standard"] = [e for e in g["changelog_entetes"] if e and e not in CHANGELOG_COLONNES]
        for ligne in ch[1:]:
            if any(str(v).strip() for v in ligne):
                d = {c: "" for c in CHANGELOG_COLONNES}
                for j, val in enumerate(ligne):
                    nom = g["changelog_entetes"][j] if j < len(g["changelog_entetes"]) else ""
                    if nom in d:
                        d[nom] = nfc(val).strip()
                    elif str(val).strip() and not nom:
                        g["changelog_hors_entete"] += 1
                d["DATE"] = date_texte(d["DATE"])
                g["changelog"].append(d)
    return g


# ------------------------------------------------------------------ ce que la réécriture ne reprend pas
_NS_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
_NS_S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_NS_FIL = "{http://schemas.microsoft.com/office/spreadsheetml/2018/threadedcomments}"
_NS_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _cible(base, target):
    return target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(base), target))


def commentaires_excel(chemin):
    """[(onglet, cellule, texte)] des commentaires et notes Excel du classeur. Le programme réécrit le
    classeur sans eux : ils sont repris dans NOTES (onglet Termes) ou font refuser l'écriture."""
    out = []
    try:
        with zipfile.ZipFile(chemin) as z:
            noms = set(z.namelist())
            if not any("comment" in n.lower() for n in noms):
                return out
            classeur = ET.fromstring(z.read("xl/workbook.xml"))
            liens = {l.get("Id"): l.get("Target") for l in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
            for f in classeur.iter(_NS_S + "sheet"):
                feuille = _cible("xl/workbook.xml", liens.get(f.get(_NS_R + "id"), ""))
                rels = posixpath.join(posixpath.dirname(feuille), "_rels", posixpath.basename(feuille) + ".rels")
                if rels not in noms:
                    continue
                cibles = {l.get("Type", "").rsplit("/", 1)[-1]: _cible(feuille, l.get("Target", ""))
                          for l in ET.fromstring(z.read(rels))}
                vus = {}
                # Excel 365 range ses commentaires « à thread » dans threadedComments ET en double (texte de
                # remplacement) dans comments ; ses notes ne sont QUE dans comments. On lit donc les deux : le
                # texte à thread pour une cellule qui en a un, la note pour toutes les autres — jamais l'un
                # à la place de l'autre (une feuille qui porte les deux perdait ses notes en silence).
                if cibles.get("threadedComment") in noms:
                    for c in ET.fromstring(z.read(cibles["threadedComment"])).iter(_NS_FIL + "threadedComment"):
                        texte = "".join(c.find(_NS_FIL + "text").itertext()).strip() if c.find(_NS_FIL + "text") is not None else ""
                        vus[c.get("ref")] = " / ".join(x for x in (vus.get(c.get("ref")), texte) if x)
                a_thread = set(vus)
                if cibles.get("comments") in noms:
                    for c in ET.fromstring(z.read(cibles["comments"])).iter(_NS_S + "comment"):
                        if c.get("ref") not in a_thread:
                            vus[c.get("ref")] = "".join(c.itertext()).strip()
                out += [(nfc(f.get("name")), ref, nfc(txt)) for ref, txt in vus.items()]
    except (KeyError, zipfile.BadZipFile, ET.ParseError):
        return out
    return out


def ref_cellule(ref):
    """« C12 » → (index de colonne 2, ligne 12) ; (None, None) si illisible."""
    m = re.fullmatch(r"\$?([A-Z]+)\$?(\d+)", ref or "")
    if not m:
        return None, None
    n = 0
    for c in m.group(1):
        n = n * 26 + ord(c) - 64
    return n - 1, int(m.group(2))


def commentaires_hors_termes(g):
    """Commentaires Excel qui ne sont pas posés sur une ligne de terme de l'onglet Termes : le programme
    ne peut les reprendre nulle part (ceux d'une ligne de terme vont dans ses NOTES)."""
    lignes = {t["_ligne"] for t in g["termes"]}
    return [(o, ref, x) for o, ref, x in g["commentaires"] if o != "Termes" or ref_cellule(ref)[1] not in lignes]


def _retoucher(chemin, changer=None, ajouter=None):
    """Pour les auto-tests seulement : modifie des parties du classeur (nom → fonction(texte) → texte) et
    en ajoute (nom → texte), comme le ferait une retouche à la main dans Excel."""
    parts = {}
    with zipfile.ZipFile(chemin) as z:
        for n in z.namelist():
            parts[n] = z.read(n)
    for n, f in (changer or {}).items():
        parts[n] = f(parts[n].decode("utf-8")).encode("utf-8")
    for n, x in (ajouter or {}).items():
        parts[n] = x.encode("utf-8")
    with zipfile.ZipFile(chemin, "w", zipfile.ZIP_DEFLATED) as z:
        for n, octets in parts.items():
            z.writestr(n, octets)


def textes_onglets(chemin, onglets=("Tableau de bord", "Notice")):
    """{onglet: [textes]} des cellules de texte (chiffres exclus) de ces onglets, dans l'ordre."""
    feuilles = {nfc(k): v for k, v in lecture.feuilles_xlsx(chemin).items()}
    out = {}
    for o in onglets:
        vus = []
        for ligne in feuilles.get(o, []):
            for v in ligne:
                s = nfc(v).strip()
                if s and s not in ("—", "-") and not re.fullmatch(r"-?\d+(?:[.,]\d+)?", s) and s not in vus:
                    vus.append(s)
        out[o] = vus
    return out


def nombre_termes(termes):
    return sum(1 for t in termes if t.get("EN", "").strip())


# ------------------------------------------------------------------ fichiers : verrou, sauvegarde
def verrou_excel(chemin):
    """Excel pose « ~$nom.xlsx » à côté d'un fichier ouvert. Renvoie ce fichier s'il existe."""
    p = Path(chemin)
    for nom in (f"~${p.name}", f"~${p.name[2:]}"):
        if (p.parent / nom).exists():
            return p.parent / nom
    return None


def gamme_depuis_nom(chemin):
    m = re.fullmatch(r"Glossaire_(.+)\.xlsx", Path(chemin).name, re.I)
    return m.group(1) if m else Path(chemin).stem


def dossier_archives(chemin):
    """<HERVÉ WORLD>/Glossaires/Glossaire_X.xlsx → <HERVÉ WORLD>/Core/Archives ; sinon None."""
    p = Path(chemin).resolve()
    if p.parent.name == "Glossaires":
        return p.parent.parent / "Core" / "Archives"
    return None


def sauvegarder(chemin, archives=None, quand=None):
    """Copie datée AVANT modification : Glossaire_<Gamme>_avant_AAAA-MM-JJ_HHhMM_<N>termes.xlsx.

    Ne s'écrase jamais : si le nom existe avec un contenu différent, suffixe _2, _3…
    Renvoie (chemin de la sauvegarde, déjà_existante)."""
    src = Path(chemin)
    archives = Path(archives) if archives else dossier_archives(src)
    if archives is None:
        raise ValueError("dossier d'archives inconnu : le glossaire n'est pas dans Glossaires/ ; "
                         "préciser --archives <HERVÉ WORLD>/Core/Archives")
    lecture.hors_du_plugin(archives)
    archives.mkdir(parents=True, exist_ok=True)
    quand = quand or dt.datetime.now()
    n = nombre_termes(lire_glossaire(src)["termes"]) if src.suffix.lower() == ".xlsx" else 0
    base = f"Glossaire_{gamme_depuis_nom(src)}_avant_{quand:%Y-%m-%d_%Hh%M}_{n}termes"
    cible, k = archives / f"{base}.xlsx", 1
    octets = src.read_bytes()
    while cible.exists():
        if cible.read_bytes() == octets:
            return cible, True
        k += 1
        cible = archives / f"{base}_{k}.xlsx"
    shutil.copy2(src, cible)
    return cible, False


# ------------------------------------------------------------------ identifiants et versions
def prochain_id(termes):
    nums = [int(m.group(1)) for t in termes for m in [re.fullmatch(r"T-(\d+)", t.get("ID", ""))] if m]
    return f"T-{(max(nums) if nums else 0) + 1:04d}"


def version_courante(changelog):
    for l in reversed(changelog):
        if re.fullmatch(r"\d+\.\d+", l.get("VERSION", "")):
            return l["VERSION"]
    return "1.0"


def version_suivante(v, majeure):
    a, b = (int(x) for x in v.split("."))
    return f"{a + 1}.0" if majeure else f"{a}.{b + 1}"


# ------------------------------------------------------------------ catégorie proposée à l'import
CATEGORIE_ALIAS = {
    "MÉCANIQUE": ["MECANIQUE", "MECANIQUES", "MECHANIC", "MECHANICS", "PHASE", "PHASES", "ACTION", "ACTIONS",
                  "RESSOURCE", "RESSOURCES", "RESOURCE", "RESOURCES", "STATUT", "STATUTS", "ETAT", "ETATS",
                  "REGLE", "REGLES", "CAPACITE", "CAPACITES", "EFFET", "EFFETS"],
    "MOT-CLÉ": ["MOT CLE", "MOTS CLES", "KEYWORD", "KEYWORDS"],
    "COMPOSANT": ["COMPOSANT", "COMPOSANTS", "COMPONENT", "COMPONENTS", "CARTE", "CARTES", "TYPE DE CARTE",
                  "JETON", "JETONS", "TOKEN", "TOKENS", "PION", "PIONS", "PLATEAU", "TUILE", "TUILES"],
    "PERSONNAGE": ["PERSONNAGE", "PERSONNAGES", "CHARACTER", "CHARACTERS", "HEROS", "PNJ"],
    "LIEU": ["LIEU", "LIEUX", "LIEU PROPRE", "LOCATION", "LOCATIONS", "PLACE", "REGION", "REGIONS"],
    "OBJET": ["OBJET", "OBJETS", "ITEM", "ITEMS", "EQUIPEMENT"],
    "LORE": ["LORE", "ENTITE", "ENTITES", "FACTION", "FACTIONS", "PEUPLE", "PEUPLES", "CREATURE", "CREATURES",
             "MONSTRE", "MONSTRES", "UNIVERS"],
    "INTERFACE": ["INTERFACE", "UI", "INTERFACE UTILISATEUR"],
}
_ALIAS_CAT = {a: cat for cat, alias in CATEGORIE_ALIAS.items() for a in alias}


def proposer_categorie(*valeurs):
    """(type, catégorie d'origine…) → (catégorie v3, exacte?). Une PROPOSITION, à valider par Hervé."""
    for v in valeurs:
        if not str(v).strip():
            continue
        for c in CATEGORIES:
            if cle_entete(c) == cle_entete(v):
                return c, True
    for v in valeurs:
        if cle_entete(v) in _ALIAS_CAT:
            return _ALIAS_CAT[cle_entete(v)], False
    return "AUTRE", False


# ------------------------------------------------------------------ écriture du classeur au standard
_ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
NSR = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'


def _x(s):
    return escape(_ILLEGAL.sub("", str(s)))


def _a(s):
    return escape(_ILLEGAL.sub("", str(s)), {'"': "&quot;"})


def _col(i):
    s, i = "", i + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _txt(ref, s, st=0):
    if s is None or str(s) == "":
        return f'<c r="{ref}" s="{st}"/>' if st else ""
    return f'<c r="{ref}" s="{st}" t="inlineStr"><is><t xml:space="preserve">{_x(s)}</t></is></c>'


def _f(ref, formule, valeur, st):
    if isinstance(valeur, str):
        return f'<c r="{ref}" s="{st}" t="str"><f>{_x(formule)}</f><v>{_x(valeur)}</v></c>'
    return f'<c r="{ref}" s="{st}"><f>{_x(formule)}</f><v>{valeur}</v></c>'


# styles : 0 normal · 1 en-tête · 2 corps · 3 titre · 4 sous-titre · 5 section · 6 nombre · 7 libellé
#          8 total (nombre) · 9 total (libellé) · 10 notice · 11 notice (intertitre)
STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet {NS}>
<fonts count="6">
<font><sz val="11"/><name val="Calibri"/><family val="2"/></font>
<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>
<font><b/><sz val="15"/><color rgb="FF1F3864"/><name val="Calibri"/><family val="2"/></font>
<font><i/><sz val="10"/><color rgb="FF595959"/><name val="Calibri"/><family val="2"/></font>
<font><b/><sz val="11"/><name val="Calibri"/><family val="2"/></font>
<font><b/><sz val="11"/><color rgb="FF1F3864"/><name val="Calibri"/><family val="2"/></font>
</fonts>
<fills count="5">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF1F3864"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFD9E1F2"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="3">
<border><left/><right/><top/><bottom/><diagonal/></border>
<border><left/><right/><top/><bottom style="thin"><color rgb="FFD9D9D9"/></bottom><diagonal/></border>
<border><left/><right/><top style="thin"><color rgb="FF1F3864"/></top><bottom style="thin"><color rgb="FF1F3864"/></bottom><diagonal/></border>
</borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="12">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="5" fillId="3" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="1" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"/>
<xf numFmtId="1" fontId="4" fillId="4" borderId="2" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right"/></xf>
<xf numFmtId="0" fontId="4" fillId="4" borderId="2" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="5" fillId="0" borderId="0" xfId="0" applyFont="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
<dxfs count="6">
<dxf><fill><patternFill patternType="solid"><fgColor rgb="FFFCE4E4"/><bgColor rgb="FFFCE4E4"/></patternFill></fill></dxf>
<dxf><fill><patternFill patternType="solid"><fgColor rgb="FFFFEBCC"/><bgColor rgb="FFFFEBCC"/></patternFill></fill></dxf>
<dxf><fill><patternFill patternType="solid"><fgColor rgb="FFE2EFDA"/><bgColor rgb="FFE2EFDA"/></patternFill></fill></dxf>
<dxf><font><b/><color rgb="FF1F3864"/></font><fill><patternFill patternType="solid"><fgColor rgb="FFBDD7EE"/><bgColor rgb="FFBDD7EE"/></patternFill></fill></dxf>
<dxf><font><i/><strike/><color rgb="FF808080"/></font></dxf>
<dxf><font><b/><color rgb="FF9C0006"/></font><fill><patternFill patternType="solid"><fgColor rgb="FFFFC7CE"/><bgColor rgb="FFFFC7CE"/></patternFill></fill></dxf>
</dxfs>
<tableStyles count="0" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/>
</styleSheet>"""

COULEUR_STATUT = {"Brouillon": 0, "À confirmer": 1, "Confirmé": 2, "Gelé": 3, "Archivé": 4}  # dxfId
LARGEURS_TERMES = [9, 24, 24, 13, 8, 11, 9, 22, 30, 40, 13, 28, 22, 48, 11]
LARGEURS_CHANGELOG = [11, 9, 9, 22, 18, 24, 24, 40, 20]


def _feuille(lignes, largeurs, *, gele=None, filtre=None, cf="", dv="", grille=True, actif=False,
             paysage=False):
    dern_l = max(lignes) if lignes else 1
    dern_c = _col(len(largeurs) - 1)
    attrs = (' tabSelected="1"' if actif else "") + ("" if grille else ' showGridLines="0"')
    vue = '<sheetView workbookViewId="0"' + attrs + ">"
    if gele:
        xs, ys = gele
        tl = f"{_col(xs)}{ys + 1}"
        if xs and ys:
            vue += (f'<pane xSplit="{xs}" ySplit="{ys}" topLeftCell="{tl}" activePane="bottomRight" state="frozen"/>'
                    f'<selection pane="topRight"/><selection pane="bottomLeft"/>'
                    f'<selection pane="bottomRight" activeCell="{tl}" sqref="{tl}"/>')
        else:
            vue += (f'<pane ySplit="{ys}" topLeftCell="{tl}" activePane="bottomLeft" state="frozen"/>'
                    f'<selection pane="bottomLeft" activeCell="{tl}" sqref="{tl}"/>')
    vue += "</sheetView>"
    cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(largeurs))
    data = "".join(f'<row r="{n}">{"".join(lignes[n])}</row>' for n in sorted(lignes))
    xml = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet {NS} {NSR}>'
           f'<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr><dimension ref="A1:{dern_c}{dern_l}"/>'
           f'<sheetViews>{vue}</sheetViews><sheetFormatPr defaultRowHeight="15"/><cols>{cols}</cols>'
           f'<sheetData>{data}</sheetData>')
    if filtre:
        xml += f'<autoFilter ref="{filtre}"/>'
    xml += cf + dv
    xml += ('<pageMargins left="0.4" right="0.4" top="0.6" bottom="0.6" header="0.3" footer="0.3"/>'
            '<pageSetup paperSize="9" orientation="' + ("landscape" if paysage else "portrait")
            + '" fitToWidth="1" fitToHeight="0"/>'
            '<headerFooter><oddFooter>&amp;L&amp;A&amp;RPage &amp;P sur &amp;N</oddFooter></headerFooter>'
            "</worksheet>")
    return xml


def _liste_excel(valeurs):
    return '"' + ",".join(valeurs) + '"'


def _produits(termes):
    vus = []
    for t in termes:
        for p in re.split(r"\s*;\s*", t.get("PUBLIÉ DANS", "")):
            if p.strip() and cle(p) not in {cle(v) for v in vus}:
                vus.append(p.strip())
    return vus


def notice(gamme):
    """Une page : ce qu'est le classeur, ses colonnes, ses statuts, ses règles. (style, texte)"""
    L = [(3, f"Notice — Glossaire {gamme}"),
         (4, "À lire une fois. Ce classeur est LE glossaire de la gamme : un seul fichier par gamme, sans numéro "
             "de version dans son nom. La version et l'historique sont dans l'onglet CHANGELOG."),
         (11, "Les onglets"),
         (10, "Tableau de bord : chiffres calculés par formule à partir de l'onglet Termes. Rien à y saisir. "
              "Une case rouge signale un point à régler."),
         (10, "Termes : une ligne par terme et par sens mécanique. En-tête et colonnes ID et EN figés, filtres "
              "actifs, listes déroulantes sur CATÉGORIE, GENRE, NOMBRE, ÉLISION et STATUT, couleur selon le statut."),
         (10, "CHANGELOG : chaque changement (date, version, terme, avant, après, raison, qui a décidé). "
              "On ajoute en bas, on n'efface jamais."),
         (11, "Les colonnes de Termes"),
         (10, "ID : identifiant stable (T-0001…), jamais réutilisé, même pour un terme archivé. "
              "EN : le terme anglais exact. FR : le terme retenu, un seul par cellule."),
         (10, "CATÉGORIE : " + ", ".join(CATEGORIES) + "."),
         (10, "GENRE (m, f, ou — quand sans objet), NOMBRE (singulier, pluriel, invariable), ÉLISION (oui : l'… ; "
              "non : le…, h aspiré), FORMES ACCORDÉES (les formes écrites, par ex. au féminin et au pluriel). "
              "Le genre est obligatoire pour " + ", ".join(GENRE_OBLIGATOIRE) + " (mot-clé nominal) : "
              "Hervé le déclare, AURA ne le devine jamais."),
         (10, "RAPPEL STANDARD : le texte de rappel identique sur toute la gamme pour un mot-clé. "
              "DÉFINITION MÉCANIQUE : ce que le terme fait en jeu, en français ; c'est elle qui rapproche deux "
              "termes, jamais la ressemblance des mots."),
         (10, "SOURCE : d'où vient le terme (livret p. X, échange éditeur du JJ/MM, glossaire officiel de licence…). "
              "PUBLIÉ DANS : les produits où le terme est imprimé, séparés par un point-virgule. "
              "NOTES : justification, alternatives écartées, risques de confusion, termes liés. "
              "DATE : dernière modification de la ligne (AAAA-MM-JJ)."),
         (11, "Les 5 statuts"),
         (10, "Brouillon : proposé, non validé ; peut changer librement."),
         (10, "À confirmer : attend l'éditeur ou l'ayant droit ; la question est notée dans Core/Questions_Editeurs.md."),
         (10, "Confirmé : validé par Hervé (ou l'éditeur) ; peut encore changer, avec une ligne au CHANGELOG."),
         (10, "Gelé : imprimé dans un produit (PUBLIÉ DANS rempli) ; ne bouge plus sans erratum."),
         (10, "Archivé : remplacé, gardé pour trace ; NOTES dit par quoi et à partir de quel produit."),
         (11, "Les règles"),
         (10, "Un sens mécanique = un terme français. Un même mot anglais à deux sens a deux lignes et deux "
              "définitions, et NOTES l'explique."),
         (10, "Une décision de terme s'écrit ici seulement, justifiée en NOTES, jamais ailleurs."),
         (10, "Avant qu'AURA modifie ce fichier : le fermer dans Excel. AURA fait une sauvegarde datée dans "
              "Core/Archives avant toute modification groupée."),
         (10, "Pour un relecteur : AURA prépare une copie avec des colonnes de retour ; ce fichier-ci ne change pas.")]
    return L


def ecrire_glossaire(chemin, gamme, termes, changelog, remplacer=False):
    """Écrit le classeur v3 complet (4 onglets). Écrit dans une copie temporaire, puis remplace."""
    chemin = Path(chemin)
    if chemin.exists() and not remplacer:
        raise FileExistsError(f"{chemin} existe déjà : rien n'est écrasé sans sauvegarde (voir --ecrire)")
    v = verrou_excel(chemin)
    if v:
        raise PermissionError(f"le fichier semble ouvert dans Excel ({v.name} présent) : le fermer, puis relancer")
    N = PLAGE_MAX
    # ---- Termes
    lt = {1: [_txt(f"{_col(j)}1", c, 1) for j, c in enumerate(COLONNES)]}
    for i, t in enumerate(termes, start=2):
        lt[i] = [_txt(f"{_col(j)}{i}", t.get(c, ""), 2) for j, c in enumerate(COLONNES)]
    der = max(lt)
    k = COLONNES.index("STATUT")
    colk = _col(k)
    cf = (f'<conditionalFormatting sqref="A2:{_col(len(COLONNES) - 1)}{N}">'
          + "".join(f'<cfRule type="expression" dxfId="{d}" priority="{p}"><formula>${colk}2="{_x(s)}"</formula></cfRule>'
                    for p, (s, d) in enumerate(COULEUR_STATUT.items(), start=1))
          + "</conditionalFormatting>")
    dv_items = []
    for nom, valeurs in LISTES.items():
        c = _col(COLONNES.index(nom))
        dv_items.append(f'<dataValidation type="list" allowBlank="1" showErrorMessage="1" errorTitle="{_a(nom)}" '
                        f'error="{_a("Valeurs admises : " + ", ".join(valeurs))}" sqref="{c}2:{c}{N}">'
                        f'<formula1>{_x(_liste_excel(valeurs))}</formula1></dataValidation>')
    dv = f'<dataValidations count="{len(dv_items)}">{"".join(dv_items)}</dataValidations>'
    filtre_t = f"A1:{_col(len(COLONNES) - 1)}{der}"
    f_termes = _feuille(lt, LARGEURS_TERMES, gele=(2, 1), filtre=filtre_t, cf=cf, dv=dv, paysage=True)
    # ---- CHANGELOG
    lc = {1: [_txt(f"{_col(j)}1", c, 1) for j, c in enumerate(CHANGELOG_COLONNES)]}
    for i, l in enumerate(changelog, start=2):
        lc[i] = [_txt(f"{_col(j)}{i}", l.get(c, ""), 2) for j, c in enumerate(CHANGELOG_COLONNES)]
    derc = max(lc)
    filtre_c = f"A1:{_col(len(CHANGELOG_COLONNES) - 1)}{derc}"
    f_chg = _feuille(lc, LARGEURS_CHANGELOG, gele=(0, 1), filtre=filtre_c, paysage=True)
    # ---- Tableau de bord (formules + valeurs déjà calculées pour l'aperçu)
    nb = nombre_termes(termes)

    def compte(col, val):
        return sum(1 for t in termes if cle(t.get(col, "")) == cle(val) and t.get("EN", "").strip())

    tb, r = {}, 1
    col_d, col_e, col_m = (_col(COLONNES.index(x)) for x in ("CATÉGORIE", "GENRE", "PUBLIÉ DANS"))
    tb[1] = [_txt("A1", f"Glossaire {gamme} — tableau de bord", 3)]
    tb[2] = [_txt("A2", "Chiffres calculés par formule à partir de l'onglet Termes. Rien à saisir ici. "
                        "Une case rouge = un point à régler.", 4)]
    vers = version_courante(changelog)
    tb[4] = [_txt("A4", "Version du glossaire (dernière ligne du CHANGELOG)", 7),
             _f("B4", f'IFERROR(LOOKUP(2,1/(CHANGELOG!$B$2:$B${N}<>""),CHANGELOG!$B$2:$B${N}),"—")', vers, 6)]
    tb[5] = [_txt("A5", "Termes (lignes avec un EN)", 9), _f("B5", "COUNTA(Termes!$B:$B)-1", nb, 8)]
    tb[6] = [_txt("A6", "Termes affichés avec le filtre actuel de l'onglet Termes", 7),
             _f("B6", f"SUBTOTAL(103,Termes!$B$2:$B${N})", nb, 6)]
    tb[8] = [_txt("A8", "Par statut", 5), _txt("B8", "Termes", 5)]
    r = 9
    for s in STATUTS:
        tb[r] = [_txt(f"A{r}", s, 7), _f(f"B{r}", f"COUNTIF(Termes!${colk}:${colk},$A{r})", compte("STATUT", s), 6)]
        r += 1
    tot_s = sum(compte("STATUT", s) for s in STATUTS)
    tb[r] = [_txt(f"A{r}", "Total des 5 statuts", 9), _f(f"B{r}", f"SUM(B9:B{r - 1})", tot_s, 8)]
    alertes = [f"B{r + 1}"]
    tb[r + 1] = [_txt(f"A{r + 1}", "Statut vide ou hors des 5 statuts (doit être 0)", 7),
                 _f(f"B{r + 1}", f"B5-B{r}", nb - tot_s, 6)]
    r += 3
    tb[r] = [_txt(f"A{r}", "Ensembles utiles (définis par ce qu'ils contiennent)", 5), _txt(f"B{r}", "Termes", 5)]
    ens = [("À trancher (Brouillon + À confirmer)", ["Brouillon", "À confirmer"]),
           ("En vigueur (Confirmé + Gelé)", ["Confirmé", "Gelé"]),
           ("Gardés pour trace (Archivé)", ["Archivé"])]
    for lib, membres in ens:
        r += 1
        refs = "+".join(f"B{9 + STATUTS.index(m)}" for m in membres)
        tb[r] = [_txt(f"A{r}", lib, 7), _f(f"B{r}", refs, sum(compte("STATUT", m) for m in membres), 6)]
    r += 2
    tb[r] = [_txt(f"A{r}", "Par catégorie", 5), _txt(f"B{r}", "Termes", 5)]
    debut_cat = r + 1
    for c in CATEGORIES:
        r += 1
        tb[r] = [_txt(f"A{r}", c, 7), _f(f"B{r}", f"COUNTIF(Termes!${col_d}:${col_d},$A{r})", compte("CATÉGORIE", c), 6)]
    r += 1
    tot_c = sum(compte("CATÉGORIE", c) for c in CATEGORIES)
    tb[r] = [_txt(f"A{r}", "Catégorie vide ou hors liste (doit être 0)", 7),
             _f(f"B{r}", f"B5-SUM(B{debut_cat}:B{r - 1})", nb - tot_c, 6)]
    alertes.append(f"B{r}")
    r += 2
    tb[r] = [_txt(f"A{r}", "Points à régler", 5), _txt(f"B{r}", "Termes", 5)]
    r += 1
    obl = ",".join(f'"{c}"' for c in GENRE_OBLIGATOIRE)
    act = ",".join(f'"{s}"' for s in ACTIFS)
    n_genre = sum(1 for t in termes if t.get("EN", "").strip() and t.get("CATÉGORIE") in GENRE_OBLIGATOIRE
                  and not t.get("GENRE", "").strip() and t.get("STATUT") in ACTIFS)
    tb[r] = [_txt(f"A{r}", "Genre à déclarer par Hervé (" + ", ".join(GENRE_OBLIGATOIRE) + ")", 7),
             _f(f"B{r}", f"SUMPRODUCT(ISNUMBER(MATCH(Termes!${col_d}$2:${col_d}${N},{{{obl}}},0))"
                         f"*(Termes!${col_e}$2:${col_e}${N}=\"\")*ISNUMBER(MATCH(Termes!${colk}$2:${colk}${N},{{{act}}},0)))",
                n_genre, 6)]
    alertes.append(f"B{r}")
    r += 1
    n_gel = sum(1 for t in termes if t.get("STATUT") == "Gelé" and not t.get("PUBLIÉ DANS", "").strip())
    tb[r] = [_txt(f"A{r}", "Gelés sans PUBLIÉ DANS", 7),
             _f(f"B{r}", f'COUNTIFS(Termes!${colk}:${colk},"Gelé",Termes!${col_m}:${col_m},"")', n_gel, 6)]
    alertes.append(f"B{r}")
    r += 2
    tb[r] = [_txt(f"A{r}", "Par produit (colonne PUBLIÉ DANS)", 5), _txt(f"B{r}", "Termes", 5)]
    prods = _produits(termes)
    if not prods:
        r += 1
        tb[r] = [_txt(f"A{r}", "Aucun produit renseigné pour l'instant. Quand un produit apparaît, AURA ajoute "
                               "sa ligne ici (même formule).", 4)]
    for p in prods:
        r += 1
        n_p = sum(1 for t in termes if cle(p) in cle(t.get("PUBLIÉ DANS", "")))
        tb[r] = [_txt(f"A{r}", p, 7), _f(f"B{r}", f'COUNTIF(Termes!${col_m}:${col_m},"*"&$A{r}&"*")', n_p, 6)]
    cf_tb = (f'<conditionalFormatting sqref="{" ".join(alertes)}"><cfRule type="cellIs" dxfId="5" priority="1" '
             f'operator="greaterThan"><formula>0</formula></cfRule></conditionalFormatting>')
    f_tb = _feuille(tb, [74, 12], grille=False, actif=True, cf=cf_tb)
    # ---- Notice
    ln = {i: [_txt(f"A{i}", texte, st)] for i, (st, texte) in enumerate(notice(gamme), start=1)}
    f_not = _feuille(ln, [120], grille=False)
    # ---- assemblage
    noms = (f'<definedName name="_xlnm._FilterDatabase" localSheetId="1" hidden="1">Termes!$A$1:${_col(len(COLONNES) - 1)}${der}</definedName>'
            f'<definedName name="_xlnm._FilterDatabase" localSheetId="2" hidden="1">CHANGELOG!$A$1:${_col(len(CHANGELOG_COLONNES) - 1)}${derc}</definedName>'
            '<definedName name="_xlnm.Print_Titles" localSheetId="1">Termes!$1:$1</definedName>')
    return _classeur(chemin, list(zip(ONGLETS, [f_tb, f_termes, f_chg, f_not])), noms)


def _classeur(chemin, onglets, noms_definis=""):
    """Assemble et écrit le fichier .xlsx (copie temporaire, puis remplacement)."""
    n = len(onglets)
    wb = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook {NS} {NSR}>'
          '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="28800" windowHeight="16000" activeTab="0"/></bookViews><sheets>'
          + "".join(f'<sheet name="{_a(nom)}" sheetId="{i}" r:id="rId{i}"/>' for i, (nom, _) in enumerate(onglets, start=1))
          + "</sheets>" + (f"<definedNames>{noms_definis}</definedNames>" if noms_definis else "")
          + '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                      f'Target="worksheets/sheet{i}.xml"/>' for i in range(1, n + 1))
            + f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            "</Relationships>")
    racine = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
              '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
              "</Relationships>")
    types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
             + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                       for i in range(1, n + 1))
             + '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
             "</Types>")
    chemin = Path(lecture.hors_du_plugin(chemin))
    tmp = chemin.parent / f".ecriture_{chemin.name}"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", racine)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", rels)
        z.writestr("xl/styles.xml", STYLES)
        for i, (_, f) in enumerate(onglets, start=1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", f)
    os.replace(tmp, chemin)
    return chemin


# ------------------------------------------------------------------ export pour un traducteur ou un relecteur
EXPORT_COLONNES = ["EN", "FR", "CATÉGORIE", "GENRE", "NOMBRE", "ÉLISION", "FORMES ACCORDÉES", "RAPPEL STANDARD",
                   "DÉFINITION MÉCANIQUE", "STATUT", "CE QUE LE STATUT PERMET"]
RETOUR_COLONNES = ["RETOUR RELECTEUR", "RÉPONSE D'HERVÉ"]
PERMET = {"Brouillon": "Proposition : on peut la contester (en commentaire).",
          "À confirmer": "S'applique en attendant la réponse de l'éditeur.",
          "Confirmé": "S'applique sans discussion.",
          "Gelé": "Imprimé : s'applique sans discussion, ne change que par erratum.",
          "Archivé": "Ancien terme : ne plus l'employer (voir le terme qui le remplace)."}


def lisezmoi(gamme, pour):
    L = [(3, f"Glossaire {gamme} — à lire avant de commencer"),
         (4, "Copie de travail du glossaire de la gamme. Le glossaire de référence reste chez Hervé ; "
             "cette copie ne le modifie pas."),
         (11, "Ce que chaque statut permet"),
         *[(10, f"{s} : {PERMET[s]}") for s in STATUTS],
         (11, "Les règles"),
         (10, "Les termes de jeu et les mots-clés de ce glossaire ne se modifient pas dans la traduction : "
              "on les commente."),
         (10, "Un terme absent de ce glossaire ne s'invente pas : il fait l'objet d'une question à Hervé, "
              "avec la référence de la carte ou de la règle."),
         (10, "GENRE, NOMBRE et ÉLISION disent comment accorder un nom inventé. Une case vide veut dire : "
              "pas encore décidé, demander à Hervé avant d'accorder.")]
    if pour == "relecteur":
        L += [(11, "Comment rendre vos remarques"),
              (10, "Écrire uniquement dans la colonne RETOUR RELECTEUR, en commençant par un code :"),
              (10, "[OK] terme approuvé · [?] question · [MOD] suggestion, avec la proposition · "
                   "[ERR] erreur constatée, avec l'endroit."),
              (10, "Sur un terme Gelé (imprimé), on peut signaler un problème ; la décision revient à l'éditeur."),
              (10, "Ne pas modifier les autres colonnes, ni l'ordre des lignes, ni la colonne RÉF.")]
    return L


def ecrire_export(chemin, gamme, termes, pour="traducteur", avec_archives=False):
    """Copie propre pour un traducteur ou un relecteur : Lisez-moi + Termes (sans NOTES ni SOURCE)."""
    chemin = Path(chemin)
    if chemin.exists():
        raise FileExistsError(f"{chemin} existe déjà : choisir un autre nom (la date ou _v2)")
    garder = STATUTS if avec_archives else ACTIFS
    lignes_t = [t for t in termes if t.get("EN") and t.get("STATUT") in garder]
    cols = EXPORT_COLONNES + (RETOUR_COLONNES if pour == "relecteur" else []) + ["RÉF."]
    lt = {1: [_txt(f"{_col(j)}1", c, 1) for j, c in enumerate(cols)]}
    for i, t in enumerate(lignes_t, start=2):
        val = [t.get(c, "") for c in EXPORT_COLONNES[:-1]] + [PERMET.get(t.get("STATUT"), "")]
        val += [""] * (len(cols) - len(val) - 1) + [t.get("ID", "")]
        lt[i] = [_txt(f"{_col(j)}{i}", v, 2) for j, v in enumerate(val)]
    der = max(lt)
    k = _col(cols.index("STATUT"))
    cf = (f'<conditionalFormatting sqref="A2:{_col(len(cols) - 1)}{max(der, 2)}">'
          + "".join(f'<cfRule type="expression" dxfId="{d}" priority="{p}"><formula>${k}2="{_x(s)}"</formula></cfRule>'
                    for p, (s, d) in enumerate(COULEUR_STATUT.items(), start=1))
          + "</conditionalFormatting>")
    larg = [24, 24, 13, 8, 11, 9, 22, 30, 40, 13, 34] + ([40, 30] if pour == "relecteur" else []) + [9]
    f_t = _feuille(lt, larg, gele=(1, 1), filtre=f"A1:{_col(len(cols) - 1)}{der}", cf=cf, paysage=True)
    ln = {i: [_txt(f"A{i}", texte, st)] for i, (st, texte) in enumerate(lisezmoi(gamme, pour), start=1)}
    f_l = _feuille(ln, [120], grille=False, actif=True)
    noms = (f'<definedName name="_xlnm._FilterDatabase" localSheetId="1" hidden="1">Termes!$A$1:${_col(len(cols) - 1)}${der}</definedName>'
            '<definedName name="_xlnm.Print_Titles" localSheetId="1">Termes!$1:$1</definedName>')
    _classeur(chemin, [("Lisez-moi", f_l), ("Termes", f_t)], noms)
    return len(lignes_t)


if __name__ == "__main__":
    print("Colonnes de Termes :", " | ".join(COLONNES))
    print("Statuts :", " → ".join(STATUTS[:4]), "; puis", STATUTS[4])
    print("Catégories :", ", ".join(CATEGORIES))
    print("Genre obligatoire :", ", ".join(GENRE_OBLIGATOIRE))
    print("Onglets :", ", ".join(ONGLETS))
    print("CHANGELOG :", " | ".join(CHANGELOG_COLONNES))
