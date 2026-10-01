# Les programmes du glossaire — commandes et garde-fous

Tous dans `${CLAUDE_SKILL_DIR}/scripts/`, Python 3, bibliothèque standard seulement. Ils lisent les
fichiers avec `lecture.py` (copie identique à celle des autres skills : ne jamais la modifier seule).
Ils travaillent sur des fichiers que le programme voit. Avant de les lancer, AURA applique la règle « Les programmes et le dossier d'Hervé » du skill `noyau`
(vérifier que le fichier existe pour le programme ; sinon le faire glisser ; un classeur produit hors du
dossier se pose par la procédure « Poser un fichier produit », jamais par simple remplacement).

| Programme | Ce qu'il fait | Écrit ? |
|---|---|---|
| `modele_glossaire.py` | les listes du modèle (colonnes, statuts, catégories) et l'écriture du classeur ; lancé seul, il affiche les listes | — |
| `controle_glossaire.py` | contrôle un ou plusieurs glossaires | jamais |
| `chercher_terme.py` | cherche un terme et ses variantes dans tout le dossier HERVÉ WORLD | jamais |
| `gerer_glossaire.py` | créer, importer, fusionner, **migrer un glossaire v2.0** (tous ses onglets, statuts repris), modifier, exporter, lire des retours, comparer, sauvegarder | seulement avec `--ecrire` |

## gerer_glossaire.py

Sans `--ecrire`, chaque commande est un **essai** : elle affiche ce qu'elle ferait, rien de plus. Avec
`--ecrire`, avant de toucher un glossaire existant, elle vérifie qu'Excel ne l'a pas ouvert, pose une
sauvegarde datée dans `Core/Archives/`, écrit dans une copie temporaire, remplace, puis **relit** le
fichier écrit et compare le nombre de termes (un écart arrête tout).

```
creer       --gamme "<Gamme>" --sortie Glossaires/Glossaire_<Gamme>.xlsx --par "Hervé"
importer    <source.xlsx|.csv> --gamme "<Gamme>" --sortie Glossaires/Glossaire_<Gamme>.xlsx
            --provenance "<d'où il vient>" [--feuille <nom>] [--colonne EN="<en-tête>"] [--par "Hervé"]
importer    <source> --gamme "<Gamme>" --dans Glossaires/Glossaire_<Gamme>.xlsx --provenance "…"
            [--garder-seuls]  (importer aussi les lignes où seul l'anglais est rempli)
modifier    <glossaire> --id T-0012 --champ STATUT=Confirmé --champ GENRE=f --par "Hervé" --raison "…"
modifier    <glossaire> --ajouter --champ EN=… --champ FR=… --champ CATÉGORIE=… [--champ "DÉFINITION MÉCANIQUE=…"]
modifier    <glossaire> --lot decisions.csv          (colonnes ID;CHAMP;VALEUR;RAISON;PAR;ERRATUM)
exporter    <glossaire> --sortie Livrables/<Projet>/Glossaire_<Gamme>_<Produit>_AAAA-MM-JJ.xlsx --pour relecteur
retours     <export renvoyé par le relecteur.xlsx>
comparer    <ancien.xlsx> <nouveau.xlsx>
sauvegarder <glossaire>
```

Les refus de `modifier` (rien n'est appliqué tant qu'un seul point est refusé) :
- passer en Confirmé ou Gelé sans GENRE pour une catégorie qui l'exige, avec un FR vide ou à double
  proposition ;
- toucher un terme Confirmé ou Gelé sans `--raison` et `--par` ;
- changer l'anglais ou le français d'un terme **Gelé**, ou le dégeler, sans `--erratum <référence>` ;
- geler sans PUBLIÉ DANS ; archiver sans `--raison` ;
- ajouter un anglais déjà présent (non archivé), sauf `--second-sens` avec deux définitions mécaniques
  remplies et différentes ;
- donner un français déjà pris par un autre anglais, sauf `--accepter-fr-partage` (décision d'Hervé).

Versions : toute modification qui touche un terme Confirmé ou Gelé, ou qui fait entrer un terme dans
l'un de ces statuts, fait monter la version d'un cran (1.3 → 1.4) ;
un erratum sur un terme Gelé ou son archivage la fait monter d'un rang (1.4 → 2.0). Les Brouillons
changent sans changer la version, mais chaque changement fait par le programme a sa ligne au CHANGELOG.

Chaque programme a un `--auto-test` : il se vérifie lui-même sur des fichiers fabriqués dans un dossier
temporaire (aucun fichier réel touché) et affiche `AUTO-TEST OK` ou la liste de ce qui a échoué. Celui du
contrôle vérifie aussi que SKILL.md et le programme portent les mêmes colonnes, statuts et catégories. AURA le
lance si un résultat lui paraît étrange, avant de conclure quoi que ce soit.

## controle_glossaire.py

```
controle_glossaire.py Glossaires/Glossaire_<Gamme>.xlsx [autre.xlsx …] [--attente-jours 30]
```
Trois niveaux : ANOMALIE (à corriger), À VÉRIFIER (jugement d'Hervé), INFO. Code de sortie 0 s'il n'y a
aucune anomalie, 1 sinon, 2 si un fichier est illisible. Les numéros de ligne sont ceux de la feuille
quand elle n'a pas de ligne vide intercalée ; l'ID et le terme anglais identifient la ligne dans tous les cas.

## chercher_terme.py

```
chercher_terme.py "<dossier HERVÉ WORLD>" "terme" ["autre forme" …] [--langue en|fr] [--exact] [--tout] [--avec-archives]
```
Casse, accents, apostrophes et tirets ignorés ; mots entiers. En anglais, il ajoute pluriel, possessif et
formes verbales (-s, -es, -ed, -ing). En français, pluriel et féminin des noms et adjectifs ; **pour un
verbe, donner ses formes** (le programme ne conjugue pas). Résultat groupé par zone (glossaires,
segments, références, livrables, Preferences, evas, Journal, IMPORT), avec le nombre exact
d'occurrences par fichier et les fichiers NON FOUILLÉS (PDF, illisibles). `Core/Archives` n'est fouillé
qu'avec `--avec-archives`.

## Essais faits le 01/10/2026 (pour savoir ce qui a été vérifié)

- Import du glossaire de la démo (`Glossaire_TaintedGrail_EN-FR.xlsx`, 9 372 octets) : 53 termes
  trouvés, 8 lignes de section ignorées, 2 cellules à double proposition, 8 genres à déclarer ; fichier
  écrit relu par le programme et par un second lecteur (openpyxl) : 4 onglets, volets figés, filtre,
  5 listes déroulantes, formules du tableau de bord ; aperçu macOS du tableau de bord conforme (il ne
  montre que le premier onglet ; Excel lui-même n'a pas été ouvert).
- Contrôle d'un glossaire saboté exprès, écrit par une autre bibliothèque (openpyxl) comme le ferait Excel
  (chaînes partagées, vraies dates) : les 18 anomalies et 4 points à vérifier posés ont tous été trouvés.
- Modifications : refus vérifiés un par un (genre manquant, gel sans produit, terme Gelé sans erratum,
  doublon d'anglais, français déjà pris, fichier ouvert dans Excel) ; lot de 4 décisions ; second sens ;
  archivage d'un terme gelé puis ajout du remplaçant.
- Recherche dans un dossier fabriqué (Preferences, evas, segments CSV, livrable Word, PDF) : comptes
  exacts, PDF déclaré non fouillé.
- Essais sous Python 3.14 ; import, modification, création, sauvegarde, contrôle et recherche rejoués
  sous Python 3.9.
