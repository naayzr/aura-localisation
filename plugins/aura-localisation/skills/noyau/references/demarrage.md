# AURA START — le démarrage en détail

## 0. Le dossier et la version
- Le dossier connecté doit contenir `CLAUDE.md` et `Core/CONTEXT.md`. Sinon : « Je ne vois pas ton dossier HERVÉ WORLD. Connecte-le à cette conversation (bouton dossier, puis choisis le dossier qui contient directement CLAUDE.md, Core et Glossaires). » Et tu t'arrêtes là.
- La version, ensuite : la règle est au point 1 de la section 2 du SKILL.md de ce skill, et seulement là. <!-- [R-11] --> <!-- [R-24] --> Si `Core/VERSION.md` manque, le démarrage s'arrête à la phrase qu'elle donne : rien de ce qui suit ne s'applique, et rien ne s'écrit dans le dossier. La version du plugin se lit dans son fichier `plugin.json`, jamais en chargeant le skill `mise-a-jour`. <!-- [R-13] -->

## 1. La date et l'heure
Tu ne supposes ni la date ni l'heure : tu les lis dans ton environnement (date du système) et, si tu as un doute sur le fuseau, tu demandes. Le matin (avant midi, heure d'Hervé) : briefing complet ; l'après-midi et le soir : briefing court. <!-- [D-36] -->

## 2. Ce que tu lis, dans cet ordre
1. `Core/CONTEXT.md` — l'état présent.
2. `Core/Profile.md` — qui est Hervé, ses éditeurs, ses gammes, son statut.
3. `Core/Preferences.md` — ses règles de style et de travail.
4. `Core/Tasks.md` — missions, actions, échéances.
5. `Core/Suivi.md` — les fils en attente.
6. `Core/_EN_COURS.md` — le travail en cours et ses portes, une section par projet.
7. `Core/ONBOARDING.md` — la mise en place.
8. La dernière entrée de `Core/Journal.md`, la section Patterns de `Core/evas.md`, la note la plus récente de `Core/Sessions/`.
Puis, selon le sujet : la fiche `Core/Editeurs/<Éditeur>.md`, le registre `Core/Gammes/<Gamme>.md`, le glossaire `Glossaires/Glossaire_<Gamme>.xlsx`.

Un fichier mémoire absent n'est pas une erreur : tu le crées à la première écriture qui le concerne, avec la structure donnée par le skill `mise-a-jour` (`references/graines/`). Cela vaut seulement quand `Core/VERSION.md` existe (section 0).

## 3. Les fils en attente — vérifiés, jamais recopiés <!-- [I-08] -->
Avant de citer une ligne de `Core/Suivi.md`, du tableau des questions éditeurs ou des termes « À confirmer », tu la vérifies contre sa source : la question a-t-elle reçu sa réponse (registre `Core/Questions_Editeurs.md`, glossaire mis à jour, Journal) ? Le terme a-t-il changé de statut ? C'est **la règle des fils**, écrite ici seulement : une ligne de `Core/Suivi.md` réglée ou périmée est **close**, c'est-à-dire déplacée dans le tableau « Fils clos » du même fichier, avec la date et la raison ; elle n'est jamais effacée, et jamais recopiée au briefing. Une question à un éditeur ou un terme change de statut dans son propre registre (`Core/Questions_Editeurs.md`, le glossaire). <!-- [R-27] --> Quand deux fichiers se contredisent, le plus récent gagne, et tu le dis. Un relevé daté reste tel quel ; une affirmation au présent se corrige.

## 4. Le fil oublié <!-- [I-04] -->
`Core/Suivi.md` liste chaque fil ouvert avec sa date de dernière activité : question envoyée à un éditeur sans réponse, terme « À confirmer », relecteur à relancer, facture non réglée, produit annoncé. Au briefing, en plus de l'urgent, tu fais remonter **une seule** ligne qui ne vient pas de la dernière session, la plus ancienne qui compte : « La question sur [terme] attend la réponse de [éditeur] depuis 12 jours. »

## 5. Le point du lundi <!-- [I-19] -->
Le premier AURA START de la semaine (lundi, ou le premier jour travaillé), tu ajoutes au briefing un point de moins de 20 lignes : livraisons des 7 prochains jours, jalons de rétroplanning menacés (skill `gestion-gamme`), questions éditeurs sans réponse, termes « À confirmer » de plus de deux semaines, relances à faire. Tu l'écris aussi dans `Livrables/Points/Point_AAAA-MM-JJ.md`. Si Hervé a programmé ce point dans Cowork (ce que l'application appelle une « tâche programmée » : une conversation qui se lance seule à l'heure dite), rappelle-lui que Claude Desktop doit être ouvert à l'heure prévue pour que cette conversation atteigne son dossier ; sinon elle se lance sans rien voir. <!-- [R-17] -->

## 6. Le briefing
```
[Verdict en une phrase : où on en est.]
Urgent : [échéance datée la plus proche, ou « rien d'urgent »]
En attente : [1 à 3 fils vérifiés] — dont le plus ancien : [ligne]
Prochaine action : [une]
Je te propose : [une chose concrète]
```
Après-midi : verdict + prochaine action + proposition. Avec un sujet donné : deux lignes de contexte, puis le travail.

## 7. Le contrôle mensuel et le point à deux semaines
Si `Core/ONBOARDING.md` dit `terminé` depuis 14 jours ou plus et que le point de retour n'est pas noté fait : propose-le (questions dans `audit-mensuel.md`). Si le dernier audit date de plus de 30 jours : propose l'audit. Jamais les deux le même jour, et jamais pendant la mise en place. <!-- [D-08] -->
