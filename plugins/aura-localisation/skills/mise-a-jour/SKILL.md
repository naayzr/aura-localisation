---
name: mise-a-jour
description: "AURA MISE À JOUR (aussi « AURA MISE A JOUR ») : met à jour la petite partie d'AURA qui vit dans le dossier HERVÉ WORLD (le fichier de démarrage CLAUDE.md, la version, la carte des outils, les guides) et crée les nouveaux fichiers de mémoire qui manquent, sans jamais modifier un fichier de mémoire existant. Fait aussi la migration depuis la version 2.0, en gardant ses outils sur mesure et sans deviner où en est sa mise en place. À utiliser quand Hervé tape « AURA MISE À JOUR », « mets AURA à jour », « installe la mise à jour », ou quand AURA START signale qu'une mise à jour est disponible. Répond aussi, sans rien écrire, à « quelle version d'AURA » ou « AURA est-elle à jour »."
---

# AURA MISE À JOUR

**Version de ce plugin : 3.0** (la même que dans `plugin.json` ; un contrôle de Dorian vérifie qu'elles concordent).

Les outils d'AURA viennent du plugin AURA installé sur le compte d'Hervé ; ses nouvelles versions y arrivent par la synchronisation du plugin (rythme et gestes : section « Si le plugin n'est pas à jour sur le compte », plus bas). Cette commande s'occupe du reste : la petite **couche système locale** du dossier HERVÉ WORLD. Elle est sûre par construction : les chemins qu'elle a le droit de toucher sont listés dans `references/couches.json`, ce qu'elle peut en faire est dit dans la règle d'or ci-dessous, et **tout le reste est la mémoire d'Hervé, qu'elle ne modifie jamais**. <!-- [I-17] -->

## Une simple question de version : tu réponds sans rien écrire <!-- [R-39] -->
Si Hervé demande seulement où en est AURA (« quelle version d'AURA ? », « AURA est-elle à jour ? ») sans demander la mise à jour, tu ne lances pas le déroulé. Tu lis `Core/VERSION.md` (absent : le dossier est en version 2.0) et la première ligne de `CLAUDE.md`, puis tu réponds : « Le plugin AURA installé sur ton compte est en version 3.0. Ton dossier est en version [X]. » Si les deux diffèrent, tu ajoutes : « Tape AURA MISE À JOUR pour mettre ton dossier au même niveau. » Si Hervé te dit que Dorian a annoncé une version plus récente que 3.0, tu lui donnes les gestes de la dernière section. Tu n'écris rien.

## La règle d'or — à relire avant chaque écriture
`references/couches.json` donne les chemins ; cette règle dit ce que tu as le droit d'en faire. Elle n'est écrite qu'ici.
- **Tu remplaces** seulement : l'amorce `CLAUDE.md`, les fichiers de `systeme_local`, et `Core/VERSION.md` quand la version change. Avant de remplacer `CLAUDE.md` ou `Core/Skills.md`, l'étape 4 dit s'il faut d'abord en garder une copie.
- **Tu crées, seulement s'ils n'existent pas** (vérifié juste avant) : les fichiers de `graines` ; les fichiers de `systeme_si_dossier_present`, et seulement si leur dossier existe déjà ; les copies de l'étape 4 dans `_archives-systeme/`. Un fichier qui existe, tu n'y touches pas, même s'il est vide.
- **Une seule exception** à « aucun fichier existant n'est modifié » : le document de démonstration de la version 2.0 nommé par `bandeau_fictif` reçoit une ligne d'avertissement **en tête**, une seule fois, et rien d'autre (étape 5).
- **Tout le reste, tu ne le modifies, ne le réécris, ne le déplaces et ne le supprimes jamais** : la couche mémoire (`Core/` sauf `Core/VERSION.md` et `Core/Skills.md`, puis `Glossaires/`, `Références/`, `Livrables/`, `IMPORT/`), les sous-dossiers de `skills/`, et tout autre fichier. Pas même pour y ajouter une ligne : la mise à jour ne laisse aucune trace dans la mémoire existante ; le prochain AURA SAVE la notera au Journal.
- Si quelque chose t'oblige à sortir de cette règle, tu t'arrêtes et tu expliques à Hervé ; tu ne contournes pas.
- **Tu tiens la liste de chaque fichier que tu remplaces, crées, copies ou complètes, au moment où tu le fais.** Le compte rendu la recopie en entier. <!-- [R-07] -->

## Déroulé

### 1. Annoncer et vérifier le dossier
Une phrase : « Je mets AURA à jour. Je ne touche à aucun de tes fichiers de mémoire : glossaires, journal, profil, tâches restent tels quels. »
Le dossier connecté doit contenir `CLAUDE.md` et `Core/CONTEXT.md`. Sinon : arrête-toi et demande à Hervé de connecter le dossier HERVÉ WORLD (celui qui contient directement CLAUDE.md, Core et Glossaires). Il faut aussi que Claude Desktop reste **ouvert** pendant la mise à jour : si la tâche tourne dans le cloud, c'est l'application qui transmet les fichiers.

### 2. Lire l'état
- `Core/VERSION.md` : absent → version installée « 2.0 ». Sinon, lis la ligne `version:`.
- Première ligne de `CLAUDE.md` : contient-elle `AURA-HERVE-VERSION: 3.0` ?
- Relève les **noms** des fichiers de la couche mémoire présents, sans les ouvrir en écriture. Ce relevé sert à l'étape 7 : c'est une liste de noms, pas une preuve que leur contenu n'a pas changé. <!-- [R-22] -->
- **Tu listes pour de bon** : chaque nom de fichier ou de dossier que tu cites ensuite (relevé, glossaires de l'étape 3 bis, sous-dossiers de `skills/` à l'étape 4, compte rendu, `Core/Suivi.md`) vient d'une liste réelle du dossier, faite avec ton outil de liste ou une commande `ls`. Jamais d'un exemple de ce skill (`Glossaire_TaintedGrail_EN-FR.xlsx`, `GLOSSAIRE_<GAMME>_v2.3.xlsx` sont des exemples), jamais d'un nom deviné puis essayé. Si tu ne peux pas lister un dossier, tu ne conclus rien sur son contenu : tu le dis au compte rendu et tu demandes à Hervé ce qu'il y voit.

**Déjà à jour** si : la version installée est 3.0, l'amorce porte `AURA-HERVE-VERSION: 3.0`, et tous les fichiers de `systeme_local` et de `graines` existent (ceux de `systeme_si_dossier_present` ne comptent pas : Hervé a le droit de supprimer le dossier `skills/`). <!-- [R-15] --> Alors tu réponds, sans rien écrire : <!-- [R-08] -->
« Ton dossier est déjà au niveau de la version d'AURA installée sur ton compte (3.0) : il est déjà à jour, et je n'ai rien modifié. Si Dorian t'a annoncé une version plus récente, ton compte ne l'a pas encore reçue : » suivi des gestes de la dernière section (« Si le plugin n'est pas à jour sur le compte »). Puis tu t'arrêtes.

Si la version est 3.0 et l'amorce porte la marque, mais qu'un fichier de `systeme_local` ou une graine manque : tu recrées **seulement ce fichier-là** et tu le dis (« J'ai recréé Core/Suivi.md, qui manquait »). Tu ne réécris ni `Core/VERSION.md` ni rien d'autre, et tu ne recrées pas `skills/`. <!-- [R-21] -->

### 3. L'état de la mise en place (seulement si `Core/ONBOARDING.md` n'existe pas) — sans deviner
Compare `Core/Profile.md` à son empreinte d'origine (section « Comparer à l'empreinte d'origine », juste après) et compte les sessions du Journal (`## Session …`).
- Profil **identique à l'origine** ET **une seule** session au Journal → la mise en place n'a pas commencé : `statut: non commencé`, `étape en cours: ACCUEIL`.
- Sinon, tu **ne devines pas** l'étape : un profil pré-rempli par Dorian ressemble à un profil commencé, et une mise en place finie ressemble à une mise en place en cours. Tu écris `statut: à confirmer` et `étape en cours: à confirmer avec Hervé`, puis en dessous `indices relevés le AAAA-MM-JJ : …` (profil modifié ou non, nombre de sessions, fiches éditeurs, glossaires). Au compte rendu, tu poses **une seule question** : « Ta mise en place est-elle terminée ? Sinon, à quelle étape t'es-tu arrêté ? », en lui rappelant les étapes de la version 2.0 qu'il a vues (`etapes_v2` dans `couches.json`). <!-- [R-04] --> <!-- [R-44] -->
- Sa réponse, dans cette conversation ou au START suivant, s'écrit dans `Core/ONBOARDING.md` : « terminée » → `statut: terminé` et `date de fin: à confirmer avec Hervé` ; une étape de la version 2.0 → `statut: en cours` et `étape en cours:` son identifiant de la version 3.0, donné par `correspondance_etapes_v2_v3`.
- `date de début:` « à confirmer avec Hervé » (la date du Journal de la version 2.0 est celle de la préparation, pas de l'installation).
Tu crées `Core/ONBOARDING.md` à partir de `references/graines/Core/ONBOARDING.md`, avec ces valeurs.

### Comparer à l'empreinte d'origine (étapes 3 et 4) <!-- [R-18] --> <!-- [R-23] -->
`empreintes_v2` (dans `couches.json`) décrit `CLAUDE.md`, `Core/Skills.md` et `Core/Profile.md` tels que Dorian les a livrés en version 2.0.
- **Si un programme voit ton dossier** (étape 0 de la règle des programmes, skill `noyau`) : compare la taille du fichier en octets à `octets` et son empreinte sha256 à `sha256`. C'est la seule comparaison exacte.
- **Sinon** (tâche dans le cloud) : compare le nombre de lignes à `lignes`, puis chaque ligne de `temoins` (numéro de ligne → texte exact attendu) à la ligne qui porte ce numéro dans le fichier.
- Le fichier est **identique à l'origine** seulement si tout correspond. Au moindre écart, ou si tu n'as pas pu lire une des lignes, il est **modifié**.
- Sans programme, une retouche qui garde le nombre de lignes et ne touche aucune ligne témoin ne se voit pas. C'est la limite connue de cette comparaison ; Dorian garde les originaux de la version 2.0.

### 3 bis. Ses glossaires de la version 2.0 <!-- [R-06] -->
Liste `Glossaires/`. Un classeur nommé à la manière de la version 2.0, `GLOSSAIRE_<GAMME>_v<N>.xlsx` (par exemple `GLOSSAIRE_<GAMME>_v2.3.xlsx`), est un **glossaire de la version 2.0** : tu n'y touches pas. Tu le notes pour le compte rendu (« ton glossaire X sera converti au nouveau format à ta prochaine séance, en gardant tes validations ») et, au moment de créer la graine `Core/Suivi.md`, tu y ajoutes une ligne par glossaire : « Glossaire v2.0 à convertir : X — attend Hervé — ouvert le AAAA-MM-JJ ». La conversion elle-même se fait avec lui, par le skill `glossaire` (migration d'un glossaire v2.0), jamais pendant la mise à jour.
Un autre fichier de `Glossaires/` (hors `LISEZ-MOI.md` et les fichiers temporaires d'Excel qui commencent par `~$`) qui ne porte pas le nom d'un glossaire de gamme, `Glossaire_<Gamme>.xlsx` avec un seul `_`, celui qui suit « Glossaire » : par exemple `Glossaire_TaintedGrail_EN-FR.xlsx`, le glossaire de la démonstration, posé là au lieu d'`IMPORT/`. Tant qu'il est dans `Glossaires/`, il passe pour un second glossaire de sa gamme (skill `glossaire` : un seul par gamme). Tu n'y touches pas, tu ne le classes pas et tu ne le déplaces pas : c'est Hervé qui choisit, et c'est lui qui le déplace. <!-- [R-25] -->
- Au compte rendu, pour chacun : « Je n'ai pas reconnu [nom] dans Glossaires/, qui ne garde qu'un glossaire par gamme. Si c'est un glossaire à importer (celui de la démonstration, un ancien Excel, celui d'un éditeur), déplace-le toi-même dans le dossier IMPORT, puis dis-moi “j'ai mis [nom] dans IMPORT”. Si c'est un glossaire que tu as fait avec AURA, dis-le-moi : on le convertira en gardant tes validations. » Tu recopies cette phrase telle quelle : le verbe « déplace » compte, parce qu'une copie laissée dans `Glossaires/` y resterait un second glossaire. Les deux suites sont celles du skill `glossaire` : l'import d'un glossaire existant, ou la migration d'un glossaire de la version 2.0.
- Au moment de créer la graine `Core/Suivi.md`, une ligne pour chacun : « Fichier de Glossaires/ non reconnu : [nom] — attend Hervé (à déplacer dans IMPORT, ou à convertir) — ouvert le AAAA-MM-JJ ».

### 4. Les anciens fichiers système — rien ne se perd <!-- [D-28] -->
La version 2.0 présentait deux fichiers comme évolutifs : l'amorce `CLAUDE.md` et la carte des outils `Core/Skills.md` (son AURA l'enrichissait à chaque outil créé pour lui). Avant de remplacer **chacun** :
- **Version 2.0 identique à l'origine** (comparaison ci-dessus) → pas de copie à faire (Dorian garde l'original) ; note-le pour `VERSION.md`.
- **Dans tous les autres cas** — fichier de la version 2.0 modifié, amorce d'une version 3.x (Claude peut retoucher seul les instructions d'un dossier, tu ne peux pas savoir s'il l'a fait), fichier que tu ne reconnais pas — **copie-le d'abord** tel quel dans `_archives-systeme/<nom>_v<version installée>_AAAA-MM-JJ.md` (`CLAUDE_v2.0_…`, `Skills_v2.0_…` ; crée le dossier ; si le nom existe déjà, ajoute l'heure).
  - Si un programme voit ton dossier, la copie se fait par programme, octet pour octet, et tu vérifies que son sha256 est celui de l'original.
  - Sinon, tu la réécris avec tes outils de fichiers, puis tu la relis sur les mêmes repères que l'original : même nombre de lignes, même première et même dernière ligne et, pour un fichier de la version 2.0, la même ligne que **l'original** à chaque numéro de `temoins`. Au moindre écart, tu t'arrêtes avant de remplacer quoi que ce soit, et tu le dis à Hervé.
- Pour `Core/Skills.md` enrichi : relis la copie et repère les outils qui n'appartiennent ni aux 7 outils de la v2.0 (`skills_v2`) ni aux capacités générales de Claude (Excel, Word, PDF, créateur de skills). Ce sont **ses outils sur mesure** : tu les écriras dans `Core/Outils_Perso.md` à l'étape 6 (nom, ce qu'il fait, « repris de Core/Skills.md v2.0 »).

Le dossier `skills/` du dossier : liste ses sous-dossiers. Ceux qui portent un nom de `skills_v2` sont l'ancienne version des outils. **Tout autre sous-dossier est un outil fait pour Hervé** : tu n'y touches pas, tu ne proposes pas de supprimer `skills/`, et tu l'inscris aussi dans `Core/Outils_Perso.md` à l'étape 6 (« dossier skills/<nom>, conservé tel quel »).

### 5. Écrire la couche système locale
1. `CLAUDE.md` ← contenu exact de `references/amorce-CLAUDE.md`.
2. Chaque fichier de `systeme_local` ← contenu exact du fichier du même chemin sous `references/systeme/`. Tu les écris **tous**, toujours : à l'étape 4, « identique à l'origine » décide seulement s'il faut d'abord une copie, jamais s'il faut écrire. Note chaque fichier dans ta liste au moment où tu l'écris. Chaque fichier de `systeme_si_dossier_present` ← de même, **seulement si son dossier existe déjà** : sans dossier `skills/`, tu ne le crées pas.
3. `Core/VERSION.md`, **seulement si la version change** (version installée différente de 3.0) ← le modèle ci-dessous. Si elle vaut déjà 3.0, tu ne le réécris pas : il garde la trace de la migration depuis la version 2.0.
```
version: 3.0
appliquée le: AAAA-MM-JJ
version précédente: [2.0 ou la version lue]
ancien fichier de démarrage: [v2.0 d'origine, conservée par Dorian | copiée dans _archives-systeme/…]
Ce fichier est écrit par AURA MISE À JOUR. Ne pas le modifier à la main.
```
4. Le document nommé par `bandeau_fictif` (s'il existe à la racine) : si sa première ligne contient déjà `EXEMPLE FICTIF`, tu n'y touches pas. Sinon, tu insères **avant** sa première ligne la ligne `> [EXEMPLE FICTIF — démonstration de la version 2.0 : aucun nom, contact ou chiffre de ce document n'est réel.]` suivie d'une ligne vide, avec un outil qui modifie seulement ce passage. Si ton seul moyen est de réécrire le document en entier, tu n'y touches pas (l'amorce le déclare déjà fictif) et tu le dis au compte rendu. <!-- [D-23] --> <!-- [D-39] --> <!-- [R-14] -->

### 6. Créer les graines manquantes
Pour chaque chemin de `graines` : s'il **n'existe pas**, crée-le avec le contenu du fichier correspondant sous `references/graines/` (crée les dossiers au besoin — c'est aussi ce qui recrée les dossiers vides perdus au téléchargement). S'il existe, **passe**. <!-- [D-25] -->
**Un nom accentué peut s'écrire de deux façons invisibles à l'œil** : le « é » de `Références` est soit un seul caractère, soit un « e » suivi d'un accent. Sous Windows, ce sont deux dossiers différents. Avant de créer une graine dans un dossier dont le nom porte un accent, liste le dossier qui le contient : s'il y a déjà un dossier qui s'affiche sous ce nom, c'est le sien ; tu écris dedans en reprenant son nom tel que la liste te le donne. Tu ne crées jamais un second dossier qui s'affiche pareil. <!-- [R-35] -->
Deux exceptions au contenu des graines, et seulement à leur création : `Core/Outils_Perso.md` reçoit en plus une ligne par outil sur mesure trouvé à l'étape 4 ; `Core/Suivi.md` reçoit une ligne par glossaire v2.0 et par fichier non reconnu trouvés à l'étape 3 bis. Si le fichier existe déjà, tu n'y touches pas et tu cites ces éléments dans le compte rendu.

### 7. Vérifier — avant de dire que c'est fait
- Relis la première ligne de `CLAUDE.md` : `AURA-HERVE-VERSION: 3.0`.
- Relis `Core/VERSION.md` : `version: 3.0`.
- Chaque fichier de `systeme_local` existe **et porte le contenu de `references/systeme/`** : relis-le et compare sa première ligne, sa dernière ligne et son nombre de lignes à ceux du fichier de référence (`Core/Skills.md` commence par « # Les outils d'AURA »). Un fichier resté dans sa version 2.0 n'a pas été écrit : tu l'écris, puis tu le relis.
- Chaque fichier de `graines` existe.
- **Aucun nom en double** : à la racine et dans chaque dossier où tu as créé quelque chose, aucun dossier ne s'affiche deux fois sous le même nom. Si c'est le cas, tu t'arrêtes, tu ne supprimes rien, et tu demandes à Hervé de prévenir Dorian.
- Les fichiers de mémoire relevés à l'étape 2 sont tous encore là, sous le même nom ; les seuls noms nouveaux sont les graines que tu viens de créer (compare en les mettant à part).
Si une vérification échoue, tu le dis tel quel, sans conclure « c'est fait ».

### 8. Le compte rendu à Hervé
```
AURA est à jour : version [ancienne] → 3.0.
Remplacé : [chaque fichier de la couche système réellement écrit à l'étape 5 et relu à l'étape 7, d'après ta liste : le fichier de démarrage CLAUDE.md, Core/Skills.md, GUIDE_AURA.md, GUIDE_OBSIDIAN.md, Core/VERSION.md, et skills/_ANCIENNE_VERSION_LIRE_MOI.md s'il a été écrit]
Créé : [chaque nouveau fichier de mémoire, avec ce qu'il contient déjà : Core/ONBOARDING.md (l'état de ta mise en place), Core/Suivi.md (les fils ouverts à l'étape 3 bis), Core/Outils_Perso.md (n outils repris)… ; les autres sont vides, prêts à servir]
Ajouté : [la ligne d'avertissement en tête de Simulation_Onboarding_Herve.md — ou « rien »]
Conservé : [les copies faites dans _archives-systeme/ ; les outils sur mesure repris dans Core/Outils_Perso.md — ou « rien à conserver »]
Ta mémoire : [N] fichiers, tous encore là sous le même nom ; je n'en ai ouvert aucun pour y écrire (je ne peux pas te le prouver octet par octet).
Ce qui change pour toi : [3 lignes tirées du guide, section « Ce qui a changé »]
```
Puis, une seule fois chacune, les suites utiles :
1. **La ligne dans tes réglages**, pour qu'AURA soit toujours chargée, même dans une nouvelle conversation. Si la phrase de la clé `ligne_instructions` de `references/couches.json` figure déjà dans les instructions que tu as reçues au début de cette tâche, tu dis seulement : « La ligne de tes réglages est bien en place. » Sinon : Réglages > Général > Instructions pour Claude, coller cette phrase (recopie-la exactement, entre guillemets). <!-- [D-05] --> <!-- [R-16] -->
2. **Le dossier `skills/`** : si l'étape 4 n'y a trouvé que les 7 outils de la version 2.0, dis qu'AURA ne le lit plus et qu'il peut le supprimer quand il veut : la mise à jour suivante ne le recréera pas. S'il contient un outil fait pour lui, ne propose **pas** de le supprimer.
3. Si la mise en place est `à confirmer` : la question unique de l'étape 3 (« Ta mise en place est-elle terminée ? Sinon, à quelle étape t'es-tu arrêté ? »), avec la liste des étapes de la version 2.0.
4. S'il a des glossaires v2.0 : « Ton glossaire [nom] sera converti au nouveau format à ta prochaine séance, sans perdre tes validations. » Et, pour chaque fichier de `Glossaires/` que tu n'as pas reconnu, la phrase de l'étape 3 bis.

## Les mises à jour suivantes
Quand Dorian publie une nouvelle version, elle arrive sur le compte par la synchronisation du plugin (section suivante) ; si la couche locale doit changer, ce skill porte la nouvelle version et AURA START propose « tape AURA MISE À JOUR ». Les fichiers de mémoire ne sont jamais concernés.

## Si le plugin n'est pas à jour sur le compte <!-- [R-08] --> <!-- [R-09] -->
Le plugin AURA se synchronise au début d'une conversation, à un rythme que l'application ne précise pas. Tu ne peux pas savoir si une version plus récente que la tienne (3.0) a été publiée, et tu ne peux pas cliquer à la place d'Hervé. Si Dorian lui a annoncé une version plus récente, tu lui donnes ces gestes, recopiés tels quels (les menus portent les noms anglais de l'aide d'Anthropic ; la source est le dépôt de Dorian, qui s'affiche sous le nom `aura-dorian`) :
« Dans Claude Desktop, ouvre Customize (« Personnaliser » si ton application est en français), puis Plugins. À la source aura-dorian, celle qui porte le plugin AURA, clique sur Check for updates. Si tu arrives sur un écran « Extensions » sans ce bouton, ce n'est pas le bon : reviens à Customize. Ensuite, ferme cette conversation, ouvre une nouvelle conversation avec ton dossier HERVÉ WORLD, et tape de nouveau AURA MISE À JOUR. »
Si Hervé a installé le plugin depuis un fichier zip, il n'a pas de source à interroger et ne se met pas à jour seul. Dis-lui de demander à Dorian soit le nouveau fichier, soit l'adresse de la source avec les gestes pour l'ajouter (ce sont ceux du message d'installation de Dorian) : une source ajoutée avec Sync automatically se met ensuite à jour seule.
