"""Identifications initiales d'un lot GeneWeb (décision 19, R9, R11, R24, R25).

Une personne par clé GeneWeb (``interp_personne.ref``), propre à la lignée du
fichier : une même clé dans deux bases distinctes ne désigne pas la même personne.
Chaque masque du lot est rattaché à la personne de sa clé par une identification
« certain » du contributeur ``import_geneweb``, versée « actif ». Au réimport, la
personne est réutilisée et les identifications du lot précédent sont retirées
(``audit_retractation``) ; si la dernière décision humaine sur la clé contredit
le rattachement, les nouvelles identifications sont seulement « proposées » (R24).

Toutes les écritures sont ensemblistes et idempotentes ; l'appelant gère la
transaction.
"""

import json
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

CONTRIBUTEUR_IMPORT = "import_geneweb"

# Personne de la clé du masque m dans la lignée (:lignee, liste JSON d'ids de lots).
_PERSONNE_DE_M = (
    "(SELECT MIN(p.id) FROM interp_personne p WHERE p.ref = m.cle_externe"
    " AND p.lot_id IN (SELECT value FROM json_each(:lignee)))"
)

_NON_RETRACTEE = (
    "NOT EXISTS (SELECT 1 FROM audit_retractation r"
    " WHERE r.cible_table = 'interp_ident_personne' AND r.cible_id = i.id)"
)


@dataclass(frozen=True)
class BilanIdentificationImport:
    personnes_creees: int
    personnes_reutilisees: int
    identifications_actives: int
    identifications_proposees: int


def contributeur_import(con: sqlite3.Connection) -> int:
    """Identifiant du contributeur canonique de l'import GeneWeb, créé au besoin."""
    con.execute(
        "INSERT INTO interp_contributeur (nom, type) SELECT ?, 'import'"
        " WHERE NOT EXISTS (SELECT 1 FROM interp_contributeur WHERE nom = ?)",
        (CONTRIBUTEUR_IMPORT, CONTRIBUTEUR_IMPORT),
    )
    ligne = con.execute(
        "SELECT id FROM interp_contributeur WHERE nom = ?", (CONTRIBUTEUR_IMPORT,)
    ).fetchone()
    return int(ligne[0])


def _lignee(
    con: sqlite3.Connection, lot_id: int, lot_precedent_id: Optional[int]
) -> List[int]:
    """Lots de la même base : même format et même nom de fichier, plus le précédent."""
    ids = {
        int(r[0])
        for r in con.execute(
            "SELECT l.id FROM source_lot_import l JOIN source_lot_import n"
            " ON n.format = l.format AND n.fichier = l.fichier WHERE n.id = ?",
            (lot_id,),
        )
    }
    ids.add(lot_id)
    if lot_precedent_id is not None:
        ids.add(lot_precedent_id)
    return sorted(ids)


def _cles_divergentes(con: sqlite3.Connection, lot_id: int, lignee: str) -> List[str]:
    """Clés du lot dont la dernière décision humaine contredit le rattachement (R24).

    Contradiction : un rejet visant la personne de la clé, ou une activation
    visant une autre personne, sur un masque de la clé dans la lignée, retiré ou non.
    """
    rows = con.execute(
        "WITH decision AS ("
        "  SELECT m.cle_externe AS cle, i.personne_id, s.statut,"
        "         ROW_NUMBER() OVER (PARTITION BY m.cle_externe"
        "                            ORDER BY s.date DESC, s.id DESC) AS rang"
        "  FROM interp_ident_personne_statut s"
        "  JOIN interp_contributeur c ON c.id = s.contributeur_id AND c.type = 'humain'"
        "  JOIN interp_ident_personne i ON i.id = s.ident_id"
        "  JOIN source_masque m ON m.id = i.masque_id"
        "  WHERE s.statut IN ('actif', 'rejete')"
        "    AND m.lot_id IN (SELECT value FROM json_each(:lignee))"
        "    AND m.cle_externe IN (SELECT cle_externe FROM source_masque WHERE lot_id = :lot)"
        ")"
        " SELECT d.cle FROM decision d"
        " JOIN interp_personne p ON p.ref = d.cle"
        "  AND p.lot_id IN (SELECT value FROM json_each(:lignee))"
        " WHERE d.rang = 1 AND ((d.statut = 'rejete' AND d.personne_id = p.id)"
        "                    OR (d.statut = 'actif' AND d.personne_id <> p.id))",
        {"lot": lot_id, "lignee": lignee},
    )
    return sorted({r[0] for r in rows})


def _retracter_lot_precedent(
    con: sqlite3.Connection, lot_id: int, lot_precedent_id: int, date: str
) -> None:
    """Retire les identifications des masques du lot précédent, motif par clé."""
    con.execute(
        "INSERT INTO audit_retractation (cible_table, cible_id, lot_id, motif,"
        " date_retractation)"
        " SELECT 'interp_ident_personne', i.id, :lot, CASE"
        "   WHEN NOT EXISTS (SELECT 1 FROM source_masque n"
        "                    WHERE n.lot_id = :lot AND n.cle_externe = m.cle_externe)"
        "     THEN 'retractation'"
        "   WHEN EXISTS (SELECT 1 FROM source_masque a"
        "                WHERE a.lot_id = :ancien AND a.cle_externe = m.cle_externe"
        "                  AND NOT EXISTS (SELECT 1 FROM source_masque n"
        "                    WHERE n.lot_id = :lot AND n.cle_externe = a.cle_externe"
        "                      AND n.nom_ecrit = a.nom_ecrit AND n.sexe IS a.sexe))"
        "     OR EXISTS (SELECT 1 FROM source_masque n"
        "                WHERE n.lot_id = :lot AND n.cle_externe = m.cle_externe"
        "                  AND NOT EXISTS (SELECT 1 FROM source_masque a"
        "                    WHERE a.lot_id = :ancien AND a.cle_externe = n.cle_externe"
        "                      AND a.nom_ecrit = n.nom_ecrit AND a.sexe IS n.sexe))"
        "     THEN 'modification'"
        "   ELSE 'reconduction' END, :date"
        " FROM interp_ident_personne i JOIN source_masque m ON m.id = i.masque_id"
        f" WHERE m.lot_id = :ancien AND {_NON_RETRACTEE}",
        {"lot": lot_id, "ancien": lot_precedent_id, "date": date},
    )


def ecrire_identifications_import(
    con: sqlite3.Connection, lot_id: int, lot_precedent_id: Optional[int] = None
) -> BilanIdentificationImport:
    """Crée personnes et identifications du lot ; retire celles du lot précédent."""
    date = con.execute(
        "SELECT date_import FROM source_lot_import WHERE id = ?", (lot_id,)
    ).fetchone()[0]
    contributeur = contributeur_import(con)
    lignee = json.dumps(_lignee(con, lot_id, lot_precedent_id))
    p = {"lot": lot_id, "lignee": lignee, "contributeur": contributeur, "date": date}

    personnes_creees = con.execute(
        "INSERT INTO interp_personne (lot_id, ref)"
        " SELECT DISTINCT :lot, m.cle_externe FROM source_masque m"
        f" WHERE m.lot_id = :lot AND {_PERSONNE_DE_M} IS NULL",
        p,
    ).rowcount
    nb_cles = con.execute(
        "SELECT COUNT(DISTINCT cle_externe) FROM source_masque WHERE lot_id = ?",
        (lot_id,),
    ).fetchone()[0]

    con.execute(
        "INSERT INTO interp_ident_personne"
        " (masque_id, personne_id, degre, contributeur_id, lot_id, date)"
        f" SELECT m.id, {_PERSONNE_DE_M}, 'certain', :contributeur, :lot, :date"
        " FROM source_masque m WHERE m.lot_id = :lot AND NOT EXISTS ("
        "  SELECT 1 FROM interp_ident_personne i"
        "  WHERE i.masque_id = m.id AND i.contributeur_id = :contributeur)",
        p,
    )
    # Retirer avant d'activer : R11 n'admet qu'une identification active par masque.
    if lot_precedent_id is not None:
        _retracter_lot_precedent(con, lot_id, lot_precedent_id, date)

    divergentes = json.dumps(_cles_divergentes(con, lot_id, lignee))
    nb = {}
    for statut, test in (("actif", "NOT IN"), ("propose", "IN")):
        nb[statut] = con.execute(
            "INSERT INTO interp_ident_personne_statut"
            " (ident_id, statut, contributeur_id, date)"
            " SELECT i.id, :statut, :contributeur, :date"
            " FROM interp_ident_personne i JOIN source_masque m ON m.id = i.masque_id"
            " WHERE i.lot_id = :lot AND i.contributeur_id = :contributeur"
            f"  AND m.cle_externe {test} (SELECT value FROM json_each(:divergentes))"
            "  AND NOT EXISTS (SELECT 1 FROM interp_ident_personne_statut s"
            "                  WHERE s.ident_id = i.id)",
            {**p, "statut": statut, "divergentes": divergentes},
        ).rowcount
    return BilanIdentificationImport(
        personnes_creees, nb_cles - personnes_creees, nb["actif"], nb["propose"]
    )
