# Projet Hesdin-Lanchères, chantiers 1 et 2 (inventaire et jeu étalon) : plan d'exécution

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**But :** doter Chronologia de l'outillage générique des deux premiers chantiers. Il doit :
- valider un tableau d'inventaire ;
- valider des fiches structurées ;
- tirer un étalon et sa seconde lecture de façon rejouable ;
- mesurer la machine, Socface et la seconde lecture contre cet étalon.

**Architecture :** un sous-paquet `chronologia/etalon/`, indépendant des couches Source et Interprétation, car l'étalon doit être indépendant du logiciel qu'il juge (§8.1).
- Les données vivent **hors du dépôt**, dans un répertoire passé en argument : inventaire, cadres, tirages, fiches et exports.
- Le dépôt ne contient que les schémas, les scripts, les conventions et des fixtures synthétiques.
- Trois sous-commandes s'ajoutent à la CLI existante : `etalon-inventaire`, `etalon-tirer` et `etalon-mesurer`.

**Pile :** Python ≥ 3.12, `argparse` (CLI existante), PyYAML, jsonschema (Draft 2020-12), jiwer ≥ 3.0 (CER, WER), pytest, mypy strict.

**Spec :** `docs/superpowers/specs/2026-11-11-projet-hesdin-design.md` : §8 principalement, plus §4.3 et §6 pour les garde-fous.

**Révision du 11/11/2026 :** le plan intègre une relecture critique faite par Codex. Les points retenus sont repris dans les règles des tâches 3 à 7.

## Contraintes globales

- Aucune donnée nominative réelle dans le dépôt, les journaux, les messages d'erreur ou les comptes rendus : agrégats seulement (§6, `AGENTS.md`).
  - Un message d'erreur cite le fichier, le chemin du champ et un code, **jamais la valeur**.
  - Les fixtures sont **synthétiques**, avec des noms visiblement inventés.
- Rien de propre à une commune dans le code (§8.6, critère 6). La commune, la période et les tranches sont des paramètres.
- Valeurs « telles qu'écrites » (R13). Ni l'étalon ni la comparaison ne normalisent, au-delà de la forme NFC d'Unicode et du repli des espaces.
- Un même schéma de fiche pour tous les terrains. Une particularité locale élargit le schéma, sans jamais créer de variante (garde-fou n° 1).
- Un tirage se rejoue : avec les mêmes entrées, les mêmes paramètres et la même graine, `tirage.csv` est identique à l'octet près. Seul `tirage.meta.json` porte une date.
- Un acte tiré illisible reste dans l'étalon (§8.3).
- Les mesures sont toujours séparées par commune et par source comparée. Il n'y a jamais de cumul entre Hesdin et Lanchères (§8.3).
- Langue : français ; identifiants sans accents.
- Vérifications à chaque tâche : `uv run python -m pytest -q` et `uv run mypy`, avec 0 erreur.

## Points de vigilance de la revue

1. **Fuite nominative sur entrée invalide.** Une fiche invalide ou un YAML malformé ne fait apparaître aucune valeur, ni sur stdout ni sur stderr, ni dans les fichiers produits. Testé aux tâches 3 et 7 avec des valeurs sentinelles.
2. **Données dans le dépôt.** Chaque chemin lu ou écrit, y compris un fichier de sortie existant qui serait un lien symbolique, est refusé s'il se résout sous la racine du dépôt. Testé aux tâches 1 et 7.
3. **Omissions favorables.** Une personne, une ligne ou un fichier de l'étalon absent de l'autre côté compte en faux négatifs pour tous ses champs : on ne peut pas améliorer ses scores en omettant les cas difficiles. Testé aux tâches 6 et 7.
4. **Strate vide, lacune.** Une strate vide ou une année absente n'est jamais tirée, mais elle est déclarée dans les métadonnées (R24, R29). Testé à la tâche 4.
5. **Petits effectifs.** Le cas d'une strate de 1 acte, d'égalités de restes, ou d'un `n` supérieur à la population est traité par une règle explicite, jamais par hasard. Testé à la tâche 4.

---

### Tâche 1 : sous-paquet `etalon`, dépendances et garde-fou du répertoire de données

**Fichiers :**
- Modifier `pyproject.toml` :
  - dépendances `pyyaml>=6`, `jsonschema>=4.21` et `jiwer>=3.0` ;
  - groupe dev `types-PyYAML` et `types-jsonschema` ;
  - une section `[[tool.mypy.overrides]]` pour `module = ["jiwer", "jiwer.*"]`, avec `ignore_missing_imports = true`.
- Créer : `chronologia/etalon/__init__.py`, `chronologia/etalon/donnees.py`.
- Test : `tests/etalon/__init__.py`, `tests/etalon/test_donnees.py`.

**Interfaces produites :**
- `class DonneesDansLeDepot(ValueError)`.
- `racine_depot() -> Path` : racine du dépôt, calculée depuis `__file__` **à l'appel**, ce qui permet de la remplacer par `monkeypatch` dans les tests.
- `verifier_hors_depot(chemin: Path, racine: Path | None = None) -> Path` :
  - renvoie `chemin.resolve()` ;
  - lève `DonneesDansLeDepot` si ce chemin résolu est sous `racine or racine_depot()` ;
  - le message cite le chemin, ce qui n'est pas une donnée nominative.

- [ ] **Étape 1 : écrire les tests**
  - `test_chemin_hors_depot_accepte`.
  - `test_chemin_dans_le_depot_refuse`.
  - `test_lien_symbolique_vers_le_depot_refuse` : un lien hors du dépôt qui pointe dans le dépôt est refusé.
  - `test_racine_par_defaut_resolue_a_l_appel` : avec `monkeypatch.setattr(donnees, "racine_depot", lambda: tmp_path / "depot")`, un chemin sous `tmp_path / "depot"` est refusé.
- [ ] **Étape 2 :** lancer `uv sync` puis `uv run python -m pytest tests/etalon -q`. Les tests doivent échouer à l'import.
- [ ] **Étape 3 :** implémenter.
- [ ] **Étape 4 :** pytest et mypy au vert.
- [ ] **Étape 5 :** commit `feat(etalon): sous-paquet etalon et garde-fou des données hors dépôt`.

### Tâche 2 : tableau d'inventaire et registre des vérifications

**Inventaire :** fichier `inventaire.csv`, en UTF-8 avec en-tête. Colonnes, dans cet ordre :
`commune, service, type, annee_debut, annee_fin, cote, disponibilite, nb_vues, estimation_unites, socface, remarques, motif_lacune`.

- `type` ∈ {`naissances`, `mariages`, `deces`, `nmd`, `tables_decennales`, `recensement`, `publications`, `inscription_maritime`}. `nmd` désigne un registre qui réunit naissances, mariages et décès ; l'inventaire ne le décompose pas, la décomposition se fait dans le cadre de tirage (tâche 4).
- `disponibilite` ∈ {`en_ligne`, `salle_lecture`, `absent`}.
- `socface` ∈ {`oui`, `non`, `partiel`} pour `recensement`, vide sinon.
- `nb_vues` et `estimation_unites` : entier positif ou nul, ou vide.
- `motif_lacune` est **obligatoire** si `disponibilite = absent` (lacune motivée, décision 39).

**Correspondance Socface / vues :** fichier `correspondance_socface.csv`, avec les colonnes `commune, annee, page_socface, cote, vue`. Il est validé par les mêmes règles de types (§8.2 : correspondance entre pages Socface et vues des archives).

**Registre des vérifications :** fichier `verifications.csv`, avec les colonnes `numero, service, objet, statut, date, reference, stockage_local, stockage_serveur`.
- `statut` ∈ {`a_faire`, `demande`, `repondu`}.
- `stockage_local` et `stockage_serveur` ∈ {`oui`, `non`, `inconnu`}.
- Il sert à donner une réponse écrite aux vérifications de §8.2 (critère 2 de §8.6).

**Fichiers :**
- Créer : `chronologia/etalon/inventaire.py`.
- Test : `tests/etalon/test_inventaire.py`.
- Fixtures : `tests/etalon/fixtures/inventaire_synthetique.csv` (commune « Villefictive », 6 lignes dont une `absent` motivée), `correspondance_synthetique.csv` et `verifications_synthetique.csv`.

**Interfaces produites :**
- `@dataclass(frozen=True) class UniteInventaire` :
  - un champ par colonne ;
  - années en `int` ;
  - `nb_vues` et `estimation_unites` en `int | None`.
- `charger_inventaire(chemin: Path) -> tuple[list[UniteInventaire], list[str]]` :
  - renvoie les unités valides et les erreurs `"ligne N : colonne C : code"` ;
  - le message ne contient jamais la valeur fautive ;
  - ne lève pas d'exception sur une ligne invalide.
- `charger_correspondance(chemin: Path) -> tuple[list[CorrespondanceSocface], list[str]]` et `charger_verifications(chemin: Path) -> tuple[list[Verification], list[str]]`, sur le même modèle.
- `lacunes(unites: Sequence[UniteInventaire]) -> list[UniteInventaire]`.
- `resume(unites: Sequence[UniteInventaire]) -> list[tuple[str, str, str, int]]` :
  - renvoie des tuples `(commune, type, disponibilite, nb_unites)`, triés ;
  - c'est la seule sortie destinée aux comptes rendus.

- [ ] **Étape 1 : écrire les tests**
  - `test_fixture_valide` : 6 unités, 0 erreur.
  - `test_absent_sans_motif_est_une_erreur` : contient `"ligne 3"` et `"motif_lacune"`.
  - `test_annee_fin_avant_debut_est_une_erreur`.
  - `test_type_inconnu_est_une_erreur` : le message ne contient pas la valeur sentinelle `"ZZSENTINELLE"`.
  - `test_recensement_sans_socface_est_une_erreur`.
  - `test_colonnes_manquantes_erreur_globale`.
  - `test_resume_ne_contient_ni_cote_ni_remarque`.
  - `test_verifications_statut_inconnu_refuse`.
  - `test_correspondance_valide`.
- [ ] **Étapes 2 à 4 :** vérifier l'échec, implémenter avec `csv.DictReader`, puis tout au vert.
- [ ] **Étape 5 :** commit `feat(etalon): inventaire, correspondance Socface et registre des vérifications`.

### Tâche 3 : schémas et lecture sûre des fiches structurées

**Valeur transcrite** (`$defs/valeur`) : elle sert **uniquement** aux champs transcrits, pas aux identifiants, rôles, rangs ni métadonnées. Elle prend l'une des formes suivantes :
- une chaîne, telle qu'écrite ;
- `{"illisible": true}` ;
- `{"illisible": "partiel", "lu": "<chaîne>"}` ;
- `{"absent": true}` : la case existe mais elle est vide dans le document.

Une colonne qui n'existe pas l'année considérée vaut `null`, ce qui signifie « non applicable ».

**Schéma `acte`** (`$id` `.../acte/1`) :
- Racine :
  - `schema_version: 1` ;
  - `kind: "acte"`, qui sert de discriminant ;
  - `commune`, `type_acte` (`naissance|mariage|deces`), `annee` (entier) ;
  - `reference` (cote, vue, rang) ;
  - `date_acte`, `date_evenement` et `lieu`, qui sont des valeurs transcrites ;
  - `personnes[]`, `liens[]`, `mentions_marginales[]` (valeurs transcrites) ;
  - `meta`, avec `lecteur`, `lecture: premiere|seconde`, `date_saisie` (chaîne ISO), `prerempli_par_modele: bool`, `source: etalon|socface|machine` et `illisible: bool`.
- Personne :
  - `rang`, un entier unique dans l'acte égal au rang de la première mention dans le texte ; c'est la **clé d'appariement**, indépendante des valeurs mesurées ;
  - `nom`, `prenoms`, `sexe`, `age`, `profession`, `domicile` et `lieu_naissance`, qui sont des valeurs transcrites ;
  - `role` ∈ {`sujet`, `pere`, `mere`, `epoux`, `epouse`, `temoin`, `declarant`, `officier`, `autre`}.
- Lien : `{de, vers, nature}`, où `de` et `vers` sont des rangs de personnes.

**Schéma `page_recensement`** (`$id` `.../page_recensement/1`) :
- Racine : `schema_version: 1`, `kind: "page_recensement"`, `commune`, `annee`, `reference` (cote, vue, page), `lignes[]` et `meta` (comme pour l'acte).
- Ligne :
  - `ligne` : entier unique dans la page, égal à la position de la ligne sur la page. C'est la clé d'appariement.
  - `menage` et `ordre` : valeurs transcrites, car elles sont mesurées et ne servent pas à l'appariement.
  - `nom`, `prenoms`, `age_ou_annee`, `lieu_naissance`, `nationalite`, `profession`, `position_menage` et `patron` : valeurs transcrites, ou `null`.

**Lecture YAML (C) :**
- `yaml.load` avec un chargeur dérivé de `SafeLoader` qui :
  - **retire la conversion implicite des dates et des horodatages**, de sorte qu'un `1872-03-05` non cité reste une chaîne ;
  - **refuse les clés dupliquées**.
- La racine doit être un mapping.
- Une erreur de lecture est signalée par `"<fichier> : yaml_invalide (ligne N)"`, sans extrait de texte.

**Erreurs de validation :** chacune est rendue par `"<fichier> : <chemin JSON> : <mot-clé du validateur>"`, par exemple `fiches/x.yaml : /personnes/2/role : enum`. **Jamais `error.message`**, qui reprend la valeur.

**Fichiers :**
- Créer : `chronologia/etalon/schemas/acte.schema.json`, `chronologia/etalon/schemas/page_recensement.schema.json` et `chronologia/etalon/fiches.py`.
- Test : `tests/etalon/test_fiches.py`.
- Fixtures : `tests/etalon/fixtures/fiches/{acte_naissance.yaml, acte_mariage.yaml, page_recensement.yaml, acte_illisible.yaml}`.

**Interfaces produites :**
- `Json = None | bool | int | float | str | list["Json"] | dict[str, "Json"]`.
- `charger_fiche(chemin: Path) -> tuple[dict[str, Json] | None, list[str]]`.
- `valider_fiche(fiche: Mapping[str, Json], nom: str) -> list[str]` :
  - choisit le schéma par `kind` ;
  - contrôle en plus l'unicité des `rang` et des `ligne`, et que chaque lien vise des rangs existants.
- `etat_valeur(v: Json) -> Literal["lisible", "partiel", "illisible", "absent", "non_applicable"]`.
- `texte_valeur(v: Json) -> str | None` : renvoie la chaîne si lisible, `lu` si partiel, `None` sinon.

- [ ] **Étape 1 : écrire les tests**
  - `test_fixtures_valides`, paramétré sur les quatre fiches.
  - `test_role_inconnu_refuse_sans_valeur` : la valeur sentinelle `"ZZSENTINELLE"`, utilisée comme rôle, n'apparaît pas dans le message.
  - `test_yaml_malforme_sans_extrait` : un fichier contenant `nom: ZZSENTINELLE: [` donne `yaml_invalide`, sans la sentinelle.
  - `test_date_non_citee_reste_chaine`.
  - `test_cle_dupliquee_refusee`.
  - `test_racine_liste_refusee`.
  - `test_rang_duplique_refuse`.
  - `test_lien_vers_rang_absent_refuse`.
  - `test_etat_valeur` : couvre les cinq états.
- [ ] **Étapes 2 à 4 :** vérifier l'échec, implémenter (`Draft202012Validator`, schémas chargés par `Path(__file__).parent / "schemas"`), puis tout au vert.
- [ ] **Étape 5 :** commit `feat(etalon): schémas versionnés et lecture sûre des fiches`.

### Tâche 4 : tirage stratifié, pilote et seconde lecture

**Cadre de tirage :** fichier `cadre.csv` par commune, rempli par le chercheur depuis les tables décennales ou l'inventaire.
- Colonnes : `commune, type, annee, nb_unites, cote`.
- `type` ∈ {`naissance`, `mariage`, `deces`, `recensement`}. Un registre `nmd` de l'inventaire donne ici trois lignes.
- `nb_unites` compte les actes de l'année dans l'ordre du registre ; pour `recensement`, il compte les pages.
- Une année absente, ou un `nb_unites = 0`, est une lacune.
- Une unité tirée est désignée par `(type, annee, rang)` : c'est le *rang*-ième acte de l'année dans l'ordre du registre, ou la *rang*-ième page du dénombrement.
- Le chercheur retrouve l'unité par la cote et l'ordre du registre. Un double registre ou une numérotation interrompue n'empêche pas de compter le rang.

**Candidats de remontée :** fichier `candidats_remontee.csv`, avec les colonnes `commune, type, annee, rang, cote`. L'année doit être < `periode[0]`.

**Règles (C, à appliquer telles quelles) :**
- **Période et tranches :** ce sont des paramètres du plan de tirage. On découpe la période en tranches de `largeur_tranche` ans à partir de `periode[0]`. Pour le projet : `(1872, 1911)` et une largeur de 10, ce qui donne 1872-1881, 1882-1891, 1892-1901 et 1902-1911. Une strate est un couple `(type, tranche)`.
- **Pilote (révisé après relecture) :** l'état civil et le recensement ont chacun leur pilote, afin de ne perdre aucun dénombrement.
  - *Pilote d'état civil :* une année tirée uniformément parmi celles de la période qui ont au moins un acte. Tous ses actes sont exclus du tirage d'état civil.
  - *Pilote de recensement :* une page tirée uniformément parmi toutes les pages de recensement. **Seule cette page** est exclue du tirage de son dénombrement, qui garde donc ses `pages_par_denombrement` pages.
- **Répartition des actes**, entièrement déterministe :
  1. Réserver 1 acte pour chaque strate non vide.
  2. Si `n_actes` est inférieur au nombre de strates non vides, lever `ValueError("strates_trop_nombreuses")`.
  3. Si `n_actes` dépasse le nombre total d'actes tirables, lever `ValueError("population_insuffisante")`.
  4. Répartir le solde proportionnellement aux effectifs, selon la méthode du plus fort reste.
  5. Plafonner chaque strate à son effectif, puis redistribuer l'excédent par le même procédé.
  6. Départager les égalités de reste dans l'ordre croissant des strates `(type, tranche)`.
  - Une répartition fixée par le chercheur (`repartition`) remplace ce calcul (§8.7). Elle doit totaliser `n_actes`, ne viser que des strates non vides, et rester comprise entre 0 et l'effectif de chaque strate. Sinon, `ValueError` avec un code.
- **Dans une strate :** tirer uniformément, sans remise, des couples `(annee, rang)` parmi toutes les unités de la strate.
- **Recensements :** tirer `pages_par_denombrement` pages par année de recensement présente, sans remise.
- **Remontée :** tirer `n_remontee` candidats uniformément, sans remise.
- **Générateur :** `random.Random(graine)`. L'ordre de parcours est fixe : pilote d'état civil, pilote de recensement, strates triées, recensements par année, remontée.
- **Seconde lecture :** l'échantillon a son propre générateur, `random.Random(graine_seconde)`. On tire `ceil(0,10 × nombre d'actes de l'étalon, remontée comprise)` actes. Pour Hesdin, 110 actes donnent 11 ; pour Lanchères, 45 donnent 5.
- **La graine se fixe avant tout tirage, et ne change plus.** Le tirage à blanc qui fait connaître le pilote utilise la graine définitive. Choisir une graine après avoir vu un tirage est interdit ; cette règle figure dans le mode opératoire (tâche 8).

**Fichiers :**
- Créer : `chronologia/etalon/tirage.py`.
- Test : `tests/etalon/test_tirage.py`.
- Fixture : `tests/etalon/fixtures/cadre_synthetique.csv` (Villefictive, 1872-1911, 1890 absente, mariages à 0 en 1905, une strate à 1 acte) et `candidats_synthetique.csv`.

**Interfaces produites :**
- `Strate = tuple[str, str]`.
- `tranches(periode: tuple[int, int], largeur: int) -> list[tuple[int, int]]`.
- `tranche_de(annee: int, periode: tuple[int, int], largeur: int) -> str` : renvoie `"1872-1881"` ; pour une année antérieure à `periode[0]`, renvoie `"avant-1872"` ; lève `ValueError` après `periode[1]`.
- `@dataclass(frozen=True) class PlanTirage` :
  - `commune: str`, `n_actes: int`, `pages_par_denombrement: int`, `n_remontee: int` ;
  - `periode: tuple[int, int] = (1872, 1911)`, `largeur_tranche: int = 10` ;
  - `repartition: Mapping[Strate, int] | None = None`.
- `@dataclass(frozen=True) class Tire` : `commune`, `categorie` (`acte|recensement|remontee|pilote_acte|pilote_recensement`), `type`, `annee: int`, `rang: int`, `cote: str`.
- `@dataclass(frozen=True) class Tirage` :
  - `tires: list[Tire]` ;
  - `annee_pilote: int`, `page_pilote: tuple[int, int]` (année, rang) ;
  - `graine: int` ;
  - `empreintes: dict[str, str]` : sha256 du cadre, des candidats et de la répartition, ainsi que des paramètres du plan sérialisés en JSON trié ;
  - `strates_vides: list[Strate]`, `annees_absentes: list[int]` ;
  - `version: str = "1"`.
- `charger_cadre(chemin: Path) -> tuple[list[LigneCadre], list[str]]`.
- `repartir(effectifs: Mapping[Strate, int], n: int) -> dict[Strate, int]`.
- `tirer(cadre: Path, candidats_remontee: Path | None, plan: PlanTirage, graine: int) -> Tirage`.
- `tirer_seconde_lecture(t: Tirage, graine_seconde: int, proportion: float = 0.10) -> list[Tire]`.
- `ecrire_tirage(t: Tirage, dossier: Path) -> None` :
  - écrit `tirage.csv`, déterministe, trié ;
  - écrit `tirage.meta.json` : tout sauf `tires`, plus `date` ;
  - passe chaque chemin écrit par `verifier_hors_depot`.

- [ ] **Étape 1 : écrire les tests**
  - `test_repartir_proportionnel` : `{A:60, B:30, C:10}` avec `n=10` donne `{A:6, B:3, C:1}`.
  - `test_repartir_minimum_un` : `{A:1, B:1, C:98}` avec `n=10` donne `{A:1, B:1, C:8}`.
  - `test_repartir_plafond_redistribue` : `{A:2, B:100}` avec `n=50` donne `{A:2, B:48}`.
  - `test_repartir_egalite_departagee_par_ordre` : `{A:5, B:5}` avec `n=3` donne `{A:2, B:1}`.
  - `test_repartir_strates_trop_nombreuses`.
  - `test_repartir_population_insuffisante`.
  - `test_repartition_imposee_invalide_refusee` : un total faux, une strate vide, ou une demande au-delà de l'effectif.
  - `test_meme_graine_meme_csv` : comparaison octet par octet.
  - `test_graine_differente_tirage_different`.
  - `test_empreintes_changent_avec_chaque_entree` : chacune réagit à son entrée (cadre, candidats, répartition, paramètres).
  - `test_annee_pilote_exclue_des_actes`.
  - `test_page_pilote_exclue_mais_denombrement_complet` : chaque année de recensement garde `pages_par_denombrement` pages, et aucune n'est la page pilote.
  - `test_lacunes_declarees`.
  - `test_effectifs_du_plan`.
  - `test_pas_de_doublon`.
  - `test_remontee_candidat_apres_periode_refuse`.
  - `test_seconde_lecture_plafond_superieur` : 45 actes donnent 5, 110 donnent 11 ; c'est un sous-ensemble des actes et remontées, jamais un pilote.
  - `test_ecrire_tirage_refuse_le_depot`.
- [ ] **Étapes 2 à 4 :** vérifier l'échec, implémenter, puis tout au vert.
- [ ] **Étape 5 :** commit `feat(etalon): tirage stratifié rejouable, pilotes et seconde lecture`.

### Tâche 5 : mesures sur le texte (CER, WER)

**Règles :**
- Avant mesure : appliquer NFC, puis remplacer toute suite d'espaces par une seule espace. Aucune autre transformation : la casse et la ponctuation sont conservées.
- Calcul : `jiwer.process_characters` et `jiwer.process_words`, avec des transformations passées explicitement, l'identité après notre normalisation.
- On **conserve les éditions et les longueurs de référence**. L'agrégat est une micro-moyenne : somme des éditions divisée par somme des longueurs.
- Une référence vide n'entre dans aucun taux ; elle est comptée dans `references_vides`. Un taux à dénominateur nul vaut `None`.
- Une unité dont la fiche de l'étalon porte `meta.illisible: true` est comptée dans `illisibles` et exclue des taux.
- **Lecture des résultats :** le rapport précise que ces taux décrivent l'échantillon tiré. Ce ne sont pas des taux du corpus redressés par les poids du tirage (une phrase fixe dans le CSV d'en-tête de la tâche 7).

**Fichiers :**
- Créer : `chronologia/etalon/mesures_texte.py`.
- Test : `tests/etalon/test_mesures_texte.py`.

**Interfaces produites :**
- `normaliser_espaces(s: str) -> str` : NFC et repli des espaces. Elle est partagée avec la tâche 6.
- `@dataclass(frozen=True) class PaireTexte` : `commune`, `source` (`machine|socface|seconde_lecture`), `type`, `annee: int`, `reference: str`, `hypothese: str`, `illisible: bool`.
- `@dataclass(frozen=True) class LigneMesureTexte` :
  - `commune`, `source`, `type`, `tranche` ;
  - `n_unites` ;
  - `editions_car`, `longueur_car`, `editions_mots`, `longueur_mots` ;
  - `cer: float | None`, `wer: float | None` ;
  - `references_vides`, `illisibles`.
- `mesurer_textes(paires: Sequence[PaireTexte], periode: tuple[int, int], largeur: int) -> list[LigneMesureTexte]` :
  - une ligne par `(commune, source, type, tranche)` ;
  - plus une ligne `type="*"`, `tranche="*"` par `(commune, source)` ;
  - aucune ligne ne mélange deux communes.

- [ ] **Étape 1 : écrire les tests**
  - `test_identique_zero`.
  - `test_abreviation_est_une_erreur`.
  - `test_nfc_seulement`.
  - `test_casse_comptee`.
  - `test_micro_moyenne` : le résultat vaut `20/110`.
  - `test_reference_vide_comptee_a_part`.
  - `test_illisible_exclu_et_compte`.
  - `test_communes_jamais_cumulees` : deux communes donnent deux lignes `*`, et aucune ligne ne les fusionne.
  - `test_remontee_dans_tranche_avant`.
  - `test_aucun_texte_dans_le_resultat`.
- [ ] **Étapes 2 à 4 :** vérifier l'échec, implémenter, puis tout au vert.
- [ ] **Étape 5 :** commit `feat(etalon): mesure CER et WER par commune, source, type et tranche`.

### Tâche 6 : comparaison des fiches (champs, rôles, détection, accord)

Une seule fonction de comparaison sert trois usages : la machine contre l'étalon, Socface contre l'étalon, et la seconde lecture contre la première.

**Appariement (révisé après relecture, C) :**
- L'appariement ne dépend **d'aucune valeur mesurée**.
- Pour un acte, on apparie les personnes par `rang` (rang de première mention) ; pour une page, on apparie les lignes par `ligne` (position sur la page).
- L'appariement est injectif par construction, car ces clés sont uniques (tâche 3).

**Décompte d'un champ de l'étalon contre l'autre côté :**

| Étalon \ autre | lisible, même texte | lisible, texte différent | absent de l'autre côté (personne ou ligne non appariée, champ manquant) |
|---|---|---|---|
| lisible | vp | fp + fn | fn |
| partiel | compté dans `partiels`, hors vp, fp et fn | idem | idem |
| illisible | compté dans `illisibles`, hors vp, fp et fn | idem | idem |
| `absent` (case vide) | fp si l'autre côté donne un texte, sinon rien | | rien |
| `null` (non applicable) | rien | | rien |

- Une personne ou une ligne présente **seulement de l'autre côté** compte un fp pour chacun de ses champs lisibles.
- Une personne ou une ligne de l'étalon non appariée compte un fn pour chacun de ses champs lisibles. Ainsi, aucune omission ne peut améliorer les scores.
- Le texte est comparé par `normaliser_espaces` (tâche 5).

**Rôles et détection :** on compte séparément :
- `roles_corrects` et `personnes_appariees` ;
- `personnes_manquantes` : dans l'étalon seulement ;
- `personnes_en_trop` : de l'autre côté seulement.

**Accord entre lectures (révisé après relecture) :**
- `accord_exact = concordants / (concordants + discordants)`.
- Il se calcule sur les champs **lisibles des deux côtés**.
- Les désaccords de présence (lisible d'un côté, illisible, absent ou manquant de l'autre) sont comptés à part dans `desaccords_presence`.
- Il est symétrique : échanger les deux lectures donne le même résultat.

**Fichiers :**
- Créer : `chronologia/etalon/comparaison.py`.
- Test : `tests/etalon/test_comparaison.py`, qui réutilise les fixtures de la tâche 3 et en construit des variantes dans les tests.

**Interfaces produites :**
- `@dataclass class CompteChamp` :
  - compteurs `vp`, `fp`, `fn`, `partiels`, `illisibles` ;
  - propriétés `precision` et `rappel`, qui valent `None` si le dénominateur est nul.
- `@dataclass class Comparaison` :
  - `commune: str`, `source: str` ;
  - `champs: dict[str, CompteChamp]`, avec des clés comme `"personne.nom"`, `"ligne.profession"` ou `"date_acte"` ;
  - `roles_corrects`, `personnes_appariees`, `personnes_manquantes`, `personnes_en_trop` ;
  - `unites: int`.
- `@dataclass class Accord` : `concordants: dict[str, int]`, `discordants: dict[str, int]`, `desaccords_presence: dict[str, int]`, et la propriété `accord_exact(champ) -> float | None`.
- `comparer_fiches(etalon: Mapping[str, Json], autre: Mapping[str, Json]) -> Comparaison`.
- `comparer_lectures(premiere: Mapping[str, Json], seconde: Mapping[str, Json]) -> Accord`.
- `cumuler(comparaisons: Iterable[Comparaison]) -> Comparaison` : lève `ValueError("communes_ou_sources_melangees")` si les `commune` ou les `source` diffèrent.

- [ ] **Étape 1 : écrire les tests**
  - `test_fiche_identique_tout_vrai_positif`.
  - `test_profession_differente_fp_et_fn`.
  - `test_illisible_et_partiel_comptes_a_part`.
  - `test_case_vide_remplie_par_machine_est_fp`.
  - `test_non_applicable_ignore`.
  - `test_role_inverse_pere_temoin` : on attend `appariees == 2` et `roles_corrects == 0`.
  - `test_personne_omise_donne_fn_sur_tous_ses_champs`.
  - `test_personne_en_trop_donne_fp`.
  - `test_ligne_appariee_par_position_meme_si_menage_faux` : le champ `ligne.menage` compte fp + fn.
  - `test_accord_symetrique`.
  - `test_accord_une_concordance_une_discordance_vaut_un_demi`.
  - `test_cumuler_refuse_deux_communes`.
- [ ] **Étapes 2 à 4 :** vérifier l'échec, implémenter, puis tout au vert.
- [ ] **Étape 5 :** commit `feat(etalon): comparaison par position, détection, rôles et accord entre lectures`.

### Tâche 7 : sous-commandes CLI et rapport d'agrégats

**Fichiers :**
- Modifier `chronologia/cli.py` :
  - ajouter trois sous-parseurs dans `_parseur()`, au style de `_importer` et `_erreur` ;
  - mettre à jour la docstring du module.
- Créer : `chronologia/etalon/rapport.py`.
- Test : `tests/etalon/test_cli_etalon.py`.

**Sous-commandes :**

**`etalon-inventaire --donnees <dossier commune>`**
- Valide `inventaire.csv`, plus `correspondance_socface.csv` et `verifications.csv` s'ils existent.
- Affiche les erreurs sur stderr et rend le code 2 s'il y en a.
- Sinon, affiche `resume()`, le nombre de lacunes et l'état des vérifications par statut.

**`etalon-tirer`**
- Arguments : `--cadre <csv> [--remontee <csv>] --commune X --actes N --pages-par-denombrement 2 --remontee-n M --graine G --graine-seconde H [--repartition <csv type,tranche,n>] [--periode 1872 1911] [--largeur-tranche 10] --sortie <dossier>`.
- Écrit `tirage.csv`, `tirage.meta.json` et `seconde_lecture.csv`.
- Affiche les effectifs par catégorie, l'année pilote, la page pilote, les strates vides et les années absentes.
- **Les graines sont obligatoires** ; aucune ne vient de l'horloge.

**`etalon-mesurer`**
- Arguments : `--etalon <dossier fiches> --autre <dossier fiches> --source machine|socface|seconde_lecture [--textes-etalon <dossier .txt>] [--textes-autre <dossier .txt>] --sortie <dossier>`.
- Valide toutes les fiches. Une fiche invalide fait **échouer la mesure** (code 2), avec les messages de la tâche 3.
- Apparie les fichiers par nom. Une fiche de l'étalon sans pendant compte en fn pour tous ses champs lisibles (règle de la tâche 6), une fiche en trop compte en fp. Le nombre de fichiers sans pendant est affiché.
- Les textes sont appariés par nom, et leurs métadonnées (commune, type, année, illisible) viennent de la fiche de l'étalon du même nom.
- Avec `--source seconde_lecture`, produit `accord.csv` au lieu de précision et rappel.
- Écrit `mesures_champs.csv`, `mesures_roles.csv` et, le cas échéant, `mesures_texte.csv`.
- Chaque CSV est séparé par commune et par source et commence par une ligne de commentaire fixe : `# taux sur l'échantillon tiré, non redressés ; voir tirage.meta.json`.

**Pour les trois sous-commandes :**
- Chaque chemin lu ou écrit passe par `verifier_hors_depot`. Sinon, code 2 et `erreur : données dans le dépôt`.
- Toute exception de lecture est interceptée et rendue sans valeur.

**Interfaces produites (`rapport.py`) :**
- `ecrire_mesures_champs(c: Comparaison, chemin: Path) -> None`.
- `ecrire_accord(a: Accord, commune: str, chemin: Path) -> None`.
- `ecrire_mesures_texte(lignes: Sequence[LigneMesureTexte], chemin: Path) -> None`.

- [ ] **Étape 1 : écrire les tests**
  - Comme dans `tests/test_cli.py`, avec `main([...])` et `capsys` ; `racine_depot` est remplacée par `monkeypatch` vers `tmp_path/"depot"`.
  - `test_inventaire_ok_code_0`.
  - `test_inventaire_absent_sans_motif_code_2`.
  - `test_tirer_ecrit_les_trois_fichiers`.
  - `test_tirer_sans_graine_refuse` : on attend `SystemExit`.
  - `test_mesurer_fichier_sans_pendant_compte_en_fn`.
  - `test_mesurer_fiche_invalide_code_2_sans_valeur` : la sentinelle n'apparaît ni dans `out`, ni dans `err`, ni dans les fichiers de `--sortie`.
  - `test_mesurer_seconde_lecture_produit_accord`.
  - `test_sortie_sans_donnee_nominative` : aucun nom des fixtures n'apparaît dans `out`, `err` ni dans les CSV.
  - `test_chaque_sous_commande_refuse_le_depot`, paramétré sur les trois sous-commandes.
  - `test_sortie_existante_lien_vers_depot_refusee`.
- [ ] **Étapes 2 à 4 :** vérifier l'échec, implémenter, puis tout au vert.
- [ ] **Étape 5 :** commit `feat(cli): sous-commandes etalon-inventaire, etalon-tirer et etalon-mesurer`.

### Tâche 8 : conventions de transcription (projet) et documentation

Les conventions s'écrivent **avant** le pilote (§8.3).

**Fichiers :**

**`docs/projet-hesdin/conventions-transcription.md`**
- C'est une **proposition à valider par le chercheur** (D) : une page, valable pour les deux terrains.
- Abréviations : conservées telles qu'écrites, jamais développées.
- Ponctuation et majuscules : telles qu'écrites.
- Mots barrés : `[barré: …]`.
- Ajouts interlinéaires et marginaux : `[ajout: …]`. Les mentions marginales vont aussi dans `mentions_marginales`.
- Chiffres en lettres : conservés.
- Lettres incertaines : `[?]`.
- Passages illisibles : `[illisible]`.
- La page donne la correspondance avec les états des fiches : lisible, partiel, illisible, absent, non applicable.
- Le rang de première mention se définit dans l'ordre du texte, marge exclue.

**`docs/projet-hesdin/mode-operatoire.md`**
- L'ordre des commandes.
- L'arborescence hors du dépôt : `<donnees>/<commune>/{inventaire.csv, correspondance_socface.csv, verifications.csv, cadre.csv, candidats_remontee.csv, tirage/, escriptorium/, fiches/{etalon,seconde_lecture,socface,machine}/, textes/…, mesures/}`.
- La règle des graines : **fixées et notées avant tout tirage, jamais choisies après coup**.
- Le délai de trois semaines entre les deux lectures, vérifié par `meta.date_saisie`.

**`AGENTS.md`**
- Une ligne sur les commandes `etalon-*` et le garde-fou des données hors du dépôt.

- [ ] **Étape 1 :** rédiger les trois fichiers.
- [ ] **Étape 2 :** vérifier qu'aucun nom réel n'y figure ; pytest et mypy restent au vert.
- [ ] **Étape 3 :** commit `docs(projet-hesdin): conventions de transcription (à valider) et mode opératoire`.

---

## Travail hors code (chercheur, avec l'aide de la machine), dans l'ordre

Le plan n'exécute pas ce travail. Il est listé pour que le chantier se termine selon les critères de §8.6.

1. **Inventaire.** Remplir les fichiers des quatre communes et les valider avec `etalon-inventaire`. L'inventaire des AD80 est déjà relevé (§4.2) ; celui des AD62 se fera après leur maintenance.
2. **Vérifications de §8.2**, tenues dans `verifications.csv` :
   1. AD62 après 1882 ;
   2. Socface : licence et export ;
   3. **mairies de Lanchères et de Saint-Valery** : registres absents des AD80 et doubles des listes nominatives de 1876 à 1901. La machine rédige les brouillons de courrier, le chercheur les envoie ;
   4. conditions de stockage des images, aux AD62 et aux AD80.
3. **Décisions du chercheur** au vu de l'inventaire : profondeur de la remontée, périmètre des échantillons de Saint-Omer et de Saint-Valery.
4. **Cadres de tirage** depuis les tables décennales ; validation des **conventions** (tâche 8) ; **graines fixées et notées**.
5. **eScriptorium** en local (Docker), avec un projet par commune.
6. **Pilote.** Un tirage à blanc avec la graine définitive fait connaître l'année pilote et la page pilote. Le pilote mesure le temps par unité. On fixe ensuite, si besoin, la répartition (`--repartition`) **avant** le vrai tirage, qui garde la même graine.
7. **Tirage définitif, transcription et annotation.** Environ 17 heures sur environ neuf semaines, avec un plafond de quatre mois. Aucun acte tiré n'est retiré.
8. **Seconde lecture.** L'échantillon vient de `seconde_lecture.csv`, et la lecture a lieu au moins trois semaines après la première. Puis `etalon-mesurer --source seconde_lecture`.
9. **Socface.** Relever les lignes des pages tirées, dans l'ordre de la page, en fiches `socface`. Puis `etalon-mesurer --source socface` pour chaque terrain. C'est le premier résultat chiffré du projet.
