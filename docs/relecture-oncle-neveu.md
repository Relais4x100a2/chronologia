# Relecture du modèle v0.10.1 : l'oncle et le neveu

*9 novembre 2026. Relecture critique du document de référence (`docs/modele-evenement-masque-factoide.md`, v0.10.1), à deux voix.*

- **L'oncle** est un prosopographe émérite. Il a publié dans les années 1960 une prosopographie faite entièrement à la main, sur fiches, avec des dizaines d'étudiants et de chercheurs. Il a vu arriver l'informatique : il en a aimé la puissance et en a détesté les promesses.
- **Le neveu** est designer d'interfaces. Sa spécialité : lire et saisir des données sans effort.

Les propositions sont regroupées au §6. Les propositions 1, 3, 10, 11 et 12 ont été retenues le 9 novembre 2026 : décisions 39 à 43 du modèle v0.11. Les autres restent ouvertes.

---

## 1. Le verdict d'ensemble

**L'oncle.** J'ai lu les 1 200 lignes. Ma première réaction est le respect. Sur ce point, le document a raison contre tout ce qu'on m'a vendu depuis 1975 : il refuse de confondre ce que dit la source et ce que l'historien en conclut. Nous le faisions sur fiches avec deux couleurs de bristol : blanc pour l'acte, jaune pour la notice. Le passage, le masque, la couche Source « coffre‑fort », l'incertitude assumée (R23), « rien n'est masqué en silence » (R24) : c'est notre déontologie, enfin écrite pour une machine.

Ma seconde réaction est l'inquiétude. Ce document décrit très bien **ce que la base garantit**, et très mal **ce que fait le chercheur**. On y trouve des identifications, des statuts et des journaux. Je n'y trouve ni le dépouillement d'un registre, ni le carnet de travail, ni la fiche qu'on retourne trois fois avant de savoir où la ranger. Il ne dit rien non plus de l'étudiant qu'il faut former en deux semaines ni de la notice qu'on publie à la fin. Le modèle garde la preuve ; le travail qui produit cette preuve en est absent.

**Le neveu.** Je dirais la même chose en termes d'interface : le document a un modèle de données remarquable et un modèle mental implicite. Les écrans du §6 sont tous des écrans d'**arbitrage** : file de décisions, conflit de date, conflit de lieu. Ce sont les moments rares et nobles. Or 90 % du temps d'un projet se passe à **dépouiller, relire, chercher et rédiger**. C'est là que l'outil sera jugé, et c'est là que tu as vu l'informatique devenir plus rébarbative que le formulaire papier.

**L'oncle.** Exactement. Le formulaire papier avait une vertu qu'on a oubliée : la marge. On y écrivait ce que le formulaire n'avait pas prévu.

---

## 2. Le volet macro : ce qui manque au projet prosopographique

### 2.1 Le dépouillement, unité de travail oubliée

**L'oncle.** Une prosopographie ne se construit pas acte par acte, mais registre par registre. Nous tenions un cahier de dépouillement : tel registre, folios 1 à 212, dépouillé par untel en mars 1963, lacune des folios 88 à 95 (feuillets arrachés), années 1694‑1695 en déficit, à vérifier. Sans ce cahier, une absence ne veut rien dire. « Pas de baptême de Jean à Saint‑Aubin », est‑ce parce qu'il n'y en a pas, ou parce que personne n'a encore lu 1712 ?

Le mot « dépouillement » n'apparaît pas une seule fois dans le document, ni le mot « lacune ». La question 9.2‑10 (valeur inconnue, absence attestée) touche le sujet par le petit bout. Le grand bout, c'est la **couverture** : on ne peut interpréter un silence qu'à l'intérieur d'une zone dépouillée.

**Le neveu.** Et c'est l'écran qui manque le plus. Imagine un registre dessiné comme un ruban de folios, chaque case colorée selon son état : dépouillé, en cours, lacune, illisible, pas encore vu. Au‑dessus, un histogramme des actes par mois. Un creux de six mois saute aux yeux : registre perdu, curé absent ou épidémie. Les démographes font ce contrôle depuis Fleury et Henry ; ici, il est gratuit, puisque tout est daté.

**L'oncle.** Ce contrôle sert à trois choses à la fois : il guide le travail (qu'est‑ce qui reste à lire ?), il conditionne l'interprétation (ce silence est‑il un vrai silence ?) et il sert d'argument dans le rapprochement. « Pas de sépulture de Pierre Martin dans un registre dépouillé sans lacune » est un indice ; « pas de sépulture dans un registre non dépouillé » n'en est pas un.

→ **Proposition 1** : une entité DEPOUILLEMENT (référentiel ou couche Interprétation) qui porte la source, la plage couverte, le protocole, l'auteur, l'état et les lacunes constatées (elles-mêmes datées et motivées). Elle donne sens aux absences (9.2‑10), aux indices négatifs du rapprochement et aux comptages.

### 2.2 La population étudiée

**L'oncle.** Toute prosopographie commence par une définition : « tous les notaires du bailliage entre 1650 et 1750 », « les chanoines du chapitre », « les familles de laboureurs de trois paroisses ». Cette définition décide qui entre, et elle évolue en cours de route : on élargit, on exclut un cas limite, on se dispute sur un marginal. Dans le modèle, il y a des PERSONNES ; il n'y a pas de **population**.

**Le neveu.** Pour l'interface, c'est le choix d'une « lentille ». Toutes les vues (file de décisions, statistiques, carte) devraient pouvoir se filtrer par population. Une population serait un critère enregistré (une requête versionnée), plus des inclusions et des exclusions manuelles, chacune avec son motif. On retrouve exactement le patron de vos conclusions.

**L'oncle.** Et ce motif, il faut pouvoir le publier. Mes critiques m'ont surtout attaqué sur mes cas limites.

→ **Proposition 2** : une entité POPULATION (critère versionné, inclusions et exclusions argumentées par des CONCLUSIONS). C'est peut‑être la même chose que le « groupe » de la question 9.2‑6, vu sous l'angle du chercheur plutôt que sous l'angle de la source : à instruire ensemble.

### 2.3 Les questions sérielles et la propagation de l'incertitude

**L'oncle.** La prosopographie est une biographie collective : âge au premier mariage, endogamie professionnelle, mobilité, durée des carrières. Le document est excellent pour un individu, mais il est presque muet sur les **comptages**. Une phrase isolée du §6.5 dit qu'un événement de lieu incertain est « rangé à part » dans les comptages par territoire. C'est la bonne intuition. Il faut la généraliser.

**Le neveu.** J'appelle ça la **statistique à trois étages**. Chaque agrégat affiche trois résultats : avec les seules identifications certaines, avec les probables, avec les possibles. Si l'âge moyen au mariage passe de 27,1 à 27,3 ans, la conclusion est robuste. S'il passe de 27 à 31 ans, elle dépend de vos rapprochements, et le lecteur doit le savoir. Ça s'affiche en un graphique à trois barres ou en une fourchette, pas plus.

**L'oncle.** Nous faisions ce calcul à la main pour les seuls tableaux importants, et nous le faisions mal. C'est exactement le genre de gain que la machine devait apporter et qu'elle n'a jamais apporté.

→ **Proposition 3** : un §6.9 (ou §8) « Questions sérielles ». Tout agrégat est calculé par degré (certain, probable, possible). Les événements en incertitude assumée et les personnes exclues de la population sont comptés à part, jamais répartis en silence (R24 appliquée aux nombres).

### 2.4 La notice, produit final

**L'oncle.** Le livre que j'ai publié n'était pas une base, c'était une suite de **notices** aux rubriques fixes : identité et variantes du nom, origine, famille, cursus, fortune, réseau, mort, sources. Le lecteur parcourait 2 000 notices parce qu'elles avaient toutes la même forme. Le modèle calcule une « fiche consolidée » (R8, §8.1), mais il n'en dit pas la forme.

**Le neveu.** C'est le cœur du volet lecture. Je propose une **notice générée**, typographiée comme une page imprimée, avec des rubriques paramétrables par projet. La certitude ne s'y signale pas par des badges de couleur, mais par la typographie : le certain en romain, le probable en italique, le possible relégué dans la marge avec un « ? ». Chaque affirmation porte un appel de note, et les notes sont les sources, générées depuis les factoïdes. On lit une page de livre, et chaque mot reste cliquable jusqu'au passage et à l'image.

**L'oncle.** Il faut aussi qu'elle soit citable. Tout est révisable, c'est le principe. Mais un collègue qui cite ma notice de Pierre Martin dans un article doit pouvoir retrouver, dans dix ans, ce que la notice disait le jour où il l'a lue.

→ **Proposition 4** : un gabarit de NOTICE par projet (rubriques et ordre), avec un apparat de notes généré automatiquement et une typographie de la certitude.
→ **Proposition 5** : des **instantanés citables**. Un état daté de la vue active, identifié de façon stable (permalien, et éventuellement un DOI pour une édition), reconstructible à partir des journaux. Les journaux (R25) le permettent déjà : il reste à le promettre.

### 2.5 L'équipe

**L'oncle.** J'ai encadré des dizaines de personnes. Les problèmes n'étaient pas techniques, ils étaient humains. Deux étudiants lisaient différemment la même abréviation. L'un rapprochait trop vite, l'autre jamais. Les conventions de transcription dérivaient en six mois. Notre remède était le **double dépouillement** d'un échantillon : deux personnes lisent le même cahier à l'aveugle, on compare, on discute et on corrige la convention.

Le document prévoit le contrôle par sondage pour la machine (§7.7 : « une part des actes validés est présentée à nouveau »). Rien pour les humains. Or le journal des corrections et les contributeurs existent déjà : tout est là pour mesurer l'accord entre lecteurs.

**Le neveu.** Ajoute la répartition du travail : « tel registre à Paul, tels folios à Léa ». Et la relecture : chaque acte versé par un débutant passe par un relecteur. Je ne parle pas d'un logiciel de gestion de projet, seulement de trois choses : une affectation, un état et un relecteur. La formation suit : un nouvel arrivant travaille d'abord sur des actes déjà validés, et l'outil lui montre ses écarts. C'est un tutoriel qui ne coûte rien, puisque la vérité de référence est déjà en base.

→ **Proposition 6** : affectation et relecture croisée (DEPOUILLEMENT affecté, état « à relire », relecteur distinct de l'auteur) ; double saisie d'un échantillon avec mesure d'accord, comme pour la machine ; mode formation sur des actes déjà validés.
→ **Proposition 7** : un **protocole de transcription** versionné du projet (abréviations, graphies, conventions). Il est référencé par chaque DEPOUILLEMENT et par chaque gabarit d'extraction (§7.1), car la machine et l'étudiant suivent la même règle.

---

## 3. Le volet micro : ce que les actes disent et que le modèle ne capte pas encore

### 3.1 « Feu », « veuve de », « défunt »

**L'oncle.** « Jean, fils de **feu** Pierre Martin. » Ce petit mot vaut de l'or : Pierre est mort avant la date de l'acte. C'est une borne de décès qui ne figure dans aucune sépulture. « Marie Dubois, **veuve de** Pierre Martin » : même chose, plus le mariage. Le mot « feu » n'apparaît nulle part dans le document, ni le mot « veuve ».

**Le neveu.** Et tu tiens là un indice de rapprochement redoutable. Si deux masques de « Pierre Martin » sont l'un « feu » en 1720 et l'autre témoin vivant en 1725, ce ne sont pas la même personne. Ou alors l'un des actes se trompe, et c'est un conflit à signaler.

**L'oncle.** Il faut le saisir comme un **état mentionné, lu**, et non déduit (R20). La déduction (« décédé avant le 3 mars 1712 ») est une contrainte temporelle produite par une conclusion.

→ **Proposition 8** : un état vital mentionné (« feu », « défunt », « veuve de », « vivant ») porté par le masque ou par une QUALITE d'état. Il alimente les contrôles de vraisemblance (§6.7), le veto chronologique du rapprochement et la question 9.2‑10.

### 3.2 La capacité de signer

**L'oncle.** « Qui a signé », « a déclaré ne savoir signer » : c'est la base de toute étude d'alphabétisation depuis Maggiolo. Le document parle de la signature surtout comme d'un **motif d'identification** (« signature identique »). Il faut aussi la saisir comme un **fait** : « a signé », « a fait sa marque », « ne sait signer ». Et, si possible, garder la zone d'image de la signature : le paraphe est un indice d'identité plus sûr qu'un nom.

→ **Proposition 9** : la signature comme attribut de la PARTICIPATION (signé, marque, déclare ne savoir, non précisé), avec une zone d'image facultative. La comparaison visuelle des paraphes devient un type d'indice.

### 3.3 Le surnom, le « dit », la maison

**L'oncle.** « Pierre Martin **dit** Lagrange. » Dans certaines régions, c'est la maison qui identifie, pas le patronyme. NOM a des types, et GeneWeb fournit `#nick` ; très bien. Le rapprochement, lui, doit savoir qu'un « dit » est souvent plus discriminant que le nom. C'est un point de barème (9.2‑1), pas de modèle. Je le note pour la calibration.

### 3.4 Les âges déclarés

**L'oncle.** « Âgé d'environ soixante ans » sur une sépulture : tout le monde sait que ces âges sont arrondis à la dizaine. La décision 23 traite déjà l'âge comme une date « déduite ». Il manque l'**attraction des âges ronds** : un âge déclaré de 60 ans devrait donner une fenêtre plus large qu'un âge de 57. Encore une question de paramètre, que je confie au barème.

---

## 4. Le volet de l'ergonomie : rendre l'outil moins rébarbatif que le papier

**L'oncle.** Je vais être franc. En 1978, on m'a installé un terminal et un bordereau de saisie à 40 champs. Mes étudiants ont perdu deux ans. Le formulaire informatique leur demandait de décider **au moment de la saisie** ce qu'ils ne savaient pas encore. Sur la fiche papier, on écrivait d'abord et on classait ensuite.

**Le neveu.** C'est la grande leçon, et le document y répond à moitié avec la saisie assistée (§7) : la machine pré‑remplit. Mais le circuit part de l'**image**. Il en faut un second qui parte de **la main du chercheur**.

### 4.1 La saisie en sténo

**Le neveu.** Le chercheur tape comme dans son carnet :

```text
3.3.1712 bapt Jean f. Pierre MARTIN lab. & Marie DUBOIS ; parr. Jean LEROY ; marr. Anne MARTIN ; tém. Claude PETIT m. d'école (sig.) — f°42v
```

La machine en tire le brouillon du §7.5 : factoïde, masques, rôles, qualités, signature. Elle l'affiche en dessous, structuré, et seules les incertitudes demandent un geste. Les abréviations sont celles du protocole du projet (proposition 7). C'est le même brouillon, la même règle R18 et le même ancrage (R19), sauf que l'ancre pointe dans la ligne tapée, qui devient elle‑même une transcription.

**L'oncle.** C'est mon bordereau de 1963, en mieux : on écrit vite, on ne quitte pas l'acte des yeux, et la structure arrive après. À une condition : que l'outil ne réécrive jamais ce que j'ai tapé. La ligne sténo est un document de travail, elle se garde.

→ **Proposition 10** : la saisie en sténo comme deuxième entrée du circuit §7, à côté de l'image (même brouillon, mêmes règles). On la teste en premier, car elle ne dépend ni de la reconnaissance d'écriture ni de la voix.

### 4.2 La table de tri

**L'oncle.** Sais‑tu comment nous identifiions les personnes ? Sur une grande table. On étalait toutes les fiches « Martin » de la paroisse, puis on faisait des **tas** : ce tas‑ci est un Pierre, celui‑là un autre Pierre, cette fiche je ne sais pas, je la mets de côté. On voyait tout d'un coup d'œil.

**Le neveu.** Le §6 propose l'inverse : un candidat à la fois, en colonnes. C'est parfait pour un doute précis, mais mauvais pour démêler un patronyme entier. Je veux une **table de tri** : tous les masques d'un groupe d'homonymes sous forme de cartes, chacune portant date, rôle, qualité, conjoint et lieu. On les fait glisser en piles, et chaque pile devient une personne. Une frise sous la table signale en direct l'impossibilité (« ce tas contient un homme baptisé en 1712 et mort en 1690 »). Les contrôles du §6.7 deviennent ainsi un retour immédiat, pas une alerte différée. Un tas « je ne sais pas » est permis : c'est le report du §6.8.

**L'oncle.** Et, quand la machine propose, elle propose des **tas**, pas des paires : « je pense que ces six fiches font un seul homme ».

→ **Proposition 11** : une table de tri par groupe d'homonymes, en complément de la comparaison par paires du §6. Une pile vaut un ensemble d'identifications avec une conclusion commune (R22). Les contrôles de vraisemblance y sont affichés en direct.

### 4.3 Le carnet

**L'oncle.** Il me manque la marge. Une idée qui n'est pas encore une conclusion : « vérifier si ce Leroy est le notaire de Mortagne », « le curé change d'écriture en 1709, copie postérieure ? ». Dans le modèle, la CONCLUSION est trop solennelle pour ça : elle a un auteur, une valeur et des effets. Et le brouillon `saisie` est réservé à l'extraction.

**Le neveu.** Une NOTE de travail, alors : texte libre, épinglable sur n'importe quoi (passage, masque, personne, folio, population), privée ou partagée avec l'équipe, et « promouvable » en conclusion d'un geste quand elle mûrit. La note ne touche à aucune vue. On retrouve toutes ses notes ouvertes dans un carnet, et c'est souvent par là qu'on commence sa journée.

→ **Proposition 12** : une entité NOTE (hors des couches Source et Interprétation, sans effet sur les vues), qu'on attache à toute entité et qu'on promeut en CONCLUSION.

### 4.4 Le « pourquoi ? » universel

**Le neveu.** Le document a toutes les justifications : indices, conclusions, effets, chaînes de prémisses (R28), sources hors calcul (R24). Il ne dit pas encore le **geste** qui les rend visibles. Je propose une seule règle d'interface : **toute valeur affichée répond à « pourquoi ? »**, au survol ou d'une touche, de la même façon partout. Pourquoi ce lieu ? Pourquoi cette date ? Pourquoi cette personne a‑t‑elle 3 enfants et pas 4 ? La réponse est la chaîne : conclusion, indices, factoïdes, passage, image.

**L'oncle.** C'était le rôle des notes de bas de page. Un historien n'a confiance que dans ce qu'il peut remonter.

→ **Proposition 13** : un principe d'interface « toute valeur répond à pourquoi ? », inscrit en tête du §6, comme pendant visible de R8 et de R24.

### 4.5 Le rythme de la file de décisions

**Le neveu.** Une file infinie décourage. Je propose des **séances** : un lot calibré (vingt minutes ou trente décisions), regroupé par thème (une famille, une paroisse), avec un bilan à la fin : décidé, reporté, ce que cela a débloqué. Ajoute un clavier complet pour les habitués : `a` activer, `r` rejeter, `p` reporter, `1` à `9` pour les motifs. Les meilleurs paléographes que j'ai observés ne touchent jamais la souris.

**L'oncle.** Et que le bilan dise ce qui a changé dans le livre : « trois notices modifiées ». C'est ce qui motive un étudiant.

→ **Proposition 14** : des séances de décision regroupées par thème, avec bilan, et un clavier complet (§6).

---

## 5. Le volet du document lui‑même

**L'oncle.** Un dernier mot sur la forme, car je l'ai lu en entier et peu de gens le feront.

- **Les règles sont dispersées.** R1 à R17 et R22 à R28 sont au §4.5, R18 à R21 au §7.6. Ceux qui lisent dans l'ordre trouvent R22 avant R18. Il faut un tableau unique des règles, avec une colonne « version d'origine » et une colonne « section ».
- **Le dictionnaire n'a pas d'exemples.** Une colonne « dans le baptême de Jean » (§4.6) pour chaque entité vaudrait dix paragraphes.
- **Il n'y a pas de glossaire.** Masque, factoïde, passage, emprise, enveloppe, cœur, halo : ces termes sont définis au fil du texte et ne sont réunis nulle part.
- **Certains titres sont datés** (« Modèle conceptuel v0.4 », « Traitement en v0.3 »). Le lecteur ne sait pas si cette partie est encore valable.
- **Le document fait 142 Ko.** Il faut un « modèle en dix pages » en tête (couches, agrégations, dix règles essentielles, un exemple), le reste devenant des annexes de référence.

**Le neveu.** Et un **parcours du chercheur** en tête, avant les entités : une journée de travail racontée de bout en bout (je dépouille, je trie, je doute, je reporte, je rédige, je cite), avec les sections qui la supportent. C'est ce qui manquait à ton terminal de 1978 : on donnait le schéma, jamais le mode d'emploi.

→ **Proposition 15** : une restructuration éditoriale, sans changer le modèle : modèle en dix pages, parcours du chercheur, glossaire, tableau unique des règles, exemples dans le dictionnaire, titres sans numéro de version.

### 5.1 Les promesses à tenir

**L'oncle.** Je finis par mon vieux métier de rabat‑joie. Le §7 dit que la lecture à voix haute est « l'apport le plus fort de ce circuit ». Peut‑être. On m'a promis la même chose de la reconnaissance optique en 1985. Une affirmation de ce genre doit être un **critère mesuré** : temps par acte, taux d'erreur résiduel et fatigue au bout de deux heures, comparés à la saisie en sténo et à la saisie manuelle, sur les 50 actes du test prévu. Et il faut écrire à l'avance **le seuil sous lequel on abandonne**.

**Le neveu.** De même pour la complexité. Qui dessinera les polygones des EMPRISES de 300 paroisses ? Il faut que le modèle dise ce qu'il fait **en mode dégradé** : un projet sans lieux historiques, seulement avec des communes actuelles, doit fonctionner, et le signaler honnêtement à l'écran (« lieu historique non renseigné »). Un modèle à étages, en somme : un premier étage aussi simple que GeneWeb, et chaque étage suivant facultatif.

→ **Proposition 16** : un protocole d'évaluation de la saisie assistée avec des seuils d'abandon écrits d'avance (§7, et test de la feuille de route sur ~50 actes).
→ **Proposition 17** : des niveaux d'exigence explicites (lieux, dépouillement, population) et un comportement documenté en mode dégradé.

---

## 6. Propositions à trancher

| # | Proposition | Nature | Effet sur le modèle | Moment suggéré |
|---|---|---|---|---|
| 1 | DEPOUILLEMENT : couverture, protocole, lacunes ; sens des absences | Modèle | Nouvelle entité ; éclaire 9.2‑10 et le barème (indices négatifs) | Avant la validation des propositions (indices négatifs) |
| 2 | POPULATION : critère versionné, inclusions et exclusions argumentées | Modèle | Nouvelle entité, à instruire avec 9.2‑6 | Avec les écrans |
| 3 | Statistique à trois étages (certain, probable, possible) ; R24 étendue aux nombres | Modèle et interface | Nouvelle section ; une règle possible (R29) | Avec les exports et les analyses |
| 4 | NOTICE : gabarit de rubriques, apparat de notes généré, typographie de la certitude | Interface | Vue, sans nouvelle table | Avec les écrans de lecture |
| 5 | Instantanés citables (permalien, état daté reconstructible) | Modèle | Garantie sur les journaux ; une règle possible | Avec le cycle de publication (décision 32) |
| 6 | Affectation, relecture croisée, double saisie avec mesure d'accord, mode formation | Modèle et interface | Champs sur DEPOUILLEMENT ; statut « à relire » | Avec la saisie |
| 7 | Protocole de transcription versionné, commun aux humains et aux gabarits | Modèle | Référentiel | Avec la saisie |
| 8 | État vital mentionné (« feu », « veuve de ») ; contrainte et indice | Modèle | Attribut lu, QUALITE d'état ou attribut du masque | Avec le rapprochement (barème v2) |
| 9 | Signature comme fait de la PARTICIPATION, zone d'image du paraphe | Modèle | Attribut de PARTICIPATION | Avec la saisie |
| 10 | Saisie en sténo, deuxième entrée du circuit §7 | Interface | Aucune nouvelle entité (brouillon §7.5) | **À tester en premier** dans la saisie |
| 11 | Table de tri par groupe d'homonymes ; la machine propose des tas | Interface | Identifications groupées par conclusion (R22) | Avec l'écran de validation |
| 12 | NOTE de travail, promouvable en conclusion | Modèle | Nouvelle entité, sans effet sur les vues | Avec les écrans |
| 13 | Principe « toute valeur répond à pourquoi ? » | Interface | Aucune | Tête du §6 |
| 14 | Séances de décision avec bilan ; clavier complet | Interface | Aucune | Avec l'écran de validation |
| 15 | Restructuration éditoriale du document | Document | Aucune | Quand vous voulez |
| 16 | Protocole d'évaluation de la saisie assistée, seuils d'abandon | Méthode | Aucune | Avant le test des ~50 actes |
| 17 | Niveaux d'exigence et mode dégradé documentés | Modèle et document | Aucune nouvelle table | Avec le socle PostgreSQL |

Points 3.3 (le « dit ») et 3.4 (âges ronds) : ce ne sont pas des propositions de modèle, mais des remarques pour la calibration du barème (9.2‑1).

**L'oncle.** Si je ne devais en garder que trois : le **dépouillement** (1), sans lequel aucun silence ne parle ; la **statistique à trois étages** (3), qui fait de l'incertitude un résultat et non un défaut ; et la **table de tri** (11), parce que c'est ainsi qu'on a toujours fait, et qu'on le faisait bien.

**Le neveu.** J'ajouterais la **sténo** (10). C'est la moins chère à construire, et c'est elle qui décidera si les étudiants aiment l'outil ou le subissent.
