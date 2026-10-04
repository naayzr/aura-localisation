# La lecture par lots — ce qu'on cherche, et comment on le note

> **[EXEMPLE FICTIF]** — toutes les règles, cartes et phrases de ce fichier sont construites pour l'illustration.

La lecture vient **après** les contrôles automatiques : la typographie, les longueurs, les balises, les termes du glossaire, les comptes et l'existence des renvois sont déjà traités par script. La lecture cherche ce qu'aucun script ne voit.

## Avant le premier lot

Charger, pour toute la durée de la lecture :
- la partie utile du glossaire (termes Confirmés et Gelés de la gamme, avec leur genre) ;
- la carte mécanique du jeu, si elle existe (skill `comprehension-regles`) : verbes d'action, états, déclencheurs, faux amis repérés. Sans carte, AURA reconstruit au fil de la lecture un modèle minimal du jeu (phases, actions, ressources) et le note dans le premier rapport ;
- la fiche de l'éditeur : tutoiement ou vouvoiement, charte ;
- les constats des contrôles automatiques, pour ne pas les compter deux fois.

## Les quatre angles, à chaque lot

### 1. La logique de jeu
Lire comme un joueur qui ne connaît que le français : qu'est-ce qui le ferait mal jouer ?
- **La grille mécanique** (skill `traduction-jeux`, point 1) sur chaque règle et chaque effet : facultatif ou obligatoire, bornes, déclencheur, durée, cible, ordre, coût, choix, exception.
- **Les verbes d'action** : chaque terme mécanique (épuiser, défausser, exiler, cibler…) est-il employé toujours dans le même sens ?
- **Les termes que les scripts ne voient pas** : une variante qui n'est jamais entrée au glossaire (« Bouger » quand seul « Déplacer » y figure), et l'accord d'un nom inventé avec le genre déclaré au glossaire (sans genre déclaré : on le signale, on ne le devine pas).
- **Les contradictions** : la règle A dit X, la règle B dit le contraire. Avant de crier à la contradiction, vérifier si le livret pose qu'une carte l'emporte sur la règle générale.
- **Les conditions impossibles** : une condition qui ne peut jamais être vraie.
- **Les cas perdus** : un cas couvert par la version originale (VO) et absent de la traduction.
- **L'ambiguïté créée** : la traduction admet deux lectures là où la VO n'en avait qu'une.

### 2. Le style et le registre
- Tutoiement ou vouvoiement constant, conforme à la fiche éditeur.
- Calques de l'anglais : structures trop littérales qui sonnent faux.
- Ruptures de ton entre des parties traduites à des moments différents.
- Phrases trop longues pour leur usage (une règle doit se lire d'une traite).
- Le texte d'ambiance se juge sur sa voix : en cas de doute, renvoyer au skill `narration-jeux`, sans réécrire ici.

### 3. Le contenu des renvois
Le script a trouvé les renvois et vérifié que les règles visées existent. La lecture juge le **sens** : la règle 5.3 parle-t-elle bien de ce que le texte promet ? Et dans l'autre sens : si la 4.3 renvoie à la 7.1, la 7.1 traite-t-elle du même sujet ?

### 4. Le sens, si la VO est fournie
Rien d'ajouté, rien de perdu, rien d'inversé. Une précision « utile » ajoutée par la traduction est une règle inventée : on la signale.

## Les constats — exemples justes, et deux erreurs corrigées de la v2.0

```
[LOG-01] § 182 (règle 6.1) et carte « Tempête » — la règle 6.1 limite à un déplacement par tour,
         la carte dit « Déplacez-vous deux fois ». Le livret pose-t-il que le texte d'une carte
         l'emporte sur les règles ? Si oui : pas de contradiction. Sinon : question à l'éditeur.
[LOG-02] § 140 (règle 4.4) — « si vous avez plus de 10 jetons » : la règle 2.3 plafonne la réserve
         à 8 jetons. Condition jamais vraie. Comparer à la VO : même chiffre → question à l'éditeur ;
         chiffre différent → erreur de traduction.
[LOG-03] § 230 (fin de partie) — l'égalité n'est pas traitée, ni dans la VO. Question à l'éditeur.
[LOG-04] § 95 (règle 3.2) — « Retirez la carte » pour *Discard* : « retirer » fait penser à une sortie
         définitive du jeu. Employer le terme du glossaire pour *discard*.
[LOG-05] § 151 (règle 5.1) — VO *When a creature you control dies* ; traduction « Lorsqu'une créature
         que vous contrôlez est détruite ». Le déclencheur a changé : dans ce jeu, mourir et être
         détruite sont deux événements. Rendre *dies* par « meurt » ou par le terme du glossaire.
[LOG-06] carte « Second souffle » — VO *You may draw a card* ; traduction « Piochez une carte » :
         un effet facultatif devenu obligatoire. BLOQUANT.
[STY-01] § 40 à § 75 — passage du vouvoiement au tutoiement au chapitre 4 ; la fiche éditeur dit
         vouvoiement.
[STY-02] carte « Crépuscule » (texte d'ambiance) — « Le vieux dieu agite sous la montagne » : calque,
         et verbe sans complément. Proposition : « Le vieux dieu gronde sous la montagne. »
[REF-01] § 160 (règle 5.3) — « voir règle 3.4 » : la 3.4 traite des ressources, pas du déplacement.
         La VO dit aussi 3.4 → question à l'éditeur.
```

Deux exemples de la v2.0 enseignaient l'inverse de ce qu'il faut voir : <!-- [D-21] -->
- Elle recommandait de remplacer « Quand vous perdez une créature » par « Lorsqu'une créature que vous contrôlez est détruite » : c'était changer l'événement déclencheur. La bonne correction suit la VO (LOG-05 ci-dessus).
- Elle tenait pour « jamais vraie » la condition « si vous n'avez pas de jetons » parce que chaque joueur commence avec 3 jetons. Or des jetons qui se dépensent finissent à zéro : la condition est parfaitement possible. Une condition impossible se prouve par une règle qui l'interdit (LOG-02 ci-dessus), pas par la situation de départ.

Les codes `[LOG-01]`, `[STY-01]`, `[REF-01]` servent à Hervé et à la synthèse. Ils ne partent jamais chez l'éditeur : une question à l'éditeur s'écrit en clair, au registre `Core/Questions_Editeurs.md`.

## Le rapport d'un lot

Écrit dans le dossier de relecture sous le nom prévu par le plan (`lot-03.md`), au format commun de `references/rapport-final.md` :

```
RAPPORT lot-03
Fichier : Livrables/<Projet>/<Livret>_FR_v2.docx — lot 3 (§ 176 → § 241)
Constats : 3
Zones non lues : aucune
[LOG-02] § 180 (règle 4.4) — …
[STY-01] § 190 — …
[REF-01] § 212 (règle 5.3) — …
FIN DU RAPPORT
```

- « Constats » = le nombre de lignes qui commencent par `[` : le script de synthèse vérifie que les deux correspondent.
- « Zones non lues » : tout ce qui, dans le lot, n'a pas été lu ou pas pu l'être (tableau en image, légende, encadré, dos de carte, texte dans une forme). « aucune » seulement si c'est vrai.
- `FIN DU RAPPORT` en dernière ligne : un rapport sans elle compte comme incomplet.

## Après chaque lot : `Core/_EN_COURS.md`

Mettre à jour les lignes de la section de ce projet (une section par projet, règle du skill `noyau`), sans réécrire le fichier ni toucher aux autres sections : <!-- [R-31] -->
```
- Relecture — lot traité : lot 3 sur 5 (§ 176 → § 241) — rapport écrit
- Prochaine étape : relecture du lot 4 (dossier Livrables/<Projet>/relecture)
```
Si la conversation devient lourde ou si le quota approche de sa limite, AURA sauvegarde (skill `noyau`) et dit à Hervé où elle reprendra. La reprise relit `Core/_EN_COURS.md` et `PLAN.txt`, puis commence au lot suivant — jamais au début.
