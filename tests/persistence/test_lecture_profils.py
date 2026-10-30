"""Lecture des profils de personnes depuis les identifications actives (décision 20, R8)."""

import sqlite3
from datetime import date

import pytest

from chronologia.interpretation.profils import FaitDate, NomPersonne
from chronologia.persistence.lecture_profils import couples_identifies, lire_profils
from chronologia.persistence.schema import creer_schema
from chronologia.services.importation import importer_fichier_geneweb

BASE_A = """fam MARTIN Pierre + DUPONT Marie
beg
- h Jean 1680
end

fam MARTIN Jean 1680 1740 +1705 DURAND Claire
"""


@pytest.fixture
def con(tmp_path):
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    chemin = tmp_path / "base_a.gw"
    chemin.write_text(BASE_A, encoding="utf-8")
    importer_fichier_geneweb(c, chemin)
    return c


def _refs(con, profils):
    """Référence de chaque personne lue, pour nommer les profils dans les tests."""
    return {
        con.execute(
            "SELECT ref FROM interp_personne WHERE id = ?", (p.personne_id,)
        ).fetchone()[0]: p
        for p in profils
    }


def _profil(con, ref):
    return _refs(con, lire_profils(con))[ref]


def test_un_profil_par_personne_active(con):
    profils = lire_profils(con)
    assert set(_refs(con, profils)) == {
        "gw:pers:MARTIN_Pierre_0", "gw:pers:DUPONT_Marie_0",
        "gw:pers:MARTIN_Jean_0", "gw:pers:DURAND_Claire_0",
    }  # fmt: skip
    assert {p.base for p in profils} == {"gw:base_a.gw"}


def test_profil_reunit_noms_faits_parents_conjoints(con):
    jean = _profil(con, "gw:pers:MARTIN_Jean_0")
    assert jean.noms == (NomPersonne("MARTIN", "Jean"),)
    assert sorted(jean.faits, key=lambda f: f.role) == [
        FaitDate("decede", date(1740, 1, 1), date(1740, 12, 31)),
        FaitDate("epoux", date(1705, 1, 1), date(1705, 12, 31)),
        FaitDate("ne", date(1680, 1, 1), date(1680, 12, 31)),
    ]
    assert jean.peres == (NomPersonne("MARTIN", "Pierre"),)
    assert jean.meres == (NomPersonne("DUPONT", "Marie"),)
    assert jean.conjoints == (NomPersonne("DURAND", "Claire"),)
    # Le faisceau reste par masque : les parents ne sont que sur le masque de filiation.
    assert sum(1 for m in jean.masques if m.pere) == 1


def test_nom_compose_et_prenoms_multiples(tmp_path):
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    chemin = tmp_path / "base.gw"
    chemin.write_text(
        "fam DE_LA_TOUR Pierre_Jean 1700 + DUPONT Marie\n", encoding="utf-8"
    )
    importer_fichier_geneweb(c, chemin)
    noms = {n for p in lire_profils(c) for n in p.noms}
    assert NomPersonne("DE_LA_TOUR", "Pierre_Jean") in noms


def test_personne_fusionnee_par_same_as_exclue(con):
    jean = _profil(con, "gw:pers:MARTIN_Jean_0")
    # Un doublon chaîné vers Jean, avec une identification active humaine.
    con.execute(
        "INSERT INTO interp_contributeur (nom, type) VALUES ('historien', 'humain')"
    )
    con.execute(
        "INSERT INTO interp_personne (lot_id, ref, same_as_id) VALUES (NULL, 'doublon', ?)",
        (jean.personne_id,),
    )
    doublon = con.execute(
        "SELECT id FROM interp_personne WHERE ref = 'doublon'"
    ).fetchone()[0]
    con.execute(
        "INSERT INTO source_masque (lot_id, ref, passage_id, nom_ecrit, cle_externe)"
        " VALUES (1, 'MX', 1, 'Jean MARTIN', 'saisie:MX')"
    )
    masque = con.execute("SELECT id FROM source_masque WHERE ref = 'MX'").fetchone()[0]
    ident = con.execute(
        "INSERT INTO interp_ident_personne (masque_id, personne_id, degre, contributeur_id,"
        " date) VALUES (?, ?, 'certain', (SELECT id FROM interp_contributeur"
        " WHERE nom = 'historien'), '2026-10-30')",
        (masque, doublon),
    ).lastrowid
    con.execute(
        "INSERT INTO interp_ident_personne_statut (ident_id, statut, contributeur_id, date)"
        " SELECT ?, 'actif', id, '2026-10-30' FROM interp_contributeur WHERE nom = 'historien'",
        (ident,),
    )
    assert "doublon" not in _refs(con, lire_profils(con))


def test_personne_sans_identification_active_absente(con, tmp_path):
    # Réimport sans Claire : sa personne demeure, sans identification active.
    chemin = tmp_path / "base_a.gw"
    chemin.write_text(BASE_A.replace(" +1705 DURAND Claire", ""), encoding="utf-8")
    importer_fichier_geneweb(con, chemin)
    assert "gw:pers:DURAND_Claire_0" not in _refs(con, lire_profils(con))


def test_couples_identifies_tous_statuts(con):
    couples = couples_identifies(con)
    n = con.execute("SELECT COUNT(*) FROM interp_ident_personne").fetchone()[0]
    assert len(couples) == n
    assert all(isinstance(m, int) and isinstance(p, int) for m, p in couples)
