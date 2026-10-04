# Le registre des questions aux éditeurs — `Core/Questions_Editeurs.md`

Une réponse écrite de l'éditeur est une référence : elle tranche un terme, une règle, un litige
éventuel, et elle resservira sur l'extension suivante. Le registre garde chaque question, de sa
naissance à sa réponse. Il appartient à la **couche mémoire** d'Hervé : AURA le crée à partir de ce
modèle s'il n'existe pas, y ajoute des lignes et met à jour leur statut ; elle n'efface jamais une
ligne et ne réécrit jamais le fichier en entier.

<!-- [R-28] -->
**Ce fichier est la seule définition de la structure du registre.** La graine que pose la mise à jour
(`Core/Questions_Editeurs.md`) est la copie exacte du bloc « Le fichier à sa création » ; les autres
skills (`qa-coherence`, `gestion-gamme`, `traduction-jeux`…) renvoient au skill `brief-editeur` sans
recopier les colonnes.

## Le fichier à sa création (copie exacte de la graine)

```markdown
# Questions aux éditeurs

> Registre des questions posées aux éditeurs et de leurs réponses — mémoire d'Hervé.
> Une ligne n'est jamais effacée : une question devenue sans objet passe « Retirée ».
> Numéros uniques dans tout le fichier, jamais réutilisés.
> Une section par éditeur, ajoutée par AURA à la première question qui le concerne.
```

## La section d'un éditeur (ajoutée à sa première question)

```markdown
## <Nom de l'éditeur tel qu'il l'écrit>

| N° | Produit | Référence (carte, page, règle) | Question | Proposition d'Hervé | Statut | Réponse | Date | Impact glossaire | Posée par |
|---|---|---|---|---|---|---|---|---|---|
```

Le titre de section porte le même nom que la fiche `Core/Editeurs/<Éditeur>.md`. Avant d'ajouter une
section, AURA vérifie qu'il n'en existe pas déjà une pour cet éditeur sous une autre graphie.

## Un registre d'une autre forme

Le fichier a pu être créé sous une autre forme : un seul tableau avec une colonne « Éditeur » et une
colonne « Date réponse », sans « Posée par » (la graine de la première publication de la version 3.0),
ou un tableau fait par Hervé. AURA ne le réécrit pas en entier et ne mélange jamais deux formes dans un
même tableau :

- **tableau encore vide** (aucune ligne de question) : AURA propose à Hervé de le remplacer par le
  bloc « Le fichier à sa création » ; elle ne le fait qu'avec son accord, et rien d'autre n'est touché ;
- **tableau qui contient des questions** : il reste tel quel, à sa place. Ses lignes gardent leurs
  numéros et se mettent à jour dans leurs propres colonnes (statut, réponse). Les questions nouvelles
  vont dans les sections par éditeur, ajoutées en dessous ; leur numéro suit le plus grand numéro de
  tout le fichier, ancien tableau compris.

## Les colonnes

| Colonne | Contenu |
|---|---|
| N° | Entier unique dans tout le fichier : le suivant est le plus grand numéro existant + 1. Jamais réutilisé, même pour une question retirée. C'est ce numéro qui figure dans l'e-mail. |
| Produit | Le produit de la gamme, comme dans le registre de gamme. |
| Référence | Carte (identifiant), page, numéro de règle : ce qui permet à l'éditeur de retrouver le passage. |
| Question | Le texte anglais en cause, cité, puis la question en une phrase. |
| Proposition d'Hervé | Sa traduction provisoire ou ses options. Jamais vide : on ne pose pas de question ouverte (voir le SKILL.md). |
| Statut | **À envoyer** → **Envoyée** → **Répondue** → **Close** ; ou **Retirée** (devenue sans objet, gardée pour trace). |
| Réponse | Le texte de l'éditeur, cité fidèlement, ou résumé et marqué « résumé ». |
| Date | Historique court : « posée 2026-10-03 · envoyée 2026-10-05 (lot 2) · répondue 2026-10-12 ». |
| Impact glossaire | « aucun », ou « terme validé : EN → FR, reporté au glossaire le AAAA-MM-JJ », ou « proposition refusée : FR retenu par l'éditeur … ». |
| Posée par | « Hervé » ou le prénom du traducteur de l'équipe dont vient la question. |

Ces statuts sont ceux des **questions**. Les statuts des **termes** (Brouillon, À confirmer, Confirmé,
Gelé, Archivé) sont ceux du glossaire et ne se mélangent pas avec eux.

## Le cycle d'une question

1. **Naissance** : dès qu'une question apparaît pendant la traduction (ou arrive d'un traducteur de
   l'équipe, fusionnée par le skill `gestion-gamme`), elle entre au registre, statut « À envoyer ».
   On n'attend pas la fin de la séance.
<!-- [I-08] -->
2. **Avant chaque envoi**, AURA revérifie chaque ligne « À envoyer » : la réponse est-elle déjà
   arrivée par un autre e-mail ? le glossaire a-t-il été mis à jour depuis ? la même question a-t-elle
   déjà une réponse sur un produit précédent ? Une ligne périmée passe « Retirée » (avec la raison)
   au lieu d'être envoyée.
3. **Envoi groupé** : un e-mail par éditeur et par produit, avec les lignes « À envoyer » (modèle A de
   `references/modeles-emails.md`). Hervé relit et envoie lui-même. **AURA ne passe une ligne à
   « Envoyée » que lorsqu'Hervé confirme l'avoir envoyée**, avec la date et le numéro du lot.
<!-- [I-04] -->
4. **Fil en attente** : à l'envoi, une ligne dans `Core/Suivi.md` (« questions n° 12 à 18 envoyées à
   <Éditeur> le 2026-10-05, réponse demandée avant le 2026-10-12 »). Elle est close à la réponse selon
   la règle des fils du skill `noyau` (jamais effacée), jamais recopiée telle quelle d'une séance à
   l'autre. <!-- [R-27] -->
5. **Réponse** : chaque réponse est reportée sur sa ligne (statut « Répondue »), puis appliquée :
   glossaire (skill `glossaire`), texte en cours, traducteur concerné. Quand tout est reporté, la ligne
   passe « Close ».
6. **Sans réponse** passé le délai demandé : AURA propose une relance (modèle F), une seule fois par
   délai écoulé, et seulement si Hervé est d'accord.

<!-- [I-06] -->
## Une réponse « terme validé »

La décision va au **seul glossaire**, par le skill `glossaire` : traduction validée, statut
« Confirmé » (ou ce que la réponse indique), SOURCE = « échange éditeur du JJ/MM/AAAA, question n° N »,
proposition refusée gardée en NOTES le cas échéant. Le registre ne fait que dire où la décision a été
reportée (colonne « Impact glossaire »). Rien n'est écrit dans `Core/Preferences.md` : un terme n'est
pas une préférence de style.

Si la réponse contredit un terme **Gelé** (déjà imprimé), ce n'est pas une simple mise à jour : c'est un
erratum, à traiter avec le skill `gestion-gamme` et le skill `glossaire`.

## Exemple de lignes [EXEMPLE FICTIF]

<!-- [I-30] -->
Jeu, éditeur, cartes et réponses inventés pour montrer la forme.

| N° | Produit | Référence | Question | Proposition d'Hervé | Statut | Réponse | Date | Impact glossaire | Posée par |
|---|---|---|---|---|---|---|---|---|---|
| 12 | Brumeval — extension Le Guet | règle 3.4 | « Flummox the wizard » : nom propre d'un personnage, ou sorcier générique ? | Nom propre, gardé tel quel : « Flummox le sorcier » | Close | « Nom propre, à garder. » (e-mail du 12/10) | posée 2026-10-03 · envoyée 2026-10-05 (lot 2) · répondue 2026-10-12 | terme validé : Flummox → Flummox, reporté au glossaire le 2026-10-12 | Hervé |
| 13 | Brumeval — extension Le Guet | carte C044 | « attack track » : existe-t-il un terme maison déjà employé sur d'autres titres ? | « piste d'attaque » | Envoyée | | posée 2026-10-04 · envoyée 2026-10-05 (lot 2) | | Sacha |
| 14 | Brumeval — extension Le Guet | mise en place, p. 4 | « Discard face-up » : la défausse est-elle visible de tous ? | « Défaussez face visible » | Retirée | | posée 2026-10-04 · retirée 2026-10-05 : réponse déjà donnée pour la boîte de base, question n° 3 | aucun | Hervé |
