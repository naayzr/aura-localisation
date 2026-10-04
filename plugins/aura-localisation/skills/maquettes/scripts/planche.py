#!/usr/bin/env python3
"""Planche de cartes en français, aux dimensions réelles, pour repérer le texte qui déborde ;
et fichier de fusion de données pour InDesign ou Affinity.

Usage :
  python3 planche.py TABLEUR --fr NOM [--id NOM] [--titre NOM] [--largeur 63] [--hauteur 88]
                     [--zone X,Y,L,H] [--police "Georgia"] [--taille 8.5] [--interligne 1.2]
                     [--sortie planche.html] [--csv-fusion base]
  python3 planche.py --auto-test

  TABLEUR       .xlsx ou .csv, une ligne par carte ; --fr = en-tête exact de la colonne française
  --largeur/--hauteur  format de la carte en mm (défaut 63 × 88, carte « poker »)
  --zone X,Y,L,H       zone de texte dans la carte, en mm depuis le coin haut gauche (défaut : marges de 5 mm)
  --police, --taille   police et corps (pt) de l'éditeur ; la police doit être installée sur l'ordinateur
                       qui ouvre la planche, sinon le navigateur en prend une autre et la mesure est fausse
  --sortie             fichier HTML produit (défaut : planche_cartes.html à côté du tableur) ; jamais écrasé
  --csv-fusion BASE    écrit aussi BASE_utf8.csv et BASE_utf16.txt pour une fusion de données

La planche est une APPROCHE : elle mesure avec la police et le corps donnés, dans le navigateur. Seule
l'épreuve faite avec le vrai gabarit et la vraie police (InDesign, Affinity, épreuve de l'éditeur) prouve
qu'un texte tient.
"""
import argparse, csv, html, io, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

BALISE = re.compile(r"(\{[^{}\n]{1,40}\}|<[^<>\n]{1,40}>|\[[^\[\]\n]{1,40}\])")


def lignes_tableur(chemin, col_fr, col_id, col_titre):
    p = Path(chemin)
    feuilles = lecture.feuilles_xlsx(p) if p.suffix.lower() == ".xlsx" else {"": lecture.lignes_csv(p)}
    for feuille, lignes in feuilles.items():
        for i, ligne in enumerate(lignes):
            norm = [str(c).strip().lower() for c in ligne]
            if col_fr.lower() in norm:
                k = norm.index(col_fr.lower())
                ki = norm.index(col_id.lower()) if col_id and col_id.lower() in norm else None
                kt = norm.index(col_titre.lower()) if col_titre and col_titre.lower() in norm else None
                cartes = []
                for j, l in enumerate(lignes[i + 1:], i + 2):
                    get = lambda x: str(l[x]).strip() if x is not None and x < len(l) else ""
                    if get(k) or get(kt):
                        cartes.append({"id": get(ki) or f"L{j}", "titre": get(kt), "fr": get(k)})
                return cartes, [str(c) for c in ligne]
    raise SystemExit(f"Colonne « {col_fr} » introuvable dans les en-têtes de {p.name}.")


def texte_html(t):
    morceaux = BALISE.split(t)
    out = []
    for m in morceaux:
        if BALISE.fullmatch(m or ""):
            out.append(f'<span class="balise">{html.escape(m)}</span>')
        else:
            out.append(html.escape(m).replace("\n", "<br>"))
    return "".join(out)


def planche(cartes, largeur, hauteur, zone, police, taille, interligne, titre):
    x, y, l, h = zone
    cellules = "\n".join(
        f'<div class="carte" data-id="{html.escape(c["id"])}"><div class="id">{html.escape(c["id"])}</div>'
        + (f'<div class="titre">{html.escape(c["titre"])}</div>' if c["titre"] else "")
        + f'<div class="zone"><div class="texte">{texte_html(c["fr"])}</div></div></div>'
        for c in cartes)
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>{html.escape(titre)}</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 12mm; color: #1b2733; }}
  h1 {{ font-size: 16px; margin: 0 0 4px; }}
  .bilan {{ font-size: 13px; margin: 0 0 10px; }}
  .bilan b.ko {{ color: #c0392b; }}
  .avert {{ font-size: 11px; color: #64748b; margin: 0 0 14px; max-width: 180mm; }}
  .grille {{ display: flex; flex-wrap: wrap; gap: 4mm; }}
  .carte {{ position: relative; width: {largeur}mm; height: {hauteur}mm; border: 0.3mm solid #94a3b8;
           border-radius: 3mm; background: #fff; box-sizing: border-box; overflow: hidden; }}
  .carte.deborde {{ border: 0.6mm solid #c0392b; background: #fdf0ee; }}
  .id {{ position: absolute; top: 1mm; right: 2mm; font-size: 6pt; color: #94a3b8; }}
  .titre {{ position: absolute; top: 1.5mm; left: 3mm; right: 8mm; font: bold 7pt system-ui; overflow: hidden;
            white-space: nowrap; text-overflow: ellipsis; }}
  .zone {{ position: absolute; left: {x}mm; top: {y}mm; width: {l}mm; height: {h}mm; outline: 0.2mm dashed #cbd5e1; }}
  .texte {{ font-family: {police}, serif; font-size: {taille}pt; line-height: {interligne}; height: 100%;
            overflow: hidden; hyphens: auto; }}
  .carte.deborde .zone {{ outline: 0.3mm dashed #c0392b; }}
  .balise {{ font: 6pt monospace; background: #e2e8f0; border-radius: 1mm; padding: 0 0.6mm; }}
  @media print {{ body {{ margin: 5mm; }} .avert {{ display: none; }} }}
</style></head><body>
<h1>{html.escape(titre)}</h1>
<p class="bilan" id="bilan">Mesure en cours…</p>
<p class="avert">Carte {largeur} × {hauteur} mm · zone de texte {l} × {h} mm à ({x} ; {y}) mm · police « {html.escape(police)} »
{taille} pt. Approche seulement : si cette police n'est pas installée sur cet ordinateur, le navigateur en utilise une
autre et la mesure est fausse. Seule l'épreuve avec le vrai gabarit prouve qu'un texte tient.</p>
<div class="grille">
{cellules}
</div>
<script>
  const cartes = [...document.querySelectorAll('.carte')];
  const ko = [];
  for (const c of cartes) {{
    const t = c.querySelector('.texte');
    if (t.scrollHeight > t.clientHeight + 1 || t.scrollWidth > t.clientWidth + 1) {{ c.classList.add('deborde'); ko.push(c.dataset.id); }}
  }}
  document.getElementById('bilan').innerHTML = cartes.length + ' cartes · <b class="' + (ko.length ? 'ko' : '') + '">' +
    ko.length + (ko.length > 1 ? ' débordent' : ' déborde') + '</b>' + (ko.length ? ' : ' + ko.join(', ') : '') ;
</script>
</body></html>
"""


def ecrire_sans_ecraser(chemin, contenu, encodage="utf-8"):
    p = Path(lecture.hors_du_plugin(chemin))
    if p.exists():
        raise SystemExit(f"{p.name} existe déjà : je n'écrase pas. Choisis un autre nom (--sortie).")
    p.write_bytes(contenu.encode(encodage) if isinstance(contenu, str) else contenu)
    return p


def csv_fusion(cartes, base):
    """Pour une fusion de données : une ligne par carte (ID, Titre, Texte). UTF-8 avec BOM (Affinity, InDesign
    récent) et UTF-16 (InDesign, quand les accents sortent cassés en UTF-8)."""
    tampon = io.StringIO()
    w = csv.writer(tampon, lineterminator="\r\n")
    w.writerow(["ID", "Titre", "Texte"])
    for c in cartes:
        w.writerow([c["id"], c["titre"], c["fr"]])
    contenu = tampon.getvalue()
    a = ecrire_sans_ecraser(f"{base}_utf8.csv", "﻿" + contenu, "utf-8")
    b = ecrire_sans_ecraser(f"{base}_utf16.txt", contenu, "utf-16")
    return a, b


def auto_test():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "cartes.csv"
        src.write_text("Carte;Nom;EN;FR\nC01;Repos;Rest.;Reposez-vous.\nC02;Éclat;Gain {or} 3.;Gagnez {or} 3 et "
                       "piochez une carte.\nC03;Sanctuaire;Heal.;" + "Texte très long. " * 60 + "\n", encoding="utf-8")
        cartes, _ = lignes_tableur(src, "FR", "Carte", "Nom")
        h = planche(cartes, 63, 88, (5, 20, 53, 60), "Georgia", 8.5, 1.2, "essai")
        sortie = ecrire_sans_ecraser(Path(d) / "planche.html", h)
        ok = [len(cartes) == 3, h.count('class="carte"') == 3, '<span class="balise">{or}</span>' in h,
              "Éclat" in h, "scrollHeight" in h, "width: 63mm" in h and "height: 88mm" in h]
        try:
            ecrire_sans_ecraser(sortie, h)
            ok.append(False)                      # aurait dû refuser d'écraser
        except SystemExit:
            ok.append(True)
        a, b = csv_fusion(cartes, Path(d) / "fusion")
        u8 = a.read_bytes().decode("utf-8")
        u16 = b.read_bytes().decode("utf-16")
        ok += [u8.startswith("﻿ID,Titre,Texte"), "Gagnez {or} 3" in u8, "Éclat" in u16,
               b.read_bytes()[:2] in (b"\xff\xfe", b"\xfe\xff")]
    if all(ok):
        print("AUTO-TEST OK — planche de 3 cartes aux bonnes dimensions, balises marquées, mesure de débord présente, "
              "jamais d'écrasement ; fichiers de fusion UTF-8 (BOM) et UTF-16 lisibles avec les accents")
        return 0
    print(f"AUTO-TEST ÉCHOUÉ — contrôles : {ok}")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tableur", nargs="?")
    ap.add_argument("--fr"); ap.add_argument("--id"); ap.add_argument("--titre")
    ap.add_argument("--largeur", type=float, default=63); ap.add_argument("--hauteur", type=float, default=88)
    ap.add_argument("--zone")
    ap.add_argument("--police", default="Georgia"); ap.add_argument("--taille", type=float, default=8.5)
    ap.add_argument("--interligne", type=float, default=1.2)
    ap.add_argument("--sortie"); ap.add_argument("--csv-fusion")
    ap.add_argument("--auto-test", action="store_true")
    a = ap.parse_args()
    if a.auto_test:
        sys.exit(auto_test())
    if not a.tableur or not a.fr:
        ap.error("donne le tableur et --fr (en-tête de la colonne française), ou --auto-test")
    zone = tuple(float(v) for v in a.zone.split(",")) if a.zone else (5, 5, a.largeur - 10, a.hauteur - 10)
    if len(zone) != 4 or zone[0] + zone[2] > a.largeur or zone[1] + zone[3] > a.hauteur:
        ap.error("--zone X,Y,L,H doit tenir dans la carte (en mm)")
    cartes, _ = lignes_tableur(a.tableur, a.fr, a.id, a.titre)
    titre = f"Planche FR — {Path(a.tableur).name} — {len(cartes)} cartes"
    sortie = Path(a.sortie) if a.sortie else Path(a.tableur).with_name("planche_cartes.html")
    ecrire_sans_ecraser(sortie, planche(cartes, a.largeur, a.hauteur, zone, a.police, a.taille, a.interligne, titre))
    print(f"Planche écrite : {sortie} — {len(cartes)} cartes. Ouvre-la dans le navigateur : le nombre de cartes qui "
          f"débordent s'affiche en haut, et elles sont en rouge.")
    if a.csv_fusion:
        x, y = csv_fusion(cartes, a.csv_fusion)
        print(f"Fichiers de fusion : {x.name} (UTF-8) et {y.name} (UTF-16, pour InDesign si les accents sortent cassés).")


if __name__ == "__main__":
    main()
