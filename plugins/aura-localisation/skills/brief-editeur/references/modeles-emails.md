# Modèles d'e-mails aux éditeurs

Tous ces modèles produisent un **brouillon** : Hervé le relit et l'envoie lui-même.

## Ce qui se règle avant d'écrire, pour chaque modèle

<!-- [D-31] -->
- **Formule d'appel, registre (tu ou vous) et civilité** : lus dans la fiche
  `Core/Editeurs/<Éditeur>.md`, pour le contact visé. Les modèles ci-dessous sont écrits au
  vouvoiement ; si la fiche indique « tu » pour ce contact, AURA tutoie dans tout le message (pronoms,
  possessifs, impératifs) et relit les accords. Si la fiche ne dit rien, AURA demande à Hervé, puis
  note la réponse dans la fiche.
- **Signature** : `{Signature}` est remplacée par le bloc de la fiche, à l'identique. Jamais une
  signature écrite de mémoire ou reprise d'un autre éditeur.
<!-- [I-15] -->
- **Forme classique** : remercier, dire l'objet en une phrase, lister les pièces jointes par leur nom
  de fichier exact, proposer la suite. Pas d'émotion appuyée, pas de formule creuse.
- **Mention d'AURA et de l'IA** : elle suit la règle 3 du SKILL.md, seule à la fixer (la fiche de
  l'éditeur peut noter une obligation contractuelle de déclaration). <!-- [R-33] -->
<!-- [I-12] -->
- **Langage clair et chiffré** : numéros de question, références de cartes et de pages, nombres exacts
  (« 7 questions », « 340 cartes »). Aucun code interne (identifiant de glossaire, statut
  « Brouillon », étiquette de contrôle), aucune abréviation non traduite.
- **Typographie** : celle du skill `typographie-fr`, avec les écarts notés dans la fiche de l'éditeur.

Les éléments entre accolades `{…}` sont à remplir ; s'il manque une information, AURA la demande au
lieu de l'inventer.

---

## A. Questions groupées (un lot)

Quand : à un jalon convenu avec l'éditeur (noté dans sa fiche), avec les lignes « À envoyer » du
registre des questions.

```
Objet : {Jeu} — questions de traduction, lot {n}

{Formule d'appel}

Merci pour {les fichiers / votre dernier retour}. La traduction de {Jeu} avance ({où j'en suis, en
une phrase factuelle}) ; voici {nombre} points sur lesquels j'ai besoin de votre validation avant de
finaliser ces sections. Une réponse avant le {date} me permettrait de tenir le calendrier.

Question {N°} — {référence : carte, page ou règle}
Texte anglais : « {extrait} »
Contexte : {une ou deux phrases sur l'usage dans le jeu}
Question : {formulation précise}
Ma proposition : {traduction provisoire ou options}

Question {N°} — …

{Si certaines questions ne bloquent rien :} Les questions {N°} et {N°} ne bloquent pas mon avancée ;
votre réponse servira à fixer le glossaire de la gamme.

{Pièce jointe éventuelle : « Ci-joint : {nom exact du fichier}, le tableau des questions. »}

Merci d'avance,

{Signature}
```

Les numéros sont ceux du registre : l'éditeur peut répondre « question 12 : oui » sans ambiguïté.

## B. Réponse à une liste de remarques de l'éditeur

<!-- [I-11] -->
Quand : l'éditeur (ou son relecteur, ou le maquettiste via l'éditeur) renvoie une liste de remarques.
**Chaque remarque reçoit sa ligne**, aucune ne se perd dans un paragraphe. Le tableau est d'abord
rempli avec Hervé, puis sert de corps à l'e-mail.

| N° | Remarque de l'éditeur (référence) | Réponse ou correction | Statut |
|---|---|---|---|

Statuts : **Corrigé** (la correction faite), **Maintenu** (avec la raison, courte et factuelle),
**Question en retour** (ce qu'il faut à Hervé pour trancher), **Hors périmètre** (voir le modèle E).
Avant d'envoyer, AURA vérifie le compte : autant de lignes que de remarques reçues (« 12 remarques,
12 lignes »).

```
Objet : Re : {objet de l'éditeur}

{Formule d'appel}

Merci pour votre relecture. Vous trouverez ci-dessous ma réponse à chacune des {nombre} remarques :
{nombre} corrigées, {nombre} maintenues (avec la raison), {nombre} sur lesquelles j'ai besoin d'une
précision.

{tableau}

{Pièce jointe : « Ci-joint : {nom exact du fichier corrigé}. »}

{Suite proposée, en une phrase.}

{Signature}
```

## C. Livraison

Quand : à la remise d'une traduction, d'une révision, ou de corrections.

```
Objet : {Jeu} — livraison de la traduction française, {version}

{Formule d'appel}

Merci de votre confiance sur ce projet. Voici la traduction française de {Jeu}, {version}, datée du {date}.

Fichiers joints :
- {nom exact du fichier} — {contenu, en quelques mots}
- {nom exact du fichier} — {…}

Points d'attention :
- {nombre} questions attendent encore votre réponse (n° {…}) ; je reporterai vos réponses dans une
  version {suivante}.
- {Renvois de page à compléter sur l'épreuve mise en page, s'il y en a : leur nombre.}

{Rappel du délai de corrections inclus, s'il a été convenu au cadrage.}

{Signature}
```

## D. Cadrage d'un nouveau projet

Quand : avant de commencer, pour écrire noir sur blanc ce qui a été convenu à l'oral ou par bribes.

```
Objet : {Jeu} — récapitulatif de la mission de traduction

{Formule d'appel}

Merci pour votre proposition. Voici la mission telle que je la comprends ; pouvez-vous me confirmer
ou corriger ces points avant que je commence ?

- Projet : {Jeu}, {produit}
- Contenu à traduire : {livret de règles, cartes, boîte…}
- Volume : {nombre exact} caractères {ou mots}, compté sur les fichiers reçus
- Livraison : {date}, au format {format}
- Rémunération : {montant et mode, tels que convenus}
- Échéancier de paiement : {tel que convenu}
- Droits cédés et territoires : {tels que convenus}
- Mention du traducteur dans les crédits : {oui / à confirmer}
- Corrections incluses après livraison : {périmètre et délai}
- Fichiers reçus : {liste}
- Glossaire existant : {oui / non}
- Votre interlocuteur pour les questions : {prénom}

{Signature}
```

Les montants, délais et droits viennent d'Hervé ou du contrat ; AURA n'en propose aucun. Les repères
utiles pour en discuter sont dans `references/cadre-legal.md`.

## E. Demande de modification après livraison

Trois variantes, selon le cas tranché avec Hervé (voir le SKILL.md, partie 4).

```
Objet : Re : {Jeu} — demande de modification

{Formule d'appel}

Merci pour votre retour.

[Correction incluse]
La correction que vous signalez relève bien de ma traduction : je la prends en charge et vous renvoie
le fichier corrigé d'ici le {date}.

[Hors périmètre]
Cette demande porte sur {description courte : ton, coupe, terme décidé à nouveau}, ce qui dépasse la
traduction livrée. Je peux bien sûr l'intégrer :
- volume concerné : {nombre exact} caractères {ou heures}
- tarif : {montant convenu ou proposé par Hervé}
- délai : {date}
Pouvez-vous me confirmer que nous procédons ainsi ?

[Demande venue du maquettiste sans validation de l'éditeur]
J'ai bien reçu la demande de {prénom}. Pour l'intégrer, j'ai besoin de votre validation : c'est avec
vous que la traduction a été convenue.

{Signature}
```

## F. Relance

Quand : le délai demandé est passé sans réponse, et Hervé est d'accord pour relancer. Avant de
l'écrire, AURA vérifie qu'aucune réponse n'est arrivée entre-temps.

```
Objet : Re : {objet du message initial}

{Formule d'appel}

Je me permets de revenir vers vous au sujet de {mon message du {date} : questions n° {…}}.
{Pourquoi la réponse compte maintenant, en une phrase : « la mise en page commence le {date}. »}

Merci d'avance,

{Signature}
```

## G. Retours sur épreuve (BAT)

Quand : la liste de corrections de l'épreuve est prête (préparée avec le skill `gestion-gamme`).

```
Objet : {Jeu} — retours sur l'épreuve {BAT1 / BAT2}

{Formule d'appel}

Merci pour l'épreuve reçue le {date}. Vous trouverez ci-joint {nom exact du fichier} : {nombre}
corrections, numérotées et classées par page.

{BAT2 : « Sur les {nombre} corrections demandées au premier tour, {nombre} sont faites ; les n° {…}
restent à reprendre et figurent en tête de liste. »}

{Signature}
```

---

## Exemple rempli [EXEMPLE FICTIF]

<!-- [I-30] -->
Éditeur, contact, jeu et questions inventés. La fiche de l'éditeur indique : contact Camille, registre
« tu », formule « Bonjour Camille, », signature « Hervé / Traduction et relecture — gamme Brumeval ».

```
Objet : Brumeval, Le Guet — questions de traduction, lot 2

Bonjour Camille,

Merci pour les fichiers de la semaine dernière. J'ai traduit le livret de règles et 120 des 340 cartes ;
voici 2 points sur lesquels j'ai besoin de ta validation avant de finaliser ces sections. Une réponse
avant le 12 octobre me permettrait de tenir le calendrier.

Question 12 — règle 3.4
Texte anglais : « Flummox the wizard »
Contexte : le nom apparaît sur 3 cartes et dans un texte d'ambiance.
Question : est-ce le nom propre d'un personnage, ou un sorcier générique ?
Ma proposition : nom propre, gardé tel quel : « Flummox le sorcier ».

Question 13 — carte C044
Texte anglais : « attack track »
Question : existe-t-il un terme déjà employé sur vos autres titres ?
Ma proposition : « piste d'attaque ».

La question 13 ne bloque pas mon avancée ; ta réponse servira à fixer le glossaire de la gamme.

Merci d'avance,

Hervé
Traduction et relecture — gamme Brumeval
```
