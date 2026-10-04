"""Briques communes aux scripts du skill gestion-gamme (bibliothèque standard uniquement).

Chaque règle n'est écrite qu'ici : normalisation des textes, clé de comparaison d'un titre,
lecture d'un tableau (.xlsx/.csv/.tsv) avec recherche de la ligne d'en-tête, mémoire de traduction.
La lecture des fichiers passe par lecture.py (copie identique, partagée entre les skills).
"""
import difflib
import hashlib
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "`": "'", "´": "'"})


def arret(message):
    """Erreur d'usage : message clair, code de sortie 2."""
    print(message, file=sys.stderr)
    sys.exit(2)


def normaliser(texte, strict=False):
    """NFC + espaces (y compris insécables) réduites à une seule. --strict : texte brut."""
    if strict:
        return texte
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", texte)).strip()


def cle_titre(texte):
    """Clé d'égalité de deux titres : casse, apostrophes et ponctuation finale ignorées."""
    t = normaliser(texte).translate(APOSTROPHES).casefold()
    return re.sub(r"[\s.:;!?…]+$", "", t)


def sans_accents(texte):
    return "".join(c for c in unicodedata.normalize("NFD", texte) if not unicodedata.combining(c))


def raccourcir(texte, garde=50):
    """Réduit une longue zone identique pour que les changements se voient."""
    if len(texte) <= 2 * garde + 20:
        return texte
    return texte[:garde] + " … " + texte[-garde:]


def diff_mots(a, b):
    """« [-retiré-]{+ajouté+} » mot à mot entre deux textes."""
    ta = re.findall(r"\w+|\s+|[^\w\s]", a)
    tb = re.findall(r"\w+|\s+|[^\w\s]", b)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(raccourcir("".join(ta[i1:i2])))
        if op in ("delete", "replace"):
            out.append("[-" + "".join(ta[i1:i2]) + "-]")
        if op in ("insert", "replace"):
            out.append("{+" + "".join(tb[j1:j2]) + "+}")
    return "".join(out)


def ressemblance(a, b, seuil=0.0):
    """Ratio difflib de 0 à 1 ; renvoie 0 dès que les filtres rapides prouvent qu'on est sous le seuil."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    if sm.real_quick_ratio() < seuil or sm.quick_ratio() < seuil:
        return 0.0
    return sm.ratio()


def empreinte(chemin):
    return hashlib.sha256(Path(chemin).read_bytes()).hexdigest()


# ------------------------------------------------------------------ fichiers produits
def sortie_libre(chemin):
    """Un rapport ou un fichier produit ne remplace jamais un fichier existant (Livrables/ est la
    mémoire d'Hervé) : s'il existe déjà, arrêt avec le code 2, avant tout calcul."""
    if chemin:
        lecture.hors_du_plugin(chemin)
    if chemin and Path(chemin).exists():
        arret(f"{chemin} existe déjà : choisis un autre nom (on n'écrase jamais un fichier).")
    return chemin


def ecrire_sortie(chemin, texte):
    """Écrit un fichier NOUVEAU (mode « x » : refus si le fichier est apparu entre-temps)."""
    sortie_libre(chemin)
    try:
        with open(chemin, "x", encoding="utf-8") as f:
            f.write(texte)
    except FileExistsError:
        arret(f"{chemin} existe déjà : choisis un autre nom (on n'écrase jamais un fichier).")


# ------------------------------------------------------------------ tableaux
def colonne(entetes, spec, corps=None):
    """Index d'une colonne : nom d'en-tête (casse ignorée), lettre (A, B…) ou numéro (1, 2…).

    Une lettre ou un numéro n'est accepté que s'il désigne une colonne du tableau lu qui porte un
    en-tête ou au moins une valeur (`corps` : lignes [(numéro, cellules)]). Sinon, arrêt : un nom
    d'en-tête mal tapé (« FR », « ID », « TX ») ne devient jamais, en silence, une colonne Excel vide.
    """
    bas = [e.strip().lower() for e in entetes]
    s = spec.strip()
    if s.lower() in bas:
        return bas.index(s.lower())
    lus = ", ".join(e for e in entetes if e) or "aucun"
    i = None
    if re.fullmatch(r"[A-Za-z]{1,3}", s):
        n = 0
        for c in s.upper():
            n = n * 26 + ord(c) - 64
        i = n - 1
    elif s.isdigit() and int(s) >= 1:
        i = int(s) - 1
    if i is None:
        arret(f"Colonne « {spec} » introuvable. En-têtes lus : {lus}")
    porte = (i < len(entetes) and entetes[i].strip()) or any(cellule(l, i) for _, l in corps or [])
    if not porte:
        arret(f"Colonne « {spec} » introuvable : ce n'est pas un en-tête du tableau, et la colonne n° {i + 1} "
              f"qu'elle désignerait comme lettre ou numéro est vide ou hors du tableau. En-têtes lus : {lus}. "
              "Donne le nom exact de l'en-tête.")
    return i


def deviner_colonne(entetes, langue):
    """Colonne EN ou FR reconnue par son en-tête (« EN », « Terme (EN) », « Titre FR »…), sinon None."""
    for k, e in enumerate(entetes):
        b = e.strip().lower()
        if b == langue or f"({langue})" in b or b.endswith(" " + langue) or b.startswith(langue + " "):
            return k
    return None


def lire_table(chemin, feuille=None, reperes=None):
    """(en-têtes, [(numéro de ligne, cellules)]) d'un .xlsx/.csv/.tsv.

    La ligne d'en-tête est la première (parmi les 20 premières lignes non vides) qui contient un des
    noms de `reperes` ; à défaut, la première qui a au moins deux cellules remplies. Un titre placé
    au-dessus du tableau est donc sauté.
    """
    ext = Path(chemin).suffix.lower()
    if ext == ".xlsx":
        f = lecture.feuilles_xlsx(chemin)
        if feuille:
            if feuille not in f:
                arret(f"Onglet « {feuille} » absent de {Path(chemin).name}. Onglets : {', '.join(f)}")
            lignes = f[feuille]
        else:
            lignes = next((v for v in f.values() if any(any(str(c).strip() for c in l) for l in v)), [])
    elif ext in (".csv", ".tsv"):
        lignes = lecture.lignes_csv(chemin)
    else:
        arret(f"{Path(chemin).name} : un tableau .xlsx, .csv ou .tsv est attendu ici.")
    numeros = [k for k, l in enumerate(lignes, 1) if any(str(c).strip() for c in l)]
    if not numeros:
        arret(f"{Path(chemin).name} : aucune ligne lue.")
    cherches = [r.strip().lower() for r in (reperes or []) if r]
    debut = None
    for pos, k in enumerate(numeros[:20]):
        cellules = [str(c).strip().lower() for c in lignes[k - 1]]
        if any(r in cellules for r in cherches):
            debut = pos
            break
    if debut is None:
        debut = next((pos for pos, k in enumerate(numeros[:20])
                      if sum(1 for c in lignes[k - 1] if str(c).strip()) >= 2), 0)
    tete = [str(c).strip() for c in lignes[numeros[debut] - 1]]
    corps = [(k, [str(c) for c in lignes[k - 1]]) for k in numeros[debut + 1:]]
    return tete, corps


def cellule(ligne, i):
    return ligne[i].strip() if i is not None and i < len(ligne) else ""


# ------------------------------------------------------------------ mémoire de traduction
def charger_memoire(chemins):
    """CSV EN;FR;produit;date → {texte EN normalisé: [(FR, produit, date, EN d'origine), ...]}.

    Avec une ligne d'en-tête EN/FR, les colonnes sont trouvées par leur nom ; sans en-tête, l'ordre
    EN, FR, produit, date est attendu.
    """
    memo = defaultdict(list)
    for chemin in chemins or []:
        lignes = [l for l in lecture.lignes_csv(chemin) if any(c.strip() for c in l)]
        if not lignes:
            continue
        tete = [c.strip().lower() for c in lignes[0]]
        if "en" in tete and "fr" in tete:
            i_en, i_fr = tete.index("en"), tete.index("fr")
            i_pr = tete.index("produit") if "produit" in tete else None
            i_da = tete.index("date") if "date" in tete else None
            lignes = lignes[1:]
        else:
            i_en, i_fr, i_pr, i_da = 0, 1, 2, 3
        for l in lignes:
            en, fr_ = cellule(l, i_en), cellule(l, i_fr)
            if en and fr_:
                memo[normaliser(en)].append((fr_, cellule(l, i_pr), cellule(l, i_da), en))
    return memo


def traductions_distinctes(entrees):
    vues, out = set(), []
    for fr_, pr, da, *_ in entrees:
        if fr_ not in vues:
            vues.add(fr_)
            out.append((fr_, pr, da))
    return out


def decrire_traductions(entrees):
    d = traductions_distinctes(entrees)
    texte = " ; ".join(f"« {f} » ({p or 'produit ?'}, {a or 'date ?'})" for f, p, a in d)
    return ("PLUSIEURS traductions existantes, à trancher : " + texte) if len(d) > 1 else texte
