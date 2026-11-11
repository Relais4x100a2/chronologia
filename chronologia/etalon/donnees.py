"""Garde-fou : aucun fichier de données du projet ne se lit ni ne s'écrit dans le dépôt."""

from pathlib import Path


class DonneesDansLeDepot(ValueError):
    """Un chemin de données se résout sous la racine du dépôt."""


def racine_depot() -> Path:
    """Racine du dépôt Chronologia, calculée à l'appel."""
    return Path(__file__).resolve().parents[2]


def verifier_hors_depot(chemin: Path, racine: Path | None = None) -> Path:
    """Renvoie ``chemin`` résolu, ou lève ``DonneesDansLeDepot`` s'il est dans le dépôt."""
    resolu = chemin.resolve()
    base = (racine if racine is not None else racine_depot()).resolve()
    if resolu == base or base in resolu.parents:
        raise DonneesDansLeDepot(f"données dans le dépôt : {resolu}")
    return resolu
