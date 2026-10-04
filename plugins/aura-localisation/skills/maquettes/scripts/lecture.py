"""Lecture de fichiers de traduction sans dépendance : .docx, .xlsx, .csv, .tsv, .txt, .md.

Copie IDENTIQUE dans chaque skill qui a des scripts (un contrôle le vérifie). Ne pas modifier une
copie seule : modifier toutes les copies ensemble.

Fonctions :
  paragraphes_docx(chemin) -> textes du CORPS, un par paragraphe, dans l'ordre (tableaux et zones de
                              texte compris, chaque texte UNE seule fois, texte masqué exclu)
  annexes_docx(chemin)     -> [(repère, texte)] des notes de bas de page et de fin, en-têtes, pieds
  masque_docx(chemin)      -> nombre de caractères en texte masqué (exclus des autres fonctions)
  feuilles_xlsx(chemin)    -> {nom_feuille: [[cellule, ...], ...]}  (un texte tel quel ; un nombre tel
                              qu'il est enregistré, sans son format d'affichage ; une date en AAAA-MM-JJ)
  lignes_csv(chemin)       -> [[cellule, ...], ...]  (séparateur et encodage détectés, UTF-16 compris ;
                              un CSV d'une seule colonne est lu sans ses guillemets)
  textes(chemin)           -> liste de (repère, texte) pour tout format pris en charge
  hors_du_plugin(chemin)   -> refuse (code 2) une cible d'écriture située dans le dossier du plugin AURA
                              (pour un .docx : le corps, PUIS les notes, en-têtes et pieds)

Motif partagé :
  BALISE                   -> une balise ou une icône ({icone}, <b>, </b>, [degats], [/b]) ; écrit ici une
                              seule fois pour le comptage de caractères, le contrôle des longueurs et la
                              typographie (une balise n'est ni contrôlée ni corrigée)
"""
import csv, io, re, zipfile
import datetime as dt
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
ENCODAGES = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
# Word écrit une zone de texte DEUX fois (mc:Choice pour lui, mc:Fallback pour les anciens lecteurs)
# et la range DANS le paragraphe qui la porte. Sans ces deux exclusions, son texte compte 4 fois.
IGNORES = (MC + "Fallback", W + "txbxContent")
# Une balise ou une icône est un IDENTIFIANT : {icone}, {icon:gold}, [degats], [/b], [color=#f00], <b>, </b>.
# Pas d'espace entre { } ni entre [ ] : « [la règle optionnelle] » est du texte ; « score < 3 et B > 5 »
# aussi (rien de collé après « < »). Sans ces bornes, du vrai texte sortait du compte « sans balises ».
BALISE = re.compile(r"\{/?[\w:.|#=-]{1,40}\}|</?[A-Za-z][\w-]*[^<>\n]{0,30}>|\[/?[\w:.|#=-]{1,40}\]")
# Formats de date prédéfinis d'Excel (14 = date courte, 22 = date et heure) ; les formats personnalisés
# sont reconnus à leur code (un « d » ou un « y » hors texte littéral).
DATES_EXCEL = {14, 15, 16, 17, 22}


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


def _styles_date(z, noms):
    """Les numéros de style (attribut s d'une cellule) dont le format de nombre est une date."""
    if "xl/styles.xml" not in noms:
        return set()
    styles = ET.fromstring(z.read("xl/styles.xml"))
    perso = {f.get("numFmtId"): f.get("formatCode", "") for f in styles.iter(S + "numFmt")}
    xfs = styles.find(S + "cellXfs")
    dates = set()
    for i, xf in enumerate(xfs if xfs is not None else []):
        n = xf.get("numFmtId", "0")
        code = re.sub(r'"[^"]*"|\[[^\]]*\]|\\.', "", perso.get(n, ""))   # sans texte littéral ni [couleur]
        if (n.isdigit() and int(n) in DATES_EXCEL) or re.search(r"[dy]", code, re.I):
            dates.add(str(i))
    return dates


def _date_excel(valeur, origine):
    """Numéro de série Excel → AAAA-MM-JJ (suivi de HH:MM s'il porte une heure)."""
    try:
        minutes = round(float(valeur) * 1440)
    except ValueError:
        return valeur
    jours, minutes = divmod(minutes, 1440)
    texte = (origine + dt.timedelta(days=jours)).isoformat()
    return texte + (f" {minutes // 60:02d}:{minutes % 60:02d}" if minutes else "")


def feuilles_xlsx(chemin):
    with zipfile.ZipFile(chemin) as z:
        noms = z.namelist()
        partages = []
        if "xl/sharedStrings.xml" in noms:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(S + "si"):
                partages.append("".join(t.text or "" for t in si.iter(S + "t")))
        dates = _styles_date(z, noms)
        classeur = ET.fromstring(z.read("xl/workbook.xml"))
        pr = classeur.find(S + "workbookPr")
        en_1904 = pr is not None and pr.get("date1904") in ("1", "true")
        origine = dt.date(1904, 1, 1) if en_1904 else dt.date(1899, 12, 30)
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
                        if val and typ in (None, "n") and c.get("s") in dates:
                            val = _date_excel(val, origine)
                    ligne.append(val)
                lignes.append(ligne)
            resultat[f.get("name")] = lignes
        return resultat


def _decoder(octets):
    """Le texte d'un fichier : UTF-16 si la marque d'un export Excel « Texte Unicode » est là, sinon
    UTF-8, Windows-1252, Latin-1 (qui lit tout octet). Un octet nul qui reste = fichier binaire ou
    UTF-16 sans marque : refusé avec un message clair, plutôt que lu comme un texte illisible."""
    if octets[:2] in (b"\xff\xfe", b"\xfe\xff"):   # UTF-16 : export Excel « Texte Unicode »
        texte = octets.decode("utf-16", errors="replace")
    else:
        for enc in ENCODAGES:
            try:
                texte = octets.decode(enc)
                break
            except UnicodeDecodeError:
                continue
    if "\x00" in texte:
        raise ValueError("fichier illisible comme texte (octets nuls) : fichier binaire, ou export « Texte "
                         "Unicode » sans marque d'encodage. Réenregistre-le en « CSV UTF-8 » ou en texte.")
    return texte


# Un nombre coupé en deux par le séparateur : après lui, un à trois chiffres suivis d'une espace
# (« 10,000 gold », « 1,5 PV »), d'un « % », d'un multiplicateur ou d'une dimension (« 12,5% », « 1,5x les
# dégâts », « 45,5×30,5 cm ») ou d'une fin de phrase (« par 1,5. », « 1,5) »). Une case « 2027 », « 20 » ou
# « 2.5 » ne l'est pas : c'est une vraie colonne de nombres.
NOMBRE_COUPE = re.compile(r"\d{1,3}(?:\s|%|[x×](?![^\W\d_])|[.…!?)](?!\d))")
# Le début de ce nombre, avant le séparateur : après une espace ou une ouverture, avec un signe ou un
# multiplicateur collé (« par 1 », « (x1 », « +1 », « ×1 ») ; en tête de case, un signe seulement.
# « C10 », « C_01 », « CARD-012 », « X1 » finissent un identifiant.
DEBUT_NOMBRE = re.compile(r"(?:^[+\-−×]?|[\s(\[«\"'“‘][+\-−×xX]?)\d+$")


def _coupe(avant, apres, strict=False, virgule=True):
    """Vrai si la limite entre deux cases tombe au milieu d'une phrase ou d'un nombre, et non entre deux
    colonnes. Une phrase : une espace suit la virgule ou le point-virgule (« une carte, puis ») ; un
    tableur exporté ne met jamais d'espace après son séparateur. Avec « ; », la tabulation ou « | »
    (virgule=False), c'est la seule règle : eux ne coupent jamais un nombre.
    Un nombre, à la virgule : DEBUT_NOMBRE avant la limite, NOMBRE_COUPE après (« par 1,5. », « (x1,5) »,
    « 10,000 gold »). Une case faite seulement de chiffres (« 3 » dans une colonne Coût, « 12 » en
    identifiant, « 2026 ») est une valeur de colonne, jamais le début d'un nombre coupé.
    En mode strict, une phrase qui finit par un nombre (DEBUT_NOMBRE), suivie d'une case d'un à trois
    chiffres, compte aussi (« Multipliez par 1,5 », « Dégâts ×1,5 » en fin de ligne)."""
    if apres[:1].isspace() and apres.strip():       # une case faite d'une seule espace n'est pas une suite
        return True
    if not virgule or avant.strip().isdigit():
        return False
    if DEBUT_NOMBRE.search(avant) and NOMBRE_COUPE.match(apres):
        return True
    return strict and bool(re.search(r"[^\W\d_]", avant) and DEBUT_NOMBRE.search(avant)
                           and re.fullmatch(r"\d{1,3}%?", apres))


def _ligne_coupee(ligne, strict=False, virgule=True):
    return any(_coupe(a, b, strict, virgule) for a, b in zip(ligne, ligne[1:]))


DIRECTIVE = re.compile(r"\ufeff?sep=(.)\r?\n")


def separateur(texte):
    """Le séparateur d'un CSV, ou None pour une seule colonne. Deux temps.
    1. Le candidat, comme en 3.0.0 : dans l'ordre « ; », tabulation, « , », « | », le premier qui partage en
       au moins deux cases au moins la moitié des 10 premières lignes non vides (lues comme un CSV, guillemets
       compris, là où la 3.0.0 cherchait seulement le caractère). Ce regard sur le haut du
       fichier suit Excel, qui enregistre par blocs de 16 lignes et n'écrit les séparateurs des colonnes
       vides de fin que là où un bloc s'en sert : un fichier « EN;FR » dont la colonne FR est encore vide plus
       bas, ou qui a une remarque dans une colonne sans titre, garde sa largeur en haut. Une première ligne
       « sep=; » (qu'Excel sait lire et écrire) donne directement le séparateur.
    2. Le veto, jugé sur l'ensemble du fichier et jamais sur une seule ligne : un texte français contient des
       virgules et des points-virgules, et « Piochez une carte, puis défaussez » n'est pas deux colonnes. Le
       candidat est refusé si la MOITIÉ AU MOINS des lignes qu'il partage les coupent :
         - en général, seule une phrase coupée compte (une espace après le séparateur : un tableur n'en met
           jamais, et il met entre guillemets toute case qui contient le séparateur). Une espace tapée par
           mégarde, un titre « Chapitre 2,45 cartes, » complété par l'export, un tableau sans en-tête
           « C1,Vol 1,120 » ou une colonne Coût suivie de « 2 dégâts » ne font donc rien refuser ;
         - quand la PREMIÈRE ligne est plus courte que le tableau (un titre court « Cartes validées », ou
           l'en-tête « FR » d'une seule colonne), UNE phrase coupée suffit, et un nombre coupé compte aussi
           (mode strict de _coupe : « Multipliez par 1 | 5 », « (x1 | 5) », « 12 | 5% ») : sous un en-tête
           d'une seule case, c'est la forme que prend une colonne de phrases. Les lignes se jugent à partir de
           la première qui a la largeur du tableau : le titre lui-même (« Cartes validées, version 2 ») ne
           compte pas.
    Limites (un fichier écrit à la main, ambigu par nature, ou un format de nombre d'Excel). « N'est pas lu
    avec son séparateur » veut dire : lu en une seule colonne, ou découpé par un autre séparateur.
      - un fichier dont moins de la moitié des 10 premières lignes ont le séparateur est lu en une seule
        colonne (comme en 3.0.0) ;
      - n'est pas lu avec son séparateur un tableau dont la moitié au moins des lignes ont une espace après
        un séparateur (« ID; EN; FR » sur chaque ligne, ou la seule ligne d'un tableau d'une ligne) ; et, sous
        un titre court écrit à la main (sans les séparateurs qu'un export ajoute), un tableau dont une ligne a
        une espace après un séparateur, ou, en virgules seulement, dont la moitié des lignes ont une case qui
        finit par un nombre après une espace (« Carte 12 », « Épée +1 ») suivie d'une case qui commence par
        un nombre ;
      - une colonne au format « Comptabilité » ou « Style milliers » (boutons € et 000 d'Excel, format monétaire
        de Numbers) : l'export écrit une espace devant chaque nombre, ce qui ressemble à une phrase coupée sur
        toutes les lignes. Le tableau n'est alors pas lu avec son séparateur. Remède : donner le classeur .xlsx
        lui-même (il est lu directement), ou mettre cette colonne au format Standard avant l'export. Le programme qui cherche une colonne s'arrête alors sur
        « introuvable » (refus bruyant) ; un programme qui lit tout le fichier (compter.py et typo.py sans
        --colonne, comparer_versions.py sans --cle, segments.py sans --col-en, lots.py, renvois.py,
        chercher.py, chercher_terme.py) lit les lignes entières, séparateurs compris, sans le signaler ;
      - une case qui contient le séparateur sans guillemets (« Défaussez ; puis rejouez. » dans un CSV en
        « ; » écrit à la main) est coupée là : Excel et Google Sheets mettent toujours ces guillemets ;
      - une remarque tapée dans une colonne sans en-tête, à droite d'une seule colonne de phrases : en haut
        du fichier (le premier bloc de 16 lignes d'un export Excel), elle peut faire lire le fichier en deux
        colonnes ; plus bas, le séparateur reste collé au texte des lignes de son bloc de 16 lignes, et les
        guillemets d'Excel restent sur tout le fichier (comme en 3.0.0) ;
      - est lue en colonnes une colonne de listes de mots sans espace après la virgule (« Vol,Portée »,
        « Gardien,Sentinelle »), avec ou sans en-tête ; et, sans en-tête, une colonne dont moins de la moitié
        des lignes partagées coupent une phrase (nombres décimaux « Multipliez par 1,5 », virgules sans
        espace « A3,B4 »). En français, une virgule de phrase ou de liste est suivie d'une espace ;
      - sous l'en-tête « FR », une colonne de phrases dont toutes les lignes coupées commencent par un nombre
        décimal (« 1,5 fois plus de dégâts. ») est lue en colonnes : « 1 » ressemble à un identifiant."""
    directive = DIRECTIVE.match(texte)
    if directive:
        return directive.group(1)       # « sep=; » en tête : Excel dit lui-même son séparateur
    for d in (";", "\t", ",", "|"):
        try:
            lignes = [l for l in csv.reader(io.StringIO(texte, newline=None), delimiter=d) if any(c.strip() for c in l)]
        except csv.Error:
            continue
        haut = lignes[:10]
        partages = [l for l in haut if len(l) >= 2]
        if not partages or len(partages) * 2 < len(haut):
            continue                    # le candidat de la 3.0.0 : la moitié des 10 premières lignes partagées
        n = Counter(len(l) for l in partages).most_common(1)[0][0]
        larges = [l for l in lignes if len(l) >= 2]
        if len(lignes[0]) < n:
            # titre court ou en-tête « FR » en tête : on juge à partir de la 1re ligne de la largeur du tableau
            # (le titre lui-même ne compte pas) ; une phrase coupée suffit, et un nombre coupé compte aussi
            debut = next(i for i, l in enumerate(lignes) if len(l) >= n)
            corps = [l for l in lignes[debut:] if len(l) >= 2]
            if any(_ligne_coupee(l, virgule=False) for l in corps) or \
                    sum(_ligne_coupee(l, strict=True, virgule=d == ",") for l in corps) * 2 >= len(corps):
                continue
        elif sum(_ligne_coupee(l, virgule=False) for l in larges) * 2 >= len(larges):
            continue                    # la moitié des lignes partagées coupent une phrase : une colonne de phrases
        return d
    return None


def hors_du_plugin(chemin):
    """Toute cible d'écriture passe ici. Le dossier du plugin AURA (celui des programmes) n'est pas chez
    Hervé : un fichier écrit là se perd à la synchronisation suivante, sans que personne le voie. Refus,
    code 2 (règle « Écrire une commande » du skill noyau). Renvoie le chemin tel quel s'il est ailleurs."""
    cible = Path(chemin).resolve()
    racine = next((d for d in Path(__file__).resolve().parents if (d / ".claude-plugin" / "plugin.json").is_file()), None)
    if racine and (cible == racine or racine in cible.parents):
        print(f"REFUS — « {chemin} » tombe dans le dossier du plugin AURA ({racine}) : un fichier écrit là se perd. "
              "Écris sous HERVÉ WORLD, avec un chemin complet (règle « Écrire une commande » du skill noyau).")
        raise SystemExit(2)
    return chemin


def lignes_csv(chemin):
    """Les lignes d'un CSV, chacune en liste de cases. Sans séparateur (une seule colonne), le fichier est
    quand même lu comme un CSV, pour retirer les guillemets qu'Excel ou Google Sheets mettent autour
    d'une case qui contient une virgule ; s'il n'est pas un CSV bien formé (un guillemet ouvert en début
    de phrase, par exemple), chaque ligne est gardée telle quelle, guillemets compris."""
    texte = _decoder(Path(chemin).read_bytes())
    d = separateur(texte)
    if d is not None:
        return [l for l in csv.reader(io.StringIO(texte, newline=None), delimiter=d)]
    if "\x1f" not in texte:          # un séparateur absent du texte : seuls les guillemets sont lus
        try:
            return [l for l in csv.reader(io.StringIO(texte, newline=None), delimiter="\x1f", strict=True)]
        except csv.Error:
            pass
    return [[l] for l in texte.splitlines()]


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
