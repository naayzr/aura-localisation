# Les rapports : celui de chaque contrôle, et la synthèse finale

> **[EXEMPLE FICTIF]** — le jeu, les règles, les cartes et les chiffres de ce fichier sont construits pour l'illustration.

## 1. Le format commun d'un rapport (contrôle automatique, lot, relecteur)

Un fichier par rapport prévu dans `PLAN.txt`, dans le dossier de relecture, nommé `<nom prévu>.md` :

```
RAPPORT <nom prévu>
Fichier : <fichier relu> — <portée : lot, ou fichier entier>
Constats : <nombre>
Zones non lues : <ce qui n'a pas été lu ou contrôlé, ou « aucune »>
<les constats, ou la sortie réelle du script>
FIN DU RAPPORT
```

**Pour un contrôle par script**, le rapport contient la sortie **réelle** du script, recopiée par l'ordinateur et non retapée. Exemple pour les renvois :
```
{ echo "RAPPORT controle-renvois"; echo "Fichier : <fichier>"; \
  python3 "${CLAUDE_SKILL_DIR}/../qa-coherence/scripts/renvois.py" "<fichier>" --source "<version originale>"; \
  echo "Constats : <nombre lu sur la ligne BILAN>"; echo "Zones non lues : <…>"; \
  echo "FIN DU RAPPORT"; } > "<HERVÉ WORLD>/Livrables/<Projet>/relecture/controle-renvois.md"
```
Même principe pour les scripts des skills `typographie-fr`, `controle-longueur`, `glossaire` et `comptage-caracteres`. Un script qui n'a pas tourné ne laisse **aucun** fichier : c'est ce qui permet à `rapports.py` de le voir manquer.

## 2. La synthèse finale <!-- [I-29] -->

Elle s'écrit **après** `python3 "${CLAUDE_SKILL_DIR}/scripts/rapports.py" <dossier de relecture>`, et en reprend les chiffres tels quels.

```
═══════════════════════════════════════════════════════
RAPPORT DE RELECTURE — <Jeu> — <produit> — <date>
Fichier relu : <copie de travail> · <N> caractères · <M> lots
Mode : relecture standard | <K> relecteurs en parallèle
═══════════════════════════════════════════════════════

CE QUI A ÉTÉ VÉRIFIÉ
Rapports prévus : 10 — rendus complets : 9 sur 10.
- controle-typographie : MANQUANT → la typographie n'a pas été vérifiée.
- controle-longueur : « BILAN : 4 champs au-delà du cadre, 0 balise perdue »
- controle-glossaire : « [G-01] § 88 : "Bouger" au lieu de "Déplacer" (Confirmé) »
- controle-comptage : « 340 cartes en anglais, 338 en français : manquent C-112, C-207 »
- controle-renvois : « BILAN : 2 anomalie(s) de renvoi ou de numérotation. »
- lot-01 : « [LOG-06] carte "Second souffle" — effet facultatif devenu obligatoire »
- lot-02 : « [STY-01] § 40 à § 75 — passage au tutoiement au chapitre 4 »
- lot-03 : 0 constat — vérifié : logique, style, renvois, sens du lot 3
- lot-04 : « [REF-01] § 160 (règle 5.3) — renvoi vers une règle hors sujet »
- lot-05 : « [LOG-03] § 230 — égalité non traitée, ni dans la VO »
Essai sur copie sabotée : 3 fautes glissées, 3 retrouvées (glossaire, longueur, renvois) —
  la typographie n'a pas pu être essayée.
Zones non lues : lot-02, tableau des coûts en image (§ 61) ; dos des cartes (non fournis).

VERDICT : VÉRIFICATION INCOMPLÈTE — la typographie n'a pas été vérifiée.
(Les autres verdicts possibles : OK À LIVRER · CORRECTIONS REQUISES.)

RÉSUMÉ
• Bloquant : 2 · Important : 3 · Mineur : 5 · Questions éditeur : 2

───────────────────────────────────────────────────────
BLOQUANT — à corriger avant toute livraison
───────────────────────────────────────────────────────
[BLQ-01] Carte « Second souffle » — un effet facultatif devenu obligatoire
  Vu par : lecture du lot 1.
  VO : You may draw a card. — Traduction : « Piochez une carte. »
  Correction proposée : « Vous pouvez piocher une carte. » (et contrôle de longueur du champ)

[BLQ-02] Cartes C-112 et C-207 absentes de la traduction
  Vu par : contrôle de comptage.
  Correction : les traduire ; les portes de livraison ne peuvent pas être cochées sans elles.

───────────────────────────────────────────────────────
IMPORTANT — à traiter avant livraison si possible
───────────────────────────────────────────────────────
[IMP-01] Tutoiement au chapitre 4 (§ 40 à § 75) ; la fiche éditeur dit vouvoiement.
[IMP-02] « Bouger » à 3 endroits au lieu de « Déplacer » (terme Confirmé) — § 88, § 102, § 140.
[IMP-03] Renvoi de la règle 5.3 vers la 3.4, hors sujet — même chose dans la VO → 2e question à l'éditeur.

───────────────────────────────────────────────────────
MINEUR
───────────────────────────────────────────────────────
[MIN-01] … 

───────────────────────────────────────────────────────
QUESTIONS À L'ÉDITEUR (erreurs de la version originale)
───────────────────────────────────────────────────────
Inscrites au registre Core/Questions_Editeurs.md, en clair :
- Égalité en fin de partie : non traitée dans la version originale (§ 230). Quelle règle appliquer ?
- Règle 5.3 : la version originale renvoie à la règle 3.4, qui traite des ressources. Faut-il lire 3.5 ?

───────────────────────────────────────────────────────
CE QUI RESTE AVANT DE POUVOIR DIRE « OK À LIVRER »
───────────────────────────────────────────────────────
- relancer le contrôle de typographie (skill typographie-fr), puis compter à nouveau ;
- corriger BLQ-01 et BLQ-02 ;
- obtenir les 2 réponses de l'éditeur.
═══════════════════════════════════════════════════════
```

## 3. Les règles que la synthèse ne transgresse jamais

1. **Le compte d'abord**, recopié de `rapports.py` : « Rapports prévus : N — rendus complets : M sur N. »
2. **Un extrait par rapport rendu**, entre guillemets, tel qu'il est écrit dans le rapport. Pas de paraphrase qui pourrait masquer un rapport vide.
3. **Un rapport manquant reste manquant.** Sa phrase (« la typographie n'a pas été vérifiée ») figure dans « Ce qui a été vérifié » ET dans le verdict. On ne déduit pas qu'un contrôle « serait passé ».
4. **Les zones non lues et l'essai sur copie sabotée** sont écrits, même quand tout va bien.
5. **OK À LIVRER** exige : tous les rapports prévus rendus, zéro bloquant, chaque porte de livraison de `Core/_EN_COURS.md` cochée avec son chiffre.
6. **Ce qui part chez l'éditeur** (questions, courriel) s'écrit en clair, sans les codes `[BLQ-01]`, `[LOG-06]` ni nom de skill : ces codes servent à Hervé.
