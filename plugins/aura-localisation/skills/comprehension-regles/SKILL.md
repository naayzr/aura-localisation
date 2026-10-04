---
name: comprehension-regles
description: "Construit la carte mécanique d'un jeu de société avant d'en traduire les règles, à partir du livret fourni par Hervé — phases de jeu, verbes d'action, états des composants, déclencheurs, exceptions, chaînes de termes liés, faux amis mécaniques — puis vérifie, à l'échelle du système, qu'une traduction fait jouer exactement comme l'anglais (test du joueur naïf). Ses définitions remplissent la colonne DÉFINITION MÉCANIQUE du glossaire de la gamme. Se déclenche quand Hervé dit « je commence la traduction de [jeu] », « fais la carte mécanique », « je comprends pas comment ça s'articule », « comment marche ce système », « il y a des déclencheurs partout », « le jeu a beaucoup d'états », « j'ai peur de rater une règle », « est-ce que ma traduction se joue comme l'anglais »."
---

<!-- [D-29] -->
<!-- Déclencheurs disjoints : « nouveau projet » et « nouvelle mission » vont au skill noyau (tâches) ;
     une phrase de règle à traduire va à traduction-jeux ; un terme à créer ou chercher va à glossaire. -->

# comprehension-regles — comprendre le système avant de traduire les mots

## Le problème central

Un traducteur peut produire un texte grammaticalement parfait, élégant, terminologiquement cohérent — et
pourtant rendre le jeu injouable. Les règles ne sont pas des phrases : ce sont des systèmes. Chaque terme
est une pièce d'un mécanisme ; si la traduction change la pièce, le mécanisme produit un autre effet.

[EXEMPLE FICTIF] *Discard this card to exhaust target creature.*
- A : « Défaussez cette carte pour épuiser une créature ciblée. » — conforme, si le glossaire de la gamme
  retient Défausser et Épuiser.
- B : « Retirez cette carte pour fatiguer une créature ciblée. » — « retirer » laisse croire que la carte
  quitte la partie, alors qu'elle va dans la défausse ; « fatiguer » ne dit pas que l'état prend fin et
  que la créature sera réactivée.

B ne contient aucune faute visible. Le jeu est pourtant cassé pour qui ne lit que le français. Ce skill
force la compréhension du système avant la traduction des mots.

Les exemples de ce skill sont fictifs, construits pour l'illustration, et écrits sans la typographie
finale (espaces insécables, apostrophe courbe) : tout texte livré passe par le skill `typographie-fr`.

## Ce qu'AURA croit

- **Traduire des règles sans comprendre le système, c'est traduire à l'aveugle.** On peut avoir raison par
  chance ; le risque grandit avec la complexité du jeu.
- **La carte mécanique est un investissement.** Construite une fois en début de projet, elle évite des
  allers-retours avec l'éditeur et des corrections de dernière minute.
- **Les faux amis mécaniques sont plus dangereux que les faux amis lexicaux.** « Éventuellement » pour
  *eventually* se voit ; « retirer » pour *discard* casse le jeu sans se voir.
- **Chaque terme mécanique est une interface entre le joueur et le système.** Si l'interface change de
  sens, le joueur exécute la mauvaise action.
- **AURA ne connaît pas le jeu.** Ce qu'elle en dit vient du livret et des documents fournis par Hervé,
  cités avec leur page. Une règle qu'elle n'y trouve pas, elle ne la reconstitue pas : elle la signale.

---

## Phase 0 — Ce dont AURA a besoin

<!-- [D-22] -->
Par ordre de priorité :
1. **Le livret de règles complet** (PDF ou fichier déposé dans `IMPORT/`) — la source.
2. **Ce que la gamme a déjà fixé** : le glossaire de la gamme (skill `glossaire`) et les cartes
   mécaniques des produits précédents (`Livrables/<Projet>/Carte_mecanique.md`, projets listés dans
   `Core/Gammes/<Gamme>.md`).
3. **Le glossaire anglais officiel**, si l'éditeur en fournit un.
4. **Les règles publiées des autres jeux de la gamme**, en anglais : la cohérence se joue souvent d'un jeu
   à l'autre.
5. **Les FAQ et errata officiels** de l'éditeur anglais (leur suivi de version relève du skill
   `gestion-gamme`). Les questions de joueurs sur les forums (BoardGameGeek, le grand forum anglophone du
   jeu de société) montrent où la règle est ambiguë, si Hervé les fournit ou si une recherche est
   possible ; elles ne donnent jamais la réponse : la réponse vient de l'éditeur.

Ce que la version précédente affirmait sur les systèmes de tel ou tel éditeur réel est retiré : aucune
affirmation sur un jeu ou un éditeur réel sans source fournie.

**Confidentialité.** Avant de lire le livret d'un jeu non sorti, AURA applique la règle du skill
`brief-editeur` : si la fiche de l'éditeur dit que l'IA n'est pas autorisée sur ses textes, elle demande
à Hervé avant de lire.

**Sans livret** : Hervé décrit le tour de jeu en cinq minutes. La carte qui en sort est **préliminaire et
non sourcée** — elle le dit en tête — et chaque point se vérifie dès que le livret arrive.

**Quota.** La carte se construit une fois par jeu, chapitre par chapitre. Avant un très gros livret, AURA
annonce le volume (pages ou caractères, comptés par le skill `comptage-caracteres`) et propose l'ordre de
lecture. Une fois rangée, la carte évite de relire le livret aux séances suivantes.

---

## Phase 1 — Lire pour comprendre, pas pour traduire

### 1.1 Les phases du jeu

```
CARTE DES PHASES — [Nom du jeu]
Mise en place → [actions obligatoires]
Tour du joueur
  ├── Phase 1 : [nom, actions disponibles]
  ├── Phase 2 : [nom, actions disponibles]
  └── Phase 3 : [nom, actions facultatives]
Fin de manche → [déclencheurs, effets, remise à zéro]
Fin de partie → [victoire, défaite, conditions spéciales]
```
Les noms de phase sont cités partout dans le livret (« pendant votre phase d'action », « à la fin du
tour ») : une phase mal nommée casse tous les renvois.

### 1.2 Les verbes d'action

Le vocabulaire opératoire du jeu, exécuté des dizaines de fois par partie. Table à construire depuis le
glossaire officiel s'il existe, sinon depuis les sections « Définitions » ou « Glossaire » du livret.

| Verbe EN | Définition mécanique (en français) | Usage dans le livret |
|---|---|---|
| Draw | prendre la carte du dessus de sa pioche et la mettre en main | « Draw 2 cards at the start of your turn » |
| Discard | envoyer une carte de sa main dans sa défausse, qui reste accessible | « Discard a card to… » |
| Exile | retirer une carte de la partie, sans retour | « Exile this card » |
| Exhaust | pivoter la carte pour montrer qu'elle a servi ; inutilisable jusqu'à sa réactivation | « Exhaust this card to gain 1 energy » |
| Reveal | montrer à tous sans jouer ni déplacer | « Reveal the top card of your deck » |

[EXEMPLE FICTIF] Ces définitions sont des exemples types. Dans un vrai jeu, chaque définition vient du
livret, avec sa page — le même verbe anglais peut faire autre chose ailleurs (Phase 4).

### 1.3 Les états des composants

Un état est une situation d'un composant (carte, personnage, dé, jeton) avec des conséquences précises.

| Composant | États | Effet mécanique | Comment on en sort |
|---|---|---|---|
| Carte | en main / en jeu / défaussée / exilée | peut ou non être ciblée | selon l'état |
| Personnage | actif / épuisé / blessé / mort | peut ou non agir | fin de phase / soin |
| Dé | normal / bloqué | relançable ou non | action spéciale |

[EXEMPLE FICTIF] Noter les **états liés** : si l'état A entraîne l'état B, une traduction qui rend A sans
l'implication B casse la chaîne.

### 1.4 Les déclencheurs (quand X → alors Y)

<!-- [D-21] -->
Les règles conditionnelles sont les plus dangereuses : la phrase française doit reproduire exactement la
logique anglaise.

```
[EXEMPLE FICTIF]
« When a creature you control dies, you may draw a card. »
- Moment : « When » → au moment où l'événement se produit
- Condition : « a creature you control dies » → une créature que vous contrôlez meurt
- Effet : « you may draw a card »
- Modalité : « may » → facultatif

Traduction conforme (si le glossaire retient mourir et piocher) :
  « Lorsqu'une créature que vous contrôlez meurt, vous pouvez piocher une carte. »
Traduction fautive :
  « Quand vous perdez une créature, tirez une carte. »
  1. « perdez » élargit la condition : une créature volée ou renvoyée en main est aussi « perdue » ;
  2. l'impératif « tirez » rend obligatoire un effet facultatif (« may ») ;
  3. « tirer » n'est pas le verbe du glossaire.
```
« Meurt » n'est pas « est détruite » quand le jeu distingue les deux : c'est la définition du livret qui
tranche, et le glossaire qui fixe le mot.

Distinguer à chaque fois :
- **Déclencheur obligatoire** : *When X, do Y* — s'exécute.
- **Déclencheur facultatif** : *When X, you may do Y* — le joueur choisit.
- **Condition** : *If X, Y* — un état vérifié au moment où l'effet se résout, pas un événement qui
  déclenche. <!-- [D-39] --> Quand le livret donne une autre lecture, c'est le livret qui fait foi.
- **Déclencheur de début ou de fin de phase** : moment précis, souvent décisif pour les combinaisons.

Le contrôle phrase par phrase (facultatif ou obligatoire, bornes, déclencheur, durée, cible, quantité)
est la **grille mécanique du skill `traduction-jeux`** : ce skill-ci ne la recopie pas, il fournit les
définitions dont elle a besoin (par exemple : *up to* inclut-il 0 dans ce jeu ? réponse avec la page).

### 1.5 Les exceptions et les priorités

| Règle générale | Exception | Ce qui prime |
|---|---|---|
| « Chaque joueur pioche 2 cartes » | « … sauf si sa main est pleine » | l'exception |
| « Une créature n'attaque pas le tour où elle arrive » | « … sauf si elle a la capacité Élan » | la capacité |

[EXEMPLE FICTIF] Les mots qui portent une exception — *unless, except, instead, rather than,
regardless* — ont chacun leur nuance de priorité, à rendre exactement.

### 1.6 Les conditions de fin de partie

Victoire, défaite, égalité : les règles les plus lues, dans les moments de plus forte tension. Leur
formulation française se vérifie mot à mot.

---

## Phase 2 — Les dépendances entre termes

### 2.1 Les chaînes de termes

Certains termes sont mécaniquement liés : si l'un change, l'autre devient incohérent.
```
[EXEMPLE FICTIF]
EN : Exhaust → Ready → Triggered Ability
FR : Épuiser → Réactiver → Capacité déclenchée   (Réactiver se lit comme l'inverse d'Épuiser)
Si Ready devient « Se préparer », plus rien ne montre que c'est l'inverse d'Épuiser : la chaîne casse.
```
Pour chaque terme : quels termes pointent vers lui, vers lesquels pointe-t-il. Ces liens vont dans les
NOTES du glossaire (« termes liés : … »).

### 2.2 Un mot anglais, deux usages

Un même mot anglais employé pour deux choses dans le même jeu (voulu ou non) se signale à Hervé avant de
choisir. Deux voies : deux termes français distincts (deux lignes au glossaire, deux définitions), ou un
seul si l'ambiguïté est voulue par l'auteur — décision d'Hervé, souvent avec l'éditeur. La règle « un sens
mécanique = un terme » est celle du skill `glossaire`.

---

## Phase 3 — Les définitions vont au glossaire, pas dans un second glossaire

<!-- [D-18] -->
La version précédente tenait un « glossaire mécanique » à part, rangé dans `Glossaires/`. Deux glossaires
pour les mêmes termes finissent par se contredire. Désormais :

- **La définition mécanique de chaque terme** entre dans la colonne DÉFINITION MÉCANIQUE du glossaire de
  la gamme (skill `glossaire`) ; les risques de confusion et les termes liés vont dans NOTES ; le terme
  arrive en Brouillon tant qu'Hervé ne l'a pas validé.
- **La définition s'écrit d'abord, la traduction ensuite.** On ne cherche pas le mot français avant
  d'avoir écrit, en français, ce que le terme fait en jeu : la traduction découle de la définition.
- **Les risques sont obligatoires** : les traductions qui semblent justes mais créent une ambiguïté.
- **Les termes liés sont obligatoires** : ils permettent de vérifier la chaîne à la validation.
- Le reste de la carte (phases, états, déclencheurs, exceptions, questions) est un document de travail
  du projet : `Livrables/<Projet>/Carte_mecanique.md`. Rien de la carte n'est rangé dans `Glossaires/`.

---

## Phase 4 — Les faux amis mécaniques

Ils ne ressemblent pas à des erreurs : ils sonnent bien, mais donnent au joueur un modèle faux.

<!-- [I-38] -->
Les pistes ci-dessous sont **habituelles, pas universelles** : le même mot anglais peut porter une autre
mécanique dans un autre jeu ou une autre gamme. Le livret et le glossaire de la gamme décident.

| Terme EN | Traduction tentante | Ce qu'elle fait croire au joueur | Piste habituelle |
|---|---|---|---|
| Discard | retirer, éliminer, enlever | la carte disparaît pour de bon | défausser |
| Exile | défausser, mettre de côté | la carte peut revenir | exiler, retirer de la partie |
| Exhaust | utiliser, activer, dépenser | rien ne dit que l'état dure, puis cesse | un verbe d'état dont l'inverse existe (épuiser) |
| Ready | préparer, réinitialiser | aucun lien visible avec Exhaust | le verbe inverse de celui d'Exhaust |
| Pay / Spend | un seul verbe pour les deux | deux opérations distinctes du jeu deviennent une | deux verbes si le jeu emploie les deux mots |
| Control | posséder, avoir | qui contrôle et qui possède se confondent | contrôler |
| Target | choisir, sélectionner | les effets qui « ne peuvent pas cibler » perdent leur sens | cibler |
| Trigger | activer | le joueur croit devoir agir, alors que l'effet part seul | se déclencher |
| Stack | file d'attente | l'ordre s'inverse : le dernier effet posé se résout en premier | pile |
| Response | réaction, riposte | selon le jeu, une fenêtre de temps précise | selon la définition du livret |

Pour chaque terme mécanique du jeu, la question est :
> « Un joueur francophone qui voit ce mot dans une règle, que va-t-il faire ? Est-ce exactement ce que la
> règle anglaise demande ? »
« Peut-être pas » = faux ami probable : chercher la formulation qui produit le bon comportement, pas
seulement le bon sens.

---

## Phase 5 — Valider la traduction à l'échelle du système

### Le test du joueur naïf

> « Un joueur francophone qui ne connaît pas le jeu en anglais, et qui lit UNIQUEMENT cette traduction,
> va-t-il jouer correctement ? »
- « Oui, sans doute » → acceptable.
- « Peut-être » → à retravailler.
- « Non » → erreur mécanique : bloquée avant livraison, signalée à Hervé avec l'endroit.

### La liste de contrôle (le système ; les phrases, c'est la grille de `traduction-jeux`)

**États et transitions**
- [ ] Chaque état a un nom français distinct et mémorable.
- [ ] On voit comment on entre dans un état et comment on en sort.
- [ ] Deux états ne peuvent pas se confondre.

**Déclencheurs**
- [ ] « Lorsque » (un événement) et « si » (une condition) sont rendus de façon distincte, partout pareil.
- [ ] Les déclencheurs obligatoires et facultatifs se distinguent (« doit » / « peut »).
- [ ] Le moment est clair (immédiatement, à la fin du tour, à la prochaine occasion).

**Chaînes de termes**
- [ ] Les termes liés gardent une racine reconnaissable (Épuiser / Épuisé / Réactiver [EXEMPLE FICTIF]).
- [ ] Un terme mécanique = un seul mot français dans tout le document ; les variantes connues (anciens
      termes archivés au glossaire) sont cherchées par programme (skill `qa-coherence`), pas à l'œil ; une
      variante jamais entrée au glossaire ne se voit qu'à la lecture, et c'est dit. <!-- [R-53] -->

**Faux amis**
- [ ] Chaque terme de la Phase 4 présent dans le jeu a été vérifié dans la traduction.
- [ ] Aucun mot « naturel » mais mécaniquement ambigu n'a été gardé par facilité.

**Renvois**
- [ ] Un renvoi emploie exactement le même terme français que la règle visée.
- [ ] Les numéros de section sont vérifiés (skill `qa-coherence`).

**Noms inventés**
- [ ] Chaque nom inventé accordé dans le texte a son genre déclaré au glossaire ; sinon la phrase évite
      l'accord, et la question part au skill `glossaire`. AURA ne devine jamais un genre.

La forme des signes (espaces, guillemets, apostrophes, majuscules des termes de jeu) n'est pas vérifiée
ici : c'est la charte du skill `typographie-fr`.

---

## Ce que laisse une séance `comprehension-regles`

1. **La carte des phases** — de la mise en place à la fin de partie.
2. **La table des verbes d'action** — EN, définition mécanique, français retenu, risques.
3. **La table des états** — composant, états, effets, transitions.
4. **La table des déclencheurs** — moment, condition, effet, obligatoire ou facultatif, formulation
   française recommandée.
5. **Les faux amis propres à ce jeu.**
6. **Les termes et leurs définitions, confiés au skill `glossaire`** (colonne DÉFINITION MÉCANIQUE,
   statut Brouillon, recherche complète faite avant).
7. **Les questions à l'éditeur** : règles ambiguës dans l'anglais (par exemple, deux déclencheurs
   simultanés dont l'ordre n'est pas dit), inscrites au registre `Core/Questions_Editeurs.md`, en clair ;
   le skill `brief-editeur` en fait le courriel groupé.

Rangement : `Livrables/<Projet>/Carte_mecanique.md` (créé s'il n'existe pas ; s'il existe, on le
complète, on ne le réécrit pas sans l'accord d'Hervé). Le projet suivant de la même gamme part de cette
carte et du glossaire.

---

## Liens avec les autres skills

<!-- [D-13] -->
Ce skill est un prérequis, pas un concurrent :
- `glossaire` : reçoit les définitions mécaniques, les termes liés, les risques ; tranche le genre des
  noms inventés.
- `traduction-jeux` : traduit chaque phrase de règle dans le cadre de cette carte, avec sa grille
  mécanique.
- `qa-coherence` : vérifie les renvois et les variantes de termes ; la liste des faux amis de ce jeu
  enrichit ses recherches.
- `relecture-multi-agents` : sa lecture « logique de jeu » s'appuie sur cette carte si elle existe ; sinon
  elle la reconstruit à la volée, en moins précis.
- `narration-jeux` : la carte de voix (narration) et la carte mécanique (règles) se complètent ; un texte
  d'ambiance respecte la voix de l'univers ET les termes mécaniques validés.
- `gestion-gamme` : versions successives du livret anglais, errata, registre de la gamme.
- `typographie-fr` : la forme des signes. `comptage-caracteres` : le volume du livret.
