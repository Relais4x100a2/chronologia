"""Moteur de rapprochement d'homonymes : candidats, barème, propositions (décision 20).

Les personnes sont regroupées par clé de blocage (nom et premier prénom
phonétiques) ; chaque paire est orientée de la personne la plus récente vers la
plus ancienne, et chaque masque de la première est évalué contre la seconde.
Un veto sur l'un des masques élimine la paire entière : les masques d'une même
personne sont réunis par l'auteur de la base (R4), un frère homonyme né après la
mort du premier ne doit pas être proposé par son seul acte de filiation.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import (
    AbstractSet,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from chronologia.interpretation.normalisation import cle_phonetique, premier_prenom
from chronologia.interpretation.profils import MasqueObserve, ProfilPersonne
from chronologia.interpretation.regles import (
    Indice,
    regle_chrono,
    regle_onomastique,
    regle_reseau,
)


@dataclass(frozen=True)
class Bareme:
    veto: float  # un indice « contre » de ce poids élimine le candidat
    possible: float
    probable: float


BAREME_V1 = Bareme(veto=2.0, possible=2.0, probable=3.5)


@dataclass(frozen=True)
class Decision:
    score: float
    degre: Optional[str]  # None : éliminé ou sous le seuil ; jamais « certain »
    veto: bool


@dataclass(frozen=True)
class Evaluation:
    masque_id: int
    personne_id: int
    indices: Tuple[Indice, ...]
    score: float
    degre: Optional[str]
    veto: bool


@dataclass(frozen=True)
class Proposition:
    masque_id: int
    personne_id: int
    degre: str
    score: float
    indices: Tuple[Indice, ...]


@dataclass(frozen=True)
class ResultatRapprochement:
    propositions: Tuple[Proposition, ...]
    paires_examinees: int
    paires_eliminees: int  # veto chronologique ou autre « contre » éliminatoire
    masques_sous_seuil: int
    couples_deja_identifies: int


def decider(indices: Sequence[Indice], bareme: Bareme = BAREME_V1) -> Decision:
    """Score = Σ pour − Σ contre ; veto si un « contre » atteint le seuil."""
    score = sum(i.poids for i in indices if i.sens == "pour") - sum(
        i.poids for i in indices if i.sens == "contre"
    )
    if any(i.sens == "contre" and i.poids >= bareme.veto for i in indices):
        return Decision(score, None, True)
    if score >= bareme.probable:
        return Decision(score, "probable", False)
    if score >= bareme.possible:
        return Decision(score, "possible", False)
    return Decision(score, None, False)


def evaluer_masque(
    masque: MasqueObserve, profil: ProfilPersonne, bareme: Bareme = BAREME_V1
) -> Evaluation:
    indices = (
        regle_onomastique(masque, profil)
        + regle_chrono(masque, profil)
        + regle_reseau(masque, profil)
    )
    d = decider(indices, bareme)
    return Evaluation(
        masque.masque_id, profil.personne_id, tuple(indices), d.score, d.degre, d.veto
    )


def cles_blocage(profil: ProfilPersonne) -> Set[Tuple[str, str]]:
    return {
        (cle_phonetique(n.nom), cle_phonetique(premier_prenom(n.prenoms)))
        for n in profil.noms
    }


def paires_candidates(
    profils: Iterable[ProfilPersonne], intra_base: bool = False
) -> List[Tuple[ProfilPersonne, ProfilPersonne]]:
    """Paires (plus récente, plus ancienne) partageant une clé de blocage."""
    groupes: Dict[Tuple[str, str], List[ProfilPersonne]] = defaultdict(list)
    for p in profils:
        for cle in cles_blocage(p):
            groupes[cle].append(p)
    vues: Set[Tuple[int, int]] = set()
    paires: List[Tuple[ProfilPersonne, ProfilPersonne]] = []
    for groupe in groupes.values():
        groupe.sort(key=lambda p: p.personne_id)
        for i, ancien in enumerate(groupe):
            for recent in groupe[i + 1 :]:
                couple = (recent.personne_id, ancien.personne_id)
                if couple in vues or recent.personne_id == ancien.personne_id:
                    continue
                if not intra_base and recent.base == ancien.base:
                    continue
                vues.add(couple)
                paires.append((recent, ancien))
    return sorted(paires, key=lambda p: (p[0].personne_id, p[1].personne_id))


def rapprocher(
    profils: Iterable[ProfilPersonne],
    deja_identifies: AbstractSet[Tuple[int, int]] = frozenset(),
    intra_base: bool = False,
    bareme: Bareme = BAREME_V1,
) -> ResultatRapprochement:
    """Propositions pour chaque masque, hors couples (masque, personne) déjà identifiés."""
    propositions: List[Proposition] = []
    paires = paires_candidates(profils, intra_base)
    eliminees = sous_seuil = deja = 0
    for recent, ancien in paires:
        evaluations = [evaluer_masque(m, ancien, bareme) for m in recent.masques]
        if any(e.veto for e in evaluations):
            eliminees += 1
            continue
        for e in evaluations:
            if (e.masque_id, e.personne_id) in deja_identifies:
                deja += 1
            elif e.degre is None:
                sous_seuil += 1
            else:
                propositions.append(
                    Proposition(e.masque_id, e.personne_id, e.degre, e.score, e.indices)
                )
    return ResultatRapprochement(
        tuple(propositions), len(paires), eliminees, sous_seuil, deja
    )
