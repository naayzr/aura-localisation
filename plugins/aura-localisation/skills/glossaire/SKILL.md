---
name: glossaire
description: "Tient le glossaire Excel unique de chaque gamme (Glossaires/Glossaire_<Gamme>.xlsx) avec ses 15 colonnes et ses 5 statuts fixes, le genre, le nombre et l'élision des noms inventés (déclarés par Hervé, jamais devinés), un tableau de bord, un CHANGELOG et une sauvegarde datée avant chaque modification ; cherche dans tous les glossaires, segments et livrables avant de proposer un terme. Sert à créer ou importer un glossaire (dont un ancien Excel ou CSV), ajouter, valider, geler, archiver ou corriger un terme partout, contrôler un glossaire par programme, préparer une copie pour un traducteur ou un relecteur. Se déclenche quand Hervé dit « ajoute ce terme au glossaire », « valide ce terme », « on garde X pour Y », « importe mon glossaire », « crée le glossaire de la gamme », « corrige ce terme partout », « quel terme on a pris pour X », « ce mot existe déjà ? », « quel genre pour ce nom », « contrôle le glossaire », « prépare le glossaire pour le relecteur »."
---

# Glossaire — un fichier par gamme, une seule vérité par terme

Le glossaire est le contrat terminologique d'une gamme : ce que la boîte de base a imprimé, l'extension
le reprend. Ce skill le crée, l'importe, le fait vivre et le contrôle. Il ne traduit pas (skill
`traduction-jeux`) et ne décide jamais à la place d'Hervé : AURA propose, cherche, compte, écrit après
son accord.

Trois croyances qui viennent de la version précédente et restent vraies :
- **Un doute ne bloque jamais la traduction.** On marque, on avance, on tranche ensuite.
- **Le glossaire est un contrat.** Un terme imprimé ne change pas sans erratum.
- **Un glossaire se lit seul.** Un relecteur qui arrive doit comprendre pourquoi tel terme a été
  retenu : la DÉFINITION MÉCANIQUE et les NOTES le disent.

<!-- [D-30] -->
**Les règles du glossaire sont écrites ici, et nulle part ailleurs dans l'extension.** Les autres
skills y renvoient. `Core/Preferences.md` peut contenir d'anciennes copies de ces règles (installation
v2.0) : on ne les réécrit pas, on ne les recopie pas non plus. En cas d'écart, l'ordre est : règles
absolues (aucun terme inventé, aucun genre deviné, aucune décision de terme hors du glossaire) >
préférence explicite d'Hervé dans Preferences > réglages par défaut de ce skill.

Les programmes sont dans `${CLAUDE_SKILL_DIR}/scripts/` (Python 3, bibliothèque standard). **Par défaut,
aucun n'écrit** : ils affichent ce qu'ils feraient. Une décision qu'Hervé vient de dire (« valide ce
terme », « on garde X pour Y ») s'écrit directement avec `--ecrire` : sa phrase est l'accord. Un import,
une fusion, une correction partout ou une modification groupée se montre d'abord en essai, et ne s'écrit
qu'après son oui. Commandes et options : `references/scripts.md`.

---

## 1. Le fichier : un seul glossaire maître par gamme

<!-- [D-18] -->
- Chemin et nom fixes : `Glossaires/Glossaire_<Gamme>.xlsx`, où `<Gamme>` s'écrit exactement comme
  le registre de la gamme `Core/Gammes/<Gamme>.md` (nom d'usage, accents conservés). Si le registre
  n'existe pas encore, AURA demande le nom d'usage à Hervé et le même nom sert aux deux.
- **Jamais de numéro de version dans le nom.** La version vit dans l'onglet CHANGELOG ; le tableau de
  bord l'affiche. Un seul fichier « actuel », donc.
- **Jamais deux glossaires maîtres pour une même gamme.** Avant de créer ou d'importer, AURA regarde
  dans `Glossaires/` ; le programme refuse aussi un nom voisin (`Glossaire_TaintedGrail` à côté de
  `Glossaire_Tainted Grail`). Un glossaire qui arrive pour une gamme qui en a déjà un se **fusionne**.
- Les copies données à d'autres (traducteur, relecteur, éditeur) sont des **exports** nommés par
  produit et datés, rangés dans `Livrables/<Projet>/` : `Glossaire_<Gamme>_<Produit>_AAAA-MM-JJ.xlsx`.
  Ils ne remplacent jamais le maître.
- Une carte mécanique (skill `comprehension-regles`) ne se range pas dans `Glossaires/` : ses
  définitions entrent dans la colonne DÉFINITION MÉCANIQUE du maître.

**Si le programme ne voit pas le dossier HERVÉ WORLD** (cas normal des tâches qui tournent dans le
cloud, à partir du 06/10/2026), AURA applique la règle « Les programmes et le dossier d'Hervé » du skill `noyau`, section « Poser un fichier produit » :
les décisions sont d'abord écrites en texte dans la note de séance, le fichier produit s'appelle
`Glossaire_<Gamme>_NOUVEAU_AAAA-MM-JJ.xlsx`, Hervé range l'ancien maître dans `Core/Archives/` AVANT de
poser le nouveau, et la pose est vérifiée (nombre de termes, dernière ligne du CHANGELOG) avant que la
note soit close. Une sauvegarde faite par le programme hors du dossier n'existe pas : elle disparaît avec
la tâche.

---

## 2. Le modèle : colonnes, catégories, statuts

<!-- [D-17] -->
Une seule liste de colonnes, une seule liste de statuts, ici. Tout autre fichier y renvoie. Le programme
`scripts/modele_glossaire.py` porte exactement les mêmes listes (il les affiche si on le lance seul).

**Onglets**, dans cet ordre : `Tableau de bord` · `Termes` · `CHANGELOG` · `Notice`.

**Colonnes de `Termes`**, dans cet ordre :

| Colonne | Contenu |
|---|---|
| ID | identifiant stable `T-0001`, donné par le programme, jamais réutilisé (même archivé) |
| EN | le terme anglais exact |
| FR | le terme retenu — **un seul** par cellule (deux propositions = à trancher, pas à valider) |
| CATÉGORIE | MÉCANIQUE, MOT-CLÉ, COMPOSANT, PERSONNAGE, LIEU, OBJET, LORE, INTERFACE, AUTRE |
| GENRE | m, f, ou « — » quand sans objet (verbe, adjectif, mot-clé non nominal) |
| NOMBRE | singulier, pluriel, invariable |
| ÉLISION | oui (l'…) / non (le…, h aspiré) |
| FORMES ACCORDÉES | les formes écrites dont le texte a besoin (féminin, pluriel, participe) |
| RAPPEL STANDARD | pour un mot-clé : le texte de rappel identique sur toute la gamme |
| DÉFINITION MÉCANIQUE | ce que le terme fait en jeu, en français ; c'est elle qui rapproche deux termes |
| STATUT | Brouillon, À confirmer, Confirmé, Gelé, Archivé |
| SOURCE | d'où vient le terme : livret p. X, échange éditeur du JJ/MM, glossaire officiel de licence… |
| PUBLIÉ DANS | les produits où le terme est imprimé, séparés par un point-virgule |
| NOTES | justification, alternatives écartées, risques de confusion, termes liés |
| DATE | dernière modification de la ligne, AAAA-MM-JJ (tenue par le programme) |

**Les 5 statuts** — une seule liste, la même partout (glossaire, texte, questions, rapports) :

| Statut | Sens | Pour y entrer |
|---|---|---|
| Brouillon | proposé, non validé ; change librement | tout terme proposé ou importé |
| À confirmer | attend l'éditeur ou l'ayant droit | la question est inscrite au registre `Core/Questions_Editeurs.md` |
| Confirmé | validé ; change encore, mais avec une ligne au CHANGELOG | accord d'Hervé (ou réponse de l'éditeur), FR unique, GENRE déclaré si la catégorie l'exige |
| Gelé | imprimé ; ne bouge plus sans erratum | PUBLIÉ DANS rempli |
| Archivé | remplacé, gardé pour trace | NOTES dit par quoi, et à partir de quel produit |

Une ligne ne disparaît jamais : le terme s'archive.

**Les ensembles se nomment par ce qu'ils contiennent.** « À trancher » = Brouillon + À confirmer ;
« en vigueur » = Confirmé + Gelé ; « gardés pour trace » = Archivé. Jamais « tout sauf Confirmé », qui
avalerait les Gelés et les Archivés. Le tableau de bord et les programmes calculent ainsi.

<!-- [D-33] -->
**Un sens mécanique = un terme français.** Un même mot anglais employé pour deux mécaniques
différentes a deux lignes, chacune avec sa DÉFINITION MÉCANIQUE, et NOTES explique la distinction
(ou le choix de garder un seul mot français si l'ambiguïté de l'anglais est voulue — décision d'Hervé,
souvent avec l'éditeur). Le programme refuse un second sens tant que les deux définitions ne sont pas
remplies et différentes.

---

## 3. Genre, nombre, élision : déclarés, jamais devinés

<!-- [I-37] -->
Un nom inventé (faction, lieu, créature, ressource, mot-clé) n'a pas de genre en anglais. Le choix fixe
pourtant les accords dans tout le texte des règles et des cartes : article, adjectif, participe, pronom,
élision. Une incohérence se voit à l'impression.

- **Le genre est obligatoire** pour PERSONNAGE, LIEU, OBJET, LORE et MOT-CLÉ nominal. C'est Hervé qui
  le déclare. Le programme refuse de passer un tel terme en Confirmé tant que GENRE est vide.
- **AURA ne devine jamais.** Pour un nom commun du dictionnaire, elle peut indiquer le genre du
  dictionnaire comme *proposition*. Pour un nom inventé, elle laisse « ? ». Elle présente une liste
  groupée (« 6 termes attendent leur genre : … »), rien n'est écrit avant la réponse d'Hervé.
- **Sans genre déclaré, AURA contourne l'accord** dans tout ce qu'elle rédige : tournure qui n'accorde
  pas, terme repris en tête de phrase, reformulation. Elle ne pose jamais un article ou un adjectif accordé
  sur un terme dont le genre n'est pas au glossaire.
- NOMBRE, ÉLISION et FORMES ACCORDÉES suivent la même règle : déclarés, sinon demandés.
- Le contrôle (`controle_glossaire.py`) liste chaque genre manquant, avec son compte exact.

---

## 4. Une décision de terme ne s'écrit qu'au glossaire

<!-- [I-06] -->
Deux écritures du même fait finissent par diverger, et c'est celle qu'on lit qui a tort. Donc :

- « On garde Épuiser pour Exhaust » [EXEMPLE FICTIF] est une **décision de terme** : elle s'écrit dans
  la ligne du glossaire de la gamme (STATUT, SOURCE, et la justification en NOTES : « décision d'Hervé du
  JJ/MM : … »), avec sa ligne au CHANGELOG. **Jamais dans `Core/Preferences.md`**, jamais dans CONTEXT,
  le Journal ou une fiche éditeur.
- `Core/Preferences.md` ne garde que des règles de style et de travail d'Hervé (« toujours grouper mes
  questions »). Ce qui est propre à un éditeur (tutoiement ou vouvoiement, écarts à la charte) va dans
  sa fiche `Core/Editeurs/<Éditeur>.md`.
- Le Journal peut **mentionner** qu'une décision a été prise (« 3 termes validés, voir le glossaire »),
  sans recopier le terme comme une règle.
- **Ancienne installation** : si Preferences contient déjà des décisions de terme (cas de la v2.0), AURA
  les signale à Hervé, propose de les porter au glossaire (NOTES : « repris de Preferences.md le … »),
  puis, avec son accord seulement, de retirer ces lignes de Preferences. Rien n'est réécrit sans son oui.

---

## 5. Avant de proposer un terme : la recherche complète

<!-- [I-35] -->
« Absent du glossaire » ne se dit qu'après une recherche complète. Une recherche partielle ne conclut
rien. Avant de proposer un terme français :

1. **Chercher l'anglais et ses variantes** (pluriel, majuscule, sans accent, forme verbale : *Exhaust,
   exhausted, exhausting*) dans **tous** les glossaires de la gamme et des autres gammes du même éditeur,
   dans les segments réutilisables (`Références/Segments/`), les références, les livrables passés et
   en cours. Le programme le fait d'un coup, avec les comptes :
   `python3 chercher_terme.py "<dossier HERVÉ WORLD>" "Exhaust"`
2. **Vérifier que le français candidat n'est pas déjà pris** pour autre chose :
   `python3 chercher_terme.py "<dossier>" "Épuiser" "épuisé" "épuisez" --langue fr` (pour un verbe
   français, on donne ses formes).
3. **Lire les fichiers NON FOUILLÉS** que le programme liste (PDF, fichier illisible) : tant qu'ils
   n'ont pas été lus autrement, l'absence n'est pas prouvée, et AURA le dit.
4. Puis appliquer la garde contre les inventions du skill `noyau` : glossaire → texte source → projet
   précédent de la gamme → inférence annoncée comme telle → rien (on demande).

Si le programme ne voit pas le dossier (la règle « Les programmes et le dossier d'Hervé » du skill `noyau`), AURA cherche dans les fichiers texte (.md, .csv)
avec ses outils de lecture, demande à Hervé de glisser les glossaires et livrables Excel ou Word
concernés, et **dit quels fichiers n'ont pas été fouillés** : « absent » ne se dit pas sans eux.

<!-- [I-38] -->
**Le même mot anglais dans deux gammes n'est pas le même terme.** *Exhaust* peut, dans un jeu, faire
pivoter une carte et, dans un autre, la retirer jusqu'à la fin du combat [EXEMPLE FICTIF]. Le
rapprochement se fait par la DÉFINITION MÉCANIQUE (carte du skill `comprehension-regles`) et par la
gamme, jamais par le mot seul. Le même mot trouvé ailleurs est un **signal à vérifier** : sans preuve
que la mécanique est la même, le terme reste en Brouillon ou À confirmer, et AURA dit d'où vient le
rapprochement. Le contrôle à plusieurs fichiers (`controle_glossaire.py A.xlsx B.xlsx`) liste ces
mots avec leurs définitions côte à côte.

---

## 6. Faire vivre les termes

**Quand créer une entrée** : à la première occurrence dans le texte source, pas après avoir tout
traduit. En pratique, parcourir le source avant de commencer, repérer les termes candidats, les créer
en Brouillon, traduire, puis valider.

**Valider en trois temps** :
1. *Proposition* — EN, FR proposé, catégorie, définition mécanique, source, justification courte en
   NOTES ; statut Brouillon.
2. *Cohérence de gamme* — la recherche complète (section 5) ; pas de conflit avec un terme Confirmé ou
   Gelé ; termes liés cohérents (Épuiser / Épuisé / Réactiver [EXEMPLE FICTIF]).
3. *Éditeur si doute* — nom de marque, référence culturelle voulue, terme de licence, choix qui touche
   l'identité de la gamme : la question va au registre `Core/Questions_Editeurs.md` (le skill
   `brief-editeur` en fait le courriel groupé), le terme passe À confirmer. Dans le texte traduit, le
   passage reste lisible et porte la marque `[À CONFIRMER : <terme EN>]`, que tout programme retrouve.

**Quand la réponse arrive** (Hervé ou l'éditeur) : le terme passe Confirmé, SOURCE dit « échange
éditeur du JJ/MM » ou « décision d'Hervé du JJ/MM », la ligne du registre des questions est close avec
son « impact glossaire ». Une seule commande fait la modification, la date, la ligne de CHANGELOG et la
sauvegarde :
`python3 gerer_glossaire.py modifier <glossaire> --id T-0012 --champ STATUT=Confirmé --champ GENRE=f --par "Hervé" --raison "validé en séance du JJ/MM"`
Plusieurs décisions d'un coup : un petit tableau `ID;CHAMP;VALEUR;RAISON;PAR` passé avec `--lot`.

**Ce qu'on n'y met pas** : les mots génériques sans risque d'ambiguïté (*player*, *round*), sauf si
l'éditeur impose leur traduction ; les synonymes écartés comme lignes séparées (ils vont dans les NOTES
du terme retenu).

**Fin de projet** : AURA propose les termes structurants du projet absents du glossaire (après la
recherche complète), en Brouillon. C'est l'accumulation qui fait que le cinquième produit d'une gamme
démarre sur une base solide.

**Si Hervé modifie le fichier à la main** dans Excel, c'est son droit. Avant la prochaine écriture, AURA
compare le fichier à la dernière sauvegarde (`gerer_glossaire.py comparer`) et lui montre les changements
qui n'ont pas de ligne au CHANGELOG, pour les tracer avec son accord.

---

## 7. Corriger un terme partout

<!-- [I-07] -->
Un terme faux écrit quelque part revient par un segment, un ancien lot de cartes ou une préférence. Quand
Hervé corrige un terme :

1. **Chercher l'ancien français partout** — tous les glossaires, segments, Références, livrables en cours,
   `Core/Preferences.md`, `Core/evas.md` — avec ses formes :
   `python3 chercher_terme.py "<dossier>" "<ancien terme>" "<ses formes>" --langue fr --tout`
2. **Montrer la liste à Hervé AVANT de remplacer** : nombre total, nombre par fichier, chaque endroit
   avec son extrait, et ce qu'AURA propose pour chacun :
   - *à remplacer* : glossaires (ligne active), segments, livrables **en cours** (sur la copie de travail
     `_v2`, jamais sur l'original), une règle de Preferences qui citerait le terme ;
   - *à garder pour trace* : la ligne archivée, le CHANGELOG, le Journal, les entrées d'evas (qui
     racontent l'erreur), les sauvegardes ;
   - *déjà imprimé* (livrable livré, produit publié) : pas de correction silencieuse — c'est un erratum
     (skill `gestion-gamme`) ; dans le glossaire, l'ancien terme passe Archivé et le nouveau prend une
     nouvelle ligne.
3. Après son accord : sauvegarde, modification du glossaire (`modifier`, avec `--erratum` si le terme
   était Gelé), remplacements dans les copies.
4. **Relancer la recherche** et montrer le nouveau compte : zéro hors des endroits gardés pour trace.

Si l'erreur était une invention d'AURA, le protocole du skill `noyau` (registre `Core/evas.md`)
s'applique en plus.

---

## 8. Sauvegarde datée avant toute modification en masse

<!-- [D-19] -->
Avant toute écriture dans un glossaire existant — et toujours avant une modification qui touche plus
d'une ligne (import, fusion, correction partout, validation groupée) — une copie datée est posée dans
`Core/Archives/` :

`Glossaire_<Gamme>_avant_AAAA-MM-JJ_HHhMM_<N>termes.xlsx`

`N` est le nombre de termes du fichier sauvegardé (compté par le programme). Une sauvegarde ne s'écrase
jamais : même minute et même nombre, le programme ajoute `_2`, `_3` ; un contenu identique n'est pas
recopié. Les programmes la font d'eux-mêmes avant d'écrire ; à la main : `gerer_glossaire.py sauvegarder`.
L'heure est celle de la machine qui exécute le programme (peut être en temps universel). **Le glossaire
doit être fermé dans Excel** : si Excel l'a ouvert (petit fichier `~$…` à côté), le programme refuse
d'écrire et le dit.

---

## 9. Importer un glossaire existant

<!-- [D-24] -->
Un glossaire qui existait avant (Excel ou CSV d'Hervé, glossaire d'un éditeur, liste d'un relecteur, ou
le glossaire Tainted Grail de la démo du 30/05 que Dorian enverra) **entre en Brouillon, sans exception**.
Aucun terme n'arrive pré-validé : son statut d'origine est gardé en NOTES, et c'est Hervé qui valide.

1. Hervé dépose le fichier dans `IMPORT/` (ou le glisse dans la conversation). L'original n'est jamais
   modifié.
2. AURA vérifie s'il existe déjà un glossaire maître pour cette gamme : si oui, ce sera une **fusion**
   (`--dans`), jamais un second maître.
3. Essai : `gerer_glossaire.py importer <fichier> --gamme "<Gamme>" --sortie Glossaires/Glossaire_<Gamme>.xlsx --provenance "<d'où vient ce glossaire>"`.
   AURA montre à Hervé le **nombre réel** de termes compté par le programme, la correspondance des
   colonnes, les statuts d'origine, les catégories proposées, les cellules à double proposition, les
   genres à déclarer, et, pour une fusion, les conflits (non appliqués).
4. Avec son accord : la même commande avec `--ecrire`, puis le contrôle, puis une séance de validation
   par lots (genres d'abord, puis statuts).

Détail, correspondance des colonnes et cas du glossaire de la démo : `references/import.md`.

---

## 10. Le classeur au standard

<!-- [I-13] -->
Un glossaire se juge à sa lisibilité ligne à ligne. Le programme écrit toujours le même classeur :
`Tableau de bord` en premier (chiffres par statut, par catégorie, par produit, ensembles utiles, points
à régler, version — **tous calculés par formule** sur l'onglet Termes), `Termes` (en-tête et colonnes
ID et EN figés, filtres, couleur de ligne selon le statut, listes déroulantes sur CATÉGORIE, GENRE,
NOMBRE, ÉLISION et STATUT), `CHANGELOG`, et une `Notice` d'une page. Détail :
`references/classeur-excel.md`.

---

## 11. Contrôler un glossaire

`python3 controle_glossaire.py Glossaires/Glossaire_<Gamme>.xlsx` — lecture seule. Il signale, avec des
comptes exacts : onglets ou colonnes manquants ou mal nommés, statut ou catégorie hors liste, ID vide ou
en double, EN en double, même français pour deux anglais différents (à vérifier), genre vide là où il est
obligatoire, Gelé sans PUBLIÉ DANS, Confirmé sans français, cellule à double proposition, termes
« À confirmer » qui attendent depuis plus de 30 jours. Avec plusieurs fichiers, il compare aussi les
gammes entre elles (section 5).

AURA lance ce contrôle après chaque import ou modification groupée, avant de partager un glossaire, et à
l'audit mensuel. Elle rapporte les chiffres tels quels, sans arrondir.

---

## 12. La gamme dans la durée, et le relecteur

Héritage boîte de base → extensions, conflit entre deux produits, éditeur qui change d'avis sur un terme
déjà imprimé, export pour un traducteur ou un relecteur et intégration de ses retours :
`references/gamme-et-relecteur.md`.

---

## 13. Ce qu'une séance de glossaire laisse

- Le glossaire maître à jour (et sa sauvegarde datée s'il a été modifié).
- La liste des termes validés dans la séance, avec leurs statuts.
- La liste des termes À confirmer, prêts pour un envoi groupé à l'éditeur.
- Les genres encore à déclarer, comptés.
- Les conflits trouvés : tranchés, ou portés au registre des questions.
- Le CHANGELOG à jour pour tout terme Confirmé ou Gelé modifié.

---

## Liens avec les autres skills

<!-- [D-13] -->
- `comprehension-regles` : ses définitions mécaniques remplissent la colonne DÉFINITION MÉCANIQUE.
- `traduction-jeux` et `narration-jeux` : prennent leurs termes ici ; un nom inventé sans genre déclaré
  revient ici avant d'être accordé.
- `qa-coherence` et `relecture-multi-agents` : vérifient le texte contre ce glossaire.
- `typographie-fr` : la casse et la typographie des termes français suivent sa charte et la fiche de
  l'éditeur ; ce skill n'en écrit aucune règle.
- `brief-editeur` : envoie les questions À confirmer, en courriel groupé.
- `gestion-gamme` : registre des produits, titres publiés, errata, briefs des traducteurs (qui utilisent
  l'export de ce skill).
- `noyau` : garde contre les inventions, sauvegarde de session, registre `Core/evas.md`.
