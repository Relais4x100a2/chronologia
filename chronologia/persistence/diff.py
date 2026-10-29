"""Application d'un différentiel de lots : rétractions par audit, jamais de DELETE (R10)."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from chronologia.adapters.geneweb.diff import DiffLots, Ecart

_TABLES = {"factoide": "source_factoide", "conclusion": "interp_conclusion"}


@dataclass(frozen=True)
class BilanApplicationDiff:
    """Rétractions nouvellement écrites, par motif (0 partout si déjà appliqué)."""

    retractions: int = 0  # fait disparu du lot nouveau
    modifications: int = 0  # ancienne version remplacée par la nouvelle
    reconductions: int = 0  # fait identique : le lot nouveau le porte désormais


def _retracter(
    con: sqlite3.Connection,
    ecart: Ecart,
    lot_ancien_id: int,
    lot_nouveau_id: int,
    motif: str,
    maintenant: str,
) -> bool:
    """Retire l'ancienne occurrence ; faux si elle l'était déjà."""
    table = _TABLES[ecart.genre]
    assert ecart.ancien is not None
    ligne = con.execute(
        f"SELECT id FROM {table} WHERE lot_id=? AND ref=?",
        (lot_ancien_id, ecart.ancien.ref),
    ).fetchone()
    if ligne is None:
        raise KeyError(f"{table}: {ecart.ancien.ref} absent du lot {lot_ancien_id}")
    cur = con.execute(
        "INSERT INTO audit_retractation (cible_table, cible_id, lot_id, motif,"
        " date_retractation) SELECT ?, ?, ?, ?, ? WHERE NOT EXISTS"
        " (SELECT 1 FROM audit_retractation WHERE cible_table=? AND cible_id=?)",
        (table, ligne[0], lot_nouveau_id, motif, maintenant, table, ligne[0]),
    )
    return cur.rowcount == 1


def appliquer_diff(
    con: sqlite3.Connection,
    diff: DiffLots,
    lot_ancien_id: int,
    lot_nouveau_id: int,
    maintenant: Optional[datetime] = None,
) -> BilanApplicationDiff:
    """Retire de la vue active les occurrences du lot ancien que le lot nouveau remplace.

    Les deux lots sont déjà persistés. Sont retirés (``audit_retractation``) :
    les faits disparus (``retractation``), modifiés (``modification``) et
    reconduits à l'identique (``reconduction``, le lot nouveau les porte). Les
    masques ne sont pas retirés : leur identification relève d'un autre chantier.
    Atomique ; rappliquer le même diff n'écrit rien de plus.

    Raises:
        KeyError: un élément ancien du diff n'est pas dans ``lot_ancien_id``.
    """
    horodatage = (maintenant or datetime.now(timezone.utc)).isoformat()
    compteurs = {"retractation": 0, "modification": 0, "reconduction": 0}
    groupes = (
        ("retractation", diff.retractions),
        ("modification", diff.modifications),
        ("reconduction", diff.invariants),
    )
    with con:
        for motif, ecarts in groupes:
            for e in ecarts:
                if e.genre in _TABLES and e.ancien is not None:
                    if _retracter(con, e, lot_ancien_id, lot_nouveau_id, motif, horodatage):
                        compteurs[motif] += 1
    return BilanApplicationDiff(
        compteurs["retractation"], compteurs["modification"], compteurs["reconduction"]
    )
