# Modèle du registre de gamme — `Core/Gammes/<Gamme>.md`

Le registre est la mémoire d'Hervé sur une gamme : ce qui a été publié, ce qui est en cours, qui travaille
dessus, ce qui a changé dans la version originale. Il appartient à la **couche mémoire** : AURA le crée
à partir de ce modèle quand il n'existe pas (avec l'accord d'Hervé), puis ne fait qu'y ajouter ou y
mettre à jour des lignes. Il n'est jamais réécrit en entier, jamais supprimé.

## Nommage

- Un registre par gamme : `Core/Gammes/<Nom de la gamme tel que l'éditeur l'écrit>.md`, accents et
  espaces conservés. Les caractères interdits dans un nom de fichier Windows (`\ / : * ? " < > |`)
  sont remplacés par un tiret.
- Le même nom sert au glossaire (`Glossaires/Glossaire_<Gamme>.xlsx`) et à la mémoire de traduction
  (`Références/Segments/Segments_<Gamme>.csv`).
- Avant d'en créer un, AURA liste `Core/Gammes/` et compare les noms sans tenir compte de la casse,
  des accents, des espaces ni de la ponctuation : « Les Marches de Brumeval » et
  « marches-de-brumeval » désignent le même registre. En cas de doute, elle demande.

## Règles d'écriture

<!-- [I-06] -->
- **Un fait, un seul foyer.** Le registre ne recopie pas ce qui vit ailleurs : les termes et leur
  statut vivent au glossaire (skill `glossaire`), les contacts et les clauses du contrat dans la fiche
  éditeur (skill `brief-editeur`), les questions à l'éditeur dans `Core/Questions_Editeurs.md`, les
  fils en attente dans `Core/Suivi.md`. Le registre y renvoie.
- **On n'efface pas.** Une ligne devenue fausse passe au statut « Archivé » avec la date et la raison ;
  elle reste lisible.
<!-- [I-31] -->
- **Copie datée avant une modification en masse** (import de 300 titres publiés, réorganisation d'un
  tableau) : `Core/Archives/<Gamme>_registre_avant_AAAA-MM-JJ_HHhMM.md`, jamais écrasée.
- Les dates s'écrivent AAAA-MM-JJ. Les chiffres (caractères, cartes, lots) sont comptés sur les
  fichiers, jamais estimés.

---

## Le modèle (à copier tel quel à la création)

```markdown
# Registre de gamme — <Nom de la gamme>

> Mémoire d'Hervé sur cette gamme. AURA ajoute et met à jour des lignes ; elle ne réécrit jamais le
> fichier en entier et n'efface rien (une ligne périmée passe « Archivé »).
> Créé le AAAA-MM-JJ. Dernière mise à jour : AAAA-MM-JJ.

## Identité

- Gamme : <nom tel que l'éditeur l'écrit>
- Éditeur de la version française : <nom> — fiche : Core/Editeurs/<Éditeur>.md
- Éditeur de la version originale / ayant droit : <nom>
- Rôle d'Hervé sur la gamme : <responsable de gamme / traducteur / relecteur>
- Glossaire : Glossaires/Glossaire_<Gamme>.xlsx
- Mémoire de traduction : Références/Segments/Segments_<Gamme>.csv

## Licence et termes officiels imposés

- Licence : <oui / non>. Ayant droit : <nom>.
- Document de référence fourni : <glossaire officiel, bible de l'univers…>, version du <date>.
- Qui valide les termes de licence, et sous quel délai : <…>
- Validation de la version française par l'ayant droit avant impression : <oui / non>, délai annoncé :
  <N jours ouvrés> (source, date). C'est la durée donnée au rétroplanning (étape « validation »).
- Les termes imposés eux-mêmes sont au glossaire (SOURCE = « glossaire officiel de licence, <document>,
  <date> »). Ici, seulement le cadre.

## Produits

| Réf. | Produit | Type | Version source reçue | Traducteur | Relecteur | Statut | Remise imprimeur | Sortie | Notes |
|---|---|---|---|---|---|---|---|---|---|

Type : boîte de base, extension, réimpression, promotionnel, livret, autre.
Statut : Annoncé → Sources reçues → Traduction → Relecture → Mise en page → BAT1 → BAT2 →
Remis à l'imprimeur → Publié ; ou Abandonné.

## Calendrier en cours

Calcul du AAAA-MM-JJ, fait avec la capacité d'Hervé lue dans Core/Profile.md ce jour-là : <N> caractères
par jour ouvré. (Un relevé daté : la capacité elle-même ne vit que dans Core/Profile.md.)

| Produit | Étape | Début au plus tard | Fin au plus tard | Responsable | État |
|---|---|---|---|---|---|

## Lots

| Produit | Lot | Contenu (cartes, pages, chapitres) | Caractères | Attribué à | Remis le | Échéance | Livré le | Relu le | Statut |
|---|---|---|---|---|---|---|---|---|---|

Statut d'un lot : À attribuer → Attribué → Livré → Relu → Intégré.

## Équipe

| Prénom | Rôle (traducteur, relecteur, maquettiste, contact éditeur) | Lots ou produits | Capacité donnée | Notes |
|---|---|---|---|---|

Les coordonnées restent dans la fiche éditeur ou dans le carnet d'Hervé, pas ici.

## Titres de cartes publiés

| EN | FR | Produit | Réf. carte | Date |
|---|---|---|---|---|

Un titre publié ne change pas sans erratum. Un titre qui est aussi un terme de jeu (cité dans les
règles ou sur d'autres cartes) vit au glossaire, statut Gelé, colonne PUBLIÉ DANS : il n'est pas
recopié ici.

## Termes gelés

Pas de liste ici : le glossaire fait foi (filtre STATUT = Gelé).
Dernier gel : AAAA-MM-JJ, à la publication de <produit>.

## Versions du texte source

| Produit | Fichier source | Version | Reçue le | Comparée le | Passages modifiés / ajoutés / supprimés | Caractères à retraduire |
|---|---|---|---|---|---|---|

## Errata

| N° | Date | Produit | Origine (document de l'éditeur VO, date) | Passage (carte, page, règle) | Correction VO | Correction VF | Report (glossaire, texte, segments) | Statut |
|---|---|---|---|---|---|---|---|---|

Statut : À traiter → Traduit → Reporté dans la VF → Intégré à la réimpression <réf.>. Un erratum qui n'a
pas encore ce dernier statut reste à intégrer à la prochaine réimpression.

## BAT

| Produit | Cycle | Épreuve reçue le | Retours envoyés le | Corrections demandées | Corrections vérifiées | Validé le (par qui) |
|---|---|---|---|---|---|---|

## Historique du registre

- AAAA-MM-JJ : création.
```

---

<!-- [R-51] -->
La liste des statuts d'un erratum ci-dessus est la seule : le SKILL.md (partie 5) y renvoie.

## Exemple de lignes remplies [EXEMPLE FICTIF]

<!-- [I-30] -->
Gamme inventée, pour montrer la forme. Aucun de ces noms ne désigne un jeu ou un éditeur réel.

| Réf. | Produit | Type | Version source reçue | Traducteur | Relecteur | Statut | Remise imprimeur | Sortie | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P1 | Les Marches de Brumeval — boîte de base | boîte de base | règles v1.2 du 2026-02-10 | Hervé | Camille | Publié | 2026-04-15 | 2026-09 | |
| P2 | Brumeval — extension Le Guet | extension | règles v1.0 du 2026-10-05 | Hervé + Sacha (lot 2) | Camille | Traduction | 2027-03-15 | | rétroplanning du 2026-10-06 |

| N° | Date | Produit | Origine | Passage | Correction VO | Correction VF | Report | Statut |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-10-20 | P1 | FAQ de l'éditeur VO du 2026-10-18 | règle 4.2, déplacement | « up to 2 spaces » → « up to 3 spaces » | « 2 cases maximum » → « 3 cases maximum » | texte VF, segments | Reporté dans la VF |
