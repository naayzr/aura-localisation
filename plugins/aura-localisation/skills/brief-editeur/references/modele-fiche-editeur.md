# Modèle de fiche éditeur — `Core/Editeurs/<Éditeur>.md`

La fiche éditeur est la mémoire d'Hervé sur un donneur d'ordre : à qui il écrit, comment, avec quelle
signature, ce que le contrat permet. Elle appartient à la **couche mémoire** : AURA la crée à partir
de ce modèle quand elle n'existe pas, puis met à jour une ligne à la fois, avec la date et la source.
Rien n'est effacé : une information périmée est barrée ou passe en « ancien » avec sa date.

<!-- [D-40] -->
## Règle de nommage : une fiche par éditeur

- Chemin : `Core/Editeurs/<Nom de l'éditeur tel qu'il l'écrit>.md`. Le nom est celui que l'éditeur
  emploie lui-même (signature de ses e-mails, mentions légales, site), **accents, espaces et capitales
  conservés**. Pas de forme abrégée inventée, pas de suppression d'accent.
- Les caractères interdits dans un nom de fichier Windows (`\ / : * ? " < > |`) sont remplacés par un
  tiret.
- **Avant de créer une fiche**, AURA liste `Core/Editeurs/` et compare les noms sans tenir compte de la
  casse, des accents, des espaces, des tirets ni de la ponctuation. Si une fiche existe sous une autre
  graphie (une fiche sans accent face à une fiche accentuée, une forme collée face à une forme en
  deux mots), elle la complète au lieu d'en créer une deuxième, et note la graphie rencontrée dans
  « Autres graphies ». En cas de doute (deux sociétés distinctes au nom voisin), elle demande à Hervé.
- Le fichier `Core/Editeurs/README.md` éventuellement présent depuis la version précédente reste tel
  quel : c'est un ancien gabarit, ce modèle-ci le remplace sans le toucher.

## Ce que la fiche contient, et d'où vient chaque ligne

Chaque information vient d'Hervé ou d'un document (e-mail de l'éditeur, contrat, guide de style), et
la ligne dit d'où et quand. AURA ne remplit jamais une case par déduction : une case inconnue reste
« à demander ».

---

## Le modèle (à copier tel quel à la création)

```markdown
# <Nom de l'éditeur tel qu'il l'écrit>

> Fiche éditeur — mémoire d'Hervé. Mise à jour une ligne à la fois, avec la date et la source ;
> rien n'est effacé. Créée le AAAA-MM-JJ. Dernière mise à jour : AAAA-MM-JJ.

## Identité

- Nom tel que l'éditeur l'écrit : <…>
- Autres graphies rencontrées : <…>
- Gammes suivies pour cet éditeur : <Gamme> (registre : Core/Gammes/<Gamme>.md)
- Rôle d'Hervé chez cet éditeur : <traducteur / relecteur / responsable de gamme>

## Contacts

| Prénom et nom (orthographe vérifiée) | Fonction | Civilité | Registre | Formule d'appel | Rôle dans les projets | Vérifié le (source) |
|---|---|---|---|---|---|---|

- Civilité : « Madame », « Monsieur », ou « aucune » (on écrit au prénom). Jamais devinée d'après le
  prénom : elle vient de la signature du contact ou d'Hervé.
- Registre : « tu » ou « vous », pour CE contact (un même éditeur peut avoir des contacts tutoyés et
  d'autres vouvoyés).
- Formule d'appel : exactement celle qu'Hervé emploie (« Bonjour Camille, », « Bonjour Madame, »…).
- Les adresses e-mail et téléphones, si Hervé veut les garder ici, vont dans une colonne Notes ;
  AURA ne les recopie dans aucun autre fichier.

## Signature d'Hervé pour cet éditeur

    <bloc exact de la signature qu'Hervé utilise avec cet éditeur, ligne par ligne>

Validée par Hervé le AAAA-MM-JJ.

## Habitudes de travail

- Format des fichiers reçus et livrés : <…>
- Format des questions : <tableau joint / liste dans le mail / plateforme de l'éditeur>
- Jalons d'envoi des questions convenus : <…>
- Délai de réponse habituel de l'éditeur : <…>
- Format des retours sur épreuve (BAT) : <tableau / annotations PDF / liste numérotée>
- Interlocuteur pour les mentions légales et les crédits : <…>

## Noms propres et noms anglais

<!-- [R-41] -->
La politique de l'éditeur, écrite ici seulement (la fiche de style d'une gamme y renvoie) : garder
l'anglais, adapter ou traduire, et pour quelles catégories (personnages, lieux, mécaniques, noms de
genres de jeu), avec sa source. Une exception propre à une gamme (licence dont l'ayant droit impose ses
noms) s'écrit ici, avec le nom de la gamme. Les cas tranchés, nom par nom, vont au glossaire.

| Catégorie | Politique | Gamme concernée (ou « toutes ») | Source |
|---|---|---|---|

## Écarts à la charte typographique

Seulement ce qui diffère de la charte du skill `typographie-fr`, avec la source de chaque écart
(guide de style de l'éditeur, e-mail du AAAA-MM-JJ). Aucune règle de la charte n'est recopiée ici.

| Écart | Source | Depuis le |
|---|---|---|

## Contrat : intelligence artificielle et confidentialité

- Usage de l'IA selon le contrat : <Autorisé / Autorisé sous conditions : lesquelles / Non autorisé /
  Inconnu>
- Source : <contrat du AAAA-MM-JJ, article … / e-mail du … / « dit par Hervé le … »>
- Accord de confidentialité : <Oui / Non / Inconnu> ; portée : <produits, durée> ; exclut-il les
  outils en ligne : <Oui / Non / Inconnu>
- Obligation de déclarer l'usage d'outils d'IA : <Oui : mention prévue « … » (article …) / Non / Inconnu>
- Ce qu'AURA fait en conséquence : <ex. « demander avant d'ouvrir un fichier source de cet éditeur »>

## Conditions convenues (repères, le contrat fait foi)

- Mode de rémunération et délai de paiement convenus : <… (source)>
- Mention du traducteur dans les crédits : <… (source)>
- Tarif des modifications hors périmètre : <… (source)>

## Historique de la fiche

- AAAA-MM-JJ : création (source : …).
```

---

## Exemple de fiche remplie [EXEMPLE FICTIF]

<!-- [I-30] -->
Éditeur, personnes et clauses inventés pour montrer la forme. Aucun nom ne désigne une société ou une
personne réelle.

```markdown
# Ludo Fictif

## Contacts

| Prénom et nom (orthographe vérifiée) | Fonction | Civilité | Registre | Formule d'appel | Rôle dans les projets | Vérifié le (source) |
|---|---|---|---|---|---|---|
| Camille Exemple | cheffe de projet localisation | aucune | tu | Bonjour Camille, | interlocutrice projet, valide les termes | 2026-10-02 (signature de son e-mail du 30/09) |
| Dominique Fictif | directeur éditorial | Monsieur | vous | Bonjour Monsieur, | contrats, mentions légales | 2026-10-02 (dit par Hervé) |

## Signature d'Hervé pour cet éditeur

    Hervé
    Traduction et relecture — gamme Brumeval

Validée par Hervé le 2026-10-02.

## Contrat : intelligence artificielle et confidentialité

- Usage de l'IA selon le contrat : Non autorisé
- Source : contrat du 2026-09-15, article 7 (lu par Hervé)
- Accord de confidentialité : Oui ; portée : extension « Le Guet » jusqu'à sa sortie ; exclut les outils
  en ligne : Oui
- Obligation de déclarer l'usage d'outils d'IA : Sans objet (IA non autorisée)
- Ce qu'AURA fait en conséquence : demander avant d'ouvrir tout fichier source de cet éditeur.
```
