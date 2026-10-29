"""Relecture d'un lot depuis la base : identique au lot écrit."""

import sqlite3
from pathlib import Path

import geneweb_py
import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie
from chronologia.persistence.depot import persister_lot, relire_lot
from chronologia.persistence.schema import creer_schema

V1 = Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
V2 = Path(__file__).parents[1] / "fixtures/chronologia_sample_5_7_v2.gw"


@pytest.mark.parametrize("chemin", [V1, V2])
def test_relire_lot_redonne_le_lot_ecrit(chemin):
    lot_import = importer_genealogie(
        GeneWebParser(validate=False).parse_string(chemin.read_text(encoding="utf-8")),
        fichier=chemin.name,
        empreinte="e",
    )
    con = sqlite3.connect(":memory:")
    creer_schema(con)
    persister_lot(con, lot_import)
    lot_id = persister_lot(con, _autre(chemin))  # un second lot ne doit pas se mêler
    assert relire_lot(con, 1) == lot_import
    assert relire_lot(con, lot_id) != lot_import


def _autre(chemin):
    autre = V2 if chemin == V1 else V1
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(autre.read_text(encoding="utf-8")),
        fichier=autre.name,
        empreinte="autre",
    )


def test_relire_lot_inconnu():
    con = sqlite3.connect(":memory:")
    creer_schema(con)
    with pytest.raises(KeyError):
        relire_lot(con, 99)
