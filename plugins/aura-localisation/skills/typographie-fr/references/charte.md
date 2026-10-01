# Charte typographique française — la seule de l'extension

<!-- [I-36] -->

Cette charte est écrite **une seule fois**, ici. Tous les autres skills y renvoient. Chaque règle a un identifiant (T01…) qui est aussi celui du script `scripts/typo.py` ; un contrôle vérifie que les deux listes concordent.

**Les écarts propres à un éditeur** (par exemple : espace insécable normale partout au lieu de l'espace fine) s'écrivent dans sa fiche `Core/Editeurs/<Éditeur>.md`, section « Charte typographique », et passent avant cette charte pour ses textes.

Caractères invisibles (le point de code entre crochets) :
- espace insécable normale [U+00A0] — dans Word : `^s`
- espace fine insécable [U+202F] — pas de code Word ; à copier-coller, ou à faire poser par la mise en page
- apostrophe typographique ’ [U+2019]
- points de suspension … [U+2026]
- tiret demi-cadratin – [U+2013] — Word : `^=` ; tiret cadratin — [U+2014] — Word : `^+`

| Id | Règle | Faux | Juste |
|---|---|---|---|
| T01 | Espace insécable (fine ou normale) **avant** `;` `!` `?` — jamais d'espace ordinaire, jamais rien | `Défaussez !` (espace ordinaire) · `Défaussez!` | `Défaussez[U+202F]!` |
| T02 | Espace insécable normale **avant** `:` | `Effet : …` (espace ordinaire) · `Effet: …` | `Effet[U+00A0]: …` |
| T03 | Guillemets français `« »` avec espace insécable à l'intérieur ; guillemets anglais seulement pour une citation dans une citation | `"Éclat"` · `«Éclat»` | `«[U+00A0]Éclat[U+00A0]»` |
| T04 | Apostrophe typographique ’ | `l'action` (droite) | `l’action` |
| T05 | Points de suspension en un seul caractère | `...` | `…` |
| T06 | Pas d'espace avant `,` et `.` | `une carte , puis` | `une carte, puis` |
| T07 | Pas de double espace | `deux  espaces` | `deux espaces` |
| T08 | Majuscules accentuées | `Etape`, `Etat`, `Epuisé`, `A la fin` | `Étape`, `État`, `Épuisé`, `À la fin` |
| T09 | Ordinaux abrégés : `1er`, `1re`, `2e` — jamais `2ème`, `2nd`, `2eme` | `2ème manche` | `2e manche` |
| T10 | Séparateur de milliers : espace insécable (fine ou normale) à partir de 10 000 ; virgule décimale | `10000 points` · `10,000` | `10[U+202F]000 points` |
| T11 | Incise : tiret demi-cadratin entouré d'espaces (insécable avant) ; jamais un trait d'union | `cette carte - si elle est épuisée - reste` | `cette carte – si elle est épuisée – reste` |
| T12 | Espace insécable après `n°`, entre un nombre et son unité ou son symbole | `n° 3` (espace ordinaire), `3 PV` (ordinaire) | `n°[U+00A0]3`, `3[U+00A0]PV` |

## Ce que la charte ne tranche pas (à demander à Hervé ou à lire dans la fiche éditeur)
- **Majuscule des termes de jeu** (« Défaussez une carte Équipement » ou « équipement ») : convention de l'éditeur, écrite dans sa fiche ; à défaut, la forme du glossaire fait foi.
- **Tutoiement ou vouvoiement du joueur**, infinitif ou impératif dans les règles : convention de l'éditeur.
- **Mots-clés en gras ou en petites capitales** : convention de l'éditeur, et forme exacte donnée par la colonne RAPPEL STANDARD du glossaire.

## Faire passer la typographie dans Word (sans outil)
`Ctrl+H` (Rechercher et remplacer), « Plus >> » puis « Spécial » :
- `Rechercher : ^w:` → `Remplacer : ^s:` (tout espace avant deux-points devient insécable). Même chose pour `;` `!` `?`.
- `Rechercher : '` → `Remplacer : '` (avec l'option « Remplacer les guillemets droits par des guillemets typographiques » activée dans Fichier > Options > Vérification > Options de correction automatique > Lors de la frappe).
- `Rechercher : ...` → `Remplacer : …` (Alt+0133 sur le pavé numérique).
Toujours sur une **copie** du fichier, jamais sur l'original de l'éditeur.
