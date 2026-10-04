#!/usr/bin/env python3
"""La preuve que la mise à jour n'a touché à rien de ce qu'Hervé avait déjà fait.

  python3 releve.py avant "<HERVÉ WORLD>"   → avant la PREMIÈRE écriture : relève chaque fichier (taille, sha256)
  python3 releve.py apres "<HERVÉ WORLD>"   → après la dernière : compare au relevé, octet pour octet, et écrit la
                                              preuve lisible _archives-systeme/PREUVE_MISE_A_JOUR_AAAA-MM-JJ.md
  python3 releve.py --auto-test             → essai sur un dossier fabriqué, sabotages compris

Ce que le programme sait des chemins vient de ../references/couches.json (une seule écriture) :
  - les fichiers système (l'amorce CLAUDE.md, Core/VERSION.md, systeme_local, systeme_si_dossier_present, le document
    du bandeau) peuvent être remplacés : ils sont listés à part ;
  - les graines peuvent être créées ;
  - TOUT LE RESTE est la mémoire d'Hervé : chaque fichier doit être identique, octet pour octet, et toujours là.
Le relevé et la preuve vont dans _archives-systeme/ (jamais dans sa mémoire). Ne sont pas comptés : _archives-systeme/,
.obsidian/, .claude/, .DS_Store, les fichiers temporaires d'Excel (~$…).

Codes de sortie : 0 = mémoire intacte (ou relevé fait) ; 1 = mémoire touchée, ou fichier inattendu ; 2 = dossier ou
relevé introuvable, ou cible refusée.
"""
import hashlib
import json
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

ICI = Path(__file__).resolve().parent
COUCHES = ICI.parent / "references" / "couches.json"
ARCHIVES = "_archives-systeme"
IGNORES = (ARCHIVES, ".obsidian", ".claude")


def nfc(s):
    return unicodedata.normalize("NFC", s)


def refuser(message):
    print(f"REFUS — {message}")
    raise SystemExit(2)


def dossier_herve(chemin):
    """Le dossier HERVÉ WORLD, jamais celui du plugin : on y écrira le relevé."""
    d = Path(chemin).resolve()
    if not d.is_dir() or not (d / "Core").is_dir():
        refuser(f"« {chemin} » n'est pas le dossier HERVÉ WORLD (il doit contenir Core/).")
    racine = next((p for p in ICI.parents if (p / ".claude-plugin" / "plugin.json").is_file()), None)
    if racine and (d == racine or racine in d.parents):
        refuser(f"« {chemin} » est dans le dossier du plugin AURA : le relevé se fait sur le dossier d'Hervé.")
    return d


def releve(d):
    out = {}
    for p in sorted(d.rglob("*")):
        if not p.is_file():
            continue
        rel = nfc(p.relative_to(d).as_posix())
        if rel.split("/")[0] in IGNORES or p.name == ".DS_Store" or p.name.startswith("~$"):
            continue
        b = p.read_bytes()
        out[rel] = {"octets": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    return out


def chemins(c):
    systeme = {"CLAUDE.md", c["version_locale"], c["bandeau_fictif"], *c["systeme_local"], *c["systeme_si_dossier_present"]}
    return {nfc(x) for x in systeme}, {nfc(x) for x in c["graines"]}


def avant(chemin, maintenant=None):
    d = dossier_herve(chemin)
    r = releve(d)
    (d / ARCHIVES).mkdir(exist_ok=True)
    quand = maintenant or datetime.now()
    f = d / ARCHIVES / f"releve_avant_{quand:%Y-%m-%d_%H%M%S}.json"
    f.write_text(json.dumps({"date": quand.isoformat(timespec="seconds"), "fichiers": r}, ensure_ascii=False, indent=1),
                 encoding="utf-8")
    print(f"RELEVÉ AVANT — {len(r)} fichiers relevés (taille et empreinte) dans {ARCHIVES}/{f.name}. "
          f"Ne rien écrire dans le dossier avant ce relevé ; « releve.py apres » le comparera.")
    return f


def comparer(av, ap, c):
    systeme, graines = chemins(c)
    memoire = [k for k in av if k not in systeme]
    touches = [k for k in memoire if k in ap and ap[k] != av[k]]
    disparus = [k for k in memoire if k not in ap]
    remplaces = sorted(k for k in av if k in systeme and ap.get(k) != av[k])
    nouveaux = sorted(k for k in ap if k not in av)
    crees = [k for k in nouveaux if k in graines or k in systeme]
    inattendus = [k for k in nouveaux if k not in crees]
    return {"memoire": sorted(memoire), "touches": sorted(touches), "disparus": sorted(disparus),
            "remplaces": remplaces, "crees": crees, "inattendus": inattendus}


def apres(chemin, maintenant=None, couches=None):
    d = dossier_herve(chemin)
    c = couches or json.loads(COUCHES.read_text(encoding="utf-8"))
    releves = sorted((d / ARCHIVES).glob("releve_avant_*.json")) if (d / ARCHIVES).is_dir() else []
    if not releves:
        refuser("aucun relevé « avant » dans _archives-systeme/ : la preuve est impossible (relance « releve.py avant » "
                "AVANT d'écrire, à la prochaine mise à jour).")
    base = json.loads(releves[-1].read_text(encoding="utf-8"))
    av, ap = base["fichiers"], releve(d)
    r = comparer(av, ap, c)
    intacte = not (r["touches"] or r["disparus"] or r["inattendus"])
    quand = maintenant or datetime.now()
    lignes = [f"# Preuve de la mise à jour d'AURA — {quand:%d/%m/%Y à %H:%M}", "",
              f"Relevé « avant » : {releves[-1].name} ({base['date']}). Chaque fichier est comparé à l'octet près "
              f"(taille et empreinte sha256).", "",
              "## Verdict", "",
              (f"**MÉMOIRE INTACTE** : les {len(r['memoire'])} fichiers de ta mémoire sont tous là, identiques octet pour octet."
               if intacte else "**ATTENTION** : la mémoire n'est pas intacte (détail ci-dessous). Préviens Dorian."), "",
              "## Ta mémoire (tout ce que tu avais déjà fait)", "", "| Fichier | Taille | État |", "|---|---|---|"]
    for k in r["memoire"]:
        etat = "**MODIFIÉ**" if k in r["touches"] else "**DISPARU**" if k in r["disparus"] else "identique"
        lignes.append(f"| {k} | {av[k]['octets']} octets | {etat} |")
    lignes += ["", "## Ce que la mise à jour a écrit", ""]
    lignes += [f"- Remplacé (fichier système, l'ancien est gardé dans {ARCHIVES}/ s'il avait changé) : {k}" for k in r["remplaces"]]
    lignes += [f"- Créé (nouveau fichier, n'existait pas) : {k}" for k in r["crees"]]
    lignes += [f"- **Inattendu** (créé hors de ce que la mise à jour a le droit d'écrire) : {k}" for k in r["inattendus"]]
    if not (r["remplaces"] or r["crees"] or r["inattendus"]):
        lignes.append("- Rien.")
    preuve = d / ARCHIVES / f"PREUVE_MISE_A_JOUR_{quand:%Y-%m-%d}.md"
    if preuve.exists():
        preuve = d / ARCHIVES / f"PREUVE_MISE_A_JOUR_{quand:%Y-%m-%d_%H%M%S}.md"
    preuve.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    if intacte:
        print(f"MÉMOIRE INTACTE — {len(r['memoire'])} fichiers de mémoire vérifiés octet pour octet avant et après : tous "
              f"identiques. Remplacés (système) : {len(r['remplaces'])} ; créés : {len(r['crees'])}. "
              f"Preuve : {ARCHIVES}/{preuve.name}")
        return 0
    print(f"ATTENTION — mémoire touchée : modifiés {r['touches']} ; disparus {r['disparus']} ; inattendus {r['inattendus']}. "
          f"Preuve : {ARCHIVES}/{preuve.name}")
    return 1


def auto_test():
    c = json.loads(COUCHES.read_text(encoding="utf-8"))
    ok = True

    def voir(quoi, vu):
        nonlocal ok
        print(f"  {quoi} : {'OK' if vu else 'ÉCHEC'}")
        ok &= bool(vu)

    with tempfile.TemporaryDirectory() as t:
        def dossier(nom):
            d = Path(t) / nom
            for ch, x in {"CLAUDE.md": "v2.0\n", "Core/Profile.md": "Hervé\n", "Core/Journal.md": "## Session 1\n",
                          "Core/Skills.md": "v2\n", "Glossaires/Glossaire_Test.xlsx": "xlsx", "Références/Narration/é.md": "é\n",
                          c["bandeau_fictif"]: "démo\n"}.items():
                (d / ch).parent.mkdir(parents=True, exist_ok=True)
                (d / ch).write_text(x, encoding="utf-8")
            return d

        def mise_a_jour(d):        # ce que la mise à jour a le droit de faire
            (d / "CLAUDE.md").write_text("AURA-HERVE-VERSION: 3.0\n", encoding="utf-8")
            (d / "Core/Skills.md").write_text("v3\n", encoding="utf-8")
            (d / c["version_locale"]).write_text("version: 3.0\n", encoding="utf-8")
            (d / c["bandeau_fictif"]).write_text("> [EXEMPLE FICTIF]\n\ndémo\n", encoding="utf-8")
            for g in c["graines"]:
                (d / g).parent.mkdir(parents=True, exist_ok=True)
                (d / g).write_text("graine\n", encoding="utf-8")
            (d / ARCHIVES / "CLAUDE_v2.0_2026-10-04.md").write_text("v2.0\n", encoding="utf-8")

        jour = datetime(2026, 10, 4, 12, 0, 0)
        d = dossier("juste")
        avant(d, jour)
        mise_a_jour(d)
        voir("mise à jour conforme : MÉMOIRE INTACTE (code 0)", apres(d, jour, c) == 0)
        p = (d / ARCHIVES / "PREUVE_MISE_A_JOUR_2026-10-04.md").read_text(encoding="utf-8")
        voir("la preuve liste la mémoire identique et ce qui a été écrit",
             "MÉMOIRE INTACTE" in p and "| Core/Profile.md |" in p and "identique" in p and "Créé" in p and "Remplacé" in p)
        for nom, sabotage, attendu in (
                ("modifie", lambda d: (d / "Core/Journal.md").write_text("## Session 1\nx\n", encoding="utf-8"), "MODIFIÉ"),
                ("supprime", lambda d: (d / "Glossaires/Glossaire_Test.xlsx").unlink(), "DISPARU"),
                ("ajoute", lambda d: (d / "Core/Note_inventee.md").write_text("x\n", encoding="utf-8"), "Inattendu"),
                ("graine_existante", lambda d: None, None)):
            d = dossier(nom)
            if nom == "graine_existante":    # une graine qui existait déjà (Hervé l'a remplie) est de la mémoire
                (d / "Core/Suivi.md").parent.mkdir(parents=True, exist_ok=True)
                (d / "Core/Suivi.md").write_text("mes fils\n", encoding="utf-8")
                avant(d, jour)
                mise_a_jour(d)
                voir("une graine déjà remplie par Hervé puis réécrite est vue comme MODIFIÉE", apres(d, jour, c) == 1)
                continue
            avant(d, jour)
            mise_a_jour(d)
            sabotage(d)
            code = apres(d, jour, c)
            p = sorted((d / ARCHIVES).glob("PREUVE_*.md"))[-1].read_text(encoding="utf-8")
            voir(f"sabotage « {nom} » attrapé (code 1, « {attendu} » écrit dans la preuve)", code == 1 and attendu in p)
        d = dossier("sans_releve")
        try:
            apres(d, jour, c)
            voir("sans relevé « avant » : refus", False)
        except SystemExit as e:
            voir("sans relevé « avant » : refus (code 2), jamais une preuve inventée", e.code == 2)
        try:
            dossier_herve(ICI.parent)
            voir("cible dans le plugin : refus", False)
        except SystemExit as e:
            voir("cible dans le plugin : refus (code 2)", e.code == 2)
    print("AUTO-TEST " + ("OK — mémoire intacte prouvée, et chaque sabotage (modifié, disparu, inattendu, graine "
                          "remplie réécrite) attrapé" if ok else "ÉCHOUÉ : ne pas se fier à cette preuve."))
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
