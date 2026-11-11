# Projet Hesdin 1872-1911 : Chronologia à l'épreuve d'un vrai terrain

Document de conception, 11 novembre 2026. Statut : à approuver.

Ce document a deux étages :

1. le **cadre** du projet entier (sections 1 à 7), valable pour tous les chantiers ;
2. la conception détaillée du **premier chantier** seulement : inventaire et jeu étalon (section 8).

Les chantiers suivants feront chacun l'objet d'une conception à part, qui s'appuiera sur ce cadre.

Convention : ce qui a été **décidé par le chercheur** est marqué (D). Ce qui est **un choix de conception** fait en rédigeant, révisable, est marqué (C).

---

## 1. Intention

Construire et valider Chronologia en menant une vraie étude d'histoire sociale, sur du volume, plutôt que sur des exemples choisis (D). Le logiciel progresse parce qu'il bute sur des sources réelles. L'étude progresse parce que le logiciel lui retire la copie (doctrine §1.1 du document de référence).

L'étude porte sur la population de **Hesdin** (Pas-de-Calais, environ 3 000 habitants) entre **1872 et 1911** (D). **Saint-Omer** (environ 20 000 habitants) sert de **corpus témoin** (D) : on vérifie que la chaîne construite pour Hesdin tient sans réglage spécifique.

## 2. Questions d'histoire

1. **Démographie.** Comment la population évolue-t-elle (natalité, mortalité, nuptialité, migrations, structure des ménages) ? Ces évolutions suivent-elles celles de la région et de la France ? (D)
2. **Reproduction sociale.** Les enfants des familles aisées restent-ils aisés ? Même question pour les autres couches de la population. (D)

La position sociale se lit d'abord par la **profession et la domesticité** (D), relevées dans les actes et les recensements. Une **source fiscale ou successorale** viendra ensuite, sur un échantillon de familles (D). Dans la presse, on relève les **licitations, faillites, ventes et adjudications** (D).

Le projet couvre une génération : 1872-1911 (D). Pour ancrer les grands-parents, on remonte dans l'état civil antérieur à 1872 **pour tous les ménages du recensement de 1872, autant que possible** (D). Un ménage qu'on ne peut pas remonter n'est jamais écarté en silence : il devient une **lacune motivée** (décision 39, R24).

## 3. Objectifs, non-objectifs, anti-objectifs

**Objectifs**
- Faire passer à Chronologia l'épreuve du volume : environ 8 000 actes et 27 000 lignes de recensement pour Hesdin (estimation (C), à confirmer par l'inventaire).
- Mesurer à chaque étape ce que vaut la machine (reconnaissance d'écriture, extraction, rapprochement) contre un jeu étalon humain.
- Produire des résultats d'histoire comparables, grâce à des nomenclatures standard.

**Non-objectifs**
- Une base généalogique complète de Hesdin.
- Une transcription parfaite de chaque acte. Le seuil d'erreur acceptable se mesure, il n'est pas nul.
- Une réécriture des recensements que Socface a déjà transcrits.

**Anti-objectifs** (échec même si « ça marche »)
- **Un logiciel qui ne sait faire que Hesdin.** Fonctions, tables ou règles taillées pour ce corpus (D, principal risque identifié par le chercheur).
- **Des résultats biaisés par la sélection.** Familles faciles ou intéressantes mieux suivies que les autres, émigrés qui disparaissent sans qu'on le voie.
- **Des chiffres sans hypothèses.** Un comptage qui ne dit pas ce qu'il exclut (R29).
- **La machine qui verse sans mesure** au-delà de ce qui a été contrôlé (R18, R33).

## 4. Contraintes

### 4.1 Temps humain
- **20 minutes par jour, six jours par semaine** (pas le samedi), par le chercheur seul (D). Cela fait environ 2 heures par semaine et 100 heures par an.
- Conséquence (C) : impossible de tout relire. La **délégation mesurée (R33, §7.11)** devient le mode normal. Le chercheur relit un échantillon aléatoire et les cas douteux. Au-delà, la machine ne verse qu'en « probable » et seulement là où son taux d'erreur mesuré passe sous un seuil fixé à l'avance. Un contrôle qui dépasse le seuil suspend la délégation d'office.
- Conséquence (C) : chaque séance doit être utile tout de suite. La file de décisions est prête et triée, et on reprend exactement là où on s'est arrêté.
- Les séances se passent **au bureau et sur téléphone ou tablette** (D). L'écran de relecture doit donc fonctionner dans un navigateur, sur les deux formats.

### 4.2 Sources (état de la reconnaissance, novembre 2026)

| Source | Accès | À savoir |
|---|---|---|
| État civil Hesdin (N/M/D) | Portail des AD62, visionneuse | Couverture annoncée « 1793 à 1912 environ ». Les années 1883-1914 de Hesdin sont **à vérifier**. Les tables décennales sont numérisées : ce sont des index exhaustifs. |
| Recensements 1872, 1876, 1881, 1886, 1891, 1896, 1901, 1906, 1911 | Images aux AD62 ; transcription **Socface** sur FranceArchives | Socface annonce 15 à 20 % d'erreurs. La couverture du Pas-de-Calais, la licence et le téléchargement en masse sont **à vérifier**. Les numéros de page ne correspondent pas toujours aux images. |
| Presse, Hesdin | Gallica, AD62 | Aucun titre local numérisé trouvé. Il faudra passer par la presse d'arrondissement (Montreuil) ou départementale. |
| Presse, Saint-Omer | Gallica, bibliothèque d'agglomération | Numérisation en cours (*Mémorial artésien*, *Coin de terre et du foyer*, plan DRAC 2023). |
| Arbres publics Geneanet | Consultation | **Témoin extérieur, pas une source** (C). Comparaison à la main sur échantillon, car les conditions d'utilisation interdisent l'aspiration automatique. |

### 4.3 Droit et confidentialité
- Les actes ont tous plus de 75 ans, donc ils sont communicables.
- Les AD62 autorisent le téléchargement gratuit en PDF. Le JPEG est payant, et une licence avec redevance existe pour l'usage commercial. Un usage de recherche non commercial et un stockage sur serveur privé sont **à confirmer auprès des AD62** avant tout stockage d'images sur le serveur.
- Les garde-fous existants (`AGENTS.md`) s'appliquent : **aucune donnée nominative réelle dans le dépôt Git**, ni dans les journaux ou les comptes rendus. Les données du projet vivent dans un répertoire de données à part, hors du dépôt (C, section 8.4).

### 4.4 Règles du modèle les plus exposées
R2, R10, R13 (couche Source fidèle et immuable), R18 et R26 (la machine propose), R24 (rien en silence), R29 (comptages), R33 (délégation mesurée), R34 (relecture qui s'ajoute). Toute décision de modèle née du projet se consigne d'abord dans le document de référence, comme d'habitude.

## 5. Choix de mise en œuvre

| Choix | Statut |
|---|---|
| Hesdin pour construire, Saint-Omer en témoin | (D) |
| Recensements : **Socface comme première lecture**, à relire et à mesurer, pas de transcription maison | (D) |
| État civil : chaîne maison, image → reconnaissance d'écriture → extraction par modèle de langage → brouillon (schéma `saisie`) → validation | (D) |
| Jeu étalon fait **hors de Chronologia** : eScriptorium pour le texte, fichiers structurés pour les champs | (D) |
| Vérification de cohérence avec Geneanet, en témoin | (D) |
| Classement des professions et des positions sociales par nomenclatures standard (HISCO, puis HISCLASS ou SOCPO), pas de grille maison | (C) |
| Écran de relecture web, adapté au téléphone, hébergé sur le serveur Hetzner/Coolify avec authentification | (C), à concevoir dans le chantier 4 |
| Passage à PostgreSQL avant la chaîne de lecture (serveur partagé, file à état) | (C), à trancher au début du chantier 3 |
| Modèles de langage via OpenRouter, tracés dans Langfuse (consigne générale du poste) | (C) |

## 6. Garde-fous contre la surspécialisation

1. **Séparer le projet du logiciel (C).** Tout ce qui est propre à Hesdin (référentiels locaux, gabarits d'actes, réglages, seuils) vit dans un espace « projet » de données et de configuration. Le code et le schéma n'en dépendent pas. Toute fonction nouvelle se justifie d'abord dans le document de référence, avec un cas d'usage formulé hors de ce projet.
2. **Utiliser des nomenclatures standard (C).** HISCO et HISCLASS ou SOCPO pour les professions, plutôt que des catégories inventées pour Hesdin.
3. **Garder un corpus témoin (D).** Saint-Omer est passé dans la chaîne sans réglage, sur un échantillon (quelques années d'actes et un recensement). Toute casse révèle une spécificité cachée, à traiter dans le logiciel, pas par un réglage propre à Saint-Omer. Les bases GeneWeb existantes servent de second témoin, d'une autre nature.
4. **Fixer les mesures avant de regarder (C).** Métriques, seuils et tirages sont fixés avant de lancer un lot, et enregistrés avec lui.

## 7. Chantiers et ordre

| # | Chantier | Contenu | Conception |
|---|---|---|---|
| 1 | Inventaire et plan de dépouillement | Registres, recensements, tables décennales, lacunes, conditions de réutilisation | Ce document, §8 |
| 2 | Jeu étalon | Tirage aléatoire, transcription et annotation humaines, protocole de mesure | Ce document, §8 |
| 3 | Chaîne de lecture | Import Socface en première lecture ; reconnaissance d'écriture et extraction pour l'état civil ; mesures contre l'étalon ; délégation mesurée | À concevoir |
| 4 | Relecture et reconstitution des familles | Écran de relecture (bureau et téléphone), rapprochement étendu aux actes et aux recensements, remontée avant 1872 | À concevoir |
| 5 | Analyses | Démographie comparée, classement HISCO, mobilité sociale, comptages R29 | À concevoir |
| 6 | Presse, témoin Saint-Omer, source fiscale | Dans cet ordre, ou réordonné selon ce que montrent les chantiers 3 à 5 | À concevoir |

Point de vigilance pour le chantier 4 (C) : définir **qui fait partie de « la population de Hesdin »**. La ville a une garnison (caserne de la Frézelière, cavalerie, gendarmerie) comptée parfois à part dans les recensements, et l'hôpital enregistre des décès de non-résidents. C'est une règle d'inclusion, à déclarer et non à appliquer en silence.

---

## 8. Premier chantier : inventaire et jeu étalon

### 8.1 But
Savoir exactement ce qui existe (et ce qui manque), puis constituer un **étalon humain tiré au hasard** contre lequel toute la machine sera mesurée. Ce chantier ne produit presque pas de code dans Chronologia : c'est voulu, l'étalon doit être indépendant du logiciel qu'il juge.

### 8.2 Inventaire (chantier 1)

Livrable : un **tableau d'inventaire** (CSV ou YAML, dans le répertoire de données du projet), une ligne par unité documentaire :

- commune, type (naissances, mariages, décès, tables décennales, recensement, publications de mariage si elles existent), années couvertes, cote AD62 ;
- disponibilité : en ligne, en salle de lecture seulement, absent ;
- nombre de vues (images) ;
- estimation du nombre d'actes ou de lignes ;
- pour les recensements : présence dans Socface (oui, non, partiel) et correspondance entre pages Socface et vues AD62 ;
- remarques (registre abîmé, double registre, écriture difficile, garnison comptée à part…).

Le tableau couvre :
- Hesdin 1872-1911 en entier ;
- l'état civil de Hesdin **antérieur à 1872** utile à la remontée, sur une profondeur à fixer par le chercheur en voyant l'inventaire ;
- l'échantillon témoin de Saint-Omer (périmètre fixé à la fin de l'inventaire, avant tout réglage de la chaîne).

Vérifications à faire pendant l'inventaire :
1. la couverture en ligne de l'état civil de Hesdin après 1882 ;
2. la présence de Hesdin et de Saint-Omer dans Socface, la licence des données et la possibilité d'export ;
3. auprès des AD62 : un usage de recherche non commercial et un stockage d'images sur un serveur privé non public sont-ils autorisés ?

Les manques constatés sont saisis comme **lacunes** (décision 39), avec leur motif. Ils seront importés dans la couche Travail quand elle existera ; d'ici là, ils restent dans le tableau.

Exécution (C) : l'inventaire peut être préparé par la machine, en consultant page à page les instruments de recherche des AD62, le portail et FranceArchives, puis **contrôlé par le chercheur**. Aucune aspiration en masse d'images à cette étape.

**Images en attendant la réponse des AD62 (C).** Les vues de l'étalon (environ 128 unités) sont téléchargées à la main en PDF, ce qui est gratuit selon le tarif 2025. Elles restent **sur le poste uniquement**, dans le répertoire de données du projet. L'étalon garde ses images, et ses mesures peuvent donc être rejouées. Le stockage sur le serveur n'intervient qu'après accord écrit des AD62. En attendant, eScriptorium tourne en local.

**Socface pour l'étalon (C).** Les lignes Socface des 18 pages tirées (environ 450 lignes) sont relevées par consultation de FranceArchives, à la main ou page à page. Cela ne pose pas de question de licence pour une mesure de recherche. L'import en masse de Socface, et donc sa licence et son export, est une question du chantier 3, pas de celui-ci.

### 8.3 Jeu étalon (chantier 2)

**Tirage (C).** Le tirage est aléatoire, avec une graine enregistrée, et stratifié par type de document et par décennie. On tire **à partir des tables décennales ou de l'inventaire**, jamais à vue. Le script de tirage et sa graine sont conservés : le tirage doit pouvoir se rejouer.

- **État civil : 100 actes** de Hesdin 1872-1911, répartis à peu près comme le corpus (indication : 40 naissances, 15 mariages, 45 décès, à ajuster aux effectifs réels de l'inventaire), soit environ 25 par décennie.
- **Recensements : 18 pages**, 2 tirées au hasard dans chacun des 9 dénombrements (environ 450 lignes).
- **Remontée avant 1872 :** 10 actes de plus, tirés parmi ceux qui servent à remonter les ménages de 1872 (écritures plus anciennes).

**Deux niveaux de vérité.**

1. **Texte**, dans eScriptorium (D) : segmentation des lignes et transcription diplomatique de chaque acte ou page. Les conventions de transcription (abréviations, ponctuation, majuscules, mots barrés, ajouts marginaux, chiffres en lettres) s'écrivent **avant** de commencer, sur une page.
   - Export : ALTO ou PAGE XML, plus le texte brut.
   - Mesures : taux d'erreur sur les caractères (CER) et sur les mots (WER), par type d'acte et par décennie.
2. **Champs structurés**, dans un fichier par acte (C : YAML, validé par un schéma JSON versionné dans le dépôt, puisque le **schéma** n'est pas une donnée nominative).
   - Contenu : type d'acte, date de l'acte, date de l'événement, lieu ; chaque personne mentionnée (nom et prénoms tels qu'écrits, sexe, âge, profession telle qu'écrite, domicile, lieu de naissance, rôle : sujet, père, mère, époux, témoin, déclarant, officier) ; les liens entre personnes ; les mentions marginales.
   - Chaque valeur reste **telle qu'écrite** (R13). Aucune normalisation dans l'étalon : la normalisation (HISCO, lieux) est une étape mesurée à part.
   - Pour les recensements, le fichier suit les colonnes de la liste nominative (ménage, nom, prénoms, âge ou année de naissance, lieu de naissance, nationalité, profession, position dans le ménage, patron ou employeur selon les années).
   - Mesures : précision et rappel par champ, et pour les personnes, appariement correct des rôles.

**Socface contre l'étalon (C).** Une fois les 18 pages de recensement annotées, on mesure le taux d'erreur réel de Socface sur Hesdin, champ par champ. Cette mesure est le premier résultat chiffré du projet. Elle fixe le niveau de relecture à prévoir pour les recensements dans le chantier 3.

**Lecture unique (C).** Le document de référence recommande « de préférence deux lecteurs » pour un étalon. Ici, il n'y a qu'un chercheur. Palliatif proposé : une **seconde lecture différée** par le même chercheur, sur 10 % des actes tirés au hasard, au moins trois semaines après la première. L'accord entre les deux lectures est mesuré et publié avec l'étalon. La limite est déclarée, pas cachée.

**Coût (C, estimation).** 110 actes à environ 4 minutes, plus 18 pages à environ 15 minutes, soit à peu près 12 heures, donc **six semaines** de séances. Les séances du chantier 2 remplacent celles de relecture, qui n'existent pas encore.

**Pilote (C).** Avant le tirage, un pilote sur 5 actes et 1 page de recensement, pris **hors de l'échantillon** (une année tirée au hasard, puis exclue du tirage), sert à mesurer le temps réel par unité et à éprouver les conventions de transcription. **La taille de l'étalon est fixe (D)** : si le rythme réel est plus lent, on allonge la durée plutôt que de réduire l'échantillon, tant que la durée reste raisonnable. Seuil retenu (C) : jusqu'à **quatre mois** de séances, on allonge sans rediscuter. Au-delà, on revient vers le chercheur avant de tirer, avec le temps mesuré.

**Ce qu'on s'interdit.** Retirer un acte tiré parce qu'il est illisible. Il reste dans l'étalon, marqué illisible en tout ou partie, car c'est aussi une mesure.

### 8.4 Où vivent les fichiers (C)

- **Dans le dépôt Chronologia :** les schémas (format d'inventaire, format des champs structurés), le script de tirage, le script de calcul des métriques, les conventions de transcription, et des fixtures **synthétiques** pour les tests.
- **Hors du dépôt**, dans un répertoire de données du projet sur le poste (sauvegardé à part) : le tableau d'inventaire, les tirages et leur graine, les exports eScriptorium, les fichiers structurés, et les extraits d'images si les conditions des AD62 le permettent.
- Les comptes rendus et les journaux ne contiennent que des agrégats (garde-fou existant).

### 8.5 eScriptorium (C)
Instance auto-hébergée en Docker, soit sur le poste, soit sur le serveur Hetzner derrière Coolify, avec authentification et sans accès public. Ce choix dépend de la réponse des AD62 sur le stockage d'images. Le chantier 2 n'a besoin d'**aucun entraînement de modèle** : l'outil sert à segmenter et à transcrire. On pourra y tester, sans s'y engager, un modèle public (par exemple LECTAUREP, CC-BY) pour préremplir la transcription. Cela accélère la saisie, mais il faut alors **corriger intégralement** chaque ligne, sans quoi l'étalon hérite des erreurs du modèle. Ce préremplissage est signalé dans les métadonnées de l'étalon.

### 8.6 Critères de réussite du premier chantier
1. Le tableau d'inventaire couvre Hesdin 1872-1911, la remontée et l'échantillon de Saint-Omer. Chaque manque y figure comme lacune motivée.
2. Les trois vérifications de §8.2 ont une réponse écrite (couverture en ligne, Socface, conditions AD62).
3. L'étalon existe : 110 actes et 18 pages, tirés par script avec une graine, aucun retiré. Il est transcrit (eScriptorium) et annoté (fichiers structurés valides contre le schéma).
4. La seconde lecture différée sur 10 % est faite et l'accord mesuré.
5. Le taux d'erreur de Socface sur Hesdin est mesuré champ par champ.
6. Les scripts de tirage et de métriques sont dans le dépôt, testés sur fixtures synthétiques (TDD, `pytest`, `mypy`).

### 8.7 Laissé au constructeur
- Le format exact du tableau d'inventaire et du schéma des champs, dans l'esprit ci-dessus.
- L'outillage de calcul du CER et du WER (bibliothèque existante plutôt que du code maison).
- La répartition exacte de l'échantillon une fois les effectifs connus, à condition de la fixer **avant** le tirage.

## 9. Décisions de modèle à consigner

Ce projet ne change pas le modèle à ce stade. Deux points seront à porter au document de référence quand le chantier 3 les rendra concrets :
- une **transcription externe** (Socface) entre comme une première lecture machine d'un document, à relire (R33, R34). C'est son statut dans la couche Source ;
- l'**espace « projet »** (référentiels et réglages propres à une étude) comme garde-fou de généricité.
