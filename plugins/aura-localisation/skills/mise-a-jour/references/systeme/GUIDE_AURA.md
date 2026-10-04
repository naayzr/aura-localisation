# Guide AURA — version 3.0

<!-- [D-16] --> <!-- [D-38] --> <!-- [D-41] --> <!-- [R-09] --> <!-- [R-13] --> <!-- [R-17] --> <!-- [R-45] --> <!-- [R-25] -->

AURA est ton assistante. Elle connaît ton métier, retient ce que tu lui apprends d'une séance à l'autre, et fait le travail mécanique pour que tu te concentres sur la traduction. Elle propose, tu décides.

## Les commandes

| Ce que tu veux | Ce que tu tapes |
|---|---|
| Commencer une séance | `AURA START` |
| Commencer sur un sujet précis | `AURA START — [sujet]` |
| Sauvegarder et fermer | `AURA SAVE` |
| Vérifier que tout marche | `AURA DIAGNOSTIC` |
| Installer une nouveauté annoncée par Dorian | `AURA MISE À JOUR` (sans accent, `AURA MISE A JOUR` marche aussi) |
| Noter une mission, une action, une idée | `nouvelle mission : …` · `rappelle-moi de …` · `nouvelle idée : …` |
| Clore une tâche, voir tes tâches | `j'ai terminé …` · `montre mes tâches` |
| Signaler une erreur | `correction : …` · `hallucination : [le terme inventé]` |
| Lui donner un fichier | Copie-le dans le dossier `IMPORT`, puis dis : `j'ai mis [nom] dans IMPORT` |

Pour tout le reste, parle-lui normalement.

## Ce qui a changé avec la version 3.0
- **Elle ne perd plus le fil de ta mise en place** : si tu t'arrêtes au milieu, elle reprend à l'étape où vous en étiez.
- **Elle sauvegarde seule** pendant les longues séances, et note au fil de l'eau ce qui compte (termes validés, échéances, corrections). Fais quand même `AURA SAVE` en fin de séance.
- **Ses outils arrivent par le plugin AURA**, installé sur ton compte Claude : ce que Dorian publie y arrive par la synchronisation automatique, au début d'une nouvelle conversation, à un rythme que l'application ne précise pas. Quand Dorian t'annonce une nouveauté, tape `AURA MISE À JOUR` ; si elle n'apparaît pas, tape `AURA DIAGNOSTIC`.
- **Nouveaux outils pour ton métier** : contrôle de la typographie française, comptage exact des caractères pour tes devis et factures, contrôle de la longueur des textes de cartes et des balises, genre des noms inventés dans le glossaire, gestion d'une gamme (calendrier à rebours, BAT (bon à tirer), errata, nouvelles versions du texte source, coordination des traducteurs et relecteurs), et **maquettes** : une planche de toutes tes cartes en français pour voir d'un coup celles qui débordent, la préparation d'une fusion pour InDesign ou Affinity, des présentations pour tes éditeurs.
- **Obsidian, si tu veux** : un logiciel gratuit pour lire ton dossier comme un carnet relié — page d'accueil, tableaux, fiches des personnages et des lieux de tes jeux. Le guide pas à pas est `GUIDE_OBSIDIAN.md`, dans ton dossier.
- **Tes glossaires de la version 2.0 sont convertis au nouveau format avec toi**, en gardant tes validations : rien n'est revalidé à zéro.
- **La relecture avant livraison est légère par défaut** ; la relecture « à plusieurs relecteurs » se fait seulement si tu la demandes, parce qu'elle consomme beaucoup ton abonnement.

## Quand AURA te demande de glisser un fichier
Selon la façon dont la conversation tourne, les petits programmes d'AURA (comptage, typographie, glossaire…) ne voient pas toujours ton dossier. Elle te dira alors : « Glisse [le fichier] dans cette conversation » — tu le fais glisser depuis ton dossier vers la fenêtre de la conversation. Et quand elle produit un nouveau fichier (un glossaire mis à jour, par exemple), elle te donne **les deux gestes exacts** pour le ranger : d'abord mettre l'ancien de côté dans `Core\Archives`, ensuite poser le nouveau à sa place. Tant que ce n'est pas fait et vérifié, elle garde ses décisions par écrit : rien ne se perd.

**Laisse Claude Desktop ouvert pendant que tu travailles avec AURA** : c'est l'application qui lui ouvre ton dossier.

## Deux limites à connaître
- **Une conversation = un sujet.** Quand un sujet est fini : `AURA SAVE`, puis une nouvelle conversation. AURA relit ses fichiers et reprend exactement où vous en étiez.
- **Ton abonnement a un quota** (sur 5 heures et sur la semaine). Les gros fichiers et les relectures à plusieurs relecteurs le consomment vite. Si tu l'atteins, il faut attendre que l'application te dise quand il revient. Le plugin AURA est rattaché à ton compte : la courte présentation de ses outils est lue au début de chacune de tes conversations avec Claude, même hors de HERVÉ WORLD. C'est peu, mais cela compte aussi.

## Ce qu'AURA ne fait pas
- Elle n'envoie pas d'e-mail : elle rédige, tu envoies.
- Elle ne modifie jamais tes fichiers d'origine : elle travaille sur des copies, dans `Livrables`.
- Elle n'achète rien et ne s'abonne à rien.
- Elle n'invente pas de terme : si un terme n'a pas de source, elle te le dit.

## Si quelque chose cloche
Tape `AURA DIAGNOSTIC`. Elle te dit en une ligne ce qui ne va pas et quoi faire. Si ça résiste, fais une capture d'écran et envoie-la à Dorian.

Les anciens documents (`Guide_Herve`, `Guide_Onboarding`, `Simulation_Onboarding_Herve`) datent de la version 2.0 ; ce guide les remplace. La « simulation » était un exemple fictif. Le `README.md` du dossier `IMPORT` date aussi de la version 2.0 : ce qu'il dit du rangement et de la suppression de tes fichiers ne vaut plus ; pour donner un fichier à AURA, suis la ligne « Lui donner un fichier » du tableau des commandes.
