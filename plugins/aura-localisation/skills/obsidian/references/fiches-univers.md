# Fiches d'univers — le format

Une fiche par personnage, lieu, faction ou objet d'un jeu. Elles vivent dans
`Références/Narration/Univers/<Gamme>/<Nom anglais>.md` ; `<Gamme>` s'écrit comme dans `Core/Gammes/<Gamme>.md`.
Le tableau « Fiches d'univers » de `TABLEAU.base` les rassemble, groupées par gamme ; la vue « Personnages » les montre en vignettes.

## Les propriétés (en tête de fichier, entre deux lignes `---`)

| Propriété | Ce qu'elle contient | D'où elle vient |
|---|---|---|
| `type` | `personnage`, `lieu`, `faction`, `objet` ou `autre` | le modèle choisi |
| `gamme` | le nom de la gamme, comme dans `Core/Gammes/` | Hervé ou la séance |
| `nom_en` | le nom anglais exact, tel qu'imprimé | la source anglaise |
| `nom_fr` | le nom français | **copie du glossaire** (colonne FR du terme `id_glossaire`) ; vide tant que le terme n'y est pas |
| `id_glossaire` | l'identifiant du terme (colonne ID) | le glossaire ; vide tant que le terme n'y est pas |
| `registre` | en une ligne : à qui il dit « tu » ou « vous », niveau de langue | les textes lus, ou Hervé |
| `premiere_apparition` | carte, page, livret, scénario | la source |
| `statut_fiche` | `brouillon` (écrite par AURA) ou `relue` (relue par Hervé) | Hervé passe la fiche à `relue` |
| `tags` | `univers` | le modèle |

Les valeurs sont écrites entre guillemets droits quand elles contiennent `:`, `#`, `[` ou commencent par un chiffre ; une valeur qui contient `"` s'écrit entre apostrophes droites (une apostrophe s'y double : `'L''Ordre'`).
Le genre d'un nom inventé n'est **pas** dans la fiche : il est au glossaire (colonne GENRE), qui fait foi.

## Le nom du fichier
- Le nom anglais exact, sans les caractères que Windows refuse dans un nom de fichier (`\ / : * ? " < > |`) : on les remplace par un tiret, et on garde le nom exact dans `nom_en`.
- Deux éléments au même nom anglais dans une gamme (un lieu et une faction homonymes) : on ajoute le type entre parenthèses — `Ashen Order (faction).md` [EXEMPLE FICTIF].
- On ne renomme pas une fiche quand le nom français change : c'est tout l'intérêt du nom anglais.
- Une fiche créée par Hervé avec un modèle prend le nom du fichier dans `nom_en` : si le nom du fichier a perdu un signe ou porte « (faction) », tu remets dans `nom_en` le nom anglais exact.

## Le corps
Les sections du modèle, dans l'ordre. Chaque fait porte sa source entre parenthèses — `(carte 12)`, `(livret de règles p. 8)`, `(e-mail de l'éditeur du 14/09)`. Les phrases d'ambiance validées par Hervé ne sont pas recopiées ici : elles vivent dans le fichier d'exemples de la gamme (skill `narration-jeux`), la fiche y renvoie.
Les liens vers d'autres fiches : forme et conditions dans le SKILL, section 4.

## Quand le glossaire change
Une correction de terme cherche toutes les occurrences, partout (skill `glossaire`) : les fiches en font partie, par leur `nom_fr` et par les noms affichés des liens qui les visent. La porte qui le prouve, et ce qu'on fait de chaque ligne du contrôle : SKILL, section 3.

## Exemple [EXEMPLE FICTIF]
```
---
type: personnage
gamme: "Royaume fictif"
nom_en: "Grey Warden"
nom_fr: "Gardien gris"
id_glossaire: "RF-001"
registre: "vouvoie tout le monde, phrases courtes"
premiere_apparition: "carte 12"
statut_fiche: brouillon
tags:
  - univers
---
## En une phrase
Le gardien qui ouvre la campagne (livret de campagne p. 3).
```
