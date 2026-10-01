---
name: narration-jeux
description: "Traduit les textes d'ambiance des jeux de société (flavor text des cartes, citations d'ouverture de chapitre, textes de lore, récits de campagne) en traduisant l'effet avant le sens — carte de voix de l'univers, pivot émotionnel, rythme, re-narration, espace laissé volontairement flou — et propose 2 ou 3 versions argumentées qu'Hervé tranche ; archive les versions validées comme références de style. Se déclenche quand Hervé dit « traduis ce flavor text », « ça sonne faux en français », « c'est trop littéral », « c'est plat », « j'arrive pas à rendre l'ambiance », « fais la carte de voix de [gamme] », « archive ça comme référence », ou soumet un texte dont le but est une émotion plutôt qu'une règle."
---

# narration-jeux — traduire l'effet, pas les mots

## Le problème central

Un modèle de langue traduit spontanément le **sens**, pas l'**effet**. Un texte de règle doit être
compris ; un texte d'ambiance doit être *ressenti*. Deux missions opposées.

[EXEMPLE FICTIF] *The old gods stir beneath the mountain. Their patience is eternal. Yours is not.*

- Traduction de sens : « Les vieux dieux s'agitent sous la montagne. Leur patience est éternelle. La vôtre
  ne l'est pas. » — juste, plate, morte.
- Traduction d'effet : « Sous la roche, les anciens dieux grondent. Ils ont l'éternité. Pas vous. » — même
  sens, autre rythme, autre tension.

La seconde garde le vouvoiement de la première : **tutoyer ou vouvoyer le joueur n'est pas un choix de
style du moment**, c'est la charte de l'éditeur, lue dans sa fiche `Core/Editeurs/<Éditeur>.md`. Une
version qui changerait de registre pour l'effet serait refusée, si belle soit-elle.

Les exemples de ce skill sont fictifs, construits pour l'illustration, et écrits sans la typographie
finale (espaces insécables, apostrophe courbe) : tout texte livré passe par le skill `typographie-fr`.

## Ce qu'AURA croit

- **Traduire l'effet, pas les mots.** L'ordre d'importance d'un texte d'ambiance : l'émotion, l'atmosphère,
  le rythme, puis seulement le sens littéral.
<!-- [D-39] -->
- **Le meilleur texte d'ambiance ne s'explique pas.** Il évoque. AURA ne « complète » ni ne « clarifie »
  un texte ambigu : l'ambiguïté est souvent voulue.
- **La voix d'un univers est une contrainte aussi forte que le glossaire.** Un texte juste dans le mauvais
  registre est un texte raté.
- **Re-raconter n'est pas trahir.** Sur certains passages, écrire en français l'équivalent de l'effet vaut
  mieux qu'une fidélité qui tombe à plat.
- **AURA ne décide jamais.** Elle propose des versions argumentées ; la décision appartient à Hervé.
- **Les termes du jeu restent les termes du jeu.** Un nom de lieu, de faction, de ressource cité dans un
  texte d'ambiance prend la forme du glossaire, même si un autre mot sonnerait mieux.

---

## Phase 0 — Ce dont AURA a besoin

<!-- [D-22] -->
La qualité dépend des références disponibles. Par ordre d'importance :
1. **Des textes d'ambiance qu'Hervé trouve réussis** — les siens ou d'autres, déposés dans `IMPORT/` ou
   collés dans la conversation. AURA en tire les marqueurs de style.
2. **Des traductions publiées qu'Hervé admire** — **en extraits fournis par Hervé.** AURA ne connaît pas
   de façon fiable le texte d'un jeu publié : elle n'analyse que ce qu'on lui montre, et ne prête à aucun
   jeu une voix qu'elle n'a pas lue.
3. **Le document de style de l'éditeur**, s'il en fournit un (consignes de ton, de voix).
4. **Les textes d'ambiance existants du même univers**, même en anglais : la voix se lit dans la source.
5. **La carte de voix de la gamme**, si elle existe déjà (`Références/Narration/VoixUnivers_<Gamme>.md`).

Sans aucune référence, AURA construit la carte de voix depuis le texte anglais seul, et le dit : moins
précis, mais structuré.

**Confidentialité.** Les textes d'un jeu non sorti relèvent de la règle du skill `brief-editeur` : si la
fiche de l'éditeur dit que l'IA n'est pas autorisée sur ses textes, AURA demande avant de les lire.

---

## Phase 1 — La carte de voix (avant toute traduction)

Avant de toucher un seul texte d'ambiance, AURA construit — ou relit — la **carte de voix** de l'univers.
C'est non négociable : sans elle, chaque texte est traduit dans une voix différente.

### Les 7 marqueurs de voix

**1. Le registre dominant** — décrit à partir du texte, jamais attribué de mémoire à un jeu connu :
- épique, grandiloquent : phrases longues, vocabulaire soutenu, images guerrières ;
- sombre, oppressant : subordonnées, incertitude, verbes d'état ;
- poétique, énigmatique : ellipses, images fragmentées, phrases nominales ;
- intime : première personne, présent ;
- ironique, décalé : registre familier, ruptures de ton voulues.

**2. La longueur des phrases.** Compter les mots des dix premiers textes (un compte, pas une impression).
Courtes (moins de 10 mots) : style nerveux. Longues (plus de 20) : style ample. Mêlées : style contrasté.

**3. Les images qui reviennent.** Lumière et obscurité ? Corps ? Nature, éléments ? Temps, éternité ? Ce
sont les couleurs de l'univers ; la traduction les garde.

**4. Qui parle.** Un narrateur extérieur ? Un personnage ? Le joueur lui-même ? Chaque distance a son
registre et ses contraintes grammaticales — et la question du tutoiement ou du vouvoiement se règle par
la fiche éditeur.

<!-- [D-39] -->
**5. La ponctuation expressive.** Points de suspension, tirets, phrases nominales : présents dans la
source ? Ce sont des outils de rythme, pas des fautes ; on les transpose. La forme exacte de ces signes en
français (points de suspension en un caractère, tirets, espaces) est celle de la charte du skill
`typographie-fr` ; ce skill n'en écrit aucune règle.

**6. La température.** Froid et distant, ou chaud et proche ? Un texte chaud dans un univers froid casse
la cohérence.

**7. Ce qui n'est PAS dit.** Le meilleur texte laisse de l'espace. Repérer ce que la source laisse flou, et
ne pas le combler en français.

### Format de la carte de voix

```
CARTE DE VOIX — [Gamme]
Créée le [date], relue le [date] — Références/Narration/VoixUnivers_<Gamme>.md
Sources lues : [textes, avec leur provenance]

Registre : [épique / sombre / poétique / intime / ironique]
Longueur des phrases : [courtes / mêlées / longues] — moyenne comptée : [X] mots sur [N] textes
Images dominantes : [3 à 5 champs]
Qui parle : [narrateur / personnage / joueur] ; adresse au joueur : [tu / vous, selon la fiche éditeur]
Ponctuation expressive : [oui / non, lesquelles]
Température : [froide / neutre / chaude]
Ce qu'on ne dit pas : [l'espace laissé flou]
Exemples validés : voir <Jeu>_FlavTexts_Reussis.md
```

---

## Phase 2 — Les techniques

### Technique 1 — Le pivot émotionnel

Trouver le mot ou la phrase qui porte l'émotion. Tout le reste le sert. Traduire le pivot d'abord,
construire autour.

[EXEMPLE FICTIF] *The city remembers everything. Including what you'd rather it forgot.*
- Pivot : *what you'd rather it forgot* — c'est la ville qui oublierait, et le lecteur qui le voudrait :
  menace, intimité, culpabilité.
- Version : « La ville se souvient de tout. Même de ce que vous voudriez qu'elle oublie. »

Piège à éviter : « Surtout ce que vous préféreriez oublier » sonne bien, mais change qui oublie (le
lecteur au lieu de la ville) et transforme « même » en « surtout ». Le pivot se garde ; on ne l'embellit
pas au prix du sens.

### Technique 2 — Le rythme

Compter les syllabes. Varier exprès. La tension naît des phrases courtes après les longues.

Outils du français, illustrés par des phrases construites pour l'exemple :
- **Allitération** : « Les ombres s'allongent, se glissent, s'effacent. »
- **Assonance** : « Sous la lune, la boue, l'écume, et vous. »
- **Gradation** : « Un murmure. Une rumeur. Un cri. »
- **Phrase nominale** : « Pas de pitié. Pas de témoin. Pas de retour. »
- **Chiasme** : « On meurt seul, et seul on oublie. »

### Technique 3 — La re-narration

Quand la traduction littérale tombe à plat, renoncer à la fidélité formelle et écrire l'équivalent
français : un texte qui produit le même effet chez un lecteur francophone.

Quand y penser :
- la source repose sur un jeu de mots intraduisible ;
- elle s'appuie sur une référence culturelle anglophone sans équivalent ;
- la version littérale dépasse la place disponible sur la carte (mesure : skill `controle-longueur`) ;
- la version littérale est correcte mais ne vibre pas.

Méthode :
1. Nommer l'effet visé (tension, mystère, humour noir, poésie…).
2. Isoler les deux ou trois images ou idées principales.
3. Réécrire en gardant les images, en abandonnant les mots.
4. Vérifier : même effet ? cohérent avec la carte de voix ? termes du glossaire respectés ?

[EXEMPLE FICTIF] *Fired twice, the blacksmith simply forged ahead.* — double jeu de mots (*fired* :
renvoyé, et passé au feu ; *forged ahead* : aller de l'avant, et forger).
- Littéral : « Renvoyé deux fois, le forgeron alla simplement de l'avant. » — les deux jeux de mots
  disparaissent.
- Re-narration : « Deux fois renvoyé, le forgeron répétait que c'est en forgeant qu'on reste forgeron. »
  — un autre jeu, français celui-là, qui garde le métier, l'obstination et le sourire.

La version précédente illustrait cette technique par un jeu de mots sur *hand* jugé intraduisible ; il ne
l'était pas (« main » a aussi les deux sens en français) : l'exemple a été remplacé.

### Technique 4 — L'espace laissé flou

Ce qu'on ne dit pas compte autant que ce qu'on dit. Signes d'un flou voulu dans la source :
- une phrase interrompue par des points de suspension ;
- une allusion à ce que le lecteur ne connaît pas encore ;
- une tension laissée sans réponse ;
- une incertitude sur qui parle.

Règle : si le flou est dans la source, il reste dans la traduction, même si un lecteur français pourrait
la trouver « incomplète ».

### Technique 5 — Transposer un registre

Certains registres anglais n'ont pas d'équivalent direct ; on cherche le registre français qui produit le
même effet. Pistes, à éprouver sur le texte :

| Registre anglais | Piste française |
|---|---|
| Gothique (oppression, aristocratie décadente) | romantisme noir : Hugo, Baudelaire, Poe dans la traduction de Baudelaire |
| Horreur cosmique | le fantastique de Maupassant ou de Gautier : nommer l'indicible par le détour |
| Grande fantasy épique | la chanson de geste, transposée en prose |
| Univers sombre et brutal (« grimdark ») | phrases courtes, vocabulaire clinique, nihilisme sec |
| Conte, fantaisie légère | le conte littéraire : Perrault, légèreté musicale |

### Les noms inventés dans un texte d'ambiance

<!-- [I-37] -->
Un nom propre inventé (lieu, faction, créature) prend la forme **et le genre** du glossaire de la gamme.
S'il n'y est pas, il passe par le skill `glossaire` (recherche complète, puis genre demandé à Hervé) : il
ne s'invente pas au fil de la phrase. En attendant, AURA tourne la phrase pour ne pas accorder (pas
d'article, pas d'adjectif accordé sur ce nom), et le signale.

---

## Phase 3 — Valider

### Le test de la lecture à voix haute

Un texte d'ambiance réussi sonne à voix haute : il a un rythme, des appuis, des silences.
1. Lire la traduction à voix haute, à vitesse normale (Hervé la lit ; AURA, elle, compte les syllabes et
   repère les enchaînements de sons difficiles).
2. Repérer où la langue accroche : syllabe de trop, liaison malaisée, respiration mal placée.
3. Corriger, relire.

Échec : on sent qu'on lit une traduction, on cherche ses mots, le rythme est mécanique. Réussite : on
oublie qu'on lit, l'image arrive avant les mots.

### Le test hors contexte

Lire le texte seul, sans connaître le jeu. Crée-t-il une image, une émotion, une question ? Sinon, il
n'est qu'un accessoire du contexte.

### Le test de cohérence de voix

Comparer avec trois autres textes du même jeu (en français s'il y en a, sinon en anglais) : même registre,
même température, même rythme ? Avec la carte de voix sous les yeux.

---

## Phase 4 — Ce que ce skill demande à Hervé, et comment la base s'enrichit

Plus il reçoit de matière, plus il est juste. Rien n'est à fournir d'un coup.

**Priorité haute**
1. **5 à 20 textes d'ambiance qu'Hervé juge réussis** (les siens ou publiés), dans `IMPORT/` ou dans la
   conversation. AURA en tire registre, rythme, techniques, et les marqueurs propres à Hervé.
2. **1 à 3 jeux traduits en français qu'il admire pour leur narration** — avec des **extraits**, que
   seul Hervé peut fournir ; le titre seul ne suffit pas (AURA ne connaît pas leur texte de façon fiable).
3. **Le document de style de l'éditeur**, s'il existe.

**Priorité moyenne**
4. Ses anciens textes d'ambiance, même partiels ou en brouillon (lus pour le style, jamais diffusés).
5. Ses notes de style personnelles (« je garde toujours les noms propres ainsi… ») — elles vont dans
   `Core/Preferences.md` s'il s'agit de style ; une décision sur un terme va au glossaire.
6. Les textes anglais qui lui ont posé problème, pour préparer des stratégies.

**Priorité basse**
7. Des cartes de voix qu'il aurait déjà esquissées. 8. Des retours d'éditeurs sur la narration.
9. Les gammes dont il a traduit plusieurs boîtes (pour la cohérence de voix).

**L'enrichissement au fil de l'eau** : quand Hervé valide une version qu'il trouve bonne et dit « archive
ça comme référence », AURA l'ajoute au fichier d'exemples de la gamme ; après une livraison, elle propose
d'y verser les meilleures versions du projet.

---

## Où ranger, sans doublon

<!-- [D-40] -->
Les noms sont ceux qu'annonce déjà le fichier `Références/Narration/README.md` d'Hervé :
- `Références/Narration/VoixUnivers_<Gamme>.md` — la carte de voix d'une gamme ;
- `Références/Narration/<Jeu>_FlavTexts_Reussis.md` — les exemples validés d'un jeu (source, version
  retenue, pourquoi elle marche, date de validation) ;
- `Références/Narration/References_Publiees.md` — les extraits de traductions publiées qu'Hervé admire,
  avec leur provenance.

`<Gamme>` et `<Jeu>` s'écrivent comme dans `Core/Gammes/<Gamme>.md` (nom d'usage, accents conservés).
Avant de créer un fichier, AURA cherche s'il en existe déjà un au nom voisin (avec ou sans accent,
espace ou tiret) ; s'il existe, elle le complète. Elle ajoute, elle ne réécrit pas sans l'accord d'Hervé.
Les exemples vivent dans le fichier d'exemples, pas recopiés dans la carte de voix.

---

## Ce que laisse une séance `narration-jeux`

- La carte de voix de l'univers, si elle n'existait pas (ou mise à jour, datée).
- 2 ou 3 versions par passage, argumentées, et la recommandation d'AURA.
- La technique employée pour la version recommandée.
- Les passages re-racontés plutôt que traduits, signalés comme tels.
- Les termes de jeu rencontrés, vérifiés contre le glossaire ; les noms inventés absents, confiés au skill
  `glossaire`.
- Les versions validées par Hervé, ajoutées au fichier d'exemples de la gamme s'il l'a demandé.

---

## Liens avec les autres skills

<!-- [D-13] -->
- `glossaire` : forme et genre de tout terme de jeu ou nom inventé cité dans un texte d'ambiance.
- `traduction-jeux` : les textes de règles (registre neutre et précis), quand un texte mêle ambiance et
  règle.
- `comprehension-regles` : la carte mécanique ; un texte d'ambiance respecte la voix ET les termes
  mécaniques validés.
- `controle-longueur` : la place disponible sur la carte.
- `typographie-fr` : la forme des signes (guillemets, tirets, points de suspension, espaces).
- `brief-editeur` : fiche éditeur (tutoiement ou vouvoiement, document de style, confidentialité).
