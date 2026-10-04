# AURA DIAGNOSTIC — vérifier que tout marche, en mots simples <!-- [I-18] -->

Hervé tape `AURA DIAGNOSTIC` (ou dit « quelque chose ne marche pas »). Tu fais les contrôles toi-même, puis tu donnes **un verdict en trois couleurs**, **une seule action** à faire (la plus bloquante d'abord), et le détail technique en dessous, pour Dorian.

## Les contrôles, dans l'ordre
1. **Le dossier est connecté** : la conversation voit-elle un dossier qui contient `CLAUDE.md` et `Core/CONTEXT.md` ? S'il y a un dossier intermédiaire (téléchargement Drive : `HERVÉ WORLD-2026…\HERVÉ WORLD\`), le bon est celui qui contient directement CLAUDE.md, Core et Glossaires. Pour le connecter : le bouton dossier de la conversation, puis ce dossier-là. <!-- [D-05] -->
2. **La version du dossier** : si `Core/VERSION.md` manque, la mise à jour n'est pas faite, et la règle du SKILL.md de ce skill (section 2, point 1) s'applique au diagnostic aussi : **tu t'arrêtes ici, sans rien écrire**. Verdict : 🟠, « Ton dossier n'a pas encore reçu la mise à jour d'AURA. À faire : tape AURA MISE À JOUR. » C'est la mise à jour qui vérifiera l'écriture dans ton dossier. <!-- [R-24] -->
   Si `Core/VERSION.md` existe : sa ligne `version:` est celle du plugin (son fichier `plugin.json`, chemin donné au même endroit du SKILL.md) et l'amorce `CLAUDE.md` porte la même version. Si `plugin.json` est illisible, tu le dis dans le détail pour Dorian. <!-- [R-13] -->
3. **Lecture ET écriture** : tu écris une ligne témoin datée en bas de la note de séance `Core/Sessions/AAAA-MM-JJ.md` (jamais dans le Journal), tu la relis. Une conversation qui tourne « dans le cloud » n'atteint le dossier que si Claude Desktop est **ouvert** sur l'ordinateur.
4. **Les fichiers de mémoire** : CONTEXT, Profile, Preferences, Journal, Tasks, evas, ONBOARDING, Suivi, _EN_COURS, Questions_Editeurs — présents ou à créer.
5. **Les dossiers** : Glossaires, Références, Livrables, IMPORT — un téléchargement en zip peut avoir omis les dossiers vides ; tu les recrées s'ils manquent (avec un fichier LISEZ-MOI). <!-- [D-25] -->
6. **Le plugin AURA** : les skills `aura-localisation:…` se chargent (tu en charges un pour vérifier). Les skills ont besoin que l'exécution de code soit activée : Settings > Capabilities > Code execution (en français, si l'application est traduite : Réglages > Capacités).
7. **Les doublons de skills** <!-- [R-10] --> : dans ta liste de skills, un nom du plugin (`glossaire`, `traduction-jeux`, `narration-jeux`, `comprehension-regles`, `qa-coherence`, `relecture-multi-agents`, `brief-editeur`…) apparaît-il aussi **sans** le préfixe `aura-localisation:` ? C'est un ancien skill ajouté au compte, qui suit un autre format de glossaire. Verdict 🟠, action : « Dans Customize > Skills, désactive [nom] : c'est une ancienne version, le plugin AURA a la sienne. » Tu ne le désactives pas toi-même.
8. **Le plugin a-t-il reçu la dernière version ?** <!-- [R-45] --> Tu ne peux pas le savoir seule (la raison est écrite dans la dernière section du skill `mise-a-jour`). Si Hervé dit que Dorian lui a annoncé une nouveauté qu'il ne voit pas, ou une version plus récente que celle de `plugin.json` : verdict 🟠, action : les gestes de cette dernière section du skill `mise-a-jour`, recopiés tels qu'elle les écrit.
9. **Les programmes voient-ils le dossier ?** (règle « Les programmes et le dossier d'Hervé », étape 0) : dans une conversation qui tourne dans le cloud, la réponse normale est **non** — ce n'est pas une panne, c'est le fonctionnement ; tu le dis en 🟢, avec la marche à suivre (glisser le fichier).
10. **Les glossaires** (seulement si le programme voit le dossier) : chaque `Glossaires/Glossaire_*.xlsx` s'ouvre (script du skill `glossaire`) ; un fichier qui refuse de s'ouvrir alors que le programme voit le dossier est peut-être ouvert dans Excel.
11. **Les doublons de synchronisation** <!-- [I-26] --> : des fichiers « Nom (1).xlsx », « Nom-NOMDUPC.md », « Nom 2.md » signalent un conflit de synchronisation (OneDrive, Drive). Le bon remède est que HERVÉ WORLD ne soit pas dans un dossier synchronisé en permanence ; s'il reste dans OneDrive, le minimum est « Toujours conserver sur cet appareil » sur HERVÉ WORLD (clic droit dans l'Explorateur de fichiers), comme le dit `GUIDE_OBSIDIAN.md`. Tu le signales, tu ne fusionnes rien seule.

## Le verdict
```
🟢 Tout est en ordre.                     (ou)
🟠 Ça marche, mais : [le problème en une phrase]. À faire : [une action].
🔴 Bloqué : [le problème en une phrase]. À faire : [une action].
Si le rouge résiste : fais une capture de cet écran et envoie-la à Dorian.

Détail pour Dorian : [contrôle par contrôle, en une ligne chacun]
```
Jamais plus d'une action demandée à la fois.
