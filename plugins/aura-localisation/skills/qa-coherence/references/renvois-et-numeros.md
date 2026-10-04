# Renvois et numéros de règle — table, rapport, questions

> **[EXEMPLE FICTIF]** — les numéros, titres et pages ci-dessous sont construits pour l'illustration.

## 1. La table des renvois (classeur de travail du projet)

VO = version originale ; FR = traduction.

Elle se crée **avant** de traduire, dans `Livrables/<Projet>/` (par exemple `Renvois_<Projet>.xlsx`), et se tient jusqu'à l'épreuve finale.

| Concept | N° règle VO | Page VO | N° règle FR | Page FR | Statut |
|---|---|---|---|---|---|
| Combat | 4.3 | 12 | 4.3 | [PAGE À CONFIRMER] | Règle vérifiée |
| Déplacement | 5.1 | 15 | 5.1 | [PAGE À CONFIRMER] | Règle vérifiée |
| Blessures | 5.3 | 16 | — | — | Absente de la traduction : à traiter |

- Les colonnes VO se remplissent **avant** de traduire, depuis la version originale.
- La colonne « N° règle FR » se remplit pendant la traduction et se vérifie avec `scripts/renvois.py`.
- La colonne « Page FR » ne se remplit **que sur l'épreuve mise en page** : jusque-là, `[PAGE À CONFIRMER]`. La traduction allonge le texte ; les renvois de page glissent, parfois de plusieurs pages.

## 2. Lire le rapport de `renvois.py`

```
python3 "${CLAUDE_SKILL_DIR}/scripts/renvois.py" "<HERVÉ WORLD>/Livrables/<Projet>/<Livret>_FR_v2.docx" --source <Livret>_EN.docx
```

| Rubrique du rapport | Ce que ça veut dire | Ce qu'AURA fait |
|---|---|---|
| Renvoi vers une règle introuvable | le texte renvoie à un numéro à plusieurs niveaux qui n'existe pas (« voir 8.2 »), ni dans la traduction ni dans le fichier `--regles` | comparer à la VO : erreur de traduction → correction proposée ; erreur déjà dans la VO → question à l'éditeur |
| À lire : renvoi à un seul niveau que le programme ne peut pas établir | « règle 7 », « section 2 du plateau », « règle 12 du livret de campagne », « règle 52 », « Règle 52 : … » en tête d'un aide-mémoire, le 3e numéro de « règles 3, 4 et 13 » : aucun titre « Règle 7 — … », « Chapitre 7 » ni aucune règle 7.1 ne l'établit. Le programme ne sait pas si le numéro vise une zone du plateau, un autre document, une étape de liste, ou s'il est faux ; « (un titre « 7. » existe…) » signale une liste numérotée qui porte ce numéro. Ce n'est pas une anomalie, mais le code de sortie vaut 1 tant qu'il y en a | lire chaque phrase : zone du plateau ou autre document → rien à corriger, et le rapport le dit (« lu : vise le plateau ») ; sinon faute de numéro → comparer à la VO, et proposer la correction (« 52 » pour « 5.2 » : la rubrique « Renvois en nombre différent » montre aussi le 5.2 perdu, quand la VO y a un renvoi « 5.2 ») |
| Numéro défini plusieurs fois | deux titres portent le même numéro | numérotation glissée : retrouver le bon numéro dans la VO |
| Trou dans la numérotation | 5.1, 5.2, 5.4 : la 5.3 manque | règle oubliée, ou numéro glissé |
| Numéro écrit avec une virgule | « règle 5,2 » | aligner sur la forme du livret |
| Règle de la VO absente de la traduction | la VO a une 7.3, la traduction non | paragraphe oublié ou fusionné : à retrouver |
| Renvois en nombre différent | la VO renvoie 2 fois à la 5.2, la traduction 1 fois (numéros à plusieurs niveaux seulement : « section 7 of the board » peut devenir « zone 7 du plateau ») | un renvoi perdu ou modifié : à retrouver |
| Renvois de page | « page 12 », « p. 12 » | marquer `[PAGE À CONFIRMER]`, à remplir sur l'épreuve |

Le code de sortie vaut 0 seulement si aucune anomalie n'est trouvée, qu'aucun renvoi n'est à lire, **et** que l'existence des règles à plusieurs niveaux visées a pu être vérifiée (dans un texte sans aucune règle à plusieurs niveaux, le code peut valoir 0 : l'avertissement en tête du rapport dit alors ce qui n'a pas été vérifié). « Contrôle incomplet » veut dire : numérotation automatique de Word, ou fichier de cartes sans `--regles`.

## 3. Le rapport des renvois, pour Hervé

```
RENVOIS ET NUMÉROS DE RÈGLE — <Jeu> — <date>

Résumé
- Renvois internes trouvés : N (comptés par script), contenu vérifié : N sur N
- Anomalies de la traduction : N (corrections proposées ci-dessous)
- Renvois à lire (un seul niveau, numéro absent) : N, tous lus : <ce que chacun vise — zone du plateau, autre livret, ou faute corrigée ci-dessous>
- Erreurs de la version originale : N (questions à l'éditeur)
- Renvois de page : N, tous marqués [PAGE À CONFIRMER] — à remplir sur l'épreuve
- Non vérifié : <ce qui ne l'a pas été, et pourquoi — ou « rien »>

Corrections proposées
- § 41 (règle 1.2) : « règle 8.2 » → « règle 5.3 » (la VO renvoie à 5.3)

Questions à l'éditeur (inscrites au registre Core/Questions_Editeurs.md)
- n° <N> : …
```

## 4. Une question à l'éditeur

Chaque question s'ajoute en une ligne au registre `Core/Questions_Editeurs.md`, dans la section de l'éditeur, au format défini par le skill `brief-editeur` (qui seul en fixe les colonnes et les statuts). <!-- [R-28] --> Elle est écrite en clair, comme elle partira :

> **Référence** : règle 6.2, 3e ligne.
> **Question** : la version originale renvoie à la règle 3.4, qui traite des ressources et non du déplacement. Faut-il lire 3.5 (Mouvement) ?
> **Proposition** : en attendant votre réponse, la traduction garde « règle 3.4 ».

Pas de code interne (pas de « [REF-03] », pas de nom de skill) dans ce qui part chez l'éditeur. Le courriel qui groupe les questions se rédige avec le skill `brief-editeur`, en brouillon ; la signature et le registre se lisent dans la fiche de l'éditeur.
