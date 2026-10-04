#!/usr/bin/env python3
"""La preuve que la mise à jour n'a touché à rien de ce qu'Hervé avait déjà fait.

  python3 releve.py avant "<HERVÉ WORLD>"   → avant la PREMIÈRE écriture : relève chaque fichier (taille, sha256)
  python3 releve.py apres "<HERVÉ WORLD>"   → après la dernière : compare au relevé, octet pour octet, et écrit la
                                              preuve lisible _archives-systeme/PREUVE_MISE_A_JOUR_AAAA-MM-JJ.md
  python3 releve.py --auto-test             → essai sur des dossiers fabriqués, sabotages compris

Ce que le programme sait des chemins vient de ../references/couches.json (une seule écriture) :
  - les fichiers système (l'amorce CLAUDE.md, Core/VERSION.md, systeme_local, systeme_si_dossier_present, le document
    du bandeau) peuvent être remplacés ou créés, chacun à sa condition, et la preuve VÉRIFIE cette condition :
      · CLAUDE.md et Core/Skills.md (que l'AURA 2.0 enrichissait) : l'ancien était celui d'origine (empreintes_v2),
        ou déjà identique au nouveau, ou une copie de même empreinte existe dans _archives-systeme/ ;
      · le document du bandeau : seulement s'il existait, et seulement une ligne d'avertissement en tête (le reste
        identique octet pour octet) ;
      · systeme_si_dossier_present : seulement si son dossier existait déjà ;
      · un fichier système qui disparaît est une faute ;
  - les graines peuvent être créées ;
  - TOUT LE RESTE est la mémoire d'Hervé : chaque fichier doit être identique, octet pour octet, et toujours là.
  - les copies déjà présentes dans _archives-systeme/ ne doivent être ni modifiées ni supprimées.
Les noms sont gardés tels que le disque les donne ; ils ne sont rapprochés (forme NFC, sans la casse) que pour
reconnaître un fichier système ou une graine. Deux noms différents qui s'affichent pareil (« Références » écrit de
deux façons, sous Windows) sont signalés s'ils apparaissent pendant la mise à jour.

Le relevé et la preuve vont dans _archives-systeme/ (jamais dans sa mémoire). Ne sont pas comptés : _archives-systeme/,
.obsidian/, .claude/, .DS_Store, les fichiers temporaires d'Excel (~$…).

Un relevé ne sert qu'à UNE mise à jour : la preuve cite le relevé qu'elle a utilisé, et un relevé déjà cité est
refusé. Si une mise à jour a été coupée (relevé sans preuve) et qu'on la relance le même jour (12 heures), « avant »
garde ce premier relevé au lieu d'en prendre un nouveau : la preuve couvre alors aussi la première tentative.

Codes de sortie : 0 = mémoire intacte (ou relevé fait) ; 1 = mémoire touchée, fichier inattendu, ou condition d'un
fichier système non tenue ; 2 = rien n'a été relevé ou comparé (dossier refusé, relevé introuvable ou déjà utilisé,
fichier illisible).
"""
import hashlib
import json
import sys
import tempfile
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

ICI = Path(__file__).resolve().parent
REFS = ICI.parent / "references"
COUCHES = REFS / "couches.json"
ARCHIVES = "_archives-systeme"
IGNORES = (ARCHIVES, ".obsidian", ".claude")
FORMAT = 2
EVOLUTIFS = {"CLAUDE.md": REFS / "amorce-CLAUDE.md", "Core/Skills.md": REFS / "systeme" / "Core" / "Skills.md"}
LIGNE_BANDEAU = "> [EXEMPLE FICTIF"
REPRISE_MAX = timedelta(hours=12)


def nfc(s):
    return unicodedata.normalize("NFC", s)


def cle(s):
    """Forme de rapprochement : NFC et sans la casse (Windows et le Mac ignorent la casse)."""
    return nfc(s).casefold()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def refuser(message):
    print(f"REFUS — {message}")
    raise SystemExit(2)


def dossier_herve(chemin):
    """Le dossier HERVÉ WORLD, jamais celui du plugin : on y écrira le relevé."""
    d = Path(chemin).resolve()
    racine = next((p for p in ICI.parents if (p / ".claude-plugin" / "plugin.json").is_file()), None)
    if racine and (d == racine or racine in d.parents):
        refuser(f"« {chemin} » est dans le dossier du plugin AURA : le relevé se fait sur le dossier d'Hervé.")
    if not d.is_dir() or not (d / "Core").is_dir():
        refuser(f"« {chemin} » n'est pas le dossier HERVÉ WORLD (il doit contenir Core/).")
    return d


def lister(d):
    return sorted(d.rglob("*"))


def lire_octets(p, rel):
    try:
        return p.read_bytes()
    except OSError as e:
        refuser(f"le fichier « {rel} » ne se lit pas ({e.strerror or e}) : s'il est ouvert (Excel, Word), ferme-le ; "
                f"s'il n'est qu'en ligne (OneDrive), rends-le disponible sur l'ordinateur ; puis relance. "
                f"Rien n'a été relevé ni comparé.")


def releve(d, liste=None):
    out = {}
    for p in (liste if liste is not None else lister(d)):
        if not p.is_file():
            continue
        rel = p.relative_to(d).as_posix()
        if nfc(rel).split("/")[0] in IGNORES or p.name == ".DS_Store" or p.name.startswith("~$"):
            continue
        b = lire_octets(p, rel)
        out[rel] = {"octets": len(b), "sha256": sha(b)}
    return out


def releve_archives(d):
    """Les copies gardées dans _archives-systeme/ (hors relevés et preuves) : nom → empreinte."""
    a = d / ARCHIVES
    if not a.is_dir():
        return {}
    return {p.relative_to(a).as_posix(): sha(lire_octets(p, f"{ARCHIVES}/{p.name}")) for p in sorted(a.rglob("*"))
            if p.is_file() and not p.name.startswith(("releve_avant_", "PREUVE_MISE_A_JOUR_")) and p.name != ".DS_Store"}


def jumeaux(cles_brutes):
    """Les noms (fichier ou dossier) écrits de plusieurs façons qui s'affichent pareil : forme rapprochée → variantes."""
    vus = {}
    for k in cles_brutes:
        parts = k.split("/")
        for i in range(1, len(parts) + 1):
            brut = "/".join(parts[:i])
            vus.setdefault(cle(brut), set()).add(brut)
    return {c: sorted(v) for c, v in vus.items() if len(v) > 1}


def chemins(c):
    systeme = {"CLAUDE.md", c["version_locale"], c["bandeau_fictif"], *c["systeme_local"], *c["systeme_si_dossier_present"]}
    return {cle(x) for x in systeme}, {cle(x) for x in c["graines"]}


def releves_et_preuves(d):
    a = d / ARCHIVES
    if not a.is_dir():
        return [], ""
    preuves = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(a.glob("PREUVE_MISE_A_JOUR_*.md")))
    return sorted(a.glob("releve_avant_*.json")), preuves


def deja_utilise(releve_fichier, preuves):
    return f"Relevé « avant » : {releve_fichier.name}" in preuves


def avant(chemin, maintenant=None):
    d = dossier_herve(chemin)
    quand = maintenant or datetime.now()
    releves, preuves = releves_et_preuves(d)
    non_prouves = [r for r in releves if not deja_utilise(r, preuves)]
    alerte = None
    if non_prouves:
        dernier = non_prouves[-1]
        date = datetime.fromisoformat(json.loads(dernier.read_text(encoding="utf-8"))["date"])
        if timedelta(0) <= quand - date <= REPRISE_MAX:
            print(f"REPRISE — une mise à jour commencée le {date:%d/%m/%Y à %H:%M} n'a pas été prouvée : je garde son "
                  f"relevé ({ARCHIVES}/{dernier.name}) au lieu d'en prendre un nouveau, pour que la preuve couvre aussi "
                  f"ce qu'elle a déjà écrit.")
            return dernier
        alerte = dernier.name
    r = releve(d)
    (d / ARCHIVES).mkdir(exist_ok=True)
    f = d / ARCHIVES / f"releve_avant_{quand:%Y-%m-%d_%H%M%S}.json"
    f.write_text(json.dumps({"format": FORMAT, "date": quand.isoformat(timespec="seconds"), "fichiers": r,
                             "archives": releve_archives(d), "tentative_non_prouvee": alerte},
                            ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"RELEVÉ AVANT — {len(r)} fichiers relevés (taille et empreinte) dans {ARCHIVES}/{f.name}. "
          f"Ne rien écrire dans le dossier avant ce relevé ; « releve.py apres » le comparera."
          + (f" Attention : la mise à jour du relevé {alerte} n'a jamais été prouvée ; ce qu'elle a écrit n'est pas "
             f"couvert par la nouvelle preuve." if alerte else ""))
    return f


def bandeau_seul(nouveau, ancien_sha):
    """Vrai si le nouveau contenu est la ligne d'avertissement, une ligne vide, puis l'ancien contenu à l'identique."""
    for fin in (b"\r\n", b"\n"):
        lignes = nouveau.split(fin, 2)
        if len(lignes) == 3 and lignes[0].decode("utf-8", "replace").startswith(LIGNE_BANDEAU) \
                and "EXEMPLE FICTIF" in lignes[0].decode("utf-8", "replace") and lignes[1].strip() == b"" \
                and sha(lignes[2]) == ancien_sha:
            return True
    return False


def comparer(av, ap, c, d=None, arch_av=None, arch_ap=None, jum_av=None, jum_ap=None):
    """av, ap : relevés {nom brut: {octets, sha256}}. d : le dossier (pour relire le bandeau et les références)."""
    systeme, graines = chemins(c)
    si_dossier = {cle(x) for x in c["systeme_si_dossier_present"]}
    origine = {cle(k): v["sha256"] for k, v in c.get("empreintes_v2", {}).items()}
    evolutifs = {cle(k): sha(p.read_bytes()) for k, p in EVOLUTIFS.items() if p.is_file()}
    arch_av, arch_ap = arch_av or {}, arch_ap or {}
    copies = {}
    for nom, h in arch_ap.items():
        copies.setdefault(h, nom)
    r = {"memoire": [], "touches": [], "disparus": [], "remplaces": [], "ajoutes": [], "crees": [], "inattendus": [],
         "problemes": []}
    for k in sorted(av):
        if cle(k) not in systeme:
            r["memoire"].append(k)
            if k not in ap:
                r["disparus"].append(k)
            elif ap[k] != av[k]:
                r["touches"].append(k)
            continue
        if k not in ap:
            r["problemes"].append(f"fichier système disparu : {k} (la mise à jour remplace, elle ne supprime jamais)")
            continue
        if ap[k] == av[k]:
            continue
        if cle(k) == cle(c["bandeau_fictif"]):
            if d is not None and bandeau_seul(lire_octets(d / k, k), av[k]["sha256"]):
                r["ajoutes"].append(f"{k} : la ligne d'avertissement en tête, le reste du document identique (vérifié)")
            else:
                r["problemes"].append(f"{k} : autre chose que la ligne d'avertissement en tête a changé")
            continue
        if cle(k) in evolutifs:
            h = av[k]["sha256"]
            if h == origine.get(cle(k)):
                r["remplaces"].append(f"{k} — l'ancien était celui d'origine de la version 2.0 (Dorian le garde)")
            elif h == evolutifs[cle(k)]:
                r["remplaces"].append(f"{k} — l'ancien était déjà identique au nouveau")
            elif h in copies:
                r["remplaces"].append(f"{k} — l'ancien est gardé : {ARCHIVES}/{copies[h]} (même empreinte, vérifié)")
            else:
                r["problemes"].append(f"{k} remplacé sans copie de l'ancien dans {ARCHIVES}/ (il avait changé depuis "
                                      f"l'origine : ce qu'il contenait en plus est perdu)")
            continue
        r["remplaces"].append(k)
    dossiers_av = {"/".join(cle(k).split("/")[:i]) for k in av for i in range(1, cle(k).count("/") + 1)}
    for k in sorted(ap):
        if k in av:
            continue
        if cle(k) in graines:
            r["crees"].append(k)
        elif cle(k) in si_dossier:
            (r["crees"] if cle(k).rsplit("/", 1)[0] in dossiers_av else r["inattendus"]).append(k)
        elif cle(k) in systeme and cle(k) != cle(c["bandeau_fictif"]):
            r["crees"].append(k)
        else:
            r["inattendus"].append(k)
    for nom, h in sorted(arch_av.items()):
        if arch_ap.get(nom) != h:
            r["problemes"].append(f"copie déjà gardée dans {ARCHIVES}/ {'supprimée' if nom not in arch_ap else 'modifiée'} : {nom}")
    for c_, variantes in sorted((jum_ap or {}).items()):
        if c_ not in (jum_av or {}):
            r["problemes"].append(f"deux noms qui s'affichent pareil sont apparus : {' / '.join(repr(v) for v in variantes)}")
    return r


def apres(chemin, maintenant=None, couches=None, liste=None):
    d = dossier_herve(chemin)
    c = couches or json.loads(COUCHES.read_text(encoding="utf-8"))
    releves, preuves = releves_et_preuves(d)
    if not releves:
        refuser("aucun relevé « avant » dans _archives-systeme/ : la preuve est impossible (relance « releve.py avant » "
                "AVANT d'écrire, à la prochaine mise à jour).")
    dernier = releves[-1]
    if deja_utilise(dernier, preuves):
        refuser(f"le dernier relevé ({dernier.name}) a déjà servi à une preuve : il ne dit rien de cette mise à jour. "
                f"Relance « releve.py avant » AVANT d'écrire quoi que ce soit.")
    base = json.loads(dernier.read_text(encoding="utf-8"))
    av = base["fichiers"]
    ap_brut = releve(d, liste)
    ap = ap_brut if base.get("format", 1) >= 2 else {nfc(k): v for k, v in ap_brut.items()}
    r = comparer(av, ap, c, d, base.get("archives", {}), releve_archives(d),
                 jumeaux(av) if base.get("format", 1) >= 2 else {}, jumeaux(ap_brut))
    intacte = not (r["touches"] or r["disparus"] or r["inattendus"] or r["problemes"])
    quand = maintenant or datetime.now()
    lignes = [f"# Preuve de la mise à jour d'AURA — {quand:%d/%m/%Y à %H:%M}", "",
              f"Relevé « avant » : {dernier.name} ({base['date']}). Chaque fichier est comparé à l'octet près "
              f"(taille et empreinte sha256).", ""]
    if base.get("tentative_non_prouvee"):
        lignes += [f"Une mise à jour plus ancienne (relevé {base['tentative_non_prouvee']}) n'a jamais été prouvée : "
                   f"ce qu'elle a pu écrire n'est pas couvert par cette preuve.", ""]
    lignes += ["## Verdict", "",
               (f"**MÉMOIRE INTACTE** : les {len(r['memoire'])} fichiers de ta mémoire sont tous là, identiques octet pour octet."
                if intacte else "**ATTENTION** : la mise à jour n'a pas tenu toutes ses règles (détail ci-dessous). Préviens Dorian."),
               "", "## Ta mémoire (tout ce que tu avais déjà fait)", "", "| Fichier | Taille | État |", "|---|---|---|"]
    for k in r["memoire"]:
        etat = "**MODIFIÉ**" if k in r["touches"] else "**DISPARU**" if k in r["disparus"] else "identique"
        lignes.append(f"| {k} | {av[k]['octets']} octets | {etat} |")
    lignes += ["", "## Ce que la mise à jour a écrit", ""]
    lignes += [f"- Remplacé (fichier système) : {k}" for k in r["remplaces"]]
    lignes += [f"- Ajouté : {k}" for k in r["ajoutes"]]
    lignes += [f"- Créé (nouveau fichier, n'existait pas) : {k}" for k in r["crees"]]
    lignes += [f"- **Inattendu** (créé hors de ce que la mise à jour a le droit d'écrire) : {k}" for k in r["inattendus"]]
    lignes += [f"- **Problème** : {p}" for p in r["problemes"]]
    if not any(r[x] for x in ("remplaces", "ajoutes", "crees", "inattendus", "problemes")):
        lignes.append("- Rien.")
    preuve = d / ARCHIVES / f"PREUVE_MISE_A_JOUR_{quand:%Y-%m-%d}.md"
    if preuve.exists():
        preuve = d / ARCHIVES / f"PREUVE_MISE_A_JOUR_{quand:%Y-%m-%d_%H%M%S}.md"
    preuve.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    if intacte:
        print(f"MÉMOIRE INTACTE — {len(r['memoire'])} fichiers de mémoire vérifiés octet pour octet avant et après : tous "
              f"identiques. Remplacés (système) : {len(r['remplaces'])} ; ajouté : {len(r['ajoutes'])} ; "
              f"créés : {len(r['crees'])}. Preuve : {ARCHIVES}/{preuve.name}")
        return 0
    print(f"ATTENTION — modifiés {r['touches']} ; disparus {r['disparus']} ; inattendus {r['inattendus']} ; "
          f"problèmes {r['problemes']}. Preuve : {ARCHIVES}/{preuve.name}")
    return 1


def auto_test():
    c = json.loads(COUCHES.read_text(encoding="utf-8"))
    ok = True

    def voir(quoi, vu):
        nonlocal ok
        print(f"  {quoi} : {'OK' if vu else 'ÉCHEC'}")
        ok &= bool(vu)

    def code_de(f, *a, **k):
        try:
            return f(*a, **k)
        except SystemExit as e:
            return e.code

    amorce = EVOLUTIFS["CLAUDE.md"].read_bytes()
    skills3 = EVOLUTIFS["Core/Skills.md"].read_bytes()
    with tempfile.TemporaryDirectory() as t:
        def dossier(nom, enrichi=False):
            d = Path(t) / nom
            for ch, x in {"CLAUDE.md": "v2.0\n", "Core/Profile.md": "Hervé\n", "Core/Journal.md": "## Session 1\n",
                          "Core/Skills.md": "v2\n" + ("recap-mensuel\n" if enrichi else ""),
                          "Glossaires/Glossaire_Test.xlsx": "xlsx", "Références/Narration/é.md": "é\n",
                          c["bandeau_fictif"]: "démo\nsuite\n"}.items():
                (d / ch).parent.mkdir(parents=True, exist_ok=True)
                (d / ch).write_text(x, encoding="utf-8")
            return d

        def copier_anciens(d):          # l'étape 4 : les deux fichiers évolutifs ont changé depuis l'origine
            (d / ARCHIVES).mkdir(exist_ok=True)
            (d / ARCHIVES / "CLAUDE_v2.0_2026-10-04.md").write_bytes((d / "CLAUDE.md").read_bytes())
            (d / ARCHIVES / "Skills_v2.0_2026-10-04.md").write_bytes((d / "Core/Skills.md").read_bytes())

        def mise_a_jour(d, copie=True, bandeau=b"> [EXEMPLE FICTIF \xe2\x80\x94 d\xc3\xa9mo]\n\n"):
            if copie:
                copier_anciens(d)
            (d / "CLAUDE.md").write_bytes(amorce)
            (d / "Core/Skills.md").write_bytes(skills3)
            (d / c["version_locale"]).write_text("version: 3.0\n", encoding="utf-8")
            b = d / c["bandeau_fictif"]
            b.write_bytes(bandeau + b.read_bytes())
            for g in c["graines"]:
                if not (d / g).exists():
                    (d / g).parent.mkdir(parents=True, exist_ok=True)
                    (d / g).write_text("graine\n", encoding="utf-8")

        jour = datetime(2026, 10, 4, 12, 0, 0)
        plus_tard = jour + timedelta(minutes=30)

        d = dossier("juste")
        avant(d, jour)
        mise_a_jour(d)
        voir("mise à jour conforme : MÉMOIRE INTACTE (code 0)", apres(d, plus_tard, c) == 0)
        p = sorted((d / ARCHIVES).glob("PREUVE_*.md"))[-1].read_text(encoding="utf-8")
        voir("la preuve nomme la copie gardée, la ligne ajoutée, la mémoire identique et les fichiers créés",
             "MÉMOIRE INTACTE" in p and "| Core/Profile.md |" in p and "l'ancien est gardé : _archives-systeme/CLAUDE_v2.0"
             in p and "Ajouté :" in p and "Créé" in p)
        voir("un relevé déjà cité par une preuve est refusé (code 2), jamais réutilisé",
             code_de(apres, d, plus_tard + timedelta(days=6), c) == 2)

        cas = (
            ("modifie", lambda d: (d / "Core/Journal.md").write_text("## Session 1\nx\n", encoding="utf-8"), "MODIFIÉ", {}),
            ("supprime", lambda d: (d / "Glossaires/Glossaire_Test.xlsx").unlink(), "DISPARU", {}),
            ("ajoute", lambda d: (d / "Core/Note_inventee.md").write_text("x\n", encoding="utf-8"), "Inattendu", {}),
            ("evolutif_sans_copie", lambda d: None, "remplacé sans copie", {"copie": False}),
            ("bandeau_reecrit", lambda d: (d / c["bandeau_fictif"]).write_text("> [EXEMPLE FICTIF]\n\ndémo\n",
                                                                                 encoding="utf-8"), "ligne d'avertissement", {}),
            ("systeme_disparu", lambda d: (d / "GUIDE_AURA.md").unlink() if (d / "GUIDE_AURA.md").exists() else
             (d / "Core/Skills.md").unlink(), "fichier système disparu", {}),
            ("copie_ecrasee", lambda d: (d / ARCHIVES / "ANCIEN.md").write_text("autre\n", encoding="utf-8"),
             "copie déjà gardée", {}),
            ("ancienne_version_sans_dossier", lambda d: ((d / "skills").mkdir(), (d / c["systeme_si_dossier_present"][0])
                                                          .write_text("x\n", encoding="utf-8")), "Inattendu", {}),
        )
        for nom, sabotage, attendu, opts in cas:
            d = dossier(nom, enrichi=True)
            if nom == "copie_ecrasee":
                (d / ARCHIVES).mkdir()
                (d / ARCHIVES / "ANCIEN.md").write_text("ancien\n", encoding="utf-8")
            if nom == "systeme_disparu":
                (d / "GUIDE_AURA.md").write_text("guide v3.0\n", encoding="utf-8")
            avant(d, jour)
            mise_a_jour(d, **opts)
            sabotage(d)
            code = apres(d, plus_tard, c)
            p = sorted((d / ARCHIVES).glob("PREUVE_*.md"))[-1].read_text(encoding="utf-8")
            voir(f"sabotage « {nom} » attrapé (code 1, « {attendu} » dans la preuve)", code == 1 and attendu in p)

        d = dossier("ancienne_version_dossier_present")      # skills/ ne contient que des sous-dossiers (v2.0)
        (d / "skills/glossaire").mkdir(parents=True)
        (d / "skills/glossaire/SKILL.md").write_text("v2\n", encoding="utf-8")
        avant(d, jour)
        mise_a_jour(d)
        (d / c["systeme_si_dossier_present"][0]).write_text("lis-moi\n", encoding="utf-8")
        voir("la note de l'ancienne version, posée dans un skills/ qui n'a que des sous-dossiers : acceptée",
             apres(d, plus_tard, c) == 0)

        d = dossier("graine_existante")
        (d / "Core/Suivi.md").write_text("mes fils\n", encoding="utf-8")
        avant(d, jour)
        mise_a_jour(d)
        (d / "Core/Suivi.md").write_text("graine\n", encoding="utf-8")
        voir("une graine déjà remplie par Hervé puis réécrite est vue comme MODIFIÉE", apres(d, plus_tard, c) == 1)

        d = dossier("bandeau_crlf")
        (d / c["bandeau_fictif"]).write_bytes(b"d\xc3\xa9mo\r\nsuite\r\n")
        avant(d, jour)
        mise_a_jour(d, bandeau="> [EXEMPLE FICTIF — démo]\r\n\r\n".encode("utf-8"))
        voir("bandeau posé sur un document Windows (fins de ligne CRLF) : accepté", apres(d, plus_tard, c) == 0)

        d = dossier("relance")
        avant(d, jour)
        (d / "CLAUDE.md").write_bytes(amorce)                                           # 1re tentative, coupée…
        (d / "Core/Journal.md").write_text("## Session 1\nfaute\n", encoding="utf-8")   # …avec une faute
        f2 = avant(d, jour + timedelta(minutes=40))
        voir("relance le même jour : le premier relevé est gardé, aucun nouveau n'est pris",
             len(list((d / ARCHIVES).glob("releve_avant_*.json"))) == 1 and f2.name.endswith("120000.json"))
        mise_a_jour(d)
        voir("la faute de la tentative coupée est vue par la preuve de la relance", apres(d, plus_tard + timedelta(hours=1), c) == 1)

        d = dossier("casse")
        (d / "Glossaires").rename(d / "glossaires")
        avant(d, jour)
        mise_a_jour(d)
        voir("graine écrite dans un dossier de casse différente (« glossaires ») : reconnue, pas d'alerte",
             apres(d, plus_tard, c) == 0)

        k_nfc, k_nfd = nfc("Références/Segments/LISEZ-MOI.md"), unicodedata.normalize("NFD", "Références/Narration/é.md")
        voir("deux écritures de « Références » repérées comme noms jumeaux", list(jumeaux([k_nfc, k_nfd]).values())
             and all(len(v) == 2 for v in jumeaux([k_nfc, k_nfd]).values()))
        r = comparer({k_nfd: {"octets": 2, "sha256": "x"}}, {k_nfd: {"octets": 2, "sha256": "x"},
                                                              k_nfc: {"octets": 1, "sha256": "y"}}, c,
                     jum_av=jumeaux([k_nfd]), jum_ap=jumeaux([k_nfd, k_nfc]))
        voir("une graine posée dans un second « Références » est un problème, pas une création ordinaire",
             any("s'affichent pareil" in x for x in r["problemes"]))

        d = dossier("illisible")
        cible = d / "Core/Profile.md"
        cible.chmod(0)
        try:
            cible.open("rb").close()
            illisible = False
        except OSError:
            illisible = True
        if illisible:
            voir("un fichier illisible : refus en code 2 (rien n'est relevé), jamais une trace en code 1",
                 code_de(avant, d, jour) == 2 and not (d / ARCHIVES).exists())
        else:
            print("  un fichier illisible : non testé (le compte qui lance l'essai lit même un fichier verrouillé)")
        cible.chmod(0o644)

        d = dossier("sans_releve")
        voir("sans relevé « avant » : refus (code 2), jamais une preuve inventée", code_de(apres, d, jour, c) == 2)
        voir("cible dans le plugin (un dossier qui a pourtant un Core/) : refus (code 2) par la garde du plugin",
             (REFS / "graines" / "Core").is_dir() and code_de(dossier_herve, REFS / "graines") == 2)
    print("AUTO-TEST " + ("OK — mémoire intacte prouvée, chaque sabotage attrapé (modifié, disparu, inattendu, évolutif "
                          "sans copie, bandeau réécrit, système disparu, copie écrasée, fichier hors dossier, graine "
                          "remplie réécrite, relance, noms jumeaux), relevé réutilisé et fichier illisible refusés"
                          if ok else "ÉCHOUÉ : ne pas se fier à cette preuve."))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if a[:1] == ["--auto-test"]:
        sys.exit(auto_test())
    if len(a) != 2 or a[0] not in ("avant", "apres"):
        print(__doc__)
        sys.exit(2)
    if a[0] == "avant":
        avant(a[1])
        sys.exit(0)
    sys.exit(apres(a[1]))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
