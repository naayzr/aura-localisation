---
name: typographie-fr
description: "Typographie française d'un texte traduit : contrôle exact, par programme, des espaces insécables (avant : ; ! ? et dans les guillemets), des guillemets « », de l'apostrophe ’, des points de suspension, des majuscules accentuées, des ordinaux, du séparateur de milliers et des tirets, dans un fichier Word, Excel, CSV ou texte ; donne la liste des fautes par ligne ou par carte et comment les corriger. À utiliser pour « vérifie la typo », « les insécables », « les guillemets », « passe la typographie », avant une livraison, ou quand un autre outil d'AURA demande la charte typographique. Seul endroit où les règles typographiques sont écrites."
---

# Typographie française

La charte complète est dans `references/charte.md` : **c'est le seul endroit de l'extension où les règles typographiques sont écrites.** Les autres skills (traduction, vérification, relecture) y renvoient. Si une règle change, elle change là, et dans le programme qui l'applique (même identifiant T01…).

Les **écarts d'un éditeur** (par exemple : espace insécable normale partout, mots-clés en petites capitales) sont dans sa fiche `Core/Editeurs/<Éditeur>.md`, section « Charte typographique », et passent avant la charte pour ses textes. Tu lis cette section avant de contrôler un texte de cet éditeur.

## Pourquoi un programme
Les espaces insécables, l'apostrophe droite ou courbe, « ... » contre « … » sont **invisibles à la lecture** : un modèle de langue ne les voit pas de façon fiable. Le programme, lui, lit chaque caractère, sur tout le fichier, et compte exactement. Il ne coûte presque rien au quota.

## Contrôler un fichier
1. Applique d'abord la règle « Les programmes et le dossier d'Hervé » du skill `noyau` : le programme voit-il le fichier ? Sinon, Hervé le glisse dans la conversation ; si le programme ne le lit toujours pas, tu ne présentes aucun contrôle comme fait.
2. Lance, depuis le dossier de ce skill :
   - un texte, un Word : `python3 scripts/typo.py "<fichier>"`
   - un tableur de cartes : `python3 scripts/typo.py "<fichier>" --colonne FR` (le nom exact de l'en-tête de la colonne française)
3. **Avant de croire un résultat « 0 alerte »**, lance `python3 scripts/typo.py --auto-test` : le programme doit trouver les 11 fautes glissées exprès dans son extrait de contrôle. S'il échoue, tu ne présentes pas le résultat comme fiable.
4. Présente à Hervé : le nombre d'alertes par règle (verdict d'abord), puis les premières alertes avec leur repère (paragraphe §, ligne L, cellule). Les alertes T08 (majuscules) et T10 (milliers) sont à **vérifier** : un nom propre ou un identifiant peut être voulu.

## Corriger
- **Texte, CSV** : `--corriger` écrit une **copie** `<nom>_typo.<ext>` avec les corrections sûres (apostrophes, points de suspension, espaces en trop) ; l'original n'est jamais modifié, et la copie n'en écrase jamais une autre.
- **Word, Excel** : tu ne modifies pas le fichier. Tu donnes à Hervé les Rechercher/Remplacer de la charte (section Word), à faire sur une **copie** dans `Livrables/<Projet>/`, ou tu prépares les corrections dans un tableau « repère → faux → juste ».
- Les espaces fines insécables [U+202F] n'ont pas de raccourci dans Word : si l'éditeur les exige, c'est souvent la mise en page qui les pose ; demande-le à Hervé et note la réponse dans la fiche éditeur.

## Ce que ce skill ne tranche pas
La majuscule des termes de jeu, le tutoiement du joueur, l'impératif ou l'infinitif, le gras des mots-clés : conventions de l'éditeur (fiche éditeur) ou du glossaire (colonne RAPPEL STANDARD). Tu demandes si rien n'est écrit, et tu notes la réponse dans la fiche.
