# Trois logiciels voisins : nodegoat, Arches, ResearchSpace

*Étude du 9 novembre 2026, faite à partir du code source de chaque logiciel (clones du jour). Elle complète `docs/etude-heurist.md`. Les numéros de règles, de décisions et de sections renvoient à `docs/modele-evenement-masque-factoide.md` (v0.9.4).*

Les trois logiciels sont sous **AGPL‑3**. Comme pour Heurist, on reprend des idées, jamais du code. La seule exception possible est la bibliothèque Python `edtf`, une dépendance d'Arches et non du code d'Arches ; sa licence reste à vérifier.

## 0. En une page

| | nodegoat | Arches | ResearchSpace |
|---|---|---|---|
| Éditeur | LAB1100 (Pays‑Bas), depuis 2011 | Getty Conservation Institute et World Monuments Fund | British Museum, puis communauté |
| Pile | PHP sur le cadre 1100CC, MySQL | Python, Django 6.1, PostgreSQL et PostGIS, Elasticsearch | Java 11, triple store Blazegraph, interface React |
| Dernier commit | 29 juin 2026 (version 8.6) | 9 novembre 2026 (8.2.0a25) | 25 août 2026 |
| Domaine | Données historiques, réseaux et analyse diachronique | Inventaire du patrimoine, données géographiques | Données liées CIDOC‑CRM, argumentation |
| Proche de Chronologia par | ses **dates relatives** et sa **mémoire des correspondances** | sa **pile** et sa **validation des modifications** | son **modèle d'argumentation** (CRMinf) |

**Ce qu'il faut retenir**
1. Le modèle de Chronologia sort renforcé : la CONTRAINTE_TEMPORELLE à quatre bornes (nodegoat), la CONCLUSION calquée sur CRMinf (ResearchSpace) et la séparation entre la proposition et sa validation (Arches) existent ailleurs, en production.
2. Trois manques apparaissent :
   - l'**écart** dans une contrainte relative (« au plus trois jours après la naissance ») ;
   - la **nature d'un argument** : observation de la source, adoption d'une opinion publiée ou inférence ;
   - les **conclusions qui reposent sur d'autres conclusions**.
3. Côté import, Arches confirme R9 (annuler un lot entier) et apporte une **table des anomalies** consultable.
4. Pour l'étape « Lieux », la **mémoire des formes écrites** de nodegoat est l'idée la plus directement utile.

Les propositions sont regroupées au §4. Aucune n'est encore consignée dans le document de référence.

---

## 1. nodegoat

### 1.1 Principe

L'utilisateur décrit son modèle dans l'interface, comme dans Heurist. Chaque **objet** (une personne, une ville) porte des **descriptions** (ses champs) et des **sous‑objets**. Un sous‑objet est un fait daté et localisé : une résidence, un voyage, une fonction. C'est la pièce centrale : nodegoat pense « objet + suite de faits datés et situés », ce qui le rapproche de notre couple PERSONNE + EVENEMENT, plus que Heurist.

### 1.2 Les dates : une chronologie à quatre points, relative si besoin

Tables `data_type_object_sub_date_chronology` et `cache_type_object_sub_date` (`setup/nodegoat_content.sql`), code dans `FormatTypeObjectsBase::formatToSQLChronology` et `StoreType::getTimeDirections`.

- Une date n'est pas un point mais **quatre bornes** : début au plus tôt, début au plus tard, fin au plus tôt, fin au plus tard (`DATE_START_START`, `DATE_START_END`, `DATE_END_START`, `DATE_END_END`). C'est exactement le champ `borne` de notre CONTRAINTE_TEMPORELLE.
- Chaque borne est un **énoncé** :
  - soit une date fixe (`date_value`) ;
  - soit une **référence à un autre sous‑objet** (`date_object_sub_id`), avec une **direction** (après le début, avant le début, après la fin, avant la fin) et un **écart** (`offset_amount` et `offset_unit` : jours, mois, années) ;
  - éventuellement un **cycle** (`cycle_object_id`), c'est‑à‑dire une date récurrente définie comme un objet. Le code ne dit pas clairement si cela sert aux fêtes mobiles ; à vérifier dans la documentation.
- Les bornes sont **calculées puis mises en cache** (`cache_type_object_sub_date`), avec le **chemin de dépendance** (`cache_type_object_sub_date_path`). Quand la date de référence change, nodegoat sait quelles dates recalculer.
- Une durée peut aussi être donnée (`span_period_amount`, `span_period_unit`).

**Ce que Chronologia a déjà** : les quatre bornes et la référence à un autre événement (`evenement_reference_id`).
**Ce qui manque** : la direction et surtout l'**écart**. On ne peut pas écrire aujourd'hui « baptême au plus trois jours après la naissance » ni « décès au moins neuf mois avant la naissance posthume », deux raisonnements très courants en généalogie. Il manque aussi un mécanisme de **recalcul** quand l'événement de référence bouge.

### 1.3 Les lieux hérités

Un sous‑objet peut avoir sa propre géométrie ou **renvoyer à un autre objet** (`location_ref_object_id`), une ville par exemple, dont il hérite la position. C'est notre MENTION_LIEU → LIEU_HISTORIQUE, mais sans identification révisable : le lien est direct.

### 1.4 Sources, versions et relecture

- **Citation par valeur** : chaque valeur et chaque sous‑objet peut citer un ou plusieurs objets « source », avec une précision libre, une page par exemple (`data_type_object_sub_definition_sources.value`). C'est plus fin que Heurist, moins que notre factoïde, qui fait de la source le point de départ.
- **Versions** : chaque valeur est versionnée avec l'auteur et la date (`data_type_object_definition_version`).
- **Relecture** : une colonne `date_audited` reste vide tant qu'un responsable n'a pas relu la modification. Les modifications non relues sont repérables (`StoreTypeObjects.php`, `date_audited IS NULL`). C'est la même idée que notre R18, mais au niveau de chaque saisie humaine, pas seulement des propositions des agents.
- **Discussion** par objet (`data_type_object_discussion`) : un fil de commentaires attaché à la fiche.

### 1.5 Le rapprochement et sa mémoire

`ReconcileTypeObjectsValues.php` rapproche des valeurs textuelles (par exemple des noms de lieux dans un import) des objets existants, avec des seuils de score et de distance. `StorePatternsTypeObjectPair.php` **retient les décisions** : une forme écrite (`identifier`) est associée à un objet, ou marquée « sans référence » (`no-reference`) ou « à ignorer » (`ignore`). La fois suivante, la même forme est résolue d'emblée.

**Pour Chronologia** : c'est l'outil qu'il faudra à l'étape « Lieux ». Une forme écrite déjà rattachée (« St Aubin des Bois » → LIEU_HISTORIQUE n°12) est **proposée** à l'identique pour une nouvelle mention, en « proposé » seulement (R18). Les marques « sans référence » et « à ignorer » évitent de reposer sans cesse la même question, dans l'esprit de R27.

### 1.6 Analyse et ergonomie

- Visualisations **géographique, sociale et temporelle** liées entre elles, avec des « conditions » qui pondèrent ou colorent les éléments, et des scénarios enregistrés.
- Import depuis des **sources de données liées** (`IngestTypeObjectsResourceExternal.php`), Wikidata par exemple, pour enrichir des objets.
- Défaut partagé avec Heurist : l'utilisateur doit d'abord **concevoir son modèle**, ce qui demande une vraie formation. Chronologia, à modèle fixe, n'a pas ce coût.

---

## 2. Arches

### 2.1 Principe

Une **ressource** suit un **modèle en graphe** (`GraphModel`, `Node`, `Edge`) aligné sur une ontologie, CIDOC‑CRM en général. Les valeurs sont rangées par groupes de nœuds dans des **tuiles** (`TileModel.data`, en JSONB). L'interface se construit à partir de **fiches** (`CardModel`) et de **widgets**.

**À ne pas reprendre** : les tuiles en JSONB rendent le modèle très souple, mais renvoient les contraintes dans le code applicatif. Notre schéma relationnel fixe, gardé par des triggers (R10, R11, R18), est plus sûr pour un modèle qui ne doit pas dériver.

### 2.2 Les modifications provisoires

Une tuile porte, à côté de ses valeurs, un champ `provisionaledits` (`models.py`, docstring de `TileModel`) : pour chaque utilisateur sans droit de validation, sa **valeur proposée**, son **action** (créer, modifier, supprimer), son **statut** (« review », « approved », « rejected »), le **relecteur** et les **dates**. Le journal `edit_log` garde l'auteur de la proposition et celui de la décision (`provisional_userid`, `userid`).

**Pour Chronologia** : c'est R18 appliquée aux saisies humaines. Notre modèle est plus solide (une proposition est une ligne immuable, son statut est un journal, R25), mais Arches montre ce dont l'**écran de validation** aura besoin :
- un filtre « en attente de relecture » dans la recherche ;
- des notifications au relecteur (`Notification`, `UserXNotification`) ;
- l'affichage côte à côte de la valeur en place et de la valeur proposée.

### 2.3 Les états du cycle de vie

Une ressource suit un **cycle de vie** configurable (`ResourceInstanceLifecycle`, migration `11042`) : par défaut brouillon → actif → retiré. Chaque état dit si la ressource peut être modifiée ou supprimée.

**Pour Chronologia** : utile pour la **publication** (connecteurs Heurist, décision 24, et future publication RDF). Une PERSONNE ou un EVENEMENT pourrait être « en cours », « publiable » ou « publié ». À ne pas confondre avec le statut d'une identification (proposé, actif, rejeté), qui reste l'affaire de R11 et R18.

### 2.4 L'import en zone d'attente

Tables `load_event`, `load_staging` et `load_errors`, modules dans `arches/app/etl_modules/` :
- les lignes à importer passent d'abord en **zone d'attente**, avec un indicateur `passes_validation` ;
- chaque erreur est rangée dans une **table d'erreurs** avec la valeur, la source, le champ et le message ;
- un import entier peut être **annulé** (`reverse_load`).

**Pour Chronologia** : nous avons le lot (LOT_IMPORT), l'empreinte, l'idempotence et le différentiel. L'annulation d'un lot entier est déjà prévue par **R9** (statut « annulé ») ; Arches confirme qu'elle est indispensable en pratique, et il reste à l'exposer en commande. Ce qui manque vraiment, c'est une **table des anomalies** de l'import, consultable au lieu d'un simple rapport d'exécution : forme de date non reconnue, lieu illisible, ligne ignorée.

### 2.5 Les dates EDTF

Le type `EDTFDataType` (`datatypes.py`) s'appuie sur la bibliothèque Python **`edtf`** (version 4.0.1). `ExtendedDateFormat` (`utils/date_utils.py`) en tire quatre bornes : `lower`, `upper`, `lower_fuzzy`, `upper_fuzzy`, avec une marge réglable pour les dates floues.

**Pour Chronologia** : EDTF (norme de la Library of Congress, intégrée à ISO 8601‑2) écrit simplement ce que nos historiens écrivent à la main :
- `1709?` : incertain ;
- `1709~` : approximatif ;
- `[1708..1710]` : une des années ;
- `17XX` : siècle connu, années non.

Cela donnerait une **syntaxe de saisie** et un **format d'export** pour `date_min` et `date_max`. Deux limites :
- EDTF est **grégorien seulement** : le champ `calendrier` et `date_brute` restent indispensables ;
- `?` et `~` ne recouvrent pas nos modes de détermination (décision 23) : « estimée » est proche de `~`, mais « déduite » n'a pas d'équivalent.

### 2.6 Le reste

- **Libellés multilingues** (`I18n_TextField`) et **thésaurus SKOS** pour les vocabulaires : un modèle pour nos référentiels TYPE_EVENEMENT et ROLE.
- **IIIF** : manifestes et annotations d'images (`IIIFManifest`, `VwAnnotation`). À regarder pour la question des outils d'annotation (§9.2‑8).
- **Couches cartographiques** dans PostGIS (`MapLayer`, `SpatialView`) : une référence pour notre écran de carte (MapLibre GL).

---

## 3. ResearchSpace

### 3.1 Principe

Les données sont des **graphes RDF** en CIDOC‑CRM, rangés dans un triple store (Blazegraph). Les formulaires sont décrits par des **champs**, chacun défini par des requêtes SPARQL. La partie qui nous intéresse est le module **arguments** (`src/main/web/components/arguments/`, environ 4 300 lignes de TypeScript), bâti sur **CRMinf**.

**À ne pas reprendre** : la pile. Blazegraph n'est plus maintenu depuis plusieurs années et un triple store comme base principale rend les contraintes d'intégrité difficiles. Chronologia garde PostgreSQL et **publie** en RDF (§9.2‑3).

### 3.2 Assertions, croyances et arguments

Types dans `ArgumentsApi.ts`, stockage dans `AssertionsStore.ts` et `ArgumentsStore.ts` :

- Une **assertion** vise **une valeur d'un champ d'une fiche** (`targetsRecord`, `targetsField`). On ne conteste pas une fiche entière, mais une affirmation précise : « né à Rouen ».
- Chaque assertion porte des **croyances** (`AssertedBelief`), avec trois valeurs : d'accord, pas d'accord, sans opinion (`Agree`, `Disagree`, `No Opinion`). C'est la propriété CRMinf `J5 holds to be`. Une croyance peut viser **une autre valeur** que celle enregistrée (`targetValue`) ; un indicateur `isCanonical` dit si c'est la valeur en place.
- Une croyance est justifiée par un **argument** de l'un des trois types suivants :
  - **observation** (`Observation`) : examen direct, avec un lieu et une date ;
  - **adoption d'une croyance** (`BeliefAdoption`) : on fait sienne l'opinion d'un autre, d'une publication par exemple ;
  - **inférence** (`Inference`) : un type de raisonnement (`logicType`) et des **prémisses**, qui sont elles‑mêmes des croyances, et qui mènent à des **conclusions**.

### 3.3 Ce que cela apporte à Chronologia

Notre CONCLUSION est déjà proche : `valeur` (vrai, faux, incertain) correspond aux trois croyances, `argument` au texte, `factoides[]` aux observations, `cible` à l'assertion. Trois écarts :

1. **La nature de l'argument n'est pas dite.** « Je l'ai lu dans l'acte », « je reprends l'avis de l'abbé Dupont (1902) » et « je le déduis de l'âge au décès » sont trois choses différentes pour l'historien et pour la publication CRMinf. Les `motifs[]` décrivent le *pourquoi*, pas le *type* de raisonnement.
2. **Une conclusion ne peut pas s'appuyer sur une autre conclusion.** Ses appuis sont des factoïdes. Or un raisonnement prosopographique s'enchaîne : « ces deux masques sont la même personne », donc « son père est Jean », donc « la famille vient de tel village ». Si la première conclusion est retirée, les suivantes doivent être **signalées** (R24), sans être retirées en silence.
3. **L'adoption d'une opinion publiée** suppose de pouvoir citer un auteur publié. Or CONTRIBUTEUR n'est aujourd'hui qu'un « chercheur ou processus automatique » (§4.4, types humain, agent, import). Il faudrait soit un type « auteur publié », soit traiter la publication comme une SOURCE dont le passage est cité.

Le premier et le deuxième point préparent directement la correspondance CRMinf de la publication RDF (§9.2‑3) : I1 Argumentation, I2 Belief, I5 Inference Making, I7 Belief Adoption.

### 3.4 Ergonomie

L'assertion se fait **en place** : depuis la valeur affichée, un clic ouvre « contester ou appuyer cette valeur ». C'est la bonne réponse à la leçon 5 de l'étude Heurist (« comparer plutôt que lister ») et un modèle pour l'écran de validation.

---

## 4. Propositions

À trancher, comme pour le §9 de l'étude Heurist. Rien n'est consigné.

| n° | Proposition | Inspirée de | Ce qui change dans le modèle | Quand |
|---|---|---|---|---|
| 1 | **Écart et direction dans la contrainte temporelle.** Une borne relative dit « avant ou après le début ou la fin » de l'événement de référence, avec un écart minimal et maximal (en jours, mois ou années). Les bornes calculées sont recalculées quand la référence change ; une dépendance circulaire est refusée et signalée. | nodegoat | Colonnes de CONTRAINTE_TEMPORELLE (§4.4), sans nouvelle règle | Socle PostgreSQL |
| 2 | **Nature de l'argument.** CONCLUSION reçoit un `mode` : observation, adoption ou inférence. | ResearchSpace, CRMinf | Colonne de CONCLUSION, correspondance du §4.7 | Socle PostgreSQL |
| 3 | **Conclusions enchaînées.** Une conclusion peut avoir d'autres conclusions pour prémisses. Quand une prémisse est retirée, les conclusions qui en dépendent sont signalées dans la file de décisions, pas retirées. Les cycles sont interdits. | ResearchSpace, CRMinf | Nouvelle table de prémisses, et sans doute **R28** | Socle PostgreSQL |
| 4 | **Table des anomalies d'import.** Chaque lot garde ses anomalies (valeur, ligne, message), consultables et liées à la file de décisions (R24). L'annulation d'un lot (R9) devient une commande. | Arches | Une table de la couche Source (§5), sans nouvelle règle | Avant la validation des propositions |
| 5 | **Mémoire des formes écrites des lieux.** Une forme déjà rattachée est proposée à l'identique ; les marques « sans référence » et « à ignorer » sont retenues. | nodegoat | Table de la couche Interprétation, en « proposé » seulement (R18) | Étape « Lieux » |
| 6 | **EDTF en saisie et en export**, à côté du calendrier d'origine. Bibliothèque `edtf` si sa licence le permet. | Arches | Aucune : format d'entrée et de sortie | Saisie assistée, exports |
| 7 | **Cycle de publication** (en cours, publiable, publié) pour les entités exportées. | Arches | À préciser avec la décision 24 | Connecteurs et publication |

Les propositions 1 et 3 touchent le cœur du modèle ; les autres sont des ajouts locaux.

## 5. Les trois comme voisins

- **Arches** publie en JSON‑LD CIDOC‑CRM. Un export Chronologia aligné sur CIDOC‑CRM (§9.2‑3) serait lisible par Arches sans connecteur dédié.
- **ResearchSpace** est un bon **banc d'essai** pour notre RDF : si nos conclusions s'y chargent et s'y affichent comme des arguments, la correspondance CRMinf est juste.
- **nodegoat** a une API et un import de données liées. C'est une cible de publication possible, mais après Heurist (décision 24), plus répandu en France grâce à Huma‑Num.

## Annexe : où regarder dans le code

| Sujet | Fichier |
|---|---|
| nodegoat, tables | `nodegoat/setup/nodegoat_content.sql` |
| nodegoat, chronologie | `nodegoat/APP/nodegoat/CMS/classes/FormatTypeObjectsBase.php` (`formatToSQLChronology`, `formatToChronology`), `StoreType.php` (`getTimeDirections`, `getTimeUnits`) |
| nodegoat, relecture | `nodegoat/APP/nodegoat/CMS/classes/StoreTypeObjects.php` (`date_audited`) |
| nodegoat, rapprochement | `ReconcileTypeObjectsValues.php`, `StorePatternsTypeObjectPair.php` |
| Arches, modèles | `arches/arches/app/models/models.py` (`TileModel`, `EditLog`, `ResourceInstanceLifecycle`, `LoadStaging`, `LoadErrors`) |
| Arches, modifications provisoires | `arches/arches/app/models/tile.py` (`apply_provisional_edit`) |
| Arches, dates | `arches/arches/app/datatypes/datatypes.py` (`EDTFDataType`), `arches/arches/app/utils/date_utils.py` |
| Arches, import | `arches/arches/app/etl_modules/` (`reverse_load`) |
| ResearchSpace, arguments | `researchspace/src/main/web/components/arguments/ArgumentsApi.ts`, `AssertionsStore.ts`, `ArgumentsStore.ts` |
| ResearchSpace, vocabulaire | `researchspace/src/main/java/org/researchspace/vocabulary/CrmInf.java` |
