---
name: controle-longueur
description: "Contrôle, carte par carte ou ligne par ligne, de la longueur du texte français face à l'anglais (expansion, débord du cadre de texte, maximum fixé par l'éditeur ou le maquettiste) et de l'intégrité de chaque traduction : balises et icônes ({icone}, balises de mise en forme comme b ou i, [degats]) présentes et identiques, nombres identiques, aucune traduction vide. Fonctionne sur un tableur de cartes (Excel, CSV) ou deux Word alignés. Propose des raccourcissements qui gardent la mécanique. À utiliser pour « ça déborde », « c'est trop long », « vérifie les longueurs », « les balises », « les icônes », « les chiffres des cartes », avant un BAT."
---

# Longueur, débord et intégrité des cartes

Le français est souvent plus long que l'anglais, mais la vraie contrainte est **le cadre de texte de chaque carte**. Et une balise perdue ou un chiffre changé donne une carte fausse à l'impression. Ce contrôle se fait par programme, sur tout le fichier, sans coût notable sur le quota.

## Contrôler
Applique d'abord la règle « Les programmes et le dossier d'Hervé » du skill `noyau` (le programme voit-il le fichier ? sinon, le glisser ; les rapports s'écrivent dans HERVÉ WORLD). Puis, avec le programme et les fichiers en chemins complets (règle « Écrire une commande » du skill `noyau`) : <!-- [R-29] -->
- **Tableur de cartes** : `python3 "${CLAUDE_SKILL_DIR}/scripts/longueurs.py" "<fichier>" --en EN --fr FR --id Carte` (les en-têtes exacts des colonnes).
  - Seuil d'expansion : `--seuil 1.25` par défaut (+25 % et au moins 10 caractères de plus). L'éditeur ou le maquettiste peut donner un autre seuil : il est noté dans sa fiche `Core/Editeurs/<Éditeur>.md` ou dans le registre de gamme.
  - Maximum connu : `--max 180` (tous les champs), ou `--max-col Max` si le tableur a une colonne de longueur maximale par ligne. Une case de cette colonne qui n'est pas un nombre (« N/A ») est listée en fin de rapport : la ligne est contrôlée sans son maximum, tu la montres à Hervé.
  - Un nom de colonne demandé (`--en`, `--fr`, `--id`, `--max-col`) absent des en-têtes arrête le programme, qui liste les en-têtes lus : tu reprends avec le nom exact, rien n'a été contrôlé entre-temps. <!-- [R-58] [R-49] -->
- **Deux Word** (source et traduction) : `python3 "${CLAUDE_SKILL_DIR}/scripts/longueurs.py" "<source.docx>" "<cible.docx>"`. Seulement s'ils ont le même nombre de paragraphes ; sinon le programme le dit et s'arrête plutôt que de mal aligner.
- **Avant de croire « 0 alerte »** : `python3 "${CLAUDE_SKILL_DIR}/scripts/longueurs.py" --auto-test` doit répondre « AUTO-TEST OK » (toutes les fautes glissées exprès trouvées, aucune fausse alerte sur les cartes propres).

## Lire le rapport
- **[L] longueur / débord** : à raccourcir, ou à signaler au maquettiste.
- **[B] balises ou icônes** : manquantes ou en trop. Toujours une erreur à corriger avant livraison, sauf accord écrit de l'éditeur. Une balise est reconnue comme dans le skill `comptage-caracteres` (un identifiant sans espace).
- **[N] nombres** : différents entre l'anglais et le français (le séparateur de milliers ne compte pas : « 1,000 » et « 1 000 » sont le même nombre). Souvent une vraie erreur (« one card » traduit par « deux cartes »). Parfois voulu (un chiffre écrit en toutes lettres) : tu le présentes comme « à vérifier », tu ne tranches pas.
- **[V] traduction vide** : ligne oubliée.
Tu présentes : le verdict chiffré, puis le tableau « carte → alerte → proposition ».

## Raccourcir sans casser la mécanique
Pour chaque carte en débord, tu proposes 1 ou 2 versions plus courtes qui **gardent** : le caractère facultatif ou obligatoire (« peut » ≠ « doit »), les bornes (« jusqu'à », « au moins », « exactement »), le moment de déclenchement et la durée, la cible (« un autre joueur » ≠ « un joueur »), les mots-clés **sous leur forme exacte du glossaire** (colonne RAPPEL STANDARD). Tu ne raccourcis jamais un mot-clé ni un terme Gelé. Hervé choisit.

Les règles de typographie sont dans le skill `typographie-fr` ; les termes, dans le skill `glossaire`.

## Au moment du BAT
La liste des cartes en alerte [L] est reprise au contrôle de l'épreuve mise en page (skill `gestion-gamme`, BAT) : ce sont les premières à regarder sur le PDF.
