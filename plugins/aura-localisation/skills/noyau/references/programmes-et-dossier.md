# Les programmes et le dossier d'Hervé — LA règle (la seule écriture)

Tous les outils qui lancent un programme (comptage, typographie, longueurs, glossaire, vérifications,
gamme, relecture) appliquent cette règle. Aucun d'eux ne la réécrit à sa façon.

## Ce qui est établi, et ce qui ne l'est pas
- Une tâche Cowork tourne soit **sur l'ordinateur d'Hervé**, soit **dans le cloud**. À partir du
  06/10/2026, les nouvelles tâches d'un abonnement Pro ou Max tournent **dans le cloud** : c'est le cas
  normal, pas une exception.
- Dans une tâche **sur l'ordinateur**, les programmes voient le dossier HERVÉ WORLD connecté.
- Dans une tâche **dans le cloud**, les programmes tournent sur une machine distante et temporaire : ils
  **ne voient pas** le dossier d'Hervé. Toi, tu continues de lire et d'écrire ses fichiers **texte** avec
  tes outils de fichiers, mais **seulement tant que Claude Desktop reste ouvert** sur son ordinateur.
- **Non établi** (à ne jamais promettre) : qu'un fichier glissé dans la conversation soit visible du
  programme dans une tâche Cowork ; qu'un fichier produit par le programme puisse être téléchargé ;
  que tes outils de fichiers puissent écrire un fichier binaire (Excel, Word) dans son dossier.
  Tant que Dorian ne l'a pas vérifié, tu le **constates** à chaque fois au lieu de le supposer.

## Écrire une commande — deux chemins complets, jamais un chemin relatif <!-- [R-29] -->
Une commande vise deux endroits différents : le programme, qui est dans le plugin, et les fichiers
d'Hervé, qui sont dans HERVÉ WORLD. Un chemin relatif dépend du dossier où la commande est lancée :
lancé depuis le dossier d'un skill, un `Glossaires/…` ou un `Livrables/…` écrirait **dans le plugin**,
où le fichier se perd à la prochaine synchronisation. Donc, dans toutes les commandes des skills :
- **le programme** s'écrit avec son chemin complet : `python3 "${CLAUDE_SKILL_DIR}/scripts/<programme>.py"`
  (dans un SKILL.md, l'application remplace `${CLAUDE_SKILL_DIR}` par le dossier du skill ; dans un
  fichier `references/`, c'est le dossier du skill auquel il appartient). Le programme d'un autre skill
  du plugin : `python3 "${CLAUDE_SKILL_DIR}/../<autre skill>/scripts/<programme>.py"`. Quand un skill
  cite un programme en abrégé (`scripts/<programme>.py`, `<programme>.py …`), c'est ce chemin-là. Si `${CLAUDE_SKILL_DIR}` t'arrive écrit tel quel (non remplacé), le dossier du skill est
  celui du `SKILL.md` que tu viens de lire : tu écris ce chemin en entier, jamais la variable brute ;
- **chaque fichier d'Hervé** s'écrit avec son chemin complet sous HERVÉ WORLD, tel que le programme le
  voit (étape 0) : `"<HERVÉ WORLD>/Glossaires/Glossaire_<Gamme>.xlsx"`. Quand un skill écrit
  `Glossaires/…`, `Livrables/…`, `Core/…` ou `Références/…`, c'est sous HERVÉ WORLD ;
- **tu lances toujours un programme depuis HERVÉ WORLD**, jamais depuis le dossier d'un skill : la
  commande commence par `cd "<HERVÉ WORLD>" && ` (si le programme ne voit pas HERVÉ WORLD, par un `cd`
  vers le dossier de travail temporaire). C'est le filet, si un chemin relatif t'a échappé : une cible
  `Glossaires/…` tombe alors dans HERVÉ WORLD, et un programme cité en abrégé (`python3 scripts/…`)
  n'est pas trouvé, ce qui arrête la commande au lieu d'écrire dans le plugin. Tu la réécris et tu
  relances ;
- **avant de lancer un programme qui écrit** (`--ecrire`, `--sortie`, `--dans`, `--plan`, ou une sortie
  envoyée dans un fichier par `>`), tu relis la commande : chaque fichier ou dossier où il écrira
  commence par le chemin complet de HERVÉ WORLD ou, si le programme ne voit pas HERVÉ WORLD, par celui
  du dossier de travail temporaire. Une cible qui commence par un nom de dossier (`Glossaires/…`,
  `Livrables/…`) est relative : tu ne lances pas, tu la réécris ;
- **après un programme qui écrit** (glossaire, mémoire de traduction, plan de relecture), tu ne te fies
  pas au chemin qu'il affiche, qui répète celui qu'on lui a donné, même relatif. Tu refais l'étape 0
  ci-dessous sur le chemin complet où le fichier devait arriver : `False` veut dire que le fichier n'est
  pas posé. Tu le dis, et tu relances la même commande en chemins complets ;
- si le programme ne voit pas HERVÉ WORLD (tâche dans le cloud), ce qu'il produit va dans un dossier de
  travail temporaire, jamais dans le dossier du plugin, puis tu suis « Le programme ne voit pas le
  fichier » ci-dessous.

## Étape 0 — toujours vérifier avant de lancer un programme
Demande au programme si le fichier existe pour lui, avant tout calcul :
`python3 -c "import os,sys; print(os.path.exists(sys.argv[1]))" "<chemin du fichier>"`
- `True` → le programme voit le fichier : tu travailles directement, comme décrit dans chaque outil.
- `False` → le programme ne le voit pas : procédure ci-dessous. Tu ne présentes **aucun chiffre ni
  aucun contrôle** comme fait sur ce fichier tant que le programme ne l'a pas lu.

## Le programme ne voit pas le fichier
1. **Demande à Hervé de glisser le fichier dans la conversation**, en une phrase : « Glisse
   [nom du fichier] dans cette conversation, je le passe au programme. »
2. **Refais l'étape 0 sur le fichier glissé.** S'il est visible, le programme travaille dessus. S'il ne
   l'est pas non plus, dis-le franchement : « Dans cette conversation, mon programme ne peut pas lire
   ton fichier. » Tu peux relire un texte toi-même, mais un comptage ou un contrôle fait « à l'œil » se
   présente comme une **estimation**, jamais comme un compte exact ; un chiffre qui part sur un devis
   attend une tâche où le programme lit le fichier.
3. **Les résultats en texte** (rapports, listes d'alertes, plan de relecture `PLAN.txt`, comptes) : tu
   les écris **toi-même** dans HERVÉ WORLD avec tes outils de fichiers (dans `Livrables/<Projet>/` ou la
   note de séance). Un résultat laissé seulement sur la machine du programme disparaît avec la tâche.
4. **Les résultats binaires** (un glossaire Excel, un Word corrigé) : tu ne remplaces **jamais** un
   fichier d'Hervé par toi-même. Tu suis « Poser un fichier produit » ci-dessous.

## Poser un fichier produit (glossaire, Word) — sans jamais rien perdre
1. Le fichier produit porte un nom qui ne peut écraser rien : `<Nom>_NOUVEAU_AAAA-MM-JJ.xlsx`.
2. **Avant toute pose, tu écris les décisions en texte** dans la note de séance
   `Core/Sessions/AAAA-MM-JJ.md` (« décisions de termes en attente de pose dans le glossaire : … ») et
   une ligne dans `Core/Suivi.md`. Tant que la pose n'est pas vérifiée, c'est cette trace qui fait foi.
3. Si le programme a pu écrire directement dans le dossier (tâche sur l'ordinateur) : il a fait
   lui-même la sauvegarde datée dans `Core/Archives/` ; tu le vérifies (le fichier `_avant_…` existe).
4. Sinon, si Hervé a pu **télécharger** le fichier produit (il le voit dans ses Téléchargements), tu lui
   donnes **deux gestes, dans cet ordre, avec les noms exacts** :
   1. « Dans ton dossier HERVÉ WORLD, déplace `Glossaires/Glossaire_<Gamme>.xlsx` dans
      `Core/Archives/` et renomme-le `Glossaire_<Gamme>_avant_AAAA-MM-JJ.xlsx`. »
   2. « Enregistre le fichier que je te donne dans `Glossaires/` sous le nom `Glossaire_<Gamme>.xlsx`. »
5. **Vérifier la pose** (tout de suite, ou au début de la séance suivante) : le maître de `Glossaires/`
   doit avoir le nombre de termes attendu et, en dernière ligne de son CHANGELOG, la dernière décision
   (programme `controle_glossaire.py` du skill `glossaire`, sur le fichier relu ou glissé). Alors
   seulement, tu marques dans la note de séance « posé et vérifié le … » et tu clos la ligne du Suivi.
6. Si Hervé ne peut pas récupérer le fichier : les décisions restent dans la note de séance et le
   Suivi, et tu les poses à la prochaine tâche où le programme voit le dossier. Rien n'est perdu.

## Ce que tu dis à Hervé, une fois, quand le cas se présente
« Selon la façon dont la conversation tourne, mes petits programmes ne voient pas toujours ton dossier. Dans
ce cas je te demande de glisser le fichier dans la conversation, et quand je produis un nouveau
fichier, je te dis exactement où le ranger. Laisse Claude Desktop ouvert pendant que tu travailles
avec moi : c'est lui qui me donne accès à ton dossier. »
