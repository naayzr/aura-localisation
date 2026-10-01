# AURA SAVE — la sauvegarde en détail

La sauvegarde se déclenche de trois façons : Hervé tape `AURA SAVE` ; tu la lances toi-même (toutes les 10 à 15 réponses d'une longue séance, ou quand la conversation approche de sa limite — annoncé en une ligne) ; ou au démarrage, pour rattraper une session fermée sans SAVE (note de `Core/Sessions/` plus récente que le Journal).

## 1. Le scan — actif, catégorie par catégorie
Tu relis la conversation (et la note de session du jour) pour chacune des cinq catégories. Ce n'est pas un souvenir : c'est une relecture.

| # | Catégorie | Où ça s'écrit |
|---|---|---|
| 1 | **Termes** validés, discutés, refusés, modifiés | Le glossaire de la gamme, par le skill `glossaire` (statut : Confirmé si Hervé a validé, sinon Brouillon ou À confirmer). **Nulle part ailleurs.** |
| 2 | **Corrections** d'AURA — signaux directs ET doux | `Core/Preferences.md` (règle de style ou de travail) ; si c'était une invention : aussi `Core/evas.md` (format dans `anti-hallucination.md`) |
| 3 | **Faits** sur Hervé, ses éditeurs, ses projets, ses contacts, ses gammes : nom propre nouveau, échéance, statut, volume, tarif | `Core/Profile.md`, `Core/Editeurs/<Éditeur>.md`, `Core/Gammes/<Gamme>.md`, `Core/CONTEXT.md` |
| 4 | **Décisions et préférences** de travail (« je groupe toujours mes questions ») | `Core/Preferences.md` — jamais une décision de terme, qui va au glossaire |
| 5 | **Tâches** dites avec les mots-clés OU en passant (« il faudrait que je », « pense à », « à ne pas oublier ») | `Core/Tasks.md` ; si c'est un fil en attente d'un tiers : `Core/Suivi.md` ; une question à un éditeur : `Core/Questions_Editeurs.md` |

<!-- [D-10] --> <!-- [D-30] -->

## 2. L'écriture — tous les fichiers concernés, dans cet ordre
1. Glossaire(s) — par le skill `glossaire` (sauvegarde datée avant toute modification en masse).
2. `Core/evas.md`, puis `Core/Preferences.md`.
3. `Core/Profile.md`, fiches `Core/Editeurs/`, registres `Core/Gammes/`.
4. `Core/Questions_Editeurs.md`, `Core/Suivi.md` (fils ouverts avec leur date de dernière activité, fils clos avec leur date).
5. `Core/Tasks.md`.
6. `Core/_EN_COURS.md` (état présent du travail et portes de livraison).
7. `Core/CONTEXT.md` — réécrit en **état présent** seulement, et **plafonné à ~1 500 tokens (≈ 6 000 caractères)** : qui, projet actif, pipeline en tableau court, prochaine action. Ce qui dépasse va au Journal. <!-- [I-05] -->
8. `Core/Journal.md` — **on ajoute en bas, on n'efface jamais** : `## Session AAAA-MM-JJ — [sujet]`, ce qui a été fait, décidé, appris, ce qui reste. Une ligne de sommaire en tête du Journal (date + sujet).
9. La note `Core/Sessions/AAAA-MM-JJ.md` : ajoute en bas « promue dans le Journal à HHhMM ».
10. Tu confirmes : « Sauvegardé. Reprends avec AURA START quand tu veux. » — et tu dis en une ligne s'il reste un point non sauvegardé (fichier verrouillé, par exemple).

Si `Core/Profile.md` dit qu'Hervé utilise Obsidian, les gammes, éditeurs et fiches d'univers que tu cites dans ces fichiers s'écrivent en liens : la forme est dans le skill `obsidian` (section 4), charge-le.

## 3. Les filets
- **Fichier ouvert dans Excel** : sous Windows, un classeur ouvert est verrouillé. Si l'écriture échoue, tu ne forces pas : « Ferme Glossaire_X.xlsx dans Excel, je réessaie. » Tu ne réécris jamais un glossaire depuis ta mémoire. <!-- [D-19] -->
- **Fichier modifié par Hervé entre-temps** : relis-le juste avant d'écrire, et n'écris que la ligne qui change.
- **Jamais de réécriture complète** d'un fichier mémoire long (Journal, Preferences, un glossaire) : tu ajoutes ou tu modifies la ligne concernée.

## 4. L'archivage — quand le Journal grossit
Au-delà de ~50 sessions ou chaque trimestre, à l'audit mensuel : les sessions anciennes partent dans `Core/Archives/Journal_AAAA-T<n>.md`, et le Journal garde, pour chacune, sa ligne de sommaire. Tu relis l'archive après l'avoir écrite, avant de retirer quoi que ce soit du Journal, et tu demandes l'accord d'Hervé avant de retirer.
