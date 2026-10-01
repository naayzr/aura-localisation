# Le dictionnaire des symboles <!-- [D-22] -->

> **[EXEMPLE FICTIF]** — les symboles, noms et cartes de ce fichier sont inventés pour l'illustration. Aucune affirmation sur un jeu réel n'est faite ici : un cas tiré d'un jeu publié n'entre dans un skill qu'avec sa source (page, document de l'éditeur).

## 1. Le modèle

Un classeur par jeu, dans `Livrables/<Projet>/` (par exemple `Symboles_<Projet>.xlsx`), créé **avant** de traduire.

| Description visuelle | Nom officiel (version originale) | Nom FR retenu | Signification mécanique | Première occurrence | Statut |
|---|---|---|---|---|---|
| Flamme orange | Fire | Feu | inflige 1 dégât aux cases adjacentes | carte « Brasier », recto | Confirmé |
| Flamme bleue | Arcane Fire | Feu arcanique | ignore les résistances physiques | règle 8.4 | À confirmer |

- **Pourquoi une description visuelle ?** On traduit souvent sur des fichiers texte, sans les visuels définitifs. La description permet de retrouver le symbole quand la planche arrive.
- **Le nom français retenu** est un terme de jeu : il vit au glossaire de la gamme (catégorie COMPOSANT ou MOT-CLÉ), avec le même statut. Le dictionnaire le reprend, il ne le décide pas.
- **La signification mécanique** est écrite en clair : c'est elle qui permet de repérer deux symboles proches aux sens opposés.

## 2. Les symboles qui se ressemblent

Deux icônes visuellement proches peuvent dire le contraire :
- l'une est un **coût** (on dépense), l'autre un **gain** (on reçoit) ;
- l'une s'applique **à vous**, l'autre **à l'adversaire** ;
- l'une est **permanente**, l'autre **temporaire**.

[EXEMPLE FICTIF] Dans un jeu imaginaire, les jetons *Brume* et *Ombre* ont la même forme ronde et des teintes voisines une fois imprimés en petit ; seule une flèche, montante ou descendante, distingue *Peur produite* de *Peur exigée*. Les confondre dans le texte d'un pouvoir crée un effet impossible.

Pour chaque paire à risque, le dictionnaire porte une ligne « Ne pas confondre avec : … ».

## 3. La méthode

1. **Au-delà d'une dizaine de symboles distincts**, demander à l'éditeur un document de référence — même une capture de la planche d'icônes avec les noms officiels — et lui faire valider le dictionnaire **avant** de traduire.
2. **Pendant la traduction**, chaque nouveau symbole entre au dictionnaire avec sa première occurrence.
3. **Après la traduction**, le balayage par script (dossier `scripts/` de ce skill) :
   - `chercher.py <texte> --liste noms_anglais.txt` : chaque nom anglais resté dans la traduction, avec son endroit ;
   - `chercher.py <texte> --liste variantes_refusees.txt` : chaque forme française non conforme ;
   - `chercher.py <texte> "Feu arcanique" --strict` : la majuscule appliquée partout de la même façon (la convention est celle de l'éditeur, skill `typographie-fr`).
4. **L'intégrité des balises d'icônes** (`{icon_fire}`, `[fire]`…) d'une langue à l'autre — même nombre, même ordre — se contrôle avec le skill `controle-longueur`.
