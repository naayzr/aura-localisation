---
name: qa-coherence
description: "Vérification CIBLÉE d'un point précis dans un texte traduit de jeu de société, avec l'endroit exact de chaque occurrence : un renvoi (« voir règle 5.2 » mène-t-il à la bonne règle ?), la numérotation des règles (trous, doublons, règle absente), un symbole ou une icône (nom, sens mécanique), ou un mot qui traîne partout (variante, nom anglais oublié). Cherche par script dans le .docx, .xlsx ou .csv déposé, tient la table des renvois et le dictionnaire des symboles, prépare les questions à l'éditeur. Quand Hervé dit « vérifie ce renvoi », « les numéros de règles sont-ils bons ? », « ce symbole est-il le bon ? », « cherche toutes les occurrences de… », « ce mot traîne-t-il encore quelque part ? ». Pas pour relire tout un texte (relecture-multi-agents), la typographie (typographie-fr), la longueur et les balises (controle-longueur), le choix d'un terme (glossaire)."
---

# qa-coherence — vérifier un point précis, partout, avec l'endroit exact

> Les exemples de ce skill sont des **[EXEMPLE FICTIF]** : numéros de règles, noms de cartes et de symboles construits pour l'illustration, tirés d'aucun jeu publié.

## Ce skill, ou un autre <!-- [D-29] -->

Ce skill répond à **une** question précise sur un texte : un renvoi, une numérotation, un symbole, un mot à retrouver partout. Il ne donne **pas** de verdict de livraison.

| Hervé demande | Skill |
|---|---|
| « vérifie ce renvoi », « la règle 5.2 existe-t-elle encore ? », « ce symbole, c'est le bon ? », « cherche toutes les occurrences de *Bouger* » | `qa-coherence` (ce skill) |
| « relis tout avant livraison », « est-ce que je peux livrer ? », « relecture complète » | `relecture-multi-agents` (qui utilise les scripts de ce skill) |
| espaces insécables, guillemets, apostrophes, majuscules | `typographie-fr` |
| texte qui déborde, balises ou icônes perdues entre l'anglais et le français | `controle-longueur` |
| le bon terme français, la décision sur un terme | `glossaire` |

Quand la demande est ambiguë (« vérifie le chapitre 3 » : un point, ou tout ?), AURA pose une seule question avant de commencer.

## Ce qu'Hervé obtient

1. **La réponse au point demandé**, chiffrée et localisée : chaque occurrence avec son repère (§ 12 = 12e paragraphe du Word, `Cartes!L5C3` = cellule), comptée par script sur le fichier entier — jamais « à vue ».
2. Si le point le demande : **la table des renvois** ou **le dictionnaire des symboles**, construits ou complétés.
3. **Les questions pour l'éditeur** quand l'erreur vient de la version originale (VO), inscrites au registre `Core/Questions_Editeurs.md` (le skill `brief-editeur` les groupe ensuite en courriel).
4. **Ce qui n'a pas été vérifié**, dit clairement (une zone non lue, une numérotation que le script ne voit pas).

## Les principes

- **Signaler les erreurs de la VO, ne jamais les corriger en silence.** Une correction non documentée engage la responsabilité du traducteur.
- **Un renvoi de règle se vérifie sur le texte ; un renvoi de page, seulement sur l'épreuve mise en page.** La traduction allonge le texte et les pages glissent. Le contrôle des épreuves relève du skill `gestion-gamme`.
- **Une passe = un objectif.** On ne mélange pas renvois, symboles et typographie dans la même lecture.
- **Avant de croire un « 0 occurrence » ou un « 0 anomalie »,** on essaie la passe sur une copie sabotée exprès : c'est une règle du skill `noyau` (règles de travail).

---

## Comment AURA travaille : le fichier, puis le script <!-- [D-34] -->

AURA fait la recherche **elle-même**, par script, sur le fichier d'Hervé. Hervé n'a ni expression régulière à écrire, ni macro, ni ligne de commande à taper.

1. **Le fichier** : Hervé le dépose dans la conversation, ou il est déjà dans l'espace de travail de la tâche (sa copie de travail dans `Livrables/<Projet>/`). On ne travaille jamais sur l'original de l'éditeur. Avant de lancer un script, AURA applique la règle « Les programmes et le dossier d'Hervé » du skill `noyau` (le programme voit-il le fichier ? sinon, le glisser ; sans lecture par le programme, aucun contrôle n'est présenté comme fait).
2. **Les scripts**, dans `${CLAUDE_SKILL_DIR}/scripts/` (Python, bibliothèque standard, lisent .docx, .xlsx, .csv, .tsv, .txt, .md) ; chaque commande se lance avec le programme et les fichiers en chemins complets (règle « Écrire une commande » du skill `noyau`) : <!-- [R-29] -->
   - `renvois.py TEXTE [--source VO] [--regles LIVRET]` — renvois internes et numéros de règle (point 2).
   - `chercher.py FICHIER MOT [MOT…] [--liste fichier] [--colonne EN] [--si STATUT=Archivé] [--debut | --racine] [--strict]` — toutes les occurrences d'un ou plusieurs mots, avec leur endroit et leurs formes (points 3 et 4).
   - Chacun a un essai intégré sur une copie sabotée : `--auto-test`. AURA le lance la première fois qu'elle s'en sert dans une tâche ; s'il échoue, elle ne se fie pas au script et le dit.
3. **Le résultat** : AURA montre le bilan chiffré et les endroits, puis propose les corrections. Elle ne modifie le fichier que sur une copie (`_v2`, `_v3`…), jamais l'original.

Si Hervé préfère chercher lui-même dans Word, les procédures **valides** (Word n'utilise pas les expressions régulières habituelles) sont dans `references/recherche-word.md`.

---

## 1. Les erreurs que ce skill sait trouver

1. **Renvoi cassé** — « voir règle 5.2 », mais la 5.2 de la traduction ne parle pas de ce que le texte promet : la numérotation a glissé, ou le contenu a bougé.
2. **Numéro de règle faux** — « 5,2 » au lieu de « 5.2 », « règle 52 » au lieu de « 5.2 » (relevé à lire ; la comparaison avec la VO le montre aussi quand la VO y a un renvoi « 5.2 »), deux règles 6.1, une 5.3 qui manque, une règle de la VO absente de la traduction. Invisible à la relecture, fatal à la table.
3. **Symbole mal identifié** — deux icônes proches confondues dans le texte : le coût pris pour un gain, l'effet sur soi pris pour l'effet sur l'adversaire.
4. **Un point incohérent** — un mot qui traîne (« Bouger » quand la gamme dit « Déplacer »), un nom anglais oublié, une majuscule appliquée ici et pas là.

Ce que ce skill ne cherche pas, et qui va ailleurs : <!-- [D-20] -->
- **La typographie française** (espaces, guillemets, apostrophes, majuscules accentuées, majuscule des termes de jeu) : skill `typographie-fr`. Ce skill n'en énonce aucune règle.
- **Le texte tronqué ou trop long, et les balises ou icônes perdues** (`{icon_sword}`, `<b>`, `[damage]`) : skill `controle-longueur`, qui a le script de contrôle segment par segment.

<!-- [R-40] [R-53] -->
**Les variantes d'un terme au regard du glossaire** se cherchent ici, avec deux limites à dire à Hervé :
- **les variantes connues** — les anciens termes que le glossaire a archivés — se trouvent par script,
  chacune avec son endroit : `python3 "${CLAUDE_SKILL_DIR}/scripts/chercher.py" "<texte>" --liste "<HERVÉ WORLD>/Glossaires/Glossaire_<Gamme>.xlsx" --colonne FR --si STATUT=Archivé --racine`
  (section 4). Le contrôle `controle_glossaire.py` du skill `glossaire` ne lit que le glossaire, jamais
  un texte traduit : il ne trouve aucune variante dans une traduction ;
- **une variante jamais entrée au glossaire** (« Bouger » quand seul « Déplacer » y figure) ne se trouve
  par aucun script : seulement à la lecture (skill `relecture-multi-agents`, lecture par lots). AURA ne
  dit donc jamais « aucune variante » sur la seule foi d'un script.

**Quand le temps manque** (moins de 48 heures avant la livraison) : d'abord les renvois et les numéros de règle — ce sont eux qui rendent un jeu injouable — puis les symboles.

---

## 2. Renvois et numéros de règle

**La méthode.**
1. **Lancer `renvois.py`** sur la traduction, avec la VO si Hervé l'a (`--source`). Pour un fichier de cartes qui renvoie au livret, ajouter le livret avec `--regles`. Le script liste : les renvois vers une règle introuvable, les numéros définis deux fois, les trous dans une suite, les numéros écrits avec une virgule, les règles de la VO absentes de la traduction, les renvois en nombre différent entre VO et traduction, et tous les renvois de page. Le script ne juge que les numéros à plusieurs niveaux (5.2). Un renvoi à un seul niveau (« règle 52 », « voir règle 7 », « règle n° 7 ») est relevé juste après un mot-clé (règle, section, chapitre, paragraphe, §) ou dans la suite d'une liste de renvois (« règles 3, 4 et 13 ») ; s'il ne correspond à aucun titre « Règle 7 — … », « Chapitre 7 » ni à des règles 7.1, 7.2, il sort « À lire » : zone du plateau, autre livret, étape d'une liste ou faute, le programme ne peut pas trancher. AURA lit chaque phrase et dit ce qu'elle en conclut. « voir 7 » seul n'est pas relevé : AURA le cherche à la lecture. La faute « règle 52 » pour « 5.2 » se voit aussi dans la comparaison avec la VO (le 5.2 perdu). <!-- [R-62] -->
2. **Vérifier le contenu de chaque renvoi** : pour chaque « voir règle X.Y », ouvrir la règle X.Y et vérifier qu'elle parle bien de ce que le texte promet. Le script trouve les renvois ; il ne juge pas leur sens.
3. **Vérification dans les deux sens** : si la 4.3 renvoie à la 7.1, la 7.1 traite-t-elle bien du même sujet ?
4. **Renvois de page** : tous marqués `[PAGE À CONFIRMER]` dans la traduction. Ils se remplissent sur l'épreuve mise en page, jamais sur le Word. Le script compte ceux qui n'ont pas encore le marqueur.

**Limite à dire à Hervé** : si les numéros de règles sont produits par la **numérotation automatique** de Word, ils ne sont pas dans le texte et le script ne les voit pas. Il l'écrit en tête de son rapport ; il compare alors aux règles de la VO, ou au fichier donné par `--regles`. Sinon l'existence des règles visées n'est pas vérifiée, et AURA le dit.

**Renvois stables et renvois volatils.** Un numéro de règle reste fiable tant que la structure ne change pas ; un numéro de page n'est valable que sur le fichier final. Les deux ne se vérifient pas au même moment.

**Une erreur dans la VO** se signale, ne se corrige pas en silence. On garde le renvoi de la VO dans la traduction en attendant la réponse, et la question part au registre `Core/Questions_Editeurs.md`, en clair, sans code interne. [EXEMPLE FICTIF] :
> Règle 6.2, 3e ligne : la VO renvoie à la règle 3.4, qui traite des ressources et non du déplacement. Faut-il lire 3.5 (Mouvement) ? En attendant votre réponse, la traduction garde « règle 3.4 ».

La table des renvois (modèle), le rapport des renvois et le format complet d'une question : `references/renvois-et-numeros.md`.

---

## 3. Symboles et icônes <!-- [D-22] -->

**Le dictionnaire des symboles se construit avant de traduire**, pas après : description visuelle, nom officiel anglais, nom français retenu, signification mécanique, première occurrence. La description visuelle sert à retrouver le symbole quand la planche définitive arrive plus tard. Modèle et méthode : `references/symboles.md`.

**Le piège des symboles qui se ressemblent.** Deux icônes proches peuvent avoir des sens opposés : l'une est un coût (on dépense), l'autre un gain (on reçoit) ; l'une s'applique à vous, l'autre à l'adversaire ; l'une est permanente, l'autre temporaire. [EXEMPLE FICTIF] Dans un jeu imaginaire, les jetons *Brume* et *Ombre* ont la même forme ronde et des teintes voisines une fois imprimés en petit ; une flèche montante ou descendante distingue seule *Peur produite* de *Peur exigée*. Ce skill ne cite aucun cas tiré d'un jeu réel : une affirmation sur un jeu publié n'entre ici qu'avec sa source.

**Méthode.** Au-delà d'une dizaine de symboles distincts, demander à l'éditeur un document de référence — même une capture de la planche avec les noms officiels — et faire valider le dictionnaire avant de traduire.

**Après la traduction — un balayage par script :**
1. `chercher.py` avec la liste des noms anglais des symboles (`--liste`, ou directement le glossaire : `--liste Glossaire.xlsx --colonne EN`) : chaque nom anglais resté dans la traduction sort avec son endroit. Un nom gardé en anglais exprès sort aussi : chaque occurrence se regarde.
2. `chercher.py` avec les variantes françaises non retenues : chaque forme non conforme au dictionnaire sort avec son endroit.
3. La majuscule de ces noms : la convention de l'éditeur (fiche éditeur, skill `typographie-fr`) appliquée partout, vérifiée avec `--strict`.
4. Que chaque balise d'icône soit présente et intacte d'une langue à l'autre : skill `controle-longueur`.

---

## 4. La cohérence d'un point, partout

Pour toute question du type « est-ce que X apparaît encore ? », « combien de fois ? », « où exactement ? » :
- `chercher.py fichier.docx "Bouger" "Déplacer" --racine` → les deux mots, leur nombre, leurs formes (Bouge, Bougez, Déplacez…) et chaque endroit. Par défaut la recherche ignore la casse et les accents (« deplacer » trouve « Déplacer ») ; `--strict` les respecte.
- `--debut` trouve les mots qui commencent par la forme donnée (« déplac » → déplacer, déplacez, déplacement).
- `--racine` coupe d'abord la terminaison : « Bouger » trouve aussi « bougez », « bouge » (et « bougie » : chaque occurrence se regarde). Sans cette option, « Bouger » ne trouve pas « Bougez ».
- `--liste noms.txt` cherche toute une liste (un mot ou une expression par ligne) ; `--liste Glossaire.xlsx --colonne FR --si STATUT=Archivé --racine` cherche toutes les formes refusées de la gamme.

AURA donne le nombre total et les endroits, puis la correction proposée. Si le mot vient d'une décision de terme, la correction passe par le glossaire (skill `glossaire`) : une décision de terme ne s'écrit qu'au glossaire.

---

## 5. Ce que la vérification laisse à la livraison <!-- [D-31] -->

Ce skill ne livre pas et ne dit pas « prêt à livrer » : c'est le rôle du skill `relecture-multi-agents`, avec les portes de livraison de `Core/_EN_COURS.md` (skill `noyau`).

Ce qu'il fournit au paquet de livraison :
- la table des renvois, avec les renvois de page marqués `[PAGE À CONFIRMER]` ;
- les questions à l'éditeur, numérotées, avec leur statut, au registre `Core/Questions_Editeurs.md` ;
- le dictionnaire des symboles validé, si le jeu en a un.

Le **courriel de livraison** se rédige avec le skill `brief-editeur`, en brouillon qu'Hervé envoie lui-même. **La signature d'Hervé et le registre (tutoiement ou vouvoiement) se lisent dans la fiche de l'éditeur, `Core/Editeurs/<Éditeur>.md`** ; ils ne sont jamais écrits dans un modèle. Si la fiche ne les donne pas, AURA demande à Hervé et note sa réponse dans la fiche.

**Ce qu'Hervé fait lui-même, ce qu'il confie à un relecteur.** Hervé garde la vérification des renvois et des termes : il connaît le jeu, la VO et ses choix. Un relecteur apporte un œil neuf sur la fluidité, la lisibilité des règles pour un joueur qui découvre, les coquilles restantes. Consigne au relecteur : ne pas modifier un terme de jeu sans en parler ; noter en commentaire ce qui lui semble bizarre ; le glossaire de référence est joint. Le paquet complet du relecteur : skill `gestion-gamme`.

---

## Ce que livre une vérification `qa-coherence`

- Le bilan chiffré du point demandé, avec chaque endroit (repère) et la commande lancée.
- Les anomalies classées : **bloquant** (rend une règle injouable : renvoi vers une règle absente, symbole au sens inversé), **important** (numérotation glissée, variante qui traîne), **mineur**.
- Les questions pour l'éditeur, au registre.
- Ce qui n'a pas été vérifié, et pourquoi.

## Ce que ce skill ne fait pas

- Relire tout un texte et décider s'il peut partir : `relecture-multi-agents`.
- La typographie : `typographie-fr`. La longueur, le débord, les balises : `controle-longueur`.
- Choisir ou valider un terme : `glossaire`. Traduire une phrase : `traduction-jeux`.
- Contrôler les épreuves mises en page (le bon à tirer) et remplir les renvois de page : `gestion-gamme`.
- Écrire à l'éditeur : `brief-editeur`.
