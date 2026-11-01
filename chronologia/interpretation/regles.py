"""Règles d'indices v1 du rapprochement d'homonymes (décision 20).

Chaque règle compare un masque à une personne candidate et rend ses indices
(``interp_indice``, mode calculé), chacun citant la version de sa règle (R13).
Une règle sans matière à comparer ne rend rien ; une comparaison faite sans
incompatibilité rend un indice « neutre » de poids nul, pour rester visible.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterator, List, Optional, Sequence, Tuple

from chronologia.interpretation.normalisation import (
    cle_phonetique,
    normaliser,
    premier_prenom,
)
from chronologia.interpretation.profils import (
    FaitDate,
    MasqueObserve,
    NomPersonne,
    ProfilPersonne,
)

REGLE_ONOMASTIQUE = "regle:onomastique:nom_prenom:v1"
REGLE_CHRONO = "regle:chrono:v1"
REGLE_RESEAU = "regle:reseau:famille:v1"

# Rôles où la personne est vivante ; les autres (mention « fils de feu… ») sont
# ignorés pour ne pas compter de mentions posthumes.
ROLES_VIVANT = frozenset(
    {"ne", "baptise", "epoux", "epouse", "temoin", "parrain", "marraine",
     "parrain_ou_marraine"}
)  # fmt: skip
ROLES_DECES = frozenset({"decede", "inhume"})
TOLERANCE_INHUMATION = timedelta(days=365)
ECART_MAXIMAL = timedelta(days=round(110 * 365.25))


@dataclass(frozen=True)
class Indice:
    type: str
    sens: str
    poids: float
    valeur_masque: str
    valeur_personne: str
    regle_version: str


# --- Onomastique -----------------------------------------------------------


def _forme(n: NomPersonne) -> str:
    return normaliser(f"{n.nom} {n.prenoms}")


def _variante(a: NomPersonne, b: NomPersonne) -> bool:
    """Même nom phonétique, et prénoms phonétiquement égaux ou même premier prénom."""
    if cle_phonetique(a.nom) != cle_phonetique(b.nom):
        return False
    premier = premier_prenom(a.prenoms)
    return cle_phonetique(a.prenoms) == cle_phonetique(b.prenoms) or (
        premier != "" and premier == premier_prenom(b.prenoms)
    )


def regle_onomastique(masque: MasqueObserve, profil: ProfilPersonne) -> List[Indice]:
    forme = _forme(masque.nom)
    noms = profil.noms
    for n in noms:
        if _forme(n) == forme:
            return [Indice("onomastique", "pour", 1.0, forme, forme, REGLE_ONOMASTIQUE)]
    for n in noms:
        if _variante(masque.nom, n):
            return [
                Indice("onomastique", "pour", 0.5, forme, _forme(n), REGLE_ONOMASTIQUE)
            ]
    return []


# --- Chronologie -----------------------------------------------------------


@dataclass(frozen=True)
class _Vie:
    """Faits datés comparables d'un côté, et ses bornes de vie."""

    faits: Tuple[FaitDate, ...]
    naissance: Optional[FaitDate]
    deces: Optional[FaitDate]
    mort: Optional[FaitDate]  # décès, à défaut inhumation


def _debut(f: FaitDate) -> date:
    assert f.debut is not None
    return f.debut


def _fin(f: FaitDate) -> date:
    assert f.fin is not None
    return f.fin


def _vie(faits: Sequence[FaitDate]) -> _Vie:
    utiles = tuple(
        f
        for f in faits
        if f.datee and (f.role in ROLES_VIVANT or f.role in ROLES_DECES)
    )

    def premier(role: str) -> Optional[FaitDate]:
        return min((f for f in utiles if f.role == role), key=_debut, default=None)

    def dernier(role: str) -> Optional[FaitDate]:
        return max((f for f in utiles if f.role == role), key=_fin, default=None)

    deces = dernier("decede")
    return _Vie(
        utiles,
        premier("ne") or premier("baptise"),
        deces,
        deces or dernier("inhume"),
    )


def _annees(f: FaitDate) -> str:
    a, b = _debut(f).year, _fin(f).year
    return f"{f.role} {a}" if a == b else f"{f.role} {a}-{b}"


def _conflits(x: _Vie, y: _Vie) -> Iterator[Tuple[str, FaitDate, FaitDate]]:
    """Incompatibilités des faits de ``x`` avec les bornes de vie de ``y``."""
    for f in x.faits:
        if y.naissance and _fin(f) < _debut(y.naissance):
            yield "avant_naissance", f, y.naissance
        if f.role in ROLES_VIVANT and y.mort and _debut(f) > _fin(y.mort):
            yield "apres_deces", f, y.mort
        if (
            f.role == "inhume"
            and y.deces
            and (_debut(f) > _fin(y.deces) + TOLERANCE_INHUMATION)
        ):
            yield "inhumation_tardive", f, y.deces
        for g in y.faits:
            if _debut(f) - _fin(g) > ECART_MAXIMAL:
                yield "ecart", f, g


def regle_chrono(masque: MasqueObserve, profil: ProfilPersonne) -> List[Indice]:
    m, p = _vie(masque.faits), _vie(profil.faits)
    if not m.faits or not p.faits:
        return []
    indices: dict[str, Indice] = {}
    for genre, f, g in _conflits(m, p):
        indices.setdefault(
            genre,
            Indice("chronologie", "contre", 2.0, _annees(f), _annees(g), REGLE_CHRONO),
        )
    for genre, g, f in _conflits(p, m):
        indices.setdefault(
            genre,
            Indice("chronologie", "contre", 2.0, _annees(f), _annees(g), REGLE_CHRONO),
        )
    if indices:
        return list(indices.values())
    return [
        Indice(
            "chronologie", "neutre", 0.0,
            ", ".join(_annees(f) for f in m.faits),
            ", ".join(_annees(f) for f in p.faits),
            REGLE_CHRONO,
        )
    ]  # fmt: skip


# --- Réseau familial -------------------------------------------------------


def _egaux(a: NomPersonne, b: NomPersonne) -> bool:
    return _forme(a) == _forme(b)


def _differents(a: NomPersonne, b: NomPersonne) -> bool:
    """Formellement différents : pas même une variante phonétique."""
    return cle_phonetique(_forme(a)) != cle_phonetique(_forme(b))


def _parents(m: MasqueObserve) -> str:
    return " / ".join(_forme(n) for n in (m.pere, m.mere) if n)


def _parents_profil(p: ProfilPersonne) -> str:
    return " / ".join(
        ", ".join(_forme(n) for n in noms) for noms in (p.peres, p.meres) if noms
    )


def regle_reseau(masque: MasqueObserve, profil: ProfilPersonne) -> List[Indice]:
    indices: List[Indice] = []
    cotes = [(masque.pere, profil.peres), (masque.mere, profil.meres)]
    if all(n and connus and any(_egaux(n, c) for c in connus) for n, connus in cotes):
        indices.append(
            Indice("filiation", "pour", 2.0, _parents(masque), _parents_profil(profil),
                   REGLE_RESEAU)
        )  # fmt: skip
    elif any(
        n and connus and all(_differents(n, c) for c in connus) for n, connus in cotes
    ):
        indices.append(
            Indice("filiation", "contre", 1.5, _parents(masque), _parents_profil(profil),
                   REGLE_RESEAU)
        )  # fmt: skip
    for c in masque.conjoints:
        commun = next((d for d in profil.conjoints if _egaux(c, d)), None)
        if commun is not None:
            indices.append(
                Indice("conjoint", "pour", 1.5, _forme(c), _forme(commun), REGLE_RESEAU)
            )
            break
    return indices
