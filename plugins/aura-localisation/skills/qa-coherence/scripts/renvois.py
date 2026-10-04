#!/usr/bin/env python3
"""Contrôle des renvois internes et des numéros de règle d'un texte (traduction, et sa VO si fournie).

Usage :
  python3 renvois.py TEXTE_FR [--source TEXTE_EN] [--regles LIVRET_FR]
  python3 renvois.py --auto-test    (essai sur des copies sabotées et des textes justes : chaque ligne doit dire OK)

  --source  la VO : compare les règles et le nombre de renvois de chaque côté.
  --regles  un autre fichier qui contient les règles visées (ex. : les cartes renvoient au livret).

Formats lus : .docx .xlsx .csv .tsv .txt .md (par lecture.py, copie identique dans ce dossier).

Ce que le script relève, avec le repère de chaque segment (§12 = 12e paragraphe Word,
L5 = 5e ligne, Cartes!L5C3 = cellule) :
  1. les règles numérotées : un segment qui COMMENCE par un numéro à plusieurs niveaux
     (« 5.2 Déplacement », « Règle 5.2 », « § 5.2 », « Rule 5.2 ») ;
  2. les renvois à plusieurs niveaux : un numéro précédé de près par « voir », « cf. », « règle »,
     « section », « paragraphe », « § » (« see », « rule », « section » en anglais), ou écrit entre
     parenthèses « (5.2) », et le second numéro d'une liste ou d'une plage écrite « 5.1 et 5.3 »,
     « 5.1 à 5.3 », « rules 5.1 to 5.3 » (lecture de la version d'origine, inchangée) ;
  3. ANOMALIES, sur les numéros à plusieurs niveaux seulement : renvoi vers une règle absente ; numéro
     défini deux fois ; trou dans une suite (5.1, 5.2, 5.4) ; numéro écrit avec une virgule (« règle 5,2 ») ;
  4. À LIRE, les renvois à UN seul niveau que le livret n'établit pas. Un tel renvoi est relevé juste
     après un mot-clé (« règle 7 », « section 3 », « chapitre 2 », « paragraphe 4 », « § 7 », « rule 7 »),
     « n° » compris (« règle n° 52 »), ou dans la suite d'une liste de renvois (« règles 3, 4 et 13 »,
     « règles 2.1, 4.3, 6.2 et 71 »),
     jamais après « voir » seul, ni devant un des noms qui comptent de la liste COMPTE, en minuscules
     (« règle 2 joueurs », « 3 cartes »). Il est
     ÉTABLI si le livret (ou --regles) a un titre à mot-clé (« Règle 7 — Égalités », « Chapitre 7 »,
     « Section 7 « … » », « Chapitre 7 Le combat » : après le numéro, un tiret, deux-points, guillemets,
     parenthèse, barre, la fin de la ligne ou un mot en MAJUSCULE ; « Règle 7 en cas d'égalité » et
     « Section 7 du plateau : … » ne sont pas des titres) ou des règles 7.1, 7.2. Dans un livret qui a
     des règles à plusieurs niveaux, un tel titre n'établit son numéro que s'il a des sous-règles
     (« Chapitre 5 » devant 5.1) ; sinon il est lui-même à lire : « Règle 52 : le défenseur gagne. » en
     tête d'un aide-mémoire peut être la faute « 52 » pour « 5.2 ». Sinon il est à lire : « section 2 du plateau », « règle
     12 du livret de campagne », une liste « 7. Le plus jeune commence » et la faute « règle 52 » pour
     « 5.2 » s'écrivent pareil, et aucune liste de mots ne les sépare sans se tromper (quatre essais l'ont
     montré). Ce n'est pas une anomalie, mais le code de sortie vaut 1 tant qu'il y en a ;
  5. renvois de PAGE (« page 12 », « p. 12 ») : à confirmer sur l'épreuve mise en page, jamais sur Word ;
  6. avec --source : règles de la VO absentes de la traduction, et renvois à plusieurs niveaux en nombre
     différent. Les renvois à un seul niveau n'y sont pas comptés (« section 7 of the board » devient
     « zone 7 du plateau ») ; la faute « règle 52 » s'y voit quand même, par le 5.2 que la VO a et pas elle.

Ce que le script NE fait PAS : juger le contenu (que la règle 5.2 parle bien de ce que le renvoi
promet se vérifie en lisant), ni voir une numérotation AUTOMATIQUE de Word (listes numérotées) : ces
numéros ne sont pas dans le texte. Dans ce cas il le dit et compare aux règles de --regles ou de la VO.
Limites : un numéro défini sous un autre mot-clé établit le renvoi (« Chapitre 7 » établit « règle 7 ») ; un
titre de chapitre sans sous-règles (« Chapitre 9 — Crédits ») dans un livret numéroté 5.1 sort à lire ; dans un
livret sans règles à plusieurs niveaux, une ligne ou une case qui commence comme un titre (« Règle 9 : le défenseur
gagne. ») établit la règle 9, même si elle n'existe pas ; une ligne « Règle 5.2 : … » qui reprend un titre compte
comme une seconde définition de 5.2 (comme la 3.0.0) ; une
liste des mots-clés est fermée (règle, section, chapitre, paragraphe, § et leurs équivalents anglais : « article 52 »,
« point 52 », « voir 52 » et « (52) » seuls ne sont pas relevés) ; un numéro mal formé (« 5-2 », « 5 2 », « 5. 2 »)
n'est lu que par sa première partie ; une liste reliée autrement que par « , », « et », « ou », « à », « & »,
« / » (« ainsi que 61 », « (et 53) ») s'arrête là ;
une case qui ne contient que « Règle 12 » (fichier de cartes) compte comme un titre ; « Section 9 Points
de victoire » dont la section 9 n'existe pas est à lire, mais « section 9 points » en minuscules est pris
pour un compte et n'est pas relevé ; dans une plage écrite avec un tiret (« rules 5.1–5.3 ») ou avec des
mots entre les numéros (« de la 5.1 à la 5.3 », « 5.1 jusqu'à 5.3 »), seul le premier numéro est relevé : si
l'autre langue l'écrit « 5.1 à 5.3 », la comparaison avec la VO le signale dans « Renvois en nombre
différent » (comme la 3.0.0) ; au-delà du 2e numéro d'une liste à plusieurs niveaux (« 2.1, 4.3, 6.2 »), les
suivants ne sont ni vérifiés ni comptés (comme la 3.0.0), sauf un numéro à un seul niveau, relevé à lire ;
la liste des noms qui comptent est courte : un nombre qui suit un renvoi et compte autre chose (« règle 5.1,
10 PV par ville », « règle 3.3 à 6 cibles ») sort à lire.

Le texte est d'abord normalisé (NFC) : « règle » écrit avec un accent décomposé reste « règle ».

Codes de sortie : 0 = aucune anomalie et rien à lire ; 1 = anomalies à voir, renvois à lire, ou contrôle
incomplet ; 2 = fichier illisible.
"""
import argparse
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lecture  # noqa: E402

NUM = r"\d{1,3}(?:\.\d{1,3})+[a-z]?"
NUM_VIRGULE = r"\d{1,3},\d{1,3}"
ESP = r"[ \u00a0\u202f\t]"  # espace ordinaire, insécable U+00A0, fine insécable U+202F, tabulation
MOTS = (r"voir|cf\.?|consultez|reportez-vous|se reporter|r[èe]gles?|sections?|paragraphes?|"
        r"see|refer(?:\s+to)?|rules?")
CLE = rf"(?:(?<!\w)(?:{MOTS})|§)"

DEFINITION = re.compile(
    rf"^{ESP}*(?:(?:r[èe]gle|rule|section|paragraphe|§){ESP}*)?({NUM})\.?(?:{ESP}|[—–:-]|$)", re.IGNORECASE)
# Numéro à UN seul niveau : accepté seulement derrière un mot-clé explicite, suivi au plus de « n° » ou « numéro »
# (« Règle 7 — Égalités » en tête de segment ; « voir règle 7 », « règle 52 » dans le texte).
MOT_SIMPLE = (r"r[èe]gles?|rules?|sections?|chapitres?|chapters?|paragraphes?|paragraphs?|§")
SIMPLE = r"\d{1,3}[a-z]?"
COMPTE = (r"joueu(?:r|se)s?|players?|cartes?|cards?|jetons?|tokens?|points?|d[ée]s|dice|tours?|turns?|"
          r"rounds?|manches?|fois|times?|cases?|spaces?")
# Entre un mot-clé et un numéro à UN seul niveau : toute espace, même invisible (fine, cadratin, sans chasse,
# trait d'union conditionnel), et au plus « n° », « numéro » ou un guillemet. Les numéros à plusieurs niveaux
# gardent ESP (lecture de la 3.0.0).
ESP_LARGE = r"[\s\u00a0\u202f\u2000-\u200b\u00ad]"
NUMERO = rf"(?:n[°ºo˚ᵒ]\.?{ESP_LARGE}*|num(?:[ée]ro{ESP_LARGE}+|\.{ESP_LARGE}*))?[«\"“]?{ESP_LARGE}*"
DEFINITION_SIMPLE = re.compile(
    rf"^{ESP}*(?:{MOT_SIMPLE}){ESP}*{NUMERO}({SIMPLE})\.?(?:{ESP}*[—–:|/(«\"“-]|{ESP}*$|{ESP}+(?=(?-i:[A-ZÀ-ÝŒŸ])))", re.IGNORECASE)
RENVOI_SIMPLE = re.compile(
    rf"(?<!\w)(?:{MOT_SIMPLE}){ESP_LARGE}*{NUMERO}(?P<num>{SIMPLE})(?![\d\w]|[.,]\d)(?!{ESP}+(?-i:{COMPTE})\b)", re.IGNORECASE)
# Titre à un seul niveau SANS mot-clé (« 3. Déplacement ») : il prouve que la règle 3 existe, mais ne
# compte ni dans les doublons ni dans les trous (une liste numérotée « 1. Piochez… » a la même forme).
TITRE_SIMPLE = re.compile(rf"^{ESP}*(\d{{1,3}})\.{ESP}+(?=[A-ZÀ-Ý])")
# Mot-clé, puis au plus 25 caractères sans ponctuation forte, puis le numéro (« voir la règle 5.2 »).
RENVOI_MOT = re.compile(rf"{CLE}(?P<entre>[^.;:!?\n]{{0,25}}?)(?P<num>{NUM})(?!\d)", re.IGNORECASE)
RENVOI_PAREN = re.compile(rf"\({ESP}*(?P<num>{NUM}){ESP}*\)")
# « règles 5.2 et 5.3 », « règles 5.1 à 5.3 », « rules 5.1 to 5.3 » : le 2e numéro à plusieurs niveaux suit le
# 1er sans mot-clé (lecture de la version d'origine, gardée telle quelle : la comparaison avec la VO en dépend).
SUITE = re.compile(rf"(?P<num>{NUM}){ESP}*(?:et|ou|and|or|,|à|to){ESP}*(?P<num2>{NUM})(?!\d)")
# La suite d'une liste de renvois, lue maillon par maillon depuis chaque renvoi relevé : « règles 3, 4 et 13 »,
# « règles 2.1, 4.3, 6.2 et 71 ». Un numéro à UN seul niveau trouvé ainsi va dans les renvois À LIRE ; les
# numéros à plusieurs niveaux au-delà du 2e ne sont ni vérifiés ni comptés (lecture de la 3.0.0, inchangée).
MAILLON = re.compile(rf"{ESP}*(?:,?{ESP}*(?:et|ou|and|or)\b|,|à|to\b|&|/){ESP}*(?:(?:la|le|les|the){ESP}+)?"
                     rf"(?P<num>\d{{1,3}}(?:\.\d{{1,3}})*[a-z]?)"
                     rf"(?![\d\w]|[.,]\d)", re.IGNORECASE)
QUANTITE = re.compile(rf"{ESP}+(?-i:{COMPTE})\b")
VIRGULE = re.compile(rf"{CLE}{ESP}*(?P<num>{NUM_VIRGULE})(?!\d)", re.IGNORECASE)
PAGE = re.compile(rf"(?<!\w)(?:pages?|pg\.|p\.){ESP}*(?P<num>\d{{1,3}})(?!\d)", re.IGNORECASE)
MARQUEUR_PAGE = re.compile(r"\[PAGE À CONFIRMER[^\]]*\]", re.IGNORECASE)


def extrait(texte, span, large=35):
    a, b = max(0, span[0] - large), min(len(texte), span[1] + large)
    return ("…" if a else "") + texte[a:b].replace("\n", " ") + ("…" if b < len(texte) else "")


def analyser(chemin):
    """(segments, definitions, renvois, virgules, pages, simples). definitions et renvois ne portent que
    sur les numéros à plusieurs niveaux (5.2), les seuls que le programme juge. simples : ce qu'il relève
    des numéros à un seul niveau, {"definis": numéro -> [repères] (« Règle 7 — Égalités »), "titres":
    numéros en tête de segment (« 3. Déplacement », mais aussi une étape de liste « 3. Piochez… »),
    "renvois": [(repère, numéro, extrait)]}."""
    segments = lecture.textes(chemin)
    definitions = defaultdict(list)   # numéro -> [repères]
    renvois = []                      # (repère, numéro, extrait)
    virgules = []                     # (repère, texte trouvé)
    pages = []                        # (repère, numéro, marqueur [PAGE À CONFIRMER] présent ?)
    simples = {"definis": defaultdict(list), "titres": set(), "renvois": [], "titres_def": []}
    for repere, texte in segments:
        texte = unicodedata.normalize("NFC", texte)     # « règle » écrit avec un accent décomposé (e + ̀)
        t = TITRE_SIMPLE.match(texte)
        if t:
            simples["titres"].add(t.group(1))
        m = DEFINITION.match(texte)
        d = None if m else DEFINITION_SIMPLE.match(texte)
        if m:
            definitions[m.group(1)].append(repere)
        if d:
            simples["definis"][d.group(1)].append(repere)
            simples["titres_def"].append((repere, d.group(1), extrait(texte, d.span(1))))
        span_def = (m or d).span(1) if (m or d) else None

        def noter(num, span):
            (renvois if "." in num else simples["renvois"]).append((repere, num, extrait(texte, span)))
        vus = set()
        for rx in (RENVOI_MOT, RENVOI_PAREN, RENVOI_SIMPLE):
            for r in rx.finditer(texte):
                span = r.span("num")
                if span == span_def or span in vus:
                    continue
                vus.add(span)
                noter(r.group("num"), span)
        for r in SUITE.finditer(texte):
            if r.span("num") in vus and r.span("num2") not in vus:
                vus.add(r.span("num2"))
                noter(r.group("num2"), r.span("num2"))
        for depart in sorted(vus):
            pos = depart[1]
            while (r := MAILLON.match(texte, pos)) and not QUANTITE.match(texte, r.end("num")):
                if "." not in r.group("num") and r.span("num") not in vus:
                    vus.add(r.span("num"))
                    noter(r.group("num"), r.span("num"))
                pos = r.end("num")
        virgules += [(repere, r.group(0).strip()) for r in VIRGULE.finditer(texte)]
        marque = bool(MARQUEUR_PAGE.search(texte))
        pages += [(repere, r.group("num"), marque) for r in PAGE.finditer(texte)]
    return segments, definitions, renvois, virgules, pages, simples


def existe(num, reference):
    """Un renvoi à UN seul niveau est établi si son numéro est défini, ou si c'est le parent de règles
    définies (« section 5 » quand le livret a 5.1 et 5.2). Un renvoi à plusieurs niveaux, lui, doit viser un
    numéro défini : « 5.1 » dont le titre a perdu son numéro reste introuvable, même si 5.1.1 existe."""
    return num in reference or any(r.startswith(num + ".") for r in reference)


def cle_tri(num):
    return [(0, int(p)) if p.isdigit() else (1, p) for p in re.findall(r"\d+|[a-z]", num)]


def trous(definitions):
    """Suites interrompues : 5.1, 5.2, 5.4 -> 5.3 manque (dernier niveau numérique seulement)."""
    par_parent = defaultdict(set)
    for n in definitions:
        parent, _, dernier = n.rpartition(".")
        if dernier.isdigit():
            par_parent[parent].add(int(dernier))
    manques = [f"{p}.{i}" if p else str(i) for p, vus in par_parent.items() if len(vus) > 1
               for i in range(min(vus), max(vus)) if i not in vus]
    return sorted(manques, key=cle_tri)


A_LIRE = ("À lire : renvoi à un seul niveau que le programme ne peut pas établir (zone du plateau, autre "
          "document, étape d'une liste, ou faute de numéro comme « 52 » pour « 5.2 »)")


def controler(res, src=None, ext=None):
    """Toutes les vérifications, sans rien afficher : (rubriques, a_lire, avertissements, incomplet).
    Les anomalies ne portent que sur les numéros à plusieurs niveaux (5.2). Un renvoi à un seul niveau
    (« règle 7 ») est ÉTABLI si le livret, ou --regles, a un titre « Règle 7 — … », « Chapitre 7 »… ou des
    règles 7.1, 7.2 ; sinon il est dans a_lire, jamais une anomalie : « section 2 du plateau », « règle 12 du
    livret de campagne », une liste « 7. Le plus jeune commence » et la faute « 52 » s'écrivent pareil, et
    aucune liste de mots ne les sépare. a_lire met le code de sortie à 1 : quelqu'un doit les lire. Les
    renvois à un seul niveau ne sont pas comptés dans la comparaison avec la VO (« section 7 of the board »
    devient « zone 7 du plateau ») ; la faute « 52 » pour « 5.2 » s'y voit quand même, par le 5.2 perdu."""
    _, defs, renv, virg, pages, simples = res
    rubriques, avertissements, incomplet = [], [], False
    trie = lambda d: sorted(d.items(), key=lambda kv: cle_tri(kv[0]))  # noqa: E731

    # Les règles qui existent : celles du texte, plus celles de --regles.
    reference = set(defs) | (set(ext[1]) if ext else set())
    titres_un = set(simples["definis"]) | (set(ext[5]["definis"]) if ext else set())
    titres = simples["titres"] | (ext[5]["titres"] if ext else set())
    if not reference:
        avertissements.append("Aucune règle numérotée à plusieurs niveaux (« 5.2 ») trouvée : soit le texte n'en a pas, "
                              "soit Word les génère par numérotation automatique (invisible pour le script).")
        if src and src[1]:
            avertissements.append("Les renvois sont comparés aux règles de la VO (la structure est en général la même).")
            reference = set(src[1])
            titres_un |= set(src[5]["definis"])
        else:
            avertissements.append("L'existence des règles visées n'est PAS vérifiée : à contrôler en lisant"
                                  + (" (le fichier --regles n'a pas de règles à plusieurs niveaux)." if ext
                                     else ", ou relancer avec --regles."))
            reference = None
            incomplet = bool(renv)

    if reference is not None:
        rubriques.append(("Renvoi vers une règle introuvable",
                          [f"{r} : « {n} » — {x}" for r, n, x in renv if n not in reference]))
    # Un titre à un seul niveau (« Règle 7 — Égalités », « Chapitre 3 ») établit son numéro dans un livret qui n'a
    # pas de règles à plusieurs niveaux. Dans un livret numéroté 5.1, 5.2, il ne l'établit que s'il a des
    # sous-règles (« Chapitre 5 » devant 5.1) : sinon, il est lui-même à lire (« Règle 52 : … » pour « 5.2 »).
    plusieurs = bool(reference)
    etablis = {n for n in titres_un if not plusieurs or existe(n, reference)}
    a_lire = [f"{r} : « {n} » — {x} (titre à un seul niveau sans règle {n}.1, {n}.2… : titre de chapitre, ou faute "
              f"comme « Règle 52 : » pour « 5.2 » ?)" for r, n, x in simples["titres_def"] if n not in etablis]
    a_lire += [f"{r} : « {n} » — {x}" + (f" (un titre « {n}. » existe : la règle visée, ou une étape de liste ?)"
                                           if n in titres else "")
               for r, n, x in simples["renvois"] if n not in etablis and not existe(n, reference or set())]
    rubriques.append(("Numéro de règle défini plusieurs fois",
                      [f"{n} : {', '.join(rs)}" for n, rs in trie(defs) if len(rs) > 1]))
    rubriques.append(("Trou dans la numérotation (règle manquante ou numéro glissé ?)",
                      [f"{n} absent entre ses voisins" for n in trous(defs)]))
    rubriques.append(("Numéro écrit avec une virgule (le livret utilise-t-il le point ?)",
                      [f"{r} : « {x} »" for r, x in virg]))
    if src:
        _, sdefs, srenv, _, spages, _ = src
        if defs:
            rubriques.append(("Règle présente dans la VO, absente de la traduction",
                              [f"{n} (VO : {', '.join(rs)})" for n, rs in trie(sdefs) if n not in defs]))
            rubriques.append(("Règle présente dans la traduction, absente de la VO",
                              [f"{n} ({', '.join(rs)})" for n, rs in trie(defs) if n not in sdefs]))
        c_fr, c_en = Counter(n for _, n, _ in renv), Counter(n for _, n, _ in srenv)
        rubriques.append(("Renvois en nombre différent entre la VO et la traduction",
                          [f"vers {n} : VO {c_en[n]} · traduction {c_fr[n]}"
                           for n in sorted(set(c_fr) | set(c_en), key=cle_tri) if c_fr[n] != c_en[n]]))
        if len(pages) != len(spages):
            rubriques.append(("Renvois de page en nombre différent", [f"VO {len(spages)} · traduction {len(pages)}"]))
    return [(titre, lignes) for titre, lignes in rubriques if lignes], a_lire, avertissements, incomplet


def auto_test():
    """Copie sabotée : un livret et sa VO où des fautes connues ont été glissées exprès, et des textes justes
    écrits de toutes les façons qui ont trompé les versions précédentes."""
    import tempfile
    fr = ["1.1 Mise en place", "Prenez 3 jetons (voir 5.1).", "5.1 Déplacement", "Voir la règle 8.2.",
          "5.2 Combat", "Voir la règle 5,2, page 14.", "5.4 Terrain", "6.1 Fin de manche", "6.1 Fin de partie",
          "Voir règle 7 pour les égalités.",            # renvoi à un seul niveau vers une règle absente
          "En cas de doute, voir la règle 52.",          # « 52 » pour « 5.2 »
          "La règle 2 joueurs se joue sans le plateau.",  # un compte, pas un renvoi
          "Voir les règles 5.1 et 5.4."]                 # le 2e numéro d'une liste est aussi un renvoi
    en = ["1.1 Setup", "Take 3 tokens (see 5.1).", "5.1 Movement", "See rule 5.3.", "5.2 Combat",
          "See rule 5.2, page 14.", "5.3 Wounds", "5.4 Terrain", "6.1 End of round", "6.2 End of game", "7.3 Ties",
          "In doubt, see rule 5.2.", "Play the 2-player rule without the board.", "See rules 5.1 and 5.4."]
    attendus = {
        "Renvoi vers une règle introuvable": "8.2",
        "Numéro de règle défini plusieurs fois": "6.1",
        "Trou dans la numérotation (règle manquante ou numéro glissé ?)": "5.3",
        "Numéro écrit avec une virgule (le livret utilise-t-il le point ?)": "5,2",
        "Règle présente dans la VO, absente de la traduction": "7.3",
        "Renvois en nombre différent entre la VO et la traduction": "vers 5.2 :",   # le 5.2 perdu dans « 52 »
    }
    with tempfile.TemporaryDirectory() as d:
        def lire(nom, lignes):
            f = Path(d) / nom
            f.write_text("\n".join(lignes), encoding="utf-8")
            return analyser(f)
        res, src = lire("fr.txt", fr), lire("en.txt", en)
        rub, a_lire, _, _ = controler(res, src)
        trouvees = dict(rub)
        pages = res[4]
        # livret à un seul niveau : « Règle 2 — Combat » établit la règle 2 ; un renvoi vers la 5 est à lire
        un_rub, un_lire, _, _ = controler(lire("un_niveau.txt", [
            "Règle 1 — Mise en place", "Voir règle 2.", "Règle 2 — Combat", "Règle 4 — Fin de partie", "Voir règle 5."]))
        # chapitres et sections qui repartent à 1, titres suivis de guillemets ou de parenthèses, zones du
        # plateau, liste numérotée qui atteint 7, titre en majuscule après le numéro : aucune anomalie
        ch_rub, ch_lire, _, _ = controler(lire("chapitres.txt", [
            "Chapitre 1 — Mise en place", "Section 1 — Les pions", "Chapitre 2 (avancé) — Le brouillard",
            "Section 1 — Les cartes", "Chapitre 3 « Le combat »", "1. Le plus âgé mélange.", "7. Le plus jeune commence.",
            "Placez le jeton dans la section 7 du plateau.", "Voir la section 9 Points de victoire.",
            "Voir règle 7 pour les égalités.", "Voir le chapitre 2."]))
        # aide-mémoire en tête de segment (« Règle 7 en cas d'égalité. ») : ce n'est pas un titre ; listes de
        # profondeurs différentes et fin de plage absentes : introuvables
        am_rub, am_lire, _, _ = controler(lire("aide.txt", [
            "5.1 Attaque", "5.2 Défense", "6.1 Fin", "Règle 52 pour résoudre un combat.", "Règle 7 en cas d'égalité.",
            "Section 7 du plateau : posez-y la pioche.", "Voir 5.1 et 5.1.3.", "Voir les règles 5.1 à 5.9.",
            "Règle 53 : le défenseur gagne les égalités.", "Chapitre 5 — Le combat"]))
        # le titre « 5.1 » a perdu son numéro, ses sous-règles restent : « voir la règle 5.1 » est introuvable ;
        # une longue liste qui finit par « 71 », et « règle n° 52 » : à lire
        lo_rub, lo_lire, _, _ = controler(lire("liste.txt", [
            "2.1 Tour", "4.3 Fin", "5.1.1 Mêlée", "5.1.2 Tir", "5.2 Défense", "6.2 Score", "Attaque",
            "Pour attaquer, voir la règle 5.1.", "Voir les règles 2.1, 4.3, 6.2 et 71.", "Voir la règle n° 52."]))
        # livret à plusieurs niveaux : titres sans mot-clé, numéro parent, listes numérotées
        ti_rub, ti_lire, _, _ = controler(lire("titres.txt", [
            "3. Déplacement", "1. Piochez une carte.", "Voir règle 3.", "5.1 Attaque", "5.2 Défense",
            "1. Prenez un jeton.", "Voir la section 5.", "Voir règle 9.", "Placez le jeton dans la section 2 du plateau.",
            "Appliquez la règle 8 durant la phase.", "See rule 6 only once."]))
        # la VO et sa traduction juste, quelle que soit la tournure : aucune anomalie
        vo_rub, vo_lire, _, _ = controler(
            lire("fr_juste.txt", ["5.1 Attaque", "5.2 Défense", "Placez-les dans les sections 5 et 6 du plateau.",
                                  "Appliquez la règle 6 en entier.", "Appliquez la règle 9 d'abord.",
                                  "Voir les règles 12 et 13 du livret.", "Posez-le dans la zone 7 du plateau.",
                                  "Lisez le paragraphe 112.", "Voir la section 6 Points de victoire.",
                                  "Voir les règles de la 5.1 à la 5.2.", "Voir les règles 5.1 à 5.2.",
                                  "Résolvez dans l'ordre de la règle 5.1 à la règle 5.2.",
                                  "Appliquez les règles comprises entre 5.1 et 5.2.", "(voir règle 5, 5.1 et 5.2)"]),
            lire("en_juste.txt", ["5.1 Attack", "5.2 Defense", "Place them in sections 5 and 6 of the board.",
                                  "Apply rule 6 in full.", "Apply rule 9 first.", "See rules 12 and 13 of the booklet.",
                                  "Place it in section 7 of the board.", "Read entry 112.",
                                  "See section 6 Victory Points.", "See rules 5.1–5.2.", "See rules 5.1 to 5.2.",
                                  "Resolve rules 5.1 to 5.2 in order.", "Apply rules 5.1 to 5.2.",
                                  "(see rule 5, especially 5.1 and 5.2)"]))
        # « 5.1 à 52 » face à « 5.1 to 5.2 » : le 5.2 perdu se voit ; « 52 » et le 3e numéro d'une liste à lire
        pl_rub, pl_lire, _, _ = controler(
            lire("plage_fr.txt", ["3.1 Tour", "4.1 Fin", "5.1 Attaque", "5.2 Défense", "Pour le combat, voir les règles 5.1 à 52.",
                                  "Pour finir, voir les règles 3, 4 et 13."]),
            lire("plage_en.txt", ["3.1 Turn", "4.1 End", "5.1 Attack", "5.2 Defense", "For combat, see rules 5.1 to 5.2.",
                                  "Finally, see rules 3, 4 and 13."]))
    ok = True

    def voir(quoi, vu):
        nonlocal ok
        print(f"  {quoi} : {'OK' if vu else 'ÉCHEC'}")
        ok &= bool(vu)
    for titre, cle in attendus.items():
        voir(f"{titre} — {cle}", any(cle in l for l in trouvees.get(titre, [])))
    voir("Renvoi de page sans marqueur — page 14", any(n == "14" and not m for _, n, m in pages))
    voir("« règle 7 » et « règle 52 » à lire", all(any(c in l for l in a_lire) for c in ("« 7 »", "« 52 »")))
    voir("Second numéro d'une liste (« règles 5.1 et 5.4 »)", any(n == "5.4" for _, n, _ in res[2]))
    voir("« règle 2 joueurs » n'est pas un renvoi", not any("« 2 »" in l for l in a_lire))
    voir("Livret à un seul niveau : 0 anomalie, règle 2 établie, renvoi vers 5 à lire",
         not un_rub and any("« 5 »" in l for l in un_lire) and not any("« 2 »" in l for l in un_lire))
    voir(f"Chapitres, sections, zones, liste « 7. » : 0 anomalie, 7 et 9 à lire, 1, 2, 3 établis ({ch_rub} ; {ch_lire})",
         not ch_rub and any("« 7 »" in l and "étape de liste" in l for l in ch_lire) and any("« 9 »" in l for l in ch_lire)
         and not any(f"« {n} »" in l for l in ch_lire for n in ("1", "2", "3")))
    intr = dict(am_rub).get("Renvoi vers une règle introuvable", [])
    voir(f"Aide-mémoire « Règle 7 en cas d'égalité. », « Section 7 du plateau : », « Règle 53 : … » : 52, 7 et 53 "
         f"à lire, « Chapitre 5 » établi par 5.1 ; 5.1.3 et 5.9 "
         f"introuvables ({am_rub} ; {am_lire})",
         any("« 52 »" in l for l in am_lire) and sum("« 7 »" in l for l in am_lire) == 2
         and any("5.1.3" in l for l in intr) and any("5.9" in l for l in intr)
         and any("« 53 »" in l for l in am_lire) and not any("« 5 »" in l for l in am_lire))
    voir(f"Titre « 5.1 » perdu : « règle 5.1 » introuvable ; « 2.1, 4.3, 6.2 et 71 » et « n° 52 » à lire "
         f"({lo_rub} ; {lo_lire})",
         any("« 5.1 »" in l for l in dict(lo_rub).get("Renvoi vers une règle introuvable", []))
         and any("« 71 »" in l for l in lo_lire) and any("« 52 »" in l for l in lo_lire))
    voir(f"Livret à plusieurs niveaux : 0 anomalie, 9, 8, 6, 2 et 3 (titre ou liste) à lire, section parente 5 établie",
         not ti_rub and all(any(f"« {n} »" in l for l in ti_lire) for n in ("9", "8", "6", "2", "3"))
         and not any("« 5 »" in l for l in ti_lire))
    voir(f"VO et traduction justes (liste, plage, zone, autre livret, mot qui change) : 0 anomalie ({vo_rub})", not vo_rub)
    voir(f"« 5.1 à 52 » face à « 5.1 to 5.2 » : 5.2 perdu vu par la VO, 52 et 13 à lire ({pl_rub} ; {pl_lire})",
         any("vers 5.2 :" in l for l in dict(pl_rub).get("Renvois en nombre différent entre la VO et la traduction", []))
         and any("« 52 »" in l for l in pl_lire) and any("« 13 »" in l for l in pl_lire))
    print("AUTO-TEST " + ("OK — les fautes glissées sont trouvées (« règle 52 » par le 5.2 perdu et à lire, « règle 7 » "
                          "à lire), 0 anomalie sur des textes justes écrits de 6 façons."
                          if ok else "ÉCHOUÉ : ne pas se fier à ce contrôle."))
    sys.exit(0 if ok else 1)


def main():
    if "--auto-test" in sys.argv:
        auto_test()
    ap = argparse.ArgumentParser(description="Renvois internes et numéros de règle.")
    ap.add_argument("texte", help="la traduction (.docx .xlsx .csv .tsv .txt .md)")
    ap.add_argument("--source", help="la VO, pour comparer les règles et les renvois")
    ap.add_argument("--regles", help="fichier qui contient les règles visées (ex. : le livret, pour un fichier de cartes)")
    ap.add_argument("--max", type=int, default=40, help="nombre maximal de lignes affichées par rubrique")
    a = ap.parse_args()

    try:
        res = analyser(a.texte)
        src = analyser(a.source) if a.source else None
        ext = analyser(a.regles) if a.regles else None
    except Exception as e:  # fichier absent, zip abîmé, format non pris en charge
        print(f"Fichier illisible : {e}")
        sys.exit(2)
    seg, defs, renv, _, pages, simples = res

    print(f"RENVOIS ET NUMÉROS DE RÈGLE — {Path(a.texte).name}")
    print(f"Segments lus : {len(seg)} · règles numérotées trouvées : {len(defs)} · "
          f"renvois : {len(renv)} · à un seul niveau : {len(simples['renvois'])} · renvois de page : {len(pages)}")
    if src:
        print(f"VO {Path(a.source).name} : règles numérotées {len(src[1])} · renvois {len(src[2])} · "
              f"renvois de page {len(src[4])}")
    if ext:
        print(f"Règles lues dans {Path(a.regles).name} : {len(ext[1])}")
    print()

    rubriques, a_lire, avertissements, incomplet = controler(res, src, ext)
    for i, av in enumerate(avertissements):
        print(("! " if i == 0 else "  ") + av)
    if avertissements:
        print()
    anomalies = 0
    for titre, lignes in rubriques:
        anomalies += len(lignes)
        print(f"{titre} ({len(lignes)})")
        for l in lignes[: a.max]:
            print("  " + l)
        if len(lignes) > a.max:
            print(f"  … et {len(lignes) - a.max} de plus (--max pour tout afficher)")
        print()

    if a_lire:
        print(f"{A_LIRE} ({len(a_lire)})")
        for l in a_lire[: a.max]:
            print("  " + l)
        if len(a_lire) > a.max:
            print(f"  … et {len(a_lire) - a.max} de plus (--max pour tout afficher)")
        print()

    if pages:
        sans = sum(1 for p in pages if not p[2])
        print(f"Renvois de page à confirmer sur l'épreuve mise en page : {len(pages)} "
              f"(dont {sans} sans le marqueur [PAGE À CONFIRMER])")
        for r, n, m in pages[: a.max]:
            print(f"  {r} : page {n}" + ("" if m else " — marqueur absent"))
        print()

    tous = renv + simples["renvois"]
    if tous:
        print(f"Renvois trouvés ({len(tous)}) — leur CONTENU reste à vérifier en lisant :")
        for r, n, x in tous[: a.max]:
            print(f"  {r} → {n} : {x}")
        if len(tous) > a.max:
            print(f"  … et {len(tous) - a.max} de plus (--max pour tout afficher)")
        print()

    print(f"BILAN : {anomalies} anomalie(s) de renvoi ou de numérotation"
          + (f" ; {len(a_lire)} renvoi(s) à lire." if a_lire else ".")
          + (" CONTRÔLE INCOMPLET : l'existence des règles visées n'a pas été vérifiée." if incomplet else ""))
    sys.exit(1 if anomalies or a_lire or incomplet else 0)


if __name__ == "__main__":
    main()
