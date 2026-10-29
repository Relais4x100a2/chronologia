"""Mapper GeneWeb -> couche Source, sur l'exemple 5.7 (fixture synthétique de toldot)."""

from datetime import date
from pathlib import Path

import geneweb_py
import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie

FIXTURE = (
    Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
)


@pytest.fixture(scope="module")
def lot():
    genealogie = GeneWebParser(validate=False).parse_file(FIXTURE)
    return importer_genealogie(genealogie, fichier="chronologia_sample_5_7.gw")


def _factoide(lot, type_evenement):
    return next(f for f in lot.factoides if f.type_evenement == type_evenement)


def _passage(lot, factoide):
    return next(p for p in lot.passages if p.ref == factoide.passage_ref)


def _roles(lot, factoide):
    masques = {m.ref: m for m in lot.masques}
    return {
        masques[p.masque_ref].cle_externe: p.role
        for p in lot.participations
        if p.factoide_ref == factoide.ref
    }


def test_bapteme_passage_porte_citation_et_lignes(lot):
    passage = _passage(lot, _factoide(lot, "bapteme"))
    assert passage.citation_brute == "BMS Saint-Aubin f°42v"
    assert (passage.ligne_debut, passage.ligne_fin) == (11, 15)
    assert passage.fichier_source == "chronologia_sample_5_7.gw"


def test_bapteme_date_exacte_et_texte_declare(lot):
    f = _factoide(lot, "bapteme")
    assert (f.date_min, f.date_max) == (date(1712, 3, 3), date(1712, 3, 3))
    assert f.date_declaree == "03/03/1712"


def test_deces_environ_donne_fenetre_de_cinq_ans(lot):
    f = _factoide(lot, "deces")
    assert f.date_declaree == "~1790"
    assert (f.date_min, f.date_max) == (date(1785, 1, 1), date(1795, 12, 31))


def test_roles_des_participants_du_bapteme(lot):
    roles = _roles(lot, _factoide(lot, "bapteme"))
    assert roles["MARTIN_Jean_0"] == "baptise"
    assert roles["MOREAU_Louis_0"] == "parrain"
    assert roles["DUBOIS_Anne_2"] == "marraine"
    assert roles["LEROY_Jean_0"] == "temoin"
    assert roles["GIRARD_Camille_0"] == "temoin"


def test_un_masque_par_personne_et_par_passage(lot):
    f = _factoide(lot, "bapteme")
    masques = [m for m in lot.masques if m.passage_ref == f.passage_ref]
    cles = [m.cle_externe for m in masques]
    assert len(cles) == len(set(cles)) == 5


def test_chaque_factoide_d_evenement_a_son_evenement_certain(lot):
    evenements = [f for f in lot.factoides if f.type_evenement is not None]
    assert len(evenements) == 3
    for f in evenements:
        idents = [i for i in lot.ident_evenements if i.factoide_ref == f.ref]
        assert len(idents) == 1
        assert (idents[0].degre, idents[0].statut) == ("certain", "actif")


def test_relations_typees_gardent_les_occurrences(lot):
    masques = {m.ref: m.cle_externe for m in lot.masques}
    relations = {
        (r.type_relation, r.orientation, masques[r.objet_masque_ref])
        for r in lot.relations
        if masques[r.sujet_masque_ref] == "MARTIN_Jean_0" and r.type_relation != "filiation"
    }
    assert relations == {
        ("parrainage", "pere", "MOREAU_Louis_1"),
        ("parrainage", "mere", "DUBOIS_Anne_2"),
        ("adoption", None, "LEROY_Jean_3"),
        ("nourricier", "mere", "GIRARD_Camille_0"),
    }


def test_homonymes_restent_distincts(lot):
    cles = {m.cle_externe for m in lot.masques}
    assert {"MOREAU_Louis_0", "MOREAU_Louis_1"} <= cles


def test_toute_relation_est_portee_par_un_factoide_existant(lot):
    refs = {f.ref for f in lot.factoides}
    assert all(r.factoide_ref in refs for r in lot.relations)
