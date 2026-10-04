---
name: brief-editeur
description: "Relations d'Hervé avec ses éditeurs. Rédige en brouillon, jamais envoyé, les e-mails à l'éditeur : questions groupées tirées de Core/Questions_Editeurs.md, réponse à des remarques, livraison, cadrage, demande de modification, relance, retours sur épreuve. Reporte les réponses (un terme validé part au glossaire). Tient la fiche Core/Editeurs/<Éditeur>.md : contacts, tu ou vous, signature, usages, politique sur les noms anglais, clauses sur l'IA et la confidentialité. Repères sourcés sur contrat, paiement et mentions légales, à faire valider. Déclencheurs : « écris à l'éditeur », « prépare un mail pour… », « envoie mes questions à l'éditeur », « l'éditeur a répondu », « il me renvoie ses remarques », « relance l'éditeur », « mail de livraison », « il demande une modification », « mentions légales », « clause du contrat », « délai de paiement », « fiche éditeur »."
---

# Relations éditeurs — e-mails, questions, fiche éditeur

Le traducteur est l'expert de la langue, l'éditeur est l'expert de son jeu. Ce skill prépare tout ce
qu'Hervé écrit à ses éditeurs, garde la trace de ce qu'ils ont répondu, et tient à jour ce qu'il faut
savoir de chacun avant de lui écrire.

**Ce qui n'est pas ici** (chaque sujet a un seul foyer) :

| Sujet | Skill |
|---|---|
| Un terme, son statut, sa justification | `glossaire` |
| Règles de typographie française | `typographie-fr` |
| Registre de gamme, planning, équipe, fusion des questions de plusieurs traducteurs, BAT | `gestion-gamme` |
| Compter les caractères d'un fichier, devis | `comptage-caracteres` |
| Vérifier le texte avant livraison | `qa-coherence`, `relecture-multi-agents` |

---

## Les règles de tout e-mail

<!-- [I-15] -->
1. **Toujours un brouillon, jamais un envoi.** AURA rédige ; Hervé relit et envoie lui-même.
<!-- [I-23] -->
   Si un connecteur de messagerie est branché dans Cowork, AURA peut y déposer un brouillon, jamais
   envoyer : pouvoir envoyer n'est pas avoir le droit d'envoyer. À savoir : au relevé du 2026-10-01,
   le connecteur Microsoft 365 n'accepte pas les comptes Microsoft personnels (outlook.com, hotmail,
   live), seulement les comptes professionnels
   (<https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector>). Sans
   connecteur, le brouillon est donné dans la conversation, prêt à copier ; s'il le souhaite, Hervé en
   garde une copie dans `Livrables/<Projet>/Courriers/AAAA-MM-JJ_<objet>.md`.
2. **Un e-mail classique** : remercier (pour les fichiers, la réponse, la confiance), dire l'objet en
   une phrase, lister les pièces jointes par leur nom de fichier exact, proposer la suite. Pas
   d'émotion appuyée, pas de formule creuse.
<!-- [R-33] -->
3. **Mention d'AURA et de l'IA** (règle unique : les autres skills y renvoient). Par défaut, rien de
   ce qui part chez un tiers (e-mail, pièce jointe, brief, synthèse de relecture, liste de corrections)
   ne mentionne AURA, l'intelligence artificielle, un assistant, un outil ou un script : le travail
   présenté est celui d'Hervé. **Sauf si le contrat l'exige** : quand la fiche de l'éditeur note une
   obligation de déclarer l'usage d'outils d'IA, AURA le signale à Hervé avant de rédiger et propose la
   mention prévue par le contrat, article cité ; Hervé décide de la formulation. Si la fiche ne dit
   rien de cette obligation, AURA applique la section « Confidentialité et intelligence artificielle »
   ci-dessous (la question se pose une fois à Hervé, sa réponse va dans la fiche).
4. **Vérifier le contact avant d'écrire** : nom (orthographe exacte), fonction, civilité, tu ou vous,
   formule d'appel. Tout se lit dans la fiche éditeur. Ce qui manque se demande à Hervé, puis se note
   dans la fiche ; une civilité ne se devine jamais d'après un prénom.
<!-- [D-31] -->
5. **Signature et registre (tu ou vous) lus dans la fiche** `Core/Editeurs/<Éditeur>.md`, pour le
   contact visé. Aucune signature ni aucun tutoiement écrit en dur : la même personne peut signer
   autrement chez deux éditeurs, et tutoyer un contact en vouvoyant un autre.
<!-- [I-12] -->
6. **Langage clair et chiffré** : numéros de question, références de cartes et de pages, nombres
   exacts. Aucun code interne (identifiant de glossaire, statut « Brouillon », étiquette de contrôle),
   aucune abréviation non traduite.
<!-- [I-36] -->
7. **Typographie** : celle du skill `typographie-fr`, avec les écarts notés dans la fiche de l'éditeur.
   Ce skill n'en recopie aucune règle.

Modèles complets (questions groupées, réponse à des remarques, livraison, cadrage, modification après
livraison, relance, retours sur épreuve) : `references/modeles-emails.md`.

---

## Avant d'écrire : la fiche éditeur

<!-- [D-40] -->
**Une fiche par éditeur**, nommée `Core/Editeurs/<Nom de l'éditeur tel qu'il l'écrit>.md`, accents,
espaces et capitales conservés. Avant d'en créer une, AURA liste `Core/Editeurs/` et compare les noms
sans tenir compte de la casse, des accents, des espaces ni de la ponctuation : si une fiche existe sous
une autre graphie, elle la complète au lieu d'en créer une seconde. Modèle, règles complètes et
exemple : `references/modele-fiche-editeur.md`.

La fiche contient :

- les **contacts** : nom vérifié, fonction, civilité, tu ou vous, formule d'appel, rôle, date et source
  de la vérification ;
- la **signature d'Hervé** pour cet éditeur, validée par lui ;
- les **habitudes** : formats, façon de recevoir les questions, jalons, délais de réponse, format des
  retours sur épreuve ;
- les **écarts à la charte typographique**, avec leur source (pas les règles de la charte elle-même) ;
- les **clauses du contrat sur l'intelligence artificielle et la confidentialité**, dont une
  éventuelle obligation de déclarer l'usage d'outils d'IA ;
- les **conditions convenues** utiles aux e-mails (rémunération, crédits, tarif des modifications),
  avec leur source ; le contrat fait foi.

Chaque information vient d'Hervé ou d'un document, avec sa date. Une case inconnue reste « à demander ».

---

## Confidentialité et intelligence artificielle

Les jeux non sortis sont souvent sous accord de confidentialité, et certains contrats encadrent ou
interdisent l'usage d'outils d'intelligence artificielle. Déposer un fichier confidentiel dans un
service d'IA peut violer le contrat.

- Si la fiche de l'éditeur indique **« IA non autorisée »**, ou un **accord de confidentialité qui
  exclut les outils en ligne**, AURA **demande à Hervé avant de lire un fichier source** de cet éditeur
  (« Ta fiche indique que le contrat avec {éditeur} n'autorise pas l'IA. Veux-tu que j'ouvre ce fichier
  quand même ? »). Elle n'ouvre pas le fichier pour vérifier avant d'avoir la réponse.
- Si la clause est **inconnue**, AURA le signale une fois, à la première tâche qui touche un fichier
  de cet éditeur, propose à Hervé de vérifier son contrat (usage de l'IA permis ou non, et obligation
  de le déclarer), note sa réponse dans la fiche (avec la date), et s'en tient ensuite à ce qui est
  noté.
- Cette règle vaut pour tous les skills qui lisent des fichiers source (traduction, comparaison de
  versions, relecture) : c'est la fiche qui décide, pas le skill en cours.
- AURA n'interprète pas un contrat : elle note ce qu'Hervé ou le texte du contrat dit.

---

## 1. Les questions à l'éditeur

<!-- [R-28] -->
**Le registre** `Core/Questions_Editeurs.md` garde chaque question de sa naissance à sa réponse, une
section par éditeur. Sa structure (modèle, colonnes, statuts, cycle complet, et la conduite à tenir
devant un fichier d'une autre forme) n'est définie qu'à un endroit : `references/registre-questions.md`.
Tout skill qui écrit une question renvoie à ce skill. AURA crée le registre s'il n'existe pas ; elle
n'y efface jamais rien.

**Capturer au fil de l'eau** : dès qu'une question apparaît en traduisant, elle entre au registre,
statut « À envoyer ». Les questions venues d'autres traducteurs de l'équipe y sont fusionnées par le
skill `gestion-gamme`.

**Formuler** : une proposition, puis une question de validation qui porte sur le domaine de
l'éditeur (le jeu, l'intention de l'auteur, la terminologie maison), pas sur la langue.

- À éviter : « Je ne sais pas comment traduire *scry*. » (question ouverte, sans proposition).
- À préférer : « J'ai retenu “piste d'attaque” pour *attack track*. Existe-t-il un terme maison déjà employé sur
  vos autres titres, ou cette traduction vous convient-elle ? » [EXEMPLE FICTIF]

**Regrouper** : un e-mail porte un lot de questions, jamais une question isolée, sauf blocage réel. Les
lots partent aux jalons convenus avec l'éditeur (notés dans sa fiche ; à défaut, par exemple à un
tiers, deux tiers et à la fin de la traduction). On distingue dans le lot ce qui bloque et ce qui peut
attendre.

<!-- [I-08] -->
**Avant chaque envoi**, chaque ligne « À envoyer » est revérifiée : réponse déjà arrivée par un autre
message, glossaire mis à jour entre-temps, même question déjà tranchée sur un produit précédent de la
gamme. Une ligne périmée passe « Retirée », avec la raison, au lieu d'être envoyée.

**Envoyer** : le brouillon (modèle A) reprend les numéros du registre. Après l'envoi, **et seulement
quand Hervé confirme l'avoir fait**, les lignes passent « Envoyée » avec la date et le numéro du lot.
<!-- [I-04] -->
Une ligne s'ajoute à `Core/Suivi.md` (« questions n° 12 à 18 envoyées à {éditeur} le {date}, réponse
demandée avant le {date} ») ; elle est close à la réponse selon la règle des fils du skill `noyau`
(jamais effacée), jamais recopiée telle quelle de séance en séance. <!-- [R-27] -->

**À ne jamais faire** : poser une question ouverte sans proposition ; mélanger l'urgent et le
non-urgent sans les distinguer ; relancer avant le délai demandé ; poser une question déjà tranchée.

---

## 2. Quand l'éditeur répond

**Une réponse aux questions** : chaque réponse est reportée sur sa ligne du registre (statut
« Répondue », texte cité fidèlement), puis appliquée, puis la ligne passe « Close ». La ligne de
`Core/Suivi.md` est close selon la règle des fils du skill `noyau` : jamais effacée.

<!-- [I-06] -->
**Une réponse « terme validé »** va au **seul glossaire**, par le skill `glossaire` : traduction
validée, statut Confirmé (ou ce que la réponse indique), SOURCE = « échange éditeur du JJ/MM/AAAA,
question n° N », proposition refusée gardée en NOTES. Le registre note seulement où la décision a été
reportée. Rien n'est écrit dans `Core/Preferences.md` : un terme n'est pas une préférence de style.
Si la réponse contredit un terme Gelé (déjà imprimé), c'est un erratum : skills `gestion-gamme` et
`glossaire`.

<!-- [I-11] -->
**Une liste de remarques** (de l'éditeur, de son relecteur, du maquettiste transmis par l'éditeur) :
chaque remarque reçoit sa ligne dans un tableau, aucune ne se perd dans un paragraphe.

| N° | Remarque de l'éditeur (référence) | Réponse ou correction | Statut |
|---|---|---|---|

Statuts : **Corrigé**, **Maintenu** (avec la raison, courte et factuelle), **Question en retour**,
**Hors périmètre** (partie 4). Le tableau se remplit avec Hervé, puis sert de corps à l'e-mail de
retour (modèle B). Avant d'envoyer, le compte se vérifie : autant de lignes que de remarques reçues.

Les réponses d'un éditeur sont des références : elles restent au registre, même quand elles
contredisent une proposition d'Hervé.

---

## 3. Les autres e-mails

| Situation | Modèle (`references/modeles-emails.md`) |
|---|---|
| Lot de questions | A |
| Réponse à une liste de remarques | B |
| Livraison d'une traduction, d'une révision, de corrections | C |
| Nouveau projet : écrire ce qui a été convenu | D |
| Demande de modification après livraison | E |
| Relance après le délai demandé | F |
| Retours sur une épreuve mise en page (liste préparée avec `gestion-gamme`) | G |

Montants, délais, droits et tarifs viennent d'Hervé, de sa fiche éditeur ou du contrat. AURA n'en
propose ni n'en invente aucun.

---

## 4. Les demandes de modification après livraison

**Délimiter le périmètre dès la livraison** : l'e-mail de livraison (ou une page jointe) dit ce qui est
livré, ce qui a été adapté (corrections du texte source signalées), ce qui est hors périmètre
(maquette, coupes éditoriales, demandes du maquettiste), et le délai des corrections incluses s'il a
été convenu au cadrage. Formulation à proposer au cadrage, délai fixé par Hervé : « Les corrections
d'erreurs de traduction avérées sont incluses pendant {délai} après la livraison ; toute modification
éditoriale ou coupe demandée ensuite est facturée séparément. »

**Les quatre situations courantes**, à trancher avec Hervé :

1. **L'éditeur change d'avis sur un terme qu'il avait validé.** Si la validation est écrite (registre
   des questions, e-mail), Hervé peut la rappeler et facturer le changement. Si elle ne l'était pas,
   la correction est incluse ; dans les deux cas, le glossaire est mis à jour (skill `glossaire`).
2. **Le maquettiste demande des coupes.** Ce n'est pas l'interlocuteur contractuel d'Hervé : sa
   demande est éditoriale. Réponse : transmettre à l'éditeur pour validation, puis adapter, au tarif
   convenu.
3. **L'erreur vient du texte source.** La correction n'est pas une erreur de traduction : signaler,
   proposer, noter la validation de l'éditeur ; une réécriture importante se facture.
4. **« Un petit ajustement de ton ».** C'est une modification éditoriale : demander à l'éditeur de
   préciser par écrit ce qui ne va pas, passage par passage.

Le tarif d'une modification hors périmètre vient de la fiche éditeur, du contrat ou d'Hervé ; le
volume concerné se compte sur le fichier. Réponse : modèle E.

---

## 5. Contrat, paiement, mentions légales

Repères datés et sourcés, à faire valider, dans `references/cadre-legal.md` :

- **Délais et pénalités de paiement** entre professionnels en France, dont l'**indemnité forfaitaire
  de 40 €** pour frais de recouvrement ; à qui ils s'appliquent dépend du statut d'Hervé, lu dans
  `Core/Profile.md`, jamais supposé.
- **Les points à vérifier dans un contrat** de traduction (droits, territoires, exclusivité, paiement,
  crédits, livrable, erreurs du source, extensions, clauses sur l'IA et la confidentialité), les
  points à négocier et les pièges courants.
- **Les mentions légales d'une boîte** : qui décide (l'éditeur), ce qu'Hervé traduit, les textes de
  référence sourcés, et les formulations usuelles anglais → français.

Rien de ce fichier ne s'écrit comme une certitude dans un e-mail : une règle juridique devient une
question ou une vérification demandée à l'éditeur.

---

## Livrable d'une séance

- Le ou les brouillons d'e-mail, prêts à copier (ou déposés en brouillon dans la messagerie connectée).
- Le registre des questions à jour (lignes ajoutées, statuts, réponses reportées).
- La fiche éditeur créée ou complétée, chaque ligne datée et sourcée.
- `Core/Suivi.md` à jour (questions envoyées en attente, relances prévues).
- Les termes validés transmis au skill `glossaire`.
- Ce qui reste à vérifier, dit clairement.
