# AURA — extension « aura-localisation »

Extension Cowork (Claude Desktop) qui porte le fonctionnement d'AURA, une assistante pour la traduction et la localisation de jeux de société de l'anglais vers le français : mémoire de travail tenue dans le dossier de l'utilisateur, glossaires par gamme, typographie française, comptage de caractères, longueurs et balises des cartes, relecture, relations éditeurs, gestion de gamme.

L'extension ne contient aucune donnée personnelle : la mémoire de l'utilisateur reste dans son propre dossier, que l'extension lit et complète sans jamais la remplacer.

## Installation (une fois, environ 5 minutes)
<!-- ETAPES:DEBUT (produit par construire_textes.py) -->
1. Ouvre Claude Desktop. S'il te propose une mise à jour de l'application, accepte-la : l'extension a besoin de la dernière version.
2. Dans les réglages, section Capacités (« Capabilities »), vérifie que l'exécution de code (« Code execution ») est activée.
3. Va dans Personnaliser (« Customize ») > Extensions (« Plugins ») > Ajouter (« Add ») > Ajouter une marketplace (« Add marketplace »), colle cette adresse : https://github.com/naayzr/aura-localisation, puis installe « aura-localisation » et active la synchronisation automatique (« Sync automatically »).
4. Dans les réglages, section Général, case « Instructions pour Claude » (« Instructions for Claude »), colle cette phrase : « Quand je travaille dans mon dossier HERVÉ WORLD, commence toujours par lire le fichier CLAUDE.md de ce dossier et applique-le. »
5. Ferme la conversation que tu avais ouverte. Ouvre une NOUVELLE tâche Cowork avec ton dossier HERVÉ WORLD (l'extension ne se charge qu'au démarrage d'une tâche), laisse Claude Desktop ouvert pendant tout le travail, et tape : AURA MISE À JOUR. Sa première réponse doit dire qu'elle met AURA à jour sans toucher à tes fichiers de mémoire. Si elle ne le dit pas, tape plutôt /aura-localisation:mettre-a-jour ; si rien ne marche, appelle-moi.
<!-- ETAPES:FIN -->

Les versions suivantes arrivent seules grâce à la synchronisation automatique.

## Contenu
- `.claude-plugin/marketplace.json` — la marketplace
- `plugins/aura-localisation/` — l'extension : 15 skills, 4 commandes, journal des versions
