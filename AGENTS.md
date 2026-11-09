# AGENTS.md — état du projet Chronologia

Contexte de reprise pour les agents IA. Source de vérité du modèle : `docs/modele-evenement-masque-factoide.md` (voir `CLAUDE.md`).

## État (modèle v0.9 : jalon achevé et validé sur données réelles)

- **Persistance SQLite** (`chronologia/persistence/`) : schéma portable, schémas PostgreSQL simulés par préfixe de table : `source_*` (lot_import, passage, masque, factoide, participation, relation, qualite, mention_lieu), `interp_*` (evenement, ident_evenement, conclusion), `audit_retractation`. Décision 18.
- **R10** : insertion seule, appliquée par triggers `BEFORE UPDATE` / `BEFORE DELETE` sur toutes les tables. Une rétractation s'écrit dans `audit_retractation` (motifs `retractation`, `modification`, `reconduction`), jamais par suppression. Vues actives : `source_factoide_actif`, `interp_conclusion_actif`.
- **R13** : fidélité textuelle intégrale. Aucune déduplication silencieuse (ex. relations répétées conservées, clé substitut `id`), texte d'origine gardé (`date_brute`).
- **Adaptateur GeneWeb** (`chronologia/adapters/geneweb/`) : projection de la `Genealogy` de prosopo-gw vers la couche Source, différentiel de lots (`comparer_lots`, décision 16).
- **Service** (`chronologia/services/importation.py`) : `importer_fichier_geneweb` (empreinte SHA-256, idempotence, lot et différentiel en une transaction). `relire_lot` reconstruit un `LotImport` depuis la base.
- **Identifications de l'import** (`chronologia/persistence/identification.py`, décision 19) : une personne par clé GeneWeb dans la lignée du fichier, réutilisée au réimport ; triggers R11 et R18.
- **Rapprochement d'homonymes** (décision 20) : moteur pur dans `chronologia/interpretation/` (normalisation et clé phonétique, profils, règles v1 onomastique, chronologie et réseau familial, barème v1 avec veto à l'échelle de la paire) ; lecture des profils (`persistence/lecture_profils.py`, vue active matérialisée) et écriture des propositions (`persistence/propositions.py`, contributeur agent `apparieur_homonymes`, indices calculés) ; service atomique `proposer_rapprochements` (`services/rapprochement.py`). R26 : un agent ne propose que « possible » ou « probable » (trigger), jamais sans indice, jamais un couple déjà identifié (R24).
- **CLI** : `uv run python -m chronologia importer <fichier.gw> --base <db>`, `info-lot`, `rechercher --personne/--lieu/--date`, `rapprocher --base <db> [--intra-base]`. Projet en `package = false` (pas de script installé).
- **Performances mesurées** (plus gros fichier réel, en mémoire) : ~166 000 entités importées en ~8 s, insertion du lot 0,7 s, réimport identique 0,03 s, requêtes de consultation < 3 ms. Rapprochement intra-base (34 744 masques, 8 573 personnes) : import ~7,5 s, rapprochement complet 2,4 s (dont lecture des profils 0,8 s), pic mémoire 270 Mo ; 1 641 paires examinées, 80 % écartées par veto chronologique, 21 propositions « possible ».

## Choix de pile (retenus)

- **Langage du cœur** : Python (backend, import, rapprochement, passerelle vers les modèles de langage). Pas de réécriture : le socle et le parseur `prosopo-gw` sont en Python et testés. OCaml abandonné pour le connecteur GeneWeb (le parseur Python le remplace). Rust seulement en extension isolée (PyO3) si le profilage montre un goulot précis ; Go écarté.
- **API** : FastAPI (déjà utilisé dans prosopo-gw). Les écrans passent toujours par l'API, jamais autour (R18, R24).
- **Interface** (dossier `web/`, à créer) : SPA React + TypeScript + Vite, servie en fichiers statiques par FastAPI ou Traefik (aucun serveur Node en production). TanStack Query (appels et cache) et TanStack Table (listes de propositions), Tailwind + composants Radix (ou shadcn/ui), MapLibre GL pour les cartes. Types TypeScript générés depuis l'OpenAPI de FastAPI (`openapi-typescript`) pour éviter la dérive du contrat.
- **Ordre de développement des écrans** : validation, puis rattachements (feuille de route de `CLAUDE.md`). Une première version HTMX + Jinja de l'écran de validation reste possible pour éviter Node au début, mais serait à réécrire avec les cartes et les frises.

## Parseur GeneWeb

Source unique : dépôt `prosopo-gw` (`../prosopo-gw`), monorepo `uv` (Python ≥ 3.11) à deux membres : `core` (package `geneweb-py`, seule dépendance de Chronologia, en locale éditable `../prosopo-gw/core`) et `atelier` (`prosopo-gw-atelier`, nettoyage des lieux, export « pivot »). Toute adaptation du format GeneWeb se fait dans prosopo-gw, jamais copiée ici. prosopo-gw est public : fixtures synthétiques seulement.

- Le parseur finalise comme `gwc` (décision 21) et garde entier un complément de lieu entre crochets qui contient « - » (décision 22, test `test_complement_entre_crochets_avec_tiret_reste_entier`).
- `core` déduit aussi des organisations (`Organization`, fichier compagnon `org.json`) et des « expériences partagées » : calculs, non importés (question ouverte §9.2-6).
- L'export pivot de l'atelier (`lieux`, `niveaux_lieux`, `ecritures_lieux`) est un candidat pour les lieux historiques ; articulation ouverte (§9.2-9).
- Après une évolution de prosopo-gw : `uv sync`, puis `uv run python -m pytest -q` et `uv run mypy`.

## Garde-fous

- Bases réelles (`~/code_dev/TOLDOT/xxx_archive_GENEWEB_PROJECTS/...`) : lecture seule, jamais copiées, importées ni versionnées ici ; essais par scripts éphémères hors Git ; aucune donnée nominative dans les logs ni comptes-rendus (agrégats seulement).
- Toute décision de modèle se consigne d'abord dans le document de référence (journal, section concernée, §9). Prochaine règle : R29.
- `docs/etude-page-claude.html` est généré : `uv run --no-project --with markdown python tools/build_page.py`.
- TDD ; vérifications : `uv run python -m pytest -q` et `uv run mypy` (0 erreur).
- Pas de `git add -A` ni de push sans accord explicite.

## Reprise : feuille de route

1. Petits restes : `nb_ajouts` dans `BilanApplicationDiff` (tiré de `diff.ajouts`) et dans le résumé de la CLI ; règle B905 (`zip` sans `strict=`) et formatage en attente dans `chronologia/cli.py` et `tests/test_cli.py`.
2. ✅ **Identification prosopographique MASQUE → PERSONNE** (couche Interprétation, achevée en v0.9) : schéma arrêté en v0.8 (décision 19, R25). Six tables : `interp_contributeur`, `interp_personne` (coquille, `same_as_id`), `interp_ident_personne` (proposition immuable), `interp_ident_personne_statut` (journal des décisions, vue `interp_ident_personne_actif`), `interp_indice` (faisceau d'indices), `interp_conclusion_effet` (R22) ; `interp_conclusion.cible_masque_id` devient facultatif. Triggers R11 (une identification active par masque) et R18 (un agent ne verse que « proposé ») ; schéma en place et testé (`tests/persistence/test_schema_interpretation.py`). Identifications de l'import GeneWeb faites (`chronologia/persistence/identification.py`, décision 19 : une personne par clé en `ref` dans la lignée du fichier, réutilisée au réimport, anciennes identifications retirées par `audit_retractation`, repli en « proposé » si une décision humaine diverge, R24 ; réimport complet du plus gros fichier réel en ~4 s). Rapprochement d'homonymes par faisceau d'indices fait (décision 20, R26, voir l'état ci-dessus).
3. **Validation des propositions** : écran ou commande pour accepter (« actif ») ou rejeter les identifications proposées par l'agent, avec leur faisceau d'indices ; calibration du barème v1 sur un échantillon annoté (§9.2-1).
4. Ensuite : normalisation des lieux (MENTION_LIEU → LIEU_HISTORIQUE, en s'appuyant sur l'export pivot de l'atelier de prosopo-gw si §9.2-9 est tranchée), exports, saisie assistée.
5. **Dates (décision 23, v0.9.4)** : colonne `determination_date` (attestée, déduite, estimée, inconnue ; « inconnue » pour l'import GeneWeb) et liste fermée pour `calendrier`, dont le républicain (suffixe `F` de GeneWeb, déjà converti par `geneweb-py` pour les ans I à XIV ; l'hébreu reste sans bornes, texte gardé). À faire avec le socle PostgreSQL.
6. **Connecteurs Heurist (décision 24)** : import d'une base Heurist et export vers Heurist pour la publication, après le socle PostgreSQL.
7. **Reprises de nodegoat, Arches et ResearchSpace (décisions 26 à 32, v0.10, `docs/etude-nodegoat-arches-researchspace.md`)** :
   - avec le socle PostgreSQL : direction et écart dans CONTRAINTE_TEMPORELLE (26), `mode` de CONCLUSION (27), table CONCLUSION_PREMISSE (28), et R28 (pas de cycle, retrait signalé et non appliqué en cascade) ;
   - avant la validation des propositions : table ANOMALIE_IMPORT et commande d'annulation d'un lot, R9 (29) ;
   - avec l'étape « Lieux » : FORME_LIEU, mémoire des formes écrites (30) ;
   - avec les exports et la saisie : EDTF (31, licence de `edtf` à vérifier) ;
   - avec les connecteurs : cycle de publication (32).
