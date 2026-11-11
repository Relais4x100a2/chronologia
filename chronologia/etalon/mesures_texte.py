"""Mesures sur le texte (CER, WER) contre l'étalon : micro-moyennes, sans redressement.

Normalisation minimale (NFC et repli des espaces) : la casse, la ponctuation et les
abréviations comptent comme écrites (R13). Le résultat ne contient que des comptes.
"""

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

import jiwer
from jiwer import transforms

from chronologia.etalon.tirage import tranche_de

_CARACTERES = transforms.Compose([transforms.ReduceToListOfListOfChars()])
_MOTS = transforms.Compose([transforms.ReduceToListOfListOfWords()])
_ESPACES = re.compile(r"\s+")


def normaliser_espaces(s: str) -> str:
    return _ESPACES.sub(" ", unicodedata.normalize("NFC", s)).strip()


@dataclass(frozen=True)
class PaireTexte:
    commune: str
    source: str
    type: str
    annee: int
    reference: str
    hypothese: str
    illisible: bool


@dataclass(frozen=True)
class LigneMesureTexte:
    commune: str
    source: str
    type: str
    tranche: str
    n_unites: int
    editions_car: int
    longueur_car: int
    editions_mots: int
    longueur_mots: int
    cer: float | None
    wer: float | None
    references_vides: int
    illisibles: int


@dataclass
class _Cumul:
    n_unites: int = 0
    editions_car: int = 0
    longueur_car: int = 0
    editions_mots: int = 0
    longueur_mots: int = 0
    references_vides: int = 0
    illisibles: int = 0


def _ajouter(c: _Cumul, p: PaireTexte) -> None:
    c.n_unites += 1
    if p.illisible:
        c.illisibles += 1
        return
    ref, hyp = normaliser_espaces(p.reference), normaliser_espaces(p.hypothese)
    if not ref:
        c.references_vides += 1
        return
    car = jiwer.process_characters(ref, hyp, reference_transform=_CARACTERES, hypothesis_transform=_CARACTERES)
    mots = jiwer.process_words(ref, hyp, reference_transform=_MOTS, hypothesis_transform=_MOTS)
    c.editions_car += car.substitutions + car.deletions + car.insertions
    c.longueur_car += car.substitutions + car.deletions + car.hits
    c.editions_mots += mots.substitutions + mots.deletions + mots.insertions
    c.longueur_mots += mots.substitutions + mots.deletions + mots.hits


def _taux(editions: int, longueur: int) -> float | None:
    return editions / longueur if longueur else None


def mesurer_textes(
    paires: Sequence[PaireTexte], periode: tuple[int, int], largeur: int
) -> list[LigneMesureTexte]:
    """Une ligne par (commune, source, type, tranche), plus une ligne « * » par (commune, source)."""
    cumuls: dict[tuple[str, str, str, str], _Cumul] = {}
    for p in paires:
        tranche = tranche_de(p.annee, periode, largeur)
        for cle in ((p.commune, p.source, p.type, tranche), (p.commune, p.source, "*", "*")):
            _ajouter(cumuls.setdefault(cle, _Cumul()), p)
    return [
        LigneMesureTexte(
            commune=commune,
            source=source,
            type=type_,
            tranche=tranche,
            n_unites=c.n_unites,
            editions_car=c.editions_car,
            longueur_car=c.longueur_car,
            editions_mots=c.editions_mots,
            longueur_mots=c.longueur_mots,
            cer=_taux(c.editions_car, c.longueur_car),
            wer=_taux(c.editions_mots, c.longueur_mots),
            references_vides=c.references_vides,
            illisibles=c.illisibles,
        )
        for (commune, source, type_, tranche), c in sorted(cumuls.items())
    ]
