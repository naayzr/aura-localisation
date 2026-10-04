# Relecteurs en parallèle — sur demande expresse d'Hervé seulement <!-- [D-03] -->

La relecture standard (scripts, puis lecture par lots par AURA) est la règle. Ce fichier ne sert que si Hervé demande **expressément** plusieurs relecteurs en parallèle. Le seuil d'accord et l'ordre « fichiers, puis scripts, puis agents » sont la règle des agents du skill `noyau` (ses règles de travail, « Dépenser juste »).

## 1. Préparer le plan

```
python3 "${CLAUDE_SKILL_DIR}/scripts/lots.py" <fichier> --relecteurs 3 --angles logique,style,renvois --plan "<HERVÉ WORLD>/Livrables/<Projet>/relecture"
```

Si le programme ne voit pas le dossier (la règle « Les programmes et le dossier d'Hervé » du skill `noyau`), `PLAN.txt` est écrit sur la machine du programme : AURA le relit et le **réécrit elle-même** dans `Livrables/<Projet>/relecture/PLAN.txt`, sinon il disparaît avec la tâche.
- Angles possibles : `logique` (logique de jeu), `style` (style et registre), `renvois` (contenu des renvois), `sens` (fidélité à la version originale, si Hervé la fournit).
- Les contrôles automatiques (typographie, longueurs et balises, glossaire, comptage, existence des renvois) restent faits **par script**, une fois, avant les relecteurs. Aucun relecteur ne refait la typographie à la main.
- Le script affiche le nombre de lancements (relecteurs × lots) et l'ordre de grandeur lu.

## 2. Annoncer, avant de lancer quoi que ce soit

Texte type, chiffres tirés de la sortie de `lots.py` :

> Tu me demandes une relecture à plusieurs relecteurs. Voilà ce que ça représente :
> - **3 relecteurs en même temps** (logique de jeu, style, renvois), sur **5 lots** de 30 000 caractères au plus : **15 lancements** au total ;
> - chaque relecteur lit son lot en entier : de l'ordre de **95 000 à 127 000 jetons** rien que pour la lecture (une estimation, pas un compte) ;
> - **cela consomme ton quota d'abonnement** : chaque relecteur compte pour lui-même, et une fois la limite atteinte, il faut attendre qu'elle se réinitialise.
>
> La relecture standard, sans relecteurs parallèles, couvre les mêmes angles en lisant les lots l'un après l'autre, pour bien moins. Je lance les 15 lancements, ou je fais la relecture standard ?

**Au-delà du seuil de la règle des agents du skill `noyau`, AURA attend un « oui » explicite** à cette question ; en deçà, elle lance après l'annonce. La règle est appliquée telle qu'elle y est écrite, sans la redire ici. <!-- [R-37] -->

## 3. Lancer

- Un relecteur par angle et par lot, lot après lot : les 3 relecteurs du lot 1, puis ceux du lot 2, etc. Jamais tous les lots d'un coup.
- **Si la session ne permet pas de lancer des relecteurs séparés**, AURA le dit à Hervé en une phrase et passe à la relecture standard. Elle n'écrit jamais elle-même des rapports présentés comme ceux de relecteurs qui n'ont pas existé.

## 4. La consigne de chaque relecteur

Chaque relecteur reçoit la même trame, remplie :

```
Tu relis UN lot d'une traduction anglais → français d'un jeu de société, sous UN angle.

Fichier : <chemin de la copie de travail> — lot <N> : du repère <début> au repère <fin>.
Angle : <logique de jeu | style et registre | contenu des renvois | fidélité à la version originale>.
Ne lis que ce lot. Ne traite que cet angle.

Références (à lire avant le lot) :
- glossaire : <chemin> — termes Confirmés et Gelés font foi ; ne propose jamais un autre terme ;
- fiche éditeur : <chemin> — tutoiement ou vouvoiement, charte ;
- carte mécanique : <chemin, ou « aucune »> ;
- VO : <chemin, ou « non fournie »>.

Ce que tu ne fais pas : la typographie, les longueurs, les balises, les comptes (déjà contrôlés
par script) ; corriger le fichier ; inventer une règle pour combler un silence de la VO.

Écris ton rapport dans <dossier de relecture>/<angle>-lot-<NN>.md, exactement ainsi :
RAPPORT <angle>-lot-<NN>
Fichier : <fichier> — lot <N> (<début> → <fin>)
Constats : <nombre de lignes de constat ci-dessous>
Zones non lues : <ce que tu n'as pas pu lire, ou « aucune »>
[<CODE>-01] <repère> (<règle ou carte>) — <constat> — <correction proposée ou question>
…
FIN DU RAPPORT

S'il n'y a aucun constat, écris « Constats : 0 » et dis en une ligne ce que tu as vérifié.
```

Codes de constat : `LOG` (logique de jeu), `STY` (style et registre), `REF` (contenu des renvois), `SEN` (sens). Les angles et leurs pièges : `references/lecture-par-lots.md`.

## 5. Après les relecteurs

La synthèse commence par `scripts/rapports.py` (étape 3 du skill) : compter les rapports réellement rendus, citer un extrait de chacun, ne jamais combler un rapport manquant.
