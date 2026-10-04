# Le point à deux semaines et l'audit mensuel

## Le point à deux semaines (une fois, après la mise en place)
Proposé au START quand `Core/ONBOARDING.md` le prévoit : « Ça fait deux semaines qu'on travaille ensemble. Tu as 20 minutes pour un point ? » Quatre questions :
1. Qu'as-tu utilisé depuis l'installation ?
2. Une situation où tu aurais voulu mon aide sans savoir comment la demander ?
3. Quelque chose que je fais qui t'agace ou ne sert à rien ?
4. Le plus utile jusqu'ici ?
Les réponses vont dans `Core/Preferences.md` (règles) et `Core/Observations.md` (frictions). Tu proposes UN ajustement concret. Puis `point à deux semaines: fait le [date]`.

## L'audit mensuel
Proposé au START si le dernier audit (noté au Journal : `## Audit AAAA-MM-JJ`) date de plus de 30 jours. Jamais pendant la mise en place, jamais le même jour que le point à deux semaines.

### Ce que tu vérifies, avant de présenter quoi que ce soit
- **Glossaires** (script du skill `glossaire` sur chaque fichier) : même mot anglais traduit différemment selon les gammes — à **vérifier** (ce n'est pas forcément une erreur : le rapprochement se fait par la mécanique) ; termes « À confirmer » de plus de deux semaines ; doublons ; genres manquants ; écarts volontaires d'Hervé listés comme tels, jamais resignalés.
- **Mémoire** : CONTEXT sous son plafond ; projets terminés encore listés ; sections de `Core/_EN_COURS.md` marquées « livré » (tu proposes de les déplacer dans `Core/Archives/`) ; <!-- [R-31] --> règles contradictoires dans Preferences ; fils de `Core/Suivi.md` sans activité depuis plus de 14 jours ; tâches qui n'avancent plus.
- **evas** : un même mécanisme d'erreur revenu deux fois ou plus → règle renforcée.
- **Observations** <!-- [I-27] --> : `Core/Observations.md` est le carnet où tu notes, pendant le travail, chaque friction : une correction qu'Hervé refait souvent, une étape manuelle qui revient (export d'un glossaire, mise en forme d'une fiche de questions), une méthode qui a très bien marché. À l'audit, tu le relis et tu proposes l'ajustement qui en découle (une règle dans Preferences, un outil sur mesure, ou une remarque pour Dorian s'il s'agit du plugin AURA lui-même).
- **Outils peu utilisés** : signalés, jamais supprimés.

### La consolidation — sans rien effacer <!-- [I-20] -->
- Jamais de suppression dans `Core/` ni dans un glossaire. On **déplace** vers `Core/Archives/` (fichier daté), puis on relit la source et l'archive avant de retirer quoi que ce soit de la source.
- Les fichiers vivants (CONTEXT, Preferences, un glossaire) ne sont jamais réécrits d'office : tu proposes une version consolidée **à côté** (`Core/Archives/Preferences_propose_AAAA-MM-JJ.md`), Hervé valide, puis tu remplaces. À la sauvegarde, CONTEXT n'est que mis à jour section par section, après que chaque ligne retirée a été écrite ailleurs (`sauvegarde.md`, point 8). <!-- [R-26] -->
- Un glossaire n'est jamais réécrit sans son accord : c'est sa mémoire de traducteur, une perte serait irréparable.
- Archivage du Journal par trimestre (voir `sauvegarde.md`).

### Le rapport
```
AUDIT AURA — [date]
🔴 À corriger maintenant : [problème précis + action proposée]
🟠 À traiter ce mois : [problème + suggestion]
🟡 Ce qui marche bien / outils peu utilisés
💡 Une amélioration proposée
Prochain audit proposé vers le [date + 30 jours].
```
