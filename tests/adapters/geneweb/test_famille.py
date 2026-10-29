"""Mariage et filiation : fam, fevt et enfants vers la couche Source."""

from datetime import date
from pathlib import Path

import geneweb_py
import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie

FIXTURE = (
    Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
)

# Fictif. Le fevt reprend le mariage de la ligne fam : un seul factoïde attendu.
FEVT = """\
fam DUPONT Paul +1750 #mp Chartres MARTIN Anne
fevt
#marr 12/5/1750 #p Chartres #s Registre BMS Chartres
wit m: #offi BERNARD Henri
end fevt
beg
- h Luc
end
"""

DIVORCE = "fam DUPONT Paul +1750 - 1760 MARTIN Anne\n"


def _lot(texte=None):
    parseur = GeneWebParser(validate=False)
    genealogie = (
        parseur.parse_file(FIXTURE) if texte is None else parseur.parse_string(texte)
    )
    return importer_genealogie(genealogie, fichier="x.gw")


def _cles(lot):
    return {m.ref: m.cle_externe for m in lot.masques}


def _factoides(lot, type_evenement):
    return [f for f in lot.factoides if f.type_evenement == type_evenement]


def _roles(lot, factoide):
    cles = _cles(lot)
    return {
        cles[p.masque_ref]: p.role
        for p in lot.participations
        if p.factoide_ref == factoide.ref
    }


def test_mariage_de_la_ligne_fam():
    lot = _lot()
    (f,) = _factoides(lot, "mariage")
    assert f.date_declaree == "1705"
    assert (f.date_min, f.date_max) == (date(1705, 1, 1), date(1705, 12, 31))
    assert _roles(lot, f) == {"MARTIN_Pierre_0": "epoux", "DUBOIS_Marie_0": "epouse"}


def test_mariage_passage_est_le_bloc_fam():
    lot = _lot()
    (f,) = _factoides(lot, "mariage")
    passage = next(p for p in lot.passages if p.ref == f.passage_ref)
    assert passage.citation_brute == "BMS Saint-Aubin 1705-1715"
    assert (passage.ligne_debut, passage.ligne_fin) == (4, 8)
    assert passage.fichier_source == "x.gw"


def test_mariage_a_son_evenement_certain():
    lot = _lot()
    (f,) = _factoides(lot, "mariage")
    (ident,) = [i for i in lot.ident_evenements if i.factoide_ref == f.ref]
    assert (ident.degre, ident.statut) == ("certain", "actif")


def test_filiation_relie_l_enfant_a_ses_deux_parents():
    lot = _lot()
    cles = _cles(lot)
    liens = {
        (cles[r.sujet_masque_ref], r.orientation, cles[r.objet_masque_ref])
        for r in lot.relations
        if r.type_relation == "filiation"
    }
    assert liens == {
        ("MARTIN_Jean_0", "pere", "MARTIN_Pierre_0"),
        ("MARTIN_Jean_0", "mere", "DUBOIS_Marie_0"),
    }


def test_filiation_est_portee_par_la_source_de_la_famille():
    lot = _lot()
    r = next(r for r in lot.relations if r.type_relation == "filiation")
    f = next(f for f in lot.factoides if f.ref == r.factoide_ref)
    passage = next(p for p in lot.passages if p.ref == f.passage_ref)
    assert f.type_evenement is None
    assert passage.citation_brute == "BMS Saint-Aubin 1705-1715"


def test_un_seul_factoide_de_filiation_par_famille():
    lot = _lot()
    refs = {r.factoide_ref for r in lot.relations if r.type_relation == "filiation"}
    assert len(refs) == 1


def test_fevt_remplace_le_mariage_de_la_ligne_fam():
    lot = _lot(FEVT)
    (f,) = _factoides(lot, "mariage")
    assert f.date_declaree == "12/05/1750"
    passage = next(p for p in lot.passages if p.ref == f.passage_ref)
    assert passage.citation_brute == "Registre BMS Chartres"
    assert (passage.ligne_debut, passage.ligne_fin) == (3, 4)


def test_officier_d_un_mariage_est_celebrant():
    lot = _lot(FEVT)
    (f,) = _factoides(lot, "mariage")
    assert _roles(lot, f)["BERNARD_Henri_0"] == "celebrant"


def test_divorce_est_un_factoide_distinct():
    lot = _lot(DIVORCE)
    (f,) = _factoides(lot, "divorce")
    assert (f.date_min, f.date_max) == (date(1760, 1, 1), date(1760, 12, 31))
    assert _roles(lot, f) == {"DUPONT_Paul_0": "epoux", "MARTIN_Anne_0": "epouse"}


def test_date_brute_est_la_chaine_ecrite():
    lot = _lot()
    (mariage,) = _factoides(lot, "mariage")
    assert mariage.date_brute == "1705"
    lot = _lot(FEVT)
    (mariage,) = _factoides(lot, "mariage")
    assert (mariage.date_brute, mariage.date_declaree) == ("12/5/1750", "12/05/1750")
