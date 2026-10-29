"""Différentiel de deux lots d'un même corpus (modèle 5.8, étape 6, décision 16).

Fonction pure : aucun lot n'est modifié, une rétraction n'est qu'un écart (R10).
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple, Union

from chronologia.modele.entites import (
    Conclusion,
    Factoide,
    Masque,
    MentionLieu,
    Participation,
    Qualite,
    Relation,
)

from .mapper import LotImport

Entite = Union[Masque, Factoide, Conclusion]


@dataclass(frozen=True)
class Ecart:
    genre: str  # personne | factoide | conclusion
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


class _Index:
    """Regroupements d'un lot par factoïde, calculés une fois (évite un balayage par fait)."""

    def __init__(self, lot: LotImport) -> None:
        self.cles = {m.ref: m.cle_externe for m in lot.masques}
        self.passages = {p.ref: p for p in lot.passages}
        self.participations: Dict[str, List[Participation]] = defaultdict(list)
        self.relations: Dict[str, List[Relation]] = defaultdict(list)
        self.qualites: Dict[str, List[Qualite]] = defaultdict(list)
        self.lieux: Dict[str, List[MentionLieu]] = defaultdict(list)
        for p in lot.participations:
            self.participations[p.factoide_ref].append(p)
        for r in lot.relations:
            self.relations[r.factoide_ref].append(r)
        for q in lot.qualites:
            self.qualites[q.factoide_ref].append(q)
        for m in lot.mentions_lieu:
            self.lieux[m.factoide_ref].append(m)


def _principal(ix: _Index, f: Factoide) -> str:
    parts = sorted(ix.participations[f.ref], key=lambda p: p.ordre)
    if parts:
        return ix.cles[parts[0].masque_ref]
    if ix.relations[f.ref]:
        r = ix.relations[f.ref][0]
        return f"{ix.cles[r.sujet_masque_ref]}|{r.type_relation}"
    if ix.qualites[f.ref]:
        q = ix.qualites[f.ref][0]
        return f"{ix.cles[q.masque_ref]}|{q.categorie}|{q.role}"
    return ""


def _factoides_par_cle(lot: LotImport, ix: _Index) -> Dict[str, Factoide]:
    rangs: Dict[str, int] = defaultdict(int)
    res: Dict[str, Factoide] = {}
    for f in lot.factoides:
        base = f"{f.type_evenement or ''}|{f.cle_famille or ''}|{_principal(ix, f)}"
        rangs[base] += 1
        res[f"{base}|{rangs[base]}"] = f
    return res


def _contenu(ix: _Index, f: Factoide) -> _Contenu:
    cles = ix.cles
    passage = ix.passages[f.passage_ref]
    return {
        "date": (f.date_brute, f.date_min, f.date_max, f.calendrier, f.date_incertaine),
        "lieu": frozenset((m.fonction, m.forme_ecrite) for m in ix.lieux[f.ref]),
        "participants": frozenset((cles[p.masque_ref], p.role) for p in ix.participations[f.ref]),
        "relations": frozenset(
            (r.type_relation, r.orientation, cles[r.sujet_masque_ref], cles[r.objet_masque_ref])
            for r in ix.relations[f.ref]
        ),
        "qualites": frozenset(
            (cles[q.masque_ref], q.categorie, q.role, q.valide_debut, q.valide_fin, q.rang)
            for q in ix.qualites[f.ref]
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


def _conclusions_par_cible(lot: LotImport) -> Dict[str, List[Conclusion]]:
    cles = {m.ref: m.cle_externe for m in lot.masques}
    res: Dict[str, List[Conclusion]] = defaultdict(list)
    for c in lot.conclusions:
        res[cles[c.cible_masque_ref]].append(c)
    return res


def _comparer_conclusions(
    ancien: LotImport,
    nouveau: LotImport,
    ajouts: List[Ecart],
    invariants: List[Ecart],
    modifications: List[Ecart],
    retractions: List[Ecart],
) -> None:
    """Notes d'une même cible : textes identiques d'abord, puis appariement par ordre."""
    ca, cn = _conclusions_par_cible(ancien), _conclusions_par_cible(nouveau)
    for cible in sorted(ca.keys() | cn.keys()):
        restes_a = list(ca.get(cible, []))
        restes_n = list(cn.get(cible, []))
        rang = 0
        for c in list(restes_a):
            ident = next((n for n in restes_n if n.argument == c.argument), None)
            if ident is not None:
                rang += 1
                restes_a.remove(c)
                restes_n.remove(ident)
                invariants.append(Ecart("conclusion", f"{cible}|{rang}", c, ident))
        for k in range(max(len(restes_a), len(restes_n))):
            rang += 1
            cle = f"{cible}|{rang}"
            a = restes_a[k] if k < len(restes_a) else None
            n = restes_n[k] if k < len(restes_n) else None
            if a is None:
                ajouts.append(Ecart("conclusion", cle, None, n))
            elif n is None:
                retractions.append(Ecart("conclusion", cle, a, None))
            else:
                modifications.append(Ecart("conclusion", cle, a, n, ("argument",)))


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

    ia, inn = _Index(ancien), _Index(nouveau)
    ga, gn = _factoides_par_cle(ancien, ia), _factoides_par_cle(nouveau, inn)
    for cle in sorted(ga.keys() | gn.keys()):
        if cle not in ga:
            ajouts.append(Ecart("factoide", cle, None, gn[cle]))
        elif cle not in gn:
            retractions.append(Ecart("factoide", cle, ga[cle], None))
        else:
            ca, cn = _contenu(ia, ga[cle]), _contenu(inn, gn[cle])
            champs = tuple(k for k in ca if ca[k] != cn[k])
            cible = invariants if not champs else modifications
            cible.append(Ecart("factoide", cle, ga[cle], gn[cle], champs))

    _comparer_conclusions(ancien, nouveau, ajouts, invariants, modifications, retractions)
    return DiffLots(tuple(ajouts), tuple(invariants), tuple(modifications), tuple(retractions))
