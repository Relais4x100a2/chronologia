# Projet Hesdin-Lanchères 1872-1911 : Chronologia à l'épreuve de vrais terrains

Document de conception, 11 novembre 2026. Statut : approuvé par le chercheur le 11 novembre 2026. Révision du même jour : ajout de Lanchères (étude complète) et de Saint-Valery-sur-Somme (comparaison), dans la Somme.

Ce document a deux étages :

1. le **cadre** du projet entier (sections 1 à 7), valable pour tous les chantiers ;
2. la conception détaillée du **premier chantier** seulement : inventaire et jeu étalon (section 8).

Les chantiers suivants feront chacun l'objet d'une conception à part, qui s'appuiera sur ce cadre.

Convention : ce qui a été **décidé par le chercheur** est marqué (D). Ce qui est **un choix de conception** fait en rédigeant, révisable, est marqué (C).

---

## 1. Intention

Construire et valider Chronologia en menant une vraie étude d'histoire sociale, sur du volume, plutôt que sur des exemples choisis (D). Le logiciel progresse parce qu'il bute sur des sources réelles. L'étude progresse parce que le logiciel lui retire la copie (doctrine §1.1 du document de référence).

Le projet repose sur un **double comparatif** : deux départements, et dans chacun une petite et une plus grande commune (D).

| | Pas-de-Calais (AD62) | Somme (AD80) |
|---|---|---|
| **Terrain d'étude complet** | **Hesdin**, petite ville, environ 3 000 habitants | **Lanchères**, village des Bas-Champs, environ 1 000 à 1 100 habitants sur la période (Socface) |
| **Commune de comparaison** | **Saint-Omer**, environ 20 000 habitants | **Saint-Valery-sur-Somme**, port, environ 3 500 habitants |

- **Hesdin et Lanchères** sont étudiées en entier, sur **1872-1911** (D) : questions d'histoire de la section 2, remontée avant 1872.
- **Saint-Omer et Saint-Valery** sont prises en **périmètre léger** (D) : recensements et échantillon d'actes. Elles ont un double rôle. Ce sont des **points de comparaison** avec une commune plus grande du même département. Ce sont aussi des **témoins de généricité** : on vérifie que la chaîne construite pour les deux terrains tient sans réglage spécifique.

Les comparaisons attendues (C) : petite ville contre village ; Artois contre Bas-Champs ; chaque terrain face à sa grande voisine.

Contrainte de sources (constatée le 11/11/2026) : dans la Somme, seuls les recensements de **1872, 1881, 1906 et 1911** sont conservés. Toute comparaison de recensement entre les deux départements se fait donc sur ces quatre années. Les dénombrements intermédiaires du Pas-de-Calais restent exploités pour Hesdin seule, et la restriction est déclarée avec chaque comptage comparatif (R29).

## 2. Questions d'histoire

1. **Démographie.** Comment la population évolue-t-elle (natalité, mortalité, nuptialité, migrations, structure des ménages) ? Ces évolutions suivent-elles celles de la région et de la France ? (D)
2. **Reproduction sociale.** Les enfants des familles aisées restent-ils aisés ? Même question pour les autres couches de la population. (D)

Ces deux questions portent sur Hesdin et Lanchères. Pour Saint-Omer et Saint-Valery, on s'en tient aux indicateurs que permet le périmètre léger : structure des ménages et des professions par recensement, mouvements tirés de l'échantillon d'actes (C).

La position sociale se lit d'abord par la **profession et la domesticité** (D), relevées dans les actes et les recensements. Une **source fiscale ou successorale** viendra ensuite, sur un échantillon de familles (D). Dans la presse, on relève les **licitations, faillites, ventes et adjudications** (D).

Le projet couvre une génération : 1872-1911 (D). Pour ancrer les grands-parents, on remonte dans l'état civil antérieur à 1872 **pour tous les ménages du recensement de 1872 de Hesdin et de Lanchères, autant que possible** (D). Un ménage qu'on ne peut pas remonter n'est jamais écarté en silence : il devient une **lacune motivée** (décision 39, R24).

## 3. Objectifs, non-objectifs, anti-objectifs

**Objectifs**
- Faire passer à Chronologia l'épreuve du volume. Estimation (C), à confirmer par l'inventaire : environ 8 000 actes et 24 000 lignes de recensement pour Hesdin, environ 2 000 actes et 4 200 lignes pour Lanchères (environ 50 actes par an, quatre dénombrements seulement).
- Mesurer à chaque étape ce que vaut la machine (reconnaissance d'écriture, extraction, rapprochement) contre un jeu étalon humain, **séparément pour chaque terrain**.
- Produire des résultats d'histoire comparables, grâce à des nomenclatures standard.

**Non-objectifs**
- Une base généalogique complète de l'une ou l'autre commune.
- Une étude complète de Saint-Omer ou de Saint-Valery.
- Une transcription parfaite de chaque acte. Le seuil d'erreur acceptable se mesure, il n'est pas nul.
- Une réécriture des recensements que Socface a déjà transcrits.

**Anti-objectifs** (échec même si « ça marche »)
- **Un logiciel qui ne sait faire que Hesdin**, ou que le Pas-de-Calais. Fonctions, tables ou règles taillées pour un corpus ou un service d'archives (D, principal risque identifié par le chercheur).
- **Des résultats biaisés par la sélection.** Familles faciles ou intéressantes mieux suivies que les autres, émigrés ou marins qui disparaissent sans qu'on le voie.
- **Des comparaisons trompeuses.** Comparer des communes dont les sources, les lacunes ou les taux d'erreur diffèrent sans le dire (R29).
- **Des chiffres sans hypothèses.** Un comptage qui ne dit pas ce qu'il exclut (R29).
- **La machine qui verse sans mesure** au-delà de ce qui a été contrôlé (R18, R33).

## 4. Contraintes

### 4.1 Temps humain
- **20 minutes par jour, six jours par semaine** (pas le samedi), par le chercheur seul (D). Cela fait environ 2 heures par semaine et 100 heures par an.
- Conséquence (C) : impossible de tout relire. La **délégation mesurée (R33, §7.11)** devient le mode normal. Le chercheur relit un échantillon aléatoire et les cas douteux. Au-delà, la machine ne verse qu'en « probable » et seulement là où son taux d'erreur mesuré passe sous un seuil fixé à l'avance. Un contrôle qui dépasse le seuil suspend la délégation d'office. Le seuil et le taux se mesurent **par terrain** : une délégation ouverte à Hesdin ne s'étend pas d'office à Lanchères.
- Conséquence (C) : chaque séance doit être utile tout de suite. La file de décisions est prête et triée, et on reprend exactement là où on s'est arrêté.
- Les séances se passent **au bureau et sur téléphone ou tablette** (D). L'écran de relecture doit donc fonctionner dans un navigateur, sur les deux formats.

### 4.2 Sources (état de la reconnaissance, novembre 2026)

**Pas-de-Calais**

| Source | Accès | À savoir |
|---|---|---|
| État civil Hesdin (N/M/D) | Portail des AD62, visionneuse | Couverture annoncée « 1793 à 1912 environ ». Les années 1883-1914 de Hesdin sont **à vérifier** : le site des AD62 est fermé pour maintenance au 11/11/2026, réouverture annoncée vers la mi-novembre. Les tables décennales sont numérisées : ce sont des index exhaustifs. |
| Recensements 1872, 1876, 1881, 1886, 1891, 1896, 1901, 1906, 1911 | Images aux AD62 ; transcription **Socface** sur FranceArchives | **Hesdin et Saint-Omer couverts par Socface** (vérifié le 11/11/2026 sur socface.teklia.com). Hesdin 1872-1911 : 872 pages, environ 24 200 mentions d'individus, de 2 906 mentions en 1872 à 2 518 en 1911. Saint-Omer présente des irrégularités à expliquer : 26 616 mentions en 1881 contre 16 747 en 1876, 12 064 en 1906, seulement 1 889 ménages en 1891. Socface annonce 15 à 20 % d'erreurs. La licence et le téléchargement en masse restent **à vérifier** ; le détail ne se consulte pas sans compte sur le site de Teklia. Les numéros de page ne correspondent pas toujours aux images. |
| Presse, Hesdin | Gallica, AD62 | Aucun titre local numérisé trouvé. Il faudra passer par la presse d'arrondissement (Montreuil) ou départementale. |
| Presse, Saint-Omer | Gallica, bibliothèque d'agglomération | Numérisation en cours (*Mémorial artésien*, *Coin de terre et du foyer*, plan DRAC 2023). |

**Somme**

| Source | Accès | À savoir |
|---|---|---|
| État civil Lanchères et Saint-Valery (N/M/D), tables décennales | Portail des AD80, visionneuse | **Vérifié dans la visionneuse le 11/11/2026.** Les deux communes relèvent de l'arrondissement d'Abbeville (greffe brûlé en 1940 ; lacune du greffe 1836-1869, comblée par les microfilms des registres communaux, 5 MI_D ; registres « reconstitués » pour 1870-1880 environ). D'après les AD80, la collection numérisée **ne dépasse généralement pas 1902** : les registres postérieurs sont au greffe du tribunal judiciaire d'Amiens et en mairie. **Lanchères en ligne** : naissances 1870-1903 (5 MI_D 1155, 2 E 464/10-11) ; mariages 1863-1906 (5 MI_D 1155, 2 E 464/12-14) ; décès 1870-1910 (5 MI_D 1155, 2 E 464/15-17) ; NMD jusqu'en 1862 ; tables décennales 1802-1902 (5 MI_D 38). **Manquent pour Lanchères : naissances 1904-1911, mariages 1907-1911, décès 1911 ; pour la remontée, naissances et décès 1863-1869.** **Saint-Valery en ligne** : NMD 1858-1869 (microfilms), 1870-1886 (reconstitués), puis 2 E 721 jusqu'en 1899 pour N et M, mi-1902 pour D ; tables décennales 1802-1902 (5 MI_D 54). |
| Recensements | Images aux AD80 ; Socface | **Les AD80 ne conservent que les listes de 1836, 1851, 1872, 1881, 1906, 1911** (puis 1921-1936). Celles de **1876, 1886, 1891, 1896 et 1901 sont en déficit** pour tout le département (répertoire 6 M, état des lacunes). Seule piste : un double conservé en mairie, **à demander** aux deux communes. Socface couvre les deux communes pour ces quatre années (vérifié le 11/11/2026). **Lanchères** : 1 138 mentions en 1872, 1 046 en 1881, 1 034 en 1906, 964 en 1911, environ 40 pages par dénombrement. La commune comptait donc **environ 1 000 à 1 100 habitants**, et non 700. **Saint-Valery** : 3 672 mentions en 1872, 3 441 en 1911, environ 120 pages par dénombrement ; anomalies à expliquer (92 ménages seulement en 1881, 2 120 mentions en 1906). Le répertoire signale que des listes de 1872 trop fragiles sont **incommunicables** : à vérifier pour les deux communes. |
| Inscription maritime (quartier de Saint-Valery) | Service historique de la Défense, AD80 | Source possible pour suivre les marins absents des recensements ou morts en mer (C). Existence, lieu de conservation et numérisation **à vérifier**. Hors du premier chantier sauf pour l'inventaire. |
| Presse, Lanchères et Saint-Valery | Gallica, AD80 | **À rechercher** : presse d'arrondissement (Abbeville) ou départementale. |

**Pour tous les terrains**

| Source | Accès | À savoir |
|---|---|---|
| Arbres publics Geneanet | Consultation | **Témoin extérieur, pas une source** (C). Comparaison à la main sur échantillon, car les conditions d'utilisation interdisent l'aspiration automatique. |

### 4.3 Droit et confidentialité
- Les actes ont tous plus de 75 ans, donc ils sont communicables.
- Les AD62 autorisent le téléchargement gratuit en PDF. Le JPEG est payant, et une licence avec redevance existe pour l'usage commercial.
- Les **AD80** appliquent un règlement de réutilisation de 2019 fondé sur la **gratuité**, sans licence obligatoire, y compris pour la « transcription de documents d'archives sous forme de texte traitable par machine » et la constitution de bases de données. Il faut citer la source sous la forme « Archives départementales de la Somme, cote » avec une date, et respecter la délibération CNIL 2010-460 pour les données personnelles. Le stockage d'images n'est pas traité explicitement. Pour les deux services, un usage de recherche non commercial et un stockage sur serveur privé sont **à confirmer** avant tout stockage d'images sur le serveur.
- Les garde-fous existants (`AGENTS.md`) s'appliquent : **aucune donnée nominative réelle dans le dépôt Git**, ni dans les journaux ou les comptes rendus. Les données du projet vivent dans un répertoire de données à part, hors du dépôt (C, section 8.4).

### 4.4 Règles du modèle les plus exposées
R2, R10, R13 (couche Source fidèle et immuable), R18 et R26 (la machine propose), R24 (rien en silence), R29 (comptages), R33 (délégation mesurée), R34 (relecture qui s'ajoute). Toute décision de modèle née du projet se consigne d'abord dans le document de référence, comme d'habitude.

## 5. Choix de mise en œuvre

| Choix | Statut |
|---|---|
| Hesdin et Lanchères en étude complète ; Saint-Omer et Saint-Valery en comparaison et en témoins | (D) |
| Recensements : **Socface comme première lecture**, à relire et à mesurer, pas de transcription maison | (D) |
| État civil : chaîne maison, image → reconnaissance d'écriture → extraction par modèle de langage → brouillon (schéma `saisie`) → validation | (D) |
| Jeu étalon fait **hors de Chronologia** : eScriptorium pour le texte, fichiers structurés pour les champs | (D) |
| Un **étalon propre à chaque terrain** (Hesdin, Lanchères) | (D) |
| Vérification de cohérence avec Geneanet, en témoin | (D) |
| Classement des professions et des positions sociales par nomenclatures standard (HISCO, puis HISCLASS ou SOCPO), pas de grille maison | (C) |
| Écran de relecture web, adapté au téléphone, hébergé sur le serveur Hetzner/Coolify avec authentification | (C), à concevoir dans le chantier 4 |
| Passage à PostgreSQL avant la chaîne de lecture (serveur partagé, file à état) | (C), à trancher au début du chantier 3 |
| Modèles de langage via OpenRouter, tracés dans Langfuse (consigne générale du poste) | (C) |

## 6. Garde-fous contre la surspécialisation

1. **Séparer le projet du logiciel (C).** Tout ce qui est propre à une commune ou à un service d'archives (référentiels locaux, gabarits d'actes, cotes, réglages, seuils) vit dans un espace « projet » de données et de configuration. Le code et le schéma n'en dépendent pas. Toute fonction nouvelle se justifie d'abord dans le document de référence, avec un cas d'usage formulé hors de ce projet.
2. **Utiliser des nomenclatures standard (C).** HISCO et HISCLASS ou SOCPO pour les professions, plutôt que des catégories inventées pour ces communes.
3. **Garder des témoins (D).** Deux terrains complets dans deux départements obligent déjà la chaîne à servir deux services d'archives. En plus, Saint-Omer (même service que Hesdin) et Saint-Valery (même service que Lanchères) passent dans la chaîne **sans réglage**, sur leur périmètre léger. Toute casse révèle une spécificité cachée, à traiter dans le logiciel, pas par un réglage propre à la commune. Les bases GeneWeb existantes servent de témoin supplémentaire, d'une autre nature.
4. **Fixer les mesures avant de regarder (C).** Métriques, seuils et tirages sont fixés avant de lancer un lot, et enregistrés avec lui.

## 7. Chantiers et ordre

| # | Chantier | Contenu | Conception |
|---|---|---|---|
| 1 | Inventaire et plan de dépouillement | Registres, recensements, tables décennales, lacunes, conditions de réutilisation, pour les quatre communes | Ce document, §8 |
| 2 | Jeu étalon | Tirage aléatoire, transcription et annotation humaines, protocole de mesure, pour Hesdin et Lanchères | Ce document, §8 |
| 3 | Chaîne de lecture | Import Socface en première lecture ; reconnaissance d'écriture et extraction pour l'état civil ; mesures contre l'étalon ; délégation mesurée | À concevoir |
| 4 | Relecture et reconstitution des familles | Écran de relecture (bureau et téléphone), rapprochement étendu aux actes et aux recensements, remontée avant 1872 | À concevoir |
| 5 | Analyses | Démographie comparée, classement HISCO, mobilité sociale, comptages R29 | À concevoir |
| 6 | Presse, témoins Saint-Omer et Saint-Valery, source fiscale | Dans cet ordre, ou réordonné selon ce que montrent les chantiers 3 à 5 | À concevoir |

L'ordre de traitement entre les deux terrains, dans les chantiers 3 et 4, est laissé à leur conception (C). Par défaut, Hesdin ouvre chaque chantier et Lanchères suit, sans réglage propre.

Point de vigilance pour le chantier 4 (C) : définir **qui fait partie de la population** de chaque commune. Hesdin a une garnison (caserne de la Frézelière, cavalerie, gendarmerie) comptée parfois à part dans les recensements, et l'hôpital enregistre des décès de non-résidents. À Lanchères et à Saint-Valery, les **gens de mer** peuvent être absents au recensement, et leurs décès en mer transcrits tardivement. Ce sont des règles d'inclusion, à déclarer et non à appliquer en silence, et à rendre comparables d'une commune à l'autre.

---

## 8. Premier chantier : inventaire et jeu étalon

### 8.1 But
Savoir exactement ce qui existe (et ce qui manque), puis constituer, pour chaque terrain, un **étalon humain tiré au hasard** contre lequel toute la machine sera mesurée. Ce chantier ne produit presque pas de code dans Chronologia : c'est voulu, l'étalon doit être indépendant du logiciel qu'il juge.

### 8.2 Inventaire (chantier 1)

Livrable : un **tableau d'inventaire** (CSV ou YAML, dans le répertoire de données du projet), une ligne par unité documentaire :

- commune, service d'archives (AD62, AD80…), type (naissances, mariages, décès, tables décennales, recensement, publications de mariage si elles existent), années couvertes, cote ;
- disponibilité : en ligne, en salle de lecture seulement, absent ;
- nombre de vues (images) ;
- estimation du nombre d'actes ou de lignes ;
- pour les recensements : présence dans Socface (oui, non, partiel) et correspondance entre pages Socface et vues des archives ;
- remarques (registre abîmé, double registre, écriture difficile, garnison comptée à part, marins absents…).

Le tableau couvre :
- Hesdin et Lanchères, 1872-1911 en entier ;
- l'état civil de Hesdin et de Lanchères **antérieur à 1872** utile à la remontée, sur une profondeur à fixer par le chercheur en voyant l'inventaire ;
- les échantillons de Saint-Omer et de Saint-Valery (périmètre fixé à la fin de l'inventaire, avant tout réglage de la chaîne) ;
- l'existence de sources de l'inscription maritime pour Lanchères et Saint-Valery (une ligne de repérage, pas un dépouillement).

Vérifications à faire pendant l'inventaire :
1. la couverture en ligne de l'état civil de Hesdin après 1882 (Lanchères et Saint-Valery : fait le 11/11/2026, voir §4.2) ;
2. la présence des quatre communes dans Socface, la licence des données et la possibilité d'export ;
3. auprès de la mairie de Lanchères (et de celle de Saint-Valery) : consultation des registres absents des AD80 (Lanchères : N 1904-1911, M 1907-1911, D 1911, N et D 1863-1869) et existence d'un double des listes nominatives de 1876 à 1901. À défaut, la période complète de Lanchères se réduit à 1872-1903 pour les naissances, et la réduction est déclarée (R29).
4. auprès des AD62 **et des AD80** : un usage de recherche non commercial et un stockage d'images sur un serveur privé non public sont-ils autorisés ?

Les manques constatés sont saisis comme **lacunes** (décision 39), avec leur motif. Ils seront importés dans la couche Travail quand elle existera ; d'ici là, ils restent dans le tableau.

Exécution (C) : l'inventaire peut être préparé par la machine, en consultant page à page les instruments de recherche des AD62 et des AD80, leurs portails et FranceArchives, puis **contrôlé par le chercheur**. Aucune aspiration en masse d'images à cette étape.

**Images en attendant la réponse des archives (C).** Les vues de l'étalon (environ 180 unités pour les deux terrains) sont téléchargées à la main, en PDF quand c'est gratuit (tarif AD62 2025 ; tarif AD80 à relever). Elles restent **sur le poste uniquement**, dans le répertoire de données du projet. L'étalon garde ses images, et ses mesures peuvent donc être rejouées. Le stockage sur le serveur n'intervient qu'après accord écrit du service d'archives concerné. En attendant, eScriptorium tourne en local.

**Socface pour l'étalon (C).** Les lignes Socface des 26 pages tirées (environ 650 lignes) sont relevées par consultation de FranceArchives, à la main ou page à page. Cela ne pose pas de question de licence pour une mesure de recherche. L'import en masse de Socface, et donc sa licence et son export, est une question du chantier 3, pas de celui-ci. Si Lanchères n'est pas dans Socface, la mesure de Socface s'y réduit à rien et le chantier 3 devra prévoir une lecture des recensements de Lanchères : à signaler dès l'inventaire.

### 8.3 Jeu étalon (chantier 2)

**Tirage (C).** Le tirage est aléatoire, avec une graine enregistrée, et stratifié par commune, par type de document et par décennie. On tire **à partir des tables décennales ou de l'inventaire**, jamais à vue. Le script de tirage et sa graine sont conservés : le tirage doit pouvoir se rejouer. Les deux terrains sont tirés par le même script, avec la commune comme paramètre.

**Hesdin**
- **État civil : 100 actes** de 1872-1911, répartis à peu près comme le corpus (indication : 40 naissances, 15 mariages, 45 décès, à ajuster aux effectifs réels de l'inventaire), soit environ 25 par décennie.
- **Recensements : 18 pages**, 2 tirées au hasard dans chacun des 9 dénombrements (environ 450 lignes).
- **Remontée avant 1872 :** 10 actes de plus, tirés parmi ceux qui servent à remonter les ménages de 1872 (écritures plus anciennes).

**Lanchères** (D pour le principe d'un étalon propre ; tailles (C))
- **État civil : 40 actes** de 1872-1911, répartis comme le corpus, soit environ 10 par décennie.
- **Recensements : 8 pages**, 2 tirées au hasard dans chacun des 4 dénombrements conservés (1872, 1881, 1906, 1911), soit environ 200 lignes.
- **Remontée avant 1872 :** 5 actes de plus, tirés comme pour Hesdin.

Raison de deux étalons : la main d'un secrétaire de mairie de village et celle d'une mairie de ville ne se mesurent pas l'une par l'autre. Chaque terrain a ses propres taux d'erreur, et la délégation mesurée (§4.1) s'appuie sur ceux du terrain concerné.

Saint-Omer et Saint-Valery n'ont pas d'étalon dans ce chantier (C). Leur rôle de témoin se joue au chantier 6 : si la chaîne y casse, on le voit sans étalon ; si une mesure fine devient nécessaire, un petit étalon se conçoit alors.

**Deux niveaux de vérité.**

1. **Texte**, dans eScriptorium (D) : segmentation des lignes et transcription diplomatique de chaque acte ou page. Les conventions de transcription (abréviations, ponctuation, majuscules, mots barrés, ajouts marginaux, chiffres en lettres) s'écrivent **avant** de commencer, sur une page, et valent pour les deux terrains.
   - Export : ALTO ou PAGE XML, plus le texte brut.
   - Mesures : taux d'erreur sur les caractères (CER) et sur les mots (WER), par commune, par type d'acte et par décennie.
2. **Champs structurés**, dans un fichier par acte (C : YAML, validé par un schéma JSON versionné dans le dépôt, puisque le **schéma** n'est pas une donnée nominative).
   - Contenu : commune, type d'acte, date de l'acte, date de l'événement, lieu ; chaque personne mentionnée (nom et prénoms tels qu'écrits, sexe, âge, profession telle qu'écrite, domicile, lieu de naissance, rôle : sujet, père, mère, époux, témoin, déclarant, officier) ; les liens entre personnes ; les mentions marginales.
   - Chaque valeur reste **telle qu'écrite** (R13). Aucune normalisation dans l'étalon : la normalisation (HISCO, lieux) est une étape mesurée à part.
   - Pour les recensements, le fichier suit les colonnes de la liste nominative (ménage, nom, prénoms, âge ou année de naissance, lieu de naissance, nationalité, profession, position dans le ménage, patron ou employeur selon les années).
   - Le schéma est le même pour les deux terrains. Une particularité de la Somme qui ne rentre pas dans le schéma se traite en élargissant le schéma, jamais par une variante propre à Lanchères (garde-fou n° 1).
   - Mesures : précision et rappel par champ, et pour les personnes, appariement correct des rôles.

**Socface contre l'étalon (C).** Une fois les pages de recensement annotées, on mesure le taux d'erreur réel de Socface, champ par champ, **séparément pour Hesdin et pour Lanchères**. Cette mesure est le premier résultat chiffré du projet. Elle fixe le niveau de relecture à prévoir pour les recensements dans le chantier 3.

**Lecture unique (C).** Le document de référence recommande « de préférence deux lecteurs » pour un étalon. Ici, il n'y a qu'un chercheur. Palliatif proposé : une **seconde lecture différée** par le même chercheur, sur 10 % des actes de chaque terrain tirés au hasard, au moins trois semaines après la première. L'accord entre les deux lectures est mesuré et publié avec l'étalon. La limite est déclarée, pas cachée.

**Coût (C, estimation).** Hesdin : 110 actes à environ 4 minutes et 18 pages à environ 15 minutes, soit à peu près 12 heures. Lanchères : 45 actes et 8 pages, soit à peu près 5 heures. Au total, environ **17 heures, donc neuf semaines** de séances. Les séances du chantier 2 remplacent celles de relecture, qui n'existent pas encore.

**Pilote (C).** Avant le tirage, un pilote pris **hors de l'échantillon** (une année tirée au hasard par commune, puis exclue du tirage) : 5 actes et 1 page de recensement pour Hesdin, 3 actes et 1 page pour Lanchères. Il sert à mesurer le temps réel par unité et à éprouver les conventions de transcription sur les deux mains. **La taille de l'étalon est fixe (D)** : si le rythme réel est plus lent, on allonge la durée plutôt que de réduire l'échantillon, tant que la durée reste raisonnable. Seuil retenu (C) : jusqu'à **quatre mois** de séances pour l'ensemble des deux étalons, on allonge sans rediscuter. Au-delà, on revient vers le chercheur avant de tirer, avec le temps mesuré.

**Ce qu'on s'interdit.** Retirer un acte tiré parce qu'il est illisible. Il reste dans l'étalon, marqué illisible en tout ou partie, car c'est aussi une mesure.

### 8.4 Où vivent les fichiers (C)

- **Dans le dépôt Chronologia :** les schémas (format d'inventaire, format des champs structurés), le script de tirage, le script de calcul des métriques, les conventions de transcription, et des fixtures **synthétiques** pour les tests.
- **Hors du dépôt**, dans un répertoire de données du projet sur le poste (sauvegardé à part), un sous-répertoire par commune : le tableau d'inventaire, les tirages et leur graine, les exports eScriptorium, les fichiers structurés, et les extraits d'images si les conditions des archives le permettent.
- Les comptes rendus et les journaux ne contiennent que des agrégats (garde-fou existant).

### 8.5 eScriptorium (C)
Instance auto-hébergée en Docker, soit sur le poste, soit sur le serveur Hetzner derrière Coolify, avec authentification et sans accès public. Ce choix dépend de la réponse des AD62 et des AD80 sur le stockage d'images. Un projet eScriptorium par commune. Le chantier 2 n'a besoin d'**aucun entraînement de modèle** : l'outil sert à segmenter et à transcrire. On pourra y tester, sans s'y engager, un modèle public (par exemple LECTAUREP, CC-BY) pour préremplir la transcription. Cela accélère la saisie, mais il faut alors **corriger intégralement** chaque ligne, sans quoi l'étalon hérite des erreurs du modèle. Ce préremplissage est signalé dans les métadonnées de l'étalon.

### 8.6 Critères de réussite du premier chantier
1. Le tableau d'inventaire couvre Hesdin et Lanchères 1872-1911, leur remontée, et les échantillons de Saint-Omer et de Saint-Valery. Chaque manque y figure comme lacune motivée.
2. Les quatre vérifications de §8.2 ont une réponse écrite, pour les deux services d'archives (couverture en ligne, Socface, conditions de réutilisation).
3. Les deux étalons existent : 110 actes et 18 pages pour Hesdin, 45 actes et 8 pages pour Lanchères, tirés par script avec une graine, aucun retiré. Ils sont transcrits (eScriptorium) et annotés (fichiers structurés valides contre le même schéma).
4. La seconde lecture différée sur 10 % de chaque terrain est faite et l'accord mesuré.
5. Le taux d'erreur de Socface est mesuré champ par champ sur Hesdin et sur Lanchères (ou l'absence de Lanchères dans Socface est constatée et signalée).
6. Les scripts de tirage et de métriques sont dans le dépôt, testés sur fixtures synthétiques (TDD, `pytest`, `mypy`), sans rien de propre à une commune dans le code.

### 8.7 Laissé au constructeur
- Le format exact du tableau d'inventaire et du schéma des champs, dans l'esprit ci-dessus.
- L'outillage de calcul du CER et du WER (bibliothèque existante plutôt que du code maison).
- La répartition exacte des échantillons une fois les effectifs connus, à condition de la fixer **avant** le tirage.

## 9. Décisions de modèle à consigner

Ce projet ne change pas le modèle à ce stade. Deux points seront à porter au document de référence quand le chantier 3 les rendra concrets :
- une **transcription externe** (Socface) entre comme une première lecture machine d'un document, à relire (R33, R34). C'est son statut dans la couche Source ;
- l'**espace « projet »** (référentiels et réglages propres à une étude, à une commune ou à un service d'archives) comme garde-fou de généricité.
