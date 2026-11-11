# Conventions de transcription — projet Hesdin

> **Proposition à valider par le chercheur.** Valable pour les deux terrains (Hesdin et Lanchères) et pour leurs témoins (Saint-Omer, Saint-Valery-sur-Somme). Ces conventions sont fixées **avant** le pilote (note de conception, §8.3). Une fois le pilote commencé, toute modification est datée et motivée ici.

## Principe

On transcrit **ce qui est écrit**, pas ce que l'on comprend (R13 : aucune résolution dans la couche Source). Toute normalisation se fait plus tard, dans la couche Interprétation.

## Règles

| Cas | Convention | Exemple fictif |
|---|---|---|
| Abréviations | conservées telles qu'écrites, jamais développées | `Jn Bapte` reste `Jn Bapte` |
| Ponctuation, majuscules | telles qu'écrites | `jean fictif` n'est pas corrigé |
| Orthographe | telle qu'écrite, fautes comprises | `cordonier` |
| Chiffres en lettres | conservés en lettres | `vingt deux ans` |
| Mot barré | `[barré: …]` | `[barré: Pierre]` |
| Ajout interlinéaire ou marginal | `[ajout: …]` ; une mention marginale va **aussi** dans `mentions_marginales` | `[ajout: le jeune]` |
| Lettre incertaine | `[?]` après la lettre | `Mar[?]tin` |
| Passage illisible | `[illisible]` | `né à [illisible]` |

## Correspondance avec les états des fiches

Un champ de fiche prend l'un des cinq états suivants :

| État | Quand | Écriture dans la fiche |
|---|---|---|
| lisible | tout le champ est lu, avec au plus quelques `[?]` | la chaîne transcrite |
| partiel | une partie seulement est lue | `{illisible: partiel, lu: "…"}` (la partie lue) |
| illisible | rien n'est lu, mais le registre porte une écriture | `{illisible: true}` |
| absent | le registre ne porte rien à cet endroit | `{absent: true}` |
| non applicable | le champ n'a pas de sens pour cette ligne ou cet acte | `null` (ou champ omis) |

Les états partiel et illisible sont comptés à part dans les mesures ; ils n'entrent ni en vrai positif ni en faux négatif.

## Rang de première mention

Dans un acte, les personnes sont numérotées (`rang` 1, 2, 3…) **dans l'ordre de leur première mention dans le corps du texte**, marge exclue. Une personne citée seulement en marge reçoit un rang après toutes celles du corps. Dans une page de recensement, le `ligne` reprend la ligne de la page, de haut en bas.

La comparaison se fait par rang ou par ligne, jamais par la valeur lue : un rang mal attribué coûte des erreurs, c'est voulu.
