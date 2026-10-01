---
name: mise-a-jour
description: "AURA MISE À JOUR : met à jour la petite partie d'AURA qui vit dans le dossier HERVÉ WORLD (l'amorce CLAUDE.md, la version, le guide) et crée les nouveaux fichiers de mémoire qui manquent, sans jamais modifier un fichier de mémoire existant. Fait aussi la migration depuis la version 2.0, en gardant l'avancement de la mise en place. À utiliser quand Hervé tape « AURA MISE À JOUR », « mets AURA à jour », « installe la mise à jour », « quelle version d'AURA », ou quand AURA START signale qu'une mise à jour est disponible."
---

# AURA MISE À JOUR

**Version de cette extension : 3.0** (la même que dans `plugin.json` ; un contrôle de Dorian vérifie qu'elles concordent).

Les outils d'AURA (cette extension) se mettent à jour tout seuls sur le compte d'Hervé. Cette commande s'occupe du reste : la petite **couche système locale** du dossier HERVÉ WORLD. Elle est sûre par construction : la liste exacte de ce qu'elle a le droit d'écrire est dans `references/couches.json`, et **tout le reste est la mémoire d'Hervé, qu'elle ne modifie jamais**. <!-- [I-17] -->

## La règle d'or — à relire avant chaque écriture
- Tu écris **seulement** : l'amorce `CLAUDE.md`, `Core/VERSION.md`, et les fichiers listés dans `systeme_local` de `references/couches.json`.
- Tu **crées** les fichiers listés dans `graines` **seulement s'ils n'existent pas**. Tu vérifies leur existence juste avant de créer. S'il existe, tu n'y touches pas, même s'il est vide.
- Tu ne modifies, ne réécris, ne déplaces et ne supprimes **aucun fichier existant** de la couche mémoire : `Core/` (sauf `Core/VERSION.md` et `Core/Skills.md`), `Glossaires/`, `Références/`, `Livrables/`, `IMPORT/`. Pas même pour y ajouter une ligne : la mise à jour ne laisse aucune trace dans la mémoire ; le prochain AURA SAVE la notera au Journal.
- Si quelque chose t'oblige à sortir de cette règle, tu t'arrêtes et tu expliques à Hervé ; tu ne contournes pas.

## Déroulé

### 1. Annoncer et vérifier le dossier
Une phrase : « Je mets AURA à jour. Je ne touche à aucun de tes fichiers de mémoire : glossaires, journal, profil, tâches restent tels quels. »
Le dossier connecté doit contenir `CLAUDE.md` et `Core/CONTEXT.md`. Sinon : arrête-toi et demande à Hervé de connecter le dossier HERVÉ WORLD (celui qui contient directement CLAUDE.md, Core et Glossaires). Il faut aussi que Claude Desktop reste **ouvert** pendant la mise à jour : si la tâche tourne dans le cloud, c'est l'application qui transmet les fichiers.

### 2. Lire l'état
- `Core/VERSION.md` : absent → version installée « 2.0 ». Sinon, lis la ligne `version:`.
- Première ligne de `CLAUDE.md` : contient-elle `AURA-HERVE-VERSION: 3.0` ?
- Liste (sans les ouvrir en écriture) les fichiers présents de la couche mémoire : tu t'en serviras pour prouver, à la fin, qu'aucun n'a été modifié.

**Déjà à jour** si : version installée = 3.0, l'amorce porte `AURA-HERVE-VERSION: 3.0`, et tous les fichiers de `systeme_local` et de `graines` existent. Alors tu réponds : « AURA est déjà à jour (version 3.0). Rien n'a été modifié. » — et tu t'arrêtes, sans rien écrire.
Si la version est déjà 3.0 mais qu'un fichier de `systeme_local` ou une graine manque, tu recrées **seulement ce fichier-là** et tu le dis (« J'ai recréé Core/Suivi.md, qui manquait ») ; tu ne réécris rien d'autre.

### 3. L'état de la mise en place (seulement si `Core/ONBOARDING.md` n'existe pas)
Déduis où en est Hervé, sans rien modifier :
- `Core/Profile.md` encore rempli de « — » partout, aucune fiche dans `Core/Editeurs/` (hors README), `Glossaires/` vide, et une seule session au Journal → `statut: non commencé`, `étape en cours: ACCUEIL`.
- Sinon (profil commencé, fiches, glossaires, plusieurs sessions) → `statut: à confirmer`, et `étape en cours:` l'étape qui suit la dernière visiblement faite (profil rempli → BASE ; glossaire importé → OUTILS ; etc.). Ajoute une ligne `déduit par la mise à jour le AAAA-MM-JJ à partir de : [indices]`.
- `date de début:` « à confirmer avec Hervé » (la date du Journal de la version 2.0 est celle de la préparation, pas de l'installation).
Tu crées `Core/ONBOARDING.md` à partir de `references/graines/Core/ONBOARDING.md`, avec ces valeurs.

### 4. Les anciens fichiers système — rien ne se perd <!-- [D-28] -->
La version 2.0 présentait deux fichiers comme évolutifs : l'amorce `CLAUDE.md` et la carte des outils `Core/Skills.md` (son AURA l'enrichissait à chaque outil créé pour lui). Avant de les remplacer, compare **chacun** à son empreinte d'origine (`empreintes_v2` dans `couches.json` : nombre de lignes, première ligne, début de la dernière ligne).
- Identique à l'origine → pas de copie à faire (Dorian garde l'original) ; note-le pour `VERSION.md`.
- Différent (il a été enrichi ou modifié) → **avant de le remplacer**, copie-le tel quel dans `_archives-systeme/<nom>_v2.0_AAAA-MM-JJ.md` (`CLAUDE_v2.0_…`, `Skills_v2.0_…` ; crée le dossier ; si le nom existe déjà, ajoute l'heure). Relis la copie : même nombre de lignes que l'original, sinon arrête-toi.
- Pour `Core/Skills.md` enrichi : relis la copie et repère les outils qui n'appartiennent ni aux 7 outils de la v2.0 (`skills_v2`) ni aux capacités générales de Claude (Excel, Word, PDF, créateur de skills). Ce sont **ses outils sur mesure** : tu les écriras dans `Core/Outils_Perso.md` à l'étape 6 (nom, ce qu'il fait, « repris de Core/Skills.md v2.0 »).

Le dossier `skills/` du dossier : liste ses sous-dossiers. Ceux qui portent un nom de `skills_v2` sont l'ancienne version des outils. **Tout autre sous-dossier est un outil fait pour Hervé** : tu n'y touches pas, tu ne proposes pas de supprimer `skills/`, et tu l'inscris aussi dans `Core/Outils_Perso.md` à l'étape 6 (« dossier skills/<nom>, conservé tel quel »).

### 5. Écrire la couche système locale
1. `CLAUDE.md` ← contenu exact de `references/amorce-CLAUDE.md`.
2. Chaque fichier de `systeme_local` ← contenu exact du fichier du même chemin sous `references/systeme/`.
3. `Core/VERSION.md` ←
```
version: 3.0
appliquée le: AAAA-MM-JJ
version précédente: [2.0 ou la version lue]
ancienne amorce: [v2.0 d'origine, conservée par Dorian | copiée dans _archives-systeme/…]
Ce fichier est écrit par AURA MISE À JOUR. Ne pas le modifier à la main.
```
4. Le document `Simulation_Onboarding_Herve.md` (s'il existe à la racine) : remplace seulement sa **première ligne** par elle-même précédée de la ligne `> [EXEMPLE FICTIF — démonstration de la version 2.0 : aucun nom, contact ou chiffre de ce document n'est réel.]` et d'une ligne vide. Tu ne réécris pas le reste. <!-- [D-23] --> <!-- [D-39] -->

### 6. Créer les graines manquantes
Pour chaque chemin de `graines` : s'il **n'existe pas**, crée-le avec le contenu du fichier correspondant sous `references/graines/` (crée les dossiers au besoin — c'est aussi ce qui recrée les dossiers vides perdus au téléchargement). S'il existe, **passe**. <!-- [D-25] -->
Seule exception au contenu de la graine : `Core/Outils_Perso.md`, s'il n'existe pas, reçoit en plus une ligne par outil sur mesure trouvé à l'étape 4. S'il existe déjà, tu n'y touches pas et tu cites ces outils dans le compte rendu.

### 7. Vérifier — avant de dire que c'est fait
- Relis la première ligne de `CLAUDE.md` : `AURA-HERVE-VERSION: 3.0`.
- Relis `Core/VERSION.md` : `version: 3.0`.
- Chaque fichier de `systeme_local` et de `graines` existe.
- La liste des fichiers mémoire présents est la même qu'à l'étape 2, et tu n'as écrit dans aucun d'eux (seulement créé des graines absentes).
Si une vérification échoue, tu le dis tel quel, sans conclure « c'est fait ».

### 8. Le compte rendu à Hervé
```
AURA est à jour : version [ancienne] → 3.0.
Écrit : l'amorce CLAUDE.md, Core/VERSION.md, la carte des outils Core/Skills.md, le guide GUIDE_AURA.md, [n] nouveaux fichiers de mémoire vides.
Conservé : [anciens fichiers enrichis copiés dans _archives-systeme/ ; outils sur mesure repris dans Core/Outils_Perso.md — ou « rien à conserver »]
Ta mémoire : [N] fichiers vérifiés, aucun modifié.
Ce qui change pour toi : [3 lignes tirées du guide, section « Ce qui a changé »]
```
Puis, une seule fois chacune, les trois suites utiles :
1. **Une ligne à ajouter dans tes réglages**, pour qu'AURA soit toujours chargée, même dans une nouvelle tâche : Réglages > Général > Instructions pour Claude, coller la phrase donnée par la clé `ligne_instructions` de `references/couches.json` (recopie-la exactement, entre guillemets). <!-- [D-05] -->
2. **Le dossier `skills/`** : si l'étape 4 n'y a trouvé que les 7 outils de la version 2.0, dis qu'AURA ne le lit plus et qu'il peut le supprimer quand il veut. S'il contient un outil fait pour lui, ne propose **pas** de le supprimer.
3. Si la mise en place est `à confirmer` : « On s'était arrêtés vers l'étape [N] — on reprend là ? »

## Les mises à jour suivantes
Quand Dorian publie une nouvelle version, l'extension arrive seule sur le compte ; si la couche locale doit changer, ce skill porte la nouvelle version et AURA START propose « tape AURA MISE À JOUR ». Les fichiers de mémoire ne sont jamais concernés.

## Si l'extension n'est pas à jour sur le compte
Si Hervé a installé l'extension depuis un fichier zip (sans la synchronisation automatique), elle ne se met pas à jour seule : dis-lui de demander à Dorian le nouveau fichier, ou d'ajouter la source de l'extension avec la synchronisation automatique (Personnaliser > Extensions — « Plugins » dans l'application).
