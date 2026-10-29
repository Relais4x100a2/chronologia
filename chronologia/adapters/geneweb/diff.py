"""Différentiel de deux lots d'un même corpus (modèle 5.8, étape 6, décision 16).

Fonction pure : aucun lot n'est modifié, une rétraction n'est qu'un écart (R10).
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple, Union

from chronologia.modele.entites import Factoide, Masque

from .mapper import LotImport

Entite = Union[Masque, Factoide]


@dataclass(frozen=True)
class Ecart:
    genre: str  # personne | factoide
    cle: str
    ancien: Optional[Entite]
    nouveau: Optional[Entite]
    champs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DiffLots:
    ajouts: Tuple[Ecart, ...]
    invariants: Tuple[Ecart, ...]
    modifications: Tuple[Ecart, ...]
    retractions: Tuple[Ecart, ...]


_Contenu = Dict[str, object]


def _cles_masques(lot: LotImport) -> Dict[str, str]:
    return {m.ref: m.cle_externe for m in lot.masques}


def _principal(lot: LotImport, f: Factoide, cles: Dict[str, str]) -> str:
    parts = sorted(
        (p for p in lot.participations if p.factoide_ref == f.ref), key=lambda p: p.ordre
    )
    if parts:
        return cles[parts[0].masque_ref]
    rels = [r for r in lot.relations if r.factoide_ref == f.ref]
    if rels:
        r = rels[0]
        return f"{cles[r.sujet_masque_ref]}|{r.type_relation}"
    quals = [q for q in lot.qualites if q.factoide_ref == f.ref]
    if quals:
        q = quals[0]
        return f"{cles[q.masque_ref]}|{q.categorie}|{q.role}"
    return ""


def _factoides_par_cle(lot: LotImport) -> Dict[str, Factoide]:
    cles = _cles_masques(lot)
    rangs: Dict[str, int] = defaultdict(int)
    res: Dict[str, Factoide] = {}
    for f in lot.factoides:
        base = f"{f.type_evenement or ''}|{f.cle_famille or ''}|{_principal(lot, f, cles)}"
        rangs[base] += 1
        res[f"{base}|{rangs[base]}"] = f
    return res


def _contenu(lot: LotImport, f: Factoide) -> _Contenu:
    cles = _cles_masques(lot)
    passage = next(p for p in lot.passages if p.ref == f.passage_ref)
    return {
        "date": (f.date_brute, f.date_min, f.date_max, f.calendrier, f.date_incertaine),
        "lieu": frozenset(
            (m.fonction, m.forme_ecrite) for m in lot.mentions_lieu if m.factoide_ref == f.ref
        ),
        "participants": frozenset(
            (cles[p.masque_ref], p.role) for p in lot.participations if p.factoide_ref == f.ref
        ),
        "relations": frozenset(
            (r.type_relation, r.orientation, cles[r.sujet_masque_ref], cles[r.objet_masque_ref])
            for r in lot.relations
            if r.factoide_ref == f.ref
        ),
        "qualites": frozenset(
            (cles[q.masque_ref], q.categorie, q.role, q.valide_debut, q.valide_fin, q.rang)
            for q in lot.qualites
            if q.factoide_ref == f.ref
        ),
        "source": (passage.citation_brute, passage.transcription),
    }


def _formes_masques(lot: LotImport) -> Dict[str, FrozenSet[Tuple[str, Optional[str]]]]:
    res: Dict[str, set] = defaultdict(set)  # type: ignore[type-arg]
    for m in lot.masques:
        res[m.cle_externe].add((m.nom_ecrit, m.sexe))
    return {k: frozenset(v) for k, v in res.items()}


def _premier_masque(lot: LotImport) -> Dict[str, Masque]:
    res: Dict[str, Masque] = {}
    for m in lot.masques:
        res.setdefault(m.cle_externe, m)
    return res


def comparer_lots(ancien: LotImport, nouveau: LotImport) -> DiffLots:
    ajouts: List[Ecart] = []
    invariants: List[Ecart] = []
    modifications: List[Ecart] = []
    retractions: List[Ecart] = []

    fa, fn = _formes_masques(ancien), _formes_masques(nouveau)
    ma, mn = _premier_masque(ancien), _premier_masque(nouveau)
    for cle in sorted(fa.keys() | fn.keys()):
        if cle not in fa:
            ajouts.append(Ecart("personne", cle, None, mn[cle]))
        elif cle not in fn:
            retractions.append(Ecart("personne", cle, ma[cle], None))
        elif fa[cle] == fn[cle]:
            invariants.append(Ecart("personne", cle, ma[cle], mn[cle]))
        else:
            modifications.append(Ecart("personne", cle, ma[cle], mn[cle], ("nom",)))

    ga, gn = _factoides_par_cle(ancien), _factoides_par_cle(nouveau)
    for cle in sorted(ga.keys() | gn.keys()):
        if cle not in ga:
            ajouts.append(Ecart("factoide", cle, None, gn[cle]))
        elif cle not in gn:
            retractions.append(Ecart("factoide", cle, ga[cle], None))
        else:
            ca, cn = _contenu(ancien, ga[cle]), _contenu(nouveau, gn[cle])
            champs = tuple(k for k in ca if ca[k] != cn[k])
            cible = invariants if not champs else modifications
            cible.append(Ecart("factoide", cle, ga[cle], gn[cle], champs))

    return DiffLots(tuple(ajouts), tuple(invariants), tuple(modifications), tuple(retractions))
