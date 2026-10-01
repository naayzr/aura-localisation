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
pour qu'on puisse facturer avec ou sans elles selon l'accord avec l'éditeur.
"""
import argparse, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

BALISE = re.compile(r"\{[^{}\n]{1,40}\}|<[^<>\n]{1,40}>|\[[^\[\]\n]{1,40}\]")
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
    if [t for _, t in col] != ["Piochez, puis défaussez.", "Reposez-vous, ou soignez 1 blessure ; votre tour se termine."]:
        print(f"AUTO-TEST ÉCHOUÉ — CSV en points-virgules avec virgules dans le texte mal lu : {col}")
        return 1
    segs = [("§1", "Piochez 2 cartes."), ("§2", "Gagnez {or} 3."), ("§3", "Piochez 2 cartes.")]
    c = compter(segs)
    attendu = {"segments": 3, "cec": 17 + 14 + 17, "ces": 15 + 12 + 15, "balises": 1,
               "cec_sans_balises": 17 + 10 + 17, "mots": 3 + 2 + 3, "rep_segments": 1, "rep_cec": 17}
    faux = {k: (c[k], v) for k, v in attendu.items() if c[k] != v}
    if faux:
        print(f"AUTO-TEST ÉCHOUÉ — écarts (obtenu, attendu) : {faux}")
        return 1
    print("AUTO-TEST OK — comptes exacts sur un extrait connu (caractères, mots, balises, répétitions) "
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
        segs = segments_de(f, a.colonne)
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
