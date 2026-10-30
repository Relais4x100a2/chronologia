# Modèle Événement–Masque–Factoïde

**Étude documentaire, modèle conceptuel et stratégie d'import GeneWeb**
Version 0.9, 30 octobre 2026, préparée pour Guillaume Cayeux

> **Principe du modèle, depuis la v0.4 : quatre agrégations construites de la même façon**
> PASSAGE ⇢ SOURCE · MASQUE ⇢ PERSONNE · FACTOÏDE ⇢ ÉVÉNEMENT · MENTION DE LIEU ⇢ LIEU HISTORIQUE ou SITE
> À gauche, ce qui est écrit (couche Source, immuable). À droite, ce que l'on conclut (couche Interprétation, révisable). Chaque flèche est une identification révisable, qui porte un degré de confiance et une conclusion.

## Journal des versions

| Version | Changements |
|---|---|
| 0.1 | Modèle en trois couches (Source, Événement, Interprétation). Pivot sur l'événement. |
| 0.2 | Ajout de NOM, LOT_IMPORT et R9. Stratégie d'import GeneWeb. Analyse d'OCaml. |
| 0.3 | **Modèle symétrique.** L'événement passe dans la couche Interprétation ; le factoïde devient l'événement tel que la source le décrit, et porte les participations. Les chaînes de source brutes sont rattachées aux sources canoniques par le même mécanisme. Une structure d'identification commune sert aux trois agrégations. Ajouts : règles R10 à R12, choix d'implémentation (PostgreSQL, réification, projection en graphe), principes de l'interface de validation. |
| 0.4 | **Lieux en quatrième agrégation** : le lieu écrit (MENTION_LIEU) est rattaché au lieu du répertoire par une IDENT_LIEU ; la couche Source ne contient plus aucune résolution (R13). **Granularité tranchée** : un factoïde par acte, ou par épisode pour les sources narratives (R14). |
| 0.5 | **Lieu historique et site topographique distingués.** Le SITE (coordonnées physiques immuables) devient un référentiel ; le LIEU_HISTORIQUE (territoire ou institution datés) se décompose en noms, emprises, appartenances et localisations, chacun avec sa période de validité. Plusieurs hiérarchies territoriales coexistent. Règles R15 à R17. Section 4.8. |
| 0.5.1 | Ajustements PostGIS : site typé en point avec rayon d'incertitude, emprise approximative par point et rayon (zone tampon calculée à l'affichage), index spatiaux. Cas des paroisses partagées entre deux juridictions. |
| 0.6 | **Saisie assistée par modèles de langage** (section 7) : circuit dépôt, lecture à voix haute, extraction, validation ; modèles spécialisés derrière une passerelle ; déploiement hybride (serveur local, services en ligne, petits modèles en local). Ajouts au modèle : zone de brouillon, ancrage au mot, contributeur « agent », confiance d'extraction, indicateur lu ou déduit. Règles R18 à R21. |
| 0.7 | **Conclusions à effets multiples** (CONCLUSION_EFFET) et **contraintes temporelles** (CONTRAINTE_TEMPORELLE) : une même décision peut valider un lieu et resserrer la date d'un événement. État « incertitude assumée », distinct du conflit. Sources hors calcul : jamais effacées. Calculs métriques en Lambert‑93. Règles R22 à R24. Écrans de la maquette et règles d'interface consignés (6.1 à 6.6). |
| 0.7.1 | Consolidation du dossier. Question ouverte ajoutée en 9.2 (point 6) : faut-il une notion d'organisation ? Aucun changement de modèle ni de règle. |
| 0.7.2 | **Provenance de fichier sur le PASSAGE** : `fichier_source`, `ligne_debut`, `ligne_fin` (4.4, décision 7 en 9.1). Import GeneWeb : rôle `officier` pour les témoins `#offi` (décision 8) et date déclarée prise telle que normalisée par l'analyseur (décision 9). Aucune nouvelle règle d'intégrité. |
| 0.7.3 | **`date_brute` sur le FACTOÏDE** (4.4, décision 9 en 9.1) : la date telle qu'écrite dans la source est conservée à côté de la date normalisée et des bornes. Aucune nouvelle règle d'intégrité. |
| 0.7.4 | **Import GeneWeb de QUALITE et de MENTION_LIEU** : `categorie` et `rang` sur QUALITE (4.4, décision 10) ; désignation « moderne » des lieux importés et IDENT_LIEU différée jusqu'aux référentiels (décision 11). Aucune nouvelle règle d'intégrité. |
| 0.7.5 | **LOT_IMPORT, `cle_externe` et notes à l'import GeneWeb** : `nb_entites` sur LOT_IMPORT, `cle_externe` sur PASSAGE (4.4), formats de clés (5.3), réimport idempotent (5.8 étape 6) ; décisions 12 et 13. Aucune nouvelle règle d'intégrité. |
| 0.7.6 | **`cle_famille` sur le FACTOÏDE** (4.4, décision 14) : clé déterministe des familles GeneWeb pour le réimport. Aucune nouvelle règle d'intégrité. |
| 0.7.7 | **Événements déclarés sur la ligne de personne** (5.3, décision 15) : naissance, baptême, décès et inhumation écrits sur la ligne d'un enfant ou d'un conjoint donnent chacun un factoïde, sans nouvelle règle. |
| 0.7.8 | **Différentiel de lots** (5.8 étape 6, décision 16) : comparaison pure de deux LOT_IMPORT d'un même corpus (ajouts, invariants, modifications, rétractions). Aucune nouvelle règle d'intégrité. |
| 0.7.9 | **Différentiel des CONCLUSION** (décision 16 complétée) : les notes de personne sont comparées par cible. Aucune nouvelle règle d'intégrité. |
| 0.7.10 | **Note de témoin** : PARTICIPATION porte un champ optionnel `note` (le `wnote` GeneWeb, rattaché au témoin qui précède). Le texte nu des blocs `pevt`, `fam` et `fevt` est conservé (R13). Aucune nouvelle règle. |
| 0.7.11 | **Événements familiaux `fevt` exhaustifs** : chaque tag d'un bloc `fevt` donne un FACTOIDE typé (`mariage`, `divorce`, `separation`, `engagement`, `contrat_mariage`, `bans_mariage`, `licence_mariage`, `non_mariage`, `non_mention`, `annulation`, `pacs`, `residence`) ; un tag inconnu garde son écriture d'origine comme type libre. Une famille sans conjoint connu (`fam ? ? + ? ?`) est importée avec ses enfants et événements ; sa clé porte le premier enfant. Aucune règle nouvelle (R13 appliquée). |
| 0.7.12 | **Persistance SQLite** : décision 18. Socle de développement et de test en SQLite (`:memory:` ou fichier local), schémas PostgreSQL simulés par préfixe de table (`source_`, `interp_`, `audit_`). R10 appliquée par triggers `BEFORE UPDATE` et `BEFORE DELETE` ; rétractation par `audit_retractation`. Aucune règle nouvelle. |
| 0.7.13 | **Application du différentiel à la base** : décision 18 complétée. `appliquer_diff` retire de la vue active les occurrences du lot ancien que le lot nouveau remplace, par trois motifs d'audit : `retractation`, `modification`, `reconduction`. Vues actives `source_factoide_actif` et `interp_conclusion_actif`. Aucune règle nouvelle. |
| 0.8 | **Identification prosopographique MASQUE ⇢ PERSONNE** (4.4, décision 19). PERSONNE réduite à une coquille dont tout est calculé (R8), fusion par `same_as_id`. Le statut d'une identification devient un **journal** (IDENT_PERSONNE_STATUT) : chaque décision est une ligne nouvelle, le statut courant est la dernière (R10 tenue sans exception). **Faisceau d'indices** (INDICE) : chaque indice comparé est une ligne, calculée par une règle versionnée ou jugée par un humain. CONTRIBUTEUR typé (humain, agent, import). CONCLUSION sans cible obligatoire, ses conséquences passant par CONCLUSION_EFFET (R22). Règle R25. |
| 0.8.1 | **Identifications de l'import GeneWeb** (décision 19, 5.3, 5.8). Une personne par clé GeneWeb, portée en `ref` ; tous les masques de la clé lui sont rattachés. Au réimport, la personne est réutilisée et les identifications du lot ancien sortent de la vue active par `audit_retractation`, comme les factoïdes. Une décision humaine en désaccord avec l'import n'est jamais écrasée : la nouvelle identification reste « proposé » (R24). R18 précisée : un agent ne verse que des propositions, il ne rejette pas plus qu'il n'active. |
| 0.9 | **Rapprochement d'homonymes par faisceau d'indices** (décision 20). Un agent compare les personnes de bases différentes dont le nom normalisé concorde, masque par masque, selon trois familles de règles versionnées (onomastique, chronologie, parenté), et propose une identification « possible » ou « probable » quand le barème le justifie. Logique de calcul pure, séparée de la persistance. Règle R26 : encadrement des rapprochements calculés. |

## Sommaire

1. [Objectif et contexte](#1-objectif-et-contexte)
2. [Corpus de référence](#2-corpus-de-référence)
3. [Synthèse des concepts clés](#3-synthèse-des-concepts-clés)
4. [Modèle conceptuel v0.4](#4-modèle-conceptuel-v04)
5. [Import depuis GeneWeb](#5-import-depuis-geneweb)
6. [Interface de validation](#6-interface-de-validation)
7. [Saisie assistée par modèles de langage](#7-saisie-assistée-par-modèles-de-langage)
8. [Implémentation : PostgreSQL et OCaml](#8-implémentation--postgresql-et-ocaml)
9. [Décisions et questions ouvertes](#9-décisions-et-questions-ouvertes)
10. [Sources](#10-sources)

---

## 1. Objectif et contexte

Le but est de concevoir un modèle de données historique **orienté événements**, à la croisée de la généalogie, de la prosopographie et de l'analyse relationnelle.

- **Entité pivot :** l'événement, ancré dans le temps et dans l'espace. Depuis la v0.3, on distingue l'événement *tel qu'une source le décrit* (le factoïde) de l'événement *tel que le chercheur le reconstitue*.
- **Entités rattachées :** personnes, masques et rôles (une personne agit sous un rôle précis dans un événement donné), lieux, témoins, sources et preuves, types d'événements.
- **Principe :** modèle orienté **factoïde**. L'information tirée des sources est normalisée, l'incertitude et les points de vue divergents sont conservés.
- **Contrainte d'import :** une partie des données viendra de bases **GeneWeb**.

Précision de vocabulaire : IBM écrit **ELP** (Entity, Link, Property), et non EPL. Dans Analyst's Notebook, un *item type* désigne un type d'entité ou un type de lien. Les attributs forment une notion à part (*attribute classes*), et un événement n'y est pas une classe distincte : c'est un type d'entité affiché en *event frame* sur la vue chronologique.

---

## 2. Corpus de référence

Treize références en quatre familles.

### 2.1 Prosopographie et factoïdes

#### 01. Bradley & Short (2005)

- **Référence :** Bradley, J. & Short, H. (2005). « Texts into databases: the evolving field of new-style prosopography ». *Literary and Linguistic Computing*, 20 (suppl.), p. 3‑24.
- **Nature :** papier académique, le texte fondateur.
- **Modèle :** un factoïde est une affirmation tirée d'un passage de source. Elle relie une ou plusieurs personnes, un lieu et une date. La base ne dit pas qui était X : elle enregistre ce que la source S dit de X, et l'identité de la personne est reconstruite à partir de ces affirmations.
- **À retenir :** le factoïde sert de pivot entre la source et la personne. La référence précise dans la source est obligatoire, et plusieurs affirmations contradictoires peuvent coexister sans être fusionnées.

#### 02. Pasin & Bradley (2015)

- **Référence :** Pasin, M. & Bradley, J. (2015). « Factoid-based prosopography and computer ontologies: towards an integrated approach ». *Digital Scholarship in the Humanities*, 30(1), p. 86‑97.
- **Nature :** papier académique, avec une ontologie OWL (la Factoid Prosopography Ontology, FPO).
- **Modèle :** le modèle factoïde est formalisé en ontologie et aligné sur CIDOC‑CRM. Chaque personne est citée à travers une *person reference* propre à la source, qu'on rattache ensuite à la personne consolidée.
- **À retenir :** c'est la base de la séparation entre personne et masque. Le lien d'identification entre les deux est lui-même une assertion qu'on peut remettre en cause.

#### 03. SNAP:DRGN (2016)

- **Référence :** Bodard, G., Cayless, H., Depauw, M., Isaksen, L., Lawrence, K. F., Rahtz, S. (2016). « Standards for Networking Ancient Prosopographies ». In G. Bodard & M. Romanello (dir.), *Digital Classics Outside the Echo‑Chamber*, Ubiquity Press, p. 29‑44.
- **Nature :** papier académique et spécification RDF.
- **Modèle :** SNAP relie des bases prosopographiques sans les fusionner. Chaque base garde ses propres URI de personnes. Des liens de co-référence (*same as*, *may be the same as*) et des relations typées (parenté, relations sociales) sont publiés en Linked Data.
- **À retenir :** l'identification se fait par des liens explicites, jamais par écrasement. Le vocabulaire de relations sociales et de parenté est réutilisable.

#### 04. IPIF (2019)

- **Référence :** Vogeler, G., Vasold, G., Schlögl, M. (2019). « Data exchange in practice: Towards a prosopographical API ». *Biographical Data in a Digital World 2019*, CEUR‑WS vol. 3152. Spécification associée : IPIF (International Prosopography Interchange Framework).
- **Nature :** papier académique et spécification d'API (OpenAPI).
- **Modèle :** l'API expose quatre ressources : Factoid, Person, Source et Statement. Un factoïde relie une personne et une source à un ou plusieurs *statements* typés (rôle, date, lieu, personnes liées).
- **À retenir :** un gabarit prêt à l'emploi pour le triangle source → factoïde → personne, avec l'auteur et la date de saisie.

### 2.2 Standards et ontologies

#### 05. CIDOC‑CRM

- **Référence :** CIDOC‑CRM, version 7.1.x. CIDOC CRM SIG / ICOM ; norme ISO 21127:2023.
- **Nature :** standard (ontologie formelle).
- **Modèle :** **E5 Event** se spécialise en E7 Activity, E63/E64 (début et fin d'existence), E67 Birth, E69 Death, E85 Joining, E86 Leaving, etc. Un événement est ancré par P4 *has time‑span* (qui porte des bornes floues, P82a/P82b) et par P7 *took place at*. Les participants sont reliés par P11 *had participant* ou P14 *carried out by*. Le rôle est porté par une propriété de propriété, **P14.1 in the role of**, réifiée dans la version 7 sous la forme PC14.
- **À retenir :** l'événement est un pivot légitime. Le rôle est porté par le lien entre la personne et l'événement, pas par la personne. Les intervalles flous sont gérés.

#### 06. CRMinf

- **Référence :** CRMinf, Argumentation Model. Stead, Doerr et al., CIDOC CRM SIG.
- **Nature :** extension du CIDOC‑CRM.
- **Modèle :** I2 *Belief* porte une valeur de vérité (I6) sur un ensemble de propositions (I4 *Proposition Set*). Les croyances sont produites par une inférence (I5) ou par l'adoption de l'avis d'une autorité ou d'une source (I7 *Belief Adoption*).
- **À retenir :** l'outil formel pour les points de vue et l'incertitude : qui affirme quoi, avec quel degré de confiance, sur quelle base.

#### 07. GEDCOM X

- **Référence :** GEDCOM X Conceptual Model. FamilySearch, spécification 1.0, gedcomx.org.
- **Nature :** spécification technique.
- **Modèle :** le modèle sépare les *records* (personas extraits d'une source) des *conclusions* (personnes reconstruites), liés par un *EvidenceReference*. Un Event porte date et lieu ; ses participants sont des **EventRole** typés : *Principal*, *Participant*, *Official*, *Witness*. Chaque élément porte une **Attribution** et une **confidence**, et renvoie aux *SourceDescription*.
- **À retenir :** la correspondance la plus directe avec notre architecture. Persona = masque, EventRole = rôle, le témoin est un rôle natif, et la preuve est chaînée jusqu'à la source.

#### 08. GENTECH

- **Référence :** GENTECH Genealogical Data Model. Lexicon Working Group, National Genealogical Society, 1998 ; révision 2000.
- **Nature :** spécification (modèle logique).
- **Modèle :** chaque **Assertion** relie un sujet (Persona, Event, Characteristic ou Group) à une valeur, en citant une source. Les personas sont regroupés en personnes par des assertions d'identité, et une assertion peut être tirée d'autres assertions.
- **À retenir :** l'ancêtre de GEDCOM X et le modèle le plus proche du factoïde en généalogie. Les **groupes** (familles, confréries, foyers) y sont des sujets à part entière.

#### 09. FHISO

- **Référence :** FHISO. Extended Legacy Format (ELF) : Data Model et Serialisation ; vocabulaire *Citation Elements* (fhiso.org/TR).
- **Nature :** standards techniques.
- **Modèle :** ELF formalise un modèle compatible GEDCOM 5.5.1, avec des extensions déclarées. *Citation Elements* décompose une citation en éléments typés (auteur, titre, dépôt, localisation…). FHISO a aussi produit un standard de dates.
- **À retenir :** l'interopérabilité avec GEDCOM, la normalisation des sources, et un traitement des dates approximatives et des calendriers anciens.

#### 10. Bio CRM (2018)

- **Référence :** Tuominen, J., Hyvönen, E., Leskinen, P. (2018). « Bio CRM: A Data Model for Representing Biographical Data for Prosopographical Research ». *BD2017*, CEUR‑WS vol. 2119, p. 59‑66.
- **Nature :** papier académique et ontologie.
- **Modèle :** Bio CRM étend CIDOC‑CRM avec trois catégories de rôles : **rôles unaires durables** (profession, titre), **rôles binaires durables** (relations entre personnes) et **rôles de participation à un événement** (témoin, parrain, officiant).
- **À retenir :** la grille pour typer les masques et les rôles, sans confondre rôle ponctuel, statut durable et relation.

### 2.3 Modèles d'investigation (IBM i2)

#### 11. IBM i2 Analyst's Notebook

- **Référence :** IBM i2 Analyst's Notebook : Entity Link Properties (ELP) et Chart Reference. IBM, puis i2 Group.
- **Nature :** documentation technique.
- **Modèle :** un graphe d'entités typées et de liens typés, qui peuvent être orientés, multiples ou fusionnés. Les *attribute classes* portent les valeurs et les *cards* les éléments de preuve (source, date, notation). La vue chronologique place les événements en *event frames* sur des *theme lines*, une ligne par personne.
- **À retenir :** un événement peut être un lien daté entre deux personnes, ou une entité reliée à ses participants ; pour notre modèle, c'est la seconde forme qu'il faut retenir. Les cards donnent une traçabilité élément par élément, et la notation des sources (grille de type Amirauté, fiabilité × crédibilité) s'applique aux témoignages.

#### 12. IBM i2 Enterprise Insight Analysis

- **Référence :** IBM i2 Enterprise Insight Analysis Data Model White Paper (v4.1, v4.3) ; documentation « The i2 Analyze data model » (docs.i2group.com).
- **Nature :** livre blanc et spécification technique.
- **Modèle :** le schéma i2 Analyze définit des types d'entités, de liens et de propriétés, ainsi que les couples source/cible autorisés pour chaque type de lien. Chaque *item* est construit à partir de *records* qui portent chacun leur provenance et leur notation.
- **À retenir :** la séparation entre item et records correspond au couple personne / factoïde. Le schéma contraint les types de liens, et la provenance par record permet de fusionner ou dissocier des entités sans perte.

### 2.4 Format d'import

#### 13. GeneWeb

- **Référence :** GeneWeb. Daniel de Rauglaudre (INRIA, 1997‑), aujourd'hui maintenu par la communauté et Geneanet ; licence GPL. Version 7.1.0‑beta2 (décembre 2024). Documentation du format `.gw` (geneweb.tuxfamily.org) et types OCaml du module `Def` (github.com/geneweb/geneweb).
- **Nature :** logiciel libre, format de fichier et types OCaml.
- **Modèle :** modèle centré sur la personne et la famille, au niveau des conclusions. Une personne est identifiée par son nom, son prénom et un numéro d'occurrence. Depuis la version 7, des événements personnels (`pevt`) et familiaux (`fevt`) portent date, lieu, source, note et témoins. La 7.1 type les témoins : parrain, officier civil, officier religieux, informateur, présent, mentionné.
- **À retenir :** c'est la source d'import prioritaire. Ses témoins typés et ses dates à précision se transposent bien. En revanche, il n'a ni masque, ni entité source, ni lieu structuré : il faut les reconstruire à l'import (section 5).

---

## 3. Synthèse des concepts clés

| Concept | Définition pour notre modèle | Références |
|---|---|---|
| Événement pivot | Distingué en deux : le factoïde (événement tel que raconté) et l'événement reconstitué qui regroupe les factoïdes. | 05, 07, 11, 13 |
| Masque | Mention d'une personne telle que la source la présente. Distinct de la personne consolidée. | 01, 02, 07, 08 |
| Identification | Lien révisable d'un élément écrit vers une entité conclue : passage → source, masque → personne, factoïde → événement. | 03, 07, 12 |
| Rôle de participation | Porté par le lien masque ↔ événement, pas par la personne. | 05, 07, 10, 13 |
| Rôles durables | Statut unaire (profession) et relation binaire (parenté), séparés des rôles ponctuels. | 03, 10 |
| Factoïde | Unité atomique : source + localisation + énoncé + auteur de saisie. | 01, 04, 08 |
| Point de vue et confiance | Qui affirme, sur quelle base, avec quel degré de confiance. | 06, 07 |
| Notation de la preuve | Fiabilité de la source × crédibilité de l'information. | 11 |
| Témoin | Rôle dans l'événement et, le cas échéant, déclarant d'une affirmation. | 06, 07, 13 |
| Typage contraint des liens | Chaque type de lien déclare les types d'entités qu'il peut relier. | 02, 12 |
| Provenance d'import | Chaque donnée garde le lot, le fichier et la clé d'origine. | 12, 13 |

---

## 4. Modèle conceptuel v0.4

### 4.1 Principe : quatre agrégations symétriques

Rattacher deux passages d'archives au même événement, c'est déjà interpréter. La v0.3 en a tiré la conséquence, et la v0.4 l'étend aux lieux : **tout ce qui regroupe des éléments écrits relève de l'Interprétation**, et ce regroupement se fait toujours de la même façon.

| Ce qui est écrit (Source) | Ce qui est conclu (Interprétation) | Identification | Question tranchée par le chercheur |
|---|---|---|---|
| PASSAGE (citation brute et localisation) | SOURCE (document canonique) | IDENT_SOURCE | Ces citations renvoient-elles au même document ? |
| MASQUE (personne telle que nommée) | PERSONNE (individu reconstruit) | IDENT_PERSONNE | Ces mentions désignent-elles le même individu ? |
| FACTOIDE (événement tel que raconté) | EVENEMENT (événement reconstitué) | IDENT_EVENEMENT | Ces récits décrivent-ils le même événement ? |
| MENTION_LIEU (lieu tel qu'écrit) | LIEU_HISTORIQUE (territoire daté) ou SITE (emplacement physique), voir 4.8 | IDENT_LIEU | Ce « Saint‑Aubin » est-il Saint‑Aubin‑sur‑Scie, Saint‑Aubin‑des‑Bois, ou une paroisse disparue ? |

Les quatre identifications ont **la même structure** : un élément de départ, une cible, un degré (certain, probable, possible), un statut (proposé, actif, rejeté) et une conclusion qui l'argumente. Une seule logique à coder, à tester et à présenter dans l'interface.

La résolution d'un lieu historique est souvent une interprétation à part entière. En v0.3, `FACTOIDE.lieu_id` la plaçait dans la couche Source : le jour où un chercheur prouve que ce n'était pas le bon Saint‑Aubin, il aurait fallu modifier un factoïde, contre R10. La v0.4 corrige ce point.

### 4.2 Les couches

| Couche | Entités | Propriétés |
|---|---|---|
| **Source** (ce qui est écrit) | PASSAGE, FACTOIDE, MASQUE, PARTICIPATION, QUALITE, RELATION, NOM, MENTION_LIEU | **Immuable**, en insertion seule. Le factoïde est le seul point d'ancrage : il porte la date déclarée, le type d'événement décrit, ses mentions de lieu, et c'est à lui que se rattachent les participations. |
| **Interprétation** (ce que l'on conclut) | SOURCE, PERSONNE, EVENEMENT, LIEU_HISTORIQUE (+ NOM_LIEU, EMPRISE, APPARTENANCE, LOCALISATION), IDENT_SOURCE, IDENT_PERSONNE, IDENT_EVENEMENT, IDENT_LIEU, CONCLUSION | Révisable. Chaque regroupement porte un auteur, un degré et des arguments. Plusieurs points de vue coexistent ; un seul est « actif » à un instant donné. |
| **Référentiels** | TYPE_EVENEMENT, ROLE, CONTRIBUTEUR, LOT_IMPORT, SITE | Vocabulaires contrôlés (alignés sur CIDOC‑CRM et Bio CRM), provenance des imports et sites topographiques (coordonnées immuables). |
| **Vues dérivées** | Participants d'un événement, intervalle d'un événement, fiche consolidée d'une personne, réseau | Calculées à partir des identifications actives, jamais saisies à la main. |

Ce qui a changé en v0.3 par rapport à la v0.2 :

- EVENEMENT quitte la couche Source et devient un regroupement de factoïdes.
- PARTICIPATION se rattache au factoïde, et non plus à l'événement. Les participants d'un événement sont une vue.
- SOURCE devient le document canonique ; la chaîne telle qu'écrite ou importée reste dans PASSAGE.
- LIEU passe dans les référentiels (v0.3), puis dans la couche Interprétation (v0.4).

Ce qui change en v0.4 :

- Le lieu tel qu'écrit devient une MENTION_LIEU, rattachée au factoïde. Elle précise sa fonction : lieu de l'événement, domicile d'un masque (« demeurant à »), lieu d'origine, lieu attaché à un titre.
- LIEU devient une entité conclue, reliée aux mentions par IDENT_LIEU.

En v0.5, LIEU se dédouble en SITE (référentiel) et LIEU_HISTORIQUE (interprétation) : voir 4.8.

### 4.3 Diagramme entités–associations

```mermaid
erDiagram
  PASSAGE ||--o{ FACTOIDE : fonde
  PASSAGE ||--o{ MASQUE : mentionne
  FACTOIDE ||--o{ PARTICIPATION : declare
  MASQUE ||--o{ PARTICIPATION : "agit sous"
  ROLE ||--o{ PARTICIPATION : qualifie
  FACTOIDE ||--o{ QUALITE : declare
  MASQUE ||--o{ QUALITE : porte
  FACTOIDE ||--o{ RELATION : declare
  MASQUE ||--o{ RELATION : sujet
  MASQUE ||--o{ RELATION : objet
  MASQUE ||--o{ NOM : porte
  MASQUE |o--o{ FACTOIDE : "declarant de"
  TYPE_EVENEMENT |o--o{ FACTOIDE : "type decrit"
  FACTOIDE ||--o{ MENTION_LIEU : cite
  MASQUE |o--o{ MENTION_LIEU : "domicile de"
  PASSAGE ||--o{ IDENT_SOURCE : rattache
  SOURCE ||--o{ IDENT_SOURCE : regroupe
  MASQUE ||--o{ IDENT_PERSONNE : rattache
  PERSONNE ||--o{ IDENT_PERSONNE : regroupe
  FACTOIDE ||--o{ IDENT_EVENEMENT : rattache
  EVENEMENT ||--o{ IDENT_EVENEMENT : regroupe
  MENTION_LIEU ||--o{ IDENT_LIEU : rattache
  LIEU_HISTORIQUE |o--o{ IDENT_LIEU : territoire
  SITE |o--o{ IDENT_LIEU : emplacement
  TYPE_EVENEMENT ||--o{ EVENEMENT : type
  LIEU_HISTORIQUE |o--o{ EVENEMENT : "lieu retenu"
  SITE |o--o{ EVENEMENT : "site retenu"
  CONCLUSION ||--o{ IDENT_SOURCE : justifie
  IDENT_PERSONNE ||--o{ IDENT_PERSONNE_STATUT : "journal de"
  CONCLUSION |o--o{ IDENT_PERSONNE_STATUT : justifie
  CONTRIBUTEUR ||--o{ IDENT_PERSONNE : propose
  CONTRIBUTEUR ||--o{ IDENT_PERSONNE_STATUT : decide
  IDENT_PERSONNE ||--o{ INDICE : "faisceau de"
  PERSONNE |o--o{ PERSONNE : "same as"
  CONCLUSION ||--o{ IDENT_EVENEMENT : justifie
  CONCLUSION ||--o{ IDENT_LIEU : justifie
  CONCLUSION }o--o{ FACTOIDE : "s'appuie sur"
  CONCLUSION }o--o{ PARTICIPATION : "porte sur"
  CONTRIBUTEUR ||--o{ FACTOIDE : saisit
  CONTRIBUTEUR ||--o{ CONCLUSION : soutient
  CONCLUSION ||--o{ CONCLUSION_EFFET : produit
  CONCLUSION ||--o{ CONTRAINTE_TEMPORELLE : impose
  EVENEMENT ||--o{ CONTRAINTE_TEMPORELLE : borne
  EVENEMENT |o--o{ CONTRAINTE_TEMPORELLE : "date de reference"
  LOT_IMPORT |o--o{ FACTOIDE : produit
  LIEU_HISTORIQUE ||--o{ NOM_LIEU : nomme
  LIEU_HISTORIQUE ||--o{ EMPRISE : "etendue datee"
  LIEU_HISTORIQUE ||--o{ APPARTENANCE : partie
  LIEU_HISTORIQUE ||--o{ APPARTENANCE : tout
  LIEU_HISTORIQUE ||--o{ LOCALISATION : "siege ou chef-lieu"
  SITE ||--o{ LOCALISATION : situe
  TYPE_EVENEMENT |o--o{ TYPE_EVENEMENT : "sous-type de"
```

Lecture rapide : passage, factoïde, masque, participation et mention de lieu forment la couche Source ; chaque entité IDENT_* fait le pont vers son pendant de la couche Interprétation.

### 4.4 Dictionnaire des entités

**Couche Source (insertion seule)**

| Entité | Définition | Attributs principaux |
|---|---|---|
| PASSAGE | Endroit cité d'un document, tel que saisi ou importé. | `citation_brute` (texte d'origine), `localisation` (folio, page, ligne), `transcription`, `langue`, `image_uri`, `cle_externe`, `fichier_source` / `ligne_debut` / `ligne_fin` (provenance dans le fichier importé, 1‑indexées, bornes incluses) |
| FACTOIDE | Événement ou affirmation tel qu'un passage le décrit. Seul point d'ancrage de la couche. | `passage_id`, `type_evenement_id` (type décrit), `enonce`, `date_declaree` (texte), `cle_famille` (clé GeneWeb de la famille d'origine, commune aux factoïdes d'une même famille), `date_brute` (texte exact de la source), `date_min` / `date_max` / `calendrier` (normalisation mécanique du texte), `declarant_masque_id`, `credibilite` (1–6), `saisi_par`, `saisi_le`, `lot_import_id`, `remplace_id` (correction) |
| MASQUE | Personne telle que le passage la présente. | `passage_id` (un seul), `nom_ecrit`, `nom_normalise`, `sexe`, `age_declare`, `qualification_libre` |
| PARTICIPATION | Présence d'un masque dans un factoïde, sous un rôle. C'est un nœud à part entière : une conclusion peut la contester. | `factoide_id`, `masque_id`, `role_id`, `ordre`, `note` (optionnelle) |
| QUALITE | Rôle durable unaire (profession, titre, statut). Son lieu éventuel passe par une mention de lieu. | `factoide_id`, `masque_id`, `role_id` (libellé du rôle), `categorie` (profession, titre), `valide_debut`, `valide_fin`, `rang` (rang d'un titre) |
| RELATION | Rôle durable binaire (parenté, alliance, patronage). | `factoide_id`, `masque_sujet_id`, `masque_objet_id`, `type_relation`, `orientation` |
| NOM | Formes de nom d'un masque. | `masque_id`, `type` (principal, public, alias, surnom, qualificatif), `prenoms`, `nom`, `forme_ecrite` |
| MENTION_LIEU | Lieu tel que le passage l'écrit. | `factoide_id`, `forme_ecrite` (« S. Aubin »), `forme_normalisee`, `fonction` (lieu de l'événement, domicile, origine, lieu d'un titre), `masque_id` (si domicile ou origine), `qualite_id` (si titre), `epoque_designation` (contemporaine de l'acte ou moderne) |

**Couche Interprétation (révisable)**

| Entité | Définition | Attributs principaux |
|---|---|---|
| SOURCE | Document canonique auquel renvoient une ou plusieurs citations. | `titre`, `type`, `depot`, `cote` (éléments FHISO), `auteur_source`, `date_production`, `nature` (original, copie, transcription, compilation), `fiabilite` (A–F) |
| PERSONNE | Individu reconstruit ; ses données sont calculées à partir de ses masques (R8). Elle ne stocke ni nom, ni date, ni lieu : c'est une coquille. | `uri`, `nom_retenu` (vue), `same_as_id` (personne canonique après fusion, R4), `acces`, `cle_externe` (identifiant d'un référentiel externe ; la clé GeneWeb reste portée par le MASQUE) |
| EVENEMENT | Événement reconstitué à partir d'un ou plusieurs factoïdes. | `type_evenement_id`, `libelle`, `debut_min` / `debut_max` / `fin_min` / `fin_max` (calculés, ou fixés par une conclusion), `lieu_historique_id` et `site_id` (calculés à partir des mentions rattachées), `coherence` (cohérent, conflit, incertitude assumée) |
| LIEU_HISTORIQUE | Territoire ou institution territoriale datés : paroisse, seigneurie, bailliage, commune… | `type`, `existence` (intervalle flou), `uri_externe` |
| NOM_LIEU | Nom d'un lieu historique sur une période. | `lieu_historique_id`, `nom`, `langue`, `validite` |
| EMPRISE | Étendue spatiale d'un lieu historique sur une période. | `lieu_historique_id`, `geometrie` (polygone si les limites sont connues), `centre` et `rayon_incertitude_m` (sinon), `validite`, `precision`, `conclusion_id` |
| APPARTENANCE | Rattachement d'un lieu historique à un autre, dans une hiérarchie donnée. | `partie_id`, `tout_id`, `hierarchie` (ecclésiastique, judiciaire, fiscale, seigneuriale, administrative), `validite`, `conclusion_id` |
| LOCALISATION | Lien entre un lieu historique et un site. | `lieu_historique_id`, `site_id`, `fonction` (chef-lieu, église paroissiale, château), `validite` |
| IDENT_SOURCE · IDENT_PERSONNE · IDENT_EVENEMENT · IDENT_LIEU | Structure commune : un élément écrit rattaché à une entité conclue. Pour IDENT_LIEU, la cible est un lieu historique ou un site. | `de_id`, `vers_id`, `degre` (certain, probable, possible), `statut` (proposé, actif, rejeté), `conclusion_id`, `lot_import_id` ; pour IDENT_PERSONNE, depuis la v0.8, `statut` et `conclusion_id` sont portés par le journal IDENT_PERSONNE_STATUT (R25), et `contributeur_id` désigne l'auteur de la proposition |
| IDENT_PERSONNE_STATUT | Une décision sur une identification de personne. Le statut courant est la dernière décision (R25). | `ident_id`, `statut` (proposé, actif, rejeté), `conclusion_id` (facultatif pour une proposition, attendu pour une activation ou un rejet), `contributeur_id`, `date` |
| INDICE | Un élément d'un faisceau : ce qui a été comparé entre le masque et la personne candidate, et dans quel sens cela pèse. | `ident_id`, `type` (nom, sexe, âge, date, lieu, parenté, conjoint, profession, co-présence…), `sens` (pour, contre, neutre), `poids`, `valeur_masque` et `valeur_personne` (ce qui a été comparé, tel quel), `mode` (calculé, jugé), `regle_version` (si calculé, par exemple `regle:chrono:v1`), `factoide_id` (fait d'appui, facultatif), `conclusion_id` (si jugé) |
| CONCLUSION | Point de vue argumenté (CRMinf I2 Belief, I5 Inference Making). | `contributeur_id`, `date`, `valeur` (vrai, faux, incertain), `motifs[]` (liste prédéfinie), `argument` (texte libre), `factoides[]`, `cible` (élément contesté, facultatif) ; ses conséquences sont listées dans CONCLUSION_EFFET |
| CONCLUSION_EFFET | Une conséquence d'une conclusion. Une conclusion peut en avoir plusieurs, appliquées ensemble et retirées ensemble (R22). | `conclusion_id`, `type` (activer, rejeter ou proposer une identification ; poser une contrainte temporelle ; fixer un lieu retenu ; marquer une incertitude assumée), `cible_type`, `cible_id` |
| CONTRAINTE_TEMPORELLE | Borne imposée à un événement par une conclusion, qui s'ajoute à l'intersection des factoïdes. | `evenement_id`, `borne` (début min, début max, fin min, fin max), `valeur` (date fixe) ou `evenement_reference_id` (borne liée à la date d'un autre événement, par exemple un changement de territoire), `conclusion_id` |

**Référentiels**

| Entité | Définition | Attributs principaux |
|---|---|---|
| TYPE_EVENEMENT | Hiérarchie des types, alignée CIDOC (E67, E69, E85…). | `code`, `libelle`, `parent_id`, `classe_cidoc`, `roles_autorises[]` |
| ROLE | Rôles typés selon les trois catégories Bio CRM. | `code`, `libelle`, `categorie` (participation, unaire, binaire), `inverse_id` |
| CONTRIBUTEUR | Chercheur ou processus automatique. | `nom`, `type` (humain, agent, import) |
| SITE | Emplacement physique, défini par des coordonnées immuables. Ne porte aucune désignation historique. | `geometrie` (point, WGS 84), `rayon_incertitude_m`, `methode` (relevé, géoréférencement d'une carte ancienne, cadastre), `libelle_neutre` |
| LOT_IMPORT | Provenance d'un import. | `format`, `fichier`, `empreinte` (SHA‑256), `outil`, `version`, `date`, `statut` (actif, annulé), `nb_entites` (entités produites par le lot) |

### 4.5 Règles d'intégrité

1. **R1 : un masque correspond à un seul passage.** Deux mentions du même individu donnent deux masques et deux identifications.
2. **R2 : pas d'information sans factoïde.** Participations, qualités et relations sont rattachées à un factoïde par construction.
3. **R3 : les rôles sont contraints par le type d'événement.** La matrice TYPE_EVENEMENT × ROLE s'applique au type décrit par le factoïde (pas de « parrain » dans une vente).
4. **R4 : fusion et dissociation non destructives,** pour les quatre agrégations. Fusionner, c'est pointer plusieurs identifications vers la même cible ; dissocier, c'est rejeter une identification.
5. **R5 : dates en intervalles.** Le factoïde garde le texte déclaré et sa normalisation mécanique (bornes min et max, calendrier). L'intervalle d'un événement est l'intersection des intervalles de ses factoïdes actifs, sauf si une conclusion le fixe.
6. **R6 : double notation de la preuve.** Fiabilité et nature sur la source canonique (une copie tardive est moins fiable que l'original), crédibilité sur le factoïde.
7. **R7 : témoin et déclarant sont deux choses.** Le témoin est un rôle de participation ; le déclarant est la voix du factoïde. Un même masque peut cumuler les deux.
8. **R8 : les vues sont calculées.** Participants d'un événement, fiche d'une personne et réseau se déduisent des identifications actives ; changer une identification les recalcule.
9. **R9 : tout import est réversible.** Annuler un lot le marque « annulé » ; ses factoïdes et identifications sortent de toutes les vues.
10. **R10 : la couche Source est un coffre-fort.** Aucune modification ni suppression : une correction crée un nouveau factoïde qui pointe vers l'ancien (`remplace_id`).
11. **R11 : une seule identification active par élément.** C'est la vue de référence du projet. Les autres points de vue restent « proposé » ou « rejeté », avec leur conclusion, et restent consultables.
12. **R12 : un conflit est signalé, jamais tranché automatiquement.** Des dates d'intersection vide ou des lieux incompatibles passent l'événement en « conflit » et l'envoient dans la file de décisions.
13. **R13 : aucune résolution dans la couche Source.** Elle ne contient que du texte et des normalisations mécaniques (dates, graphies). Tout rattachement à une entité conclue (source, personne, événement, lieu) passe par une identification. Les règles de normalisation des dates sont versionnées pour pouvoir être rejouées.
14. **R14 : un factoïde par acte.** Un baptême, un contrat ou une déposition donne un seul factoïde, qui porte toutes ses participations : la co-présence est l'information essentielle, et l'atomiser en affirmations isolées obligerait à la reconstruire. Pour une source narrative, on crée un factoïde par épisode ; une affirmation isolée devient un factoïde de type « état » ou « activité » (CIDOC E7 Activity, E85 Joining).
15. **R15 : cohérence temporelle des lieux.** Une mention de désignation contemporaine ne peut être rattachée qu'à un lieu historique qui existe à la date du factoïde. Sinon, conflit (R12).
16. **R16 : le présent est une vue.** La commune actuelle et les coordonnées d'un événement se calculent à partir du site ou de l'emprise, jamais l'inverse : un acte de 1712 se rattache à la paroisse de 1712, pas à la commune d'aujourd'hui.
17. **R17 : une mention, un référent.** Si le texte désigne à la fois un emplacement et un territoire (« en l'église de Saint‑Aubin »), on crée deux mentions, chacune avec sa propre identification.

Règles ajoutées en v0.7 :

22. **R22 : une conclusion, plusieurs effets, un seul retrait.** Une décision comme « retenir la chapelle et dater après 1709 » produit plusieurs effets : activer l'identification de la chapelle, rejeter celle de la paroisse, poser une contrainte « début ≥ 1709 » sur l'événement. Ils sont appliqués dans une seule transaction ; retirer la conclusion les retire tous. Une contrainte peut renvoyer à la date d'un autre événement (le changement de territoire) plutôt qu'à une date fixe : si cette date est révisée, la contrainte suit.
23. **R23 : l'incertitude assumée n'est pas un conflit.** Garder l'enveloppe est une décision, signée et argumentée. L'événement sort de la file de décisions, mais il y revient automatiquement si une nouvelle source lui est rattachée.
24. **R24 : rien n'est masqué en silence.** Une source écartée d'un calcul (un domicile pris pour un lieu d'événement, par exemple) reste listée et consultable avec la raison de son exclusion. Une exclusion faite par la machine est une proposition (R18) : l'historien peut réintégrer la source.

Règle ajoutée en v0.8 :

25. **R25 : le statut d'une identification est un journal.** Une identification (élément écrit, cible, degré, auteur) ne change jamais ; chaque décision à son sujet (proposer, activer, rejeter) est une ligne nouvelle, et le statut courant est la dernière. Deux contrôles s'appliquent à l'insertion d'une décision : une décision « actif » est refusée si le même élément a déjà une autre identification active (R11 ; il faut d'abord la rejeter), et toute décision autre que « proposé » est refusée si son auteur est un agent (R18 : rejeter est un jugement au même titre qu'activer ; le désaccord d'un agent s'exprime par un INDICE de sens « contre »). L'import d'une base dont l'auteur a déjà identifié ses personnes n'est pas un agent. Une identification retirée par `audit_retractation` (lot remplacé ou annulé, R9) sort de la vue active quel que soit son statut. Appliquée d'abord à IDENT_PERSONNE ; IDENT_EVENEMENT, IDENT_SOURCE et IDENT_LIEU la rejoindront.
26. **R26 : un rapprochement calculé est encadré.** Une identification proposée par un agent est justifiée par au moins un indice calculé (`mode` calculé, `regle_version` renseignée), son degré est « possible » ou « probable », jamais « certain », et elle n'est versée qu'en « proposé » (R18). Un candidat frappé d'un indice « contre » éliminatoire selon le barème en vigueur, ou resté sous le seuil de proposition, n'est pas écrit : il n'apparaît que dans le rapport d'exécution. Un couple masque–personne qui porte déjà une identification, quels qu'en soient le statut et l'auteur, n'est pas reproposé : un rejet humain tient (R24). Le degré est contrôlé à l'insertion ; l'exigence d'un indice l'est par le moteur et ses tests, l'identification étant écrite avant son faisceau.

### 4.6 Exemple : un baptême raconté par deux sources (fictif)

> « Le trois mars mil sept cent douze a été baptisé Jean, fils de Pierre Martin, laboureur, et de Marie Dubois, sa femme. Parrain Jean Leroy, marraine Anne Martin, en présence de Claude Petit, maître d'école, qui a signé. »
> — P1, citation « Registre paroissial de Saint‑Aubin, BMS 1705‑1715 », f° 42 v°

En 1735, un extrait baptistaire est joint au contrat de mariage de Jean : « baptisé le treize mars 1712 en l'église de Saint‑Aubin, fils de Pierre Martin et de Marie Dubois ». C'est le passage P3, dans une minute notariale.

**Couche Source**

| Entité | Instances |
|---|---|
| FACTOIDE | F1 (P1) : baptême, « trois mars 1712 » → [1712‑03‑03], Saint‑Aubin · F3 (P3) : baptême, « treize mars 1712 » → [1712‑03‑13], Saint‑Aubin |
| MASQUE | P1 : M1 Jean · M2 Pierre Martin · M3 Marie Dubois · M4 Jean Leroy · M5 Anne Martin · M6 Claude Petit — P3 : M8 Jean · M9 Pierre Martin · M10 Marie Dubois |
| PARTICIPATION | F1 : M1 baptisé, M2 père, M3 mère, M4 parrain, M5 marraine, M6 témoin · F3 : M8 baptisé, M9 père, M10 mère |
| QUALITE | F1 : M2 laboureur, M6 maître d'école |
| MENTION_LIEU | ML1 « Saint‑Aubin » (F1) · ML3a « l'église » et ML3b « de Saint‑Aubin » (F3, deux mentions selon R17) |

**Couche Interprétation**

| Élément | Contenu |
|---|---|
| SOURCE | S1 registre de Saint‑Aubin (original, A) · S3 minute notariale de 1735 (copie, B) |
| IDENT_EVENEMENT | F1 → E1 certain, actif · F3 → E1 probable, actif (même enfant, mêmes parents, même paroisse) |
| EVENEMENT | E1 baptême, Saint‑Aubin. Intersection des dates vide → **conflit** (R12) |
| CONCLUSION | C5 : « Retenir le 3 mars : F1 est l'original ; F3 est une copie tardive, "trois" probablement lu "treize". » → E1 fixé au 1712‑03‑03 |
| IDENT_PERSONNE | M1, M8 → Jean (P‑020) · M2, M9 → Pierre Martin (P‑017) · M3, M10 → Marie Dubois (P‑018) |
| IDENT_LIEU | ML1, ML3b → paroisse de Saint‑Aubin (LH‑112), probable : trois paroisses homonymes dans la région ; motif « parents domiciliés dans la paroisse selon l'acte notarié » · ML3a → site de l'église paroissiale (ST‑4471) |
| LOCALISATION | LH‑112 → ST‑4471, fonction « église paroissiale », validité jusqu'en 1790 |

Les deux récits restent intacts. Si un chercheur conteste C5, il crée une autre conclusion ; si F3 s'avère décrire un autre enfant, on rejette l'identification F3 → E1 et le conflit disparaît.

Le cas « Pierre Martin, marchand » de la v0.2 fonctionne de même : l'identification M7 → P‑017 est active et « probable » pour un chercheur ; l'avis contraire d'un autre chercheur est conservé en « rejeté » avec son argument (R11).

### 4.7 Correspondances avec les standards

| Entité | CIDOC‑CRM / CRMinf | GEDCOM X | Factoïde (FPO / IPIF) | Bio CRM | IBM i2 (ELP) |
|---|---|---|---|---|---|
| PASSAGE | E33 Linguistic Object (partie de) | SourceReference + locator | Source reference | — | Source reference |
| FACTOIDE | E5 Event documenté (P70i is documented in) ; E13 Attribute Assignment | Event d'un record (niveau persona) | Factoid / Statement | Event (tel que décrit) | Record d'événement |
| MASQUE | E21 Person référencée (P67 refers to) | Persona | Person reference | — | Record d'entité |
| PARTICIPATION | PC14 carried out by + P14.1 in the role of | EventRole | Statement role | Event role | Link type (réifié) |
| MENTION_LIEU | E44 Place Appellation (P1 is identified by) | PlaceReference (champ `original`) | Statement (lieu) | — | Attribut de lieu d'un record |
| QUALITE | E85 Joining / E7 Activity | Fact (Occupation…) | Statement | Enduring unary role | Propriété ou attribut |
| RELATION | — | Relationship | Relationship statement | Enduring binary role | Link type |
| SOURCE | E31 Document | SourceDescription | Source | — | Source d'un record |
| PERSONNE | E21 Person | Person (conclusion) | Person | Person | Item d'entité |
| EVENEMENT | E5 Event reconstitué | Event (conclusion) | — | Event | Item d'événement |
| IDENT_* | I7 Belief Adoption | EvidenceReference (valable pour Person comme pour Event) | same-as / may-be-same-as | — | Fusion de records en un item |
| CONCLUSION | I2 Belief, I5 Inference Making | Attribution + confidence | — | — | Notation + notes d'analyste |
| TYPE / ROLE | E55 Type (P2 has type) | URI de types | Vocabulaires | Classes de rôles | Types du schéma |
| SITE | E53 Place défini par P168 (E94 Space Primitive) ; CRMgeo SP6 Declarative Place | PlaceDescription (latitude, longitude) | Place | Place | Type d'entité « Location » |
| LIEU_HISTORIQUE | E74 Group (institution territoriale) ; E93 Presence pour une emprise datée ; CRMgeo SP2 Phenomenal Place | PlaceDescription (jurisdiction, temporalDescription) | Place | Place | Type d'entité « Location » |

GEDCOM X confirme la symétrie : son *EvidenceReference* s'applique à tout *Subject*, donc aux événements comme aux personnes. Sa *PlaceReference* distingue de même le texte d'origine (`original`) de la description de lieu vers laquelle elle pointe, ce qui correspond au couple MENTION_LIEU / LIEU.

### 4.8 Lieux historiques et sites topographiques

Un même nom de lieu recouvre deux réalités qu'il ne faut pas confondre : un **emplacement physique**, défini par des coordonnées qui ne changent pas, et un **territoire historique**, qui naît, change de nom, de limites et de rattachements, puis disparaît.

| | Site topographique (SITE) | Lieu historique (LIEU_HISTORIQUE) |
|---|---|---|
| Nature | Emplacement défini par des coordonnées dans un système de référence (WGS 84, Lambert‑93). | Territoire ou institution territoriale : paroisse, seigneurie, fief, communauté d'habitants, bailliage, élection, commune, département. |
| Rapport au temps | Immuable. Seule notre connaissance s'affine : une meilleure mesure ajoute une géométrie plus précise, sans effacer l'ancienne. | Daté. Tout ce qui le décrit (noms, limites, rattachements) a une période de validité. |
| Exemples | Emplacement de l'église de Saint‑Aubin ; le lieu-dit la Croix‑Blanche ; un moulin, un gué, une ferme. | Paroisse de Saint‑Aubin sous l'Ancien Régime ; commune de Saint‑Aubin après 1790 ; la commune nouvelle issue d'une fusion. |
| Question résolue | Où, physiquement ? Où est-ce aujourd'hui ? | Sous quelle juridiction, à quelle date ? |
| Couche | Référentiel : c'est une mesure, pas une interprétation. | Interprétation : limites et rattachements sont des reconstructions, souvent approximatives. |

Le site ne porte aucune désignation historique. Dire que tel emplacement est « l'église paroissiale de Saint‑Aubin » est une interprétation : elle est portée par une LOCALISATION, qui relie un lieu historique à un site pour une période.

#### Un lieu historique se décompose en éléments datés

- **NOM_LIEU** : noms successifs ou concurrents, chacun avec sa période et sa langue.
- **EMPRISE** : étendue spatiale sur une période (polygone approximatif, ou point avec un rayon quand les limites sont inconnues), avec sa précision et la conclusion qui la justifie.
- **APPARTENANCE** : rattachement à un autre lieu historique sur une période, **dans une hiérarchie donnée**. Sous l'Ancien Régime, plusieurs hiérarchies coexistent : ecclésiastique (paroisse ⊂ doyenné ⊂ diocèse), judiciaire (⊂ bailliage), fiscale (⊂ élection ⊂ généralité), seigneuriale. Une hiérarchie unique « paroisse ⊂ bailliage ⊂ province » serait fausse. Une paroisse partagée entre deux juridictions de même hiérarchie (paroisse « mi-partie », co-seigneurie) se modélise en créant un lieu historique pour chaque portion, rattaché à la paroisse entière : la contrainte « un seul rattachement par hiérarchie et par période » reste ainsi valable.
- **LOCALISATION** : lien vers un ou plusieurs sites (chef-lieu, église paroissiale, château seigneurial), sur une période.

#### Les évolutions territoriales sont des événements

Créations, fusions, scissions, changements de nom ou de rattachement sont documentés par des sources : ordonnance épiscopale, décret, arrêté préfectoral. Ils entrent donc dans le modèle comme les autres événements : un FACTOIDE tiré de l'acte, un EVENEMENT de type « évolution territoriale ». Les périodes de validité des noms, emprises et appartenances s'appuient sur ces événements et sur les conclusions qui les interprètent. Le modèle s'applique ainsi à sa propre géographie.

#### Résolution des mentions

Une mention de lieu est rattachée à un lieu historique **ou** à un site, selon ce qu'elle désigne :

- « en la paroisse de Saint‑Aubin », « demeurant à Saint‑Aubin » → lieu historique ;
- « au lieu-dit la Croix‑Blanche », « en l'église » → site ;
- « en l'église de Saint‑Aubin » → deux mentions (R17), l'une vers le site, l'autre vers la paroisse.

Les règles R15 à R17 (4.5) encadrent ces rattachements : cohérence avec la date du factoïde, présent calculé et jamais saisi, une mention pour un seul référent.

#### Deux questions, deux chemins

| Question | Chemin dans le modèle |
|---|---|
| Où ce baptême a-t-il eu lieu, sur une carte d'aujourd'hui ? | Mention → site (ou emprise du lieu historique) → coordonnées → commune actuelle, GeoNames. |
| De quelle juridiction relevait le lieu de ce baptême en 1712 ? | Mention → lieu historique → appartenances valables en 1712, hiérarchie par hiérarchie. |
| Dans quelle paroisse se trouvait ce moulin en 1712 ? | Site → emprises valables en 1712 qui le contiennent (projection spatiale). |

#### Référentiels externes

- **Sites :** coordonnées IGN ou GeoNames pour les lieux actuels ; géoréférencement des cartes anciennes (Cassini, cadastre napoléonien) pour les emplacements disparus.
- **Lieux historiques :** Pleiades pour l'Antiquité (lieu, localisations et noms, chacun daté) ; World Historical Gazetteer et son Linked Places Format, qui datent noms, géométries et relations ; en France, la base « Des villages de Cassini aux communes d'aujourd'hui » (EHESS) et l'historique du Code officiel géographique de l'INSEE pour les fusions et changements de nom des communes.


---

## 5. Import depuis GeneWeb

GeneWeb stocke des **conclusions** : une personne, ses dates, ses familles. Notre modèle stocke d'abord **ce que disent les sources**. L'import reconstruit la couche Source à partir de ce que GeneWeb a retenu, sans jamais inventer de passage.

### 5.1 Le modèle GeneWeb en bref

| Élément | Représentation GeneWeb |
|---|---|
| Personne | Clé `Nom Prénom.occ` (le numéro d'occurrence distingue les homonymes). Nom public `(…)`, alias de prénom `{…}`, `#salias`, `#alias`, `#nick`, `#occu`, titres `[titre:lieu:début:fin:n]`, accès `#apubl` / `#apriv`. |
| Famille | Bloc `fam` : couple, mariage (`#mp` lieu, `#ms` source), témoins `wit`, source `src`, enfants entre `beg` et `end`. Statuts `#nm`, `#eng`, `#sep`, divorce `-`. |
| Événements | `pevt` (`#birt`, `#bapt`, `#deat`, `#buri`, `#crem`, `#occu`, `#resi`, `#cens`, `#will`, `#educ`, `#mser`…) et `fevt` (`#marr`, `#marb`, `#marc`, `#enga`, `#div`, `#sep`, `#anul`, `#resi`…). Chacun porte date, `#p` lieu, `#s` source, note et témoins. |
| Témoins | Tableau `(personne × witness_kind)` sur chaque événement. Types en 7.1 : `Witness`, `Witness_GodParent`, `Witness_CivilOfficer`, `Witness_ReligiousOfficer`, `Witness_Informant`, `Witness_Attending`, `Witness_Mentioned`, `Witness_Other`. |
| Relations | Bloc `rel` : `adop` (adoption), `reco` (reconnaissance), `cand` (parent candidat), `godp` (parrain), `fost` (nourricier), côté père ou mère. |
| Dates | `~` environ, `?` peut-être, `<` avant, `>` après, `\|` ou, `..` entre ; calendriers `J` julien, `F` républicain, `H` hébraïque ; date en texte libre. |
| Sources, lieux | Chaînes de caractères libres, sans entité ni hiérarchie. |
| Notes | `notes` par personne, `comm` par famille, notes d'événement, pages wiki avec liens `[[…]]`. |

### 5.2 Écarts avec notre modèle

| Notion | GeneWeb | Traitement en v0.3 |
|---|---|---|
| Masque | Absent : un témoin est une personne à part entière. | Un masque par personne et par passage cité, rattaché à sa personne par une IDENT_PERSONNE « certain » du lot. |
| Source | Chaîne libre par événement ou famille. | Chaque chaîne devient un PASSAGE (`citation_brute`). Le regroupement vers les SOURCE canoniques passe par IDENT_SOURCE (voir 5.5). |
| Événement | Une seule version par événement. | Chaque événement GeneWeb donne un FACTOIDE et un EVENEMENT, reliés par une IDENT_EVENEMENT « certain ». Les rapprochements avec d'autres lots ou sources deviennent des identifications proposées. |
| Lieu | Chaîne libre, souvent « lieu-dit, commune, département, pays », le plus souvent avec les noms **actuels**. | Chaque chaîne devient une MENTION_LIEU de désignation « moderne ». Elle est rattachée à la commune actuelle (correspondance unique → « certain », sinon « proposé »). Le lieu historique de l'événement (la paroisse à la date de l'acte) est déduit par projection spatiale : site du chef-lieu de la commune, puis emprise valable à la date. Il reste « proposé » tant qu'une source contemporaine ne le confirme pas. |
| Contradictions | Une seule valeur retenue par champ. | Aucune à l'import ; elles apparaissent quand d'autres sources sont rattachées aux mêmes événements. |
| Parenté | Implicite (enfant d'une famille), pas toujours sourcée. | RELATION « fils/fille de » portée par un factoïde issu de `csrc` ou `src`, à défaut par la source de repli de la base. |

### 5.3 Table de correspondance

| GeneWeb | Entités cibles | Règle |
|---|---|---|
| `Nom Prénom.occ` | PERSONNE + MASQUE(s) + NOM | Clé `nom/prénom/occ` gardée en `cle_externe` du masque pour les réimports : `gw:pers:{nom}_{prénom}_{occ}`. La PERSONNE porte la même clé en `ref` : une personne par clé, à laquelle sont rattachés tous les masques de la clé (décision 19) ; son `cle_externe` reste aux référentiels d'autorité. Une famille : `gw:fam:{clé du père}__{clé de la mère}` (`inconnu` si un parent manque) ; un passage : `gw:pass:{empreinte courte}:{ligne_debut}_{ligne_fin}`. |
| `(public)`, `{alias}`, `#salias`, `#nick` | NOM | Une ligne par forme, avec son type. |
| `pevt` naissance, baptême, décès… | FACTOIDE + PARTICIPATION + EVENEMENT + IDENT_EVENEMENT | Rôle principal selon le type : né, baptisé, décédé, inhumé. |
| `fam` + `fevt #marr`… | FACTOIDE + 2 PARTICIPATION + EVENEMENT | Rôles époux / épouse ; un type par tag : `contrat_mariage` (`#marc`), `bans_mariage` (`#marb`), `licence_mariage` (`#marl`), `non_mariage` (`#nmar`), `non_mention` (`#nmen`), `annulation` (`#anul`), `pacs`, `residence` (`#resi`), `separation`, `engagement` ; tag inconnu : type libre à l'écriture d'origine, jamais ignoré. Témoins, `wnote` et notes conservés. Famille sans conjoint connu : `gw:fam:inconnu__inconnu:{premier enfant}`. |
| Témoin (`witness_kind`) | PARTICIPATION sur le factoïde | Voir 5.4. |
| `Witness_Informant` | PARTICIPATION + `FACTOIDE.declarant` | L'informateur est aussi la voix du factoïde (R7). |
| `#occu` | QUALITE (profession) | Sans dates : validité inconnue. |
| `[titre:lieu:début:fin:n]` | QUALITE (titre) | Intervalle, lieu et rang conservés. |
| `rel adop/reco/cand/godp/fost` | RELATION | `cand` : relation de degré « possible ». |
| Enfants d'une famille | RELATION fils/fille de | Factoïde issu de `csrc` ou `src`. |
| `notes`, `comm`, note d'événement | CONCLUSION ou PASSAGE.transcription | Une note qui argumente devient une conclusion ; une transcription reste dans le passage. |
| `#apubl` / `#apriv` | `PERSONNE.acces` | À respecter à l'export et à l'affichage. |
| Décès `k`/`m`/`e`/`s` | Sous-type d'événement | Tué, assassiné, exécuté, disparu. |

### 5.4 Témoins : de `witness_kind` aux rôles

| `witness_kind` | Rôle de participation | Équivalents |
|---|---|---|
| `Witness` | témoin | GEDCOM X Witness, CIDOC P11 |
| `Witness_GodParent` | parrain ou marraine selon le sexe | Rôle de participation Bio CRM |
| `Witness_CivilOfficer` | officier d'état civil | GEDCOM X Official |
| `Witness_ReligiousOfficer` | célébrant | GEDCOM X Official |
| `Witness_Informant` | déclarant | + `FACTOIDE.declarant` |
| `Witness_Attending` | présent | GEDCOM X Participant |
| `Witness_Mentioned` | mentionné | Masque cité, sans rôle actif |
| `Witness_Other` | autre, à qualifier | File de revue |

### 5.5 Sources : des chaînes brutes aux sources canoniques

Dans une base GeneWeb, les chaînes de source sont très répétitives : chaque auteur applique ses propres conventions, et l'on compte en général quelques centaines de chaînes distinctes pour des dizaines de milliers de personnes. Pas besoin de traitement automatique du langage lourd.

1. **Découper** chaque chaîne en partie « document » et partie « localisation » avec quelques expressions régulières propres à la base (`f°42v`, `p. 12`, `acte n° 34`, `vue 118`).
2. **Regrouper** les parties « document » par similarité (empreinte normalisée, puis distance d'édition), comme le fait OpenRefine.
3. **Rattacher** : regroupement exact → IDENT_SOURCE « certain » actif ; regroupement approché → « probable » proposé, dans la file de décisions.
4. **Garder les orphelines** : une chaîne non rattachée reste un passage sans source canonique, visible dans une liste dédiée. Rien n'est perdu.

L'interface de fusion des sources est la même que pour les personnes et les événements (section 6).

### 5.6 Dates : de la précision GeneWeb aux intervalles du factoïde

| Précision GeneWeb | Exemple | `date_min` | `date_max` | Remarque |
|---|---|---|---|---|
| Sure | `3/3/1712` | 1712‑03‑03 | 1712‑03‑03 | Précision au jour |
| About `~` | `~1712` | 1707 | 1717 | Fenêtre paramétrable (ici ±5 ans) |
| Maybe `?` | `?1712` | 1712 | 1712 | Crédibilité du factoïde abaissée |
| Before `<` | `<1712` | vide | 1711‑12‑31 | Borne ouverte |
| After `>` | `>1712` | 1713‑01‑01 | vide | Borne ouverte |
| OrYear `\|` | `1712\|1713` | 1712 | 1713 | Alternative stricte notée dans l'énoncé |
| YearInt `..` | `1710..1715` | 1710 | 1715 | Intervalle direct |
| Calendrier | `12/3/1712J` | converti en grégorien | | `calendrier` = julien, texte d'origine gardé |
| Date texte | `0(Pâques 1712)` | vide ou estimée | | Texte dans `date_declaree` |

### 5.7 Exemple d'import

Extrait `.gw` illustratif, tel qu'un export `gwu` pourrait le produire :

```text
fam MARTIN Pierre +1705 #mp Saint-Aubin DUBOIS Marie
src BMS Saint-Aubin 1705-1715
beg
- h Jean 3/3/1712 #bp Saint-Aubin
end

pevt MARTIN Jean
#bapt 3/3/1712 #p Saint-Aubin #s BMS Saint-Aubin f°42v
wit m: LEROY Jean
end pevt
```

| Entité | Instances créées |
|---|---|
| LOT_IMPORT | L1 · gw · gwu 7.1 · 28/09/2026 |
| PASSAGE | P1 « BMS Saint-Aubin f°42v » · P0 « BMS Saint-Aubin 1705-1715 » |
| SOURCE + IDENT_SOURCE | S1 « BMS Saint-Aubin 1705-1715 » ← P0 (certain) et P1 (certain, même partie « document ») |
| FACTOIDE | F1 baptême [1712‑03‑03], Saint‑Aubin (P1) · F0 mariage [1705], Saint‑Aubin (P0) |
| MASQUE | P1 : M1 Jean MARTIN, M4 Jean LEROY · P0 : M2 Pierre MARTIN, M3 Marie DUBOIS |
| MENTION_LIEU + IDENT_LIEU | « Saint-Aubin » (F1 et F0), désignation moderne → commune actuelle ; paroisse de 1705‑1712 déduite par projection spatiale, en « proposé » |
| PARTICIPATION | F1 : M1 baptisé, M4 témoin (ou parrain si `witness_kind` = GodParent) · F0 : M2 époux, M3 épouse |
| EVENEMENT + IDENT_EVENEMENT | E1 ← F1 · E0 ← F0 (certain, lot L1) |
| IDENT_PERSONNE | M1 → MARTIN/Jean/0 · M2 → MARTIN/Pierre/0 · … (certain, lot L1) |

### 5.8 Chaîne d'import

1. **Extraire.** Lire la base `.gwb` en OCaml avec la bibliothèque de GeneWeb (option A, sans perte), ou analyser l'export `gwu` (option B). Le GEDCOM de `gwb2ged` reste un plan C : il risque d'aplatir les types de témoins et les notes.
2. **Normaliser.** Dates en intervalles, graphies de lieux, chaînes de source découpées (5.5). Les cas ambigus partent dans la file de décisions.
3. **Charger la couche Source.** Passages, factoïdes, masques, participations, qualités, relations, noms, tous rattachés au lot.
4. **Créer les identifications du lot.** Une personne par clé GeneWeb, un événement par factoïde, une source par groupe exact, un lieu par correspondance unique, toutes « certain » et attribuées au lot.
5. **Rapprocher avec l'existant.** Les correspondances avec les personnes, événements, sources et lieux déjà en base sont créées en « proposé » et entrent dans la file de décisions.
6. **Réimporter sans doublon.** La `cle_externe` et l'empreinte du fichier permettent de comparer deux lots et de n'appliquer que les différences. Le différentiel est décrit par la décision 16 ; ses effets sur les identifications de personnes, par la décision 19.

L'export inverse vers GeneWeb est possible mais appauvrissant : une seule valeur par champ, masques fusionnés, incertitude réduite aux symboles de précision. On exporte les vues fondées sur les identifications actives.

---

## 6. Interface de validation

L'enjeu est de laisser l'historien trancher sans le noyer sous les masques. Principe : **il ne parcourt jamais les masques, c'est l'interface qui lui propose des décisions**. Grâce à la symétrie du modèle, le même écran sert aux quatre agrégations (sources, personnes, événements, lieux). Pour les lieux, la frise est remplacée par une carte des candidats, avec un curseur de date qui affiche les emprises et les rattachements valables à la date du factoïde.

1. **File de décisions.** Le système calcule des candidats en croisant plusieurs indices : proximité des noms, compatibilité des dates, distance des lieux, proches en commun. Il les classe par impact. Les identifications « certain » d'un import n'apparaissent pas, sauf en cas de conflit.
2. **Comparaison côte à côte, écarts seulement.** Deux fiches en colonnes : les champs concordants sont repliés, les divergences surlignées avec leur source et leur notation. Chaque indice du score est affiché (« même paroisse », « parrain commun »).
3. **Frise chronologique.** Une ligne de vie par candidat, dans l'esprit des *theme lines* d'i2, avec les incohérences signalées : baptisé après son décès, présent dans deux lieux le même jour, âge impossible.
4. **Décision par groupes.** L'historien valide un ensemble de masques ou de factoïdes en une fois, et peut en détacher un seul.
5. **Argumentation en un geste.** Chaque décision propose des motifs prédéfinis (mêmes parents, même métier et même lieu, signature identique, original préféré à la copie) plus un champ libre. La conclusion est créée automatiquement.
6. **Affichage dosé.** Masques groupés par source et repliés par défaut, avis rejetés masqués mais consultables, trois à cinq candidats à la fois.
7. **Annulation.** Toute décision se défait : elle ne fait que changer le statut d'une identification (R4).

Ces principes reprennent les réflexes des outils de rapprochement comme OpenRefine ou Mix'n'match. L'écran de saisie et de validation qui précède cette file est décrit en 7.4.

### 6.1 Les cinq écrans de la maquette

| Écran | Rôle | Éléments clés |
|---|---|---|
| 1. Dépôt et lecture à voix haute | Lire le document | Ligne en cours encadrée sur l'image, enregistrement, alignement mot à mot entre écriture et voix (6.2). |
| 2. Saisie et validation d'un acte | Vérifier le brouillon | Image, transcription et fiche pré-remplie liées au mot ; seuls les champs incertains ou déduits demandent une action. |
| 3. Rattachements proposés | Trancher les identifications | File de décisions, comparaison côte à côte, détail du score, frise qui élimine les candidats impossibles, motifs en un clic. |
| 4. Conflit de date | Trancher entre des dates | Une ligne par source, cœur et halo, hypothèses vérifiées (6.3). |
| 5. Conflit de lieu | Trancher entre des lieux | Carte à la date de l'événement, frise liée, verdict selon la date (6.4). |

### 6.2 Alignement mot à mot entre écriture et voix

- **Vue en partition** : une case par mot, l'écriture en haut, la voix en bas ; un seul mot quand les deux s'accordent.
- **Comparaison après normalisation** (abréviations développées, orthographe modernisée), pour que seules les vraies différences ressortent.
- **Quatre états**, distingués par la couleur, le trait et la clarté : accord ; écart attendu entre graphie et lecture ; écriture peu sûre complétée par la voix ; divergence à trancher.
- **Résumé en tête** (mots, accords, écarts, divergences) et réécoute du passage exact de l'enregistrement pour chaque divergence.

### 6.3 Conflit de date

- **Une ligne par source** sur un axe commun, avec la date telle qu'écrite. Trait plein pour un original, hachures pour une copie, bande estompée pour un témoignage. Une date qui déborde l'échelle est signalée par des flèches.
- **Regroupement** : les sources parfaitement concordantes partagent une ligne, avec un badge « ×n » qu'on peut déplier.
- **Ligne « événement calculé »** : le cœur (intersection) en aplat foncé, le halo (union) en aplat clair ; en cas de conflit, pas de cœur et l'écart est affiché.
- **Hypothèses vérifiées** : décalage de calendrier, naissance prise pour le baptême, erreur de copie, biais de mémoire (source très postérieure, formule arrondie comme « il y a environ vingt ans »).
- **Échelle adaptée** à l'écart en jeu : jour, mois ou année.

### 6.4 Conflit de lieu et carte liée à la date

- **Deux conflits distincts** : quel lieu désigne ce nom (identité, candidats côte à côte) ; où l'événement a eu lieu (géométrie, cœur et halo).
- **Territoires à la date de l'événement**, jamais la commune actuelle (R16).
- **Cœur et halo** calculés par PostGIS ; sans zone commune, un trait ocre au plus court avec la distance. Un emboîtement (une paroisse dans son bailliage, une église dans sa paroisse) s'affiche comme « précisions compatibles ». Une intersection de zones approximatives reste affichée comme approximative.
- **Lisibilité** : une seule couche en couleur, celle de la décision ; un seul fond à la fois (moderne atténué, Cassini, aucun) et un rideau pour comparer ; sources en contours seuls, allumés au survol ; une seule façon de montrer l'incertitude (bords estompés) ; petites cartes au-delà de trois sources ; points et rayons en vue éloignée ; contrôle en niveaux de gris.
- **Lien avec la date** : sous la carte, une frise à deux lignes, date de l'événement et géographie. La géographie est découpée en périodes stables séparées par des losanges (changements de territoire). Le curseur et l'étiquette « Carte au … » partagent une couleur réservée à ce lien. Si un changement tombe dans l'intervalle de dates possibles, le curseur s'ouvre juste avant et la carte montre le territoire suivant en fantôme.

### 6.5 Incertitude assumée (« garder l'enveloppe »)

Quand un conflit ne peut pas être tranché, l'historien peut le dire. C'est une décision (R23), pas un abandon.

- **Dans les données** : une conclusion de valeur « incertain », dont l'effet marque l'événement en « incertitude assumée ». Aucun lieu ni aucune date n'est retenu à la place de l'enveloppe ; les identifications restent « proposé ».
- **Sur l'écran** : l'étiquette ocre « conflit » devient une étiquette grise « incertitude assumée », avec l'auteur et la date. Le halo reste, sans cœur ; le trait de distance passe de l'ocre au gris (« écart documenté »). Le panneau de décision est remplacé par le résumé de la conclusion et un bouton « Rouvrir ».
- **Ailleurs dans l'outil** : sur la carte de vie d'une personne, l'événement s'affiche comme une zone (le halo), jamais comme un point. Dans les comptages par territoire, il est rangé à part (« lieu incertain ») plutôt qu'attribué en silence à l'une des hypothèses. Une requête par juridiction renvoie toutes les hypothèses, signalées comme telles.
- **Réveil** : rattacher une nouvelle source à l'événement le renvoie dans la file de décisions, avec la conclusion précédente affichée.
- **Export** : vers GeneWeb, le lieu est écrit sous forme d'alternative (« Saint‑Aubin ou Les Essarts ») avec une note. Vers CIDOC‑CRM, chaque hypothèse devient une proposition CRMinf de valeur « incertain ».

### 6.6 Sources hors calcul

Une source écartée du calcul, par exemple un contrat de mariage qui donne le domicile et non le lieu du mariage, n'est jamais effacée (R24).

- **Dans la liste des sources** : barrée, grisée, avec la raison en clair (« domicile, pas lieu du mariage : hors calcul ») et un bouton « Réintégrer ».
- **Sur la carte et la frise** : absente par défaut. Au survol, elle apparaît en contour gris très fin, sans aplat ni couleur, avec la même raison en étiquette.
- **Traçabilité** : l'exclusion est une proposition de la machine, attribuée à son agent, que l'historien confirme ou annule.

---

## 7. Saisie assistée par modèles de langage

Principe : **l'utilisateur fournit le document, la machine prépare, l'humain décide.** Le but est d'obtenir une base aussi complète que possible sans la fatigue de saisie qui, champ après champ, finit par en dégrader la qualité.

Le modèle s'y prête naturellement : ce qu'une machine sait extraire correspond exactement à la couche Source (texte tel qu'écrit, masques, rôles, dates et lieux déclarés). Les rattachements aux personnes, événements, sources et lieux restent des décisions humaines (R13).

### 7.1 Le circuit

| Étape | Entrée | Traitement | Sortie |
|---|---|---|---|
| 1. Dépôt | Image, PDF ou texte | PDF avec couche texte : lecture directe. Scan : reconnaissance d'écriture (HTR) avec des modèles entraînés sur les écritures anciennes (eScriptorium, Kraken, Transkribus). Découpage de la page en actes. | Transcription machine et zones de l'image |
| 2. Lecture à voix haute (facultative) | Audio | L'utilisateur lit le passage ; reconnaissance vocale. | Lecture humaine |
| 3. Confrontation | Transcription machine et lecture | Alignement mot à mot ; les divergences sont signalées. | Transcription consolidée, qui garde la graphie et la lecture |
| 4. Extraction | Transcription consolidée | Modèle de langage à sortie structurée, contrainte par le schéma, avec un gabarit par type d'acte (baptême, mariage, sépulture, contrat…). | Brouillon : factoïde, masques, participations, qualités, relations, mentions de lieu, dates déclarées, chacun ancré dans le texte |
| 5. Suggestions | Brouillon et base existante | Calcul de score (noms, dates, lieux, réseau) ; le modèle de langage explique les candidats en clair. | Identifications « proposé » |
| 6. Validation | Brouillon et suggestions | Écran en trois colonnes (7.4). | Versement dans la couche Source ; décisions d'identification |

La lecture à voix haute est l'apport le plus fort de ce circuit : un paléographe lit plus vite qu'il ne tape, et la confrontation entre la reconnaissance d'écriture et la voix désigne d'elle-même les mots douteux. La voix donne toutefois une *lecture* (abréviations développées, orthographe modernisée) et non la *graphie* : on garde les deux, et l'image reste la preuve.

### 7.2 Des modèles spécialisés, derrière une passerelle commune

Plutôt qu'un seul modèle polyvalent, une chaîne de modèles spécialisés : écriture, voix, extraction. Chaque étape se mesure, se remplace et s'améliore séparément. Toutes passent par une **passerelle de modèles** qui fixe le contrat d'entrée et de sortie (schéma JSON) ; le choix du modèle concret (service en ligne, petit modèle local) relève de la configuration, pas du code.

Les registres paroissiaux sont très formulaires : un petit modèle bien guidé suffit en général à l'extraction. Les actes notariés et les sources narratives demanderont des modèles plus capables.

### 7.3 Déploiement hybride

| Composant | Où | Pourquoi |
|---|---|---|
| Base PostgreSQL, droits, file de décisions, images | Serveur local de l'équipe | Évite la complexité de la gestion des droits en ligne ; les données restent sous contrôle. |
| Reconnaissance d'écriture | Serveur local (idéalement avec GPU) ou service en ligne | Traitement lourd, par lots. |
| Reconnaissance vocale et extraction | Service en ligne par défaut ; petits modèles en local sur un poste puissant (ordinateur à mémoire unifiée importante) ou sur le serveur | Choix par configuration, grâce à la passerelle. |

Le système reste agnostique : un même projet peut combiner les trois modes.

**Garde-fou avant tout envoi externe.** Les personnes étudiées sont en principe décédées, et le RGPD ne s'applique pas aux défunts. Trois cas imposent pourtant un filtre :

- Les bases importées, GeneWeb en tête, contiennent souvent des **personnes vivantes** (marquées privées, ou sans date de décès et nées il y a moins d'un siècle environ).
- Les **délais de communicabilité** du Code du patrimoine protègent les documents récents : de l'ordre de 75 ans pour les actes de naissance et de mariage et pour les minutes notariales. À vérifier avec un juriste.
- Les **conditions de réutilisation** des images fixées par certains services d'archives.

Ces documents et ces personnes sont traités en local uniquement (R21).

### 7.4 L'écran de saisie et de validation

- **Trois colonnes** : l'image avec les zones repérées, la transcription, la fiche pré-remplie.
- **Traçabilité au mot** : cliquer un champ surligne les mots dans la transcription et la zone dans l'image, et inversement.
- **Attention ciblée** : seuls les champs peu sûrs, déduits ou divergents entre voix et écriture sont mis en évidence ; le reste se valide acte par acte, en un geste.
- **Correction à la voix** : « le parrain s'appelle Leroy, L‑E‑R‑O‑Y ».
- **Enchaînement** : après validation de l'acte, l'écran passe aux suggestions de rattachement (file de décisions, section 6).
- **Boucle d'amélioration** : chaque correction est journalisée et sert à évaluer et à améliorer les modèles.

### 7.5 Ce que la saisie assistée ajoute au modèle

| Ajout | Contenu |
|---|---|
| Zone de brouillon (schéma `saisie`) | La couche Source étant en insertion seule, l'extraction écrit dans un brouillon. Un LOT_SAISIE (document, statut : en cours, validé, abandonné) regroupe ses éléments. La validation les verse en une transaction dans le schéma `source`. |
| Ancrage | `ancre_debut` et `ancre_fin` (positions dans la transcription) et `zone_image` (polygone) sur les masques, mentions de lieu, participations et dates déclarées. |
| Transcriptions de PASSAGE | `transcription_machine`, `lecture_orale`, `transcription_validee`. |
| Contributeur « agent » | CONTRIBUTEUR de type agent, avec modèle, version, gabarit et paramètres : on sait toujours qui a proposé quoi. |
| Confiance d'extraction | Score de 0 à 1 porté par chaque élément du brouillon, distinct de la crédibilité de la source (R6). |
| Lu ou déduit | Indicateur `mode` sur les relations, qualités et dates : lu dans le texte, ou déduit (« sa femme », « l'an que dessus »). |
| Journal des corrections | Pour chaque champ : valeur proposée, valeur retenue, auteur. Sert de jeu d'évaluation. |

### 7.6 Règles de la saisie assistée

18. **R18 : la machine propose, l'humain verse.** Aucun élément extrait n'entre dans la couche Source sans validation humaine, et aucune identification créée par un agent n'est « actif ». Un agent ne verse que des propositions : il n'active ni ne rejette une identification, il apporte des indices (R25).
19. **R19 : pas d'élément sans ancrage.** Tout élément extrait cite sa position dans la transcription ; sans ancrage, il est rejeté automatiquement. C'est la parade contre les inventions.
20. **R20 : lu ou déduit.** Un élément déduit est marqué comme tel et n'est jamais pré-validé.
21. **R21 : filtre avant envoi externe.** Documents sous délai de communicabilité, personnes possiblement vivantes et images à réutilisation restreinte ne quittent pas le serveur local.

### 7.7 Risques

| Risque | Parade |
|---|---|
| Inventions (un parrain inexistant) | Ancrage obligatoire (R19). |
| Déductions présentées comme lues | Indicateur lu ou déduit (R20). |
| Validation machinale : l'utilisateur accepte tout, trop vite | Champs incertains qui exigent une action ; une part des actes validés est présentée à nouveau pour contrôle par sondage ; taux de correction suivi par utilisateur. |
| Dates (calendrier julien, « l'an que dessus », fêtes religieuses) | Toujours signalées pour vérification. |
| Confusion entre graphie et lecture | Les deux sont conservées ; `nom_ecrit` suit la graphie vérifiée sur l'image. |

---

## 8. Implémentation : PostgreSQL et OCaml

### 8.1 Choix d'architecture

- **PostgreSQL pour le cœur.** Tout est réifié : une participation est une ligne, qu'une conclusion peut désigner. Une base de graphe n'apporte donc pas d'avantage décisif, car dans Neo4j un lien ne peut pas pointer vers un autre lien et la participation y serait de toute façon un nœud. PostgreSQL garantit l'intégrité transactionnelle de la couche Source.
- **Quatre schémas.** `saisie` (brouillons de la saisie assistée), `source` (insertion seule), `interp` (révisable, lieux historiques compris), `ref` (référentiels, sites compris). Les droits de modification et de suppression sont retirés sur `source`.
- **PostGIS** pour les géométries des sites et des emprises, et **btree_gist** pour interdire les chevauchements de périodes.
- **Deux systèmes de coordonnées.** Stockage en WGS 84 (EPSG:4326), pour l'échange avec GeoNames, le World Historical Gazetteer et les fonds de carte. Calculs de distance, de surface, d'intersection et de zones tampons en Lambert‑93 (EPSG:2154) pour la France métropolitaine, par transformation à la volée ou colonne calculée indexée. Un projet hors métropole (outre-mer, étranger) déclare son propre système métrique, par exemple la zone UTM adaptée.
- **Vues pour les calculs.** Participants d'un événement, intervalle d'un événement, fiche consolidée ; en vues matérialisées si le volume l'exige.
- **Projection en graphe pour l'analyse.** Apache AGE (extension de graphe pour PostgreSQL) ou un export vers Neo4j en lecture seule, pour la centralité et les plus courts chemins sur le réseau de personnes.
- **Backend Python** pour l'API, la file de décisions et la publication RDF (CIDOC‑CRM, avec PC14 pour les participations).
- **OCaml pour le connecteur GeneWeb** (8.3).
- **Passerelle de modèles** pour la saisie assistée, et déploiement hybride (section 7).

### 8.2 Esquisse SQL

Esquisse non testée, pour fixer les idées.

```sql
-- Couche Source : insertion seule
CREATE TABLE source.factoide (
  id                  bigserial PRIMARY KEY,
  passage_id          bigint NOT NULL REFERENCES source.passage,
  type_evenement_id   int REFERENCES ref.type_evenement,
  enonce              text,
  date_declaree       text,
  date_brute          text,   -- chaîne telle qu'écrite dans la source (R13)
  cle_famille         text,   -- gw:fam:{père}__{mère}, import GeneWeb
  date_min            date,
  date_max            date,
  calendrier          text,
  declarant_masque_id bigint REFERENCES source.masque,
  credibilite         smallint CHECK (credibilite BETWEEN 1 AND 6),
  remplace_id         bigint REFERENCES source.factoide,
  lot_import_id       int REFERENCES ref.lot_import,
  saisi_par           int NOT NULL REFERENCES ref.contributeur,
  saisi_le            timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE source.mention_lieu (
  id              bigserial PRIMARY KEY,
  factoide_id     bigint NOT NULL REFERENCES source.factoide,
  forme_ecrite    text NOT NULL,
  forme_normalisee text,
  fonction        text NOT NULL,  -- evenement, domicile, origine, titre
  masque_id       bigint REFERENCES source.masque
);

CREATE TABLE source.participation (
  id          bigserial PRIMARY KEY,
  factoide_id bigint NOT NULL REFERENCES source.factoide,
  masque_id   bigint NOT NULL REFERENCES source.masque,
  role_id     int NOT NULL REFERENCES ref.role,
  ordre       smallint
);

REVOKE UPDATE, DELETE ON ALL TABLES IN SCHEMA source FROM app_user;

-- Structure d'identification commune, déclinée trois fois
CREATE TYPE degre AS ENUM ('certain', 'probable', 'possible');
CREATE TYPE statut_ident AS ENUM ('propose', 'actif', 'rejete');

CREATE TABLE interp.ident_evenement (
  id            bigserial PRIMARY KEY,
  factoide_id   bigint NOT NULL REFERENCES source.factoide,
  evenement_id  bigint NOT NULL REFERENCES interp.evenement,
  degre         degre NOT NULL,
  statut        statut_ident NOT NULL,
  conclusion_id bigint NOT NULL REFERENCES interp.conclusion,
  lot_import_id int REFERENCES ref.lot_import
);
-- R11 : une seule identification active par factoïde
CREATE UNIQUE INDEX ident_evenement_actif
  ON interp.ident_evenement (factoide_id) WHERE statut = 'actif';
-- interp.ident_source (passage_id → source_id) et
-- interp.ident_lieu (mention_lieu_id → lieu_historique_id ou site_id) : même structure

-- Identification de personne (v0.8, R25) : la proposition est immuable,
-- les décisions forment un journal ; le statut courant est la dernière.
CREATE TABLE interp.ident_personne (
  id              bigserial PRIMARY KEY,
  masque_id       bigint NOT NULL REFERENCES source.masque,
  personne_id     bigint NOT NULL REFERENCES interp.personne,
  degre           degre NOT NULL,
  contributeur_id int NOT NULL REFERENCES ref.contributeur,
  lot_import_id   int REFERENCES ref.lot_import,
  date            timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE interp.ident_personne_statut (
  id              bigserial PRIMARY KEY,
  ident_id        bigint NOT NULL REFERENCES interp.ident_personne,
  statut          statut_ident NOT NULL,
  conclusion_id   bigint REFERENCES interp.conclusion,
  contributeur_id int NOT NULL REFERENCES ref.contributeur,
  date            timestamptz NOT NULL DEFAULT now()
);
CREATE VIEW interp.ident_personne_actif AS
SELECT ip.*
FROM interp.ident_personne ip
JOIN LATERAL (SELECT s.statut FROM interp.ident_personne_statut s
              WHERE s.ident_id = ip.id ORDER BY s.id DESC LIMIT 1) d ON true
WHERE d.statut = 'actif'
  AND NOT EXISTS (SELECT 1 FROM audit.retractation r
                  WHERE r.cible_table = 'interp.ident_personne' AND r.cible_id = ip.id);
-- R11 (décision « actif ») et R18 (agent : « proposé » seulement) : triggers à l'insertion

-- Vue : participants d'un événement (R8)
CREATE VIEW interp.participant_evenement AS
SELECT ie.evenement_id, ip.personne_id, p.role_id, p.factoide_id
FROM interp.ident_evenement ie
JOIN source.participation p   ON p.factoide_id = ie.factoide_id
JOIN interp.ident_personne_actif ip ON ip.masque_id = p.masque_id
WHERE ie.statut = 'actif';

-- Vue : intervalle et conflit de date d'un événement (R5, R12)
CREATE VIEW interp.intervalle_evenement AS
SELECT ie.evenement_id,
       max(f.date_min) AS debut_min,
       min(f.date_max) AS debut_max,
       max(f.date_min) > min(f.date_max) AS conflit
FROM interp.ident_evenement ie
JOIN source.factoide f ON f.id = ie.factoide_id
WHERE ie.statut = 'actif'
GROUP BY ie.evenement_id;
```

**Lieux (PostGIS)**, esquisse non testée :

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Site : coordonnées immuables, insertion seule
CREATE TABLE ref.site (
  id             serial PRIMARY KEY,
  libelle_neutre text,
  geom           geometry(Point, 4326) NOT NULL,
  rayon_incertitude_m numeric,
  methode        text,            -- releve, carte ancienne, cadastre
  remplace_id    int REFERENCES ref.site
);

CREATE TABLE interp.lieu_historique (
  id        serial PRIMARY KEY,
  type      text NOT NULL,        -- paroisse, seigneurie, bailliage, commune…
  existence daterange
);

-- Une seule emprise par lieu et par période
CREATE TABLE interp.emprise (
  id                 serial PRIMARY KEY,
  lieu_historique_id int NOT NULL REFERENCES interp.lieu_historique,
  validite           daterange NOT NULL,
  geom               geometry(MultiPolygon, 4326),  -- limites connues
  centre             geometry(Point, 4326),         -- sinon : chef-lieu
  rayon_incertitude_m numeric,                      -- et rayon
  precision          text,
  CHECK (geom IS NOT NULL OR centre IS NOT NULL),
  conclusion_id      bigint REFERENCES interp.conclusion,
  EXCLUDE USING gist (lieu_historique_id WITH =, validite WITH &&)
);

-- Un seul rattachement par lieu, par hiérarchie et par période
CREATE TABLE interp.appartenance (
  id            serial PRIMARY KEY,
  partie_id     int NOT NULL REFERENCES interp.lieu_historique,
  tout_id       int NOT NULL REFERENCES interp.lieu_historique,
  hierarchie    text NOT NULL,    -- ecclesiastique, judiciaire, fiscale, seigneuriale, administrative
  validite      daterange NOT NULL,
  conclusion_id bigint REFERENCES interp.conclusion,
  EXCLUDE USING gist (partie_id WITH =, hierarchie WITH =, validite WITH &&)
);

CREATE INDEX ON ref.site USING gist (geom);
CREATE INDEX ON interp.emprise USING gist (geom);
CREATE INDEX ON interp.emprise USING gist (validite);

-- Zone tampon calculée à l'affichage, jamais stockée
CREATE VIEW interp.emprise_affichage AS
SELECT id, lieu_historique_id, validite,
       coalesce(geom, ST_Buffer(centre::geography, rayon_incertitude_m)::geometry) AS geom_affichee
FROM interp.emprise;

-- Dans quelle paroisse se trouvait ce site le 3 mars 1712 ?
SELECT lh.id
FROM ref.site s
JOIN interp.emprise e ON ST_Contains(e.geom, s.geom)
JOIN interp.lieu_historique lh ON lh.id = e.lieu_historique_id
WHERE s.id = 4471
  AND lh.type = 'paroisse'
  AND e.validite @> DATE '1712-03-03';
```


**Conclusions à effets multiples, contraintes temporelles et calculs métriques**, esquisse non testée :

```sql
CREATE TABLE interp.conclusion_effet (
  id            bigserial PRIMARY KEY,
  conclusion_id bigint NOT NULL REFERENCES interp.conclusion ON DELETE CASCADE,
  type          text NOT NULL,   -- activer_ident, rejeter_ident, contrainte_temporelle, lieu_retenu, incertitude_assumee
  cible_type    text NOT NULL,
  cible_id      bigint NOT NULL
);

CREATE TABLE interp.contrainte_temporelle (
  id                     bigserial PRIMARY KEY,
  evenement_id           bigint NOT NULL REFERENCES interp.evenement,
  borne                  text NOT NULL,   -- debut_min, debut_max, fin_min, fin_max
  valeur                 date,
  evenement_reference_id bigint REFERENCES interp.evenement,  -- ex. changement de territoire
  conclusion_id          bigint NOT NULL REFERENCES interp.conclusion,
  CHECK ((valeur IS NULL) <> (evenement_reference_id IS NULL))
);

-- « Retenir la chapelle et dater après 1709 » : une seule transaction (R22)
BEGIN;
  INSERT INTO interp.conclusion (…) VALUES (…) RETURNING id;          -- C21
  UPDATE interp.ident_lieu SET statut = 'actif'  WHERE id = :ident_chapelle;
  UPDATE interp.ident_lieu SET statut = 'rejete' WHERE id = :ident_paroisse;
  INSERT INTO interp.contrainte_temporelle (evenement_id, borne, evenement_reference_id, conclusion_id)
       VALUES (:e0, 'debut_min', :transfert_1709, :c21);
  INSERT INTO interp.conclusion_effet (conclusion_id, type, cible_type, cible_id) VALUES
       (:c21, 'activer_ident', 'ident_lieu', :ident_chapelle),
       (:c21, 'rejeter_ident', 'ident_lieu', :ident_paroisse),
       (:c21, 'contrainte_temporelle', 'evenement', :e0);
COMMIT;

-- Distance métrique : calcul en Lambert-93, stockage en WGS 84
SELECT ST_Distance(ST_Transform(s.geom, 2154), ST_Transform(e.geom, 2154)) AS distance_m
FROM ref.site s, interp.emprise e
WHERE s.id = :chapelle AND e.id = :emprise_paroisse_1706;

-- Index sur la géométrie projetée, pour que ces calculs restent rapides
CREATE INDEX ON interp.emprise USING gist (ST_Transform(geom, 2154));
```


### 8.3 OCaml : le connecteur GeneWeb

**Forces pour ce projet**

- **Types somme et filtrage exhaustif.** Ajouter un rôle ou un type d'événement fait signaler par le compilateur chaque traitement qui l'oublie.
- **Accès direct à GeneWeb.** Le connecteur lit la base avec les types officiels (`Def`), sans perte ni format intermédiaire.
- **Performances natives**, éprouvées sur les très grandes bases de Geneanet ; parallélisme depuis OCaml 5.
- **Analyse syntaxique solide** (Menhir, Angstrom) pour les chaînes de source, de lieu et de date.

**Limites**

- **Vivier de développeurs réduit** en humanités numériques, où Python et Java dominent.
- **Écosystème RDF et graphe plus mince** : pas d'équivalent mûr à rdflib ou Jena.
- **GeneWeb n'est pas un socle pour notre modèle** : moteur centré sur la personne, stockage binaire.

**Recommandation.** OCaml pour le connecteur, qui lit la base GeneWeb et émet notre modèle en JSON ou CSV ; le cœur en PostgreSQL et Python.

**Esquisse de types** (non compilée, à ajuster aux modules réels de GeneWeb 7.1). Le type paramétré `identification` exprime directement la symétrie du modèle :

```ocaml
type degre = Certain | Probable | Possible
type statut = Propose | Actif | Rejete

(* Une seule structure pour les quatre agrégations *)
type ('de, 'vers) identification = {
  de : 'de; vers : 'vers;
  degre : degre; statut : statut;
  conclusion : Conclusion.id;
  lot : Lot_import.id option;
}
type ident_source    = (Passage.id,  Source.id)    identification
type ident_personne  = (Masque.id,   Personne.id)  identification
type ident_evenement = (Factoide.id, Evenement.id) identification
type cible_lieu = Historique of Lieu_historique.id | Site of Site.id
type ident_lieu      = (Mention_lieu.id, cible_lieu) identification

type participation = {
  factoide : Factoide.id;   (* R2 : rattachée au factoïde, plus à l'événement *)
  masque : Masque.id;
  role : Role.id;
}

(* Connecteur GeneWeb : le compilateur exige un cas par type de témoin *)
let role_of_witness sexe = function
  | Def.Witness -> "temoin"
  | Def.Witness_GodParent -> if sexe = Def.Female then "marraine" else "parrain"
  | Def.Witness_CivilOfficer -> "officier_etat_civil"
  | Def.Witness_ReligiousOfficer -> "celebrant"
  | Def.Witness_Informant -> "declarant"
  | Def.Witness_Attending -> "present"
  | Def.Witness_Mentioned -> "mentionne"
  | Def.Witness_Other -> "autre"
```

---

## 9. Décisions et questions ouvertes

### 9.1 Décisions prises (v0.4 à v0.9)

1. **Les lieux forment une quatrième agrégation** (MENTION_LIEU ⇢ LIEU par IDENT_LIEU), pour que la couche Source reste en insertion seule (R10, R13).
2. **Le factoïde reste à la granularité de l'acte** (R14). La co-présence des participants est l'information essentielle des registres et minutes, et ce choix rejoint l'*Event* de niveau record de GEDCOM X. Les affirmations fines d'IPIF existent déjà à l'intérieur du factoïde, sous forme de participations, qualités et relations.
3. **Lieu historique et site topographique sont distincts** (4.8). Le site porte les coordonnées immuables ; le lieu historique porte le temps : noms, emprises, appartenances et localisations datés.
4. **Saisie assistée** (section 7) : la machine prépare le brouillon, l'humain valide ; chaîne de modèles spécialisés derrière une passerelle ; serveur local pour la base et les droits, modèles en ligne ou locaux selon la configuration.
5. **Conclusions à effets multiples et incertitude assumée** (R22, R23) : une décision peut porter à la fois sur le lieu et sur la date ; garder l'incertitude est une décision à part entière.
6. **Calculs métriques en Lambert‑93**, stockage en WGS 84.
7. **Le PASSAGE garde sa provenance dans le fichier importé** : `fichier_source`, `ligne_debut`, `ligne_fin`. Pour un événement GeneWeb, de la ligne du tag à la dernière ligne de ses témoins, source et notes ; pour un mariage, de la ligne `fam` à la fin du bloc. Cela prolonge R13 : on peut toujours retrouver, ligne à ligne, d'où vient une affirmation.
8. **Témoin `#offi`** : rôle générique `officier` ; il devient `celebrant` quand le type d'événement est religieux (baptême, mariage). L'analyseur ne distingue pas officier civil et religieux.
9. **Dates à l'import GeneWeb** (remplace la version 0.7.2) : `date_brute` conserve la chaîne exactement comme écrite (`3/3/1712`, `~1712`, `?1750`), par fidélité à R13 ; `date_declaree` reprend la forme normalisée par l'analyseur (`03/03/1712`) ; `date_min` / `date_max` viennent des bornes calculées et servent à l'interrogation temporelle.
10. **Qualités à l'import GeneWeb** : `#occu` et titres `[titre:lieu:début:fin:n]` donnent une QUALITE (`role_id` = libellé tel qu'écrit, `categorie` = profession ou titre, `rang` = n du titre). Le passage est la ligne de définition de la personne ; un factoïde sans type par personne porte ses qualités (R2). Le lieu d'un titre est une MENTION_LIEU de fonction `titre`, liée à la qualité.
11. **Lieux à l'import GeneWeb** : chaque chaîne de lieu donne une MENTION_LIEU de désignation « moderne » (`forme_ecrite` = chaîne brute, `forme_normalisee` = nom sans le complément `[complément]_-_lieu`). L'adaptateur ne crée pas d'IDENT_LIEU : elle suppose les référentiels de lieux, qui viennent après (5.8, étape 4).
12. **LOT_IMPORT et réimport** : l'adaptateur produit un LOT_IMPORT (fichier, empreinte SHA‑256 du contenu, date, outil, version, `nb_entites`). Réimporter un fichier d'empreinte déjà connue est refusé (idempotence, R9 et R10) : le lot existant est signalé, rien n'est écrasé ni dupliqué. Les clés ont une forme stable (5.3) ; la comparaison de deux lots d'empreintes différentes (5.8 étape 6) reste à faire.
13. **Notes à l'import GeneWeb** : une note d'événement et un `comm` de famille vont dans `PASSAGE.transcription` (ce qui est écrit sur l'acte). Une note de personne est de la prose d'auteur : elle devient une CONCLUSION (`argument` = texte, `cible` = masque, `valeur` non renseignée), jamais un fait (R2, R18). Limite connue : toldot espace les signes de ponctuation et les crochets de ces textes, qui ne sont donc pas encore restitués à l'identique.
14. **Clé des familles GeneWeb** : l'identifiant technique de toldot (`FAM_001`) dépend de l'ordre du fichier ; il est écarté. La clé `gw:fam:{père}__{mère}` est portée par `FACTOIDE.cle_famille` sur les factoïdes issus d'une famille (mariage, divorce, filiation, événements familiaux). Deux unions des mêmes conjoints partagent la clé : le réimport les distingue par les passages, pas par la clé seule.
15. **Événements de la ligne de personne** : les dates et lieux de naissance (`#bp`), baptême (`!`, `#pp`), décès (`#dp`) et inhumation (`#rp`) d'une ligne d'enfant (`- h Luc …`) ou de conjoint (ligne `fam`) produisent un factoïde par événement, avec pour PASSAGE la ligne de la personne (source `#bs`, `#ps`, `#ds`, `#rs` en citation) et la personne comme participant principal. Un `pevt` du même type prime : rien n'est ajouté. Le déclarant reste vide ; les témoins sont des PARTICIPATION (`temoin`, `parrain`, `marraine`, `celebrant`), sans heuristique.
16. **Différentiel de lots** : la comparaison de deux lots (`comparer_lots(ancien, nouveau)`) est une fonction pure qui ne modifie aucun lot. Les masques s'apparient par `cle_externe`. Un factoïde s'apparie par (type, `cle_famille`, participant principal, rang d'occurrence) ; sans participant, par son premier lien (relation ou qualité). Les lignes de fichier ne comptent pas dans l'égalité (un ajout en tête les décale toutes). Les CONCLUSION (notes de personne) s'apparient par cible (`cle_externe` de la personne) : textes identiques d'abord (invariants), puis les notes restantes par ordre (modification avec ancien et nouveau `argument`), le surplus étant ajout ou rétraction. Quatre issues : *ajout* (absent de l'ancien), *invariant* (identique : dates, lieux, participants, relations, qualités, citation et transcription), *modification* (même fait, valeur changée, avec la liste des champs) et *rétraction* (présent dans l'ancien seulement). Une rétraction ne supprime rien (R10) : l'application du différentiel la versera comme un retrait d'identification, jamais comme un effacement de la couche Source.
17. **Événements familiaux et familles sans conjoint** : un bloc `fevt` ne perd aucun tag (R13). Chaque tag standard a son type Source (table 5.3) ; un tag inconnu devient un type libre à son écriture d'origine. Une ligne `fam ? ? + ? ?` crée quand même sa famille, avec enfants et événements ; la clé `gw:fam:inconnu__inconnu:{clé du premier enfant}` distingue ces familles entre elles (sans enfant, la clé reste partagée : cas non rencontré).
18. **Persistance SQLite** : le DDL est écrit en SQL portable, avec un préfixe de table par schéma PostgreSQL visé (`source_*`, `interp_*`, `audit_*`), pour basculer vers `source.*` et `interp.*` (PostgreSQL/PostGIS) sans toucher à la logique métier. Dates en TEXT ISO-8601. Les tables sont en insertion seule (R10, triggers) ; une rétractation s'enregistre dans `audit_retractation`, jamais par `DELETE`. `personne` et `ident_personne` sont réservées au chantier d'identification MASQUE → PERSONNE. `appliquer_diff` enregistre, dans `audit_retractation`, trois motifs : `retractation` (fait disparu du lot nouveau), `modification` (ancienne version d'un fait dont le contenu a changé), `reconduction` (fait identique, le lot nouveau en porte l'occurrence active). Les vues `source_factoide_actif` et `interp_conclusion_actif` excluent les cibles retirées ; après application, la vue active équivaut au lot nouveau. Appliquer deux fois le même diff n'écrit rien de plus.
19. **Identification MASQUE ⇢ PERSONNE** (v0.8, R25). Six tables, en insertion seule comme les autres :
    - `interp_contributeur` (`nom`, `type` : humain, agent, import) : le référentiel CONTRIBUTEUR, préfixé `interp_` en SQLite faute de schéma `ref` simulé.
    - `interp_personne` : coquille (`ref`, `uri`, `acces`, `cle_externe`, `same_as_id`). Nom retenu, dates et fiche sont des vues sur les identifications actives (R8). Une fusion pointe les identifications vers la même personne, ou chaîne une personne vers la canonique par `same_as_id` (R4) ; la clé GeneWeb reste sur le masque.
    - `interp_ident_personne` : la proposition (`masque_id`, `personne_id`, `degre`, `contributeur_id`, `lot_id`, `date`), jamais modifiée.
    - `interp_ident_personne_statut` : le journal des décisions (`ident_id`, `statut`, `conclusion_id`, `contributeur_id`, `date`). Vue `interp_ident_personne_actif` : identifications dont la dernière décision est « actif ». Deux triggers à l'insertion : R11 (une autre identification active du même masque bloque l'activation) et R18 (un agent ne peut pas activer).
    - `interp_indice` : le faisceau d'indices, une ligne par élément comparé (`ident_id`, `type`, `sens`, `poids`, `valeur_masque`, `valeur_personne`, `mode`, `regle_version`, `factoide_id`, `conclusion_id`). Un indice calculé cite la version de sa règle, pour être rejoué comme une normalisation de date (R13) ; le score d'un candidat en découle (question 9.2-1).
    - `interp_conclusion_effet` (`conclusion_id`, `type`, `cible_type`, `cible_id`) : les conséquences d'une conclusion (R22). `interp_conclusion.cible_masque_id` devient facultatif : une conclusion peut réunir deux personnes, écarter un homonyme ou borner une date sans porter sur un seul masque.

    **Homonymes** : un masque peut avoir plusieurs identifications « proposé » vers des personnes différentes ; c'est le jeu de candidats, chacun avec son faisceau. Écarter un homonyme, c'est verser « rejeté » avec une conclusion, qui reste consultable (R11, R24). Le groupe d'homonymes est une vue sur le nom normalisé, sans table propre.

    **Import GeneWeb** : la clé `Nom Prénom.occ` est l'identification faite par l'auteur de la base.
    - *Une personne par clé.* L'import crée (ou retrouve) la personne de `ref` `gw:pers:…` et rattache chaque masque de la clé par une identification de degré « certain », versée « actif » par le contributeur canonique `import_geneweb` (type `import`) et rattachée au lot (5.3). Les masques d'une même personne sont ainsi réunis par construction (R4).
    - *Réimport.* La personne est réutilisée : les conclusions qui la visent restent valables. Les identifications des masques du lot ancien sont retirées par `audit_retractation`, avec le motif du différentiel de leur clé : `reconduction` (masques identiques), `modification` (nom ou sexe changé), `retractation` (clé disparue). La personne d'une clé disparue reste, sans identification active. Réécrire les identifications d'un lot déjà traité n'écrit rien.
    - *Primauté du chercheur (R24).* Si la dernière décision humaine sur les identifications d'une clé est en désaccord avec l'import (rejet d'une identification vers la personne de la clé, ou activation vers une autre personne), les nouvelles identifications de la clé sont versées « proposé », jamais « actif », et le rapport d'import les compte.
    - Une identification proposée par un agent reste « proposé » (R18). Annuler un lot retirera ses identifications (R9) ; la fonction d'annulation reste à écrire.

    L'identification d'événement garde pour l'instant son statut en colonne, posé à l'import ; elle rejoindra le journal dans un lot ultérieur.

20. **Rapprochement d'homonymes par faisceau d'indices** (v0.9, R26). Premier calcul de la couche Interprétation : un agent, le contributeur canonique `apparieur_homonymes` (type `agent`), propose de rattacher les masques d'une personne à une autre personne quand leurs faisceaux d'indices le justifient.
    - *Périmètre.* Par défaut, seules des personnes de bases différentes (lignées de fichiers distinctes, décision 19) sont comparées : dans une même base, le numéro d'occurrence (`Nom Prénom.occ`) est une distinction faite par l'auteur. Une option `intra_base` étend la recherche aux doublons de saisie d'une même base.
    - *Candidats et granularité.* Le regroupement se fait par personne, sur le nom normalisé et la clé phonétique du premier prénom (vue, sans table, 4.4). L'évaluation se fait par masque, conformément à l'INDICE (le masque face à la personne candidate) : chaque masque de la personne la plus récente est évalué contre la plus ancienne, pour ne pas proposer deux fois le même couple. Le faisceau d'un masque ne porte que ce que ce masque montre : sans date, pas d'indice chronologique.
    - *Règles v1* (indices `mode` calculé, `regle_version` citée) :
        - `regle:onomastique:nom_prenom:v1` : égalité des formes normalisées, « pour », poids 1,0 ; variante phonétique ou prénom secondaire (premier prénom égal, `Pierre_Jean` et `Pierre`), « pour », 0,5. La normalisation et la clé phonétique française sont écrites dans le projet, sans dépendance.
        - `regle:chrono:v1` : un fait du masque antérieur à la naissance de la personne candidate ou postérieur à son décès, « contre », 2,0 ; un écart de plus de 110 ans entre deux mentions, « contre », 2,0 ; dates compatibles, « neutre », 0 (l'absence d'incompatibilité n'est pas une preuve, mais la vérification reste visible). Seuls les faits où le masque tient un rôle de personne vivante (naissance, baptême, mariage, témoin) sont comparés, pour ne pas compter les mentions posthumes (« fils de feu… ») ; décès et inhumation le sont avec une tolérance d'un an.
        - `regle:reseau:famille:v1` : parents concordants (mêmes noms et prénoms normalisés du père et de la mère), « pour », 2,0 ; parents formellement différents, « contre », 1,5 ; même conjoint mentionné, « pour », 1,5.
    - *Barème v1.* Score = somme des poids « pour » moins somme des poids « contre ». Un indice « contre » de poids 2 ou plus est éliminatoire. Proposition « possible » à partir de 2,0, « probable » à partir de 3,5, jamais « certain ». Le barème est une constante versionnée ; sa calibration sur un échantillon annoté reste ouverte (9.2-1).
    - *Écriture.* Pour chaque candidat retenu : une identification `interp_ident_personne` du degré calculé, sa décision « proposé » au journal, puis ses indices. Un couple masque–personne déjà identifié n'est pas repris, ce qui rend le calcul rejouable et préserve les rejets humains (R24). Candidats éliminés ou sous le seuil : comptés dans le rapport d'exécution, sans écriture (R26).
    - *Architecture.* Le calcul est pur, sans SQL (`chronologia/interpretation/` : normalisation, profils, règles, homonymes) ; la lecture des profils depuis les identifications actives (R8) et l'écriture des propositions relèvent de `chronologia/persistence/` ; un service orchestre le tout dans une transaction.

### 9.2 Questions ouvertes

1. **Score des candidats.** Poids des indices (noms, dates, lieux, réseau) et seuils de proposition : à calibrer sur un échantillon annoté. Un barème v1 provisoire est fixé par la décision 20.
2. **Plusieurs équipes, plusieurs vues de référence ?** R11 suppose une vue de référence par projet. Si plusieurs projets partagent la base, `actif` devra dépendre du projet.
3. **Publication RDF.** Correspondance fine vers CIDOC‑CRM et CRMinf (PC14, I2, I7) à écrire et à tester.
4. **Types d'événements décrits.** Le type porté par le factoïde (`type_evenement_id`) est traité comme une normalisation du vocabulaire. Si des classements font débat (un « contrat » qui est en fait une donation), il faudra les traiter par une conclusion sur le factoïde.
5. **Emprises anciennes.** Les limites des paroisses et seigneuries sont rarement connues avant le cadastre napoléonien. On commence par des points (chef-lieu) avec un rayon d'incertitude, comme le recommande le World Historical Gazetteer, puis on ajoute des polygones à mesure des sources. La zone tampon est calculée à l'affichage (`ST_Buffer`), jamais stockée ; la précision doit rester visible sur la carte.
6. **Notion d'organisation.** Faut-il introduire une entité pour les groupes constitués autres que territoriaux (régiment, confrérie, communauté religieuse, corporation, étude notariale, entreprise, association) ? Rien ne l'impose aujourd'hui. Le modèle les traite déjà de trois façons partielles : le LIEU_HISTORIQUE couvre les institutions territoriales (paroisse, bailliage) ; la profession est un rôle durable unaire ; la parenté est un rôle durable binaire. Un « employeur » ou une « appartenance à un régiment » n'a pas de place propre. À instruire lors d'une prochaine itération : (a) un besoin avéré dans le corpus ou les requêtes visées (réseau, prosopographie institutionnelle) ; (b) si oui, la forme : une cinquième agrégation par identification révisable (mention d'organisation ⇢ organisation, sur le patron de IDENT_LIEU), ou un simple type de masque ; (c) le rôle durable binaire masque ↔ organisation, daté, avec intervalle flou ; (d) la frontière avec LIEU_HISTORIQUE pour les institutions à la fois territoriales et personnes morales (une paroisse, une seigneurie) ; (e) la correspondance CIDOC‑CRM (E74 Group) et le traitement des groupes dans GEDCOM X ; (f) l'effet sur l'import GeneWeb. S'il est retenu, une nouvelle règle devra fixer son statut vis-à-vis de R13 et R18. Aucune décision prise.

---

## 10. Sources

- [Bio CRM, CEUR‑WS vol. 2119, article 10](https://ceur-ws.org/Vol-2119/paper10.pdf)
- [Data Exchange in Practice: Towards a Prosopographical API, CEUR‑WS vol. 3152](https://ceur-ws.org/Vol-3152/BD2019_paper_6.pdf)
- [IPIF / prosopogrAPhI (GitHub)](https://github.com/GVogeler/prosopogrAPhI)
- [FHISO, ELF Data Model](https://fhiso.org/TR/elf-data-model.pdf)
- [FHISO, Citation Elements](https://fhiso.org/TR/cev-rdfa-bindings)
- [IBM, i2 Analyst's Notebook: Entity Link Properties (ELP)](https://www.ibm.com/support/pages/i2-analysts-notebook-entity-link-properties-elp)
- [IBM i2 EIA Data Model White Paper v4.3](https://www.ibm.com/docs/en/SSXVTH_4.3.3/com.ibm.i2.understand.data.doc/platform_datamodel_whitepaper_pdf.pdf)
- [The i2 Analyze data model](https://docs.i2group.com/analyze/4.4.3/data_model_intro.html)
- [ELP relationships in i2 Analyze](https://docs.i2group.com/analyze/4.4.4/data_model_elp_relationships.html)
- [GeneWeb, format .gw](https://geneweb.tuxfamily.org/wiki/GWformat)
- [GeneWeb, export avec gwu](https://geneweb.tuxfamily.org/wiki/gwu)
- [GeneWeb, import/export GEDCOM](https://geneweb.tuxfamily.org/wiki/ged)
- [GeneWeb, types du module Def](https://github.com/geneweb/geneweb/blob/master/lib/def/def.ml)
- [GeneWeb, versions publiées](https://github.com/geneweb/geneweb/releases)

Les autres références (Bradley & Short, Pasin & Bradley, SNAP, CIDOC‑CRM, CRMinf, CRMgeo, GEDCOM X, GENTECH, Pleiades, World Historical Gazetteer, base Cassini de l'EHESS, historique du COG de l'INSEE) sont citées de mémoire. Leurs références bibliographiques sont à vérifier avant une diffusion formelle. Les exemples (baptême, extrait baptistaire, extrait `.gw`, identifiants de lieux et de sites) sont fictifs.
