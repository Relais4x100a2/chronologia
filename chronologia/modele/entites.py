"""Entités de la couche Source et identifications associées (modèle v0.7.2).

Toutes les entités sont immuables (R10). Les références entre entités sont des
clés locales à un lot d'import (``P1``, ``M3``…) ; les identifiants de base de
données sont attribués à l'insertion.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class Passage:
    ref: str
    citation_brute: Optional[str]
    # Provenance dans le fichier d'import (lignes 1-indexées, bornes incluses).
    fichier_source: Optional[str] = None
    ligne_debut: Optional[int] = None
    ligne_fin: Optional[int] = None
    transcription: Optional[str] = None
    cle_externe: Optional[str] = None


@dataclass(frozen=True)
class Masque:
    ref: str
    passage_ref: str
    nom_ecrit: str
    sexe: Optional[str]
    cle_externe: str


@dataclass(frozen=True)
class Factoide:
    ref: str
    passage_ref: str
    type_evenement: Optional[str]
    date_declaree: Optional[str] = None
    date_min: Optional[date] = None
    date_max: Optional[date] = None
    calendrier: Optional[str] = None
    date_incertaine: bool = False
    # Chaîne exactement comme écrite dans la source (R13), avant normalisation.
    date_brute: Optional[str] = None
    cle_famille: Optional[str] = None


@dataclass(frozen=True)
class Participation:
    factoide_ref: str
    masque_ref: str
    role: str
    ordre: int
    note: Optional[str] = None  # wnote GeneWeb : note d'auteur sur le témoin


@dataclass(frozen=True)
class Relation:
    factoide_ref: str
    sujet_masque_ref: str
    objet_masque_ref: str
    type_relation: str
    orientation: Optional[str]
    degre: str = "certain"


@dataclass(frozen=True)
class Evenement:
    ref: str


@dataclass(frozen=True)
class IdentEvenement:
    factoide_ref: str
    evenement_ref: str
    degre: str
    statut: str


@dataclass(frozen=True)
class Qualite:
    """Rôle durable unaire (profession, titre). ``role`` est le libellé écrit."""

    ref: str
    factoide_ref: str
    masque_ref: str
    categorie: str  # profession | titre
    role: str
    valide_debut: Optional[date] = None
    valide_fin: Optional[date] = None
    rang: Optional[int] = None


@dataclass(frozen=True)
class MentionLieu:
    ref: str
    factoide_ref: str
    forme_ecrite: str
    forme_normalisee: Optional[str]
    fonction: str  # evenement | domicile | origine | titre
    masque_ref: Optional[str] = None
    qualite_ref: Optional[str] = None
    epoque_designation: str = "moderne"


@dataclass(frozen=True)
class Conclusion:
    """Prose d'auteur importée (note de personne) : un point de vue, pas un fait."""

    ref: str
    cible_masque_ref: str
    argument: str
    valeur: Optional[str] = None


@dataclass(frozen=True)
class Lot:
    """Provenance d'un import (LOT_IMPORT)."""

    format: str
    fichier: Optional[str]
    empreinte: Optional[str]
    outil: str
    version: str
    date: datetime
    statut: str
    nb_entites: int
