# AURA — plugin « aura-localisation »

Plugin Cowork (Claude Desktop) qui porte le fonctionnement d'AURA, une assistante pour la traduction et la localisation de jeux de société de l'anglais vers le français : mémoire de travail tenue dans le dossier de l'utilisateur, glossaires par gamme, typographie française, comptage de caractères, longueurs et balises des cartes, relecture, relations éditeurs, gestion de gamme.

Le plugin ne contient aucune donnée personnelle : la mémoire de l'utilisateur reste dans son propre dossier, que le plugin lit et complète sans jamais la remplacer.

## Installation (une fois, environ 5 minutes)
<!-- ETAPES:DEBUT (produit par construire_textes.py) -->
1. Ouvre Claude Desktop. S'il te propose une mise à jour de l'application, accepte-la : le plugin AURA a besoin de la dernière version. Les menus sont nommés ici en anglais, comme dans l'aide d'Anthropic ; si ton application est en français, ils peuvent apparaître traduits.
2. Ouvre les réglages : en bas à gauche, clique sur ton nom ou tes initiales, puis sur Settings (« Réglages »). Dans la section Capabilities (« Capacités »), vérifie que Code execution (l'exécution de code) est activée.
3. Ouvre Customize (« Personnaliser »), puis Plugins, puis Add, puis Add marketplace. Une « marketplace » est simplement une source d'outils. Colle cette adresse : https://github.com/naayzr/aura-localisation ; la source s'affichera sous le nom aura-dorian. Installe le plugin « aura-localisation » qu'elle propose, puis active Sync automatically (la synchronisation automatique). Si tu arrives sur un écran « Extensions » sans bouton Add marketplace, ce n'est pas le bon : reviens à Customize.
4. Dans les réglages, section General (« Général »), case Instructions for Claude (« Instructions pour Claude »), colle cette phrase : « Quand je travaille dans mon dossier HERVÉ WORLD, commence toujours par lire le fichier CLAUDE.md de ce dossier et applique-le. »
5. Si une conversation est déjà ouverte, ferme-la. Ouvre une NOUVELLE conversation de travail dans Cowork (l'application l'appelle une « tâche ») : le plugin ne se charge qu'au début d'une conversation. Donne-lui ton dossier avec le bouton qui permet de choisir un dossier : prends HERVÉ WORLD, celui qui contient directement CLAUDE.md, Core et Glossaires (après un téléchargement depuis Drive, il peut être rangé dans un dossier HERVÉ WORLD-2026… : prends celui de dedans). Laisse Claude Desktop ouvert pendant tout le travail, et tape : AURA MISE À JOUR (tu peux aussi l'écrire sans accent : AURA MISE A JOUR). Si l'application te demande d'autoriser l'accès à ton dossier, accepte : AURA n'écrit que dans HERVÉ WORLD. Sa première réponse doit dire qu'elle met AURA à jour sans toucher à tes fichiers de mémoire. Si elle ne le dit pas, tape plutôt /aura-localisation:mettre-a-jour ; si rien ne marche, appelle-moi.
<!-- ETAPES:FIN -->

Les versions suivantes arrivent par la synchronisation automatique de la marketplace, au début d'une nouvelle conversation (l'application n'en précise pas le rythme).

## Contenu
- `.claude-plugin/marketplace.json` — la marketplace
- `plugins/aura-localisation/` — le plugin : 15 skills, 4 commandes, journal des versions
