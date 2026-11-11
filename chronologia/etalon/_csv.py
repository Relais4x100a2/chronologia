"""Lecture de CSV de projet : erreurs localisées, jamais la valeur fautive (garde-fou nominatif)."""

import csv
from collections.abc import Callable, Collection, Mapping, Sequence
from pathlib import Path

Ligne = Mapping[str, str]


class ValeurInvalide(ValueError):
    """Une colonne d'une ligne est invalide ; le message ne contient pas la valeur."""

    def __init__(self, colonne: str, code: str) -> None:
        super().__init__(f"colonne {colonne} : {code}")
        self.colonne = colonne
        self.code = code


def texte(ligne: Ligne, colonne: str, obligatoire: bool = True) -> str:
    valeur = (ligne.get(colonne) or "").strip()
    if obligatoire and not valeur:
        raise ValeurInvalide(colonne, "obligatoire")
    return valeur


def choix(ligne: Ligne, colonne: str, valeurs: Collection[str], vide_permis: bool = False) -> str:
    valeur = texte(ligne, colonne, obligatoire=not vide_permis)
    if valeur and valeur not in valeurs:
        raise ValeurInvalide(colonne, "valeur_inconnue")
    return valeur


def entier(ligne: Ligne, colonne: str) -> int:
    valeur = texte(ligne, colonne)
    if not valeur.isdigit():
        raise ValeurInvalide(colonne, "entier_attendu")
    return int(valeur)


def entier_ou_vide(ligne: Ligne, colonne: str) -> int | None:
    if not texte(ligne, colonne, obligatoire=False):
        return None
    return entier(ligne, colonne)


def charger[T](
    chemin: Path, colonnes: Sequence[str], construire: Callable[[Ligne], T]
) -> tuple[list[T], list[str]]:
    """Lit ``chemin`` (UTF-8, en-tête) et construit un objet par ligne valide.

    Les erreurs ont la forme ``"ligne N : colonne C : code"`` ; la ligne 1 est l'en-tête.
    """
    try:
        with chemin.open(encoding="utf-8", newline="") as f:
            lignes = list(csv.DictReader(f))
            entete = list(lignes[0].keys()) if lignes else _entete(chemin)
    except UnicodeDecodeError:
        return [], ["encodage_invalide"]
    except csv.Error:
        return [], ["csv_invalide"]
    manquantes = [c for c in colonnes if c not in entete]
    if manquantes:
        return [], [f"ligne 1 : colonnes manquantes : {', '.join(manquantes)}"]
    objets: list[T] = []
    erreurs: list[str] = []
    for numero, ligne in enumerate(lignes, start=2):
        try:
            objets.append(construire(ligne))
        except ValeurInvalide as e:
            erreurs.append(f"ligne {numero} : {e}")
    return objets, erreurs


def _entete(chemin: Path) -> list[str]:
    with chemin.open(encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])
