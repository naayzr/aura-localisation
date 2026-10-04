# Charte typographique française — la seule de l'extension

<!-- [I-36] -->

Cette charte est écrite **une seule fois**, ici. Tous les autres skills y renvoient. Chaque règle a un identifiant (T01…) qui est aussi celui du script `scripts/typo.py` ; un contrôle vérifie que les deux listes concordent.

**Les écarts propres à un éditeur** (par exemple : espace insécable normale partout au lieu de l'espace fine) s'écrivent dans sa fiche `Core/Editeurs/<Éditeur>.md`, section « Charte typographique », et passent avant cette charte pour ses textes.

Caractères invisibles (le point de code entre crochets) :
- espace insécable normale [U+00A0] — dans Word : `^s`
- espace fine insécable [U+202F] — dans Word pour Windows : taper `202F` puis `Alt+X` (si un chiffre précède, sélectionner d'abord les quatre caractères `202F`) ; ou la faire poser par la mise en page
- apostrophe typographique ’ [U+2019]
- points de suspension … [U+2026]
- tiret demi-cadratin – [U+2013] — Word : `^=` ; tiret cadratin — [U+2014] — Word : `^+`

| Id | Règle | Faux | Juste |
|---|---|---|---|
| T01 | Espace insécable (fine ou normale) **avant** `;` `!` `?` — jamais d'espace ordinaire, jamais rien ; une seule espace avant un groupe de signes | `Défaussez !` (espace ordinaire) · `Défaussez!` · `Quoi?!` | `Défaussez[U+202F]!` · `Quoi[U+202F]?!` |
| T02 | Espace insécable normale (pas la fine) **avant** `:` (sauf entre deux chiffres : `10:30`, `3:1`) | `Effet : …` (espace ordinaire) · `Effet[U+202F]: …` (espace fine) · `Effet: …` · `Étape 2: …` | `Effet[U+00A0]: …` |
| T03 | Guillemets français `« »` avec espace insécable à l'intérieur ; guillemets anglais `“ ”` seulement pour une citation dans une citation | `"Éclat"` · `«Éclat»` · `“Éclat”` (seul) | `«[U+00A0]Éclat[U+00A0]»` · `«[U+00A0]Il dit “Éclat”[U+00A0]»` |
| T04 | Apostrophe typographique ’, devant une capitale aussi | `l'action` · `l'Œil` (droite) | `l’action` · `l’Œil` |
| T05 | Points de suspension en un seul caractère | `...` | `…` |
| T06 | Pas d'espace avant `,` et `.` | `une carte , puis` | `une carte, puis` |
| T07 | Pas de double espace | `deux  espaces` | `deux espaces` |
| T08 | Majuscules accentuées, en capitales aussi | `Etape`, `ETAPE`, `Etat`, `Epuisé`, `A la fin` | `Étape`, `ÉTAPE`, `État`, `Épuisé`, `À la fin` |
| T09 | Ordinaux abrégés : `1er`, `1re`, `2e` (pluriel `1ers`, `1res`, `2es`) — jamais `2ème`, `1ère`, `2nd`, `2eme` | `2ème manche` · `1ère manche` | `2e manche` · `1re manche` |
| T10 | Séparateur de milliers : espace insécable (fine ou normale) à partir de 10 000, jamais une espace ordinaire, une virgule ni un point ; virgule décimale, jamais le point anglais. Pas concernés : années, codes postaux, numéros de téléphone, numéros de règle ou de version (`règle 3.2`, `version 1.0.2`) | `10000 points` · `10,000` · `10.000` · `10 000` (espace ordinaire) · `2.5 PV` | `10[U+202F]000 points` · `2,5[U+00A0]PV` |
| T11 | Incise : tiret demi-cadratin, jamais un trait d'union ; espace insécable **à l'intérieur** de l'incise (après le tiret ouvrant, avant le tiret fermant), espace ordinaire à l'extérieur : une ligne ne finit jamais sur un tiret ouvrant | `cette carte - si elle est épuisée - reste` · `cette carte – si elle est épuisée – reste` (espaces ordinaires) | `cette carte –[U+00A0]si elle est épuisée[U+00A0]– reste` |
| T12 | Espace insécable après `n°`, entre un nombre et son unité ou son symbole (`PV`, `%`, `€`, `cm`…) | `n° 3` (espace ordinaire) · `3 PV` (ordinaire) · `50%` | `n°[U+00A0]3` · `3[U+00A0]PV` · `50[U+00A0]%` |

Une adresse web, une adresse e-mail, une entité HTML (`&nbsp;`) et une balise ou une icône (`{icon:gold}`, `<b>`) ne suivent pas ces règles : le programme ne les contrôle pas et ne les corrige pas. La ponctuation qui suit une adresse, elle, suit la charte (`exemple.fr[U+202F]!`). <!-- [R-47] [R-57] [R-61] -->

## Coupures de ligne et césure (à contrôler sur l'épreuve mise en page)
<!-- [R-61] -->
Le programme ne voit pas les fins de ligne : ces règles se vérifient sur l'épreuve (PDF), au moment du BAT (bon à tirer).
- Ne se séparent jamais d'une ligne à l'autre : un nombre et son unité ou son symbole, `n°` et son numéro (T12) ; un tiret d'incise et le mot qu'il touche à l'intérieur de l'incise (T11) ; un signe `;` `:` `!` `?` et le mot qui le précède (T01, T02) ; les groupes d'un nombre en milliers (T10). C'est le rôle de l'espace insécable : si elle est là, la coupure fautive ne peut pas se produire.
- Pas de césure (mot coupé par un trait d'union en fin de ligne) dans un nom propre, un nombre, un sigle ou une abréviation, ni dans un mot-clé ou un terme de jeu, qui doit rester reconnaissable d'un coup d'œil (sauf convention contraire écrite dans la fiche éditeur).
- Pas de coupure juste après une apostrophe (`l’` en fin de ligne, `action` à la suivante), ni de coupure qui laisse une seule lettre en fin de ligne (`é-` puis `tape`).
- Pas plus de trois lignes coupées de suite.

## Ce que le programme ne vérifie pas
<!-- [R-47] -->
Le programme `scripts/typo.py` lit tout le fichier, mais il ne voit pas tout. « 0 alerte » veut dire « aucune des fautes qu'il sait voir ». Il ne voit pas :
- les fins de ligne et la césure (section précédente : à contrôler sur l'épreuve) ;
- T08 : une capitale sans accent hors de sa liste de mots courants (`Etat`, `Etape`, `Epuisé`, `A la fin`…) ; `Ecoutez` ou `ELEMENTAIRE`, par exemple, passent ;
- T11 : un tiret espacé **seul** dans sa phrase, qui peut être un séparateur de titre (`Étape 1 – Mise en place`) ou une incise qui se ferme avec la phrase (`Il vint – enfin.`). Il voit le trait d'union pris pour un tiret, et l'incise à deux tirets dans la même phrase ;
- T12 : une unité hors de sa liste (`n°`, `PV`, `PA`, `PM`, `%`, `€`, `cm`, `mm`, `kg`, `g`) ; `30 min` ou `10 ans` passent ;
- les écarts propres à un éditeur (sa fiche) : le programme applique cette charte seule.

## Ce que la charte ne tranche pas (à demander à Hervé ou à lire dans la fiche éditeur)
- **Majuscule des termes de jeu** (« Défaussez une carte Équipement » ou « équipement ») : convention de l'éditeur, écrite dans sa fiche ; à défaut, la forme du glossaire fait foi.
- **Tutoiement ou vouvoiement du joueur**, infinitif ou impératif dans les règles : convention de l'éditeur.
- **Mots-clés en gras ou en petites capitales** : convention de l'éditeur, et forme exacte donnée par la colonne RAPPEL STANDARD du glossaire.

## Faire passer la typographie dans Word (sans outil)
`Ctrl+H` (Rechercher et remplacer), « Plus >> » puis « Spécial » :
- `Rechercher : ^w:` → `Remplacer : ^s:` (tout espace avant deux-points devient insécable). Même chose pour `;` `!` `?`.
- Espace fine plutôt que normale (si l'éditeur l'exige) : taper une fois l'espace fine dans le document (`202F` puis `Alt+X`), la copier (`Ctrl+C`), puis `Rechercher : ^w!` → `Remplacer : ^c!` (`^c` colle le contenu copié) ; même chose pour `;` et `?` (le deux-points garde l'insécable normale, T02). Pour trouver les espaces fines déjà posées : `Rechercher : ^u8239`. À essayer une première fois sur la version de Word d'Hervé, et noter dans `Core/Preferences.md` ce qui marche.
- `Rechercher : '` → `Remplacer : '` (avec l'option « Remplacer les guillemets droits par des guillemets typographiques » activée dans Fichier > Options > Vérification > Options de correction automatique > Lors de la frappe).
- `Rechercher : ...` → `Remplacer : …` (Alt+0133 sur le pavé numérique).
Toujours sur une **copie** du fichier, jamais sur l'original de l'éditeur.
