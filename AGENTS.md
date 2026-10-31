# AGENTS.md — état du projet Chronologia

Contexte de reprise pour les agents IA. Source de vérité du modèle : `docs/modele-evenement-masque-factoide.md` (voir `CLAUDE.md`).

## État (modèle v0.9 : jalon achevé et validé sur données réelles)

- **Persistance SQLite** (`chronologia/persistence/`) : schéma portable, schémas PostgreSQL simulés par préfixe de table : `source_*` (lot_import, passage, masque, factoide, participation, relation, qualite, mention_lieu), `interp_*` (evenement, ident_evenement, conclusion), `audit_retractation`. Décision 18.
- **R10** : insertion seule, appliquée par triggers `BEFORE UPDATE` / `BEFORE DELETE` sur toutes les tables. Une rétractation s'écrit dans `audit_retractation` (motifs `retractation`, `modification`, `reconduction`), jamais par suppression. Vues actives : `source_factoide_actif`, `interp_conclusion_actif`.
- **R13** : fidélité textuelle intégrale. Aucune déduplication silencieuse (ex. relations répétées conservées, clé substitut `id`), texte d'origine gardé (`date_brute`).
- **Adaptateur GeneWeb** (`chronologia/adapters/geneweb/`) : projection de la `Genealogy` de toldot vers la couche Source, différentiel de lots (`comparer_lots`, décision 16).
- **Service** (`chronologia/services/importation.py`) : `importer_fichier_geneweb` (empreinte SHA-256, idempotence, lot et différentiel en une transaction). `relire_lot` reconstruit un `LotImport` depuis la base.
- **Identifications de l'import** (`chronologia/persistence/identification.py`, décision 19) : une personne par clé GeneWeb dans la lignée du fichier, réutilisée au réimport ; triggers R11 et R18.
- **Rapprochement d'homonymes** (décision 20) : moteur pur dans `chronologia/interpretation/` (normalisation et clé phonétique, profils, règles v1 onomastique, chronologie et réseau familial, barème v1 avec veto à l'échelle de la paire) ; lecture des profils (`persistence/lecture_profils.py`, vue active matérialisée) et écriture des propositions (`persistence/propositions.py`, contributeur agent `apparieur_homonymes`, indices calculés) ; service atomique `proposer_rapprochements` (`services/rapprochement.py`). R26 : un agent ne propose que « possible » ou « probable » (trigger), jamais sans indice, jamais un couple déjà identifié (R24).
- **CLI** : `uv run python -m chronologia importer <fichier.gw> --base <db>`, `info-lot`, `rechercher --personne/--lieu/--date`, `rapprocher --base <db> [--intra-base]`. Projet en `package = false` (pas de script installé).
- **Performances mesurées** (plus gros fichier réel, en mémoire) : ~166 000 entités importées en ~8 s, insertion du lot 0,7 s, réimport identique 0,03 s, requêtes de consultation < 3 ms. Rapprochement intra-base (34 744 masques, 8 573 personnes) : import ~7,5 s, rapprochement complet 2,4 s (dont lecture des profils 0,8 s), pic mémoire 270 Mo ; 1 641 paires examinées, 80 % écartées par veto chronologique, 21 propositions « possible ».

## Parseur GeneWeb

Source unique : dépôt `toldot` (`../toldot`, package `geneweb-py`, dépendance locale éditable). Toute adaptation du format GeneWeb se fait dans toldot, jamais copiée ici. Toldot est public : fixtures synthétiques seulement.

## Garde-fous

- Bases réelles (`~/code_dev/TOLDOT/x_archive_GENEWEB_PROJECTS/...`) : lecture seule, jamais copiées, importées ni versionnées ici ; essais par scripts éphémères hors Git ; aucune donnée nominative dans les logs ni comptes-rendus (agrégats seulement).
- Toute décision de modèle se consigne d'abord dans le document de référence (journal, section concernée, §9). Prochaine règle : R27.
- `docs/etude-page-claude.html` est généré : `uv run --no-project --with markdown python tools/build_page.py`.
- TDD ; vérifications : `uv run python -m pytest -q` et `uv run mypy` (0 erreur).
- Pas de `git add -A` ni de push sans accord explicite.

## Reprise : feuille de route

1. Petits restes : `nb_ajouts` dans `BilanApplicationDiff` (tiré de `diff.ajouts`) et dans le résumé de la CLI ; règle B905 (`zip` sans `strict=`) et formatage en attente dans `chronologia/cli.py` et `tests/test_cli.py`.
2. ✅ **Identification prosopographique MASQUE → PERSONNE** (couche Interprétation, achevée en v0.9) : schéma arrêté en v0.8 (décision 19, R25). Six tables : `interp_contributeur`, `interp_personne` (coquille, `same_as_id`), `interp_ident_personne` (proposition immuable), `interp_ident_personne_statut` (journal des décisions, vue `interp_ident_personne_actif`), `interp_indice` (faisceau d'indices), `interp_conclusion_effet` (R22) ; `interp_conclusion.cible_masque_id` devient facultatif. Triggers R11 (une identification active par masque) et R18 (un agent ne verse que « proposé ») ; schéma en place et testé (`tests/persistence/test_schema_interpretation.py`). Identifications de l'import GeneWeb faites (`chronologia/persistence/identification.py`, décision 19 : une personne par clé en `ref` dans la lignée du fichier, réutilisée au réimport, anciennes identifications retirées par `audit_retractation`, repli en « proposé » si une décision humaine diverge, R24 ; réimport complet du plus gros fichier réel en ~4 s). Rapprochement d'homonymes par faisceau d'indices fait (décision 20, R26, voir l'état ci-dessus).
3. **Validation des propositions** : écran ou commande pour accepter (« actif ») ou rejeter les identifications proposées par l'agent, avec leur faisceau d'indices ; calibration du barème v1 sur un échantillon annoté (§9.2-1).
4. Ensuite : normalisation des lieux (MENTION_LIEU → LIEU_HISTORIQUE), exports, saisie assistée.
