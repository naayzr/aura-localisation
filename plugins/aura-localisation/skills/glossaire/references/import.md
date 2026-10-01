# Importer un glossaire existant

<!-- [D-24] -->
Ce qui arrive d'ailleurs — un ancien glossaire Excel ou CSV d'Hervé, un glossaire officiel d'éditeur ou
de licence, la liste d'un relecteur, le glossaire de la démonstration du 30/05 — passe par cette
procédure. Trois règles ne bougent pas :

1. **Rien n'entre validé.** Tout terme importé est en Brouillon. Son statut d'origine est gardé mot pour
   mot dans NOTES (« Statut d'origine : … »). C'est Hervé qui valide, par lots, après l'import.
2. **Jamais un second glossaire maître.** Si `Glossaires/Glossaire_<Gamme>.xlsx` existe, l'import est une
   fusion (`--dans`). Le programme refuse une création à côté d'un fichier au nom voisin.
3. **L'original ne bouge pas.** Il reste dans `IMPORT/` tel quel ; on ne le renomme pas, on ne le
   supprime pas. S'il faut le ranger ailleurs, c'est avec l'accord d'Hervé, et par copie.

Exception assumée : un glossaire officiel imposé par un ayant droit (licence) entre lui aussi en
Brouillon ; sa SOURCE dit « glossaire officiel de licence, <document>, <date> » et Hervé peut le valider
en un seul lot, puisque la décision appartient à l'ayant droit. C'est une validation explicite, pas un
import pré-validé.

## Déroulé

1. **Le fichier.** Hervé le dépose dans `IMPORT/` ou le glisse dans la conversation (la règle « Les programmes et le dossier d'Hervé » du skill `noyau` dit lequel des deux marche dans la tâche en cours). AURA demande la
   gamme concernée si elle ne ressort pas du fichier, et vérifie le nom d'usage dans `Core/Gammes/`.
2. **Le maître existe-t-il ?** AURA regarde `Glossaires/`. Oui → fusion. Non → création.
3. **Essai** (rien n'est écrit) :
   ```
   gerer_glossaire.py importer IMPORT/<fichier> --gamme "<Gamme>" --sortie "Glossaires/Glossaire_<Gamme>.xlsx" --provenance "<d'où il vient>"
   gerer_glossaire.py importer IMPORT/<fichier> --gamme "<Gamme>" --dans "Glossaires/Glossaire_<Gamme>.xlsx" --provenance "…"
   ```
4. **Ce qu'AURA montre à Hervé**, chiffres du programme tels quels :
   - le nombre de termes **compté** (et l'écart, s'il y en a un, avec un nombre annoncé ailleurs) ;
   - la correspondance des colonnes (ci-dessous) ;
   - les lignes ignorées : titres de section, lignes sans anglais, lignes où seul l'anglais est rempli ;
   - les statuts d'origine et leur nombre ;
   - les catégories proposées, en tableau (type d'origine → catégorie), à valider d'un coup ;
   - les cellules françaises à plusieurs propositions (« Voyage / Trajet ») : à trancher ;
   - le nombre de genres à déclarer ;
   - pour une fusion : ajouts, termes déjà présents à l'identique, **conflits non appliqués** (même
     anglais, autre français, sans définitions qui les distinguent), français déjà pris par un autre
     anglais.
5. **Avec son accord** : même commande avec `--ecrire`. Le programme sauvegarde le maître (fusion),
   écrit, relit et recompte.
6. **Contrôle** : `controle_glossaire.py Glossaires/Glossaire_<Gamme>.xlsx`.
7. **Séance de validation**, par lots, dans cet ordre : catégories proposées → genres (liste groupée,
   jamais devinés) → cellules à double proposition → conflits → statuts. Les décisions s'appliquent avec
   `gerer_glossaire.py modifier … --lot decisions.csv`.
8. **Journal** : une ligne (« glossaire <Gamme> importé depuis <fichier> : N termes en Brouillon, M à
   valider »). La décision sur chaque terme vit au glossaire, pas au Journal.

## Correspondance des colonnes

Le programme reconnaît l'en-tête quelle que soit la casse, les accents ou la ponctuation. S'il ne trouve
pas de colonne anglaise et française, il s'arrête et demande : `--colonne EN="<en-tête>" --colonne FR="<en-tête>"`.

| En-têtes reconnus dans la source | Colonne du glossaire |
|---|---|
| EN, Terme (EN), Terme anglais, Anglais, English, VO, Terme source | EN |
| FR, Terme (FR), Terme français, Français, Traduction, VF, Terme cible, TERME_FR_RETENU | FR |
| Catégorie, Category | CATÉGORIE si la valeur est déjà une des 9 catégories ; sinon proposition |
| Type, Nature | sert à proposer la CATÉGORIE ; la valeur d'origine va en NOTES |
| Genre, Nombre, Élision | GENRE, NOMBRE, ÉLISION si la valeur est lisible (m, masculin, f, féminin…) ; sinon NOTES |
| Définition, Définition mécanique | DÉFINITION MÉCANIQUE |
| Rappel, Reminder | RAPPEL STANDARD |
| Publié dans, Produits | PUBLIÉ DANS |
| Statut, Status, État | NOTES (« Statut d'origine ») — le STATUT devient Brouillon |
| ID, Réf, N° | NOTES (« ID d'origine ») — un nouvel ID `T-0001…` est donné |
| Source, Origine, Projet d'origine | NOTES (« Source d'origine ») ; SOURCE reçoit `--provenance` |
| Notes, Commentaire, Contexte, Justification | NOTES |
| toute autre colonne | NOTES, sous la forme « En-tête : valeur » — rien n'est perdu |

Les lignes au-dessus de l'en-tête (titre, ligne « Source : … ») sont affichées : AURA s'en sert pour
rédiger `--provenance`, qui remplit la colonne SOURCE de chaque terme.

**Catégories proposées.** Le programme rapproche le type ou la catégorie d'origine des 9 catégories
(*Ressource, Action, Phase, Statut* → MÉCANIQUE ; *Composant, Carte, Jeton, Type de carte* → COMPOSANT ;
*Lieu, Lieu propre* → LIEU ; *Entité, Faction, Créature* → LORE ; *Personnage* → PERSONNAGE ; *Objet,
Item* → OBJET ; inconnu → AUTRE). C'est une **proposition**, marquée « CATÉGORIE proposée à l'import,
à valider » dans NOTES, parce qu'elle décide si le genre est obligatoire.

## Le glossaire Tainted Grail de la démonstration

Le fichier `Glossaire_TaintedGrail_EN-FR.xlsx` (relu le 01/10/2026 : 9 372 octets, une feuille, 64
lignes) a été **produit par AURA le 30/05/2026** pendant la démonstration de Dorian ; sa deuxième ligne
le dit. Dorian l'enverra à Hervé pour qu'il le dépose dans `IMPORT/`.

Ce que le programme y trouve (essai du 01/10/2026) :
- **53 termes**, et non 54 comme l'annonce l'entrée de démonstration du Journal : 64 lignes = 1 titre,
  1 ligne de source, 1 en-tête, 8 titres de section, 53 termes. AURA annonce 53 et signale l'écart ; elle
  ne réécrit pas le Journal (il ne s'efface pas).
- Colonnes : Catégorie · Terme (EN) · Terme (FR) · Type · Notes / Contexte · Statut.
- Statuts d'origine : « Confirmé PDF » 47, « À confirmer » 5, « À vérifier » 1. **« Confirmé PDF » a été
  attribué par AURA en mai, pas par Hervé ni par l'éditeur** : c'est exactement pourquoi rien n'entre
  validé. Les 53 termes arrivent en Brouillon.
- 2 cellules françaises à deux propositions (*Travel*, *Escape*), 1 cellule française avec une précision
  entre parenthèses (la ligne d'origine « À vérifier ») : Hervé tranche.
- 8 termes dont le genre est à déclarer (catégories PERSONNAGE, LIEU, LORE proposées).
- Les notes d'origine (dont des chiffres comme un nombre de cartes) sont reprises telles quelles en NOTES :
  elles n'ont pas été revérifiées et la provenance le dit.

Commande proposée (essai, puis `--ecrire` avec l'accord d'Hervé) :
```
gerer_glossaire.py importer "IMPORT/Glossaire_TaintedGrail_EN-FR.xlsx" --gamme "<nom d'usage de la gamme>" --sortie "Glossaires/Glossaire_<nom d'usage>.xlsx" --provenance "démo AURA du 30/05/2026, à partir des livrets cités dans le fichier, non revérifiée" --par "Hervé"
```
Si Hervé a déjà importé ou commencé un glossaire de cette gamme pendant la mise en place, c'est
`--dans` qui s'applique : fusion, conflits montrés, aucun second maître.

## Ce qui se passe mal, et la réponse

| Situation | Réponse |
|---|---|
| Aucune colonne anglaise ou française reconnue | le programme s'arrête ; `--colonne EN=… --colonne FR=…` |
| CSV avec une ligne de titre au-dessus de l'en-tête | le programme essaie chaque séparateur ( ; tabulation , | ) |
| Classeur à plusieurs feuilles | le programme prend la première qui a un en-tête anglais/français ; `--feuille` pour choisir |
| Lignes où seul l'anglais est rempli | ignorées et listées ; `--garder-seuls` si ce sont des termes à traduire |
| Fichier .docx, .pdf | pas d'import direct : AURA en extrait le tableau dans un CSV, le montre à Hervé, puis importe le CSV |
| Le maître n'est pas au standard (colonne ou onglet en plus) | refus de fusionner ; contrôle d'abord, Hervé décide de ce qu'on fait de la colonne en trop |
