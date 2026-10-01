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
python3 scripts/renvois.py Livrables/<Projet>/<Livret>_FR_v2.docx --source <Livret>_EN.docx
```

| Rubrique du rapport | Ce que ça veut dire | Ce qu'AURA fait |
|---|---|---|
| Renvoi vers une règle introuvable | le texte renvoie à un numéro qui n'existe pas (dans la traduction, ou dans le fichier `--regles`) | comparer à la VO : erreur de traduction → correction proposée ; erreur déjà dans la VO → question à l'éditeur |
| Numéro défini plusieurs fois | deux titres portent le même numéro | numérotation glissée : retrouver le bon numéro dans la VO |
| Trou dans la numérotation | 5.1, 5.2, 5.4 : la 5.3 manque | règle oubliée, ou numéro glissé |
| Numéro écrit avec une virgule | « règle 5,2 » | aligner sur la forme du livret |
| Règle de la VO absente de la traduction | la VO a une 7.3, la traduction non | paragraphe oublié ou fusionné : à retrouver |
| Renvois en nombre différent | la VO renvoie 2 fois à la 5.2, la traduction 1 fois | un renvoi perdu ou modifié : à retrouver |
| Renvois de page | « page 12 », « p. 12 » | marquer `[PAGE À CONFIRMER]`, à remplir sur l'épreuve |

Le code de sortie vaut 0 seulement si aucune anomalie n'est trouvée **et** que l'existence des règles a pu être vérifiée. « Contrôle incomplet » veut dire : numérotation automatique de Word, ou fichier de cartes sans `--regles`.

## 3. Le rapport des renvois, pour Hervé

```
RENVOIS ET NUMÉROS DE RÈGLE — <Jeu> — <date>

Résumé
- Renvois internes trouvés : N (comptés par script), contenu vérifié : N sur N
- Anomalies de la traduction : N (corrections proposées ci-dessous)
- Erreurs de la version originale : N (questions à l'éditeur)
- Renvois de page : N, tous marqués [PAGE À CONFIRMER] — à remplir sur l'épreuve
- Non vérifié : <ce qui ne l'a pas été, et pourquoi — ou « rien »>

Corrections proposées
- § 41 (règle 1.2) : « règle 8.2 » → « règle 5.3 » (la VO renvoie à 5.3)

Questions à l'éditeur (inscrites au registre Core/Questions_Editeurs.md)
- n° <N> : …
```

## 4. Une question à l'éditeur

Chaque question s'ajoute en une ligne au registre `Core/Questions_Editeurs.md` (colonnes : N°, Éditeur, Produit, Référence, Question, Proposition d'Hervé, Statut, Réponse, Date réponse, Impact glossaire). Elle est écrite en clair, comme elle partira :

> **Référence** : règle 6.2, 3e ligne.
> **Question** : la version originale renvoie à la règle 3.4, qui traite des ressources et non du déplacement. Faut-il lire 3.5 (Mouvement) ?
> **Proposition** : en attendant votre réponse, la traduction garde « règle 3.4 ».

Pas de code interne (pas de « [REF-03] », pas de nom de skill) dans ce qui part chez l'éditeur. Le courriel qui groupe les questions se rédige avec le skill `brief-editeur`, en brouillon ; la signature et le registre se lisent dans la fiche de l'éditeur.
