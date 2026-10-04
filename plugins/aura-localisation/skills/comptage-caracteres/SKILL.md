---
name: comptage-caracteres
description: "Compte exact des caractères (espaces comprises et non comprises), des mots, des segments, des balises et des répétitions d'un ou plusieurs fichiers Word, Excel, CSV ou texte, source ou traduction, pour un devis, une facture, un planning ou un délai : montant au tarif aux 1 000 caractères ou au mot, nombre de jours de travail à sa cadence. À utiliser pour « combien de caractères », « compte ce fichier », « fais-moi un devis », « prépare la facture », « combien de temps pour traduire ça », « quel volume »."
---

# Comptage de caractères — pour le devis, la facture et le planning

Un chiffre qui part sur un devis ou une facture vient d'un **comptage complet**, jamais d'une estimation ni de la lecture d'un extrait. C'est le programme qui compte ; toi, tu présentes et tu expliques.

## Compter
1. Applique d'abord la règle « Les programmes et le dossier d'Hervé » du skill `noyau` : selon la tâche, le programme voit le dossier, ou il faut que Hervé glisse le fichier dans la conversation — et si le programme ne lit pas le fichier, **aucun chiffre** ne part sur un devis.
2. Le programme et les fichiers en chemins complets (règle « Écrire une commande » du skill `noyau`) : <!-- [R-29] -->
   - un ou plusieurs fichiers : `python3 "${CLAUDE_SKILL_DIR}/scripts/compter.py" "<fichier1>" "<fichier2>"` (un total est donné)
   - un tableur de cartes, une seule colonne : `--colonne EN` (la source) ou `--colonne FR` (la cible) — le nom exact de l'en-tête
   - un montant : `--tarif-1000 <prix>` (pour 1 000 caractères espaces comprises) ou `--tarif-mot <prix>`
   - un délai : `--cadence <caractères par jour>` — la capacité de traduction d'Hervé vit dans `Core/Profile.md`, et seulement là (datée, par type de texte s'il en a donné plusieurs) ; si elle n'y est pas, tu la lui demandes et tu l'y écris, tu ne la supposes jamais <!-- [R-41] -->
3. En cas de doute sur le programme, `python3 "${CLAUDE_SKILL_DIR}/scripts/compter.py" --auto-test` doit répondre OK.

## Présenter
Verdict d'abord : « 48 312 caractères espaces comprises dans la source, soit 32,2 feuillets. » Puis, en dessous :
- ce qui a été compté : quels fichiers, quelle colonne, source ou cible ;
- les **balises** comptées à part (`{icone}`, `<b>`, `[degats]`) : avec ou sans, selon l'accord avec l'éditeur — tu demandes si ce n'est pas écrit dans sa fiche. Une balise est un identifiant **sans espace** : une parenthèse entre crochets (« [la règle optionnelle] ») ou une comparaison (« score < 3 et B > 5 ») est comptée comme du texte. Si les balises de l'éditeur contiennent des espaces (`{icon gold}`), dis-le à Hervé : elles sont alors comptées dans le texte ; <!-- [R-59] -->
- les **répétitions exactes** (segments identiques) : certains éditeurs les paient moins ; tu le signales, tu ne décides pas ;
- source ou cible : le français est souvent plus long que l'anglais ; on facture sur ce que dit le contrat (fiche éditeur), sinon tu demandes.
« Environ » n'existe pas dans un chiffre qui part chez l'éditeur.

## Devis et facture
- Le **tarif** et la **base** (caractères source ou cible, avec ou sans espaces, au mot) viennent de la fiche éditeur ou d'Hervé ; jamais d'un tarif « du marché » que tu inventerais.
- Les **mentions obligatoires** dépendent de son statut (indépendant, salarié, auteur), noté dans `Core/Profile.md`. Tu ne les inventes pas : s'il n'a pas de modèle, tu proposes une structure (coordonnées, client, objet, base de calcul, quantité, prix unitaire, total, échéance) et tu marques « mentions légales à vérifier selon ton statut ». Une mention légale non sourcée ne part jamais.
- Le document est un **brouillon** dans `Livrables/<Projet>/` (`Devis_<Projet>_v1`) ; c'est Hervé qui l'envoie.

## Planning
Le nombre de jours sert au rétroplanning d'une gamme (skill `gestion-gamme`) : jours de traduction à sa cadence, plus relecture, questions et marge. Tu écris l'échéance dans `Core/Tasks.md` et le fil dans `Core/Suivi.md` si elle dépend de quelqu'un d'autre.
