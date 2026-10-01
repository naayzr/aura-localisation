---
name: maquettes
description: "Maquettes et visuels pour le métier d'Hervé : planche de toutes les cartes en français aux dimensions réelles pour voir d'un coup celles dont le texte ne tient pas, fichier de fusion de données pour InDesign ou Affinity, épreuves (BAT) en PDF, règle en PDF à rendre modifiable, présentation d'une gamme à un éditeur, visuel de boîte ou de sortie. Choisit l'outil (inclus dans Claude, plugin Adobe, Affinity gratuit, Canva) selon le besoin, le coût et la confidentialité du jeu. À utiliser pour « maquette », « planche de cartes », « est-ce que ça tient sur la carte », « mise en page », « InDesign », « Affinity », « Adobe », « Canva », « présentation pour l'éditeur », « visuel »."
---

# Maquettes et visuels

Le choix des outils vient d'un relevé sourcé (01/10/2026). Tu ne promets **jamais** un outil, un compte ou un prix que tu n'as pas vérifié à l'écran avec Hervé : les noms et les offres changent (le plugin Adobe s'appelait encore « Adobe for creativity » il y a peu).

## Les trois règles avant toute maquette
1. **Confidentialité** : un jeu non annoncé est souvent sous accord de confidentialité. Le plugin Adobe et Canva **envoient les fichiers sur les serveurs** de ces sociétés. Avant d'y déposer un BAT, un gabarit ou un texte, tu lis la fiche de l'éditeur (`Core/Editeurs/<Éditeur>.md`, clauses IA et confidentialité) ; si rien n'est écrit, tu demandes. Les outils inclus dans Claude et les logiciels installés sur son PC n'envoient rien à un tiers.
2. **Les polices** : une planche ou une maquette faite avec une police de remplacement ne prouve **rien** sur le débord. « Ça tient » ne se dit qu'avec le vrai gabarit et la vraie police (InDesign, Affinity, épreuve de l'éditeur). Une réduction automatique du corps pour faire tenir n'est pas une solution : c'est à signaler.
3. **Coût** : rien de payant sans son oui sur le montant exact (InDesign seul : 26,21 € TTC par mois en France au 01/10/2026, à revérifier). Toutes ces créations puisent aussi dans son quota Claude.

## Du plus simple au plus exact

| Besoin | Outil, dans l'ordre | Ce qu'il faut |
|---|---|---|
| **Voir quelles cartes débordent** | 1) la **planche de cartes** de ce skill (ci-dessous) ; 2) la fusion dans le vrai gabarit (Affinity gratuit ou InDesign) | le tableur de cartes ; le format de la carte et de sa zone de texte ; la police et le corps de l'éditeur |
| **Épreuve exacte avec le gabarit de l'éditeur** | **Affinity** (gratuit, compte Canva gratuit) ou **InDesign** (payant), fusion de données depuis le fichier préparé par la planche (`--csv-fusion`) ; ou la fusion InDesign du **plugin Adobe** (abonnement InDesign exigé, fichiers envoyés chez Adobe) | le gabarit .indd ou .idml de l'éditeur (le demander plutôt que convertir un PDF) |
| **Relire un BAT (épreuve PDF)** | Tu compares le texte du PDF au tableur validé et au glossaire (skills `gestion-gamme`, BAT, et `controle-longueur`), tu produis la liste des corrections en Word ou Excel (page, ligne, erreur, correction) ; Hervé la pose en commentaires dans **Acrobat Reader** (gratuit, déjà sur son PC) — ou dans l'éditeur PDF du plugin Adobe, où **c'est lui** qui valide chaque annotation | le PDF du BAT |
| **Règle en PDF à rendre modifiable** | D'abord demander à l'éditeur le texte source ou l'IDML ; sinon tu extrais le texte vers Excel ou Word ; le plugin Adobe sait exporter un PDF en Word et lire un scan en français (texte qui peut sortir décalé sur les pages illustrées) | le PDF |
| **Présenter une gamme ou un plan de localisation à un éditeur** | **Claude Design** (inclus dans Pro, exporte en PDF ou PowerPoint) ou un PowerPoint que tu crées | le contenu ; pas d'illustration de l'éditeur sans son accord |
| **Un visuel** (fiche de gamme, annonce de sortie, boîte « à la française » pour une présentation interne) | **Adobe Express** par le plugin Adobe (compte Adobe gratuit), ou **Canva** (optionnel ; création en série seulement avec Canva Pro) | les illustrations appartiennent à l'éditeur : présentation interne, avec accord ; une image générée n'est jamais un visuel définitif |

Figma ne lui sert pas (place payante, outil de développement).

## La planche de cartes — `scripts/planche.py`
Une page HTML qui dessine **toutes** les cartes en français aux dimensions réelles, chaque texte dans sa zone ; ouverte dans le navigateur, elle compte les cartes qui débordent et les met en rouge.
1. Applique d'abord la règle « Les programmes et le dossier d'Hervé » du skill `noyau` (le programme voit-il le tableur ? sinon, le glisser).
2. Demande à Hervé le **format** de la carte, la **zone de texte** (position et taille en mm, à mesurer sur le gabarit ou l'épreuve), la **police** et le **corps** de l'éditeur ; s'il ne les a pas, tu le dis : la planche sera une approche grossière.
3. Lance : `python3 scripts/planche.py "<tableur>" --fr FR --id Carte --titre Nom --largeur 63 --hauteur 88 --zone 5,45,53,38 --police "Nom de la police" --taille 8.5` (les en-têtes exacts de ses colonnes). Ajoute `--csv-fusion Livrables/<Projet>/fusion` pour préparer la fusion InDesign ou Affinity (un fichier UTF-8 et un UTF-16).
4. La planche est un fichier **texte** : si le programme l'a écrite hors du dossier (tâche dans le cloud), tu la **réécris toi-même** dans `Livrables/<Projet>/planche_cartes.html`. Hervé l'ouvre d'un double-clic.
5. Tu présentes : « 340 cartes, 12 débordent : C03, C17… — approche avec la police X ; à confirmer sur l'épreuve. » Puis les propositions de raccourci qui gardent la mécanique (skill `controle-longueur`).
6. Avant de croire « 0 carte déborde » : `python3 scripts/planche.py --auto-test` doit répondre OK, et la police doit être installée sur son PC (sinon la mesure est faite avec une autre).

## Installer le plugin Adobe — seulement s'il le demande
Personnaliser > Connecteurs (ou Plugins) > chercher « Adobe » > l'ajouter, puis se connecter avec un compte Adobe (gratuit suffit pour Acrobat et Express ; la fusion InDesign exige l'abonnement InDesign). Tu vérifies à l'écran avec lui ; tu ne t'occupes jamais de ses identifiants.
