"""Lecture des profils comparés par le rapprochement d'homonymes (décision 20, R8).

Un profil réunit les masques activement identifiés à une personne : leurs noms,
les faits datés où ils tiennent un rôle, les parents et conjoints nommés dans
leurs passages. Les personnes fusionnées dans une autre (``same_as_id``) sont
écartées. Quatre requêtes ensemblistes, quel que soit le nombre de personnes.
"""

import sqlite3
from collections import defaultdict
from datetime import date
from typing import DefaultDict, Dict, FrozenSet, List, Optional, Tuple

from chronologia.interpretation.profils import (
    FaitDate,
    MasqueObserve,
    NomPersonne,
    ProfilPersonne,
)

# Masques activement identifiés à une personne non fusionnée, et sa base. La vue
# est matérialisée d'abord : jointe telle quelle, SQLite la reparcourt pour
# chaque personne (coût quadratique).
_ACTIFS = (
    "WITH vue AS MATERIALIZED ("
    " SELECT masque_id, personne_id FROM interp_ident_personne_actif),"
    " actifs AS MATERIALIZED ("
    " SELECT a.masque_id, a.personne_id,"
    " COALESCE(l.format || ':' || l.fichier, 'personne:' || p.id) AS base"
    " FROM vue a"
    " JOIN interp_personne p ON p.id = a.personne_id AND p.same_as_id IS NULL"
    " LEFT JOIN source_lot_import l ON l.id = p.lot_id)"
)

_ROLES_CONJOINT = "('epoux', 'epouse')"


def nom_personne(nom_ecrit: str) -> NomPersonne:
    """« Prénoms NOM » (mots liés par ``_``) : le dernier mot est le nom."""
    prenoms, _, nom = nom_ecrit.strip().rpartition(" ")
    return NomPersonne(nom, prenoms)


def _date(texte: Optional[str]) -> Optional[date]:
    if not texte:
        return None
    try:
        return date.fromisoformat(texte)
    except ValueError:
        return None


def lire_profils(con: sqlite3.Connection) -> List[ProfilPersonne]:
    """Profils des personnes ayant au moins une identification active, triés par id."""
    masques: Dict[int, Tuple[int, str, NomPersonne]] = {}
    for masque_id, personne_id, base, nom_ecrit in con.execute(
        _ACTIFS + " SELECT a.masque_id, a.personne_id, a.base, m.nom_ecrit"
        " FROM actifs a JOIN source_masque m ON m.id = a.masque_id"
    ):
        masques[masque_id] = (personne_id, base, nom_personne(nom_ecrit))

    faits: DefaultDict[int, List[FaitDate]] = defaultdict(list)
    for masque_id, role, debut, fin in con.execute(
        _ACTIFS + " SELECT pa.masque_id, pa.role, f.date_min, f.date_max"
        " FROM actifs a JOIN source_participation pa ON pa.masque_id = a.masque_id"
        " JOIN source_factoide_actif f ON f.id = pa.factoide_id"
        " ORDER BY pa.masque_id, f.id, pa.ordre"
    ):
        faits[masque_id].append(FaitDate(role, _date(debut), _date(fin)))

    parents: Dict[Tuple[int, str], NomPersonne] = {}
    for masque_id, orientation, nom_ecrit in con.execute(
        _ACTIFS + " SELECT r.sujet_masque_id, r.orientation, o.nom_ecrit"
        " FROM actifs a JOIN source_relation r ON r.sujet_masque_id = a.masque_id"
        " JOIN source_factoide_actif f ON f.id = r.factoide_id"
        " JOIN source_masque o ON o.id = r.objet_masque_id"
        " WHERE r.type_relation = 'filiation' ORDER BY r.id"
    ):
        parents.setdefault((masque_id, orientation), nom_personne(nom_ecrit))

    conjoints: DefaultDict[int, List[NomPersonne]] = defaultdict(list)
    for masque_id, nom_ecrit in con.execute(
        _ACTIFS + " SELECT pa.masque_id, o.nom_ecrit"
        " FROM actifs a JOIN source_participation pa ON pa.masque_id = a.masque_id"
        f" AND pa.role IN {_ROLES_CONJOINT}"
        " JOIN source_factoide_actif f ON f.id = pa.factoide_id"
        " JOIN source_participation po ON po.factoide_id = pa.factoide_id"
        f" AND po.role IN {_ROLES_CONJOINT} AND po.masque_id <> pa.masque_id"
        " JOIN source_masque o ON o.id = po.masque_id"
        " ORDER BY pa.masque_id, f.id, po.ordre"
    ):
        conjoints[masque_id].append(nom_personne(nom_ecrit))

    par_personne: DefaultDict[Tuple[int, str], List[MasqueObserve]] = defaultdict(list)
    for masque_id in sorted(masques):
        personne_id, base, nom = masques[masque_id]
        par_personne[(personne_id, base)].append(
            MasqueObserve(
                masque_id,
                nom,
                tuple(faits[masque_id]),
                parents.get((masque_id, "pere")),
                parents.get((masque_id, "mere")),
                tuple(dict.fromkeys(conjoints[masque_id])),
            )
        )
    return [
        ProfilPersonne(personne_id, base, tuple(observes))
        for (personne_id, base), observes in sorted(par_personne.items())
    ]


def couples_identifies(con: sqlite3.Connection) -> FrozenSet[Tuple[int, int]]:
    """Couples (masque, personne) ayant un historique d'identification, quel qu'il soit (R24)."""
    return frozenset(
        (int(m), int(p))
        for m, p in con.execute(
            "SELECT DISTINCT masque_id, personne_id FROM interp_ident_personne"
        )
    )
