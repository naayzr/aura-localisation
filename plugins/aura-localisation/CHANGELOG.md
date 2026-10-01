# Journal des versions — extension aura-localisation

Les nouveautés expliquées à l'utilisateur sont dans `skills/mise-a-jour/references/systeme/GUIDE_AURA.md` (seul endroit). Ce fichier est le journal technique.

## 3.0.0 — 2026-10-01
- Skill `obsidian` (15e) : installation guidée d'Obsidian (gratuit) et ouverture de HERVÉ WORLD comme coffre, page ACCUEIL et TABLEAU de bord (Bases), fiches d'univers (personnages, lieux, factions, objets) dont le nom français reste celui du glossaire, contrôle `fiches.py` ; guide `GUIDE_OBSIDIAN.md` posé par la mise à jour ; libellés vérifiés dans Obsidian 1.13.7.
- Skill `maquettes` : planche HTML de toutes les cartes en français (débord mesuré dans le navigateur), fichier de fusion InDesign/Affinity, choix d'outil (Claude, plugin Adobe, Affinity, Canva) selon coût et confidentialité.
- Migration des glossaires v2.0 (`gerer_glossaire.py migrer`) ; la mise à jour lit l'état de la mise en place sans deviner (empreinte du profil d'origine, une question).
- Lecteur commun : séparateur CSV lu sur les premières lignes (un texte français contient des virgules), UTF-16 ; Word : zones de texte une fois, notes, en-têtes et pieds.
- Passage de la couche système en extension Cowork, synchronisée depuis ce dépôt. Le dossier de l'utilisateur ne garde qu'une amorce `CLAUDE.md` et sa mémoire.
- Skill `noyau` : démarrage, sauvegarde automatique, capture au fil de l'eau, re-ancrage, garde contre les inventions, règles de travail, diagnostic, audit, mise en place reprise à l'étape atteinte (`Core/ONBOARDING.md`).
- Skill `mise-a-jour` : migration depuis la 2.0 sans modifier aucun fichier de mémoire existant.
- Nouveaux skills : `typographie-fr`, `comptage-caracteres`, `controle-longueur`, `gestion-gamme` (programmes Python, bibliothèque standard).
- Skills métier de la 2.0 portés et corrigés (glossaire unifié : 15 colonnes, 5 statuts, genre des noms inventés).
