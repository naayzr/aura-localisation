---
name: obsidian
description: "Obsidian pour Hervé (logiciel gratuit qui affiche son dossier HERVÉ WORLD) : l'accompagner pas à pas pour l'installer sous Windows et ouvrir son dossier comme coffre, préparer le dossier (page ACCUEIL, TABLEAU de bord, fiches d'univers et leurs modèles), créer et tenir les fiches d'univers d'un jeu (personnages, lieux, factions, objets) alignées sur le glossaire, et répondre à ses questions sur Obsidian. À utiliser pour « Obsidian », « installer Obsidian », « coffre Obsidian », « prépare mon dossier pour Obsidian », « je n'utilise plus Obsidian », « fais la fiche du personnage (du lieu, de la faction, de l'objet)… », « fiches des personnages », « fiches d'univers », « la fiche de … est relue », « bible de l'univers », « le tableau d'Obsidian affiche une erreur ». Pas pour la fiche d'un éditeur (skill brief-editeur) ni le registre d'une gamme (skill gestion-gamme)."
---

# Obsidian — une fenêtre de plus sur le dossier d'Hervé

Obsidian affiche les fichiers de HERVÉ WORLD ; il n'y ajoute rien et ne parle pas à AURA. Pour toi, rien ne change : mêmes fichiers, mêmes règles de mémoire. Ce skill sert à quatre choses : l'installation guidée, la préparation du dossier, les fiches d'univers, et les questions d'Hervé.

**Une seule écriture des étapes pour Hervé** : le guide `GUIDE_OBSIDIAN.md`, à la racine de son dossier (posé par AURA MISE À JOUR). Tu le lis et tu t'appuies dessus ; tu ne réécris pas les étapes de mémoire. S'il est absent, propose d'abord `AURA MISE À JOUR`.

## 1. Installer avec lui — « installe Obsidian avec moi »
- Suis les sections « Installer Obsidian », « Ouvrir ton dossier HERVÉ WORLD » et « Trois réglages » du guide, **une étape à la fois** : tu donnes l'étape, il la fait, il te dit ce qu'il voit, tu passes à la suivante. C'est lui qui clique ; toi, tu n'installes rien.
- Les libellés que tu cites sont ceux du guide, entre guillemets, à l'identique. S'il voit autre chose, demande-lui une capture d'écran plutôt que de deviner.
- Aucun compte, aucun mot de passe, aucun paiement : Obsidian n'en demande pas pour un dossier sur son PC. S'il voit une offre payante (Sync, Publish, licence commerciale), elle ne lui sert pas.
- Une fois le dossier ouvert dans Obsidian : passe à la préparation (section 2), qui se termine par les deux gestes du guide (signet sur ACCUEIL, dossier des modèles).

## 2. Préparer le dossier — « prépare mon dossier pour Obsidian »
Les fichiers à poser sont dans `references/graines/`, chacun au chemin où il doit arriver dans HERVÉ WORLD :
`ACCUEIL.md`, `TABLEAU.base`, `Références/Narration/Univers/LISEZ-MOI.md`, et les 4 modèles de `Références/Narration/_Modèles/` (Fiche personnage, Fiche lieu, Fiche faction, Fiche objet).
1. Pour chacun : **s'il existe déjà, tu n'y touches pas** (Hervé a pu le modifier) ; sinon, tu l'écris avec le contenu exact de la graine. Ce sont des fichiers texte : tu les écris toi-même avec tes outils de fichiers (règle « Les programmes et le dossier d'Hervé » du skill `noyau`).
2. Tu relis chaque fichier écrit (même contenu que la graine), puis tu dis ce qui a été posé et ce qui existait déjà.
3. Tu demandes : « Je note dans ton profil que tu utilises Obsidian ? » S'il dit oui, tu ajoutes dans `Core/Profile.md` la ligne `Obsidian : utilisé depuis le AAAA-MM-JJ, sur ce dossier.` (une ligne ajoutée, rien d'autre modifié). Sans réponse, tu n'écris rien.
4. Tu lui rappelles les deux gestes de la section « Demander à AURA de préparer ton dossier » du guide : le signet sur ACCUEIL, puis le dossier des modèles.
5. Tu lui dis que les tableaux d'ACCUEIL sont vides au début et se remplissent avec le travail.

**« Je n'utilise plus Obsidian »** : tu ajoutes sous la ligne du profil `Obsidian : arrêté le AAAA-MM-JJ.` (rien n'est effacé), et tu cesses d'écrire des liens (section 4). Tu ne supprimes aucun fichier.

## 3. Les fiches d'univers — « fais la fiche de… », « fais les fiches des personnages »
Le format, les propriétés et les cas difficiles sont dans `references/fiches-univers.md`. Les règles qui ne se discutent pas :
- **Le glossaire fait foi.** `nom_fr` et `id_glossaire` viennent du glossaire de la gamme. Un nom absent du glossaire passe d'abord par le skill `glossaire` (recherche, genre demandé à Hervé) ; en attendant, `nom_fr` et `id_glossaire` restent vides. Une décision de terme ne s'écrit jamais dans une fiche.
- **Rien d'inventé.** Chaque fait porte sa source (carte, page du livret, échange avec l'éditeur, avec la date). Ce qu'on ne sait pas va dans « Questions ouvertes ». Un exemple inventé est marqué `[EXEMPLE FICTIF]`.
- **Le nom du fichier est le nom anglais**, qui ne bouge pas quand le nom français change.
- **La porte, écrite ici seulement** : après toute modification d'un terme au glossaire, et avant de dire que les fiches d'une gamme sont cohérentes, `python3 scripts/fiches.py verifier --glossaire "Glossaires/Glossaire_<Gamme>.xlsx" --dossier "Références/Narration/Univers" --liens-dans Core/Gammes --liens-dans Core/Suivi.md --liens-dans Core/Questions_Editeurs.md` doit **sortir en code 0**. Le programme ne contrôle que les fiches de la gamme du glossaire (les identifiants se répètent d'un glossaire à l'autre). Code 2 = rien n'a été contrôlé (dossier ou gamme introuvable) : ce n'est jamais un « conforme ». Avant de croire un code 0, `python3 scripts/fiches.py --auto-test` doit répondre OK.
- **Ce que tu corriges, et comment** : un ÉCART ou un LIEN → la fiche (ou le lien) reprend le nom français du glossaire ; À RELIER → tu remplis `id_glossaire` et `nom_fr` comme indiqué ; REMPLACÉ → le terme a été archivé : tu proposes à Hervé le nouvel identifiant indiqué, et tu ne changes rien sans son oui ; ID INCONNU, DOUBLON, NOM DE FICHIER → tu montres la ligne à Hervé et tu proposes. SANS ID est la liste des noms qui attendent le glossaire : elle se présente, elle ne se règle pas seule.
- **Un glossaire en attente de pose** (`Glossaire_<Gamme>_NOUVEAU_AAAA-MM-JJ.xlsx`, règle « Poser un fichier produit » du skill `noyau`) : tu contrôles les fiches contre ce fichier-là, et tu ne ramènes jamais une fiche au glossaire qu'il va remplacer.
- **Si le programme ne voit pas le dossier** (tâche dans le cloud) : applique la règle du skill `noyau` ; s'il reste aveugle, tu compares toi-même les propriétés de chaque fiche au glossaire glissé dans la conversation, fiche par fiche, et tu le dis : « contrôle fait à la main, sans le programme ».
- **« La fiche de … est relue »** : tu passes `statut_fiche` à `relue` dans cette fiche, rien d'autre.
- La voix d'un personnage dans une fiche complète la carte de voix de la gamme (skill `narration-jeux`), elle ne la remplace pas : la carte de voix décrit l'univers, la fiche décrit un personnage.

## 4. Écrire pour Obsidian — quand `Core/Profile.md` dit qu'Hervé l'utilise
- Dans ce que tu écris dans `Core/` (notes de séance, journal, suivi, fiches de gamme), une gamme, un éditeur ou une fiche d'univers cités deviennent des liens : `[[Core/Gammes/<Gamme>|<Gamme>]]`, `[[Core/Editeurs/<Éditeur>|<Éditeur>]]`, `[[Références/Narration/Univers/<Gamme>/<nom du fichier>|<Nom français du glossaire>]]`. Le lien vise le **nom du fichier** (sans `.md`), pas `nom_en` : les deux diffèrent quand un signe a été retiré ou qu'un homonyme porte « (faction) ». Avant d'écrire un lien : le fichier existe, et pour une fiche, son `type` et son `id_glossaire` sont bien ceux de l'élément cité.
- **Dans une cellule de tableau** (Tasks, Suivi, Questions_Editeurs, tout tableau), la barre du lien s'échappe : `[[Core/Editeurs/<Éditeur>\|<Éditeur>]]`. Après l'écriture, relis la ligne : elle a toujours le même nombre de cellules que l'en-tête.
- Tu ne renommes ni ne déplaces aucun fichier pour Obsidian. Tu ne lis pas et tu n'écris pas dans `.obsidian/`.
- `ACCUEIL.md` et `TABLEAU.base` sont à Hervé : tu ne les réécris pas sans son accord. S'il dit qu'un tableau affiche une erreur, relis `TABLEAU.base` et compare-le à la graine ; propose la correction, et ne remplace le fichier qu'avec son accord (l'ancien est d'abord copié dans `Core/Archives/`).

## 5. Ses questions
Réponds à partir du guide (sections « Ce que tu vois », « Pour ton métier », « Les règles », « Si quelque chose cloche », « Ce qu'Obsidian ne fait pas »). Hors de ces sections, dis ce que tu sais et ce que tu ne sais pas : l'interface d'Obsidian change d'une version à l'autre, une capture d'écran tranche.

## Ce que tu ne fais pas
- Tu ne conseilles aucun module complémentaire (code tiers) ni service payant.
- Tu ne présentes pas Obsidian comme une sauvegarde : il ne copie rien ailleurs.
- Tu ne mets aucun terme, aucune décision ni aucun chiffre dans `ACCUEIL` ou `TABLEAU` : ils affichent, ils ne stockent pas.
