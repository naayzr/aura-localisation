# La gamme dans la durée, et le relecteur

## Un glossaire pour toute la gamme, pas un par produit

<!-- [D-18] -->
L'extension ne repart pas de zéro et n'a pas son propre glossaire : elle enrichit le maître de la gamme.
Ce qui distingue les produits, c'est la colonne PUBLIÉ DANS (où le terme est imprimé) et la SOURCE (où il
est apparu). Pour un traducteur ou un éditeur qui ne travaille que sur un produit, on fait un **export**
(`gerer_glossaire.py exporter`), nommé par produit et daté ; le maître reste unique.

Au démarrage d'un nouveau produit de la gamme :
1. Contrôle du maître (`controle_glossaire.py`).
2. Lecture des termes Gelés : ils s'imposent au nouveau produit (titres de cartes réimprimées compris ;
   le registre des titres publiés est tenu par le skill `gestion-gamme`).
3. Parcours du nouveau source : chaque terme candidat est cherché (recherche complète, SKILL.md section 5)
   avant d'entrer en Brouillon.

## Deux traductions pour le même terme dans deux produits

1. **Trouver l'origine** : choix fait au passage (jamais formalisé) ou décision tranchée et imprimée ?
   Les DÉFINITIONS MÉCANIQUES disent d'abord s'il s'agit vraiment du même terme (un sens mécanique = un
   terme ; deux sens = deux lignes, ce n'est pas un conflit).
2. **Choisir la version qui continue**, dans cet ordre : statut (Gelé > Confirmé > Brouillon) → cohérence
   avec les termes liés (Épuiser / Épuisé / Réactiver [EXEMPLE FICTIF]) → sonorité → préférence de
   l'éditeur. Hervé tranche ; AURA présente les éléments.
3. **Documenter** : NOTES et CHANGELOG. Si le produit est encore en cours, on corrige le texte (procédure
   « corriger un terme partout »). Si les deux sont déjà imprimés, l'**anomalie historique** reste visible :
   la version qui ne continue pas passe Archivé, avec PUBLIÉ DANS rempli et NOTES « imprimé dans <produit>,
   remplacé par T-… à partir de <produit> ». On ne l'efface pas.

## L'éditeur change d'avis sur un terme déjà imprimé

[EXEMPLE FICTIF] *Sanctuaire* est imprimé dans trois boîtes ; l'éditeur veut *Sanctum* à partir de la
quatrième.
1. La ligne *Sanctuaire* (Gelé) passe **Archivé** : `modifier --id T-… --champ STATUT=Archivé --raison
   "remplacé par Sanctum à partir de la boîte 4, décision éditeur du JJ/MM" --par "éditeur (courriel du JJ/MM)"`.
2. Une nouvelle ligne *Sanctum*, même anglais, NOTES « remplace T-… à partir de la boîte 4 » ; elle passe
   Confirmé, puis Gelé à l'impression.
3. Le CHANGELOG garde la raison complète ; la version monte d'un rang (2.0).
4. L'ancien terme est cherché partout (livrables en cours, segments) avant remplacement, liste montrée à
   Hervé d'abord.
5. L'erratum lui-même (journal des errata, report sur les réimpressions) est tenu par le skill
   `gestion-gamme`.

L'incohérence est réelle et documentée, pas effacée.

## Licence : les termes imposés par l'ayant droit

Un univers sous licence arrive souvent avec un glossaire officiel. Ses termes entrent par l'import
(Brouillon), SOURCE = « glossaire officiel de licence, <document>, <version ou date> », puis Hervé les
valide explicitement (un lot suffit). Un traducteur ou un relecteur ne les discute pas : il signale. Un
terme de licence qui manque se demande à l'ayant droit (registre `Core/Questions_Editeurs.md`), il ne
s'invente pas.

## Préparer le glossaire pour un traducteur ou un relecteur

`gerer_glossaire.py exporter Glossaires/Glossaire_<Gamme>.xlsx --sortie "Livrables/<Projet>/Glossaire_<Gamme>_<Produit>_AAAA-MM-JJ.xlsx" --pour relecteur`
(`--pour traducteur` pour un brief de traduction du skill `gestion-gamme`).

La copie contient :
- un onglet **Lisez-moi** en premier : ce que chaque statut permet (Confirmé et Gelé s'appliquent sans
  discussion, À confirmer s'applique en attendant l'éditeur, Brouillon se conteste en commentaire), la
  règle « un terme absent ne s'invente pas, il se demande », le sens des colonnes GENRE, NOMBRE, ÉLISION ;
  pour un relecteur, la manière de rendre ses remarques ;
- l'onglet **Termes** sans les colonnes internes (NOTES, SOURCE), sans les termes archivés (sauf
  `--avec-archives`), avec une colonne « ce que le statut permet » et, pour un relecteur, deux colonnes
  **RETOUR RELECTEUR** et **RÉPONSE D'HERVÉ**. La colonne RÉF. (identifiant) sert à réintégrer les
  retours ; on demande de ne pas la modifier.

AURA prépare le fichier ; c'est Hervé qui l'envoie (jamais d'envoi par AURA). S'il préfère un PDF pour un
relecteur ponctuel, il l'enregistre en PDF depuis Excel ; les retours arrivent alors par courriel.

## Les règles données au relecteur

- Il écrit uniquement dans RETOUR RELECTEUR, en commençant par un code : **[OK]** terme approuvé ·
  **[?]** question · **[MOD]** suggestion, avec la proposition · **[ERR]** erreur constatée, avec l'endroit.
- Sur un terme Gelé, il peut signaler ; il ne tranche pas.
- Il ne modifie ni les autres colonnes, ni l'ordre des lignes, ni RÉF.

## Intégrer les retours

`gerer_glossaire.py retours "<fichier renvoyé>"` liste les remarques par code, avec leur nombre exact.
On les traite dans cet ordre :
- **[ERR]** d'abord : corriger le glossaire **et** le texte traduit, puis chercher si le terme fautif
  apparaît dans d'autres projets (procédure « corriger un terme partout »).
- **[MOD]** : Hervé évalue. Retenu → `modifier` (avec la raison « proposition du relecteur, retenue le
  JJ/MM »). Écarté → la raison va dans RÉPONSE D'HERVÉ.
- **[?]** : la réponse va dans RÉPONSE D'HERVÉ ; si la question vient d'un manque de clarté, on précise la
  DÉFINITION MÉCANIQUE ou les NOTES du terme.
- **[OK]** : rien à faire ; on peut noter en NOTES que le terme a passé la relecture.
- **Remarque sans code** : AURA la classe avec Hervé avant de la traiter.

Une même erreur relevée par plusieurs traducteurs signale souvent un terme mal expliqué : AURA propose de
préciser sa définition ou ses notes.
