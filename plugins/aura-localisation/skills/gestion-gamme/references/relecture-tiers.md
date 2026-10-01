# Relire la traduction d'un tiers

Hervé relit le lot d'un autre traducteur de la gamme. Le but est double : un texte juste pour
l'éditeur, et un retour qui aide le traducteur à progresser sans le décourager. Ce n'est pas la
vérification de son propre texte avant livraison (skills `qa-coherence` et `relecture-multi-agents`).

## Ce qu'il faut avant de commencer

- Le texte anglais du lot et la traduction livrée.
- Le glossaire de la gamme (skill `glossaire`), la charte typographique (skill `typographie-fr`) et
  les écarts de l'éditeur notés dans sa fiche (skill `brief-editeur`).
- Le brief que le traducteur a reçu : on ne lui reproche pas une consigne qu'il n'a pas eue.

## Méthode

<!-- [I-28] -->
1. **Une passe à la fois, sans sous-agent**, par tranches d'environ 35 000 caractères. Un fichier
   d'état `Livrables/<Projet>/relecture_<lot>_etat.md` note la dernière carte ou page relue, pour
   reprendre après une coupure.
2. **Les contrôles automatiques d'abord** (ils ne consomment rien) : typographie (skill
   `typographie-fr`), termes du glossaire et renvois (skill `qa-coherence`), longueurs (skill
   `controle-longueur`). Leurs constats entrent dans le tableau avec le type qui leur correspond.
3. **La lecture ensuite**, segment par segment contre l'anglais, pour ce qu'aucun script ne voit : le
   sens, la mécanique, le style.
4. **Le fichier du traducteur n'est jamais modifié.** Les corrections vont dans un tableau, et, si
   Hervé le veut, dans une copie `Livrables/<Projet>/<fichier>_relu_v1`.

## Le tableau des corrections

| Réf. | Texte anglais | Traduction livrée | Proposition | Type | Gravité | Commentaire pour le traducteur |
|---|---|---|---|---|---|---|

**Type** (cinq valeurs, toujours une seule) :

- **Sens** : contresens, faux sens, omission, ajout.
- **Terminologie** : terme du glossaire non respecté, terme inventé alors qu'il existe, mot-clé rappelé
  autrement que sa forme standard.
- **Mécanique** : la règle ne se joue plus pareil (facultatif devenu obligatoire, borne changée, « jusqu'à »
  perdu, cible ou moment de l'effet modifié). C'est le type le plus grave à gravité égale.
- **Typographie** : écart à la charte du skill `typographie-fr` ou aux écarts de l'éditeur.
- **Style** : registre, fluidité, voix de l'univers, répétition.

**Gravité** :

- **Bloquant** : la carte ou la règle se joue faux, ou le sens est inversé.
- **Important** : erreur réelle sans effet sur le jeu (terme hors glossaire, faute, typographie).
- **Suggestion** : une autre formulation possible ; le choix du traducteur est défendable. On l'écrit
  comme une proposition, jamais comme une faute.

<!-- [I-34] -->
Les comptes du tableau sont exacts et portent sur tout le lot (« 14 corrections sur 82 cartes, dont
2 bloquantes »), jamais « quelques » ou « la plupart ».

## La synthèse pour le traducteur

<!-- [I-12] -->
Un message court, entre pairs, qu'Hervé relit et envoie lui-même :

1. **Ce qui est réussi, cité concrètement** (deux ou trois passages précis, et pourquoi ils marchent).
2. **Les points récurrents à retenir**, deux ou trois au plus, avec leur nombre (« le mot-clé Exhaust
   rappelé de trois façons différentes sur 6 cartes »). Une erreur isolée ne devient pas une règle.
3. **Les corrections bloquantes**, une par une, avec la raison mécanique.
4. **Les questions ouvertes** : ce qu'Hervé n'a pas tranché et veut voir avec lui.
5. Une phrase de fin qui dit la suite (intégration, prochain lot).

Pas de note chiffrée, pas de jugement sur la personne, aucun code interne, aucune mention d'AURA, de
l'intelligence artificielle ou de l'outil. Le tutoiement ou le vouvoiement suit l'usage d'Hervé avec
cette personne (à lui demander la première fois, puis noté dans le tableau « Équipe » du registre).

## Après la relecture

- Les corrections retenues par Hervé sont intégrées sur la copie ; le tableau des lots du registre passe
  à « Relu » avec la date.
- Une erreur de terminologie répétée par plusieurs traducteurs signale souvent un glossaire peu clair :
  AURA propose de préciser la colonne NOTES ou DÉFINITION MÉCANIQUE du terme (skill `glossaire`).
- Une question de sens qui reste ouverte rejoint `Core/Questions_Editeurs.md` (voir
  `references/coordination.md`, partie 4).

## Exemple [EXEMPLE FICTIF]

<!-- [I-30] -->
| Réf. | Texte anglais | Traduction livrée | Proposition | Type | Gravité | Commentaire pour le traducteur |
|---|---|---|---|---|---|---|
| C044 | You may discard 1 card to draw 2 cards. | Défaussez 1 carte pour piocher 2 cartes. | Vous pouvez défausser 1 carte pour piocher 2 cartes. | Mécanique | Bloquant | « may » rend l'effet facultatif : sans « vous pouvez », le joueur est obligé de défausser. |
| C051 | Move up to 2 spaces. | Déplacez-vous de 1 à 2 cases. | Déplacez-vous de 2 cases maximum. | Mécanique | Bloquant | « up to » inclut 0 : « de 1 à 2 » interdit de rester sur place. |
| C060 | Gain 1 Resolve. | Gagnez 1 Courage. | Gagnez 1 Détermination. | Terminologie | Important | Le glossaire fixe Resolve = Détermination (Confirmé). |
| C072 | The mist parts. | La brume se lève. | La brume se déchire. | Style | Suggestion | Les deux marchent ; « se déchire » garde l'image de l'anglais. À toi de voir. |
