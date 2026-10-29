# Chronologia

Modèle de données historique orienté événements, à la croisée de la prosopographie, de la généalogie et de l'analyse relationnelle.

## Contenu

| Chemin | Contenu |
|---|---|
| `docs/modele-evenement-masque-factoide.md` | Document de référence v0.7.10 : corpus, modèle Événement–Masque–Factoïde, lieux historiques et sites, import GeneWeb, interface, saisie assistée, implémentation. |
| `docs/etude-page-claude.html` | Version page du document, générée par `tools/build_page.py`. |
| `docs/geneweb/` | Références du format GeneWeb (`gwFormat.md`, `genewWikitext.md`) pour le connecteur d'import. |
| `maquettes/design/` | Les cinq écrans de la maquette (dépôt et lecture à voix haute, validation d'un acte, rattachements, conflit de date, conflit de lieu). |
| `tools/` | Script de génération de la page. |
| `CLAUDE.md` | Contexte du projet pour Claude Code. |

## Régénérer la page

```bash
pip install markdown
python3 tools/build_page.py
```

## Historique

Conçu de septembre à octobre 2026 dans une conversation Claude (Cowork). Versions 0.1 à 0.7 du modèle : voir le journal des versions en tête du document.
