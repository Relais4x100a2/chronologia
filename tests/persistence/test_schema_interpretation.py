"""Schéma de l'identification MASQUE → PERSONNE (v0.8, décision 19, R25).

Tables, index, vue active ``interp_ident_personne_actif`` et triggers R10, R11, R18.
"""

import sqlite3

import pytest

from chronologia.persistence.schema import creer_schema

TABLES = {
    "interp_contributeur", "interp_personne", "interp_ident_personne",
    "interp_ident_personne_statut", "interp_indice", "interp_conclusion_effet",
}  # fmt: skip

HUMAIN, AGENT, IMPORT = 1, 2, 3


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON")
    creer_schema(c)
    return c


@pytest.fixture
def base(con):
    """Un lot, deux masques (M1, M2), trois contributeurs, deux personnes."""
    con.execute(
        "INSERT INTO source_lot_import (format, outil, version, date_import, statut,"
        " nb_entites) VALUES ('geneweb', 'test', '1', '2026-10-30', 'actif', 0)"
    )
    con.execute("INSERT INTO source_passage (lot_id, ref) VALUES (1, 'S1')")
    con.execute(
        "INSERT INTO source_factoide (lot_id, ref, passage_id, type_evenement)"
        " VALUES (1, 'F1', 1, 'bapteme')"
    )
    for ref, cle in (("M1", "DUPONT Jean.0"), ("M2", "MARTIN Pierre_Jean.0")):
        con.execute(
            "INSERT INTO source_masque (lot_id, ref, passage_id, nom_ecrit, cle_externe)"
            " VALUES (1, ?, 1, ?, ?)",
            (ref, cle, cle),
        )
    con.executemany(
        "INSERT INTO interp_contributeur (id, nom, type) VALUES (?, ?, ?)",
        [(HUMAIN, "historien", "humain"), (AGENT, "apparieur", "agent"),
         (IMPORT, "import geneweb", "import")],
    )  # fmt: skip
    for ref in ("P1", "P2"):
        con.execute("INSERT INTO interp_personne (lot_id, ref) VALUES (1, ?)", (ref,))
    con.execute(
        "INSERT INTO interp_conclusion (lot_id, ref, cible_masque_id, argument)"
        " VALUES (1, 'C1', NULL, 'même parrain dans les deux actes')"
    )
    return con


def _ident(con, masque_id, personne_id, contributeur_id=HUMAIN):
    cur = con.execute(
        "INSERT INTO interp_ident_personne (masque_id, personne_id, degre,"
        " contributeur_id, lot_id, date) VALUES (?, ?, 'probable', ?, 1, '2026-10-30')",
        (masque_id, personne_id, contributeur_id),
    )
    return cur.lastrowid


def _statut(con, ident_id, statut, contributeur_id=HUMAIN, date="2026-10-30T10:00"):
    con.execute(
        "INSERT INTO interp_ident_personne_statut (ident_id, statut, conclusion_id,"
        " contributeur_id, date) VALUES (?, ?, 1, ?, ?)",
        (ident_id, statut, contributeur_id, date),
    )


def _actifs(con):
    return {r[0] for r in con.execute("SELECT id FROM interp_ident_personne_actif")}


def _noms(con, type_):
    rows = con.execute("SELECT name FROM sqlite_master WHERE type=?", (type_,))
    return {r[0] for r in rows}


# 1. Création du schéma et idempotence


def test_nouvelles_tables_creees(con):
    assert TABLES <= _noms(con, "table")


def test_vue_active_creee(con):
    assert "interp_ident_personne_actif" in _noms(con, "view")


@pytest.mark.parametrize(
    "table,colonne",
    [
        ("interp_ident_personne", "masque_id"),
        ("interp_ident_personne", "personne_id"),
        ("interp_ident_personne_statut", "ident_id"),
        ("interp_indice", "ident_id"),
        ("interp_personne", "cle_externe"),
        ("interp_personne", "ref"),
        ("interp_personne", "same_as_id"),
        ("interp_conclusion_effet", "conclusion_id"),
    ],
)
def test_colonne_indexee(con, table, colonne):
    colonnes = set()
    for _, nom, *_ in con.execute(f"PRAGMA index_list({table})"):
        colonnes |= {r[2] for r in con.execute(f"PRAGMA index_info({nom})")}
    assert colonne in colonnes


def test_second_appel_sans_collision_ni_alteration(base):
    i = _ident(base, 1, 1)
    _statut(base, i, "actif")
    avant = base.execute(
        "SELECT type, name, sql FROM sqlite_master ORDER BY name"
    ).fetchall()
    creer_schema(base)
    apres = base.execute(
        "SELECT type, name, sql FROM sqlite_master ORDER BY name"
    ).fetchall()
    assert apres == avant
    assert _actifs(base) == {i}


def test_conclusion_sans_masque_cible(base):
    """``cible_masque_id`` est facultatif : les effets passent par la table d'effets."""
    base.execute(
        "INSERT INTO interp_conclusion_effet (conclusion_id, type, cible_type, cible_id)"
        " VALUES (1, 'activer_ident', 'interp_ident_personne', 1)"
    )
    assert base.execute("SELECT cible_masque_id FROM interp_conclusion").fetchone() == (
        None,
    )


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO interp_contributeur (nom, type) VALUES ('x', 'robot')",
        "INSERT INTO interp_ident_personne (masque_id, personne_id, degre,"
        " contributeur_id, date) VALUES (1, 1, 'sur', 1, '2026-10-30')",
        "INSERT INTO interp_ident_personne_statut (ident_id, statut, contributeur_id,"
        " date) VALUES (1, 'valide', 1, '2026-10-30')",
        "INSERT INTO interp_indice (ident_id, type, sens, mode)"
        " VALUES (1, 'nom', 'peut-etre', 'calcule')",
        "INSERT INTO interp_indice (ident_id, type, sens, mode)"
        " VALUES (1, 'nom', 'pour', 'devine')",
    ],
)
def test_vocabulaires_fermes(base, sql):
    _ident(base, 1, 1)
    with pytest.raises(sqlite3.IntegrityError):
        base.execute(sql)


def test_nom_de_contributeur_unique(base):
    with pytest.raises(sqlite3.IntegrityError):
        base.execute(
            "INSERT INTO interp_contributeur (nom, type) VALUES ('historien', 'humain')"
        )


def test_ref_de_personne_non_unique(base):
    """Une clé GeneWeb n'est unique que dans sa base : deux bases peuvent la porter."""
    base.execute("INSERT INTO interp_personne (lot_id, ref) VALUES (1, 'P1')")


# 2. R10 : insertion seule sur les nouvelles tables


def _remplir(con):
    i = _ident(con, 1, 1)
    _statut(con, i, "propose")
    con.execute(
        "INSERT INTO interp_personne (lot_id, ref, same_as_id) VALUES (1, 'P3', 1)"
    )
    con.execute(
        "INSERT INTO interp_indice (ident_id, type, sens, poids, valeur_masque,"
        " valeur_personne, mode, regle_version, factoide_id)"
        " VALUES (?, 'nom', 'pour', 1.0, 'Jean', 'Jean', 'calcule', 'noms-1', 1)",
        (i,),
    )
    con.execute(
        "INSERT INTO interp_conclusion_effet (conclusion_id, type, cible_type, cible_id)"
        " VALUES (1, 'rejeter_ident', 'interp_ident_personne', ?)",
        (i,),
    )


@pytest.mark.parametrize("table", sorted(TABLES))
def test_r10_update_refuse(base, table):
    _remplir(base)
    col = next(r[1] for r in base.execute(f"PRAGMA table_info({table})"))
    with pytest.raises(sqlite3.DatabaseError, match="R10"):
        base.execute(f"UPDATE {table} SET {col} = {col}")


@pytest.mark.parametrize("table", sorted(TABLES))
def test_r10_delete_refuse(base, table):
    _remplir(base)
    with pytest.raises(sqlite3.DatabaseError, match="R10"):
        base.execute(f"DELETE FROM {table}")


# 3. Vue active : la dernière décision du journal fait foi


def test_proposition_seule_n_est_pas_active(base):
    i = _ident(base, 1, 1)
    _statut(base, i, "propose")
    assert _actifs(base) == set()


def test_propose_puis_actif_devient_active(base):
    i = _ident(base, 1, 1)
    _statut(base, i, "propose", date="2026-10-30T10:00")
    _statut(base, i, "actif", date="2026-10-30T11:00")
    assert _actifs(base) == {i}


def test_actif_puis_rejete_sort_de_la_vue(base):
    i = _ident(base, 1, 1)
    _statut(base, i, "actif", date="2026-10-30T10:00")
    _statut(base, i, "rejete", date="2026-10-30T11:00")
    assert _actifs(base) == set()


def test_meme_date_departagee_par_id(base):
    i = _ident(base, 1, 1)
    _statut(base, i, "actif", date="2026-10-30T10:00")
    _statut(base, i, "rejete", date="2026-10-30T10:00")
    assert _actifs(base) == set()


def test_rejete_puis_reactive(base):
    i = _ident(base, 1, 1)
    _statut(base, i, "actif", date="2026-10-30T10:00")
    _statut(base, i, "rejete", date="2026-10-30T11:00")
    _statut(base, i, "actif", date="2026-10-30T12:00")
    assert _actifs(base) == {i}


def test_vue_expose_masque_et_personne(base):
    i = _ident(base, 2, 2)
    _statut(base, i, "actif")
    row = base.execute(
        "SELECT masque_id, personne_id FROM interp_ident_personne_actif"
    ).fetchone()
    assert row == (2, 2)


def _retracter(con, ident_id):
    con.execute(
        "INSERT INTO audit_retractation (cible_table, cible_id, lot_id, motif,"
        " date_retractation) VALUES ('interp_ident_personne', ?, 1, 'reconduction',"
        " '2026-10-30T12:00')",
        (ident_id,),
    )


def test_identification_retractee_sort_de_la_vue(base):
    i = _ident(base, 1, 1)
    _statut(base, i, "actif")
    _retracter(base, i)
    assert _actifs(base) == set()


# 4. Triggers métier : R11 et R18


def test_r11_seconde_identification_active_refusee(base):
    a, b = _ident(base, 1, 1), _ident(base, 1, 2)
    _statut(base, a, "actif", date="2026-10-30T10:00")
    with pytest.raises(sqlite3.DatabaseError, match="R11"):
        _statut(base, b, "actif", date="2026-10-30T11:00")
    assert _actifs(base) == {a}


def test_r11_permet_apres_rejet_de_la_precedente(base):
    a, b = _ident(base, 1, 1), _ident(base, 1, 2)
    _statut(base, a, "actif", date="2026-10-30T10:00")
    _statut(base, a, "rejete", date="2026-10-30T11:00")
    _statut(base, b, "actif", date="2026-10-30T12:00")
    assert _actifs(base) == {b}


def test_r11_homonymes_proposes_coexistent(base):
    a, b = _ident(base, 1, 1, AGENT), _ident(base, 1, 2, AGENT)
    _statut(base, a, "propose", AGENT)
    _statut(base, b, "propose", AGENT)
    rows = base.execute(
        "SELECT COUNT(*) FROM interp_ident_personne WHERE masque_id = 1"
    ).fetchone()
    assert rows == (2,)


def test_r11_ne_concerne_que_le_meme_masque(base):
    a, b = _ident(base, 1, 1), _ident(base, 2, 1)
    _statut(base, a, "actif")
    _statut(base, b, "actif")
    assert _actifs(base) == {a, b}


def test_r11_reactivation_de_la_meme_identification(base):
    a = _ident(base, 1, 1)
    _statut(base, a, "actif", date="2026-10-30T10:00")
    _statut(base, a, "actif", date="2026-10-30T11:00")
    assert _actifs(base) == {a}


def test_r11_ignore_une_identification_retractee(base):
    a, b = _ident(base, 1, 1), _ident(base, 1, 2)
    _statut(base, a, "actif", date="2026-10-30T10:00")
    _retracter(base, a)
    _statut(base, b, "actif", date="2026-10-30T11:00")
    assert _actifs(base) == {b}


def test_r18_agent_ne_peut_pas_activer(base):
    a = _ident(base, 1, 1, AGENT)
    with pytest.raises(sqlite3.DatabaseError, match="R18"):
        _statut(base, a, "actif", AGENT)
    assert _actifs(base) == set()


def test_r18_agent_ne_peut_pas_rejeter(base):
    """Rejeter est un jugement : l'agent apporte un indice « contre », pas un rejet."""
    a = _ident(base, 1, 1, HUMAIN)
    _statut(base, a, "actif", HUMAIN)
    with pytest.raises(sqlite3.DatabaseError, match="R18"):
        _statut(base, a, "rejete", AGENT, date="2026-10-30T11:00")
    assert _actifs(base) == {a}


def test_r18_agent_peut_proposer(base):
    a = _ident(base, 1, 1, AGENT)
    _statut(base, a, "propose", AGENT)
    assert _actifs(base) == set()


def test_r18_humain_active_une_proposition_d_agent(base):
    a = _ident(base, 1, 1, AGENT)
    _statut(base, a, "propose", AGENT, date="2026-10-30T10:00")
    _statut(base, a, "actif", HUMAIN, date="2026-10-30T11:00")
    assert _actifs(base) == {a}


def test_r18_import_peut_activer(base):
    a = _ident(base, 1, 1, IMPORT)
    _statut(base, a, "actif", IMPORT)
    assert _actifs(base) == {a}


def _ident_degre(con, degre, contributeur_id):
    return con.execute(
        "INSERT INTO interp_ident_personne (masque_id, personne_id, degre,"
        " contributeur_id, lot_id, date) VALUES (1, 1, ?, ?, 1, '2026-10-30')",
        (degre, contributeur_id),
    ).lastrowid


def test_r26_agent_ne_peut_pas_proposer_certain(base):
    with pytest.raises(sqlite3.DatabaseError, match="R26"):
        _ident_degre(base, "certain", AGENT)
    assert base.execute("SELECT COUNT(*) FROM interp_ident_personne").fetchone()[0] == 0


@pytest.mark.parametrize("degre", ["possible", "probable"])
def test_r26_agent_propose_possible_ou_probable(base, degre):
    assert _ident_degre(base, degre, AGENT)


@pytest.mark.parametrize("contributeur", [HUMAIN, IMPORT])
def test_r26_humain_et_import_peuvent_poser_certain(base, contributeur):
    assert _ident_degre(base, "certain", contributeur)
