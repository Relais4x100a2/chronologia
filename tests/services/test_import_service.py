"""Service d'import : empreinte, idempotence, persistance et différentiel en un appel."""

import sqlite3
from datetime import date
from pathlib import Path

import geneweb_py
import pytest

from chronologia.persistence.requetes import (
    rechercher_par_intervalle,
    rechercher_par_personne,
)
from chronologia.persistence.schema import creer_schema
from chronologia.services.importation import importer_fichier_geneweb

V1 = Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
V2 = Path(__file__).parents[1] / "fixtures/chronologia_sample_5_7_v2.gw"


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    return c


@pytest.fixture
def fichier(tmp_path):
    chemin = tmp_path / "base.gw"
    chemin.write_text(V1.read_text(encoding="utf-8"), encoding="utf-8")
    return chemin


def _nb(con, table):
    return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_premier_import_est_nouveau(con, fichier):
    r = importer_fichier_geneweb(con, fichier)
    assert r.statut == "nouveau"
    assert r.bilan_diff is None
    assert len(r.empreinte) == 64
    assert r.nb_entites > 0
    assert _nb(con, "source_lot_import") == 1
    assert _nb(con, "audit_retractation") == 0


def test_reimport_identique_est_ignore_sans_rien_ecrire(con, fichier):
    premier = importer_fichier_geneweb(con, fichier)
    avant = _nb(con, "source_factoide")
    second = importer_fichier_geneweb(con, fichier)
    assert second.statut == "identique_ignore"
    assert second.lot_id == premier.lot_id
    assert second.empreinte == premier.empreinte
    assert _nb(con, "source_lot_import") == 1
    assert _nb(con, "source_factoide") == avant


def test_reimport_modifie_applique_le_differentiel(con, fichier):
    premier = importer_fichier_geneweb(con, fichier)
    fichier.write_text(V2.read_text(encoding="utf-8"), encoding="utf-8")
    r = importer_fichier_geneweb(con, fichier)

    assert r.statut == "mis_a_jour"
    assert r.lot_id != premier.lot_id
    assert r.bilan_diff is not None
    assert r.bilan_diff.retractions >= 1 and r.bilan_diff.modifications >= 1
    types_jean = [
        t.type_evenement
        for t in rechercher_par_personne(con, "gw:pers:MARTIN_Jean_0")
    ]
    assert "deces" not in types_jean
    bapteme = [
        t.date_declaree
        for t in rechercher_par_intervalle(con, date(1712, 1, 1), date(1712, 12, 31))
        if t.type_evenement == "bapteme"
    ]
    assert bapteme == ["04/03/1712"]


def test_lot_precedent_explicite_prime_sur_le_nom_de_fichier(con, fichier, tmp_path):
    autre = tmp_path / "autre.gw"
    autre.write_text(V1.read_text(encoding="utf-8"), encoding="utf-8")
    importer_fichier_geneweb(con, fichier)
    id_autre = importer_fichier_geneweb(con, autre).lot_id  # même contenu : ignoré
    assert id_autre == 1
    fichier.write_text(V2.read_text(encoding="utf-8"), encoding="utf-8")
    r = importer_fichier_geneweb(con, fichier, lot_precedent_id=1)
    assert r.statut == "mis_a_jour"


def test_echec_du_differentiel_ne_laisse_pas_de_lot_a_moitie(con, fichier, monkeypatch):
    importer_fichier_geneweb(con, fichier)
    fichier.write_text(V2.read_text(encoding="utf-8"), encoding="utf-8")

    def casse(*a, **k):
        raise RuntimeError("panne")

    monkeypatch.setattr("chronologia.services.importation.comparer_lots", casse)
    with pytest.raises(RuntimeError):
        importer_fichier_geneweb(con, fichier)
    assert _nb(con, "source_lot_import") == 1
    assert _nb(con, "audit_retractation") == 0
