---
name: gestion-gamme
description: "Responsable de gamme : tient le registre de chaque gamme dans Core/Gammes/ (produits, extensions, réimpressions, titres de cartes publiés, licence, errata, équipe, lots, BAT) et vérifie par script qu'un titre n'est pas déjà publié ; rétroplanning à rebours depuis la remise à l'imprimeur, à la capacité d'Hervé en caractères par jour ; coordination des traducteurs et relecteurs (brief, lots, livraisons, fusion des questions) ; relecture du travail d'un tiers ; comparaison de deux versions du texte source pour ne retraduire que le modifié ; suivi BAT1 et BAT2 ; mémoire de traduction (Références/Segments/). Déclencheurs : « nouvelle extension », « réimpression », « planning », « rétroplanning », « on tient la date ? », « répartis les lots », « brief pour le traducteur », « relis le lot de… », « erratum », « nouvelle version des règles », « le BAT est arrivé », « ce titre est déjà sorti ? »."
---

# Gestion de gamme — registre, planning, équipe, errata, BAT

Hervé n'est pas seulement traducteur : il gère des gammes entières (traduction, relecture,
coordination). Une gamme vit des années : boîte de base, extensions, réimpressions, errata de la
version originale, plusieurs traducteurs. Ce skill tient la mémoire de la gamme et les calculs qui
s'y rattachent.

**Ce qui n'est pas ici** (chaque sujet a un seul foyer) :

| Sujet | Skill |
|---|---|
| Un terme, son statut, sa justification | `glossaire` |
| Règles de typographie française | `typographie-fr` |
| E-mails à l'éditeur, registre des questions, fiche éditeur | `brief-editeur` |
| Compter les caractères d'un fichier, devis | `comptage-caracteres` |
| Texte trop long pour son cadre | `controle-longueur` |
| Vérifier son propre texte avant livraison | `qa-coherence`, `relecture-multi-agents` |
| Comprendre le système de jeu | `comprehension-regles` |

## Règles fixes

- **Le registre est la mémoire d'Hervé.** Créé à partir de `references/modele-registre-gamme.md`
  s'il n'existe pas (avec son accord), puis on y ajoute ou on y met à jour des lignes. Jamais réécrit
  en entier, jamais supprimé ; une ligne périmée passe « Archivé ».
<!-- [I-06] -->
- **Un fait, un seul foyer.** Le registre renvoie au glossaire pour les termes (y compris les termes
  gelés et les termes imposés par une licence), à la fiche éditeur pour les contacts et les clauses,
  à `Core/Questions_Editeurs.md` pour les questions, à `Core/Suivi.md` pour les fils en attente.
<!-- [I-34] -->
- **Compter, jamais estimer.** Caractères, cartes, lots, corrections : un chiffre vient d'un fichier
  lu en entier ou d'un script. « Environ » ne part jamais chez l'éditeur ni dans un planning.
<!-- [I-28] -->
- **Pas de sous-agent dans ce skill.** Tout se fait en une passe à la fois ; l'abonnement d'Hervé a
  un quota.
- **Confidentialité.** Avant de lire un fichier source d'un éditeur, AURA regarde la clause sur
  l'intelligence artificielle de sa fiche (`Core/Editeurs/<Éditeur>.md`, règle décrite dans le skill
  `brief-editeur`). Si la fiche dit « non autorisée », ou si un accord de confidentialité l'exclut,
  elle demande à Hervé avant d'ouvrir le fichier.
<!-- [R-33] -->
- **Ce qui part chez un tiers** (brief, synthèse de relecture, liste de corrections BAT) est un
  brouillon qu'Hervé relit et envoie lui-même : phrases claires, chiffres exacts, aucun code interne.
  Ce qu'il dit, ou ne dit pas, de l'outil et de l'intelligence artificielle suit la règle « Mention
  d'AURA et de l'IA » du skill `brief-editeur` (qui tient compte d'une obligation de déclaration
  écrite au contrat).
- **Jamais d'écrasement** : les fichiers reçus restent intacts ; AURA travaille sur des copies
  `Livrables/<Projet>/<fichier>_v1`, `_v2`… Les quatre scripts refusent aussi d'écrire un rapport
  (`--sortie`) par-dessus un fichier existant : AURA choisit un autre nom (date, `_v2`). <!-- [R-36] [R-60] -->
- **Les scripts** (`${CLAUDE_SKILL_DIR}/scripts/`) : avant de les lancer, AURA applique la règle « Les programmes
  et le dossier d'Hervé » du skill `noyau`, dont « Écrire une commande » (chemins complets) <!-- [R-29] --> (fichier glissé si le programme ne voit pas le dossier ;
  rapports et registres réécrits par AURA dans HERVÉ WORLD ; jamais un fichier d'Hervé remplacé).

---

## 1. Le registre de gamme

Chemin : `Core/Gammes/<Nom de la gamme tel que l'éditeur l'écrit>.md`. Modèle, règles de nommage et
exemple : `references/modele-registre-gamme.md`. Avant de créer un registre, AURA vérifie qu'il n'en
existe pas déjà un sous une autre graphie.

**Création** : AURA demande le nom de la gamme tel que l'éditeur l'écrit, l'éditeur français,
l'éditeur ou l'ayant droit d'origine, s'il y a une licence, le rôle d'Hervé, et les produits déjà
parus. Elle ne remplit que ce qu'Hervé a dit ou ce qu'un fichier montre.

**Nouveau produit** (extension, réimpression, promotionnel) :

1. Ligne dans le tableau « Produits », statut « Annoncé » ou « Sources reçues ».
2. Version du texte source reçue → tableau « Versions du texte source ».
3. Dès que la liste des titres de cartes existe : **contrôle « titre déjà publié »** (ci-dessous).
4. Pour une réimpression : les errata du journal qui ne sont pas encore intégrés sont listés à Hervé
   (partie 5).
5. Rétroplanning (partie 2), puis répartition si d'autres traducteurs interviennent (partie 3).

### Contrôle « titre déjà publié »

<!-- [I-35] -->
```
python3 "${CLAUDE_SKILL_DIR}/scripts/titres_publies.py" --registre "<HERVÉ WORLD>/Core/Gammes/<Gamme>.md" \
    --glossaire "<HERVÉ WORLD>/Glossaires/Glossaire_<Gamme>.xlsx" \
    --nouveaux cartes_extension.xlsx --col-en Title --col-fr "Titre FR"
```

<!-- [R-50] -->
Le script compare chaque titre anglais du nouveau produit aux titres imprimés (registre) et aux
termes du glossaire (hors « Archivé »), lus selon leur statut (skill `glossaire`) : seul un terme Gelé
compte comme imprimé. Il signale, sans rien trancher :

- **déjà publié** : la traduction imprimée (registre, ou terme Gelé) à reprendre ;
- **ÉCART** : traduction proposée différente de la traduction imprimée. Un titre publié ne change pas
  sans erratum décidé avec l'éditeur ;
- **déjà décidé au glossaire** (terme Confirmé, pas encore imprimé) : le glossaire fait foi, une autre
  traduction se discute avec Hervé, sans erratum ;
- **proposition existante, non validée** (terme Brouillon ou À confirmer) : rien n'est décidé, le choix
  se tranche au glossaire ;
- **COLLISION** : traduction proposée déjà prise par un autre titre anglais de la gamme ;
<!-- [I-38] -->
- **titre proche** (au moins 85 % de ressemblance, ou identique aux accents près) : même carte ou
  carte différente ? Cela se vérifie sur l'effet de la carte, jamais sur le nom seul ;
- doublons de la nouvelle liste, incohérences de la référence (un même titre imprimé sous deux
  traductions), et titre présent à la fois au registre et au glossaire (un seul foyer à garder).

<!-- [I-10] -->
Si Hervé maintient un écart après l'avoir vu, AURA le dit une fois, en citant le titre publié, puis
applique son choix et le note (colonne Notes du registre, et colonne NOTES du glossaire si le titre y
vit, par le skill `glossaire`). Elle ne le resignale pas aux séances suivantes.

**Après publication d'un produit** : chaque titre imprimé est enregistré à un seul endroit. Si le
titre anglais est un terme du glossaire, c'est le glossaire qui reçoit l'information (statut Gelé,
PUBLIÉ DANS, par le skill `glossaire`) ; sinon il entre dans le tableau « Titres de cartes publiés »
du registre. Puis le texte validé nourrit la mémoire de traduction (partie 7).

---

## 2. Le rétroplanning

<!-- [R-52] -->
Calcul à rebours depuis la date de remise des fichiers à l'imprimeur, en jours ouvrés. La chaîne :
réception des sources → traduction → réponses aux dernières questions de l'éditeur et leur intégration
(les lots de questions partent pendant la traduction ; le relecteur lit un texte où les réponses sont
déjà reportées) → relecture → mise en page → BAT1 → BAT2 → validation de la version française par
l'éditeur de la version originale ou l'ayant droit (licence, co-édition) → fichiers d'impression →
remise. La FAQ se place après la remise, hors calcul. Une étape propre au produit (relecture de
l'auteur, validation juridique…) s'ajoute avec `--etape "Nom:jours:après"`, où « après » nomme
l'étape qui la précède.

**Ce qu'AURA demande, et ne suppose jamais** :

- la date de remise à l'imprimeur (donnée par l'éditeur) ;
- le volume à traduire, **compté sur le fichier** (skill `comptage-caracteres`) ;
- **la capacité de traduction d'Hervé, en caractères par jour ouvré**. Elle vit dans `Core/Profile.md`,
  et seulement là (datée, par type de texte : cartes courtes et livret de règles ne se traduisent pas
  forcément au même rythme). Si elle y manque, ou pas pour ce type de texte, elle se demande à lui et
  s'y écrit ; le registre ne la recopie pas, il note seulement quelle valeur a servi au calcul ; <!-- [R-41] -->
- la durée de chaque autre étape, auprès de qui la fait (relecteur, éditeur, maquettiste, ayant
  droit) ; une étape qui n'existe pas sur ce produit vaut 0. Pour une gamme sous licence ou en
  co-édition, la validation par l'ayant droit dure souvent plusieurs semaines : sa durée se demande à
  l'éditeur, elle ne se suppose pas ;
- les jours travaillés (5, 6 ou 7 par semaine, selon lui), ses indisponibilités, et si les jours
  fériés français comptent.

Exemple, toutes valeurs fictives [EXEMPLE FICTIF] :

```
python3 "${CLAUDE_SKILL_DIR}/scripts/retroplanning.py" --produit "Extension Le Guet" --remise 2027-03-15 \
    --caracteres 320000 --capacite 12000 --questions 5 --relecture 8 --mise-en-page 10 \
    --bat1 5 --bat2 3 --validation-vo 10 --fichiers 2 --debut 2026-11-02 --feries-fr \
    --indispo 2026-12-24:2027-01-01 --etape "Relecture de l'auteur:3:relecture"
```

Le script refuse de calculer s'il manque une information et dit laquelle demander. Il sort le tableau
des étapes (début et fin au plus tard), le **jalon clé** (début de traduction au plus tard), la
marge, et, si la date ne tient pas, des **leviers chiffrés** : capacité qu'il faudrait, caractères à
confier à un autre traducteur, jours de décalage de la remise. Aucun levier n'est décidé par AURA.

<!-- [I-04] -->
**Jalon menacé** (début possible après le début au plus tard) ou **marge faible** (2 jours ouvrés ou
moins) : le script donne une ligne prête pour `Core/Suivi.md` ; AURA l'y ajoute et le dit à Hervé
dans la séance. Quand la situation change (sources arrivées, levier choisi), la ligne est mise à jour,
ou close selon la règle des fils du skill `noyau` (jamais effacée), jamais recopiée telle quelle. <!-- [R-27] -->

Après validation d'Hervé, les étapes entrent dans le tableau « Calendrier en cours » du registre.
En cours de projet, on recalcule avec `--deja-traduits <caractères faits>` et `--debut <aujourd'hui>`.

Limite à dire : le même calendrier sert pour tout le monde ; si le maquettiste ne travaille pas les
mêmes jours, sa durée se donne en conséquence.

---

## 3. Coordination des traducteurs et relecteurs

Détail : `references/coordination.md`. L'essentiel :

- **Brief type**, préparé quand Hervé le demande : projet en dix lignes, lot (plage exacte et
  caractères comptés), glossaire exporté, charte typographique exportée et écarts de l'éditeur,
  procédure de questions, ce qu'on modifie et ce qu'on commente, format de livraison, contact.
- **Attribution des lots** : compter, demander la capacité de chacun, découper par cohérence de voix
  (une faction ou un type de carte par personne), garder à Hervé ce qui fixe les termes, vérifier le
  planning avec la capacité cumulée, écrire les lots dans le registre.
- **Suivi des livraisons** : lot en retard → `Core/Suivi.md` ; à la livraison, contrôle de
  complétude compté (« 82 sur 82 »), identifiants et balises intacts, puis relecture.
- **Fusion des questions** de plusieurs traducteurs dans `Core/Questions_Editeurs.md` : chercher
  d'abord au glossaire et dans les réponses déjà reçues, regrouper les doublons (colonne « Posée
  par »), séparer ce qui relève de l'éditeur de ce qu'Hervé tranche seul. L'envoi groupé passe par le
  skill `brief-editeur`.

AURA ne recrute, ne rémunère et n'engage personne : ce sont des décisions d'Hervé.

---

## 4. Relire la traduction d'un tiers

Détail et exemple : `references/relecture-tiers.md`. L'essentiel :

- Une passe à la fois, par tranches d'environ 35 000 caractères, avec un fichier d'état pour reprendre.
- Contrôles automatiques d'abord (skills `typographie-fr`, `qa-coherence`, `controle-longueur`), lecture
  contre l'anglais ensuite.
- **Tableau des corrections** : référence, anglais, traduction livrée, proposition, **type** (Sens,
  Terminologie, Mécanique, Typographie, Style), **gravité** (Bloquant, Important, Suggestion),
  commentaire pour le traducteur.
- **Synthèse bienveillante** : ce qui est réussi (cité), deux ou trois points récurrents avec leur
  nombre, les bloquants expliqués, les questions ouvertes, la suite. Pas de note, aucun code interne ;
  mention de l'outil selon la règle du skill `brief-editeur`.
- Le fichier du traducteur n'est jamais modifié ; Hervé valide les corrections avant tout envoi.

---

## 5. Errata et versions du texte source

L'éditeur de la version originale publie des errata, des FAQ, des règles révisées. On ne retraduit
que ce qui a changé.

<!-- [I-39] -->
1. **Contrôle à vide d'abord**, une fois par type de fichier : le comparateur doit voir une
   modification glissée exprès, sinon on ne croit pas son « rien n'a changé ».
   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/comparer_versions.py" regles_v1.0.docx --controle-a-vide
   ```
2. **Comparer** l'ancienne version (celle qui a été traduite) et la nouvelle :
   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/comparer_versions.py" regles_v1.0.docx regles_v1.1.docx \
       --memoire "<HERVÉ WORLD>/Références/Segments/Segments_<Gamme>.csv" --sortie "<HERVÉ WORLD>/Livrables/<Projet>/comparaison_v1.1.md"
   ```
   Pour un fichier de cartes, comparer par identifiant, pour qu'une carte insérée ne décale pas tout :
   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/comparer_versions.py" cartes_v1.xlsx cartes_v2.xlsx --cle ID --colonnes "Title,Text"
   ```
   Les colonnes se donnent par leur en-tête exact, tel qu'il est écrit dans le fichier. Un nom absent
   arrête le programme (au lieu de lire en silence une colonne vide), et une colonne-clé où aucune ligne
   ne porte d'identifiant aussi : AURA relit les en-têtes que le message liste et relance. <!-- [R-49] -->
   Le rapport classe les passages en modifiés (avec le changement mot à mot `[-retiré-]{+ajouté+}`),
   ajoutés, supprimés, déplacés (texte identique, rien à retraduire), et donne le nombre exact de
   caractères à retraduire. Avec `--memoire`, il affiche la traduction française existante de l'ancien
   passage, pour qu'Hervé n'ait qu'à l'ajuster. On compare deux fichiers du même format : entre un .md
   et un .txt, une marque de titre (`#`) compte comme une modification.
3. **Consigner** : tableau « Versions du texte source » du registre (date, nombre de passages, caractères
   à retraduire), et une ligne par correction dans le journal « Errata ».
4. **Un erratum qui touche un terme Gelé ou un titre publié** ne se règle jamais en silence : il se
   décide avec l'éditeur (question par le skill `brief-editeur`), puis le glossaire est mis à jour par le
   skill `glossaire`, qui recherche aussi l'ancien terme partout où il a pu être recopié.
<!-- [R-51] -->
5. **Réimpression** : à chaque nouveau produit de type réimpression, AURA liste à Hervé tous les errata
   du journal qui n'ont pas encore le statut « Intégré à la réimpression <réf.> », quel que soit leur
   statut d'avant (liste des statuts : `references/modele-registre-gamme.md`). Une fois reportés, ils
   passent à « Intégré à la réimpression <réf.> ».

Si l'erratum se facture, le compte du script sert de base ; les règles de devis sont dans le skill
`comptage-caracteres`.

---

## 6. BAT (bon à tirer)

Détail : `references/bat.md` (check-list complète et suivi des cycles). L'essentiel :

- Check-list par page : texte tronqué ou manquant, texte non à jour, balise affichée en brut, icône,
  valeurs, césure, renvois de page à remplir sur la pagination française, index alphabétique à retrier
  après traduction, sommaire, mots-clés, crédits, dos de cartes et boîte.
- Liste de corrections numérotée par page, en phrases claires, envoyée par Hervé.
- **Suivi BAT1 → BAT2** : chaque correction du BAT1 vérifiée une par une, avec son compte (« 37
  demandées, 35 faites, 2 non faites : n° 12 et 30 ») ; dates et validation dans le tableau « BAT » du
  registre. La validation est une décision d'Hervé et de l'éditeur, jamais d'AURA.

---

## 7. Mémoire de traduction

Fichier : `Références/Segments/Segments_<Gamme>.csv`, colonnes `EN;FR;produit;date`, séparateur
point-virgule, UTF-8. C'est la mémoire d'Hervé : on y ajoute, on n'y efface rien.

**Nourrir la mémoire** — seulement avec du texte validé (livraison acceptée ou produit publié), jamais
avec un brouillon :

```
python3 "${CLAUDE_SKILL_DIR}/scripts/segments.py" aligner cartes_validees.xlsx --col-en Text --col-fr "Texte FR" \
    --produit "Extension Le Guet" --date 2026-11-20 \
    --memoire "<HERVÉ WORLD>/Références/Segments/Segments_<Gamme>.csv" --sortie "<HERVÉ WORLD>/Livrables/<Projet>/segments_a_ajouter.csv"
```

Le script écrit les lignes nouvelles dans un fichier à part (jamais d'écrasement), écarte ce qui est
déjà en mémoire, et signale un même texte anglais déjà traduit autrement : AURA le montre à Hervé,
rien n'est remplacé. Hervé peut retirer de ce fichier à part les lignes qu'il ne veut pas garder.

<!-- [R-32] -->
**Ajouter à la mémoire** — par le programme, jamais en réécrivant le CSV à la main :

```
python3 "${CLAUDE_SKILL_DIR}/scripts/segments.py" ajouter "<HERVÉ WORLD>/Livrables/<Projet>/segments_a_ajouter.csv" \
    --memoire "<HERVÉ WORLD>/Références/Segments/Segments_<Gamme>.csv"
```

Le programme pose d'abord une copie datée de la mémoire dans `Core/Archives/`, ajoute les lignes à la
fin dans une copie, la recompte, et ne remplace la mémoire que si « avant + ajoutés = après » et si les
lignes d'avant sont restées identiques ; sinon il s'arrête sans rien toucher. Une ligne déjà en mémoire
n'est pas reprise. AURA rapporte à Hervé les trois nombres (avant, ajoutés, après).

**Réutiliser** — au début d'un nouveau produit, ou d'une réimpression :

```
python3 "${CLAUDE_SKILL_DIR}/scripts/segments.py" chercher regles_extension.docx \
    --memoire "<HERVÉ WORLD>/Références/Segments/Segments_<Gamme>.csv" --sortie "<HERVÉ WORLD>/Livrables/<Projet>/reprise.md"
```

- **Identiques** : la traduction existante est proposée, après vérification du contexte : un même
  texte anglais peut demander une autre traduction si la mécanique diffère.
- **Proches** (75 % de ressemblance par défaut) : la traduction existante sert de modèle, avec l'écart
  mot à mot entre l'ancien et le nouvel anglais.
- **Le glossaire fait foi.** Si un terme du segment a changé de traduction ou de statut après la date
  du segment, le segment est périmé sur ce point : on suit le glossaire.

Rien n'est inséré dans la traduction sans qu'Hervé l'ait vu.

---

## Les scripts

| Script | Ce qu'il fait |
|---|---|
| `scripts/comparer_versions.py` | Passages modifiés, ajoutés, supprimés, déplacés entre deux versions d'un source ; caractères à retraduire ; contrôle à vide |
| `scripts/retroplanning.py` | Rétroplanning à rebours en jours ouvrés, jalon clé, marge, leviers chiffrés, ligne pour `Core/Suivi.md` |
| `scripts/titres_publies.py` | Contrôle « titre déjà publié » contre le registre et le glossaire |
| `scripts/segments.py` | Mémoire de traduction : `chercher` (identiques et proches), `aligner` (lignes à ajouter) et `ajouter` (ajout en fin de mémoire, avec sauvegarde et recomptage) |
| `scripts/commun.py` | Règles communes aux quatre scripts (normalisation, lecture des tableaux, colonne désignée par son en-tête, mémoire, fichier produit jamais écrit par-dessus un fichier existant) |
| `scripts/lecture.py` | Lecture des .docx, .xlsx, .csv, .tsv, .txt, .md (copie identique partagée entre les skills) |

Bibliothèque standard de Python uniquement. Formats lus : .docx, .xlsx, .csv, .tsv, .txt, .md. Un PDF
se lit par AURA elle-même (pas par script).

## Ce que ce skill ne fait pas

- Il ne décide d'aucun terme, d'aucun levier de planning, d'aucune validation de BAT : il prépare, compte
  et signale ; Hervé décide.
- Il n'annote pas les PDF et n'extrait pas leur texte par script.
- Il n'envoie rien : tout ce qui part chez un tiers est un brouillon qu'Hervé envoie.

## Livrable d'une séance

- Le registre de gamme créé ou mis à jour (lignes ajoutées, rien d'effacé).
- Selon la demande : un rétroplanning, un brief, une répartition de lots, un tableau de corrections et
  sa synthèse, un rapport de comparaison de versions, une liste de corrections BAT, un rapport de
  segments réutilisables.
- Les fils en attente (jalon menacé, lot en retard) dans `Core/Suivi.md`.
- À la fin, une ligne honnête sur ce qui n'a pas été vérifié.
