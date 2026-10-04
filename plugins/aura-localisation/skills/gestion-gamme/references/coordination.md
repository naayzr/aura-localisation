# Coordination des traducteurs et relecteurs

Quand une gamme dépasse ce qu'Hervé peut traduire seul dans les délais, il répartit le travail. AURA
prépare les documents, compte, suit les échéances et fusionne les questions ; Hervé choisit les
personnes, fixe les conditions et envoie lui-même tout ce qui part.

AURA ne recrute personne, ne propose aucun tarif et n'accepte aucune condition : ce sont des
engagements d'Hervé.

## 1. Le brief type pour un traducteur ou un relecteur

<!-- [I-33] -->
AURA le prépare **quand Hervé le demande** (« prépare le brief pour Sacha »), à partir des fichiers
réels de la gamme. Rien n'est envoyé automatiquement. Le brief est un document Word ou texte qu'Hervé
relit et envoie.

Contenu, dans cet ordre :

1. **Le projet en dix lignes** : jeu, produit, public, ton de l'univers, ce qui existe déjà en
   français (boîte de base publiée, glossaire).
2. **Le lot confié** : fichier, plage exacte (cartes C041 à C120, pages 12 à 18…), volume en
   caractères **compté sur le fichier** (skill `comptage-caracteres`), échéance de livraison.
3. **Le glossaire de la gamme** : export produit par le skill `glossaire`. On y explique ce que
   chaque statut permet : Confirmé et Gelé s'appliquent sans discussion, À confirmer s'applique en
   attendant la réponse de l'éditeur, Brouillon est une proposition qu'on peut contester. Un terme
   absent du glossaire n'est jamais inventé : il fait l'objet d'une question.
4. **La charte typographique** : export de la charte du skill `typographie-fr`, plus les écarts propres
   à l'éditeur notés dans sa fiche (skill `brief-editeur`). Le brief n'en recopie aucune règle à la main.
5. **La procédure de questions** : une question = une ligne d'un tableau fourni (référence de la carte
   ou de la règle, texte anglais, question, proposition). Les questions vont à Hervé, jamais
   directement à l'éditeur, à des dates fixées dans le brief (par exemple chaque vendredi).
6. **Ce qu'on peut modifier et ce qu'on commente** : les termes de jeu et les mots-clés du glossaire
   ne se modifient pas, on les commente ; balises et icônes (`{icon_sword}`, `<b>`, `[damage]`) restent
   intactes ; les identifiants et l'ordre des lignes du fichier ne bougent pas.
7. **Le format de livraison** : le fichier reçu, avec la colonne ou le texte français rempli, nommé
   `<fichier>_FR_<prénom>_v1`.
8. **Le contact** pour une question bloquante, et le délai de réponse d'Hervé.

<!-- [I-12] -->
Écriture : phrases complètes, chiffres exacts (« 82 cartes, 14 310 caractères »), aucun code interne
(pas d'identifiant de glossaire, pas de « Brouillon » non expliqué, pas d'abréviation non traduite).
Ce que le brief dit, ou non, de l'outil et de l'intelligence artificielle suit la règle « Mention
d'AURA et de l'IA » du skill `brief-editeur`. <!-- [R-33] -->

## 2. L'attribution des lots

1. **Compter d'abord** : volume total et volume par découpage possible (chapitre, faction, type de
   carte), avec le skill `comptage-caracteres`. Un découpage se juge sur des chiffres réels.
2. **Demander la capacité** de chaque personne (caractères par jour) et ses disponibilités. Jamais
   supposées.
3. **Découper par cohérence de voix** : une faction, un personnage ou un type de carte par personne,
   pour que le ton reste uni sur un même ensemble. Les mots-clés, le livret de règles et tout ce qui
   fixe un terme restent à Hervé ou à la personne la plus expérimentée de la gamme.
4. **Vérifier que le planning tient** : le rétroplanning (`scripts/retroplanning.py`) se calcule avec la
   capacité cumulée, et chaque lot reçoit une échéance antérieure à la fin de la traduction.
5. **Écrire les lots** dans le tableau « Lots » du registre de gamme (contenu, caractères, attribué à,
   échéance), après validation d'Hervé.

Exemple de répartition [EXEMPLE FICTIF] (personnes et capacités inventées) : 320 000 caractères,
le responsable de gamme à 12 000 par jour, Sacha à 8 000 par jour, 20 jours ouvrés disponibles.
Capacité cumulée : 20 × (12 000 + 8 000) = 400 000, le volume tient. Le responsable de gamme garde le
livret de règles et les mots-clés (180 000 caractères, 15 jours), Sacha prend les cartes de deux
factions (140 000 caractères, 17,5 jours, donc 18 jours ouvrés).

## 3. Le suivi des livraisons

<!-- [I-04] -->
- Un lot dont l'échéance est passée sans livraison donne une ligne dans `Core/Suivi.md` (« lot 2,
  attendu le 2026-11-20, non livré »), relue au démarrage de chaque séance.
<!-- [I-08] -->
- Avant de signaler ou de relancer, AURA vérifie que le lot n'est pas déjà arrivé (fichier présent
  dans `Livrables/<Projet>/`, tableau des lots à jour) ; une ligne périmée de `Core/Suivi.md` est close
  selon la règle des fils du skill `noyau` (jamais effacée), au lieu d'être recopiée. <!-- [R-27] -->
- À la livraison, contrôle de complétude **compté** : nombre de cartes ou de segments reçus contre
  attendus (« 82 sur 82 », ou « 80 sur 82 : manquent C097 et C112 »), identifiants intacts, balises
  intactes. Les contrôles automatiques de termes, de typographie et de longueur passent par les skills
  `qa-coherence`, `typographie-fr` et `controle-longueur`.
- Puis la relecture du lot (voir `references/relecture-tiers.md`), et la mise à jour du tableau des
  lots : Livré le, Relu le, Statut.
- Le fichier du traducteur n'est jamais écrasé : AURA travaille sur une copie
  `Livrables/<Projet>/<fichier>_relu_v1`.

## 4. La fusion des questions de plusieurs traducteurs

Chaque traducteur envoie son tableau de questions. AURA les fusionne dans `Core/Questions_Editeurs.md`
(format décrit dans le skill `brief-editeur`) :

<!-- [I-35] -->
1. **Chercher avant de transmettre.** Pour chaque question : le terme est-il déjà au glossaire
   (toutes ses variantes : pluriel, majuscule, forme verbale) ? La même question a-t-elle déjà reçu une
   réponse dans le registre des questions, sur ce produit ou un produit précédent de la gamme ? Si oui,
   la réponse va au traducteur directement, la question ne part pas chez l'éditeur.
2. **Regrouper les doublons.** Deux traducteurs qui butent sur le même passage ou le même terme = une
   seule question, colonne « Posée par » remplie avec les deux prénoms.
3. **Séparer ce qui relève de l'éditeur** (sens du jeu, intention de l'auteur, terme de licence) de ce
   qui relève d'Hervé (choix de langue, style) : Hervé répond lui-même aux secondes.
4. **Numéroter à la suite** dans le registre des questions, statut « À envoyer ».
5. L'envoi groupé à l'éditeur passe par le skill `brief-editeur`. Quand la réponse arrive, AURA prépare
   pour chaque traducteur la liste des réponses qui le concernent.
