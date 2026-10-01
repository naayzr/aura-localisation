---
name: relecture-multi-agents
description: "Relecture COMPLÈTE d'un texte traduit de jeu de société avant livraison (chapitre, livret de règles, lot de cartes) : contrôles automatiques par script (typographie, longueurs et balises, glossaire, comptage, renvois), puis lecture par lots suivie dans Core/_EN_COURS.md (logique de jeu, style, sens), puis synthèse classée bloquant, important, mineur, qui compte les rapports réellement rendus, nomme ce qui n'a pas été vérifié, donne le verdict de livraison et les questions pour l'éditeur. Par défaut sans agent parallèle ; plusieurs relecteurs en parallèle seulement sur demande expresse d'Hervé, après annonce du nombre d'agents, de la taille des lots et de la consommation de son quota. À utiliser quand Hervé dit « relis tout le texte avant livraison », « relecture complète », « est-ce que je peux livrer ? », « dernière passe avant d'envoyer », « fais la relecture à plusieurs relecteurs ». Pas pour un seul point (qa-coherence) ni une seule phrase (traduction-jeux)."
---

# relecture-multi-agents — la relecture complète avant livraison

> Les exemples de ce skill sont des **[EXEMPLE FICTIF]** : règles, cartes et constats construits pour l'illustration, tirés d'aucun jeu publié.

## Ce skill, ou un autre <!-- [D-29] -->

Ce skill relit **tout un texte** — un chapitre, un livret, un lot de cartes — pour décider s'il peut partir. Il ne se lance pas pour une phrase ou un point isolé :

| Hervé demande | Skill |
|---|---|
| « relis tout avant livraison », « relecture complète », « est-ce que je peux livrer ? », « dernière passe » | `relecture-multi-agents` (ce skill) |
| « vérifie ce renvoi », « ce symbole est-il le bon ? », « cherche toutes les occurrences de… » | `qa-coherence` |
| « relis cette phrase », « cette formulation te va ? » | `traduction-jeux` (ou `narration-jeux` pour un texte d'ambiance) |
| « vérifie juste la typo » / « juste les longueurs » / « juste les termes » | `typographie-fr` / `controle-longueur` / `glossaire` |

Un « relis » seul ne suffit pas à lancer une relecture complète : si la portée n'est pas claire, AURA demande « tout le texte, ou ce passage ? ».

## Ce qu'Hervé obtient

1. **Un rapport de synthèse unique**, classé en trois niveaux : BLOQUANT, IMPORTANT, MINEUR — plus les questions pour l'éditeur.
2. **Chaque problème localisé** (chapitre, règle, carte, repère dans le fichier) avec une correction proposée pour les bloquants et les importants.
3. **La preuve de ce qui a été vérifié** : combien de contrôles et de lectures étaient prévus, combien ont réellement rendu leur rapport, un extrait de chacun — et ce qui n'a **pas** été vérifié, nommé en toutes lettres.
4. **Un verdict** : OK À LIVRER, CORRECTIONS REQUISES, ou VÉRIFICATION INCOMPLÈTE.

---

## Deux façons de relire — et laquelle par défaut <!-- [D-03] -->

**La relecture standard est la règle.** Elle se fait **sans aucun agent parallèle** : les scripts d'abord (ils ne coûtent presque rien), puis AURA lit elle-même le texte, lot par lot. Elle tient sur n'importe quel volume — de 50 000 à 1,5 million de caractères — parce qu'aucune lecture ne prend le texte entier d'un coup, et elle reprend où elle s'était arrêtée après une coupure (conversation pleine, quota atteint).

**La relecture à plusieurs relecteurs en parallèle est l'exception.** Elle n'a lieu que si Hervé la demande **expressément** (« fais-la à plusieurs relecteurs »). « Relis tout » ou « vérifie tout » ne sont pas des demandes de relecteurs parallèles. Chaque relecteur consomme le quota de son abonnement pour lui-même : voir le point « Relecteurs en parallèle » ci-dessous.

Pourquoi : la v2.0 lançait 5 lectures intégrales et une synthèse dès qu'Hervé disait « relis ». En français, on compte de l'ordre de 3 à 4 caractères par jeton (l'unité dans laquelle se mesure la lecture d'une IA) : un texte de 300 000 caractères représente déjà 75 000 à 100 000 jetons par lecture, soit plusieurs centaines de milliers pour une seule passe à six. Un texte de 1,5 million de caractères dépasse ce qu'une seule lecture peut tenir. Les chiffres exacts du quota ne sont pas publiés ; AURA annonce des ordres de grandeur, jamais un coût précis.

---

## Étape 0 — Préparer (une fois par relecture)

1. **La copie de travail** : on relit la dernière version dans `Livrables/<Projet>/` (`_v2`, `_v3`…), jamais l'original de l'éditeur. Avant de lancer les scripts, AURA applique la règle « Les programmes et le dossier d'Hervé » du skill `noyau` : fichier glissé si le programme ne voit pas le dossier, et le plan (`PLAN.txt`) comme les rapports réécrits par AURA dans `Livrables/<Projet>/relecture/` — un fichier laissé sur la machine du programme disparaît avec la tâche.
2. **Les références** : le glossaire de la gamme (`Glossaires/Glossaire_<Gamme>.xlsx`), la fiche de l'éditeur (`Core/Editeurs/<Éditeur>.md` : charte, registre), la carte mécanique du jeu si elle existe (skill `comprehension-regles`), la version originale (VO) si Hervé l'a.
3. **Les portes de livraison** dans `Core/_EN_COURS.md` (règle du skill `noyau`), si elles ne sont pas déjà écrites.
4. **Le plan, écrit avant de commencer** — avec le script `lots.py` du dossier `scripts/` de ce skill :
   ```
   python3 scripts/lots.py <fichier> --plan Livrables/<Projet>/relecture
   ```
   Il découpe le texte en lots de 30 000 caractères au plus (coupés de préférence avant un titre), affiche l'ordre de grandeur de la lecture, et écrit `relecture/PLAN.txt` : la liste des rapports attendus (5 contrôles automatiques + 1 rapport par lot). **Le plan ne se réécrit pas après coup** : c'est lui qui permettra de compter, à la fin, ce qui a vraiment été fait. Une nouvelle relecture prend un nouveau dossier (`relecture-2`).
   La relecture standard consomme aussi du quota : au-delà de quelques lots, AURA dit à Hervé, avant de commencer, le nombre de lots et l'ordre de grandeur lu, et lui propose de commencer par les parties les plus risquées (règles avant texte d'ambiance, chapitres modifiés depuis la dernière relecture).
5. **`Core/_EN_COURS.md`** reçoit trois lignes (mises à jour, sans réécrire le fichier) : le fichier relu, le dossier de relecture, « Lot traité : 0 sur N ».

## Étape 1 — Les contrôles automatiques (scripts, quasiment sans coût)

Chacun est fait par le skill qui en a la règle et le script ; ce skill ne recopie aucune de leurs règles. <!-- [D-20] -->

| Rapport attendu | Contrôle | Skill |
|---|---|---|
| `controle-typographie` | espaces insécables, guillemets, apostrophes, points de suspension, majuscules — selon la charte de l'éditeur | `typographie-fr` |
| `controle-longueur` | longueur par champ, débord, balises et icônes identiques entre VO et traduction | `controle-longueur` |
| `controle-glossaire` | le glossaire lui-même est sain (contrôle `controle_glossaire` du skill `glossaire`) ; dans le texte, les termes anglais du glossaire restés en anglais et les formes archivées (refusées) encore présentes (script `chercher.py` du skill `qa-coherence`, avec `--colonne EN`, puis `--colonne FR --si STATUT=Archivé --racine`) | `glossaire` + `qa-coherence` |
| `controle-comptage` | nombre de segments, cartes et caractères, VO et traduction (« 340 cartes en anglais, 338 en français ») | `comptage-caracteres` |
| `controle-renvois` | renvois internes, numéros de règle, règles de la VO absentes, renvois de page | `qa-coherence` (son script `renvois.py`) |

Ce qu'aucun script ne fait encore, et qui reste à la lecture par lots (étape 2) : repérer une variante qui n'est jamais entrée au glossaire (« Bouger » quand seul « Déplacer » y figure), et vérifier les accords d'un nom inventé contre le genre déclaré au glossaire.

**Avant de croire ces contrôles**, AURA les essaie sur une copie sabotée : un court extrait du texte réel où elle glisse exprès 3 fautes connues ; chaque passe doit retrouver la sienne. La règle et son pourquoi sont dans le skill `noyau` (règles de travail). Les scripts qui ont un essai intégré (`--auto-test`) le passent aussi. Le résultat s'écrit dans la synthèse (« essai sur copie sabotée : 3 fautes glissées, 3 retrouvées »).

**Chaque contrôle laisse un rapport** dans le dossier de relecture, au format de `references/rapport-final.md` (point 1) : le résultat réel du script, recopié, pas résumé. **Un contrôle qui n'a pas pu tourner n'a pas de rapport** — jamais un rapport écrit « de mémoire » à sa place.

## Étape 2 — La lecture par lots (ce qu'aucun script ne voit)

AURA lit les lots **l'un après l'autre**, dans l'ordre du plan. Pour chaque lot, quatre angles, détaillés avec leurs pièges dans `references/lecture-par-lots.md` :
- **la logique de jeu** : le test du joueur qui ne lit que le français ; facultatif ou obligatoire, bornes, déclencheurs, durées, cibles (la grille du skill `traduction-jeux`) ; contradictions entre règles ; cas couverts par la VO et perdus ;
- **le style et le registre** : tutoiement ou vouvoiement constant, calques de l'anglais, ruptures de ton ;
- **le contenu des renvois** : la règle visée parle-t-elle de ce que le texte promet ? (le script a trouvé les renvois, la lecture juge leur sens) ;
- **le sens**, si la VO est fournie : rien d'ajouté, rien de perdu.

Après chaque lot :
1. le rapport `lot-NN.md` est écrit dans le dossier de relecture, terminé par `FIN DU RAPPORT` ;
2. `Core/_EN_COURS.md` passe à « Lot traité : N sur M », prochaine étape « lot N+1 » ;
3. si la conversation devient lourde ou si le quota approche de sa limite : sauvegarde (skill `noyau`), et la relecture reprend plus tard au lot suivant, dans une nouvelle conversation, à partir de `Core/_EN_COURS.md` et du plan.

## Relecteurs en parallèle — seulement sur demande expresse <!-- [D-03] -->

Quand Hervé demande expressément une relecture « à plusieurs relecteurs » :
1. **AURA prépare le plan** avec le nombre de relecteurs : `python3 scripts/lots.py <fichier> --relecteurs 3 --plan Livrables/<Projet>/relecture`. Les angles par défaut sont la logique de jeu, le style, les renvois ; les contrôles automatiques de l'étape 1 restent faits par script, jamais par un relecteur.
2. **AURA annonce, avant de lancer quoi que ce soit** : le nombre de relecteurs en même temps, le nombre total de lancements (relecteurs × lots), la taille des lots, le volume lu, et que **cela consomme son quota d'abonnement** (chaque relecteur compte pour lui-même). Texte de l'annonce : `references/relecteurs-paralleles.md`.
3. **Plus de 3 lancements au total : AURA attend son accord explicite.** Jusqu'à 3, elle lance après l'annonce. (Plafond et ordre « fichiers, puis scripts, puis agents » : skill `noyau`.)
4. Chaque relecteur reçoit un lot, un angle, les références de l'étape 0 et la consigne d'écrire son rapport dans le dossier de relecture. Consignes complètes : `references/relecteurs-paralleles.md`.
5. **Si la session ne permet pas de lancer des relecteurs séparés**, AURA le dit et fait la relecture standard. Elle n'écrit jamais elle-même des rapports présentés comme ceux de relecteurs qui n'ont pas existé.

## Étape 3 — La synthèse : compter avant de conclure <!-- [I-29] -->

**Avant toute synthèse, AURA compte les rapports réellement rendus** :
```
python3 scripts/rapports.py Livrables/<Projet>/relecture
```
Le script relit `PLAN.txt` et, pour chaque rapport prévu, dit s'il est complet, incomplet, vide ou manquant ; il en sort un extrait et les zones non lues. Son essai intégré (`rapports.py --auto-test`) vérifie qu'il voit bien un rapport manquant, un incomplet et un vide.

Les règles de la synthèse, sans exception :
1. **La première ligne dit le compte** : « Rapports prévus : 10 — rendus complets : 10 sur 10. »
2. **Un extrait de chaque rapport rendu est cité** (sa première ligne de constat, ou « 0 constat »). Une voix qu'on ne peut pas citer n'a pas parlé.
3. **Une voix manquante ne se comble jamais.** Ni par déduction, ni par « ça avait l'air propre », ni en écrivant le rapport à la place du contrôle absent. On relance le contrôle, ou on écrit ce qui manque, avec la phrase que donne le script : « **la typographie n'a pas été vérifiée** » — plutôt qu'un faux feu vert.
4. **Les zones non lues sont nommées** (tableaux, légendes, dos de cartes, encadrés, ou ce que les rapports déclarent). Un rapport à « 0 constat » sur un gros volume est suspect tant que l'essai sur copie sabotée n'a pas été fait (règle du skill `noyau`).
5. **Puis seulement** : regrouper les doublons (un même problème vu par deux angles = priorité renforcée), relier les constats liés (un terme, une règle contradictoire, un renvoi cassé qui forment un seul nœud), classer par sévérité, séparer les erreurs de la traduction des erreurs de la VO.

**Le verdict.**
- **OK À LIVRER** : seulement si `rapports.py` dit « tous les rapports prévus sont rendus », s'il n'y a aucun bloquant, et si chaque porte de livraison de `Core/_EN_COURS.md` est cochée avec son chiffre.
- **CORRECTIONS REQUISES** : au moins un bloquant, ou une porte non tenue.
- **VÉRIFICATION INCOMPLÈTE** : au moins un rapport manquant ou incomplet — avec la liste exacte de ce qui n'a pas été vérifié. Jamais « OK » dans ce cas, même avec des réserves.

**La sévérité.**

| Niveau | Critère | Exemple [EXEMPLE FICTIF] |
|---|---|---|
| **BLOQUANT** | rend le jeu injouable ou incompréhensible | deux règles contradictoires, effet facultatif devenu obligatoire, renvoi vers une règle absente |
| **IMPORTANT** | dégrade nettement l'expérience | terme incohérent d'un chapitre à l'autre, calque lourd, vouvoiement qui devient tutoiement |
| **MINEUR** | qualité, sans effet sur le jeu | coquille isolée, variante de style |

Les erreurs de la VO vont au registre `Core/Questions_Editeurs.md`, écrites en clair (sans code interne) ; le skill `brief-editeur` en fait le courriel. Format complet du rapport final, avec un exemple : `references/rapport-final.md`.

---

## Quand AURA propose une relecture complète

AURA **propose** — Hervé décide :
- avant toute livraison d'un texte de plus de 50 000 caractères ;
- vers 70 % d'un très gros volume (plus de 300 000 caractères), pour corriger une dérive tôt ;
- après l'intégration des retours d'un relecteur (ses changements ont-ils introduit des incohérences ?) ;
- après une longue interruption du projet (le style a pu dériver).

Ce qu'il faut fournir : le texte (ou la partie à relire), et c'est tout — le glossaire, la fiche éditeur et la carte mécanique sont dans le dossier HERVÉ WORLD ; AURA les charge.

## Ce que ce skill ne fait pas

- Il ne traduit pas : `traduction-jeux`, `narration-jeux`.
- Il ne crée ni ne modifie le glossaire : `glossaire`.
- Il ne réécrit pas les règles des autres skills : typographie (`typographie-fr`), longueurs et balises (`controle-longueur`), comptage (`comptage-caracteres`).
- Il n'envoie rien à l'éditeur : les questions vont au registre, le courriel est un brouillon de `brief-editeur`.
- Il ne corrige pas le texte de lui-même : il signale et propose ; Hervé corrige, ou valide les corrections, sur une nouvelle version (`_v3`) — jamais sur l'original.
