#!/usr/bin/env python3
"""Comptage exact de caractères, mots et segments d'un ou plusieurs fichiers de traduction.

Usage :
  python3 compter.py FICHIER [FICHIER…] [--colonne NOM] [--tarif-1000 X | --tarif-mot X] [--cadence N]
  python3 compter.py --auto-test

  --colonne NOM   tableur : ne compter que la colonne d'en-tête NOM (ex. EN pour la source, FR pour la cible)
  --tarif-1000 X  prix pour 1 000 caractères espaces comprises → montant
  --tarif-mot X   prix au mot → montant
  --cadence N     caractères (espaces comprises) traduits par jour → nombre de jours de travail

Tout le fichier est lu ; rien n'est estimé. Les balises ({icone}, <b>, [degats]) sont comptées à part,
pour qu'on puisse facturer avec ou sans elles selon l'accord avec l'éditeur. Une balise est un
identifiant sans espace (motif BALISE de lecture.py) : « [la règle optionnelle] » ou « score < 3 et
B > 5 » restent du texte, comptés et facturés comme tel.
"""
import argparse, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

BALISE = lecture.BALISE      # écrit une seule fois, dans lecture.py (le même pour controle-longueur)
MOT = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿŒœ]+(?:[’'\-][0-9A-Za-zÀ-ÖØ-öø-ÿŒœ]+)*")
FEUILLET = 1500


def segments_de(chemin, colonne):
    p = Path(chemin)
    if not colonne:
        return lecture.textes(p)
    feuilles = lecture.feuilles_xlsx(p) if p.suffix.lower() == ".xlsx" else {"": lecture.lignes_csv(p)}
    out, vue = [], False
    for feuille, lignes in feuilles.items():
        for i, ligne in enumerate(lignes):
            norm = [str(c).strip().lower() for c in ligne]
            if colonne.lower() in norm:
                vue = True
                k = norm.index(colonne.lower())
                for j, l2 in enumerate(lignes[i + 1:], i + 2):
                    if k < len(l2) and str(l2[k]).strip():
                        out.append((f"{feuille}!L{j}" if feuille else f"L{j}", str(l2[k])))
                break
    if not vue:
        raise SystemExit(f"Colonne « {colonne} » introuvable dans {p.name}.")
    return out


def compter(segments):
    c = Counter()
    vus = Counter(t.strip() for _, t in segments)
    deja = set()
    for _, t in segments:
        sans_bal = BALISE.sub("", t)
        c["segments"] += 1
        c["cec"] += len(t)
        c["ces"] += len(re.sub(r"\s", "", t))
        c["cec_sans_balises"] += len(sans_bal)
        c["balises"] += len(BALISE.findall(t))
        c["mots"] += len(MOT.findall(sans_bal))
        cle = t.strip()
        if vus[cle] > 1:
            if cle in deja:
                c["rep_segments"] += 1
                c["rep_cec"] += len(t)
            deja.add(cle)
    return c


def fr(n):
    return f"{n:,}".replace(",", " ")


def afficher(nom, c):
    print(f"{nom}")
    print(f"  segments (paragraphes, cellules ou lignes non vides) : {fr(c['segments'])}")
    print(f"  caractères espaces comprises : {fr(c['cec'])}   (sans balises : {fr(c['cec_sans_balises'])} ; balises : {fr(c['balises'])})")
    print(f"  caractères sans espaces : {fr(c['ces'])}")
    print(f"  mots (hors balises) : {fr(c['mots'])}")
    print(f"  feuillets de {fr(FEUILLET)} signes : {c['cec'] / FEUILLET:.1f}".replace(".", ","))
    if c["rep_segments"]:
        print(f"  répétitions exactes : {fr(c['rep_segments'])} segments, {fr(c['rep_cec'])} caractères (déjà comptés ci-dessus)")


DOCX_PIEGE = {
    "[Content_Types].xml": '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
    "word/document.xml": (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"><w:body>'
        '<w:p><w:r><w:t>Piochez deux cartes.</w:t></w:r><w:r><w:rPr><w:vanish/></w:rPr><w:t>CACHE</w:t></w:r></w:p>'
        '<w:p><w:r><mc:AlternateContent><mc:Choice Requires="wps"><w:txbxContent><w:p><w:r><w:t>Encadré de vingt car</w:t></w:r></w:p>'
        '</w:txbxContent></mc:Choice><mc:Fallback><w:txbxContent><w:p><w:r><w:t>Encadré de vingt car</w:t></w:r></w:p>'
        '</w:txbxContent></mc:Fallback></mc:AlternateContent></w:r></w:p></w:body></w:document>'),
    "word/footnotes.xml": (
        '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:t>---</w:t></w:r></w:p></w:footnote>'
        '<w:footnote w:id="1"><w:p><w:r><w:t>Une note.</w:t></w:r></w:p></w:footnote></w:footnotes>'),
    "word/header1.xml": ('<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                         '<w:p><w:r><w:t>Livret de règles</w:t></w:r></w:p></w:hdr>'),
}


def auto_test_docx():
    """Un Word piégé : la zone de texte que Word écrit DEUX fois, une note, un en-tête, du texte masqué."""
    import tempfile, zipfile
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "piege.docx"
        with zipfile.ZipFile(f, "w") as z:
            for nom, contenu in DOCX_PIEGE.items():
                z.writestr(nom, contenu)
        c = compter(segments_de(f, None))
        masque = getattr(lecture, "masque_docx", lambda _f: -1)(f)   # un ancien lecteur n'a pas cette fonction
    attendu = {"segments": 4, "cec": 20 + 20 + 9 + 16}
    faux = {k: (c[k], v) for k, v in attendu.items() if c[k] != v}
    if masque != 5:
        faux["texte masqué"] = (masque, 5)
    return faux


def auto_test():
    faux_docx = auto_test_docx()
    if faux_docx:
        print(f"AUTO-TEST ÉCHOUÉ — Word piégé (zone de texte, note, en-tête, masqué) : écarts (obtenu, attendu) {faux_docx}")
        return 1
    # un CSV « à la française » : ligne de titre au-dessus, séparateur ;, virgules dans le texte
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "cartes.csv"
        f.write_text("Gamme test\nCarte;EN;FR\nC1;Draw, then discard.;Piochez, puis défaussez.\n"
                     "C2;Rest.;\"Reposez-vous, ou soignez 1 blessure ; votre tour se termine.\"\n", encoding="utf-8")
        try:
            col = segments_de(f, "FR")
        except SystemExit:
            col = []
        # un CSV « à l'anglaise » : ligne de titre au-dessus, séparateur virgule. Les virgules qui séparent
        # les colonnes ne sont pas du texte : elles ne doivent pas entrer dans le compte d'un devis.
        g = Path(d) / "devis.csv"
        g.write_text("Cartes validées\nID,EN,FR\nC1,Draw a card,Piochez une carte\nC2,Discard two,Défaussez-en deux\n",
                     encoding="utf-8")
        tout = compter(segments_de(g, None))["cec"]
        try:
            col_fr = [t for _, t in segments_de(g, "FR")]
        except SystemExit:
            col_fr = []
        # une colonne de phrases (en-tête FR) dont la première virgule n'est pas suivie d'une espace
        # (« 1,5. ») : elle n'est pas un tableau, et rien de ce qui suit les virgules n'est perdu du compte
        h = Path(d) / "une_colonne.csv"
        phrases = ["Les dégâts sont multipliés par 1,5.", "Piochez une carte, puis défaussez-en une !",
                   "Gagnez 2 PV, puis piochez…"]
        h.write_text("FR\n" + "\n".join(phrases) + "\n", encoding="utf-8")
        try:
            une_col = compter(segments_de(h, "FR"))["cec"]
        except SystemExit:
            une_col = 0
        # un tableau en points-virgules sous un titre, dont une case finit par un chiffre et la suivante
        # commence par un nombre (« C2;2 dégâts ») : le point-virgule ne coupe jamais un nombre
        # même piège à la virgule, sans titre (export Excel anglais), avec les identifiants courants
        col_vr = {}
        for ref in ("C1", "C10", "R12", "C_01", "CARD-012", "12"):
            v = Path(d) / f"virgules_{len(col_vr)}.csv"
            v.write_text(f"ID,EN,FR\n{ref},2 damage,2 dégâts\nX2,Draw a card,Piochez une carte\nX3,3 VP,3 PV\n", encoding="utf-8")
            try:
                col_vr[ref] = [t for _, t in segments_de(v, "FR")]
            except SystemExit:
                col_vr[ref] = []
        # une colonne de nombres en 2e position (Coût) suivie d'un texte qui commence par un nombre, avec ou
        # sans titre, et un identifiant qui contient une espace : « 3,2 dégâts » n'est pas un nombre coupé
        col_cout = {}
        # et des en-têtes abrégés (« Long. max. », « Card No. ») : un libellé peut finir par un point
        for nom, tete, ref, en_tete in (
                ("coût", "", "C1", "ID,Coût,EN,FR"), ("coût sous un titre", "Cartes validées\n", "C1", "ID,Coût,EN,FR"),
                ("« Carte 12 »", "", "Carte 12", "ID,Coût,EN,FR"), ("« Long. max. »", "", "C1", "ID,Long. max.,EN,FR"),
                ("« Card No. » sous un titre", "Set : Core\n", "C1", "Card No.,Max. len.,EN,FR")):
            v = Path(d) / f"cout_{len(col_cout)}.csv"
            v.write_text(f"{tete}{en_tete}\n{ref},3,2 damage,2 dégâts\nX2,1,Draw a card,Piochez une carte\n"
                         "X3,2,3 VP,3 PV\n", encoding="utf-8")
            try:
                col_cout[nom] = [t for _, t in segments_de(v, "FR")]
            except SystemExit:
                col_cout[nom] = []
        # une seule colonne de phrases dont un nombre décimal porte un signe ou un multiplicateur collé
        # (« (x1,5) », « ×1,5 », « +1,5 », « -0,5 »), ou ouvre la phrase (« 1,5 fois plus ») : rien n'est perdu
        une_signe = {}
        for phrase in ("Relancez (x1,5).", "Dégâts ×1,5.", "Gagnez +1,5 PV.", "Perdez -0,5 PV.",
                       "Les dégâts augmentent de 12,5%.", "Inflige 1,5x les dégâts.", "Dégâts ×1,5", "Soin +2,5",
                       "1 plateau de jeu (45,5×30,5 cm)"):
            v = Path(d) / f"signe_{len(une_signe)}.csv"
            v.write_text(f"FR\n{phrase}\n{phrase}\n", encoding="utf-8")
            try:
                une_signe[phrase] = [t for _, t in segments_de(v, "FR")]
            except SystemExit:
                une_signe[phrase] = []
        # une dernière colonne « Note » remplie sur une ligne seulement (Excel n'écrit pas le « ; » final des
        # autres), et une espace tapée par mégarde : l'en-tête n'est pas un titre, le tableau reste un tableau
        v = Path(d) / "note.csv"
        v.write_text("ID;EN;FR;Note\nC1;Draw a card.;Piochez une carte.;à valider\nC2;Discard.;Défaussez.\n"
                     "C3;Gain 2 gold.;Gagnez 2 pièces d’or.\nC4;Roll the die.; Lancez le dé.\nC5;Heal.;Soignez.\n",
                     encoding="utf-8")
        try:
            col_note = [t for _, t in segments_de(v, "FR")]
        except SystemExit:
            col_note = []
        # export Excel par blocs de 16 lignes : la colonne FR encore vide n'a pas son « ; » sur les blocs entiers
        v = Path(d) / "a_traduire.csv"
        en = [f"Draw {i} cards." for i in range(1, 41)]
        v.write_text("EN;FR\n" + "".join(f"{e};\n" if i < 15 else f"{e}\n" for i, e in enumerate(en)), encoding="utf-8")
        try:
            col_bloc = [t for _, t in segments_de(v, "EN")]
        except SystemExit:
            col_bloc = []
        # le même export Excel sous un titre daté (« Cartes du chapitre 2;30/09/2026 »)
        v = Path(d) / "a_traduire_titre.csv"
        v.write_text("Cartes du chapitre 2;30/09/2026\nEN;FR\n" + "".join(f"{e};\n" if i < 14 else f"{e}\n"
                                                                         for i, e in enumerate(en)), encoding="utf-8")
        try:
            col_bloc_titre = [t for _, t in segments_de(v, "EN")]
        except SystemExit:
            col_bloc_titre = []
        # export Google Sheets : le titre « Chapitre 2 | 45 cartes » complété jusqu'à la largeur du tableau
        v = Path(d) / "gsheets_titre.csv"
        v.write_text("Chapitre 2,45 cartes,\r\nID,EN,FR\r\nC1,Draw a card.,Piochez une carte.\r\n"
                     "C2,Gain 2 gold.,Gagnez 2 pièces d’or.\r\n", encoding="utf-8")
        try:
            col_gs = [t for _, t in segments_de(v, "FR")]
        except SystemExit:
            col_gs = []
        # un tableau sans en-tête dont les premières lignes finissent une case par un nombre suivie d'une case
        # de nombre (« C1,Vol 1,Vol 1,120 ») : des lignes de tableau, pas des nombres coupés
        v = Path(d) / "sans_entete_chiffre.csv"
        v.write_text("C1,Flying 1,Vol 1,120\r\nC2,Armor 2,Armure 2,40\r\nC3,Level 3,Niveau 3,60\r\n"
                     "C4,Age 2,Âge 2,25\r\nC5,Draw a card.,Piochez une carte.,60\r\n", encoding="utf-8")
        lu_chiffre = lecture.lignes_csv(v)
        # le même tableau, avec une espace tapée par mégarde au début d'une case de la 1re ligne
        v = Path(d) / "sans_entete_espace.csv"
        v.write_text("C1;Discard a card.; Défaussez une carte.;60\nC2;Gain 2 gold.;Gagnez 2 pièces d’or.;40\n"
                     "C3;Rest.;Reposez-vous.;25\nC4;Roll the die.;Lancez le dé.;30\n", encoding="utf-8")
        lu_espace = lecture.lignes_csv(v)
        # une colonne de phrases sans en-tête dont la première ligne a une virgule sans espace (« A3,B4 »)
        v = Path(d) / "phrases_sans_entete.txt.csv"
        phr = ["Placez un jeton sur les cases A3,B4 et C5.", "Lancez le dé, puis avancez.", "Gagnez 2 PV.",
               "Reposez-vous.", "Piochez une carte.", "Défaussez une carte.", "Passez votre tour."]
        v.write_text("\n".join(phr) + "\n", encoding="utf-8")
        une_sans = compter(segments_de(v, None))["cec"]
        # un titre écrit en phrase, plus large que le tableau, au-dessus d'un tableau en virgules
        v = Path(d) / "titre_phrase.csv"
        v.write_text("Glossaire Arkham, version 2, septembre\nEN,FR\nAttack,Attaque\nShield,Bouclier\n", encoding="utf-8")
        try:
            col_titre = [t for _, t in segments_de(v, "FR")]
        except SystemExit:
            col_titre = []
        k = Path(d) / "points_virgules.csv"
        k.write_text("Cartes validées\nID;FR\nC1;Piochez une carte.\nC2;2 dégâts à la cible.\n", encoding="utf-8")
        try:
            col_pv = [t for _, t in segments_de(k, "FR")]
        except SystemExit:
            col_pv = []
    if [t for _, t in col] != ["Piochez, puis défaussez.", "Reposez-vous, ou soignez 1 blessure ; votre tour se termine."]:
        print(f"AUTO-TEST ÉCHOUÉ — CSV en points-virgules avec virgules dans le texte mal lu : {col}")
        return 1
    attendu_tout = len("Cartes validées") + len("IDENFR") + len("C1Draw a cardPiochez une carte") + len(
        "C2Discard twoDéfaussez-en deux")
    if tout != attendu_tout or col_fr != ["Piochez une carte", "Défaussez-en deux"]:
        print(f"AUTO-TEST ÉCHOUÉ — CSV en virgules avec un titre au-dessus mal lu : {tout} caractères (attendu "
              f"{attendu_tout}, séparateurs exclus) ; colonne FR : {col_fr}")
        return 1
    mal_lus = {r: c for r, c in col_vr.items() if c != ["2 dégâts", "Piochez une carte", "3 PV"]}
    if mal_lus:
        print(f"AUTO-TEST ÉCHOUÉ — tableau en virgules « <ref>,2 damage » lu en une colonne : {mal_lus}")
        return 1
    mal_lus = {r: c for r, c in col_cout.items() if c != ["2 dégâts", "Piochez une carte", "3 PV"]}
    if mal_lus:
        print(f"AUTO-TEST ÉCHOUÉ — tableau en virgules « C1,3,2 damage » (colonne de nombres) mal lu : {mal_lus}")
        return 1
    if col_note != ["Piochez une carte.", "Défaussez.", "Gagnez 2 pièces d’or.", " Lancez le dé.", "Soignez."]:
        print(f"AUTO-TEST ÉCHOUÉ — tableau à dernière colonne « Note » incomplète lu de travers : {col_note}")
        return 1
    if [len(l) for l in lu_espace] != [4, 4, 4, 4]:
        print(f"AUTO-TEST ÉCHOUÉ — une espace tapée par mégarde en 1re ligne fait lire le tableau de travers : {lu_espace[:2]}")
        return 1
    if [l[2] if len(l) > 2 else None for l in lu_chiffre] != ["Vol 1", "Armure 2", "Niveau 3", "Âge 2", "Piochez une carte."]:
        print(f"AUTO-TEST ÉCHOUÉ — tableau sans en-tête à cases chiffrées (« C1,Vol 1,120 ») mal lu : {lu_chiffre[:2]}")
        return 1
    if col_gs != ["Piochez une carte.", "Gagnez 2 pièces d’or."]:
        print(f"AUTO-TEST ÉCHOUÉ — export Google Sheets sous un titre « Chapitre 2,45 cartes, » mal lu : {col_gs}")
        return 1
    if col_bloc_titre != en or une_sans != sum(len(p) for p in phr):
        print(f"AUTO-TEST ÉCHOUÉ — export Excel sous un titre daté ({len(col_bloc_titre)} lignes EN sur 40) ou colonne "
              f"de phrases sans en-tête ({une_sans} caractères, attendu {sum(len(p) for p in phr)}) mal lus")
        return 1
    if col_bloc != en or col_titre != ["Attaque", "Bouclier"]:
        print(f"AUTO-TEST ÉCHOUÉ — export Excel par blocs ({len(col_bloc)} lignes EN sur 40) ou titre en phrase "
              f"({col_titre}) mal lus")
        return 1
    mal_lus = {p: c for p, c in une_signe.items() if c != [p, p]}
    if mal_lus:
        print(f"AUTO-TEST ÉCHOUÉ — colonne de phrases coupée à la virgule d'un nombre décimal : {mal_lus}")
        return 1
    if col_pv != ["Piochez une carte.", "2 dégâts à la cible."]:
        print(f"AUTO-TEST ÉCHOUÉ — tableau en points-virgules sous un titre lu en une colonne (« C2;2 dégâts ») : {col_pv}")
        return 1
    if une_col != sum(len(t) for t in phrases):
        print(f"AUTO-TEST ÉCHOUÉ — CSV d'une colonne coupé aux virgules : {une_col} caractères comptés dans la "
              f"colonne FR, attendu {sum(len(t) for t in phrases)}")
        return 1
    segs = [("§1", "Piochez 2 cartes."), ("§2", "Gagnez {or} 3."), ("§3", "Piochez 2 cartes.")]
    c = compter(segs)
    attendu = {"segments": 3, "cec": 17 + 14 + 17, "ces": 15 + 12 + 15, "balises": 1,
               "cec_sans_balises": 17 + 10 + 17, "mots": 3 + 2 + 3, "rep_segments": 1, "rep_cec": 17}
    faux = {k: (c[k], v) for k, v in attendu.items() if c[k] != v}
    if faux:
        print(f"AUTO-TEST ÉCHOUÉ — écarts (obtenu, attendu) : {faux}")
        return 1
    # du vrai texte qui ressemble à une balise (comparaison, parenthèse entre crochets) reste du texte ;
    # les vraies balises, fermantes comprises, sont toujours comptées à part
    textes = ["Si votre score < 3 et celui de B > 5, gagnez.", "Voir [la règle optionnelle de fin de partie] page 12.",
              "[b]Attaque[/b] {icon:gold}"]
    c = compter([(f"§{i}", t) for i, t in enumerate(textes, 1)])
    attendu = {"balises": 3, "cec_sans_balises": len(textes[0]) + len(textes[1]) + len("Attaque "),
               "mots": 10 + 10 + 1}
    faux = {k: (c[k], v) for k, v in attendu.items() if c[k] != v}
    if faux:
        print(f"AUTO-TEST ÉCHOUÉ — texte pris pour une balise, écarts (obtenu, attendu) : {faux}")
        return 1
    print("AUTO-TEST OK — comptes exacts sur un extrait connu (caractères, mots, balises, répétitions), "
          "sur du texte qui ressemble à une balise (« < 3 … > », crochets rédactionnels), "
          "sur des CSV (points-virgules, virgules avec un titre au-dessus, colonne de nombres, une seule colonne de "
          "phrases avec des nombres décimaux) "
          "et sur un Word piégé (zone de texte comptée une fois, note et en-tête lus, texte masqué à part)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichiers", nargs="*")
    ap.add_argument("--colonne")
    ap.add_argument("--tarif-1000", type=float)
    ap.add_argument("--tarif-mot", type=float)
    ap.add_argument("--cadence", type=int)
    ap.add_argument("--auto-test", action="store_true")
    a = ap.parse_args()
    if a.auto_test:
        sys.exit(auto_test())
    if not a.fichiers:
        ap.error("donne au moins un fichier, ou --auto-test")
    total = Counter()
    for f in a.fichiers:
        try:
            segs = segments_de(f, a.colonne)
        except ValueError as e:                   # format non pris en charge, octets nuls
            raise SystemExit(f"{Path(f).name} : {e} Aucun chiffre n'est donné.")
        c = compter(segs)
        afficher(Path(f).name + (f" — colonne {a.colonne}" if a.colonne else ""), c)
        if Path(f).suffix.lower() == ".docx" and not a.colonne:
            annexes = [t for r, t in segs if not r.startswith("§")]
            if annexes:
                print(f"  dont notes, en-têtes et pieds de page : {fr(sum(len(t) for t in annexes))} caractères "
                      f"({len(annexes)} segments) — à inclure ou non selon l'accord avec l'éditeur")
            m = lecture.masque_docx(f)
            if m:
                print(f"  texte masqué dans Word, NON compté : {fr(m)} caractères — à vérifier avec Hervé")
        total.update(c)
    if len(a.fichiers) > 1:
        afficher(f"TOTAL ({len(a.fichiers)} fichiers)", total)
    if a.tarif_1000:
        m = total["cec"] / 1000 * a.tarif_1000
        print(f"Montant au tarif de {a.tarif_1000:.2f} € / 1 000 caractères espaces comprises : {m:,.2f} €".replace(",", " ").replace(".", ","))
    if a.tarif_mot:
        m = total["mots"] * a.tarif_mot
        print(f"Montant au tarif de {a.tarif_mot:.3f} € / mot : {m:,.2f} €".replace(",", " ").replace(".", ","))
    if a.cadence:
        print(f"Durée à {fr(a.cadence)} caractères par jour : {total['cec'] / a.cadence:.1f} jours de travail".replace(".", ","))
    print("Base du compte : tout le fichier, sans estimation (Word : corps, tableaux, zones de texte une seule fois, "
          "notes, en-têtes et pieds ; pas les commentaires ni le texte masqué). Les espaces insécables comptent comme des espaces.")


if __name__ == "__main__":
    main()
