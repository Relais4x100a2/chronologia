# Listes d'inventaires d'archives (data.gouv.fr)

Copies, tenues à jour automatiquement, de trois listes d'instruments de recherche publiées en données ouvertes. Elles servent au **repérage des sources** : quels fonds, dans quel service, parlent d'une commune sur une période. C'est l'outil du chantier 1 du projet Hesdin-Lanchères (inventaire et plan de dépouillement), et de tout autre terrain.

| Clé | Jeu | Lignes | Producteur |
|---|---|---|---|
| `an` | [Liste des inventaires des Archives nationales publiés en ligne](https://www.data.gouv.fr/datasets/liste-des-inventaires-des-archives-nationales-publies-en-ligne) | ~31 000 | Ministère de la Culture |
| `ad` | [Liste des inventaires d'archives départementales sur FranceArchives](https://www.data.gouv.fr/datasets/liste-des-inventaires-darchives-departementales-sur-francearchives) | ~56 300 (85 départements) | Maïwenn Bourdic, d'après les fichiers EAD de FranceArchives (version du 27/08/2025) |
| `ac` | [Liste des inventaires d'archives communales sur FranceArchives](https://www.data.gouv.fr/datasets/liste-des-inventaires-darchives-communales-sur-francearchives) | ~4 000 (34 départements) | idem |

Licence : **Licence Ouverte 2.0** (Etalab). Toute réutilisation mentionne la source (le jeu et son producteur, ci-dessus) et la date de la version (`ressource_modifiee` dans `manifeste.json`).

## Fichiers

- `an.csv.gz`, `ad.csv.gz`, `ac.csv.gz` : le CSV d'origine, octet pour octet, compressé sans date (gzip déterministe : une même version donne les mêmes octets, donc aucun commit inutile).
- `manifeste.json` : **généré**. Ressource retenue, URL, date de modification, empreintes SHA-1 (celle de data.gouv.fr, vérifiée) et SHA-256, taille, nombre de lignes.
- `sources.json` : les trois jeux suivis, le motif de la ressource à prendre et les **colonnes attendues**. C'est un contrat : si data.gouv.fr change les colonnes, la mise à jour s'arrête.

## Mise à jour

- Automatique : le workflow `.github/workflows/inventaires-archives.yml` tourne le 7 de chaque mois (et à la demande). S'il y a une nouvelle version, il ouvre une demande de fusion `maj/inventaires-archives` ; **personne ne fusionne à la place d'un humain** (R18). Prérequis côté dépôt : autoriser GitHub Actions à créer des demandes de fusion (Settings → Actions → General → *Allow GitHub Actions to create and approve pull requests*).
- À la main : `python3 tools/maj_inventaires.py` (bibliothèque standard seulement). `--verifier` ne rien écrit et rend le code 3 si une version nouvelle existe.
- Refus (code 1, rien d'écrit, R24) : colonnes changées, empreinte différente de celle annoncée, plusieurs ressources candidates, ou baisse de plus de 20 % du nombre de lignes (à accepter après examen avec `--accepter-baisse`).

## Consultation

```bash
uv run python -m chronologia sources-reperer --lieu Hesdin --de 1872 --a 1911
uv run python -m chronologia sources-reperer --departement Somme --mots recensement
uv run python -m chronologia sources-reperer --insee 80463 --detail
uv run python -m chronologia sources-reperer --niveau an --mots "Légion d'honneur"
```

Le lieu se cherche en mots entiers, sans souci d'accents ni de casse, dans la commune, le titre et l'index des lieux : « Hesdin » trouve aussi « Auchy-lès-Hesdin » et « Vieil-Hesdin ». Rien n'est trié à la place du chercheur. Un inventaire sans dates exploitables est **gardé** quand on filtre par période, et compté à part.

## Limites (à garder en tête)

- Niveau haut seulement (`<eadheader>`, `<archdesc>`) : un fonds qui contient des pièces sur une commune sans la nommer au niveau haut n'apparaît pas. L'absence d'un résultat ne prouve pas l'absence de sources. Ex. : Lanchères n'apparaît ni dans « Registres paroissiaux et de l'état civil » (5MI_D61) ni dans « Recensement de la population » (6M) des AD80, qui la couvrent pourtant.
- Champs tronqués à 1 000 caractères par le script d'extraction du producteur ; index très inégalement remplis (dans `ad` : commune et INSEE 14 %, index des lieux 54 %, personnes 15 %).
- Pas d'adresse web des inventaires de FranceArchives dans les listes `ad` et `ac` : seulement le chemin du fichier EAD (service en tête, ex. `FRAD062/…`). Les Archives nationales ont une adresse (`url_slv`).
- Les listes `ad` et `ac` reposent sur un instantané de FranceArchives (27/08/2025) : leur fraîcheur dépend de leur producteur, pas de ce dépôt.

## Place dans le modèle

Ressource de référence, comme `docs/geneweb/` : **pas** une couche du modèle. Un inventaire n'est pas un PASSAGE et ne crée aucun factoïde (R2). Le lien avec la couche Travail (un DEPOUILLEMENT ou une LACUNE qui cite un instrument de recherche, décision 39) n'est pas décidé : à consigner dans le document de référence avant tout code qui l'utiliserait.
