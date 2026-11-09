# Étude de Heurist : forces, faiblesses et ce que Chronologia peut en reprendre

> Document d'étude, pas une décision de modèle. Les reprises retenues devront être consignées dans `modele-evenement-masque-factoide.md` (journal, section concernée, §9) avant tout code.

- **Objet étudié :** dépôt `HeuristNetwork/heurist`, branche `h7dev`, commit `1b363801a` (novembre 2026), code et dossier `documentation/`.
- **Méthode :** lecture du schéma SQL (`admin/setup/dbcreate/blankDBStructure.sql`), des classes serveur (`hserv/`, `srv/`), du client (`hclient/`), de la documentation utilisateur (*Understanding Heurist v7*) et des plans de développement 2026.
- **Licence :** Heurist est sous **GPL‑3**, Chronologia sous **MIT**. On reprend des **idées, des structures et des formats**, jamais du code copié. Toute traduction ligne à ligne d'un fichier Heurist ferait de Chronologia une œuvre dérivée GPL.

---

## 1. Heurist en bref

Heurist est un système de gestion de données de recherche pour les sciences humaines, développé depuis 2005 (Université de Sydney, puis association Heurist Network à Paris depuis 2024). Son principal serveur en service est celui de **Huma‑Num**. Il permet à un chercheur de concevoir sa propre base (types d'entités, champs, vocabulaires) par l'interface web, de la saisir, de l'interroger, de la cartographier et de la publier en site web, sans programmeur.

| Aspect | Constat |
|---|---|
| Pile | PHP, JavaScript (jQuery / jQuery UI), MySQL/MariaDB, Smarty pour les rapports, Leaflet pour les cartes |
| Volume | ≈ 240 000 lignes de PHP, ≈ 190 000 lignes de JS dans `hclient/` |
| Générations de code | Trois en parallèle : `admin/` (v3, « il marche, il n'est pas élégant »), `hserv/` + `hclient/` (v4 à v7), `srv/` (réécriture « h8 » en cours en 2026, PDO, espaces de noms, contrôleurs REST) |
| Tests automatiques | Aucun dossier de tests ; `package.json` : `"test": "no test specified"`. Les plans 2026 mentionnent quelques scripts de vérification ponctuels. |
| Multi‑bases | Une instance héberge des centaines de bases MySQL `hdb_*`, chacune avec sa propre structure |
| Licence | GPL‑3 |

---

## 2. Le modèle de données

### 2.1 Un modèle EAV dont l'utilisateur définit la structure

Heurist ne fixe pas de modèle métier. Il fournit un **méta‑modèle** dans lequel chaque base décrit le sien.

| Table | Rôle | Équivalent Chronologia |
|---|---|---|
| `Records` | Un enregistrement de n'importe quel type (`rec_RecTypeID`), titre calculé par un masque | Aucune table générique : chaque entité a sa table |
| `recDetails` | Une valeur de champ : `dtl_Value` (texte pour tout), `dtl_Geo`, `dtl_UploadedFileID`, **`dtl_Certainty`** (0 à 1), **`dtl_Annotation`**, `dtl_HideFromPublic` | Le FACTOÏDE porte l'information ; le degré est porté par l'IDENTIFICATION |
| `defRecTypes`, `defDetailTypes`, `defRecStructure` | Types d'enregistrement, « champs de base » réutilisables, structure de chaque type | Modèle fixe, documenté et gouverné par les règles R1 à R26 |
| `defTerms`, `defTermsLinks`, `defVocabularyGroups` | Vocabulaires hiérarchiques ; un terme peut être réutilisé dans plusieurs vocabulaires ; `trm_InverseTermID`, `trm_Code`, `trm_SemanticReferenceURL` | Schéma `ref` |
| `defRelationshipConstraints` | Quels types de relation entre quels types source et cible, avec limite d'usage | Contraintes rôle ↔ type d'événement (à écrire) |

### 2.2 Deux façons de relier : pointeur et relation réifiée

- **Pointeur** (`resource`) : un champ qui contient l'identifiant d'un autre enregistrement. Simple, sans attributs.
- **Relation** (`relmarker`) : un **enregistrement de type Relationship** à part entière, avec source, cible, type (un terme d'un vocabulaire de relations, avec son inverse), dates de début et de fin, notes, références. Il peut recevoir d'autres champs comme n'importe quel enregistrement.
- **`recLinks`** est un cache dénormalisé de tous les liens (pointeurs et relations), indexé dans les deux sens, pour la navigation et le réseau.

La documentation recommande la relation quand « les relations sont sujettes à interprétation » ou ont une durée, et l'**enregistrement intermédiaire** quand la relation porte trop d'attributs. C'est exactement notre choix de réifier la participation.

### 2.3 Le temps : un objet temporel riche

`hserv/utilities/Temporal.php` et `hclient/core/temporalObjectLibrary.js` définissent une date historique sérialisée en JSON dans `dtl_Value` :

- **Date simple** (`timestamp.in`) avec écart symétrique ou dissymétrique (`deviation`, `deviation_negative`, `deviation_positive`) et qualificatifs **circa / before / after**.
- **Intervalle flou** : `start` et `end`, chacun avec `in`, `earliest`, `latest`.
- **Profil** de probabilité de la borne : plat, central, montée lente, descente lente.
- **Mode de détermination** : inconnu, **attesté**, **conjecture**, **mesure** (datation physique).
- **Calendrier natif** conservé à côté de la conversion grégorienne. L'éditeur propose julien, hébreu, islamique, persan, copte, éthiopien, maya, népalais, thaï, taïwanais et japonais traditionnel (bibliothèque `jquery.calendars`). Le calendrier républicain n'y figure pas.
- **Datation radiométrique** (C14 : valeur, écart type) comme forme de date à part entière.
- Un **commentaire** libre.
- À chaque écriture, les bornes estimées sont recalculées en décimal `aaaa.mmjj` dans **`recDetailsDateIndex`** (`rdi_estMinDate`, `rdi_estMaxDate`) pour l'indexation et la recherche par période.

L'import CSV (`hserv/records/import/importDate.php`, 2026) applique une politique stricte : il **refuse plutôt que de deviner**. `1564/5` ou `1525-6` sont ambigus (année ou mois ?) et rejetés ; un **point d'interrogation est une preuve d'incertitude**, pas un bruit à nettoyer ; une année seule garde sa précision (`878` reste `0878`, jamais `0878-01-01`) ; `vers`, `avant`, `après` sont reconnus et conservés comme qualificatifs.

### 2.4 Historique, fusion, doublons

| Mécanisme | Fonctionnement |
|---|---|
| `sysArchive` | Image « avant » de chaque modification, table par table (brut, diff ou compressé), avec auteur et horodatage ; suppression « douce ». |
| `recForwarding` | Après fusion de deux enregistrements, l'ancien identifiant redirige vers le nouveau : les liens et URL publiés restent valides. |
| `recordsDupes.php` | Recherche de doublons par Levenshtein (seuil en % de longueur) ou métaphone sur des champs choisis, après nettoyage SQL (`NEW_LIPOSUCTION_255`). |
| `recSimilarButNotDupes` | Mémoire des groupes **déclarés non doublons** par l'utilisateur, pour ne plus les reproposer. |

La fusion elle‑même est **destructive** : un enregistrement absorbe l'autre.

### 2.5 Autres mécanismes notables

- **Concept codes** (`hserv/structure/ConceptCode.php`) : chaque type, champ, vocabulaire et terme reçoit un identifiant global `IdBaseOrigine-IdLocal` (ex. `2-109` pour l'annotation IIIF). Une base peut importer la structure d'une autre (« Browse templates ») et les exports XML restent interprétables d'une base à l'autre.
- **Résolveur de PID** (`redirects/resolver.php`) : point d'entrée unique et stable vers un enregistrement, une valeur ou une définition, avec suffixe de version (`_V1`) pour faire évoluer le format sans casser les appelants.
- **Étapes de workflow** (`sysWorkflowRules`) : changer l'étape d'un enregistrement change son propriétaire, sa visibilité, et envoie des courriels.
- **Droits** : propriétaire (utilisateur ou groupe) et visibilité par enregistrement (`hidden`, `viewable`, `public`, `pending`) ; masquage d'un champ au public, par valeur.
- **Recherche** : langage de requête JSON ou texte (`t:12 f:237:… linked_to:…`), facettes multi‑niveaux, règles d'expansion de réseau, et en 2026 un traducteur requête → phrase lisible (`QueryDescriber`, plan `documentation/development/query-language-filter-builder-plan.md`).
- **Lookups externes** (`hclient/widgets/lookup/`, `LookupConfigs.json`) : GeoNames, BnF, ISNI, ESTC, Nomisma, Nakala, **Opentheso**… depuis le formulaire de saisie, avec un mappage déclaratif champ externe → champ local.
- **Visualisation** : carte Leaflet couplée à une frise chronologique (`viewers/map/`), graphe de connexions, tableau croisé, rapports Smarty, sites web CMS générés depuis la base.
- **Interopérabilité** : export **RO‑Crate 1.2**, **IIIF Presentation v3** et **Web Annotations** (mode « surcouche d'annotations » sur des manifestes externes, compatible Mirador), JSON, XML (HML), KML, CSV, synchronisation Zotero, dépôt Nakala, **score FAIR** indicatif calculé par base.
- **Champs calculés** : formules Smarty attachées à un champ, avec règles de rafraîchissement (`documentation/calculated-record-links.md`).

---

## 3. Points forts

1. **Maturité et adoption française.** Vingt ans d'usage, des dizaines de projets en histoire, archéologie, histoire de l'art, hébergés gratuitement par Huma‑Num. C'est l'outil que beaucoup de nos utilisateurs potentiels connaissent déjà.
2. **Un modèle temporel pensé pour l'histoire.** Bornes floues, profil, mode de détermination, calendrier natif, commentaire : c'est plus complet que la plupart des SGBD de recherche, et plus que notre §5.6 actuel.
3. **Relations réifiées et typées par vocabulaire**, avec termes inverses et contraintes de types : la bonne réponse au problème de la relation qui porte des attributs.
4. **Incertitude au niveau de la valeur** : `dtl_Certainty` et `dtl_Annotation` existent dans le schéma pour chaque valeur.
5. **Identifiants stables à toutes les échelles** : concept codes pour la structure, `recForwarding` et résolveur versionné pour les enregistrements.
6. **Mémoire des refus de dédoublonnage** (`recSimilarButNotDupes`) : l'outil n'insiste pas sur une paire déjà rejetée.
7. **Import prudent des dates** : refuser plutôt que deviner, garder la précision déclarée.
8. **Ouverture sur l'écosystème** : IIIF v3 et Web Annotations, RO‑Crate, Opentheso, Nakala, GeoNames, score FAIR.
9. **Carte et frise couplées**, sites de publication générés depuis la base.
10. **Souplesse** : la structure se modifie à chaud sur une base vivante, et se partage entre bases.

## 4. Points faibles

1. **EAV « tout texte ».** Toute valeur est un `text` dans `recDetails`, y compris les dates (du JSON dans une chaîne). Les contraintes d'intégrité sont applicatives ; les index utiles sont des **caches** (`recLinks`, `recDetailsDateIndex`) entretenus par le code et reconstruits quand un chemin d'écriture les contourne.
2. **Pas de distinction entre ce qui est écrit et ce que l'on conclut.** Une valeur de champ est une assertion sans source propre : la source se modélise à la main par des pointeurs, la provenance n'est pas structurelle. Il n'y a ni factoïde, ni masque, ni identification révisable.
3. **Certitude décorative.** `dtl_Certainty` n'est quasiment pas exploitée : neuf occurrences dans tout le code, toutes en copie ou en synchronisation, aucune dans la recherche ou l'affichage. Une incertitude qui ne pèse sur rien n'est qu'un commentaire.
4. **Fusion destructive.** Fusionner deux personnes en efface une (la redirection garde l'URL, pas le raisonnement). Revenir sur une identification erronée passe par l'archive brute.
5. **Archive générique, pas audit métier.** `sysArchive` stocke des images de lignes ; on sait qu'une valeur a changé, pas **pourquoi**, ni quelle conclusion l'a justifiée.
6. **Dépendance forte à MySQL** (FULLTEXT, fonctions spatiales, fonctions SQL maison). La couche `srv/` prépare d'autres pilotes (PostgreSQL, SQLite) mais le SQL généré cible toujours MySQL.
7. **Dette technique visible.** Trois générations de code coexistent, des fichiers de 4 000 à 5 000 lignes (`recordSearch.php`, `recordModify.php`), état global, jQuery UI, **aucune suite de tests automatiques**. La réécriture `srv/` n'écrit encore que les types système.
8. **Logique métier dans des gabarits.** Champs calculés et rapports en Smarty, avec des règles de dépendance opt‑in par commentaire spécial : puissant mais fragile et difficile à vérifier.
9. **Souplesse sans garde‑fous.** Chaque base invente son modèle ; deux projets prosopographiques sur Heurist sont rarement comparables. Les règles du type R2 ou R11 ne peuvent pas être imposées par le moteur.
10. **Petite équipe**, financement associatif, suivi des tickets dans une base Heurist plutôt que sur GitHub : un risque pour un projet qui voudrait en dépendre.

---

## 4 bis. Ergonomie et intuitivité

Sources : chapitres 2, 4, 5, 7 et 7a de *Understanding Heurist v7* (`documentation/Understanding_Heurist_Vsn_7/`), et les widgets `hclient/widgets/editing/`, `record/`, `entity/`, `lookup/`. La version 6 (2021) a été refondue avec un designer UX professionnel. L'interface reste toutefois une application jQuery UI de fenêtres et de dialogues.

### 4 bis.1 Ce qui marche bien

| Fonction | Ce qu'elle apporte à l'utilisateur |
|---|---|
| **Cinq menus par activité** : *Design*, *Populate*, *Explore*, *Publish*, *Admin* | L'utilisateur s'oriente par ce qu'il veut faire, pas par la structure technique. |
| **Base pré‑remplie** de types courants (Personne, Lieu, Média…) et import de modèles d'autres bases | Une première base utilisable en une demi‑journée, sans page blanche. |
| **Le formulaire de saisie sert aussi à modifier la structure** (*Modify structure*), avec le nombre d'usages de chaque champ et un lien vers les enregistrements qui l'ont ou ne l'ont pas | On modélise au fil de la saisie, et on repère les champs inutilisés lors de la reprise de données anciennes. |
| **Trois niveaux de champs** (obligatoire, recommandé, optionnel), optionnels masquables, **aide affichée sous chaque champ**, onglets, séparateurs et blocs de texte explicatif dans le formulaire | Le formulaire guide sans tout montrer d'un coup. |
| **Création à la volée** : un terme manquant s'ajoute depuis la liste déroulante ; la cible d'un pointeur peut être créée depuis le sélecteur, comme enregistrement provisoire (`rec_FlagTemporary`) | On ne quitte pas l'acte en cours pour créer une personne ou un lieu. |
| **Titre construit** (masque de titre) affiché partout : listes, pointeurs, relations | Chaque enregistrement est reconnaissable d'un coup d'œil sans être ouvert. |
| **Éditeur de dates à onglets** : date simple, intervalle simple, intervalle flou, datation radiométrique ; choix du calendrier ; taper l'année fait sauter le calendrier à cette année | Les formes de dates historiques sont toutes saisissables au même endroit. |
| **Panneau latéral « Record summary »** : propriétaire, visibilité, auteur, dates, **liens entrants cliquables**, **historique avec retour à une version** | Le contexte d'un enregistrement est toujours à un clic, et une erreur se défait. |
| **Précédent / suivant** dans l'ensemble de résultats depuis le formulaire | La relecture d'une série se fait sans retour à la liste. |
| **Recherche à trois niveaux** : boîte de recherche avec mots‑clés (`type:`, `field:`…), **assistant de filtre** qui suit les liens entre types, **constructeur de facettes** (avec curseur temporel) ; filtres enregistrés et rangés **par groupe de travail** ; en 2026, **paraphrase de la requête en phrase** | Le débutant clique, l'expert tape, et chaque équipe a ses filtres prêts. |
| **Vérification d'intégrité graduée** (*Verify integrity*) : problèmes classés par gravité et expliqués (« une base avec des avertissements n'est pas forcément inutilisable »), dates ambiguës signalées | La qualité des données devient lisible et traitable, sans alarme inutile. |
| **Menu *Recode*** : ajouter, remplacer, supprimer une valeur, relier, changer de type, convertir… sur une sélection | Les corrections en série se font sans SQL. |
| **Signalement d'un problème depuis l'interface**, avec le contexte technique joint automatiquement | Moins d'allers‑retours avec le support. |
| Visite guidée (`documentation/guidedIntroTour.js`), aide contextuelle par écran, interface en six langues (dont le français) | Une prise en main possible sans formation. |

### 4 bis.2 Ce qui freine

| Constat | Effet sur l'utilisateur |
|---|---|
| **Le méta‑modèle est exposé** : type d'enregistrement, champ de base, pointeur, *relationship marker*, masque de titre, concept code. La documentation consacre des pages entières au choix « pointeur ou relation ». | L'historien doit devenir modélisateur avant de saisir. Deux projets voisins font des choix différents. |
| **Fenêtres et dialogues empilés** ; plusieurs onglets sur la même base **ne se synchronisent pas** (la documentation conseille de recharger après un changement de structure) | On se perd dans les couches, et on peut travailler sur une structure périmée sans le savoir. |
| **Affordances trompeuses** : le bouton *Save* paraît désactivé mais reste cliquable (et il est parfois nécessaire de cliquer dessus pour recalculer le titre) | L'interface ment sur ce qu'elle permet. |
| **Fonctions mortes encore visibles ou documentées** (Discussion « dépréciée », icône de signet disparue, étiquettes déconseillées par la doc elle‑même) | Du bruit, et des fonctions qu'on essaie pour rien. |
| **Éditeur de dates en jargon** : TPQ/TAQ, PDB/PDE, écart type, profils « Slow start / Slow finish », « Central tendancy » | Les formes riches ne sont utilisées que par les experts ; les autres tapent une date simple et perdent l'incertitude. |
| **Relation saisie dans une fenêtre à part**, comme un enregistrement relation ; la certitude d'une valeur n'apparaît nulle part dans l'interface | L'incertitude existe dans le schéma mais pas dans le geste de saisie, donc elle n'est pas saisie. |
| **Opérations en série sans aperçu ni annulation groupée** décrits par la documentation ; l'historique se défait enregistrement par enregistrement ; on conseille une sauvegarde avant certains recalculs | Les corrections en masse font peur, ou font des dégâts. |
| **Doublons présentés en liste** (score de distance), sans comparaison côte à côte des écarts ni motif de décision | Le dédoublonnage reste une corvée d'expert. |
| **Changer le type d'un enregistrement réaffecte les valeurs** à d'autres champs automatiquement | Une transformation silencieuse, difficile à vérifier. |
| **Accessibilité faible** : environ 140 attributs `aria-*` ou `role` pour 190 000 lignes de JS client | Lecteurs d'écran et navigation au clavier mal servis ; incompatible avec les exigences RGAA d'un service public. |
| **Mise en forme personnalisée par gabarits Smarty (`.tpl`)** : fiche d'un enregistrement, vue « carte » d'une liste, bulle sur la carte, rapport, page publique (`/tpl/nom/75`). On écrit du HTML mêlé de balises Smarty (`{foreach $results as $id}`, `{$heurist->getRecord($id)}`, `{$r.f12}` où 12 est l'identifiant numérique du champ). Un arbre des champs et des menus d'insertion aident, mais la documentation prévient que « le développement de rapports peut être assez lent » et qu'il faut du HTML, idéalement du CSS. **CSS et JS sont désactivés par défaut** (sécurité) : les gabarits fournis passent tout en styles en ligne, et l'autorisation saute si l'on renomme ou clone la base. La mise en page des **sites web** passe, elle, par un gabarit **PHP** déposé sur le serveur (`hclient/widgets/cms/templates/cmsTemplate.php`), donc hors de portée de l'utilisateur. | Une couche de programmation entre l'historien et l'affichage de ses données. Chaque projet finit par dépendre de la personne qui « sait faire les tpl », et un changement de structure (champ renommé ou supprimé) casse silencieusement les gabarits. Les thèmes et en‑têtes de site prédéfinis ajoutés en novembre 2026 (commit `0375efd77`) montrent que l'équipe cherche à réduire ce recours. |

---

## 5. Ce que Chronologia peut reprendre

Classement : **A** = à reprendre tôt, s'insère dans la feuille de route actuelle ; **B** = utile, plus tard ; **C** = idée à garder en mémoire.

### 5.1 Le temps (A)

| Reprise | Adaptation dans Chronologia | Règle |
|---|---|---|
| **Mode de détermination** (attesté / conjecture / mesure / inconnu) | Champ sur l'intervalle du FACTOÏDE ou de la CONTRAINTE_TEMPORELLE. Un factoïde dont la date est **déduite** (« âgé de 30 ans » → naissance vers 1680) n'est pas une date **attestée** : la distinction doit être visible et pondérer le rapprochement. | R5, R23 |
| **Calendrier natif conservé** à côté de la conversion | Ajouter `calendrier` (grégorien, julien, **républicain**) et garder la date native dans `date_brute`. Le républicain manque chez Heurist et compte pour les registres de 1793 à 1805. | R5, R10 |
| **Bornes `earliest` / `latest` pour le début et la fin** | Notre CONTRAINTE_TEMPORELLE a déjà début min/max et fin min/max ; garder ce vocabulaire à quatre bornes partout (factoïde compris). | R5 |
| **Index des bornes estimées** | En PostgreSQL, ne pas reproduire un cache décimal : une colonne `daterange` (ou deux colonnes `date`) indexée en GiST, calculée en base. | — |
| **Politique d'import « refuser plutôt que deviner »** (`importDate.php`) | À appliquer au connecteur GeneWeb et à la saisie assistée : les formes ambiguës (`1564/5`, `?`) partent dans la file de décisions avec la chaîne d'origine, jamais normalisées en silence. | R18, R24 |
| Profil de probabilité (plat, central…) | **C** : utile seulement si l'on calcule des densités ; pas maintenant. | — |

### 5.2 Relations et vocabulaires (A)

| Reprise | Adaptation | Règle |
|---|---|---|
| **Termes inverses** (`trm_InverseTermID`) | Pour les rôles durables binaires (parrain ↔ filleul, père ↔ enfant), stocker l'inverse dans `ref` plutôt que de dupliquer les lignes. | — |
| **Contraintes de relation** (`defRelationshipConstraints`) | Table `ref` qui dit quels rôles sont admis pour quel type d'événement et quel type de participant ; contrôle à l'écriture et dans la file de décisions. | R2 |
| **Vocabulaires hiérarchiques à termes partagés**, avec `code` et `uri_semantique` | Structure du schéma `ref` : un terme a un code (pour l'import GeneWeb), une URI (Opentheso, CIDOC‑CRM, Wikidata) et peut appartenir à plusieurs vocabulaires. La **fusion de termes** qui réaffecte les usages est à prévoir. | — |
| Le **cache des liens** (`recLinks`) | Vue matérialisée « réseau » calculée depuis les identifications actives (déjà prévue en §8.1), plutôt qu'un cache entretenu par le code. | R11 |

### 5.3 Rapprochement et identification (A)

| Reprise | Adaptation | Règle |
|---|---|---|
| **Mémoire des non‑doublons** (`recSimilarButNotDupes`) | Déjà acquis par R26 pour MASQUE → PERSONNE : un couple qui porte une identification, même rejetée, n'est pas reproposé. Reste à l'étendre aux événements, lieux et sources quand leurs rapprocheurs existeront (voir §9, point 3). | R26, R24 |
| Comparaison par Levenshtein / métaphone sur valeurs nettoyées | Indice parmi d'autres dans le faisceau ; prévoir une phonétique adaptée au français ancien plutôt que le métaphone anglais. | R26 |
| **Redirection d'identifiant** (`recForwarding`) | Quand une PERSONNE publiée disparaît parce que ses masques sont réattribués, garder une redirection de son identifiant public vers la ou les personnes héritières. | R22 |
| **Contre‑exemple** : la fusion destructive | Ne pas reprendre. Chez nous, fusionner = créer des identifications ; défaire = retirer une conclusion. C'est notre principal avantage sur Heurist et il faut le montrer dans les démonstrations. | R11, R22 |

### 5.4 Identifiants, publication et interopérabilité (B)

| Reprise | Adaptation |
|---|---|
| **Concept codes** `base-id` | Donner aux entrées de `ref` un identifiant global stable (préfixe du projet + identifiant local). Aide pour la question ouverte 9.2‑2 (plusieurs équipes) et la publication RDF (9.2‑3). |
| **Résolveur de PID versionné** | Une route `/id/{type}/{id}` stable, et des formats de sortie suffixés (`/v1`) pour pouvoir changer le JSON sans casser les liens externes. |
| **IIIF v3 + Web Annotations** | Le PASSAGE a un `image_uri` : le modéliser comme une **cible d'annotation** (canevas + zone) rend Chronologia compatible avec Mirador et eScriptorium (question 9.2‑8). Reprendre le mode « surcouche » : le fournisseur garde le manifeste, nous gardons les annotations. |
| **RO‑Crate** | Format d'archivage et de dépôt (Nakala, Zenodo) d'un lot d'import ou d'un état publié : métadonnées, schéma, données, provenance. |
| **Score FAIR** auto‑évalué | Petit diagnostic interne (sources liées, URI des référentiels, licence, visibilité) ; utile pour les dossiers de financement. |

### 5.5 Saisie, référentiels externes, workflow (B)

| Reprise | Adaptation | Règle |
|---|---|---|
| **Lookups externes déclaratifs** (`LookupConfigs.json`) | Même principe pour les lieux et les vocabulaires : GeoNames, IGN, DicoTopo, COG INSEE, Opentheso, BnF/ISNI pour les personnes connues. Un résultat de lookup est une **proposition**, versée par l'humain. | R18 |
| **Session d'import persistante** (`sysImportFiles`) | Notre lot d'import a déjà son empreinte SHA‑256 ; garder aussi l'état de la file de décisions d'un lot pour reprendre une validation interrompue. | — |
| **Étapes de workflow** (`sysWorkflowRules`) | Étapes d'un acte ou d'un lot : déposé → transcrit → factoïdes proposés → validé. Changer d'étape peut changer la visibilité et prévenir un relecteur. | R18 |
| **Visibilité par valeur et par enregistrement** | Indispensable pour les témoignages de personnes vivantes (9.2‑7) : marquer factoïdes et passages non publiables, et le faire vérifier par le subagent `gardien-regles`. | R24 |

### 5.6 Recherche et visualisation (B)

| Reprise | Adaptation |
|---|---|
| **Langage de requête JSON compilé** + **traduction en phrase lisible** | Une API de requête sur les vues actives (« personnes ayant un rôle de parrain dans un baptême à Saint‑Aubin entre 1700 et 1720 ») et sa paraphrase en français dans l'interface : l'utilisateur vérifie ce qu'il demande. |
| **Expansion de chemins** (`ExpansionEngine` : lié depuis / vers / en relation avec) | Parcours du réseau personne → événement → personne, base de l'écran « fiche consolidée ». |
| **Facettes multi‑niveaux** | Filtrer par type d'événement, période, lieu historique, degré d'identification. |
| **Carte et frise couplées** | Déjà dans nos maquettes (§6.4) ; le code Heurist (`viewers/map/timeline.js`) montre qu'une frise vis.js + Leaflet suffit. |

### 5.7 Méthode et documentation (C)

- Un `_README.md` par dossier qui dit le rôle du dossier et de ses fichiers : convention simple, utile aux agents comme aux humains.
- Des **plans de travail vivants** dans le dépôt (statut, prochaine action, décisions) : c'est ce que fait déjà notre `AGENTS.md`.
- L'aide en ligne stockée **dans une base** de l'outil lui‑même : à envisager pour la documentation des vocabulaires.

### 5.8 Ergonomie (A pour les écrans 2 et 3, B pour le reste)

| Reprise | Adaptation dans Chronologia | Écran (§6.1) |
|---|---|---|
| **Création à la volée** depuis un champ (terme, personne, lieu) | Depuis la fiche d'acte, un nom non reconnu crée un **masque**, pas une personne : on ne demande jamais à l'historien de conclure pendant la saisie. Un lieu inconnu crée une MENTION_LIEU en attente de rattachement. | 2 |
| **Titre construit** partout | Libellé lisible et calculé pour chaque masque, factoïde et personne (« Jean Mercier, baptisé le 3 mai 1712 à Saint‑Aubin »), utilisé dans les listes, la file de décisions et les liens. | 2, 3 |
| **Trois niveaux de champs** et **aide sous le champ** | Seuls les champs incertains ou déduits demandent une action (déjà prévu) ; les autres sont repliés. L'aide explique la règle en jeu en une phrase, avec un lien vers le §. | 2 |
| **Éditeur de dates complet**, mais **sans le jargon** | Garder la richesse (bornes, détermination, calendrier) derrière une saisie en langue naturelle : on tape « vers 1680 », « avant la Saint‑Martin 1712 », « 12 floréal an II », l'outil affiche l'intervalle compris et demande confirmation. Les termes TPQ/TAQ n'apparaissent jamais. | 2, 4 |
| **Panneau de contexte** (liens entrants, historique, propriétaire) | Panneau latéral « d'où vient cette donnée » : passage, image, auteur de la saisie, identifications actives et rejetées, conclusions. Le retour en arrière y passe par le retrait d'une conclusion, pas par une version brute. | 2, 3 |
| **Précédent / suivant** dans une série | Enchaîner les actes d'un lot et les décisions de la file au clavier, sans retour à une liste. | 2, 3 |
| **Recherche à trois niveaux** (boîte, assistant, facettes) **et paraphrase** | Boîte de recherche simple, assistant guidé, facettes ; la requête est toujours **relue en français** au‑dessus des résultats. Filtres enregistrés par équipe. | 5 |
| **Contrôle de qualité gradué et expliqué** | Tableau de bord des incohérences (baptisé après décès, âge impossible, dates ambiguës) classées par gravité ; chaque ligne mène à l'écran de décision qui la résout. | 3, 4 |
| **Corrections en série** (*Recode*) | Oui, mais avec **aperçu** avant application et **annulation groupée** (une conclusion de lot qu'on peut retirer), ce que Heurist n'offre pas. | — |
| **Signalement depuis l'interface** avec contexte joint | Bouton « signaler » qui joint l'écran, l'objet et la version ; utile pendant l'expérimentation sur les 50 actes. | toutes |
| **Visite guidée** et interface traduite | Visite courte par écran ; interface en français d'abord, chaînes externalisées dès le début. | toutes |
| **Vues personnalisables** (contre‑modèle : gabarits Smarty) | Garder le besoin, changer de moyen. Les affichages courants (fiche de personne, fiche d'acte, carte de vie, liste) sont des **composants livrés**, réglables par options : champs montrés, ordre, libellés, thème. Pour aller plus loin, un **éditeur visuel de mise en page** (glisser les blocs, aperçu en direct sur une vraie fiche) qui produit une configuration déclarative (JSON), jamais du code. Les champs y sont désignés par leur nom, pas par un numéro, et l'outil signale un gabarit cassé par une évolution du modèle. Les exports texte (citations, notices) passent par quelques formats prédéfinis plutôt que par un langage de gabarits. | 5 |

Leçons tirées des freins de Heurist (4 bis.2) :

1. **Cacher le modèle, montrer la source.** L'historien manipule des actes, des noms et des décisions ; les mots « masque », « factoïde », « identification » peuvent rester dans la documentation et les infobulles, pas dans les boutons.
2. **Une seule fenêtre de travail**, avec panneaux, plutôt que des dialogues empilés ; état synchronisé entre onglets (notification quand une donnée affichée a changé).
3. **Des boutons qui disent la vérité** : actif = utile, désactivé = impossible, avec la raison au survol.
4. **L'incertitude dans le geste.** Le degré se choisit au moment de la décision (certain / probable / possible en un clic, avec motifs), jamais dans un champ numérique annexe.
5. **Comparer plutôt que lister** pour les rapprochements : écarts seulement, indices du score, frise (déjà §6).
6. **Rien de silencieux** : aucune réaffectation automatique de valeurs sans écran de vérification.
7. **Personnaliser sans programmer** : la mise en forme se règle par options et par un éditeur visuel avec aperçu, pas par un langage de gabarits (voir la ligne « Vues personnalisables »).
8. **Accessibilité dès les maquettes** : navigation au clavier, contraste, alternatives textuelles aux codes couleur (déjà en partie : contrôle en niveaux de gris, §6.4), objectif RGAA.

---

## 6. Ce qu'il ne faut pas reprendre

| Choix Heurist | Pourquoi l'éviter dans Chronologia |
|---|---|
| Méta‑modèle EAV modifiable par l'utilisateur | Nos règles R1 à R26 supposent un modèle fixe. La souplesse se loge dans les vocabulaires de `ref`, pas dans la structure. |
| Valeurs et dates stockées en texte, index en caches applicatifs | PostgreSQL offre `daterange`, GiST, PostGIS, contraintes et triggers : l'intégrité doit être en base (R10 est déjà garantie par triggers). |
| Certitude en colonne libre sur la valeur | L'incertitude doit être **structurelle** et agir sur les calculs : degré d'identification, intervalle, mode de détermination. |
| Fusion destructive avec redirection | Remplacée par l'identification révisable ; seule la redirection d'identifiant public est à reprendre. |
| Archive en images de lignes | Notre audit relie chaque changement à une conclusion ; c'est ce qui rend le retrait possible (R22). |
| Logique dans des gabarits (Smarty, formules) | Calculs en vues SQL et en services Python testés. |
| Mise en forme par gabarits `.tpl` (Smarty) et site par gabarit PHP | Réservé aux initiés et fragile face aux évolutions du modèle ; remplacé par des composants configurables et un éditeur visuel (5.8). |
| Absence de tests | Le gardien des règles et les tests de scénarios restent la condition d'avancement. |
| Structure modifiable depuis le formulaire de saisie | Mélange deux métiers (saisir, modéliser) ; chez nous, une évolution du modèle passe par `/decision-modele`. |
| Fenêtres empilées, jargon de modélisation dans l'interface | Voir 5.8 : une fenêtre de travail, le vocabulaire des sources dans les boutons. |

---

## 7. Heurist comme voisin plutôt que comme concurrent

Beaucoup de projets français ont déjà leurs données dans Heurist sur Huma‑Num. Deux passerelles valent d'être étudiées après le socle PostgreSQL :

1. **Connecteur d'import Heurist → Chronologia**, sur le modèle du connecteur GeneWeb : lire l'export JSON/XML (HML) ou l'API REST `srv/` (`/api/{db}/records`, `/api/{db}/def/snapshot` pour la structure), traiter chaque valeur de champ comme un **factoïde** rattaché à un **passage** fictif « base Heurist X, enregistrement N », et chaque enregistrement Personne comme un **masque**. Les relations Heurist deviennent des factoïdes de participation, leur `dtl_Certainty` une indication de degré. Les dates JSON de Heurist se transposent presque directement vers nos intervalles.
2. **Export Chronologia → Heurist** pour la publication : générer, depuis les vues actives, des enregistrements Heurist (CSV ou HML) afin d'utiliser ses sites CMS et ses cartes hébergés par Huma‑Num, sans réécrire de couche de publication. L'export est appauvrissant (comme vers GeneWeb, §5.8) et doit le dire.

---

## 8. Proposition de calendrier, alignée sur la feuille de route

| Étape Chronologia (CLAUDE.md) | Reprises Heurist à intégrer |
|---|---|
| 1. Validation des propositions, calibration du barème | Mémoire des refus (5.3) ; phonétique comme indice ; test « une paire rejetée n'est pas reproposée » |
| 2. Socle PostgreSQL et tests des règles | Intervalle à quatre bornes + mode de détermination + calendrier (5.1) ; termes inverses et contraintes de rôles (5.2) ; vues réseau |
| 3. Lieux | Lookups déclaratifs GeoNames / DicoTopo / COG (5.5) ; identifiants globaux des entrées `ref` (5.4) |
| 4. Saisie assistée | Politique d'import « refuser plutôt que deviner » (5.1) ; PASSAGE comme cible IIIF (5.4) |
| 5. Écrans | Requête paraphrasée, facettes, carte + frise (5.6) ; visibilité publique (5.5) ; création à la volée de masques, titres construits, saisie des dates en langue naturelle, panneau « d'où vient cette donnée », navigation au clavier, accessibilité (5.8) |
| Après | Connecteurs Heurist dans les deux sens (7) ; RO‑Crate, score FAIR |

## 9. Décisions (consignées le 9 novembre 2026)

1. **Mode de détermination** de la date : **retenu**, décision 23 du document de référence (v0.9.4), champ `determination_date` (attestée, déduite, estimée, inconnue), sans nouvelle règle.
2. **Calendrier** en liste fermée, dont le républicain : **retenu**, décision 23 (le champ `calendrier` existait déjà).
3. **Non‑reproposition d'une paire rejetée** : déjà couverte par **R26** (« un couple masque–personne qui porte déjà une identification, quels qu'en soient le statut et l'auteur, n'est pas reproposé »). **Retenu** sous la forme de **R27** (décision 25) : le principe s'étend aux quatre agrégations ; un indice nouveau est montré à l'historien, qui seul peut rouvrir la question.
4. **Connecteurs Heurist** (import et export) : **retenus**, décision 24, après le socle PostgreSQL.

---

## Annexe : correspondances de concepts

| Heurist | Chronologia | Écart principal |
|---|---|---|
| Record (type Person) | PERSONNE, ou MASQUE si l'enregistrement reproduit une source | Heurist ne distingue pas le nom écrit de la personne conclue |
| Valeur de champ (`recDetails`) | FACTOÏDE | Pas de source propre, pas de statut |
| `dtl_Certainty` | Degré de l'IDENTIFICATION | Numérique et inerte chez Heurist, qualitatif et agissant chez nous |
| Relationship record | Participation réifiée / rôle durable | Équivalent proche |
| Vocabulaire de relations + inverse | Vocabulaire des rôles (`ref`) | Équivalent |
| Objet temporel | Intervalle du factoïde + `date_brute` + CONTRAINTE_TEMPORELLE | Heurist a en plus détermination, profil, calendrier natif |
| Place + `dtl_Geo` | SITE / LIEU_HISTORIQUE / EMPRISE | Heurist n'a pas de lieu daté |
| `sysArchive` | `audit_*` + conclusions | Image brute contre raisonnement tracé |
| `recForwarding` | Redirection d'identifiant public (à créer) | Fusion destructive contre identification |
| `recSimilarButNotDupes` | Identification au statut rejeté | Équivalent fonctionnel |
| Concept code | Identifiant global des entrées `ref` (à créer) | — |
| Workflow stage | Étape d'un acte ou d'un lot (à créer) | — |
