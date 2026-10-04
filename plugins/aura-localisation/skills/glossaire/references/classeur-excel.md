# Le classeur du glossaire au standard

<!-- [I-13] -->
Un classeur se juge ligne à ligne et d'un coup d'œil. Le programme (`gerer_glossaire.py`, brique
`modele_glossaire.py`) écrit **toujours le même classeur** ; AURA ne le refait pas à la main avec une mise
en forme différente à chaque fois. Les règles propres aux tableaux financiers (salaires, impôts) ne
s'appliquent pas ici.

## Les onglets, dans cet ordre

**1. Tableau de bord** — s'ouvre en premier. Rien à y saisir : tout est **calculé par formule** à partir
de l'onglet Termes, donc juste même après une modification faite à la main dans Excel.
- Version du glossaire (dernière ligne du CHANGELOG).
- Nombre de termes (lignes avec un anglais), en total surligné.
- Nombre de termes affichés avec le filtre actuel de l'onglet Termes (formule qui ne compte que les
  lignes visibles) : Hervé filtre « LORE », le tableau de bord lui dit combien il en voit.
- Par statut : les 5 statuts, leur total, et « statut vide ou hors liste » qui **doit valoir 0**.
- Ensembles utiles, **définis par ce qu'ils contiennent** : À trancher (Brouillon + À confirmer), En
  vigueur (Confirmé + Gelé), Gardés pour trace (Archivé). Jamais « tout sauf Confirmé », qui avalerait les
  Gelés et les Archivés.
- Par catégorie : les 9 catégories, et « catégorie vide ou hors liste » (doit valoir 0).
- Points à régler : genres à déclarer (catégories qui l'exigent, termes non archivés), Gelés sans PUBLIÉ
  DANS.
- Par produit : une ligne par produit cité dans PUBLIÉ DANS. Un nouveau produit apparaît à la prochaine
  écriture par le programme.
- Toute case « doit valoir 0 » ou « à régler » qui dépasse 0 passe en **rouge**.

**2. Termes** — les 15 colonnes du modèle (SKILL.md, section 2), dans l'ordre.
- En-tête sur fond bleu foncé, texte blanc ; ligne d'en-tête et colonnes ID et EN **figées**.
- **Filtres** actifs sur toutes les colonnes.
- **Couleur de ligne selon le statut** : Brouillon rose pâle, À confirmer orange pâle, Confirmé vert pâle,
  Gelé bleu (texte bleu foncé en gras), Archivé gris barré.
- **Listes déroulantes** sur CATÉGORIE, GENRE, NOMBRE, ÉLISION et STATUT : Excel refuse une valeur tapée
  hors liste, ce qui empêche un sixième statut d'apparaître par une faute de frappe (une valeur collée peut
  passer : le contrôle la trouve).
- Texte renvoyé à la ligne, alignement en haut ; impression en paysage sur la largeur d'une page, en-tête
  répété sur chaque page, pied de page avec le nom de l'onglet et le numéro de page.

**3. CHANGELOG** — la mémoire du glossaire. Colonnes : DATE · VERSION · ID · EN · CHAMP · AVANT · APRÈS ·
RAISON · DÉCIDÉ PAR. Une ligne par valeur changée (un import ou une fusion : une ligne de synthèse). On
ajoute en bas, on n'efface jamais. En-tête figé, filtres.

**4. Notice** — une page imprimable : ce qu'est le classeur, ses onglets, ses colonnes, les 5 statuts et
les règles (un sens mécanique = un terme ; décision de terme au seul glossaire ; genre déclaré par
Hervé ; Gelé = erratum ; fermer Excel avant qu'AURA écrive). Écrite par le programme à partir des mêmes
listes que le reste : elle ne peut pas diverger du modèle.

## Les chiffres

- Les formules couvrent les lignes 2 à 20 000 de Termes (largement au-delà d'un glossaire de gamme).
- Les valeurs sont aussi pré-calculées à l'écriture : un aperçu (sans recalcul) montre déjà les bons
  chiffres ; Excel recalcule tout à l'ouverture.
- AURA rapporte à Hervé les chiffres du programme ou du tableau de bord, jamais une estimation.

## Ce que le programme ne sait pas garder

<!-- [R-30] -->
Le classeur est réécrit en entier à chaque écriture par le programme (après sauvegarde datée). Ce qu'il
ne sait pas réécrire est traité ainsi, et jamais en silence :

| Ajout fait à la main dans Excel | Ce que fait le programme |
|---|---|
| Onglet en plus ; colonne en plus (ou cellule sans en-tête) dans Termes ou dans CHANGELOG | **refuse** d'écrire, et le nomme. AURA le dit à Hervé et ils décident ensemble (déplacer l'onglet dans un autre classeur, porter la colonne en NOTES ou en RAISON) |
| Commentaire Excel posé sur la ligne d'un terme | le **reprend** à la fin des NOTES du terme (« Commentaire Excel (FR) : … »), avec sa ligne au CHANGELOG |
| Commentaire Excel posé ailleurs (Tableau de bord, Notice, en-tête) | **refuse** d'écrire et le cite : Hervé le recopie où il veut, puis le supprime |
| Texte tapé dans le Tableau de bord ou la Notice | ces deux onglets sont régénérés : chaque texte qui ne sera pas gardé est **listé**, à l'essai et à l'écriture, pour qu'Hervé le voie avant de dire oui |
| Couleur de cellule, largeur de colonne, mise en forme | **pas gardée** ; l'essai le rappelle. La sauvegarde datée la garde |

Le contrôle (`controle_glossaire.py`) signale les commentaires Excel et les colonnes hors standard ; le texte tapé dans le Tableau de bord ou la Notice, lui, n'est listé que par `gerer_glossaire.py` (« NON GARDÉ », à l'essai comme à l'écriture). Pour une simple
correction d'une cellule, Hervé peut aussi la faire lui-même dans Excel ; AURA la trace ensuite
(commande `comparer`). Si la tâche tourne hors de l'ordinateur d'Hervé, la sauvegarde datée suit la
règle « Les programmes et le dossier d'Hervé » du skill `noyau`.
