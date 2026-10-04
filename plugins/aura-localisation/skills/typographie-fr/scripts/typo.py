#!/usr/bin/env python3
"""Contrôle de la typographie française d'un texte traduit (charte : references/charte.md).

Usage :
  python3 typo.py FICHIER [--colonne NOM] [--corriger] [--max N]
  python3 typo.py --auto-test

FICHIER : .docx, .xlsx, .csv, .tsv, .txt, .md
--colonne NOM : pour un tableur, ne contrôler que la colonne dont l'en-tête est NOM (ex. FR)
--corriger    : pour .txt/.md/.csv/.tsv seulement, écrit une COPIE corrigée « <nom>_typo<ext> » à côté
                (les règles sûres seulement ; l'original n'est jamais modifié). Un tableur (.csv, .tsv)
                exige toujours --colonne, et seule cette colonne est corrigée : la source anglaise, les
                identifiants, le titre et les en-têtes restent tels quels.
--auto-test   : passe le contrôle sur des fautes glissées exprès (il doit toutes les trouver), sur des
                phrases propres (il ne doit rien signaler) et sur des fichiers piégés

Chaque règle porte l'identifiant de la charte (T01…). Les comptes sont exacts : tout le fichier est lu.
Une adresse web, un e-mail et une entité HTML (&nbsp;) ne sont ni contrôlés ni corrigés.
"""
import argparse, csv, io, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

NB = "\u00a0\u202f"           # espaces insécables admises : normale [U+00A0], fine [U+202F]
E_INV = "[" + NB + "]"
LETTRE = r"[^\W\d_]"          # une lettre, accentuée ou non, Œ et œ compris
# Jamais contrôlé ni corrigé : une adresse web (sans la ponctuation qui la suit : « exemple.fr ! »),
# un e-mail, une entité HTML (« &nbsp; »), une balise ou une icône (motif BALISE du lecteur : « {icon:gold} »)
PROTEGE = re.compile(r"(?:https?://|www\.)\S*[^\s.,;:!?)\]»\"']|[\w.+-]+@[\w-]+(?:\.[\w-]+)+|&#?\w+;|"
                     + lecture.BALISE.pattern)

# Mots courants qui prennent une majuscule accentuée en tête (T08). Liste volontairement prudente.
MAJ_ACCENT = {
    "etat": "État", "etats": "États", "etape": "Étape", "etapes": "Étapes", "egalement": "Également",
    "element": "Élément", "elements": "Éléments", "equipe": "Équipe", "equipement": "Équipement",
    "epuise": "Épuisé", "epuisee": "Épuisée", "epuisez": "Épuisez", "evenement": "Événement",
    "evenements": "Événements", "ecran": "Écran", "echange": "Échange", "echangez": "Échangez",
    "eliminez": "Éliminez", "elimine": "Éliminé", "evitez": "Évitez", "etoile": "Étoile",
    "eclat": "Éclat", "energie": "Énergie", "enigme": "Énigme", "epee": "Épée", "eveil": "Éveil",
    "a": "À", "etre": "Être", "ete": "Été",
}

# Chaque règle : (id, libellé, motif, remplacement sûr ou None)
REGLES = [
    ("T01", "espace insécable avant ; ! ?",            # « ?! » : une seule alerte pour le groupe
     re.compile(r"(?:(?<=\S) |(?<=[^\s;!?]))[;!?]+"), None),
    ("T02", "espace insécable normale avant :",         # l'heure ou un rapport (10:30, 3:1) n'est pas visé
     re.compile(r"(?:(?<=\S)[ \u202f]|(?<=\S)(?!(?<=\d):\d)):(?!//)"), None),
    ("T03", "guillemets français « » avec espaces insécables",
     re.compile(r"\"|[“”„]|«(?!" + E_INV + r")|(?<!" + E_INV + r")»"), None),
    ("T04", "apostrophe typographique ’",
     re.compile(r"(?<=" + LETTRE + r")'(?=" + LETTRE + r")"), "’"),
    ("T05", "points de suspension en un caractère …", re.compile(r"\.\.\."), "…"),
    ("T06", "pas d'espace avant , et .", re.compile(r"(?<=\S)[ " + NB + r"]+(?=[,.](?!\.))"), ""),
    ("T07", "pas de double espace", re.compile(r"(?<=\S) {2,}(?=\S)"), " "),
    ("T08", "majuscule accentuée", re.compile(r"\b(E[a-zé]+|A)\b"), None),
    ("T09", "ordinal abrégé (1er, 1re, 2e)",
     re.compile(r"\b\d+(?:ère|ere|ième|ieme|ème|eme|è|nd|nde)s?\b", re.I), None),
    ("T10", "nombres : milliers à partir de 10 000, virgule décimale",
     re.compile(r"(?<![\d.,/#+\w])[1-9]\d{4,}(?![\d\w])"      # 10000
                r"|\b\d{1,3}(?:[,.]\d{3})+\b(?![.,]?\d)"      # 10,000 · 10.000
                r"|\b\d{1,3}(?: \d{3})+\b"                    # 10 000 (espace ordinaire)
                r"|(?<![\w.,])\d+\.\d+(?!\.?\d)"), None),      # 2.5 (point décimal anglais)
    ("T11", "incise : tiret demi-cadratin, insécable à l'intérieur",   # voir candidats_t11
     re.compile(r"(?<=\w)[ " + NB + r"]-[ " + NB + r"](?=\w)"), None),
    ("T12", "espace insécable après n° et avant une unité",
     re.compile(r"n° ?(?=\d)|(?<=\d) ?(?=[%€]|(?:PV|PA|PM|cm|mm|kg|g)\b)"), None),
]
IDS = [r[0] for r in REGLES]
REGLES_PAR_ID = {r[0]: r[2] for r in REGLES}
# Un tiret d'incise : demi-cadratin ou cadratin, une espace (ordinaire ou insécable) de chaque côté
TIRET = re.compile(r"(?<=\S)[ " + NB + r"][–—](?=[ " + NB + r"]\S)")
FIN_PHRASE = re.compile(r"[.!?…](?=\s|$)|\n")
# Les mots qui annoncent un numéro de règle, de section ou de version (T10 ne les vise pas)
RENVOI = re.compile(r"(?<!\w)(?:règles?|regles?|sections?|chapitres?|parties?|paragraphes?|§|voir|versions?"
                    r"|étapes?|etapes?|pages?|p\.)[ " + NB + r"]*$", re.I)


class Refus(Exception):
    """Une demande que le programme refuse, avec la raison à montrer telle quelle."""


def zones_protegees(texte):
    return [(m.start(), m.end()) for m in PROTEGE.finditer(texte)]


def _dans(zones, pos):
    return any(a <= pos < b for a, b in zones)


def _laisse_passer(rid, m, texte):
    """Les cas qu'une règle laisse passer exprès (voir la charte)."""
    if rid == "T03" and m.group(0) in "“”„":     # citation dans une citation : « … “…” … »
        avant = texte[:m.start()]
        return avant.count("«") > avant.count("»")
    if rid == "T10":
        if re.fullmatch(r"\d{5}", m.group(0)):    # code postal suivi de la ville : « 75011 Paris »
            return bool(re.match(r" [A-ZÀ-Ý][a-zà-ÿ]", texte[m.end():]))
        if re.fullmatch(r"\d+\.\d+", m.group(0)):  # numéro de règle ou de version : « règle 3.2 », « version 1.5 »
            return bool(RENVOI.search(texte[:m.start()]))
    return False


def candidats_t11(texte):
    """T11 : un trait d'union pris pour un tiret ; et, dans une incise (deux tirets espacés dans la même
    phrase), une espace ordinaire du côté intérieur : après le tiret ouvrant, avant le tiret fermant.
    Un tiret espacé SEUL dans sa phrase n'est pas contrôlé : séparateur de titre (« Étape 1 – Mise en
    place ») ou incise qui se ferme avec la phrase, le programme ne peut pas savoir lequel."""
    for m in REGLES_PAR_ID["T11"].finditer(texte):
        yield m.start(), m.end()
    par_phrase = {}
    for m in TIRET.finditer(texte):
        par_phrase.setdefault(len(FIN_PHRASE.findall(texte, 0, m.start())), []).append(m)
    for tirets in par_phrase.values():
        for k, m in enumerate(tirets[:len(tirets) // 2 * 2]):
            interieur = texte[m.end()] if k % 2 == 0 else texte[m.start()]
            if interieur not in NB:
                yield m.start(), m.end()


def candidats_t08(texte):
    for m in re.finditer(r"(?<![\w])(E[A-ZÉ]+|[EA][a-zé]*)\b", texte):
        mot = m.group(1)
        cle = mot.lower().replace("é", "e")
        if mot == "A":
            # « A » en tête de phrase et suivi d'un mot (« A la fin », « A LA FIN ») = « À » ;
            # pas « A : la face A », ni « A » qui désigne une face, un joueur ou une colonne (« A et B »)
            avant = texte[:m.start()].rstrip()
            suivi = re.match(r" (?!(?:et|ou) )(?:[a-zà-ÿ]|[A-ZÀ-Ý]{2,}\b)", texte[m.end():])   # pas « A et B »
            if (avant == "" or avant[-1] in ".!?:»\n") and suivi:
                yield m.start(), mot, "À"
        elif cle in MAJ_ACCENT and mot[0] == "E":
            juste = MAJ_ACCENT[cle].upper() if mot.isupper() else MAJ_ACCENT[cle]
            if mot != juste:
                yield m.start(), mot, juste


def controler_texte(texte):
    """Liste de (id, position, extrait, suggestion)."""
    zones = zones_protegees(texte)
    trouve = []
    for rid, _lib, motif, remp in REGLES:
        if rid == "T08":
            for pos, mot, sugg in candidats_t08(texte):
                if not _dans(zones, pos):
                    trouve.append((rid, pos, mot, sugg))
            continue
        if rid == "T11":
            for debut, fin in candidats_t11(texte):
                if not _dans(zones, debut):
                    trouve.append((rid, debut, texte[max(0, debut - 15):fin + 15].replace("\n", " "), None))
            continue
        for m in motif.finditer(texte):
            if _dans(zones, m.start()) or _laisse_passer(rid, m, texte):
                continue
            debut = max(0, m.start() - 15)
            extrait = texte[debut:m.end() + 15].replace("\n", " ")
            trouve.append((rid, m.start(), extrait, remp))
    return trouve


def corriger_texte(texte):
    """Les règles sûres (celles qui ont un remplacement), hors adresses web, e-mails et entités."""
    for _rid, _lib, motif, remp in REGLES:
        if remp is not None:
            zones = zones_protegees(texte)
            texte = motif.sub(lambda m: m.group(0) if _dans(zones, m.start()) else remp, texte)
    return texte


def _entete(lignes, nom_col):
    """(numéro de la ligne d'en-tête, index de la colonne) ou None."""
    for i, ligne in enumerate(lignes):
        norm = [str(c).strip().lower() for c in ligne]
        if nom_col.lower() in norm:
            return i, norm.index(nom_col.lower())
    return None


def _tableur(p):
    if p.suffix.lower() == ".xlsx":
        return lecture.feuilles_xlsx(p)
    return {"": lecture.lignes_csv(p)}


def colonne_filtree(chemin, nom_col):
    p = Path(chemin)
    feuilles = _tableur(p)
    out, vue = [], False
    for feuille, lignes in feuilles.items():
        pos = _entete(lignes, nom_col)
        if pos is None:
            continue
        vue = True
        i, idx = pos
        for j, l2 in enumerate(lignes[i + 1:], i + 2):
            if idx < len(l2) and str(l2[idx]).strip():
                out.append((f"{feuille}!L{j}" if feuille else f"L{j}", str(l2[idx])))
    if not vue:
        lues = []
        for feuille, lignes in feuilles.items():
            premiere = next((l for l in lignes if any(str(c).strip() for c in l)), [])
            cases = ", ".join(str(c).strip() for c in premiere if str(c).strip())[:120]
            lues.append(f"{feuille or p.name} : {cases or '(vide)'}")
        ou = f"aucun des {len(feuilles)} onglets n'a cet en-tête" if len(feuilles) > 1 else "absente des en-têtes"
        raise SystemExit(f"Colonne « {nom_col} » introuvable : {ou}. Premières lignes lues — " + " ; ".join(lues))
    return out


def segments_du_fichier(p, colonne):
    """Les segments à contrôler. Zéro segment lu n'est jamais un « 0 alerte » : c'est un arrêt."""
    try:
        segments = colonne_filtree(p, colonne) if colonne else lecture.textes(p)
    except ValueError as e:                       # format non pris en charge, octets nuls
        raise SystemExit(f"{p.name} : {e}")
    except Exception as e:                        # fichier absent, classeur ou Word abîmé
        raise SystemExit(f"{p.name} : lecture impossible ({e}). Rien n'a été contrôlé.")
    if not segments:
        quoi = f"la colonne « {colonne} » est vide" if colonne else "le fichier ne contient aucun texte lisible"
        raise SystemExit(f"Typographie — {p.name} — 0 segment lu : {quoi}. Rien n'a été contrôlé.")
    return segments


def refus_corriger(p, colonne):
    """La raison de refuser --corriger avant de lire quoi que ce soit, ou None."""
    ext = p.suffix.lower()
    if ext not in (".txt", ".md", ".csv", ".tsv"):
        return ("--corriger : seulement pour .txt/.md/.csv/.tsv ; pour Word et Excel, voir la charte "
                "(Rechercher/Remplacer sur une copie).")
    if ext in (".csv", ".tsv") and not colonne:
        # Toujours, même si le fichier semble n'avoir qu'une colonne : la détection des colonnes peut se
        # tromper (titre au-dessus, ligne irrégulière), et une erreur réécrirait la source anglaise.
        return ("--corriger sur un tableur (.csv, .tsv) : donne la colonne à corriger avec --colonne "
                "(ex. --colonne FR), même s'il n'a qu'une colonne. Sans elle, la source anglaise, les "
                "identifiants et les en-têtes seraient modifiés aussi. Aucune copie écrite.")
    sortie = Path(lecture.hors_du_plugin(p.with_name(p.stem + "_typo" + p.suffix)))
    if sortie.exists():
        return f"{sortie.name} existe déjà : je n'écrase pas. Renomme-le ou supprime-le d'abord."
    return None


def corriger_fichier(p, colonne):
    """Écrit la copie « <nom>_typo<ext> » ; renvoie (chemin de la copie, ce qui a été corrigé)."""
    refus = refus_corriger(p, colonne)
    if refus:
        raise Refus(refus)
    sortie = Path(lecture.hors_du_plugin(p.with_name(p.stem + "_typo" + p.suffix)))
    texte = lecture._decoder(p.read_bytes())
    if p.suffix.lower() in (".txt", ".md"):
        sortie.write_text(corriger_texte(texte), encoding="utf-8")
        return sortie, "tout le texte"
    introuvable = Refus(f"Colonne « {colonne} » introuvable dans les en-têtes. Aucune copie écrite.")
    d = lecture.separateur(texte)
    if d is None:
        # Une seule colonne : on corrige le texte SOUS la ligne d'en-tête, tel qu'il est écrit (guillemets,
        # retours à la ligne) ; le titre et l'en-tête restent tels quels.
        brutes = texte.splitlines(keepends=True)
        j = next((j for j, l in enumerate(brutes) if l.strip().strip('"').strip().lower() == colonne.lower()), None)
        if j is None:
            raise introuvable
        sortie.write_text("".join(brutes[:j + 1]) + corriger_texte("".join(brutes[j + 1:])), encoding="utf-8-sig")
        return sortie, f"colonne « {colonne} » seulement"
    lignes = lecture.lignes_csv(p)
    pos = _entete(lignes, colonne)
    if pos is None:
        raise introuvable
    i, k = pos
    for ligne in lignes[i + 1:]:
        if k < len(ligne):
            ligne[k] = corriger_texte(ligne[k])
    tampon = io.StringIO()
    csv.writer(tampon, delimiter=d, lineterminator="\r\n" if "\r\n" in texte else "\n").writerows(lignes)
    sortie.write_text(tampon.getvalue(), encoding="utf-8-sig")   # la marque UTF-8 : Excel lit les accents
    return sortie, f"colonne « {colonne} » seulement"


def rapport(segments, maxi):
    total = Counter()
    lignes = []
    for repere, texte in segments:
        for rid, _pos, extrait, sugg in controler_texte(texte):
            total[rid] += 1
            if sum(total.values()) <= maxi:
                s = f" → {sugg!r}" if sugg not in (None, "") else ""
                lignes.append(f"  {repere}  [{rid}] « {extrait.strip()} »{s}")
    return total, lignes


# ------------------------------------------------------------------ auto-test
# Une faute par phrase, et la règle qui doit la voir
FAUTES = [
    ("1ère manche", "T09"), ("la 3èmes vague", "T09"), ("ETAPE 1", "T08"), ("A la fin du tour", "T08"),
    ("Il dit “Éclat”", "T03"), ("Gagnez 50 % de bonus", "T12"), ("Gagnez 50% de bonus", "T12"),
    ("10 € de plus", "T12"), ("Placez 10 000 pièces.", "T10"), ("Étape 2: piochez", "T02"),
    ("l'Œil", "T04"), ("Cette carte – si elle – reste", "T11"), ("Quoi?!", "T01"),
    ("Gagnez 2.5\u00a0PV.", "T10"), ("Le jeton vaut 1.5 point.", "T10"), ("Placez 10.000 pièces.", "T10"),
    ("Effet\u202f: piochez", "T02"), ("Cette carte\u00a0– si elle est épuisée\u00a0– reste", "T11"),
    ("Voir https://exemple.fr! Puis jouez.", "T01"),
]
# Des phrases justes, où le contrôle ne doit RIEN signaler
PROPRES = [
    "1re manche", "la 3es vague", "ÉTAPE 1", "Il dit «\u00a0Prends “Éclat” ici\u00a0»",
    "Gagnez 50\u00a0% de bonus", "10\u00a0€ de plus", "Placez 10\u202f000 pièces.", "Étape 2\u00a0: piochez",
    "l’Œil", "Cette carte –\u00a0si elle\u00a0– reste", "Quoi\u202f?!", "Rendez-vous à 10:30.",
    "Voir https://exemple.fr/regles?langue=fr pour la suite.", "Écris à contact@exemple.fr.", "&nbsp;",
    "A\u00a0: description de la face A.", "75011 Paris", "réf.\u00a0012345",
    "Étape 1 – Mise en place", "Mise en place – 2 joueurs", "– Piochez une carte.", "Cartes 12–24, saison 2026–2027",
    "Cette carte –\u00a0si elle est épuisée\u00a0– reste. Étape 2 – Combat", "Voir la règle 3.2.1 et la version 1.0.2.",
    "Voir la règle 3.2 pour la suite.", "Le jeton vaut 1,5\u00a0PV.", "Gagnez 1\u00a0{icon:gold}.",
    "A et B échangent leurs cartes.", "Voir www.exemple.fr.",
]


def _xlsx_essai(chemin, feuilles):
    """Un classeur minimal : {onglet: [[cellule, …], …]} ; une cellule ("date", n) porte le numéro de
    série n au format de date courte d'Excel (format 14)."""
    import zipfile
    from xml.sax.saxutils import escape, quoteattr
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    nsr = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr("xl/workbook.xml", f"<workbook {ns} {nsr}><sheets>" + "".join(
            f'<sheet name={quoteattr(nom)} sheetId="{i}" r:id="rId{i}"/>' for i, nom in enumerate(feuilles, 1))
            + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(
                       f'<Relationship Id="rId{i}" Type="worksheet" Target="worksheets/sheet{i}.xml"/>'
                       for i in range(1, len(feuilles) + 1)) + "</Relationships>")
        z.writestr("xl/styles.xml", f'<styleSheet {ns}><cellXfs count="2"><xf numFmtId="0"/>'
                                    '<xf numFmtId="14"/></cellXfs></styleSheet>')
        for i, lignes in enumerate(feuilles.values(), 1):
            rangs = []
            for r, ligne in enumerate(lignes, 1):
                cases = []
                for c, val in enumerate(ligne):
                    ref = f"{chr(65 + c)}{r}"
                    if isinstance(val, tuple):
                        cases.append(f'<c r="{ref}" s="1"><v>{val[1]}</v></c>')
                    else:
                        cases.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(val)}</t></is></c>')
                rangs.append(f'<row r="{r}">' + "".join(cases) + "</row>")
            z.writestr(f"xl/worksheets/sheet{i}.xml", f"<worksheet {ns}><sheetData>" + "".join(rangs)
                       + "</sheetData></worksheet>")


def _arret(fonction, *args):
    """Le message d'arrêt de la fonction, ou None si elle ne s'arrête pas."""
    try:
        fonction(*args)
    except (SystemExit, Refus) as e:
        return str(e)
    return None


def auto_test_fichiers():
    """Les fichiers piégés : (nombre de fichiers, liste des échecs, vide si tout va bien)."""
    import tempfile
    echecs = []
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)

        def essai(nom, contenu):
            f = d / nom
            f.write_text(contenu, encoding="utf-8")
            return f

        def refuse_sans_colonne(f, quoi):
            """--corriger sans --colonne doit être refusé ; une copie écrite quand même est une faute, retirée
            ensuite pour ne pas fausser l'essai suivant."""
            if not _arret(corriger_fichier, f, None):
                echecs.append(f"{quoi} : --corriger sans --colonne doit être refusé")
                f.with_name(f.stem + "_typo" + f.suffix).unlink(missing_ok=True)

        def corrige_seulement_fr(f, attendu, quoi):
            """--corriger sans --colonne refusé ; avec --colonne FR, la copie lue doit valoir `attendu`."""
            refuse_sans_colonne(f, quoi)
            try:
                lu = lecture.lignes_csv(corriger_fichier(f, "FR")[0])
            except Refus as e:
                lu = str(e)
            if lu != attendu:
                echecs.append(f"{quoi}, --corriger --colonne FR : obtenu {lu}, attendu {attendu}")

        # 1. CSV bilingue : seule la colonne FR change ; l'anglais et l'adresse web restent
        corrige_seulement_fr(
            essai("bilingue.csv", "ID;EN;FR\nC1;Don't   draw...;N'en piochez pas...\n"
                                  "C3;See https://ex.com/a...b;Voir https://ex.com/a...b\n"),
            [["ID", "EN", "FR"], ["C1", "Don't   draw...", "N’en piochez pas…"],
             ["C3", "See https://ex.com/a...b", "Voir https://ex.com/a...b"]], "CSV bilingue")
        # 2. classeur de deux onglets sans la colonne demandée : arrêt, jamais « 0 alerte »
        f = d / "deux_onglets.xlsx"
        _xlsx_essai(f, {"Cartes": [["Réf.", "Texte FR"], ["C1", "Piochez."]], "Notes": [["Note"], ["x"]]})
        if not _arret(segments_du_fichier, f, "FR"):
            echecs.append("colonne absente de tous les onglets : arrêt attendu")
        # 3. colonne présente mais vide : 0 segment lu = arrêt
        f = d / "vide.xlsx"
        _xlsx_essai(f, {"Cartes": [["ID", "FR"], ["C1", ""]]})
        if not _arret(segments_du_fichier, f, "FR"):
            echecs.append("0 segment lu : arrêt attendu, pas « 0 alerte »")
        # 4. CSV d'une seule colonne : le texte après la virgule (phrase ou nombre décimal) n'est pas perdu ;
        #    les guillemets qu'Excel met autour d'une case à virgule sont retirés
        for nom, contenu, attendu in (
                ("une_colonne.csv", "FR\nPiochez une carte, puis défaussez-en une!\nGagnez 3 PV, puis piochez...\n",
                 ["Piochez une carte, puis défaussez-en une!", "Gagnez 3 PV, puis piochez..."]),
                ("decimales.csv", "FR\nLe jeton vaut 1,5 PV.\nGagnez 2,5 PV.\n", ["Le jeton vaut 1,5 PV.", "Gagnez 2,5 PV."]),
                ("guillemets.csv", '"FR"\n"Piochez une carte, puis défaussez-en une !"\n"Gagnez 3 PV, puis piochez."\n',
                 ["Piochez une carte, puis défaussez-en une !", "Gagnez 3 PV, puis piochez."]),
                # la première ligne à virgule n'a pas d'espace après sa virgule (décimale, mots collés) :
                # elle ne doit pas faire passer la colonne de phrases pour un tableau
                ("degats.csv", "FR\nLes dégâts sont multipliés par 1,5.\nPiochez une carte, puis défaussez-en une!\n"
                               "Gagnez 2 PV, puis piochez...\n",
                 ["Les dégâts sont multipliés par 1,5.", "Piochez une carte, puis défaussez-en une!",
                  "Gagnez 2 PV, puis piochez..."]),
                ("mots_colles.csv", "FR\nGardien,Sentinelle\nPiochez une carte, puis défaussez-en une!\n",
                 ["Gardien,Sentinelle", "Piochez une carte, puis défaussez-en une!"]),
                ("cle_puis_decimale.csv", "FR\nGardien,Sentinelle\nMultipliez par 1,5\n",
                 ["Gardien,Sentinelle", "Multipliez par 1,5"]),
                ("decimales_sans_point.csv", "FR\nMultipliez par 1,5\nDivisez par 2,5\n",
                 ["Multipliez par 1,5", "Divisez par 2,5"]),
                # la phrase coupée n'arrive qu'après la 20e ligne : tout le fichier est examiné
                ("longue.csv", "FR\n" + "Gardien,Sentinelle\n" * 20 + "Piochez une carte, puis défaussez.\n",
                 ["Gardien,Sentinelle"] * 20 + ["Piochez une carte, puis défaussez."])):
            try:
                segs = [t for _, t in segments_du_fichier(essai(nom, contenu), "FR")]
            except SystemExit as e:
                segs = str(e)
            if segs != attendu:
                echecs.append(f"CSV d'une colonne ({nom}) : obtenu {segs}, attendu {attendu}")
        #    … et les fautes placées après la virgule sont vues (« une! » T01, « piochez... » T05)
        try:
            vues = {r[0] for _, t in segments_du_fichier(d / "degats.csv", "FR") for r in controler_texte(t)}
        except SystemExit:
            vues = set()
        if not {"T01", "T05"} <= vues:
            echecs.append(f"CSV d'une colonne (degats.csv) : T01 et T05 attendus après la virgule, vus {sorted(vues)}")
        #    sans ligne d'en-tête non plus, une phrase n'est pas coupée à sa virgule
        f = essai("sans_entete.csv", "Gardien,Sentinelle\nPiochez une carte, puis défaussez-en une!\n"
                                     "Gagnez 2 PV, puis piochez...\n")
        segs = [t for _, t in lecture.textes(f)]
        if segs != ["Gardien,Sentinelle", "Piochez une carte, puis défaussez-en une!", "Gagnez 2 PV, puis piochez..."]:
            echecs.append(f"CSV d'une colonne sans en-tête : obtenu {segs}")
        #    et un vrai tableau dont le texte finit par un nombre, à côté d'une colonne Max, reste un tableau
        f = essai("longueurs.csv", "ID,EN,FR,Max\nC1,Draw 2,Piochez 2,25\nC2,Gain 3,Gagnez 3,20\n")
        if lecture.lignes_csv(f) != [["ID", "EN", "FR", "Max"], ["C1", "Draw 2", "Piochez 2", "25"],
                                     ["C2", "Gain 3", "Gagnez 3", "20"]]:
            echecs.append(f"tableau avec colonne Max lu à tort comme une colonne : {lecture.lignes_csv(f)}")
        # 5. une date Excel est lue en date, pas en nombre (pas de fausse alerte T10)
        f = d / "planning.xlsx"
        _xlsx_essai(f, {"Lots": [["Lot", "Remise"], ["1", ("date", 46339)]]})
        segs = lecture.textes(f)
        if ("Lots!L2C2", "2026-11-13") not in segs or any(r[0] == "T10" for _, t in segs for r in controler_texte(t)):
            echecs.append(f"date Excel : obtenu {segs}, attendu 2026-11-13 sans alerte T10")
        # 6. tableau en virgules avec une ligne de titre au-dessus (sans virgule) : trois colonnes, et seule
        #    la colonne FR est corrigée
        corrige_seulement_fr(
            essai("titre_virgule.csv", "Cartes validées\nID,EN,FR\nC1,Don't draw...,N'en piochez pas...\n"),
            [["Cartes validées"], ["ID", "EN", "FR"], ["C1", "Don't draw...", "N’en piochez pas…"]],
            "titre au-dessus d'un tableau en virgules")
        # 7. tableau en « ; » dont une ligne a une case de plus : toujours trois colonnes
        corrige_seulement_fr(
            essai("irregulier.csv", "ID;EN;FR\nC1;Don't draw...;N'en piochez pas...\nC2;Go...;Allez...;\nC3;x;y\n"),
            [["ID", "EN", "FR"], ["C1", "Don't draw...", "N’en piochez pas…"], ["C2", "Go...", "Allez…", ""],
             ["C3", "x", "y"]], "ligne irrégulière")
        # 8. CSV d'une colonne corrigé : l'en-tête et les guillemets restent tels quels, le texte est corrigé
        f = essai("seule.csv", 'FR\n"Piochez une carte, puis..."\nN\'en piochez pas...\n')
        refuse_sans_colonne(f, "CSV d'une colonne")
        try:
            lu = corriger_fichier(f, "FR")[0].read_text(encoding="utf-8-sig")
        except Refus as e:
            lu = str(e)
        if lu != 'FR\n"Piochez une carte, puis…"\nN’en piochez pas…\n':
            echecs.append(f"CSV d'une colonne, --corriger --colonne FR : obtenu {lu!r}")
        # 9. tableau écrit à la main (« ID; EN; FR », une espace après chaque séparateur), que le lecteur peut
        #    ne pas reconnaître : sans --colonne, refus ; avec --colonne FR, refus ou copie, mais l'anglais
        #    n'est jamais réécrit
        f = essai("main.csv", "ID; EN; FR\nC1; Don't draw...; N'en piochez pas...\n")
        refuse_sans_colonne(f, "tableau écrit à la main")
        try:
            copie = corriger_fichier(f, "FR")[0].read_text(encoding="utf-8-sig")
        except Refus:
            copie = None
        if copie is not None and "Don't draw..." not in copie:
            echecs.append(f"tableau écrit à la main, --colonne FR : la source anglaise a été réécrite : {copie!r}")
    return 9, echecs


def auto_test():
    sabote = ("Défaussez une carte! Effet: piochez \"Éclat\" puis l'action... "
              "Etape 2  : la 2ème manche rapporte 10000 points - sauf si n° 3.")
    attendus = {"T01", "T02", "T03", "T04", "T05", "T07", "T08", "T09", "T10", "T11", "T12"}
    manquants = sorted(attendus - {r[0] for r in controler_texte(sabote)})
    manquants += [f"{rid} dans « {p} »" for p, rid in FAUTES if rid not in {r[0] for r in controler_texte(p)}]
    propre = ("Défaussez une carte\u202f! Effet\u00a0: piochez «\u00a0Éclat\u00a0» puis l’action… "
              "Étape 2\u00a0: la 2e manche rapporte 10\u00a0000 points –\u00a0sauf si n°\u00a03.")
    faux_positifs = [r for p in [propre] + PROPRES for r in controler_texte(p)]
    n_fichiers, echecs = auto_test_fichiers()
    if manquants or faux_positifs or echecs:
        print(f"AUTO-TEST ÉCHOUÉ — fautes non trouvées : {manquants} ; fausses alertes : {faux_positifs} ; "
              f"fichiers piégés : {echecs}")
        return 1
    print(f"AUTO-TEST OK — {len(attendus) + len(FAUTES)} fautes glissées exprès, toutes trouvées ; "
          f"0 fausse alerte sur {len(PROPRES) + 1} textes propres ; {n_fichiers} essais de fichiers piégés réussis "
          "(copie corrigée limitée à la colonne FR, colonne absente, colonne vide, CSV d'une colonne même quand "
          "sa première virgule n'est pas suivie d'une espace, date Excel, "
          "titre au-dessus d'un tableau en virgules, ligne irrégulière, tableau écrit à la main)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier", nargs="?")
    ap.add_argument("--colonne")
    ap.add_argument("--corriger", action="store_true")
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--auto-test", action="store_true")
    a = ap.parse_args()
    if a.auto_test:
        sys.exit(auto_test())
    if not a.fichier:
        ap.error("donne un fichier, ou --auto-test")
    p = Path(a.fichier)
    refus = refus_corriger(p, a.colonne) if a.corriger else None
    if refus:                                     # avant tout contrôle : rien n'est lu ni écrit
        print(refus)
        sys.exit(2)
    segments = segments_du_fichier(p, a.colonne)
    total, lignes = rapport(segments, a.max)
    print(f"Typographie — {p.name} — {len(segments)} segment{'s' if len(segments) > 1 else ''} lu{'s' if len(segments) > 1 else ''} en entier")
    if not total:
        print("0 alerte. (Vérifie quand même avec --auto-test que le contrôle trouve bien des fautes glissées exprès.)")
    else:
        print(f"{sum(total.values())} alerte(s) :")
        for rid in IDS:
            if total[rid]:
                lib = next(r[1] for r in REGLES if r[0] == rid)
                print(f"  {rid} {lib} : {total[rid]}")
        print(f"Détail ({min(sum(total.values()), a.max)} premières) :")
        print("\n".join(lignes))
    if a.corriger:
        try:
            sortie, quoi = corriger_fichier(p, a.colonne)
        except Refus as e:
            print(str(e))
            sys.exit(2)
        print(f"Copie corrigée (règles sûres T04 T05 T06 T07, {quoi}, adresses web et e-mails intacts) : "
              f"{sortie.name}. L'original n'est pas modifié.")


if __name__ == "__main__":
    main()
