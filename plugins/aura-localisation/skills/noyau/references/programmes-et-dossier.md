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
   l'est pas non plus, dis-le franchement : « Dans cette tâche, mon programme ne peut pas lire ton
   fichier. » Tu peux relire un texte toi-même, mais un comptage ou un contrôle fait « à l'œil » se
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
« Selon la façon dont la tâche tourne, mes petits programmes ne voient pas toujours ton dossier. Dans
ce cas je te demande de glisser le fichier dans la conversation, et quand je produis un nouveau
fichier, je te dis exactement où le ranger. Laisse Claude Desktop ouvert pendant que tu travailles
avec moi : c'est lui qui me donne accès à ton dossier. »
