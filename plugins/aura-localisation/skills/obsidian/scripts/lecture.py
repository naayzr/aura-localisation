"""Lecture de fichiers de traduction sans dépendance : .docx, .xlsx, .csv, .tsv, .txt, .md.

Copie IDENTIQUE dans chaque skill qui a des scripts (un contrôle le vérifie). Ne pas modifier une
copie seule : modifier toutes les copies ensemble.

Fonctions :
  paragraphes_docx(chemin) -> textes du CORPS, un par paragraphe, dans l'ordre (tableaux et zones de
                              texte compris, chaque texte UNE seule fois, texte masqué exclu)
  annexes_docx(chemin)     -> [(repère, texte)] des notes de bas de page et de fin, en-têtes, pieds
  masque_docx(chemin)      -> nombre de caractères en texte masqué (exclus des autres fonctions)
  feuilles_xlsx(chemin)    -> {nom_feuille: [[cellule, ...], ...]}  (valeurs affichées en texte)
  lignes_csv(chemin)       -> [[cellule, ...], ...]  (séparateur et encodage détectés, UTF-16 compris)
  textes(chemin)           -> liste de (repère, texte) pour tout format pris en charge
                              (pour un .docx : le corps, PUIS les notes, en-têtes et pieds)
"""
import csv, io, re, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
ENCODAGES = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
# Word écrit une zone de texte DEUX fois (mc:Choice pour lui, mc:Fallback pour les anciens lecteurs)
# et la range DANS le paragraphe qui la porte. Sans ces deux exclusions, son texte compte 4 fois.
IGNORES = (MC + "Fallback", W + "txbxContent")


def _masque(run):
    rpr = run.find(W + "rPr")
    return rpr is not None and rpr.find(W + "vanish") is not None


def _texte_paragraphe(p, masque=None):
    """Le texte d'UN paragraphe : sans les zones de texte qu'il porte (lues pour elles-mêmes), sans
    la copie de secours mc:Fallback, sans le texte masqué (ajouté à `masque` s'il est fourni)."""
    morceaux = []

    def descendre(n):
        for c in n:
            if c.tag in IGNORES:
                continue
            if c.tag == W + "r" and _masque(c):
                if masque is not None:
                    masque.append(sum(len(t.text or "") for t in c.iter(W + "t")))
                continue
            if c.tag == W + "t" and c.text:
                morceaux.append(c.text)
            elif c.tag == W + "tab":
                morceaux.append("\t")
            elif c.tag in (W + "br", W + "cr"):
                morceaux.append("\n")
            elif c.tag == W + "noBreakHyphen":
                morceaux.append("‑")
            descendre(c)

    descendre(p)
    return "".join(morceaux)


def _paragraphes(racine, masque=None):
    """Tous les paragraphes sous `racine`, dans l'ordre, chacun une seule fois."""
    out = []

    def marcher(n):
        for c in n:
            if c.tag == MC + "Fallback":
                continue
            if c.tag == W + "p":
                out.append(_texte_paragraphe(c, masque))
            marcher(c)        # les paragraphes des zones de texte que porte ce paragraphe

    marcher(racine)
    return out


def paragraphes_docx(chemin):
    with zipfile.ZipFile(chemin) as z:
        racine = ET.fromstring(z.read("word/document.xml"))
    return _paragraphes(racine.find(W + "body"))


def annexes_docx(chemin):
    """Notes de bas de page et de fin, en-têtes et pieds de page, chacun avec un repère lisible."""
    out = []
    with zipfile.ZipFile(chemin) as z:
        noms = z.namelist()
        for partie, balise, nom in (("word/footnotes.xml", "footnote", "note"),
                                    ("word/endnotes.xml", "endnote", "note de fin")):
            if partie in noms:
                for n in ET.fromstring(z.read(partie)).iter(W + balise):
                    if n.get(W + "type") in ("separator", "continuationSeparator", "continuationNotice"):
                        continue
                    texte = "\n".join(t for t in _paragraphes(n) if t.strip())
                    if texte.strip():
                        out.append((f"{nom} {n.get(W + 'id')}", texte))
        for partie in sorted(x for x in noms if re.fullmatch(r"word/(header|footer)\d*\.xml", x)):
            nom = "en-tête" if "header" in partie else "pied de page"
            for i, t in enumerate(_paragraphes(ET.fromstring(z.read(partie))), 1):
                if t.strip():
                    out.append((f"{nom} {partie.split('/')[-1][:-4]} §{i}", t))
    return out


def masque_docx(chemin):
    masque = []
    with zipfile.ZipFile(chemin) as z:
        _paragraphes(ET.fromstring(z.read("word/document.xml")).find(W + "body"), masque)
    return sum(masque)


def _col_index(ref):
    lettres = re.match(r"([A-Z]+)", ref).group(1)
    n = 0
    for c in lettres:
        n = n * 26 + (ord(c) - 64)
    return n - 1


def feuilles_xlsx(chemin):
    with zipfile.ZipFile(chemin) as z:
        noms = z.namelist()
        partages = []
        if "xl/sharedStrings.xml" in noms:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(S + "si"):
                partages.append("".join(t.text or "" for t in si.iter(S + "t")))
        classeur = ET.fromstring(z.read("xl/workbook.xml"))
        liens = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        cible = {l.get("Id"): l.get("Target") for l in liens}
        resultat = {}
        for f in classeur.iter(S + "sheet"):
            t = cible[f.get(R + "id")].lstrip("/")
            t = t if t.startswith("xl/") else "xl/" + t
            lignes = []
            for row in ET.fromstring(z.read(t)).iter(S + "row"):
                ligne = []
                for c in row.iter(S + "c"):
                    i = _col_index(c.get("r")) if c.get("r") else len(ligne)
                    while len(ligne) < i:
                        ligne.append("")
                    typ, v = c.get("t"), c.find(S + "v")
                    if typ == "s" and v is not None:
                        val = partages[int(v.text)]
                    elif typ == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter(S + "t"))
                    else:
                        val = v.text if v is not None and v.text is not None else ""
                    ligne.append(val)
                lignes.append(ligne)
            resultat[f.get("name")] = lignes
        return resultat


def _decoder(octets):
    if octets[:2] in (b"\xff\xfe", b"\xfe\xff"):   # UTF-16 : export Excel « Texte Unicode »
        return octets.decode("utf-16")
    for enc in ENCODAGES:
        try:
            return octets.decode(enc)
        except UnicodeDecodeError:
            continue
    return octets.decode("latin-1", errors="replace")


def separateur(texte):
    """Le séparateur d'un CSV. Un texte français contient des virgules : deviner sur tout le contenu
    (csv.Sniffer) prenait la virgule pour un fichier en points-virgules et perdait les colonnes. On regarde
    les 10 premières lignes non vides, et on retient le premier séparateur, dans l'ordre ; tab , |,
    présent dans au moins la moitié d'entre elles (une ligne de titre au-dessus du tableau n'y change rien).
    Aucun → une seule colonne."""
    lignes = [l for l in texte.splitlines() if l.strip()][:10]
    for d in (";", "\t", ",", "|"):
        if lignes and sum(1 for l in lignes if d in l) * 2 >= len(lignes):
            return d
    return None


def lignes_csv(chemin):
    texte = _decoder(Path(chemin).read_bytes())
    d = separateur(texte)
    if d is None:
        return [[l] for l in texte.splitlines()]
    return [l for l in csv.reader(io.StringIO(texte), delimiter=d)]


def textes(chemin):
    """Tout format pris en charge → liste de (repère lisible, texte)."""
    p = Path(chemin)
    ext = p.suffix.lower()
    if ext == ".docx":
        corps = [(f"§{i}", t) for i, t in enumerate(paragraphes_docx(p), 1) if t.strip()]
        return corps + annexes_docx(p)
    if ext == ".xlsx":
        out = []
        for feuille, lignes in feuilles_xlsx(p).items():
            for i, ligne in enumerate(lignes, 1):
                for j, val in enumerate(ligne):
                    if str(val).strip():
                        out.append((f"{feuille}!L{i}C{j + 1}", str(val)))
        return out
    if ext in (".csv", ".tsv"):
        out = []
        for i, ligne in enumerate(lignes_csv(p), 1):
            for j, val in enumerate(ligne):
                if val.strip():
                    out.append((f"L{i}C{j + 1}", val))
        return out
    if ext in (".txt", ".md", ""):
        texte = _decoder(p.read_bytes())
        return [(f"L{i}", l) for i, l in enumerate(texte.splitlines(), 1) if l.strip()]
    raise ValueError(f"format non pris en charge : {ext} (accepté : .docx .xlsx .csv .tsv .txt .md)")
