"""Écriture d'un lot : atomique (tout ou rien) et idempotente par empreinte."""

import dataclasses
import sqlite3
from pathlib import Path

import geneweb_py
import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie
from chronologia.modele.entites import Participation
from chronologia.persistence.depot import LotDejaPersiste, persister_lot
from chronologia.persistence.schema import creer_schema

FIXTURE = (
    Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
)
TABLES = (
    "source_lot_import source_passage source_masque source_factoide "
    "source_participation source_relation source_qualite source_mention_lieu "
    "interp_evenement interp_ident_evenement interp_conclusion"
).split()


@pytest.fixture(scope="module")
def lot_import():
    genealogie = GeneWebParser(validate=False).parse_file(FIXTURE)
    return importer_genealogie(genealogie, fichier=FIXTURE.name, empreinte="abc123")


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    return c


def _compte(con):
    return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}


def test_lot_persiste_avec_toutes_ses_entites(con, lot_import):
    lot_id = persister_lot(con, lot_import)
    n = _compte(con)
    assert n["source_lot_import"] == 1
    assert n["source_passage"] == len(lot_import.passages)
    assert n["source_masque"] == len(lot_import.masques)
    assert n["source_factoide"] == len(lot_import.factoides)
    assert n["source_participation"] == len(lot_import.participations)
    assert n["source_relation"] == len(lot_import.relations)
    assert n["interp_evenement"] == len(lot_import.evenements)
    assert n["interp_ident_evenement"] == len(lot_import.ident_evenements)
    assert n["interp_conclusion"] == len(lot_import.conclusions)
    assert con.execute("SELECT id FROM source_lot_import").fetchone()[0] == lot_id


def test_dates_stockees_en_iso_avec_texte_verbatim(con, lot_import):
    persister_lot(con, lot_import)
    f = next(f for f in lot_import.factoides if f.date_min)
    ligne = con.execute(
        "SELECT date_min, date_max, date_brute FROM source_factoide WHERE ref=?",
        (f.ref,),
    ).fetchone()
    assert ligne == (f.date_min.isoformat(), f.date_max.isoformat(), f.date_brute)


def test_echec_en_cours_d_ecriture_ne_laisse_aucune_ligne(con, lot_import):
    cassee = dataclasses.replace(
        lot_import,
        participations=lot_import.participations
        + (Participation("F-inconnu", "M-inconnu", "sujet", 0),),
    )
    with pytest.raises(KeyError):
        persister_lot(con, cassee)
    assert set(_compte(con).values()) == {0}


def test_meme_empreinte_refusee_sans_rien_reecrire(con, lot_import):
    persister_lot(con, lot_import)
    avant = _compte(con)
    with pytest.raises(LotDejaPersiste):
        persister_lot(con, lot_import)
    assert _compte(con) == avant


def test_retractation_masque_le_factoide_sans_rien_supprimer(con, lot_import):
    from chronologia.persistence.depot import retracter_factoide

    lot_id = persister_lot(con, lot_import)
    total = len(lot_import.factoides)
    cible = lot_import.factoides[0].ref
    retracter_factoide(con, lot_id, cible, "absent du lot suivant")
    actifs = {r[0] for r in con.execute("SELECT ref FROM source_factoide_actif")}
    assert cible not in actifs
    assert len(actifs) == total - 1
    assert con.execute("SELECT COUNT(*) FROM source_factoide").fetchone()[0] == total
    assert con.execute("SELECT motif FROM audit_retractation").fetchone() == (
        "absent du lot suivant",
    )


def test_retractation_d_un_factoide_inconnu_est_refusee(con, lot_import):
    from chronologia.persistence.depot import retracter_factoide

    lot_id = persister_lot(con, lot_import)
    with pytest.raises(KeyError):
        retracter_factoide(con, lot_id, "F-inconnu", "x")


def test_relation_en_double_dans_la_source_est_conservee(con, lot_import):
    """R13 : la source peut répéter une arête ; on ne la fusionne pas en silence."""
    r = lot_import.relations[0]
    doublee = dataclasses.replace(
        lot_import, relations=lot_import.relations + (r,)
    )
    persister_lot(con, doublee)
    assert _compte(con)["source_relation"] == len(lot_import.relations) + 1
