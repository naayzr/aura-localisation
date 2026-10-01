# BAT : contrôler l'épreuve mise en page

Le **BAT** (bon à tirer) est l'épreuve PDF mise en page que l'éditeur ou le maquettiste envoie pour
validation avant l'impression. En jeu de société, c'est là qu'apparaissent les erreurs que le texte
Word ne montrait pas : texte coupé par le cadre d'une carte, balise affichée telle quelle, icône
fausse, renvoi de page faux. Il y a souvent deux cycles : **BAT1** (première épreuve, liste complète
de corrections) et **BAT2** (vérification que tout a été corrigé, et que rien de nouveau n'est cassé).

La validation (« bon à tirer ») est une décision d'Hervé et de l'éditeur. AURA ne la déclare jamais.

## Ce qu'AURA peut faire, et ce qu'elle ne peut pas

- Elle lit le PDF de l'épreuve page par page et le compare au texte français validé.
- Pour un repérage systématique, elle peut écrire le texte d'une partie de l'épreuve dans un fichier
  `.txt` et le comparer au texte validé avec `scripts/comparer_versions.py` (texte validé = ancien,
  texte de l'épreuve = nouveau). **Limite** : l'ordre du texte extrait d'un PDF suit la mise en page
  (colonnes, encadrés, cartes en planche) ; les écarts trouvés sont des pistes, pas une preuve.
  Le contrôle visuel page par page reste obligatoire.
- Elle n'annote pas le PDF : elle produit une liste de corrections par page, au format que l'éditeur
  préfère (noté dans sa fiche : tableau, liste numérotée, annotations faites par Hervé).

## Check-list d'une épreuve

Pour chaque page ou planche de cartes :

1. **Texte tronqué** : fin de phrase coupée par le cadre, dernière ligne masquée, texte qui déborde
   d'un encadré. La liste des champs déjà signalés trop longs (skill `controle-longueur`) se vérifie en
   premier.
2. **Texte manquant** : paragraphe, carte ou ligne de tableau absent par rapport au texte validé ;
   carte en double. Le compte se fait : « 120 cartes attendues, 119 sur l'épreuve : manque C087 ».
3. **Texte non à jour** : passage de l'épreuve qui correspond à une ancienne version de la traduction
   (correction de relecture ou réponse de l'éditeur non reportée).
4. **Balise affichée en brut** : `{icon_sword}`, `<b>`, `[damage]` visibles à l'impression au lieu de
   l'icône ou du gras.
5. **Icône** : manquante, fausse (épée à la place du bouclier), décalée, en nombre différent de
   l'anglais.
6. **Valeurs** : coûts, dégâts, numéros de carte, numéros de règle identiques à la version anglaise.
7. **Césure** : coupure de mot fautive, nom propre ou mot-clé coupé ; les règles de coupure sont
   celles du skill `typographie-fr`.
8. **Typographie visible à l'épreuve** : espaces avant la ponctuation haute, guillemets, apostrophes,
   capitales accentuées — contrôle selon le skill `typographie-fr`, pas de règle recopiée ici.
9. **Renvois de page** : chaque « voir p. X » renvoie à la bonne page **de l'épreuve française**
   (la pagination diffère souvent de l'anglais). Les renvois laissés en attente pendant la traduction
   (`[PAGE À CONFIRMER]` ou équivalent) sont remplis ici.
10. **Index et glossaire du livret** : après traduction, l'ordre alphabétique change. L'index se retrie
    sur les termes français, accents ignorés pour le classement, et chaque numéro de page se vérifie.
11. **Sommaire** : titres identiques aux titres des chapitres, pages justes.
12. **Mots-clés et termes** : forme du glossaire, mise en forme constante (gras, capitale initiale selon
    la charte de l'éditeur).
13. **Crédits et mentions légales** : présents, à jour, mention du traducteur conforme à ce qui a été
    convenu (skill `brief-editeur`).
14. **Dos de cartes, boîte, encarts, aides de jeu** : souvent oubliés, à vérifier comme le reste.

## La liste de corrections

| N° | Page / carte | Emplacement | Constat | Correction demandée | Type |
|---|---|---|---|---|---|

Type : tronqué, manquant, non à jour, balise, icône, valeur, césure, typographie, renvoi, index,
autre. La liste est numérotée pour que le maquettiste réponde point par point. Elle est rédigée en
phrases claires, sans code interne, sans mention d'AURA ; l'e-mail qui l'accompagne passe par le skill
`brief-editeur`.

## Le suivi BAT1 → BAT2

- À l'envoi des retours BAT1 : une ligne dans le tableau « BAT » du registre de gamme (date de
  réception, date d'envoi des retours, nombre de corrections demandées).
<!-- [I-40] -->
- À réception du BAT2 : chaque correction du BAT1 est vérifiée une par une (Fait / Non fait / Fait
  autrement), et le résultat se dit avec son compte : « 37 corrections demandées, 35 faites, 2 non
  faites (n° 12 et 30) ». Puis la check-list complète repasse sur les pages modifiées, car une
  correction peut en casser une autre (texte qui reflue sur la carte suivante).
- Une correction non faite repart dans la liste suivante avec son numéro d'origine.
- Quand Hervé et l'éditeur valident, la date et le nom de qui a validé vont dans le registre.
