# Journal des versions — extension aura-localisation

Les nouveautés expliquées à l'utilisateur sont dans `skills/mise-a-jour/references/systeme/GUIDE_AURA.md` (seul endroit). Ce fichier est le journal technique.

## 3.0.3 — 2026-10-04
- Installation par fichier (Customize > Plugins > Add > Upload plugin) : le contrôle du téléversement refuse toute description de skill qui contient des chevrons, pris pour des balises XML. Quatre descriptions en avaient (« Glossaire_<Gamme> », « <Éditeur> », « <Gamme> », « <b> ») : elles sont réécrites sans chevrons, et l'atelier contrôle désormais chaque en-tête avant de fabriquer un fichier.
- Mise à jour : le guide `GUIDE_AURA.md`, la carte `Core/Skills.md` et le skill disent les deux chemins des nouvelles versions — toutes seules depuis la source de Dorian, par un nouveau fichier zip si le plugin a été installé depuis un fichier (c'est le cas d'Hervé depuis le 04/10). Un dossier déjà passé en 3.0 garde l'ancien texte jusqu'à la prochaine version qui change sa couche locale.

## 3.0.2 — 2026-10-04
- Mise à jour d'un dossier déjà commencé : la note de passage `Core/PASSAGE_V3.md`, écrite par l'AURA de la version 2.0 à partir du fichier `skills/mise-a-jour/references/passage-v2-vers-v3.md` que Dorian lui donne, fixe l'étape où reprendre la mise en place (plus de question si elle est lisible).
- Preuve de conservation : `scripts/releve.py` relève chaque fichier du dossier avant la première écriture, le compare octet pour octet après, et écrit `_archives-systeme/PREUVE_MISE_A_JOUR_AAAA-MM-JJ.md` ; le compte rendu montre « MÉMOIRE INTACTE » et la liste des fichiers vérifiés.

## 3.0.1 — 2026-10-02
Relecture adverse de 55 points de la 3.0.0, chacun contre-vérifié par un relecteur indépendant (53 corrigés, 2 limites assumées et écrites : R-34, R-35).
- Mise à jour : empreinte exacte des fichiers d'origine (taille, sha256, lignes témoins), liste des fichiers écrits recopiée en entier au compte rendu, rien n'est écrit dans un dossier sans `Core/VERSION.md`, branche « question de version » en lecture seule, vocabulaire « le plugin AURA » et « conversation », gestes « Check for updates » justes, commande acceptée sans accent ; la couche système est toujours écrite puis vérifiée sur son contenu (et non plus seulement sa présence), et seuls les fichiers vus dans une vraie liste du dossier sont cités (deux défauts trouvés par le test réel).
- Noyau : règle IMPORT écrite une seule fois (l'original ne bouge jamais), sauvegarde légère puis complète (Journal avant CONTEXT), fils de `Core/Suivi.md` clos et jamais effacés, `Core/_EN_COURS.md` par projet, règle des agents écrite une fois, version lue dans `plugin.json`, skills `aura-localisation:` préférés aux homonymes.
- Toute écriture refusée dans le dossier du plugin (`lecture.hors_du_plugin`, code 2) ; sorties de la gestion de gamme en écriture exclusive (`commun.sortie_libre`).
- Lecteur commun : séparateur CSV choisi comme en 3.0.0 (la moitié des 10 premières lignes), puis refusé s'il couperait des phrases : une colonne de phrases n'est plus coupée (« 12,5% », « ×1,5 », « 45,5×30,5 cm », « A3,B4 » compris), les tableaux restent des tableaux (titre daté ou complété par l'export, tableau sans en-tête, export Excel par blocs de 16 lignes, ligne « sep=; ») ; fins de ligne universelles ; dates Excel lues comme des dates ; commentaires à thread et notes classiques d'Excel 365.
- Renvois (`renvois.py`) : numéros à un seul niveau relevés (« règle 7 », « règle n° 52 », « règles 3, 4 et 13 ») ; établis par un titre à mot-clé ou des règles 7.1 (dans un livret numéroté 5.1, un titre à un seul niveau sans sous-règles, « Règle 52 : … », est lui-même à lire), sinon « à lire » (code 1), jamais une anomalie ni comptés face à la VO ; numéros à plusieurs niveaux jugés comme en 3.0.0, sur un texte d'abord normalisé (un accent décomposé ne cache plus « règle »).
- Typographie : `--corriger` sur un CSV exige `--colonne` et ne touche qu'elle ; adresses web, e-mails et entités HTML protégés ; décimales anglaises (T10), incises (T11), « ?! » ; colonne introuvable ou 0 segment lu = arrêt.
- Longueurs et comptage : séparateur de milliers retiré avant de comparer les nombres, balises lues par le même motif (`lecture.BALISE`).
- Glossaire et gamme : `segments.py ajouter` (copie datée avant), glossaire non standard rangé dans `Glossaires/` importé comme source, titres publiés et errata alignés sur les 5 statuts et la liste unique des statuts d'erratum, rétroplanning avec validation de la VF par l'éditeur de la VO, registre des questions défini une seule fois, mention de l'IA à l'éditeur réglée par une seule règle.

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
