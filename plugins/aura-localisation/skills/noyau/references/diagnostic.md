# AURA DIAGNOSTIC — vérifier que tout marche, en mots simples <!-- [I-18] -->

Hervé tape `AURA DIAGNOSTIC` (ou dit « quelque chose ne marche pas »). Tu fais les contrôles toi-même, puis tu donnes **un verdict en trois couleurs**, **une seule action** à faire (la plus bloquante d'abord), et le détail technique en dessous, pour Dorian.

## Les contrôles, dans l'ordre
1. **Le dossier est connecté** : la tâche voit-elle un dossier qui contient `CLAUDE.md` et `Core/CONTEXT.md` ? S'il y a un dossier intermédiaire (téléchargement Drive : `HERVÉ WORLD-2026…\HERVÉ WORLD\`), le bon est celui qui contient directement CLAUDE.md, Core et Glossaires. <!-- [D-05] -->
2. **Lecture ET écriture** : tu écris une ligne témoin datée en bas de la note de séance `Core/Sessions/AAAA-MM-JJ.md` (jamais dans le Journal), tu la relis. Une session qui tourne « dans le cloud » n'atteint le dossier que si Claude Desktop est **ouvert** sur l'ordinateur.
3. **Les fichiers de mémoire** : CONTEXT, Profile, Preferences, Journal, Tasks, evas, ONBOARDING, Suivi, _EN_COURS, Questions_Editeurs — présents ou à créer.
4. **Les dossiers** : Glossaires, Références, Livrables, IMPORT — un téléchargement en zip peut avoir omis les dossiers vides ; tu les recrées s'ils manquent (avec un fichier LISEZ-MOI). <!-- [D-25] -->
5. **La version** : `Core/VERSION.md` existe et correspond à la version de l'extension (skill `mise-a-jour`) ; l'amorce `CLAUDE.md` porte la même version.
6. **L'extension** : les skills `aura-localisation:…` se chargent (tu en charges un pour vérifier). Les skills ont besoin que l'exécution de code soit activée dans les réglages (Réglages > Capacités).
7. **Les programmes voient-ils le dossier ?** (règle « Les programmes et le dossier d'Hervé », étape 0) : dans une tâche qui tourne dans le cloud, la réponse normale est **non** — ce n'est pas une panne, c'est le fonctionnement ; tu le dis en 🟢, avec la marche à suivre (glisser le fichier).
8. **Les glossaires** (seulement si le programme voit le dossier) : chaque `Glossaires/Glossaire_*.xlsx` s'ouvre (script du skill `glossaire`) ; un fichier qui refuse de s'ouvrir alors que le programme voit le dossier est peut-être ouvert dans Excel.
9. **Les doublons de synchronisation** <!-- [I-26] --> : des fichiers « Nom (1).xlsx », « Nom-NOMDUPC.md », « Nom 2.md » signalent un conflit de synchronisation (OneDrive, Drive). Le bon remède est que HERVÉ WORLD ne soit pas dans un dossier synchronisé en permanence ; tu le signales, tu ne fusionnes rien seule.

## Le verdict
```
🟢 Tout est en ordre.                     (ou)
🟠 Ça marche, mais : [le problème en une phrase]. À faire : [une action].
🔴 Bloqué : [le problème en une phrase]. À faire : [une action].
Si le rouge résiste : fais une capture de cet écran et envoie-la à Dorian.

Détail pour Dorian : [contrôle par contrôle, en une ligne chacun]
```
Jamais plus d'une action demandée à la fois.
