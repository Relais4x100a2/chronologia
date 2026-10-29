"""Consultation de base : par personne, par intervalle chronologique, par lieu."""

import sqlite3
from datetime import date
from pathlib import Path

import geneweb_py
import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie
from chronologia.persistence.depot import persister_lot, retracter_factoide
from chronologia.persistence.requetes import (
    rechercher_par_intervalle,
    rechercher_par_lieu,
    rechercher_par_personne,
)
from chronologia.persistence.schema import creer_schema

FIXTURE = (
    Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
)


@pytest.fixture
def base():
    lot_import = importer_genealogie(
        GeneWebParser(validate=False).parse_file(FIXTURE),
        fichier=FIXTURE.name,
        empreinte="e1",
    )
    con = sqlite3.connect(":memory:")
    creer_schema(con)
    lot_id = persister_lot(con, lot_import)
    return con, lot_id


def _types(trouves):
    return sorted(t.type_evenement or "" for t in trouves)


def test_par_personne_retrouve_ses_factoides(base):
    con, _ = base
    trouves = rechercher_par_personne(con, "gw:pers:MARTIN_Jean_0")
    assert {"naissance", "bapteme"} <= set(_types(trouves))


def test_par_personne_inconnue_est_vide(base):
    assert rechercher_par_personne(base[0], "gw:pers:NUL_Nul_0") == []


def test_par_intervalle_garde_ce_qui_chevauche(base):
    con, _ = base
    assert _types(rechercher_par_intervalle(con, date(1712, 1, 1), date(1712, 12, 31))) == [
        "bapteme",
        "naissance",
    ]
    # décès ~1790 couvre 1785-1795 : un chevauchement partiel suffit
    assert "deces" in _types(rechercher_par_intervalle(con, date(1794, 1, 1), date(1800, 1, 1)))
    assert rechercher_par_intervalle(con, date(1600, 1, 1), date(1650, 1, 1)) == []


def test_par_lieu_utilise_la_forme_normalisee_ou_ecrite(base):
    con, _ = base
    assert rechercher_par_lieu(con, "Saint-Aubin")
    assert rechercher_par_lieu(con, "Nulle-Part") == []


def test_un_factoide_retracte_n_apparait_plus(base):
    con, lot_id = base
    avant = rechercher_par_intervalle(con, date(1712, 1, 1), date(1712, 12, 31))
    retracter_factoide(con, lot_id, avant[0].ref, "retiré")
    apres = rechercher_par_intervalle(con, date(1712, 1, 1), date(1712, 12, 31))
    assert len(apres) == len(avant) - 1


def test_aller_retour_fichier_gw_vers_base_et_relecture(tmp_path):
    lot_import = importer_genealogie(
        GeneWebParser(validate=False).parse_file(FIXTURE),
        fichier=FIXTURE.name,
        empreinte="e2",
    )
    chemin = tmp_path / "chronologia.db"
    con = sqlite3.connect(chemin)
    creer_schema(con)
    persister_lot(con, lot_import)
    con.close()

    con = sqlite3.connect(chemin)  # relecture depuis le fichier
    lus = {
        r[0]: r[1:]
        for r in con.execute(
            "SELECT ref, type_evenement, date_declaree, date_brute, date_min, date_max,"
            " calendrier, date_incertaine, cle_famille FROM source_factoide"
        )
    }
    for f in lot_import.factoides:
        assert lus[f.ref] == (
            f.type_evenement, f.date_declaree, f.date_brute,
            f.date_min.isoformat() if f.date_min else None,
            f.date_max.isoformat() if f.date_max else None,
            f.calendrier, int(f.date_incertaine), f.cle_famille,
        )  # fmt: skip
    roles = sorted(
        r[0] for r in con.execute("SELECT role FROM source_participation")
    )
    assert roles == sorted(p.role for p in lot_import.participations)
    # La clé externe relie la base aux masques du lot : retrouver un parcours.
    assert rechercher_par_personne(con, "gw:pers:MARTIN_Jean_0")
