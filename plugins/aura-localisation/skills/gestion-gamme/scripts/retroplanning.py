#!/usr/bin/env python3
"""Rétroplanning d'un produit de gamme, calculé à rebours depuis la date de remise à l'imprimeur.

Bibliothèque standard uniquement. Aucune valeur n'est supposée : la capacité de traduction (caractères
par jour ouvré) et la durée de chaque étape sont OBLIGATOIRES. S'il en manque, le script s'arrête et
dit lesquelles demander à Hervé. Une étape qui n'existe pas sur ce produit se déclare à 0.

Chaîne (dans l'ordre) : réception des sources → traduction → réponses aux dernières questions de
l'éditeur et intégration (le relecteur lit un texte où elles sont déjà reportées) → relecture → mise en
page → BAT1 → BAT2 → validation de la VF par l'éditeur de la VO ou l'ayant droit (licence, co-édition) →
fichiers d'impression → remise à l'imprimeur. La FAQ se place après la remise, hors calcul.
Une étape propre à ce produit s'ajoute avec --etape "Nom:jours:après", où « après » est l'étape qui la
précède (traduction, questions, relecture, mise-en-page, bat1, bat2, validation-vo, fichiers) ; l'option
se répète.

Exemple :
  python3 retroplanning.py --produit "Extension 2" --remise 2027-03-15 --caracteres 320000 \\
      --capacite 12000 --questions 5 --relecture 8 --mise-en-page 10 --bat1 5 --bat2 3 --validation-vo 10 \\
      --fichiers 2 --debut 2026-11-02 --feries-fr --indispo 2026-12-24:2027-01-01 \\
      --etape "Relecture de l'auteur:3:relecture"
  python3 retroplanning.py --auto-test

--auto-test : refait des rétroplannings dont les dates ont été calculées à la main sur le calendrier
(jours fériés français, indisponibilités, remise un dimanche, validation par l'ayant droit, étape
ajoutée) ; il doit retrouver chaque date, dire « menacé » ou « marge faible » quand c'est le cas, et
rien de tel quand le jalon tient. --sortie ne remplace jamais un fichier existant.

Codes de sortie : 0 calcul fait (tenable ou menacé) ; 1 auto-test en échec ; 2 information manquante
ou invalide.
"""
import argparse
import contextlib
import io
import math
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import sortie_libre, ecrire_sortie  # noqa: E402

ETAPES = [  # (option, libellé) dans l'ordre de la chaîne ; la traduction est calculée à part
    ("questions", "Réponses aux dernières questions de l'éditeur et intégration"),
    ("relecture", "Relecture"),
    ("mise_en_page", "Mise en page"),
    ("bat1", "BAT1 : relecture de la 1re épreuve et retours"),
    ("bat2", "BAT2 : vérification de la 2e épreuve"),
    ("validation_vo", "Validation de la VF par l'éditeur de la VO ou l'ayant droit"),
    ("fichiers", "Fichiers d'impression"),
]
LIBELLES_OPTIONS = {
    "remise": "date de remise à l'imprimeur (--remise)",
    "caracteres": "volume total à traduire, en caractères espaces comprises, compté sur le fichier (--caracteres)",
    "capacite": "capacité de traduction d'Hervé, en caractères par jour ouvré (--capacite)",
    "relecture": "durée de la relecture, en jours ouvrés (--relecture)",
    "questions": "délai de réponse de l'éditeur aux dernières questions + intégration avant la relecture, "
                 "en jours ouvrés (--questions)",
    "validation_vo": "durée de la validation de la version française par l'éditeur de la version originale ou "
                     "l'ayant droit (licence, co-édition), en jours ouvrés (--validation-vo ; 0 si personne ne valide)",
    "mise_en_page": "durée de la mise en page, en jours ouvrés (--mise-en-page)",
    "bat1": "durée du cycle BAT1, en jours ouvrés (--bat1)",
    "bat2": "durée du cycle BAT2, en jours ouvrés (--bat2)",
    "fichiers": "durée de préparation des fichiers d'impression, en jours ouvrés (--fichiers)",
}
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def arret(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def jour_iso(texte, option):
    try:
        return date.fromisoformat(texte)
    except ValueError:
        arret(f"{option} : « {texte} » n'est pas une date AAAA-MM-JJ.")


def paques(annee):
    """Dimanche de Pâques (calendrier grégorien, algorithme de Meeus-Jones-Butcher)."""
    a, b, c = annee % 19, annee // 100, annee % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mois = (h + l - 7 * m + 114) // 31
    jour = (h + l - 7 * m + 114) % 31 + 1
    return date(annee, mois, jour)


def feries_france(annee):
    """Les 11 jours fériés nationaux (hors Alsace-Moselle et outre-mer)."""
    p = paques(annee)
    return {date(annee, 1, 1), p + timedelta(days=1), date(annee, 5, 1), date(annee, 5, 8),
            p + timedelta(days=39), p + timedelta(days=50), date(annee, 7, 14), date(annee, 8, 15),
            date(annee, 11, 1), date(annee, 11, 11), date(annee, 12, 25)}


class Calendrier:
    def __init__(self, semaine, feries_fr, indispo):
        self.semaine, self.feries_fr, self.indispo = semaine, feries_fr, indispo
        self._feries = {}

    def ouvre(self, d):
        if d.weekday() >= self.semaine:
            return False
        if self.feries_fr:
            if d.year not in self._feries:
                self._feries[d.year] = feries_france(d.year)
            if d in self._feries[d.year]:
                return False
        return not any(a <= d <= b for a, b in self.indispo)

    def dernier_ouvre(self, d):
        """Dernier jour ouvré à la date d ou avant."""
        while not self.ouvre(d):
            d -= timedelta(days=1)
        return d

    def recule(self, d, n):
        """Début d'une étape de n jours ouvrés qui finit le jour ouvré d."""
        while n > 1:
            d -= timedelta(days=1)
            if self.ouvre(d):
                n -= 1
        return d

    def veille(self, d):
        return self.dernier_ouvre(d - timedelta(days=1))

    def avance(self, d, n):
        """Fin d'une étape de n jours ouvrés qui commence au premier jour ouvré ≥ d."""
        while not self.ouvre(d):
            d += timedelta(days=1)
        while n > 1:
            d += timedelta(days=1)
            if self.ouvre(d):
                n -= 1
        return d

    def compter(self, debut, fin):
        """Nombre de jours ouvrés dans [debut, fin]."""
        n, d = 0, debut
        while d <= fin:
            n += self.ouvre(d)
            d += timedelta(days=1)
        return n


def fr(d):
    return f"{JOURS[d.weekday()]} {d.strftime('%d/%m/%Y')}"


# ------------------------------------------------------------------ auto-test
def _lancer(argv):
    """Lance le vrai programme (main) avec ces options ; renvoie (code de sortie, texte affiché)."""
    ancien, sortie = sys.argv, io.StringIO()
    sys.argv = ["retroplanning.py"] + argv
    try:
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            try:
                code = main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = ancien
    return code, sortie.getvalue()


def auto_test():
    """Des rétroplannings dont chaque date a été comptée à la main sur le calendrier, jamais
    recalculée par le programme qu'on vérifie."""
    commun = ["--produit", "Essai", "--remise", "2027-03-15", "--caracteres", "320000",
              "--relecture", "8", "--questions", "5", "--mise-en-page", "10", "--bat1", "5", "--bat2", "3",
              "--fichiers", "2", "--feries-fr", "--indispo", "2026-12-24:2027-01-01", "--aujourdhui", "2026-10-01"]
    base = commun + ["--capacite", "12000", "--validation-vo", "0"]
    licence = commun + ["--capacite", "12000", "--validation-vo", "10", "--debut", "2026-11-02",
                        "--etape", "Relecture de l'auteur:3:relecture"]
    cas = [
        # (nom, options, code attendu, morceaux qui doivent apparaître, morceaux qui ne doivent pas apparaître)
        ("calendrier et jalon tenable", base + ["--debut", "2026-11-02"], 0,
         ["| Traduction (320000 caractères à 12000 par jour) | vendredi 11/12/2026 | mercredi 27/01/2027 | 27 |",
          "| Réponses aux dernières questions de l'éditeur et intégration | jeudi 28/01/2027 | mercredi 03/02/2027 | 5 |",
          "| Relecture | jeudi 04/02/2027 | lundi 15/02/2027 | 8 |",
          "| Mise en page | mardi 16/02/2027 | lundi 01/03/2027 | 10 |",
          "| BAT1 : relecture de la 1re épreuve et retours | mardi 02/03/2027 | lundi 08/03/2027 | 5 |",
          "| BAT2 : vérification de la 2e épreuve | mardi 09/03/2027 | jeudi 11/03/2027 | 3 |",
          "| Validation de la VF par l'éditeur de la VO ou l'ayant droit | — | — | 0 (sans objet) |",
          "| Fichiers d'impression | vendredi 12/03/2027 | lundi 15/03/2027 | 2 |",
          "**TENABLE** — début possible le lundi 02/11/2026, marge de 28 jour(s) ouvré(s)"],
         ["MENACÉ", "DÉPASSÉ", "Ligne à ajouter à Core/Suivi.md", "Marge de 2 jours ouvrés ou moins"]),
        # gamme sous licence : 10 jours de validation par l'ayant droit et une étape ajoutée après la
        # relecture ; chaque date comptée à la main (11/11/2026 férié, 24/12/2026 au 01/01/2027 indisponible)
        ("validation par l'ayant droit et étape ajoutée", licence, 0,
         ["| Traduction (320000 caractères à 12000 par jour) | mardi 24/11/2026 | vendredi 08/01/2027 | 27 |",
          "| Réponses aux dernières questions de l'éditeur et intégration | lundi 11/01/2027 | vendredi 15/01/2027 | 5 |",
          "| Relecture | lundi 18/01/2027 | mercredi 27/01/2027 | 8 |",
          "| Relecture de l'auteur (étape ajoutée) | jeudi 28/01/2027 | lundi 01/02/2027 | 3 |",
          "| Mise en page | mardi 02/02/2027 | lundi 15/02/2027 | 10 |",
          "| BAT1 : relecture de la 1re épreuve et retours | mardi 16/02/2027 | lundi 22/02/2027 | 5 |",
          "| BAT2 : vérification de la 2e épreuve | mardi 23/02/2027 | jeudi 25/02/2027 | 3 |",
          "| Validation de la VF par l'éditeur de la VO ou l'ayant droit | vendredi 26/02/2027 | jeudi 11/03/2027 | 10 |",
          "| Fichiers d'impression | vendredi 12/03/2027 | lundi 15/03/2027 | 2 |",
          "**TENABLE** — début possible le lundi 02/11/2026, marge de 15 jour(s) ouvré(s)"],
         ["MENACÉ", "Marge de 2 jours ouvrés ou moins"]),
        ("validation par l'ayant droit non déclarée : refus, jamais supposée",
         commun + ["--capacite", "12000", "--debut", "2026-11-02"], 2,
         ["validation de la version française par l'éditeur de la version originale ou l'ayant droit"], ["| Traduction"]),
        ("étape ajoutée après une étape inconnue : refus", base + ["--etape", "Traduction de la FAQ:4:imprimeur"], 2,
         ["n'est pas une étape de la chaîne"], ["| Traduction"]),
        ("jalon menacé (indisponibilité de fin d'année)", base + ["--debut", "2027-01-04"], 0,
         ["**JALON MENACÉ** — début possible le lundi 04/01/2027 seulement : il manque 9 jour(s) ouvré(s).",
          "traduire 17778 caractères par jour ouvré au lieu de 12000 (sur 18 jours disponibles)",
          "confier environ 104000 caractères à un autre traducteur",
          "décaler la remise à l'imprimeur d'au moins 9 jour(s) ouvré(s)",
          "2026-10-01 — Essai : jalon menacé — traduction à commencer au plus tard le 11/12/2026 "
          "(début possible le 04/01/2027)"],
         ["**TENABLE**"]),
        ("marge faible", base + ["--debut", "2026-12-10"], 0,
         ["**TENABLE** — début possible le jeudi 10/12/2026, marge de 1 jour(s) ouvré(s)",
          "Marge de 2 jours ouvrés ou moins", "Essai : marge faible"],
         ["MENACÉ"]),
        ("capacité manquante : refus, jamais supposée", commun + ["--validation-vo", "0", "--debut", "2026-11-02"], 2,
         ["capacité de traduction d'Hervé"], ["| Traduction"]),
        ("rapport demandé dans le dossier du plugin : refus (il s'y perdrait)",
         base + ["--sortie", str(Path(__file__).resolve().parent / "retroplanning_essai.md")], 2,
         ["REFUS", "dossier du plugin AURA"], ["| Traduction"]),
        ("déjà traduit négatif : refus (le reste à traduire grossirait)", base + ["--deja-traduits", "-50000"], 2,
         ["--deja-traduits (-50000) doit être entre 0"], ["| Traduction"]),
        ("déjà traduit au-delà du total : refus", base + ["--deja-traduits", "400000"], 2,
         ["--deja-traduits (400000) doit être entre 0"], ["| Traduction"]),
    ]
    echecs = []
    for nom, argv, code_att, presents, absents in cas:
        code, texte = _lancer(argv)
        manquent = [m for m in presents if m not in texte]
        en_trop = [m for m in absents if m in texte]
        if code != code_att:
            manquent.append(f"code de sortie {code_att} (vu {code})")
        print(f"  {nom} : {'OK' if not (manquent or en_trop) else 'ÉCHEC'}")
        if manquent or en_trop:
            echecs.append(f"{nom} — non trouvé : {manquent} ; en trop : {en_trop}")
    # remise un dimanche, jours fériés de 2027 (Pâques le 28 mars) : comptés à la main
    code, texte = _lancer(["--remise", "2027-03-14", "--caracteres", "0", "--capacite", "1000", "--relecture", "0",
                           "--questions", "0", "--mise-en-page", "0", "--bat1", "0", "--bat2", "0", "--validation-vo", "0",
                           "--fichiers", "1", "--feries-fr", "--aujourdhui", "2026-10-01"])
    ok_dim = "(jour non travaillé : ramenée au vendredi 12/03/2027)" in texte and \
             "| Fichiers d'impression | vendredi 12/03/2027 | vendredi 12/03/2027 | 1 |" in texte
    print(f"  remise un dimanche : {'OK' if ok_dim else 'ÉCHEC'}")
    if not ok_dim:
        echecs.append("remise du dimanche 14/03/2027 non ramenée au vendredi 12/03/2027")
    feries_2027 = {date(2027, 1, 1), date(2027, 3, 29), date(2027, 5, 1), date(2027, 5, 6), date(2027, 5, 8),
                   date(2027, 5, 17), date(2027, 7, 14), date(2027, 8, 15), date(2027, 11, 1), date(2027, 11, 11),
                   date(2027, 12, 25)}
    vus = feries_france(2027)
    print(f"  jours fériés 2027 : {'OK' if vus == feries_2027 else 'ÉCHEC'}")
    if vus != feries_2027:
        echecs.append(f"jours fériés 2027 : manquent {sorted(feries_2027 - vus)}, en trop {sorted(vus - feries_2027)}")
    # --sortie ne remplace jamais un fichier existant (Livrables/ est la mémoire d'Hervé)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        notes = Path(d) / "planning.md"
        notes.write_text("PLANNING D'HERVÉ\n", encoding="utf-8")
        code, texte = _lancer(base + ["--debut", "2026-11-02", "--sortie", str(notes)])
        ok_s = code == 2 and "existe déjà" in texte and notes.read_text(encoding="utf-8") == "PLANNING D'HERVÉ\n"
    print(f"  fichier existant jamais remplacé : {'OK' if ok_s else 'ÉCHEC'}")
    if not ok_s:
        echecs.append(f"--sortie sur un fichier existant : refus attendu, fichier intact (vu code {code})")
    if echecs:
        print("AUTO-TEST ÉCHOUÉ — " + " ; ".join(echecs) + ". Ne pas se fier à ce rétroplanning.")
        return 1
    print("AUTO-TEST OK — dates comptées à la main toutes retrouvées (8 étapes, questions avant la relecture, "
          "validation par l'ayant droit, étape ajoutée, marge, retard et leviers, remise un dimanche, 11 jours "
          "fériés 2027) ; jalon menacé, marge faible, capacité et validation manquantes, étape inconnue et fichier "
          "existant signalés ; 0 fausse alerte quand le jalon tient")
    return 0


def main():
    if "--auto-test" in sys.argv[1:]:
        return auto_test()
    ap = argparse.ArgumentParser(description="Rétroplanning à rebours depuis la remise à l'imprimeur.")
    ap.add_argument("--produit", default="(produit non nommé)")
    ap.add_argument("--remise", help="date de remise des fichiers à l'imprimeur, AAAA-MM-JJ")
    ap.add_argument("--caracteres", type=int, help="volume total à traduire (caractères espaces comprises)")
    ap.add_argument("--deja-traduits", type=int, default=0, help="caractères déjà traduits (replanification en cours de projet)")
    ap.add_argument("--capacite", type=int, help="caractères traduits par Hervé par jour ouvré (à lui demander)")
    for option, _ in ETAPES:
        ap.add_argument("--" + option.replace("_", "-"), type=int, dest=option, help="jours ouvrés (0 si l'étape n'existe pas)")
    ap.add_argument("--etape", action="append", default=[],
                    help="étape propre à ce produit : \"Nom:jours:après\" (après = traduction, questions, relecture, "
                         "mise-en-page, bat1, bat2, validation-vo ou fichiers) ; se répète")
    ap.add_argument("--faq", type=int, help="jours ouvrés de FAQ après la remise (hors calcul, facultatif)")
    ap.add_argument("--debut", help="date à partir de laquelle Hervé peut traduire (sources reçues, ou aujourd'hui si déjà en cours)")
    ap.add_argument("--semaine", type=int, choices=(5, 6, 7), default=5, help="jours travaillés par semaine : 5 (lun-ven), 6 (lun-sam), 7")
    ap.add_argument("--feries-fr", action="store_true", help="exclut les 11 jours fériés nationaux français")
    ap.add_argument("--indispo", nargs="*", default=[], help="périodes non travaillées AAAA-MM-JJ:AAAA-MM-JJ")
    ap.add_argument("--aujourdhui", help="date du jour (tests) ; défaut : horloge de la machine")
    ap.add_argument("--sortie", help="écrit le rétroplanning dans ce nouveau fichier .md (jamais un fichier existant)")
    ap.add_argument("--auto-test", action="store_true",
                    help="essai sur des rétroplannings comptés à la main (aucune autre option)")
    a = ap.parse_args()
    sortie_libre(a.sortie)

    manquants = [LIBELLES_OPTIONS[k] for k in ["remise", "caracteres", "capacite"] + [o for o, _ in ETAPES]
                 if getattr(a, k) is None]
    if manquants:
        arret("Rétroplanning impossible : informations manquantes. À demander à Hervé, jamais à supposer :\n- "
              + "\n- ".join(manquants) + "\n(Une étape qui n'existe pas sur ce produit se déclare à 0.)")
    if a.capacite <= 0:
        arret("--capacite doit être un nombre de caractères strictement positif.")
    negatifs = [o for o, _ in ETAPES if getattr(a, o) < 0] + (["caracteres"] if a.caracteres < 0 else [])
    if negatifs:
        arret(f"Valeurs négatives refusées : {', '.join(negatifs)}.")
    if a.deja_traduits < 0 or a.deja_traduits > a.caracteres:
        arret(f"--deja-traduits ({a.deja_traduits}) doit être entre 0 et le nombre de caractères ({a.caracteres}).")
    indispo = []
    for p in a.indispo:
        if ":" not in p:
            arret(f"--indispo « {p} » : format attendu AAAA-MM-JJ:AAAA-MM-JJ.")
        d1, d2 = (jour_iso(x, "--indispo") for x in p.split(":", 1))
        indispo.append((min(d1, d2), max(d1, d2)))
    cal = Calendrier(a.semaine, a.feries_fr, indispo)
    remise = jour_iso(a.remise, "--remise")
    aujourdhui = jour_iso(a.aujourdhui, "--aujourdhui") if a.aujourdhui else date.today()
    reste = max(0, a.caracteres - a.deja_traduits)
    j_trad = math.ceil(reste / a.capacite) if reste else 0

    # la chaîne : traduction, étapes fixes, puis les étapes propres au produit, chacune après la sienne
    chaine = [("traduction", f"Traduction ({reste} caractères à {a.capacite} par jour)", j_trad)]
    chaine += [(o, lib, getattr(a, o)) for o, lib in ETAPES]
    for k, spec in enumerate(a.etape, 1):
        morceaux = spec.rsplit(":", 2)
        if len(morceaux) != 3 or not morceaux[0].strip() or not morceaux[1].strip().isdigit():
            arret(f"--etape « {spec} » : format attendu \"Nom:jours:après\" (ex. \"Relecture de l'auteur:3:relecture\").")
        nom, jours, apres = morceaux[0].strip(), int(morceaux[1]), morceaux[2].strip().replace("-", "_")
        cles = [c[0] for c in chaine]
        if apres not in cles:
            arret(f"--etape « {spec} » : « {morceaux[2]} » n'est pas une étape de la chaîne. Au choix : "
                  + ", ".join(c.replace("_", "-") for c in cles if not c.startswith("etape_")) + ".")
        pos = cles.index(apres) + 1
        while pos < len(chaine) and chaine[pos][0].startswith(f"etape_{apres}_"):
            pos += 1   # plusieurs étapes après la même : dans l'ordre donné
        chaine.insert(pos, (f"etape_{apres}_{k}", f"{nom} (étape ajoutée)", jours))

    # à rebours : chaque étape finit le jour ouvré qui précède le début de la suivante
    lignes, fin = [], cal.dernier_ouvre(remise)
    lignes.append(("Remise des fichiers à l'imprimeur", None, fin, None))
    for option, libelle, n in reversed(chaine):
        if n == 0:
            lignes.append((libelle, None, None, 0))
            continue
        debut = cal.recule(fin, n)
        lignes.append((libelle, debut, fin, n))
        if option == "traduction":
            debut_trad, fin_trad = debut, fin
        fin = cal.veille(debut)
    if j_trad == 0:
        debut_trad = fin_trad = None
    lignes.reverse()

    sortie = [f"# Rétroplanning — {a.produit}", "",
              f"Calculé le {fr(aujourdhui)} par le script retroplanning.py (calcul à rebours, jours ouvrés).", "",
              "**Hypothèses (toutes données par Hervé ou l'éditeur, aucune supposée) :**",
              f"- Remise à l'imprimeur : {fr(remise)}" + ("" if cal.ouvre(remise) else f" (jour non travaillé : ramenée au {fr(cal.dernier_ouvre(remise))})"),
              f"- Volume : {a.caracteres} caractères, dont {a.deja_traduits} déjà traduits ; reste {reste}",
              f"- Capacité de traduction : {a.capacite} caractères par jour ouvré",
              f"- Semaine de {a.semaine} jours ; jours fériés français exclus : {'oui' if a.feries_fr else 'non'}"
              + (" ; indisponibilités : " + ", ".join(f"du {x.strftime('%d/%m/%Y')} au {y.strftime('%d/%m/%Y')}" for x, y in indispo) if indispo else ""),
              "- Le même calendrier sert pour tout le monde (relecteur, maquettiste, éditeur) : à ajuster si leurs jours diffèrent.",
              "", "| Étape | Début au plus tard | Fin au plus tard | Jours ouvrés |", "|---|---|---|---|"]
    for libelle, debut, fin_l, n in lignes:
        if n == 0:
            sortie.append(f"| {libelle} | — | — | 0 (sans objet) |")
        elif n is None:
            sortie.append(f"| **{libelle}** | | **{fr(fin_l)}** | jalon |")
        else:
            sortie.append(f"| {libelle} | {fr(debut)} | {fr(fin_l)} | {n} |")
    if a.faq:
        d_faq = cal.avance(remise + timedelta(days=1), 1)
        sortie.append(f"| FAQ (après la remise, hors calcul) | {fr(d_faq)} | {fr(cal.avance(d_faq, a.faq))} | {a.faq} |")
    sortie.append("")

    menace, ligne_suivi = False, None
    if debut_trad is None:
        sortie.append("Rien à traduire : le jalon de départ est le début de la relecture.")
    else:
        sortie.append(f"**Jalon clé : la traduction doit commencer au plus tard le {fr(debut_trad)}** "
                      f"(sources reçues avant cette date).")
        depart = jour_iso(a.debut, "--debut") if a.debut else None
        if depart is not None:
            depart = cal.avance(depart, 1)  # premier jour ouvré à cette date ou après
        if depart is None:
            sortie.append("Marge non calculée : donne --debut (date de réception des sources, ou aujourd'hui si la traduction est en cours).")
            if debut_trad < aujourdhui:
                menace = True
                sortie.append(f"**JALON DÉPASSÉ :** ce début au plus tard est déjà passé (nous sommes le {fr(aujourdhui)}).")
        else:
            if depart <= debut_trad:
                marge = cal.compter(depart, debut_trad) - 1
                sortie.append(f"**TENABLE** — début possible le {fr(depart)}, marge de {marge} jour(s) ouvré(s) avant le début au plus tard.")
                if marge <= 2:
                    menace = True
                    sortie.append("Marge de 2 jours ouvrés ou moins : le moindre retard de sources fait glisser la remise. À surveiller.")
            else:
                menace = True
                retard = cal.compter(debut_trad, depart) - 1
                dispo = cal.compter(depart, fin_trad)
                sortie.append(f"**JALON MENACÉ** — début possible le {fr(depart)} seulement : il manque {retard} jour(s) ouvré(s).")
                leviers = []
                if dispo > 0:
                    requise = math.ceil(reste / dispo)
                    leviers.append(f"traduire {requise} caractères par jour ouvré au lieu de {a.capacite} (sur {dispo} jours disponibles)")
                    a_confier = reste - a.capacite * dispo
                    if a_confier > 0:
                        leviers.append(f"confier environ {a_confier} caractères à un autre traducteur (calcul : {reste} − {a.capacite} × {dispo})")
                else:
                    leviers.append("plus aucun jour disponible pour la traduction avant la fin au plus tard")
                leviers.append(f"décaler la remise à l'imprimeur d'au moins {retard} jour(s) ouvré(s) (décision de l'éditeur)")
                leviers.append("raccourcir une étape aval (relecture, mise en page, BAT) avec l'accord de ceux qui la font")
                sortie.append("Leviers chiffrés (à présenter à Hervé, aucun n'est décidé) :")
                sortie += [f"- {x}" for x in leviers]
            if menace:
                etat, action = (("jalon menacé", "choisir un levier avec Hervé") if depart > debut_trad
                                else ("marge faible", "surveiller la réception des sources"))
                ligne_suivi = (f"{aujourdhui.isoformat()} — {a.produit} : {etat} — traduction à commencer au plus tard le "
                               f"{debut_trad.strftime('%d/%m/%Y')} (début possible le {depart.strftime('%d/%m/%Y')}) pour une remise "
                               f"à l'imprimeur le {remise.strftime('%d/%m/%Y')}. Action : {action}.")
    if ligne_suivi:
        sortie += ["", "**Ligne à ajouter à Core/Suivi.md :**", "", ligne_suivi]
    texte = "\n".join(sortie)
    print(texte)
    if a.sortie:
        ecrire_sortie(a.sortie, texte + "\n")
        print(f"\nRétroplanning écrit dans {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
