# Chronologia — contexte pour Claude Code

Système à la croisée de la prosopographie, de la généalogie et de l'analyse relationnelle. Modèle de données historique orienté événements et factoïdes, avec saisie assistée par modèles de langage et import depuis GeneWeb.

## Contexte pour les agents

- `AGENTS.md` : état exact du projet, commandes, garde-fous et feuille de route de reprise. À lire en premier.
- CLI : `uv run python -m chronologia importer | info-lot | rechercher | rapprocher` (détails dans `AGENTS.md`).

## Source de vérité

- `docs/modele-evenement-masque-factoide.md` : le document de référence (version 0.13). Toute décision de modèle s'y consigne d'abord : ligne dans le « Journal des versions », section concernée, puis section 9 (décisions et questions ouvertes).
- `docs/etude-page-claude.html` est **généré** : ne pas l'éditer à la main. `python3 tools/build_page.py` le régénère.
- `docs/geneweb/` : références du format GeneWeb (`.gw`, wikitext), à consulter pour le connecteur d'import. Documentation externe, pas une décision de modèle.
- `maquettes/design/` : copie des cinq écrans de la maquette (format `.dc.html` du canevas Design de claude.ai). Ils ne s'affichent que dans ce canevas ; ici, c'est une archive de référence.

## Principes du modèle (à respecter dans tout code)

- Trois couches : **Source** (ce qui est écrit, insertion seule), **Interprétation** (ce que l'on conclut, révisable), **Référentiels**. Plus un schéma `saisie` pour les brouillons et une couche **Travail** (dépouillements, lacunes, notes, arbitrages, scénarios, délégations), v0.11 à v0.13. Doctrine : la machine retire la copie, pas la lecture (§1.1).
- Quatre agrégations symétriques, toutes par identification révisable (degré certain/probable/possible, statut proposé/actif/rejeté, conclusion) : PASSAGE → SOURCE, MASQUE → PERSONNE, FACTOIDE → EVENEMENT, MENTION_LIEU → LIEU_HISTORIQUE ou SITE.
- Règles d'intégrité R1 à R34 (sections 4.5 et 7.6). Les plus structurantes pour le code : R2 (pas d'information sans factoïde), R10 (couche Source immuable), R11 (une seule identification active par élément), R13 (aucune résolution dans la couche Source), R18 (la machine propose, l'humain verse), R22 (une conclusion, plusieurs effets, un seul retrait), R23 (incertitude assumée ≠ conflit), R24 (rien n'est masqué en silence), R26 (un rapprochement calculé n'est que « possible » ou « probable »), R27 (une question tranchée n'est pas reposée par la machine), R28 (pas de raisonnement circulaire, pas de retrait en cascade silencieux), R29 (un comptage montre ses hypothèses), R30 (pas de texte libre sans statut), R31 (une hypothèse se teste à part), R32 (une question remontée n'est jamais enterrée), R33 (une délégation est mesurée, bornée et réversible), R34 (une relecture s'ajoute à la première).
- Prochaine règle : R35. Numérotation continue, jamais réutilisée.

## Choix techniques retenus

- PostgreSQL + PostGIS + btree_gist ; schémas `saisie`, `source`, `interp`, `ref`, `travail`.
- Coordonnées stockées en WGS 84 (EPSG:4326) ; calculs métriques en Lambert‑93 (EPSG:2154).
- Backend Python (API FastAPI, interface React + TypeScript : voir `AGENTS.md`). Connecteur GeneWeb : le parseur Python `geneweb-py` du monorepo `prosopo-gw` (`../prosopo-gw/core`), qui lit le `.gw` exporté par `gwu` (décision 22 ; voie OCaml abandonnée).
- Modèles de langage derrière une passerelle (contrat JSON) ; déploiement hybride (serveur local, services en ligne, petits modèles locaux).

## Prochaine étape (section 9 et feuille de route)

Fait : import de vraies bases GeneWeb (SQLite immuable), identifications MASQUE → PERSONNE, rapprochement d'homonymes (état détaillé dans `AGENTS.md`).

1. Validation des propositions d'identification (écran ou commande), calibration du barème v1.
2. Rendre le socle exécutable en PostgreSQL : schéma SQL complet + tests automatiques des règles + rejeu des scénarios du document (baptême aux deux dates, Pierre Martin, chapelle de 1709).
3. Lieux : normalisation MENTION_LIEU → LIEU_HISTORIQUE, articulation avec l'export pivot de l'atelier de prosopo-gw (§9.2-9).
4. Test de la saisie assistée sur ~50 actes annotés à la main.
5. Développement des écrans : validation et rattachements d'abord.

## Conventions

- Langue du projet : français (documentation, noms de tables et de colonnes sans accents).
- Les esquisses SQL et OCaml (8.3, pour mémoire) du document ne sont pas testées : les traiter comme des intentions, pas comme du code acquis.
- Les exemples (Saint‑Aubin, Pierre Martin, Les Essarts, chapelle de la Croix‑Blanche) sont fictifs.
