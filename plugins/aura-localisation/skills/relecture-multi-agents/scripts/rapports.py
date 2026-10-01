#!/usr/bin/env python3
"""Compte les rapports de relecture RÉELLEMENT rendus, avant toute synthèse.

Usage :
  python3 rapports.py DOSSIER
  python3 rapports.py --auto-test    (dossier saboté : doit voir le rapport manquant, l'incomplet et le vide)

DOSSIER contient PLAN.txt (écrit par lots.py AVANT la relecture) et un fichier <nom>.md par rapport.
Un rapport est COMPLET s'il existe, n'est pas vide et se termine par la ligne « FIN DU RAPPORT ».
Format attendu d'un rapport (voir references/rapport-final.md du skill) :

  RAPPORT lot-03
  Fichier : … — lot 3 (§120 → §188)
  Constats : 4
  Zones non lues : aucune            (ou : « tableaux p. 12, dos des cartes »)
  [L-01] §131 — …
  FIN DU RAPPORT

Le script affiche, pour chaque rapport prévu : complet / incomplet / vide / manquant, le nombre de
constats annoncé, un extrait (la première ligne de constat), et les zones non lues. Pour chaque rapport
qui manque, il écrit la phrase à reprendre telle quelle dans la synthèse (« la typographie n'a pas été
vérifiée »). Il ne comble jamais un manque.

Codes de sortie : 0 = tous les rapports prévus sont complets ; 1 = au moins un manque (aucun
« OK À LIVRER » possible) ; 2 = PLAN.txt absent ou illisible.
"""
import re
import sys
from pathlib import Path

# Ce qu'un rapport manquant laisse non vérifié — phrase écrite telle quelle dans la synthèse.
NON_VERIFIE = {
    "controle-typographie": "la typographie n'a pas été vérifiée",
    "controle-longueur": "la longueur des textes et l'intégrité des balises et icônes n'ont pas été vérifiées",
    "controle-glossaire": "la terminologie (glossaire) n'a pas été vérifiée",
    "controle-comptage": "le comptage (segments et caractères, source et cible) n'a pas été fait",
    "controle-renvois": "les renvois et les numéros de règle n'ont pas été vérifiés",
}
ANGLES = {
    "logique": "la logique de jeu",
    "style": "le style et le registre",
    "renvois": "le contenu des renvois",
    "sens": "la fidélité au sens de la VO",
}
FIN = "FIN DU RAPPORT"


def phrase_manque(nom):
    if nom in NON_VERIFIE:
        return NON_VERIFIE[nom]
    m = re.fullmatch(r"(?:(?P<angle>[\w-]+)-)?lot-(?P<n>\d+)", nom)
    if m:
        n = int(m.group("n"))
        if m.group("angle"):
            quoi = ANGLES.get(m.group("angle"), f"l'angle « {m.group('angle')} »")
            return f"lot {n} : aucune relecture pour {quoi}, ce point n'est pas vérifié"
        return f"la lecture du lot {n} n'a pas été faite"
    return f"« {nom} » : aucun rapport, ce point n'est pas vérifié"


def lire_rapport(chemin):
    lignes = [l.rstrip() for l in chemin.read_text(encoding="utf-8", errors="replace").splitlines()]
    pleines = [l for l in lignes if l.strip()]
    if not pleines:
        return "vide", None, None, [], 0
    complet = pleines[-1].strip().upper() == FIN
    constats, zones, extrait, listes, bilan = None, [], None, 0, None
    for l in pleines:
        s = l.strip()
        m = re.match(r"(?i)constats?\s*:\s*(\d+)", s)
        if m and constats is None:
            constats = int(m.group(1))
            continue
        m = re.match(r"(?i)zones?\s+(?:non\s+lues|exclues)\s*:\s*(.*)", s)
        if m:
            zones.append(m.group(1).strip())
            continue
        if s.startswith("["):
            listes += 1
            if extrait is None:
                extrait = s
        elif bilan is None and re.match(r"(?i)bilan\b", s):
            bilan = s
    # Un contrôle par script n'a pas de lignes « [ » : son extrait est la ligne BILAN de sa sortie,
    # sinon la dernière ligne de contenu avant FIN DU RAPPORT.
    if extrait is None:
        fin_contenu = [l.strip() for l in pleines if l.strip().upper() != FIN]
        extrait = bilan or (fin_contenu[-1] if len(fin_contenu) > 1 else None)
    if extrait and len(extrait) > 160:
        extrait = extrait[:160] + "…"
    return ("complet" if complet else "incomplet"), constats, extrait, zones, listes


def compter(dossier):
    """(rapports prévus, état de chacun) ; lève OSError si PLAN.txt manque."""
    plan = Path(dossier) / "PLAN.txt"
    prevus = [l.strip() for l in plan.read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.strip().startswith("#")]
    etats = []
    for nom in prevus:
        f = next((Path(dossier) / (nom + ext) for ext in (".md", ".txt") if (Path(dossier) / (nom + ext)).exists()), None)
        etats.append((nom, "manquant", None, None, [], 0) if f is None else (nom, *lire_rapport(f)))
    return prevus, etats


def auto_test():
    """Dossier saboté : 4 rapports prévus, dont 1 manquant, 1 sans fin, 1 vide. Les 3 doivent être vus."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "PLAN.txt").write_text("# essai\ncontrole-typographie\ncontrole-renvois\nlot-01\nlot-02\n", encoding="utf-8")
        (d / "controle-renvois.md").write_text("RAPPORT controle-renvois\nConstats : 0\nBILAN : 0 anomalie\nFIN DU RAPPORT\n", encoding="utf-8")
        (d / "lot-01.md").write_text("RAPPORT lot-01\nConstats : 1\n[LOG-01] § 3 — coupé avant la fin\n", encoding="utf-8")
        (d / "lot-02.md").write_text("\n", encoding="utf-8")
        _, etats = compter(d)
    vus = {nom: etat for nom, etat, *_ in etats}
    attendu = {"controle-typographie": "manquant", "controle-renvois": "complet", "lot-01": "incomplet", "lot-02": "vide"}
    ok = vus == attendu
    for nom, etat in attendu.items():
        print(f"  {nom} : attendu {etat}, vu {vus.get(nom)} — {'OK' if vus.get(nom) == etat else 'ÉCHEC'}")
    print(f"  phrase pour le manquant : « {phrase_manque('controle-typographie')} »")
    print("AUTO-TEST " + ("OK — les 3 rapports défaillants sont vus." if ok else "ÉCHOUÉ : ne pas se fier à ce compte."))
    sys.exit(0 if ok else 1)


def main():
    if "--auto-test" in sys.argv:
        auto_test()
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    dossier = Path(sys.argv[1])
    try:
        prevus, etats = compter(dossier)
    except OSError as e:
        print(f"PLAN.txt illisible ({e}). Sans plan écrit AVANT la relecture, impossible de compter les rapports.")
        sys.exit(2)

    complets = [e for e in etats if e[1] == "complet"]
    print(f"RAPPORTS DE RELECTURE — {dossier}")
    print(f"Prévus : {len(prevus)} · rendus complets : {len(complets)} sur {len(prevus)}")
    print()
    ecarts = []
    for nom, etat, constats, extrait, zones, listes in etats:
        if etat == "complet":
            c = "constats non indiqués" if constats is None else f"{constats} constat(s)"
            print(f"  ✓ {nom} — {c}")
            print(f"      extrait : {extrait or '(aucune ligne de constat)'}")
            if constats is not None and constats != listes and not nom.startswith("controle-"):
                ecarts.append(f"{nom} : annonce {constats} constat(s), en liste {listes}")
        else:
            print(f"  ✗ {nom} — {etat.upper()}")

    manques = [e for e in etats if e[1] != "complet"]
    if manques:
        print()
        print("À ÉCRIRE TEL QUEL DANS LA SYNTHÈSE (ne jamais combler) :")
        for nom, etat, *_ in manques:
            precision = "" if etat == "manquant" else f" (rapport {etat})"
            print(f"  - {phrase_manque(nom)}{precision}.")

    if ecarts:
        print()
        print("Rapports dont le nombre annoncé ne correspond pas à la liste (à relire avant la synthèse) :")
        for e in ecarts:
            print(f"  - {e}")

    zones = [(n, z) for n, et, _, _, zs, _ in etats if et == "complet" for z in zs
             if z and z.lower() not in ("aucune", "aucun", "néant", "-")]
    if zones:
        print()
        print("Zones non lues, à nommer dans la synthèse :")
        for n, z in zones:
            print(f"  - {n} : {z}")

    zeros = [n for n, et, c, _, _, _ in etats if et == "complet" and c == 0]
    if zeros:
        print()
        print("Rapports à 0 constat : " + ", ".join(zeros) + ".")
        print("  Un « 0 » ne prouve rien tant que la passe n'a pas trouvé les fautes glissées dans la copie")
        print("  sabotée (règle du skill noyau) : dire dans la synthèse si cet essai a été fait.")

    print()
    if manques:
        print(f"VERDICT IMPOSSIBLE « OK À LIVRER » : {len(manques)} rapport(s) sur {len(prevus)} manquant(s) ou incomplet(s).")
        sys.exit(1)
    print(f"Tous les rapports prévus sont rendus ({len(prevus)} sur {len(prevus)}). La synthèse peut commencer.")
    sys.exit(0)


if __name__ == "__main__":
    main()
