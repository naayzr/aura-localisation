# Obsidian avec AURA — ton guide

## En deux mots
Obsidian est un logiciel **gratuit** qui affiche ton dossier HERVÉ WORLD de façon agréable : chaque fichier devient une page lisible, avec des liens cliquables, des tableaux et une recherche dans tout le dossier.

Il ne remplace pas Claude. AURA continue de travailler dans Claude, exactement comme avant. Obsidian est **une fenêtre de plus sur les mêmes fichiers** : ce qu'AURA écrit, tu le vois dans Obsidian ; rien n'est copié ailleurs, rien ne part sur Internet.

Il n'est **pas obligatoire**. Installe-le quand tu as un moment, de préférence après ta première séance avec AURA.

Ce guide est remis à jour par AURA à chaque nouvelle version : n'y écris pas tes notes, elles seraient remplacées.

## Ce que ça t'apporte, et ce que ça apporte à AURA
- **Tu vois ce qu'AURA retient.** Son état du travail, tes tâches, ce qui attend une réponse, le journal des séances : tout se lit en un clic. Si quelque chose est faux, tu le repères tout de suite et tu le lui dis (`correction : …`). Une mémoire que tu relis est une mémoire plus juste.
- **Une page d'accueil** qui rassemble tes gammes, tes éditeurs, tes dernières séances et les fiches d'univers de tes jeux.
- **La bible de l'univers d'un jeu.** Pendant qu'AURA traduit les textes d'ambiance, elle peut tenir une fiche par personnage, lieu, faction ou objet : son nom anglais, son nom français pris dans ton glossaire, sa façon de parler, où il apparaît. Dans Obsidian, tu les vois toutes dans un tableau, et les personnages en vignettes.
- **Tout retrouver** : une décision d'éditeur, un mot dans une séance passée, une question en attente.
- **Préparer une séance** : tu écris tes consignes dans une note du dossier `IMPORT`, puis tu dis à AURA « j'ai mis [nom de la note] dans IMPORT ».
- **Pour AURA, rien ne change** : mêmes fichiers, aucun compte, aucune connexion. Les liens qu'elle écrit vers une gamme, un éditeur ou une fiche deviennent cliquables chez toi.

## Installer Obsidian (10 minutes)
1. Dans ton navigateur, va sur **obsidian.md/fr/download**.
2. Clique sur **« Télécharger pour Windows »**. Un fichier d'un peu plus de 300 Mo arrive dans ton dossier Téléchargements ; son nom commence par `Obsidian-1.` (Windows n'affiche pas toujours la fin `.exe`).
3. Double-clique sur ce fichier.
   - Si Windows affiche « Windows a protégé votre ordinateur » : clique sur « Informations complémentaires », puis **vérifie que l'éditeur indiqué est Dynalist Inc.**, la société qui fait Obsidian. Si c'est bien Dynalist Inc., clique sur « Exécuter quand même ». Sinon, ne lance pas le fichier, supprime-le et préviens Dorian. (Les mots exacts peuvent varier un peu selon ta version de Windows.)
   - S'il te demande d'installer pour toi seul ou pour tous les utilisateurs, choisis **toi seul** : c'est le plus simple.
4. À la fin de l'installation, Obsidian s'ouvre (sinon, lance-le depuis le menu Démarrer, comme tout autre programme).

Obsidian se met à jour tout seul : quand une mise à jour est prête, elle s'installe au redémarrage suivant. Si un jour il affiche « … Obsidian nécessite une mise à jour majeure de son installateur. Vous devez télécharger et réinstaller Obsidian manuellement. », refais les étapes 1 à 3, sans rien désinstaller : ton dossier et tes réglages restent.

## Ouvrir ton dossier HERVÉ WORLD
1. Au premier lancement, Obsidian affiche un écran d'accueil. En bas, la langue doit être **Français** ; sinon, choisis-la dans la liste.
2. À droite de **« Ouvrir un dossier comme coffre »**, clique sur **« Ouvrir »**. (« Coffre », c'est le mot d'Obsidian pour « dossier ouvert dans Obsidian ». Le même écran parle de fichiers « Markdown » : c'est le format des fichiers texte d'AURA, ceux qui finissent par `.md`. Ton dossier en est plein.)
3. Dans la fenêtre de Windows, va jusqu'à ton dossier **HERVÉ WORLD** — celui que tu utilises avec Claude, normalement dans Documents —, clique une fois dessus, puis sur « Sélectionner un dossier ».
4. Ton dossier s'affiche : à gauche, la liste `Core`, `Glossaires`, `IMPORT`, `Livrables`, `Références`…
   - Si tu vois à la place un seul dossier `HERVÉ WORLD`, tu as choisi le dossier qui le contient : ferme Obsidian, rouvre-le, et choisis le `HERVÉ WORLD` qui est à l'intérieur.
   - Si Obsidian te demande « Faites-vous confiance à l'auteur de ce coffre ? », clique sur **« Parcourir le coffre en mode restreint »**. (Ton dossier ne contient aucun module : cette question ne devrait pas apparaître.)

Obsidian rouvre ensuite ce dossier tout seul à chaque lancement. Un dossier `.obsidian` apparaît dans HERVÉ WORLD : ce sont les réglages d'Obsidian, laisse-le.

**Si ton dossier est dans OneDrive** (dans l'Explorateur de fichiers, son chemin contient le mot « OneDrive ») : fais un clic droit sur le dossier HERVÉ WORLD et choisis « Toujours conserver sur cet appareil ». Sinon, OneDrive peut laisser certains fichiers « en ligne seulement », et Obsidian comme AURA risquent de ne pas voir la dernière version. C'est une précaution recommandée par Obsidian lui-même. `AURA DIAGNOSTIC` te dira ensuite si tout est en ordre.

## Trois réglages (5 minutes)
Les **Paramètres** s'ouvrent avec la roue dentée, en bas à gauche de la fenêtre. Leur colonne de gauche a deux parties : les options en haut, puis, sous le titre gris « Modules principaux », un réglage par module.

1. **Lire sans risque.** Dans **« Éditeur »**, réglage **« Mode par défaut pour les nouveaux onglets »** (un onglet = une page ouverte, comme dans ton navigateur) : choisis **« Mode lecture »**.
   Le texte de tes pages s'ouvre en lecture : tu ne le modifies pas par erreur. Pour écrire dans une page, appuie sur **Ctrl+E** ; appuie de nouveau sur Ctrl+E pour revenir en lecture. Trois choses restent cliquables même en lecture : les cases à cocher (dans `Core/_EN_COURS`, ne coche rien : c'est AURA qui coche ses vérifications), les propriétés en haut d'une fiche, et les cases et boutons des tableaux. N'y touche pas : pour changer quelque chose, demande-le à AURA.
2. **Voir tes glossaires et tes documents.** Dans **« Fichiers & Liens »**, active **« Détecter toutes les extensions de fichiers »**.
   Tes fichiers Excel et Word apparaissent alors dans la liste de gauche. Obsidian n'affiche pas leur contenu : un clic dessus les ouvre dans Excel ou dans Word, comme avant. Referme le glossaire dans Excel quand AURA travaille dessus : un classeur ouvert l'empêche d'écrire.
3. **Voir qui parle de quoi.** Dans **« Rétroliens »** (dans la deuxième partie de la colonne), active **« Rétroliens dans le document »**. En bas de chaque page s'affichent alors les pages qui renvoient vers elle — par exemple, toutes les séances où une gamme a été évoquée.

Si l'écran n'est pas en français : **« Général »**, réglage **« Langue »**, choisis **Français**, puis relance Obsidian.

## Demander à AURA de préparer ton dossier
Dans une tâche Cowork avec ton dossier HERVÉ WORLD, tape :

> Prépare mon dossier pour Obsidian.

AURA ajoute, sans rien toucher à ce qui existe :
- `ACCUEIL` — ta page de départ ;
- `TABLEAU` — les tableaux de tes gammes, éditeurs, séances et fiches d'univers (Obsidian l'étiquette « BASE », le nom de ses fichiers de tableaux) ;
- le dossier des fiches d'univers (`Références/Narration/Univers`) et 4 modèles de fiche (personnage, lieu, faction, objet) dans `Références/Narration/_Modèles`.

Elle te demande aussi si elle peut noter dans ton profil que tu utilises Obsidian : dès lors, quand elle cite une gamme, un éditeur ou une fiche, elle l'écrit sous forme de lien cliquable.

Ensuite, dans Obsidian :
1. **Ta page de départ en un clic** : ouvre `ACCUEIL` (un clic dans la liste de gauche), appuie sur **Ctrl+P**, tape « marquer », choisis **« Signets: Marquer... »**, puis valide. ACCUEIL rejoint tes **« Signets »** (l'icône en forme de marque-page, en haut à gauche).
2. **Les modèles de fiches** (maintenant que leur dossier existe) : dans les Paramètres, **« Modèles »** (dans la deuxième partie de la colonne, sous le titre gris « Modules principaux » — pas l'entrée « Modules principaux » du haut), réglage **« Emplacement du dossier modèle »** : tape `Références/Narration/_Modèles`.

Au début, les tableaux d'ACCUEIL sont presque vides : ils se remplissent au fil de ton travail avec AURA. C'est normal.

## Ce que tu vois dans Obsidian
- **La liste de gauche** : tous tes dossiers et fichiers. Un clic ouvre une page. Attention : **faire glisser** un fichier ou un dossier dans cette liste le déplace pour de bon (voir « Les règles »).
- **ACCUEIL** : où en est le travail, tes tâches, ce qui attend une réponse, tes gammes, tes éditeurs, tes dernières séances, les fiches d'univers.
- **Rechercher dans tout le dossier** : **Ctrl+Maj+F** (Ctrl+Shift+F). Pour ouvrir un fichier dont tu connais le nom : **Ctrl+O**.
- **Les liens** : un mot souligné en couleur ouvre la page liée. Les **« Rétroliens »**, en bas de page (réglage 3), montrent toutes les pages qui parlent de celle-ci.
- **La « Vue graphique »** (icône à gauche) dessine tes pages et leurs liens. Joli, mais pas indispensable.
- **L'icône rouge barrée**, en bas à droite de la fenêtre : c'est Obsidian Sync, le service payant de synchronisation, non branché. Ignore-la.

## Pour ton métier
- **La bible d'univers d'un jeu narratif.** Dis à AURA : « fais les fiches des personnages de [jeu] », ou « fais la fiche du personnage [nom] » (ou du lieu, de la faction, de l'objet). Elle n'écrit que ce qui est sourcé (carte, page du livret, échange avec l'éditeur) ; ce qu'on ne sait pas va dans « Questions ouvertes ». Utile pour garder la même voix à un personnage d'une boîte à l'autre, et pour briefer un relecteur.
- **Une fiche commence par ses propriétés** : les champs en haut (type, gamme, nom anglais, nom français, identifiant du glossaire, sa voix, première apparition, statut). Quand tu as relu une fiche d'AURA, dis-lui « la fiche de [nom] est relue » : elle passe son statut à « relue ».
- **Le nom français vient toujours du glossaire.** Dans une fiche, il n'est qu'une copie : si tu changes un terme, change-le avec AURA au glossaire ; elle remet ensuite les fiches à jour et vérifie qu'aucune n'est restée en arrière.
- **Tes gammes et tes éditeurs** : les fiches tenues par AURA (`Core/Gammes`, `Core/Editeurs`) se lisent en un clic depuis ACCUEIL : produits, titres publiés, calendrier, contacts, tutoiement ou vouvoiement de l'éditeur.
- **Les questions aux éditeurs** : `Core/Questions_Editeurs`, avec les réponses reçues.
- **Une fiche à toi.** Le plus simple : demande-la à AURA. Pour la faire toi-même : dans la liste de gauche, ouvre `Références` › `Narration` › `Univers`. Si le dossier de ta gamme n'y est pas, clic droit sur `Univers`, **« Nouveau dossier »**, et tape le nom de la gamme exactement comme dans `Core/Gammes`. Puis clic droit sur le dossier de la gamme, **« Nouvelle note »**, et donne-lui le **nom anglais** du personnage. Enfin **Ctrl+P**, tape « modèle », choisis **« Modèles: Insérer le modèle »** et le modèle qui convient. Si tu as dû retirer un signe du nom du fichier (Windows refuse `: ? " / \ * < > |`), dis-le à AURA : elle remet le nom anglais exact dans la fiche.

## Les règles, pour que tout reste juste
1. **Lis librement. Pour modifier un fichier de `Core`, attends qu'AURA ait fini de travailler**, ou demande-le-lui. Si vous écrivez le même fichier au même moment, l'une des deux modifications peut se perdre.
2. **Ne renomme et ne déplace aucun fichier ni dossier d'AURA** (`Core`, `CLAUDE.md`, `Glossaires`, les guides, les fiches d'univers, dont le nom reste le nom anglais) : elle les cherche à leur place. Dans la liste de gauche, faire glisser un fichier ou un dossier le déplace pour de bon, et Ctrl+Z ne l'annule pas : si ça t'arrive, refais-le glisser tout de suite à son ancienne place. Si tu ne sais plus où il était, dis à AURA « j'ai déplacé un dossier par erreur » avant de faire autre chose.
3. **Un terme se décide au glossaire**, jamais dans une fiche ni dans une note.
4. **N'installe aucun module complémentaire.** Obsidian reste en « Mode restreint » : il ne fait tourner aucun programme venu d'ailleurs.
5. **Pas besoin de compte Obsidian ni d'Obsidian Sync** (payant). Tout reste sur ton PC. Deux synchronisations sur le même dossier (Obsidian Sync et OneDrive) sont la meilleure façon de perdre des modifications.
6. **Le dossier `.obsidian`** contient les réglages d'Obsidian : n'y touche pas. AURA, elle, ne le lit pas.

## Si quelque chose cloche
- **Une page ne montre pas ce qu'AURA vient d'écrire** : ferme-la et rouvre-la ; si ça ne suffit pas, ferme et relance Obsidian.
- **Message « … a été modifié hors de l'application. Fusion automatique des modifications. »** : il n'apparaît que si tu écrivais dans ce fichier au moment où AURA l'a modifié. Relis-le tout de suite (texte en double ou disparu ?) et préviens AURA.
- **Tu as modifié une page ou une case de tableau par erreur** : appuie sur **Ctrl+Z** tout de suite. Sinon, Obsidian garde pendant 7 jours des copies de tes pages, au plus une toutes les 5 minutes, prises quand une page change pendant qu'Obsidian est ouvert : **Ctrl+P**, tape « instantanés », choisis **« Récupération de fichier: Ouvrir les instantanés »**. Ce qui change pendant qu'Obsidian est fermé n'y est pas. Un fichier supprimé dans Obsidian va dans la Corbeille de Windows.
- **Un fichier ou un dossier a été déplacé** : voir la règle 2.
- **« Modèles: Insérer le modèle » ne propose rien** : le réglage du dossier des modèles n'est pas fait (voir « Demander à AURA de préparer ton dossier », étape 2).
- **Un tableau affiche une erreur** : dis à AURA « le tableau d'Obsidian affiche une erreur » ; elle relit le fichier `TABLEAU`.
- **Obsidian s'ouvre sur l'écran d'accueil, sans ton dossier** : clique sur HERVÉ WORLD s'il est dans la liste de gauche ; sinon, clique sur « Ouvrir » à droite de « Ouvrir un dossier comme coffre » et choisis de nouveau ton dossier HERVÉ WORLD.
- Si ça résiste : décris à AURA ce que tu vois, ou envoie une capture d'écran à Dorian.

## Si tu arrêtes Obsidian
Désinstalle-le comme tout programme (Paramètres de Windows › Applications), puis dis à AURA « je n'utilise plus Obsidian » : elle le note dans ton profil et cesse d'écrire des liens. Le dossier `.obsidian`, `ACCUEIL`, `TABLEAU` et les fiches peuvent rester : ils ne gênent rien, et les fiches restent lisibles comme de simples fichiers texte.

## Ce qu'Obsidian ne fait pas
- Il n'affiche pas le contenu de tes Excel et de tes Word : un clic dessus les ouvre dans Excel ou dans Word. Tes glossaires restent dans Excel, tes traductions dans Word ou dans les fichiers de l'éditeur.
- Il ne traduit rien et ne parle pas à AURA : c'est toujours dans Claude que tu travailles avec elle.
- Il ne fait pas de mise en page : pour les maquettes, demande à AURA (outil « maquettes »).
- Il ne sauvegarde pas ton dossier ailleurs : ta sauvegarde reste celle que tu as aujourd'hui.
