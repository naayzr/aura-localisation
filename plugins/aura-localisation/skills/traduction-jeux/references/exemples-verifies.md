# Exemples vérifiés, ligne par ligne <!-- [D-21] -->

> **[EXEMPLE FICTIF]** — toutes les phrases de ce fichier sont construites pour l'illustration. Elles ne viennent d'aucun jeu publié et leurs termes d'aucun glossaire réel. Dans un vrai projet, chaque terme vient du glossaire de la gamme (skill `glossaire`).

Chaque exemple passe la grille mécanique du skill (point 1). Les erreurs de la v2.0 sont gardées ici, nommées, parce qu'elles montrent exactement ce que la grille doit attraper.

VO = version originale anglaise. Légende : ✓ gardé · ✗ changé (option rejetée) · ? à vérifier dans le livret ou à demander.

---

## 1. Une borne haute qui devient une fourchette

**VO** : *Move up to 3 spaces.*

| Proposition | Facultatif / obligatoire | Bornes | Verdict |
|---|---|---|---|
| « Déplacez-vous de 1 à 3 cases. » (v2.0) | ✓ | ✗ minimum 1 ajouté : *up to* va en général de 0 à 3 | rejetée |
| « Déplacez-vous de 3 cases maximum. » | ✓ | ✓ au plus 3, pas de minimum ajouté | retenue |

? Si le livret définit *up to* autrement, c'est sa définition qui gouverne (carte mécanique, skill `comprehension-regles`).

## 2. Un « may » qui devient une obligation pendant la compression

**VO** : *You may draw a card.* — le champ déborde, il faut gagner des caractères.

| Proposition | Caractères | Facultatif / obligatoire | Verdict |
|---|---|---|---|
| « Vous pouvez piocher une carte. » | 30 | ✓ | de départ |
| « Piocher 1 carte. » (v2.0, annoncée « 22 → 15 ») | 16 | ✗ devenu obligatoire | rejetée — et le compte de départ était faux (29 sans le point, pas 22) |
| « Vous pouvez piocher 1 carte. » | 28 | ✓ | retenue |
| Forme courte du facultatif prévue par la charte de l'éditeur | selon la charte | ✓ | retenue si la charte en a une |

Les nombres sont comptés espaces et point final compris. Un compte qui part dans une discussion avec l'éditeur vient du skill `comptage-caracteres` ou `controle-longueur`, jamais d'un calcul de tête.

## 3. Un choix ambigu tranché en silence, et un « may » perdu

**VO** : *You may discard a card to gain 2 gold or draw 2 cards.*

| Proposition | Facultatif | Coût → effet | Choix | Verdict |
|---|---|---|---|---|
| « Défaussez une carte. Choisissez ensuite : gagnez 2 pièces d'or, ou piochez 2 cartes. » (v2.0) | ✗ | lecture A imposée sans le dire | ✗ | rejetée |
| Lecture A : « Vous pouvez défausser une carte. Si vous le faites, choisissez : gagnez 2 pièces d'or, ou piochez 2 cartes. » | ✓ | ✓ la défausse paie les deux effets | ✓ | si le jeu confirme A |
| Lecture B : « Vous pouvez, au choix : défausser une carte pour gagner 2 pièces d'or, ou piocher 2 cartes. » | ✓ | ✓ la défausse ne paie que l'or | ✓ | si le jeu confirme B |

? Rien dans le jeu ne départage → question à l'éditeur, au registre `Core/Questions_Editeurs.md`.

## 4. Une règle ajoutée pour « préciser »

**VO** : *Units cannot move through spaces containing enemy pieces unless they have the Scout ability.*

| Proposition | Négation / exception | Rien d'ajouté | Verdict |
|---|---|---|---|
| « Une unité ne peut pas traverser ni s'arrêter sur une case occupée par une pièce ennemie. Exception : une unité possédant la capacité Éclaireur peut traverser ces cases, mais ne peut pas s'y arrêter. » (v2.0) | ✗ | ✗ deux règles inventées (l'arrêt interdit, l'exception à l'exception) | rejetée |
| « Une unité ne peut pas traverser une case occupée par une pièce ennemie, sauf si elle possède la capacité Éclaireur. » | ✓ | ✓ | retenue |

? « Peut-on s'arrêter sur une telle case ? » — la phrase ne le dit pas : chercher dans le livret, sinon question à l'éditeur.

## 5. « Chaque manche » qui devient « votre manche »

**VO** : *At the start of each round, you gain 1 resource.*

| Proposition | Déclencheur | Cible | Verdict |
|---|---|---|---|
| « Au début de votre manche, gagnez 1 ressource. » (v2.0) | ✗ *each round* devenu « votre manche » | ✓ | rejetée |
| Règle générale : « Au début de chaque manche, chaque joueur gagne 1 ressource. » | ✓ | ✓ tous les joueurs | retenue si le texte s'adresse à tous |
| Effet de carte : « Au début de chaque manche, gagnez 1 ressource. » | ✓ | ✓ le propriétaire | retenue si c'est une carte ou un pouvoir |

## 6. « Meurt » n'est pas « est détruite »

**VO** : *When a unit you control dies, draw a card.*

| Proposition | Déclencheur | Verdict |
|---|---|---|
| « Lorsqu'une unité que vous contrôlez est détruite, piochez une carte. » (forme proposée par la v2.0 dans ses exemples de relecture) | ✗ dans un jeu qui distingue mourir, être détruite, être sacrifiée, être vaincue, ce sont des événements différents | rejetée |
| « Quand une unité que vous contrôlez meurt, piochez une carte. » — ou le terme que le glossaire a fixé pour *dies* | ✓ | retenue |

## 7. Un tour qui devient une manche

**VO** : *Until the end of the round, your units get +1 Strength.*

| Proposition | Durée | Cible | Verdict |
|---|---|---|---|
| « Jusqu'à la fin du tour, vos unités gagnent +1 en Force. » | ✗ *round* (manche) rendu par « tour » | ✓ | rejetée, sauf si le glossaire du jeu traduit *round* par « tour » |
| « Jusqu'à la fin de la manche, vos unités ont +1 en Force. » | ✓ | ✓ | retenue |

## 8. Exemples justes de la v2.0, gardés

| VO | Traduction | Pourquoi elle passe |
|---|---|---|
| *Each player takes 3 resource tokens.* | « Chaque joueur prend 3 jetons Ressource. » | obligatoire, exactement 3, chaque joueur |
| *You may discard any number of cards.* | « Vous pouvez défausser autant de cartes que vous le souhaitez. » | facultatif, de 0 à toutes |
| *Gain 2 Gold, then draw a card.* | « Gagnez 2 Or, puis piochez une carte. » | obligatoire, ordre gardé par « puis » |
| *You cannot perform this action more than once per turn.* | « Une fois par tour maximum. » | au plus 1, par tour |
| *In order to gain 2 Gold,* | « Pour gagner 2 Or, » | aucune mécanique touchée, mots vides retirés |

La majuscule des termes (« Ressource », « Or ») suit la charte de l'éditeur (skill `typographie-fr` et fiche éditeur), pas une règle de ce skill.
