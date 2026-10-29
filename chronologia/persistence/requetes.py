"""Consultation de la base : factoïdes actifs (non rétractés) seulement."""

import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class FactoideTrouve:
    id: int
    lot_id: int
    ref: str
    type_evenement: Optional[str]
    date_declaree: Optional[str]


_COLONNES = "f.id, f.lot_id, f.ref, f.type_evenement, f.date_declaree"


def _lire(con: sqlite3.Connection, sql: str, params: tuple) -> List[FactoideTrouve]:  # type: ignore[type-arg]
    return [FactoideTrouve(*r) for r in con.execute(sql, params)]


def rechercher_par_personne(
    con: sqlite3.Connection, cle_externe: str
) -> List[FactoideTrouve]:
    """Factoïdes où un masque de cette clé externe participe."""
    return _lire(
        con,
        f"SELECT DISTINCT {_COLONNES} FROM source_factoide_actif f"
        " JOIN source_participation p ON p.factoide_id = f.id"
        " JOIN source_masque m ON m.id = p.masque_id"
        " WHERE m.cle_externe = ? ORDER BY f.date_min, f.id",
        (cle_externe,),
    )


def rechercher_par_intervalle(
    con: sqlite3.Connection, debut: date, fin: date
) -> List[FactoideTrouve]:
    """Factoïdes dont les bornes chevauchent ``[debut, fin]`` ; borne absente = ouverte.

    Un factoïde sans aucune borne n'est jamais retourné.
    """
    return _lire(
        con,
        f"SELECT {_COLONNES} FROM source_factoide_actif f"
        " WHERE (f.date_min IS NOT NULL OR f.date_max IS NOT NULL)"
        " AND (f.date_min IS NULL OR f.date_min <= ?)"
        " AND (f.date_max IS NULL OR f.date_max >= ?)"
        " ORDER BY f.date_min, f.id",
        (fin.isoformat(), debut.isoformat()),
    )


def rechercher_par_lieu(con: sqlite3.Connection, forme: str) -> List[FactoideTrouve]:
    """Factoïdes mentionnant ce lieu (forme normalisée ou écrite)."""
    return _lire(
        con,
        f"SELECT DISTINCT {_COLONNES} FROM source_factoide_actif f"
        " JOIN source_mention_lieu l ON l.factoide_id = f.id"
        " WHERE l.forme_normalisee = ? OR l.forme_ecrite = ?"
        " ORDER BY f.date_min, f.id",
        (forme, forme),
    )
