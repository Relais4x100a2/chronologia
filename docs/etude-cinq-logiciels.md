# Fiches courtes : Omeka S et FactGrid, APIS, Gramps, Recogito, World Historical Gazetteer

*Étude du 9 novembre 2026, faite à partir du code source de chaque logiciel (clones du jour). Elle suit `docs/etude-heurist.md` et `docs/etude-nodegoat-arches-researchspace.md`. Les numéros de règles, de décisions et de sections renvoient à `docs/modele-evenement-masque-factoide.md` (v0.10).*

Ce sont des **fiches courtes** : chacune se limite à ce qui répond à une question ouverte de Chronologia ou confirme un choix déjà fait. Omeka S et FactGrid sont regroupés dans une fiche « publication ».

**Licences.** On reprend des idées, jamais du code, sauf mention contraire :

| Logiciel | Licence |
|---|---|
| Omeka S | GPL‑3 |
| Wikibase (moteur de FactGrid) | GPL‑2.0 ou ultérieure |
| APIS | MIT |
| Gramps | GPL‑2 |
| Gramps Web (API) | AGPL‑3 |
| Recogito Studio (serveur) | AGPL‑3 ; certains greffons, dont le géoréférencement, sont sous BSD‑3 |
| World Historical Gazetteer | BSD‑3 |

APIS et World Historical Gazetteer sont sous licence permissive : du code pourrait en être repris, avec mention. Rien ne le justifie pour l'instant.

## 0. En une page

| Logiciel | Ce qu'il est | Ce qu'il apporte à Chronologia |
|---|---|---|
| **Omeka S** | Publication de collections | Une provenance par valeur : confirme le factoïde, sans le dépasser |
| **FactGrid / Wikibase** | Base de données historiques en énoncés | Une cible de publication ; la distinction « valeur inconnue » / « pas de valeur » |
| **APIS** | Prosopographie (Vienne, Django) | Des groupes traités comme des entités, pour la question des organisations ; un contre‑exemple de fusion destructive |
| **Gramps** et **Gramps Web** | Généalogie | Une quarantaine de contrôles de vraisemblance paramétrés ; le calcul « probablement vivant » |
| **Recogito Studio** | Annotation de textes et d'images | Le modèle d'annotation du W3C pour ancrer un élément dans un passage |
| **World Historical Gazetteer** | Répertoire de lieux historiques | Le format Linked Places ; le rapprochement par autorité, avec un statut « reporté » |

**Ce qu'il faut retenir**
1. Rien ne remet en cause le modèle. Plusieurs choix récents se retrouvent ailleurs :
   - la qualité de date « estimée » ou « calculée » de Gramps correspond à la décision 23 ;
   - la hiérarchie de lieux datée de Gramps correspond à APPARTENANCE ;
   - la mémoire des avertissements écartés de Gramps correspond à R27.
2. Deux outils concrets manquent :
   - les **contrôles de vraisemblance** sur les personnes reconstruites ;
   - un calcul explicite de **« possiblement vivant »**, dont dépendent R21 et `acces`.
3. Pour l'étape « Lieux », World Historical Gazetteer donne à la fois un **format d'échange** (Linked Places) et une **méthode de rapprochement** déjà éprouvée.
4. Une question nouvelle : distinguer une **valeur inconnue** (« fils de père inconnu ») d'une **absence attestée** (« mort sans postérité »).

Les propositions sont au §6. Les huit ont été retenues le 9 novembre 2026 : décisions 33 à 38, et questions ouvertes 9.2‑6 et 9.2‑10 du modèle v0.10.1.

---

## 1. Publication : Omeka S et FactGrid

### 1.1 Omeka S

**Principe.** Une ressource (item, collection, média) porte des **valeurs**. Chaque valeur est rattachée à une propriété d'un vocabulaire RDF (Dublin Core, FOAF, BIBO fournis ; d'autres vocabulaires importables, CIDOC‑CRM compris). Des **modèles de ressource** disent quelles propriétés saisir et avec quels types de données.

**Annotation de valeur.** Depuis la version 4, une valeur peut porter une **annotation**. Cette annotation est elle‑même une petite ressource, qui a ses propres valeurs : source, certitude, note. En JSON‑LD, elle sort sous la clé `@annotation` de la valeur.

**Pour Chronologia :**
- **Une confirmation, sans plus.** C'est une provenance par valeur, comme chez nodegoat. Notre factoïde va plus loin : la source n'est pas une note posée sur une valeur, c'est le point de départ de la valeur.
- **Une cible de publication possible.** L'API REST et le JSON‑LD d'Omeka S suffiraient à publier des fiches de personnes, avec la source de chaque valeur. Omeka S est très répandu en France pour publier des corpus. Ce n'est pas prioritaire : Heurist (décision 24), puis le RDF (§9.2‑3), couvrent déjà ce besoin.

### 1.2 FactGrid et Wikibase

**Principe.** FactGrid est une instance de **Wikibase**, le moteur de Wikidata, consacrée à l'histoire. Une entité porte des **déclarations**. Chaque déclaration se compose de quatre éléments :
- une valeur ;
- des **qualificatifs** (rôle, date, lieu) ;
- des **références** (source, page) ;
- un **rang** : préféré, normal ou déprécié.

Le code distingue trois sortes de valeur : une valeur précise, **une valeur inconnue** (« il a un père, on ne sait pas qui ») et **aucune valeur** (« il n'a pas d'enfant »). Une date porte un **calendrier** (grégorien ou julien), une **précision** (du milliard d'années au jour) et une marge **avant** et **après**.

**Ce que FactGrid fait comme nous.** Les conventions de Wikidata permettent de noter **la forme écrite du nom dans la source** (« désigné comme ») sur la référence d'une déclaration. On a ainsi l'équivalent de notre masque, mais réduit à une chaîne de caractères. Elles permettent aussi de noter une **date au plus tôt et au plus tard**. Les propriétés exactes de FactGrid restent à relever.

**Ce qu'il ne fait pas.** Une déclaration est déjà une conclusion : rien n'y sépare ce que dit la source de ce que l'on en conclut. Le rang « déprécié » marque une valeur jugée fausse, mais sans argument structuré.

**Pour Chronologia :**
- **Une cible de publication naturelle**, et la plus utilisée par la communauté allemande et internationale de l'histoire numérique. L'export se décrirait ainsi :
  - chaque valeur d'une PERSONNE active devient une déclaration ;
  - ses références sont les SOURCES des factoïdes qui la fondent ;
  - la forme écrite du masque devient « désigné comme » ;
  - une identification « certain » donne une déclaration de rang normal ; une valeur écartée par une conclusion n'est pas exportée, ou l'est au rang déprécié avec l'argument en note.
- **Une question de modèle**, au §6, proposition 7 : la distinction entre valeur inconnue et absence de valeur.

---

## 2. APIS (Autriche, ACDH)

**Principe.** APIS est un cadre Django (licence MIT) pour les bases prosopographiques. Le cœur ne fixe que des entités CIDOC‑CRM de base :
- `E21_Person` : nom, prénom, sexe, dates de naissance et de décès ;
- `E53_Place` : libellé et coordonnées ;
- `E74_Group`.

Chaque projet ajoute ses propres classes. Les **relations** sont des classes typées. Chacune dit le type de son sujet et de son objet, et porte un nom et un **nom inverse** (« est le père de » / « est l'enfant de »). Le **versionnement** passe par django‑simple‑history. **L'enrichissement** importe des données depuis des notices d'autorité (GND, Wikidata) par des correspondances RDF décrites en TOML. Les dates ne sont plus dans le cœur : chaque projet choisit son traitement.

**Pour Chronologia :**
- **Organisations (§9.2‑6).** APIS traite les groupes (`E74_Group`) comme des entités de plein droit, au même rang que les personnes et les lieux. Elles sont reliées par des relations typées et datées : membre de, fondateur de, siège à. C'est un argument pour créer une entité ORGANISATION plutôt que de faire porter ces informations par des qualités ou des notes. Le cas APIS montre aussi le prix d'un report : sans entité, les confréries, régiments ou études notariales restent dans des chaînes de texte.
- **Rôles et inverses.** Notre ROLE porte déjà `inverse_id`. APIS confirme ce choix, et y ajoute un contrôle utile : une relation dit quels types d'entités elle relie.
- **Contre‑exemple de fusion.** `merge_with` copie les champs puis **supprime** les entités fusionnées. La fusion n'est donc pas réversible, sinon en remontant l'historique. Notre R4 (fusion par pointage, `same_as_id`) évite précisément cela.
- **Enrichissement.** L'import depuis des notices d'autorité écrit directement dans l'entité. Chez nous, une donnée venue d'un référentiel externe resterait une **proposition** (R18), ancrée à une SOURCE (R2).

---

## 3. Gramps et Gramps Web

**Principe.** Gramps est le logiciel de généalogie libre de référence (Python, GPL‑2). Gramps Web en est une version web, avec une API Flask (AGPL‑3). Le modèle de Gramps est riche :
- **dates** : un modificateur (avant, après, vers, entre, de… à, texte seul), une **qualité** (estimée, calculée) et sept **calendriers**, dont le républicain ;
- **citations** : chaque citation porte une page et un **niveau de confiance** sur cinq degrés, et peut s'attacher à presque tout objet, y compris à un lien (le rôle d'une personne dans un événement, un enfant dans une famille) ;
- **lieux** : chaque lieu a des noms datés et des rattachements à des lieux englobants, eux aussi **datés**.

**Ce qui confirme nos choix :**
- la qualité estimée ou calculée recoupe nos modes de détermination « estimée » et « déduite » (décision 23) ;
- les rattachements de lieux datés correspondent à APPARTENANCE avec `validite` ;
- l'événement partagé par plusieurs personnes, chacune avec son rôle, correspond à notre EVENEMENT avec ses participations.

### 3.1 Les contrôles de vraisemblance

L'outil **Vérifier** de Gramps applique une **quarantaine de règles** aux personnes et aux familles. Exemples :
- naissance après le décès ou après le baptême ;
- inhumation avant le décès ;
- mère de moins de 17 ans ou de plus de 48 ans ;
- mariage avant la naissance ;
- enfant né après la mort du père, au-delà d'un délai ;
- écart excessif entre époux ou entre enfants ;
- baptême trop tardif ;
- personne de plus de 90 ans sans décès.

Les **seuils sont des paramètres** (`oldage` = 90, `yngmom` = 17, `oldmom` = 48, `hwdif` = 30…). Les avertissements que l'utilisateur **écarte** sont retenus, base par base, et ne réapparaissent pas.

**Pour Chronologia.** Notre rapprochement utilise déjà des règles chronologiques (`regle:chrono:v1`, décision 20), mais seulement pour comparer un masque à une personne candidate. Rien ne contrôle encore la **personne reconstruite** : une fusion acceptée peut produire une mère de 9 ans sans que personne ne le voie. Les règles de Gramps donnent un catalogue tout fait. Chez nous :
- chaque contrôle serait nommé et versionné, comme les règles du rapprochement ;
- chaque résultat entrerait dans la file de décisions (R12, R24) ;
- un avertissement écarté par l'historien ne serait pas reposé (R27).

### 3.2 « Probablement vivant »

Gramps calcule si une personne est **probablement vivante**. Il part de ses dates, puis, à défaut, de celles de ses parents, conjoints et enfants, avec un âge maximal paramétré. Gramps Web expose ce calcul et l'**intervalle estimé** de naissance et de décès.

**Pour Chronologia.** Notre §7 dit que les bases importées contiennent souvent des personnes vivantes (« sans date de décès et nées il y a moins d'un siècle environ »). R21 interdit de les envoyer à un service externe. Mais aucun calcul n'est décrit. Il faut une règle explicite, paramétrée et versionnée, qui marque une personne « possiblement vivante » en s'appuyant sur ses proches. Ce marquage est une proposition de restriction, appliquée d'office par prudence. Il ne vaut jamais autorisation : lever la restriction reste une décision humaine.

### 3.3 Le reste de Gramps Web

- **Discussion assistée par un modèle de langage** sur l'arbre (`/chat`) et **reconnaissance de texte** sur les médias (`/ocr`). C'est la même direction que notre §7, mais sans ancrage ni validation. À regarder pour l'ergonomie, pas pour la méthode.
- **Annulation par transaction** : chaque modification est rejouable à l'envers. Notre journal (R10, R25) le permet aussi.

---

## 4. Recogito Studio

**Principe.** Recogito, issu du réseau Pelagios, permet d'**annoter** des textes, des documents TEI et des images IIIF, à plusieurs. La version actuelle, Recogito Studio, repose sur PostgreSQL (via Supabase) et suit le **modèle d'annotation du W3C** :
- une **annotation** a une ou plusieurs **cibles**, chacune avec un **sélecteur** : passage de texte, fragment ou région d'image en SVG ;
- elle a aussi un ou plusieurs **corps**, chacun avec un **but** : commenter, étiqueter, géoréférencer ;
- les annotations sont rangées en **couches**, par projet et par contexte ;
- tout est versionné et attribué.

Des **greffons** ajoutent :
- la reconnaissance d'entités nommées ;
- le **géoréférencement** à partir d'un répertoire de lieux au format Linked Places (Pleiades fourni) ;
- l'insertion des annotations dans un fichier TEI.

**Pour Chronologia :**
- **Ancrage (R19).** Tout élément extrait doit citer sa position dans la transcription. Le modèle du W3C donne une forme normalisée à cette position :
  - un passage de texte cité avec ses mots voisins, ou une position par caractères ;
  - une région d'une image IIIF.
  
  Adopter cette forme pour PASSAGE et pour les ancrages de la saisie assistée rendrait nos annotations lisibles par d'autres outils.
- **Outils d'annotation (§9.2‑8).** Recogito est le candidat naturel pour annoter à la main, avant ou à côté de la saisie assistée. Ses annotations s'exportent dans ce format standard : une MENTION_LIEU ou un MASQUE pourraient en être importés comme **propositions** rattachées à un passage. Le greffon de géoréférencement fait déjà, côté annotation, ce que fera notre étape « Lieux ».
- **À ne pas reprendre** : l'annotation y est la donnée finale. Il n'y a ni personnes reconstruites ni conclusions.

---

## 5. World Historical Gazetteer

**Principe.** Le WHG (Université de Pittsburgh, licence BSD‑3) rassemble des **jeux de lieux historiques** fournis par des chercheurs. Il les **rapproche** de grands référentiels : Wikidata, Getty TGN, GeoNames, et son propre index de plus de 47 millions de lieux. La pile est très proche de la nôtre : Django, PostgreSQL, PostGIS, MapLibre GL.

Un lieu se décompose en plusieurs éléments :
- des **noms**, chacun avec sa source et son relecteur ;
- des **types** (thésaurus AAT du Getty) ;
- des **géométries**, chacune avec sa source ;
- des **périodes** (`whens`) ;
- des **liens** vers des référentiels, avec une note de relecture ;
- des **relations** à d'autres lieux.

Tous ces éléments circulent dans un format d'échange, le **Linked Places Format** (GeoJSON‑LD avec des périodes).

**Le rapprochement.** Pour chaque lieu et chaque référentiel, une tâche produit des **candidats**, avec un score et la passe de recherche qui les a trouvés. L'historien les relit un à un. Chaque lieu porte un **statut de relecture par référentiel** : non relu, relu ou **reporté**. Un rapprochement retenu garde sa **base** : identifiant d'autorité partagé, relecture humaine ou import.

**Les identifiants permanents.** Un identifiant publié doit rester résolu après une réorganisation. Le WHG a gelé dans une table la correspondance des anciens identifiants avant de retirer l'ancien index.

**Pour Chronologia :**
- **Étape « Lieux » (§9.2‑5, §9.2‑9).** Le WHG donne trois choses :
  - un **format d'échange** pour LIEU_HISTORIQUE, NOM_LIEU, APPARTENANCE et leurs périodes (Linked Places) ;
  - une **source de candidats** pour les rapprochements (son API, ou GeoNames et Wikidata directement) ;
  - une **méthode** de relecture déjà éprouvée.
  
  Nos candidats entreraient en « proposé » (R18), avec leurs indices, comme pour les personnes. L'atelier de prosopo-gw pourrait lui aussi produire du Linked Places.
- **Statut « reporté ».** La file de décisions ne connaît que « à traiter » et « tranché ». Pouvoir **reporter** une question difficile (« à revoir avec les registres paroissiaux ») sans la trancher éviterait de la laisser en tête de file ou de la trancher trop vite.
- **Identifiants permanents.** Cela confirme R4 : une PERSONNE fusionnée garde son `uri`, et `same_as_id` redirige. Il faudra le tenir aussi pour les lieux publiés.
- **Publication.** Nos lieux historiques, une fois relus, pourraient être versés au WHG comme jeu de données, à l'image de ce qu'il fait avec Pleiades.

---

## 6. Propositions

À trancher, comme pour les études précédentes.

| n° | Proposition | Inspirée de | Ce qui change dans le modèle | Quand |
|---|---|---|---|---|
| 1 | **Contrôles de vraisemblance** sur les personnes reconstruites : catalogue de règles nommées et versionnées (âge des parents, ordre des événements, écarts), seuils paramétrés. Chaque avertissement entre dans la file de décisions ; un avertissement écarté n'est pas reposé (R27). | Gramps | Aucune entité nouvelle si la file de décisions accueille ces avertissements ; sans nouvelle règle | Après la validation des propositions |
| 2 | **Calcul « possiblement vivant »** explicite, paramétré, appuyé sur les proches, qui alimente `PERSONNE.acces` et le filtre de R21. Le marquage restreint d'office ; seul un humain le lève. | Gramps | Précision de 4.4 (`acces`) et de §7 ; sans nouvelle règle | Avant tout envoi externe et tout export |
| 3 | **Linked Places Format** pour importer et exporter les lieux historiques, et **candidats de lieux** cherchés dans WHG, GeoNames et Wikidata, en « proposé » avec leurs indices. | WHG, Recogito | Format d'entrée et de sortie ; tranche une partie de §9.2‑9 | Étape « Lieux » |
| 4 | **Statut « reporté »** dans la file de décisions : une question peut être mise de côté, avec un motif, sans être tranchée. | WHG | Un état de plus pour les entrées de la file | Avec l'écran de validation |
| 5 | **Ancrage au format W3C Web Annotation** pour la localisation d'un PASSAGE et les ancrages de la saisie assistée (R19), et import des annotations de Recogito comme propositions. | Recogito | Forme normalisée de `localisation` et des ancrages ; éclaire §9.2‑8 | Saisie assistée |
| 6 | **Connecteur Wikibase / FactGrid** pour la publication, après celui de Heurist : déclarations avec références, forme du masque en « désigné comme ». | FactGrid | À inscrire dans la feuille de route des connecteurs (décision 24) | Après le connecteur Heurist |
| 7 | **Nouvelle question ouverte** : distinguer « valeur inconnue » (« de père inconnu », « fils d'un tel et d'une femme non nommée ») et « absence attestée » (« mort sans postérité »). Aujourd'hui, un conjoint `? ?` de GeneWeb est ignoré (décision 21) : l'information « il y avait un conjoint » se perd. | Wikibase | Aucune pour l'instant : question en §9.2 | À instruire |
| 8 | **Organisations (§9.2‑6)** : verser l'exemple d'APIS au dossier, en faveur d'une entité ORGANISATION reliée aux personnes par des relations datées. | APIS | Aucune pour l'instant : enrichit la question ouverte | À instruire |

Les propositions 1 à 5 sont des décisions locales. Les 7 et 8 ne décident rien : elles complètent les questions ouvertes. Omeka S n'apparaît dans aucune proposition : c'est une cible de publication possible, mais pas prioritaire.

---

## Annexe : où regarder dans le code

| Sujet | Fichier |
|---|---|
| Omeka S : annotation de valeur | `omeka-s/application/src/Entity/ValueAnnotation.php`, `Value.php`, `Api/Representation/ValueRepresentation.php` (`@annotation`) |
| Omeka S : modèles de ressource | `omeka-s/application/src/Entity/ResourceTemplateProperty.php` |
| Wikibase : rangs, valeur inconnue, aucune valeur | `lib/packages/wikibase/data-model/src/Statement/Statement.php`, `Snak/PropertySomeValueSnak.php`, `Snak/PropertyNoValueSnak.php` |
| Wikibase : dates | `view/packages/wikibase-data-values/src/values/TimeValue.js`, `repo/includes/Rdf/JulianDateTimeValueCleaner.php` |
| APIS : relations typées, inverses | `apis_core/relations/models.py` |
| APIS : fusion destructive | `apis_core/generic/abc.py` (`merge_with`) |
| APIS : entités de base, enrichissement RDF | `apis_core/entities/abc.py`, `apis_core/utils/rdf.py` |
| Gramps : dates, citations, lieux | `gramps/gen/lib/date.py`, `citation.py`, `placeref.py` |
| Gramps : contrôles de vraisemblance | `gramps/plugins/tool/verify.py` ; version web : `gramps_webapi/verify_lib.py` |
| Gramps Web : vivants, discussion, OCR | `gramps_webapi/api/resources/living.py`, `chat.py`, `ocr.py` |
| Recogito : annotations, cibles, corps, couches | `recogito-server/supabase/migrations/` |
| Recogito : géoréférencement | `plugin-geotagging/src/`, `gazetteers/pleiades-all-places.lp.json` |
| WHG : modèle des lieux, rapprochements | `website/places/models.py` (`Place`, `PlaceName`, `PlaceWhen`, `CloseMatch`, `LegacyUnionRecord`), `website/datasets/models.py` (`Hit`), `main/choices.py` (`STATUS_REVIEW`) |
| WHG : Linked Places Format | `website/validation/` |
