# Le travail du chercheur dans Chronologia

*9 novembre 2026. Note de vision, suite de la relecture (`docs/relecture-oncle-neveu.md`). Elle répond à une question : avec la saisie assistée, que fait le chercheur, et que fait le responsable scientifique ? Les propositions du §7 ont toutes été retenues le 9 novembre 2026, avec un ajout du porteur du projet (K) : décisions 44 à 54 du modèle v0.12.*

---

## 1. La thèse

**Le chercheur n'est ni écarté du travail de dépouillement, ni dispensé de le faire. La machine retire la copie, pas la lecture.**

Le travail d'une prosopographie se décompose en cinq gestes, qui n'ont pas la même nature :

| Geste | Ce qu'il produit | Couche | Rôle de la machine |
|---|---|---|---|
| **Lire** : déchiffrer, relever, transcrire | Ce que dit la source | Source | Elle prépare, propose une lecture ou relit en second (§7, §7.8). |
| **Relier** : rapprocher les masques, les actes, les lieux | Des identifications | Interprétation | Elle propose des candidats et des piles (R18, R26, §6.9). |
| **Juger** : trancher, argumenter, assumer une incertitude | Des conclusions | Interprétation | Aucun. Elle signale ; elle ne décide jamais (R18, R25). |
| **Chercher** : remarquer, supposer, vérifier | Des notes et des hypothèses | Travail | Elle calcule les conséquences et montre ce qui détonne (§4). |
| **Écrire** : notices, tableaux, publication | Des vues et des instantanés | Vues | Elle met en forme et produit l'apparat de notes. |

La règle R18 répartit les rôles sans rien interdire à l'humain : ce qui est réservé, c'est le **jugement**, que la machine n'exerce jamais. Le chercheur reste libre de faire lui-même toute tâche « de petite main ». La seule interdiction qui pèse sur lui est déjà au §7.7 : **valider sans avoir lu**.

## 2. Pourquoi le chercheur doit continuer à lire

Trois raisons, dont aucune n'est sentimentale.

1. **La découverte naît de la lecture.** Ce qui fait une thèse se voit rarement dans un champ structuré : un changement d'écriture du curé en 1709, une mention marginale, un parrain qui revient d'une paroisse à l'autre, un registre qui s'interrompt. Un brouillon extrait par la machine ne retient que ce que son gabarit a prévu. Celui qui ne lit plus ne remarque plus.
2. **On ne juge bien que ce qu'on sait faire.** Un chercheur qui n'a jamais lu un registre de cette paroisse ne sait pas évaluer les propositions de la machine. Il les accepte toutes (biais d'automatisation) ou les refuse toutes. La validation devient machinale, ce qui est le premier risque du §7.7.
3. **La machine doit être mesurée.** Son taux d'erreur ne se connaît que par comparaison avec une lecture humaine indépendante. Sans une part de lecture humaine première, aucune donnée ne permet de dire si l'assistance aide ou nuit.

À l'inverse, la machine doit retirer ce qui est **copie et non lecture** : recopier pour la centième fois « fils légitime de », reporter une date déjà lue dans trois champs, retaper un nom déjà connu, chercher un acte dans un registre de 400 vues. C'est cette fatigue qui, champ après champ, dégrade la qualité (§7).

## 3. Trois modes de dépouillement, choisis et non subis

Chaque DEPOUILLEMENT déclare son `mode` (décision 39). Le choix revient au responsable scientifique, par type de source, et se révise au vu des mesures.

| Mode | Qui lit en premier | Qui relit | Usage |
|---|---|---|---|
| **Lecteur premier** | Le chercheur, en sténo (§7.8) ou à la main | La machine, en second : elle signale les divergences entre sa lecture et celle du chercheur | Sources difficiles ou nouvelles ; formation ; échantillon de calibration |
| **Machine première** | La machine (HTR, voix, extraction, §7.1) | Le chercheur, qui vérifie les champs signalés | Séries formulaires et bien lisibles, une fois la machine mesurée sur ce fonds |
| **Échantillonné** | La machine, avec une part tirée au hasard que le chercheur lit d'abord sans voir la proposition | Le chercheur | Gros volumes : on garde une mesure continue de la qualité |

Le mode « lecteur premier » renverse l'usage habituel de l'IA : la machine n'y remplace pas le lecteur, elle joue le rôle du **second lecteur** du double dépouillement, sans fatigue ni complaisance.

## 4. Se débrancher et reprendre

Le chercheur a le droit de travailler hors de l'outil : en salle de lecture sans réseau, sur papier, sur tablette, dans un tableur. L'outil ne doit rien imposer à ce moment, et tout reprendre ensuite.

- **Partir** : un **dossier de travail** s'exporte pour un dépouillement : images ou cotes, folios à faire et lacunes déjà connues, liste des abréviations du projet, actes déjà saisis (pour ne pas les refaire), notes ouvertes sur ces cibles.
- **Travailler** : des lignes en sténo dans un fichier texte, un tableur, des photos prises aux archives, des notes au crayon tapées le soir.
- **Revenir** : le dossier se recharge comme un **lot de saisie** rattaché à son dépouillement. Les lignes sténo passent par la même analyse et la même validation (§7.8, R18, R19). Les photos entrent par le dépôt (§7.1). Les notes deviennent des NOTES (R30).
- **Sans perte ni écrasement** : rien de ce qui a été fait dehors n'est fusionné en silence (R24). Si la base a changé entre-temps (un collègue a saisi le même acte, une identification a été tranchée), l'outil montre le doublon ou le conflit ; tout rattachement reste une proposition.

Le travail débranché n'est donc pas une exception tolérée : c'est un **mode de saisie** comme un autre, avec sa provenance (`mode` du dépouillement, lot de saisie).

## 5. Découvrir, supposer, confirmer, infirmer

C'est la question la plus importante. Une base qui ne fait que stocker des réponses n'aide pas à poser des questions. L'outil doit accompagner un cycle en cinq temps.

### 5.1 Faire émerger : le tableau des curiosités

La machine excelle à voir ce qui détonne, à condition de ne pas prétendre l'expliquer. Elle tient un **tableau des curiosités** : des signaux calculés, chacun avec son effectif et ses éléments, sans interprétation.

- **Creux et ruptures** : un déficit d'actes dans la couverture, un changement brutal de formules ou de scripteur, une paroisse qui cesse d'apparaître.
- **Récurrences** : un parrain choisi par dix familles sans lien connu, des témoins qui viennent toujours d'une autre paroisse, un notaire qui concentre une catégorie de contrats.
- **Écarts** : un âge au mariage très différent de celui de son groupe, une profession qui change de rang, un comptage dont les étages divergent (§6.10).
- **Contradictions** : les avertissements de vraisemblance (§6.7), les conflits de date et de lieu (§6.3, §6.4).

Un signal n'est ni une conclusion ni une proposition d'identification. C'est une invitation à regarder. Le chercheur l'écarte, ou il en fait une note.

### 5.2 Formuler : l'hypothèse comme objet

Une hypothèse est une NOTE de type « hypothèse » (§6.11). Pour qu'elle soit testable, l'outil demande, sans l'imposer, deux listes :

- **ce qui la confirmerait** : « si Pierre dit Lagrange est Pierre Martin, ses enfants baptisés entre 1710 et 1720 ont Marie Dubois pour mère » ;
- **ce qui l'infirmerait** : « une sépulture de Pierre Martin avant 1715 dans un registre dépouillé ».

Chaque attente s'écrit, si possible, comme une **requête enregistrée** sur la base. L'outil peut alors dire, à tout moment, lesquelles sont vérifiées, contredites ou encore sans réponse, et si l'absence de réponse tient à une lacune ou à un registre non dépouillé (R29).

### 5.3 Tester : le bac à sable « et si »

On ne teste pas une hypothèse en l'inscrivant dans la vue de référence. Le **bac à sable** applique un scénario d'identifications et de conclusions hypothétiques dans une vue privée, puis recalcule :

- les personnes reconstruites et leurs contrôles de vraisemblance (ce qui devient impossible, ce qui devient cohérent) ;
- les comptages à trois étages (ce que l'hypothèse change aux résultats) ;
- les attentes de l'hypothèse (lesquelles passent au vert).

Le résultat se lit comme une **différence** avec la vue de référence. Rien n'entre au journal (R25) tant que le chercheur ne promeut pas le scénario. Une promotion crée les identifications et une conclusion dont les prémisses sont les éléments du test (CONCLUSION_PREMISSE, R28).

### 5.4 Conclure, ou renoncer

- **Confirmée** : la note est promue en conclusion (§6.11), avec ses prémisses.
- **Infirmée** : la note est close avec le motif « infirmée » et ce qui l'infirme. Un résultat négatif est un résultat : il évite à un collègue de refaire le chemin, et il se publie.
- **En suspens** : la note reste ouverte, ou la question est reportée (§6.8).

### 5.5 Revenir

Une hypothèse ouverte ou infirmée **se réveille** quand une source nouvelle touche ses cibles ou change la réponse d'une attente, comme une incertitude assumée (§6.5). C'est ainsi qu'un dépouillement fait en 2028 peut rouvrir une piste abandonnée en 2026.

**Garde-fou.** La machine montre des motifs, pas des causes. Un tableau de curiosités consulté sans retenue produit des coïncidences : tout signal affiche son effectif et ses étages de certitude, et seul l'historien nomme une explication. Un modèle de langage peut suggérer des pistes de lecture ; elles sont marquées comme telles et entrent comme des signaux, jamais comme des notes d'un chercheur.

## 6. Les rôles

| Rôle | Ce qu'il fait | Ce qui lui revient en propre |
|---|---|---|
| **Responsable scientifique** | Définit les questions et le périmètre du corpus. Fixe la méthode de dépouillement, la liste d'abréviations, les seuils (barème, vraisemblance, « possiblement vivant »). Choisit le mode de chaque dépouillement (§3). Suit la qualité : taux de correction, accord entre lecteurs, couverture. Forme les nouveaux. | **Désigner la vue de référence** quand deux chercheurs divergent (R11 ; l'avis écarté reste conservé). **Signer** les instantanés publiés. **Déléguer** : décider quelles tâches la machine fait en premier. |
| **Chercheur** | Dépouille, trie (§6.9), doute, note, formule et teste des hypothèses, argumente, rédige des notices. | Ses conclusions, signées. Le droit de faire à la main ce que la machine pourrait faire. Le droit d'être en désaccord, et que ce désaccord soit conservé. |
| **Contributeur en formation** | Dépouille, d'abord sur des actes déjà validés (mode formation), puis sur des sources réelles. | Ses saisies, relues par un chercheur avant validation (`relecteur_id` du dépouillement). |
| **Agent (machine)** | Lit en premier ou en second, propose des identifications et des piles, calcule les contrôles, les comptages et les curiosités, explique ses candidats. | Rien : il ne décide, ne rejette, ni n'écrit dans un carnet (R18, R25, R30). Il ne parle qu'en propositions, en indices et en signaux. |

Ce qui est interdit, et à qui :

- à la **machine** : décider, rejeter, verser sans validation, écrire une note au nom de quelqu'un ;
- à **tous** : valider sans avoir lu, décider sans être nommé comme auteur, écrire un texte libre sans statut (R30) ;
- à **personne** : faire soi-même une tâche que la machine sait faire, travailler hors de l'outil, ou garder son désaccord.

## 7. Propositions à trancher

| # | Proposition | Nature | Effet sur le modèle |
|---|---|---|---|
| A | **Principe « la machine retire la copie, pas la lecture »**, en tête du §7, avec le tableau des cinq gestes (§1) | Principe | Aucun |
| B | **Trois modes de dépouillement** (lecteur premier, machine première, échantillonné), choisis par le responsable scientifique et révisables au vu des mesures | Méthode | Valeurs de `DEPOUILLEMENT.mode` |
| C | **Part minimale de lecture humaine première** dans chaque fonds traité par la machine, qui sert à la calibration, à la formation et à la mesure de la qualité | Méthode | Aucune nouvelle table |
| D | **Dossier de travail hors ligne et reprise** comme lot de saisie rattaché au dépouillement | Modèle et interface | Export et import ; aucune nouvelle entité |
| E | **Hypothèse testable** : attentes « confirmerait » et « infirmerait » attachées à une note, écrites si possible en requêtes enregistrées | Modèle | Attributs de NOTE (type « hypothèse ») |
| F | **Bac à sable « et si »** : scénario privé, recalcul, différence avec la vue de référence, promotion en conclusion | Modèle et interface | Scénario hors journal ; peut-être une règle (rien n'en sort sans promotion) |
| G | **Tableau des curiosités** : signaux calculés, sans interprétation, avec effectif et étages | Interface | Signaux hors file de décisions |
| H | **Hypothèse infirmée conservée et publiable** comme résultat négatif | Modèle | Motif « infirmée » à la clôture d'une NOTE |
| I | **Rôles et délégations explicites** (responsable scientifique, chercheur, en formation, agent) et prérogatives du responsable : vue de référence, signature des instantanés, délégation | Modèle | Rôle du CONTRIBUTEUR dans le projet |
| J | **Parcours du chercheur** en tête du document de référence : une journée de travail, de la couverture au carnet, au tri et à la notice | Document | Aucun |

Si l'on ne devait en retenir que trois : **A**, parce qu'il fixe la doctrine ; **F**, parce que c'est le seul outil qui aide vraiment à penser ; et **C**, parce que sans lecture humaine, aucune assistance ne se mesure.

**Ajout retenu (K, décision 54).** Tout participant au projet, quel que soit son rôle, peut formuler une question de recherche ou une hypothèse et la faire remonter dans l'outil. Le responsable scientifique l'arbitre par une réponse motivée (retenue, non retenue, à reformuler, rattachée à une autre) ; aucune question n'est enterrée (R32). Les questions retenues forment le programme du projet ; une question non retenue reste la note de son auteur, qui peut poursuivre sa piste.
