# Mode opératoire — étalon du projet Hesdin

Ce document décrit l'enchaînement des commandes pour une commune (Hesdin, Lanchères, ou un témoin). Les données ne vont **jamais** dans le dépôt : chaque commande refuse un chemin situé dans le dépôt (`erreur : données dans le dépôt`, code 2), lien symbolique compris.

## Arborescence (hors du dépôt)

```
<donnees>/<commune>/
├── inventaire.csv              # unités disponibles, lacunes motivées
├── correspondance_socface.csv  # recensements ↔ Socface
├── verifications.csv           # registre des vérifications (AD, mairies)
├── cadre.csv                   # effectifs par type et par année, pages par dénombrement
├── candidats_remontee.csv      # candidats de la remontée (avant 1872)
├── tirage/                     # tirage.csv, tirage.meta.json, seconde_lecture.csv
├── escriptorium/               # exports de la transcription machine
├── fiches/
│   ├── etalon/                 # première lecture humaine (YAML)
│   ├── seconde_lecture/        # seconde lecture (meta.lecture: seconde)
│   ├── socface/
│   └── machine/
├── textes/                     # .txt appariés par nom de fiche (etalon/, machine/…)
└── mesures/                    # CSV d'agrégats produits par etalon-mesurer
```

## Ordre des commandes

1. **Inventaire** — valider les fichiers de la commune :
   `uv run python -m chronologia etalon-inventaire --donnees <donnees>/<commune>`
2. **Graines** — fixer et **noter dans le registre** les deux graines (tirage et seconde lecture) **avant tout tirage**.
3. **Tirage** :
   `uv run python -m chronologia etalon-tirer --cadre <…>/cadre.csv [--remontee <…>/candidats_remontee.csv] --commune <commune> --actes N --pages-par-denombrement P [--remontee-n R] --graine G --graine-seconde S --sortie <…>/tirage`
4. **Pilote** — transcrire l'année et la page pilotes affichées, relire les conventions, les ajuster si besoin (en datant la modification), puis transcrire l'échantillon.
5. **Seconde lecture** — au moins **trois semaines** après la première lecture de la même unité ; le délai se vérifie par `meta.date_saisie` des deux fiches.
6. **Mesures** :
   `uv run python -m chronologia etalon-mesurer --etalon <…>/fiches/etalon --autre <…>/fiches/machine --source machine [--textes-etalon <…>/textes/etalon --textes-autre <…>/textes/machine] --sortie <…>/mesures`
   puis la même commande avec `--source socface` et `--source seconde_lecture`.

## Règle des graines

Les graines sont **fixées et notées avant tout tirage, et jamais choisies après coup**. Relancer un tirage avec une autre graine parce que le premier « ne plaît pas » invalide l'échantillon. Un tirage se rejoue à l'identique avec les mêmes fichiers et les mêmes graines ; `tirage.meta.json` garde les empreintes de ce qui a servi. `etalon-tirer` refuse d'écraser un `tirage.csv` existant ; `--remplacer` ne sert qu'à corriger une erreur de fichier d'entrée, motivée au registre.

## Lecture des résultats

- Chaque CSV de mesures commence par : `# taux sur l'échantillon tiré, non redressés ; voir tirage.meta.json` (R29).
- Une fiche de l'étalon sans pendant compte en faux négatif ; une fiche en trop, en faux positif ; leur nombre est affiché.
- La colonne `inventes` compte les textes donnés là où l'étalon ne prévoit rien (champ non applicable) : hors précision, mais publiés.
- En seconde lecture, l'accord et les mesures de texte ne portent que sur les fiches relues.
- `tirage.meta.json` déclare les strates vides, les années sans acte d'un type et les dénombrements attendus sans page (`denombrements_vides`).
- Les sorties ne contiennent que des comptes et des taux : aucun nom, aucune cote, aucun texte transcrit.
