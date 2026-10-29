"""Schéma SQLite de la persistance : tables préfixées par couche, index de recherche."""

import sqlite3

import pytest

from chronologia.persistence.schema import creer_schema

TABLES = {
    "source_lot_import", "source_passage", "source_masque", "source_factoide",
    "source_participation", "source_relation", "source_qualite",
    "source_mention_lieu", "interp_evenement", "interp_ident_evenement",
    "interp_conclusion", "audit_retractation",
}  # fmt: skip


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    return c


def _noms(con, type_):
    rows = con.execute("SELECT name FROM sqlite_master WHERE type=?", (type_,))
    return {r[0] for r in rows}


def test_toutes_les_tables_sont_creees(con):
    assert TABLES <= _noms(con, "table")


def test_creer_schema_est_idempotent(con):
    creer_schema(con)
    assert TABLES <= _noms(con, "table")


@pytest.mark.parametrize(
    "table,colonne",
    [
        ("source_masque", "cle_externe"),
        ("source_passage", "cle_externe"),
        ("source_factoide", "cle_famille"),
        ("source_factoide", "date_min"),
        ("source_participation", "masque_id"),
        ("source_lot_import", "empreinte"),
    ],
)
def test_colonne_de_recherche_est_indexee(con, table, colonne):
    colonnes = set()
    for _, nom, *_ in con.execute(f"PRAGMA index_list({table})"):
        colonnes |= {r[2] for r in con.execute(f"PRAGMA index_info({nom})")}
    assert colonne in colonnes


def _lot(con):
    con.execute(
        "INSERT INTO source_lot_import (format, outil, version, date_import, statut,"
        " nb_entites) VALUES ('geneweb', 'test', '1', '2026-10-30', 'ok', 0)"
    )
    con.execute("INSERT INTO source_passage (lot_id, ref) VALUES (1, 'S1')")
    con.execute(
        "INSERT INTO source_factoide (lot_id, ref, passage_id, type_evenement)"
        " VALUES (1, 'F1', 1, 'naissance')"
    )
    for sql in (
        "INSERT INTO source_masque (lot_id, ref, passage_id, nom_ecrit, cle_externe)"
        " VALUES (1, 'M1', 1, 'X', 'k1')",
        "INSERT INTO source_participation VALUES (1, 1, 'sujet', 0, NULL)",
        "INSERT INTO source_relation (factoide_id, sujet_masque_id, objet_masque_id,"
        " type_relation) VALUES (1, 1, 1, 'parent')",
        "INSERT INTO source_qualite (lot_id, ref, factoide_id, masque_id, categorie,"
        " role) VALUES (1, 'Q1', 1, 1, 'profession', 'tisserand')",
        "INSERT INTO source_mention_lieu (lot_id, ref, factoide_id, forme_ecrite,"
        " fonction) VALUES (1, 'L1', 1, 'Rouen', 'evenement')",
        "INSERT INTO interp_evenement (lot_id, ref) VALUES (1, 'E1')",
        "INSERT INTO interp_ident_evenement (factoide_id, evenement_id, degre, statut)"
        " VALUES (1, 1, 'certain', 'actif')",
        "INSERT INTO interp_conclusion (lot_id, ref, cible_masque_id, argument)"
        " VALUES (1, 'C1', 1, 'note')",
        "INSERT INTO audit_retractation (cible_table, cible_id, lot_id,"
        " date_retractation) VALUES ('source_factoide', 1, 1, '2026-10-30')",
    ):
        con.execute(sql)


@pytest.mark.parametrize("table", sorted(TABLES))
def test_r10_update_refuse(con, table):
    _lot(con)
    with pytest.raises(sqlite3.DatabaseError, match="R10"):
        col = _colonne(con, table)
        con.execute(f"UPDATE {table} SET {col} = {col}")


@pytest.mark.parametrize("table", sorted(TABLES))
def test_r10_delete_refuse(con, table):
    _lot(con)
    with pytest.raises(sqlite3.DatabaseError, match="R10"):
        con.execute(f"DELETE FROM {table}")


def _colonne(con, table):
    return next(r[1] for r in con.execute(f"PRAGMA table_info({table})"))
