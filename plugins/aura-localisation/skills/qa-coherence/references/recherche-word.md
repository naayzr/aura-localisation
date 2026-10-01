# Chercher soi-même dans Word — procédures valides <!-- [D-34] -->

La voie normale : Hervé dépose le fichier, AURA lance les scripts de ce skill (`renvois.py`, `chercher.py`) et rend le résultat avec l'endroit de chaque occurrence. Ce fichier sert quand Hervé préfère vérifier lui-même dans Word.

La v2.0 proposait de chercher `règle \d+\.\d+` dans Word : **cette syntaxe ne marche pas dans Word.** Word n'utilise pas les expressions régulières habituelles, mais ses propres « caractères génériques ».

## Ouvrir la bonne fenêtre

1. Dans Word : **Ctrl+H** (ou onglet **Accueil** → **Remplacer**). La fenêtre « Rechercher et remplacer » s'ouvre ; aller sur l'onglet **Rechercher**.
2. Cliquer sur **Plus >>** pour afficher les options.
3. Cocher **Utiliser les caractères génériques**. Avec cette case cochée, Word respecte toujours les majuscules : `[Rr]` sert à accepter les deux.

Selon la version de Word, un libellé peut varier légèrement.

## Les recherches utiles (case « caractères génériques » cochée)

| Pour trouver | Taper dans « Rechercher » | Ce que ça trouve |
|---|---|---|
| Tous les numéros de règle à deux niveaux | `[0-9]@.[0-9]@` | 5.2, 12.10 — titres et renvois |
| Les renvois « règle X.Y » | `[Rr]ègle?[0-9]@.[0-9]@` | « règle 5.2 », « Règle 5.2 » (avec une espace ordinaire ou insécable) |
| Les numéros écrits avec une virgule après « règle » | `[Rr]ègle?[0-9]@,[0-9]@` | « règle 5,2 » |
| Les renvois de page | `[Pp]age?[0-9]@` puis `<p.?[0-9]@` | « page 12 », « p. 12 » |

Ce que veulent dire les signes : `[0-9]` = un chiffre ; `@` = une ou plusieurs fois ce qui précède ; `?` = n'importe quel caractère, un seul ; `<` = début de mot. Le point `.` et la virgule `,` se cherchent tels quels.

## Voir toutes les occurrences d'un coup

- **Rechercher dans** → **Document principal** : Word sélectionne toutes les occurrences (et, selon la version, indique combien il en a trouvé).
- **Lecture en surbrillance** → **Tout surligner** : toutes les occurrences restent surlignées à l'écran pendant la relecture ; **Effacer la surbrillance** pour finir.

## Chercher un mot (sans caractères génériques)

Décocher **Utiliser les caractères génériques**, puis cocher **Mot entier** pour ne pas trouver « Or » dans « Ordre » ou « dehors ». Une recherche par mot, puis **Rechercher dans → Document principal** pour le compte.

## Ce que Word ne fait pas, et que les scripts font

- Comparer la traduction à la version originale (règles absentes, renvois perdus) : `renvois.py --source`.
- Dire qu'un renvoi vise une règle qui n'existe pas : `renvois.py`.
- Chercher en ignorant les accents (« deplacer » → « Déplacer »), ou toute une liste de mots d'un coup : `chercher.py`.
- Voir les numéros produits par la numérotation automatique de Word : ni la recherche de Word ni le script ne les voient comme du texte. Ceux-là se vérifient en lisant le document.
