"""Profils comparés par le rapprochement d'homonymes (décision 20).

Un ``MasqueObserve`` est ce qu'un masque montre : son nom, les faits datés où il
tient un rôle, les parents et conjoints nommés dans son passage. Un
``ProfilPersonne`` réunit les masques activement identifiés à une personne (R8).
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple


@dataclass(frozen=True)
class NomPersonne:
    nom: str
    prenoms: str


@dataclass(frozen=True)
class FaitDate:
    """Un rôle tenu dans un factoïde, avec les bornes de sa date."""

    role: str
    debut: Optional[date]
    fin: Optional[date]

    @property
    def datee(self) -> bool:
        return self.debut is not None and self.fin is not None


@dataclass(frozen=True)
class MasqueObserve:
    masque_id: int
    nom: NomPersonne
    faits: Tuple[FaitDate, ...] = ()
    pere: Optional[NomPersonne] = None
    mere: Optional[NomPersonne] = None
    conjoints: Tuple[NomPersonne, ...] = ()


@dataclass(frozen=True)
class ProfilPersonne:
    """Une personne et ses masques ; ``base`` sépare les lignées de fichiers."""

    personne_id: int
    base: str
    masques: Tuple[MasqueObserve, ...]

    @property
    def noms(self) -> Tuple[NomPersonne, ...]:
        return tuple(dict.fromkeys(m.nom for m in self.masques))

    @property
    def faits(self) -> Tuple[FaitDate, ...]:
        return tuple(f for m in self.masques for f in m.faits)

    @property
    def peres(self) -> Tuple[NomPersonne, ...]:
        return tuple(dict.fromkeys(m.pere for m in self.masques if m.pere))

    @property
    def meres(self) -> Tuple[NomPersonne, ...]:
        return tuple(dict.fromkeys(m.mere for m in self.masques if m.mere))

    @property
    def conjoints(self) -> Tuple[NomPersonne, ...]:
        return tuple(dict.fromkeys(c for m in self.masques for c in m.conjoints))
