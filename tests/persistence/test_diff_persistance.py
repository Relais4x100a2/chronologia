"""Pont différentiel -> base : rétractions par audit, jamais de suppression (R10)."""

import sqlite3
from pathlib import Path

import geneweb_py
import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie
from chronologia.adapters.geneweb.diff import DiffLots, Ecart, comparer_lots
from chronologia.persistence.depot import persister_lot
from chronologia.persistence.diff import appliquer_diff
from chronologia.persistence.requetes import (
    rechercher_par_intervalle,
    rechercher_par_personne,
)
from chronologia.persistence.schema import creer_schema

V1 = Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
V2 = Path(__file__).parents[1] / "fixtures/chronologia_sample_5_7_v2.gw"


def _lot(chemin: Path):
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(chemin.read_text(encoding="utf-8")),
        fichier=chemin.name,
        empreinte=chemin.name,
    )


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    return c


def _actifs(con, table="source_factoide_actif"):
    return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_retractation_du_diff_masque_l_ancien_factoide(con):
    lot_a = _lot(V1)
    id_a = persister_lot(con, lot_a)
    id_b = persister_lot(con, _lot(V2))
    cible = lot_a.factoides[0]
    diff = DiffLots((), (), (), (Ecart("factoide", "k", cible, None),))
    avant_total = con.execute("SELECT COUNT(*) FROM source_factoide").fetchone()[0]
    avant_actifs = _actifs(con)

    bilan = appliquer_diff(con, diff, id_a, id_b)

    assert bilan.retractions == 1
    assert _actifs(con) == avant_actifs - 1
    assert con.execute("SELECT COUNT(*) FROM source_factoide").fetchone()[0] == avant_total
    assert con.execute(
        "SELECT motif, lot_id FROM audit_retractation"
    ).fetchall() == [("retractation", id_b)]


def test_appliquer_deux_fois_n_ecrit_rien_de_plus(con):
    id_a = persister_lot(con, lot_a := _lot(V1))
    id_b = persister_lot(con, lot_b := _lot(V2))
    diff = comparer_lots(lot_a, lot_b)
    appliquer_diff(con, diff, id_a, id_b)
    n = con.execute("SELECT COUNT(*) FROM audit_retractation").fetchone()[0]
    bilan = appliquer_diff(con, diff, id_a, id_b)
    assert con.execute("SELECT COUNT(*) FROM audit_retractation").fetchone()[0] == n
    assert bilan.retractions == bilan.modifications == bilan.reconductions == 0


def test_bout_en_bout_v1_puis_v2(con):
    lot_a, lot_b = _lot(V1), _lot(V2)
    id_a = persister_lot(con, lot_a)
    id_b = persister_lot(con, lot_b)
    diff = comparer_lots(lot_a, lot_b)
    bilan = appliquer_diff(con, diff, id_a, id_b)
    assert bilan.modifications >= 1 and bilan.retractions >= 1

    # Après application, la vue active équivaut au lot B : chaque fait une seule fois.
    assert _actifs(con) == len(lot_b.factoides)
    assert _actifs(con, "interp_conclusion_actif") == len(lot_b.conclusions)
    types_jean = [
        t.type_evenement
        for t in rechercher_par_personne(con, "gw:pers:MARTIN_Jean_0")
    ]
    assert "deces" not in types_jean  # décès retiré dans v2
    assert types_jean.count("naissance") == 1
    assert rechercher_par_personne(con, "gw:pers:MARTIN_Anne_0")  # enfant ajoutée

    from datetime import date

    bapteme = [
        t
        for t in rechercher_par_intervalle(con, date(1712, 1, 1), date(1712, 12, 31))
        if t.type_evenement == "bapteme"
    ]
    assert [t.date_declaree for t in bapteme] == ["04/03/1712"]
