"""Événements familiaux fevt : chaque tag garde son type dans la couche Source."""

import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie

_BASE = "fam MARTIN Pierre +1705 DUBOIS Marie\nfevt\n"


def _lot(corps: str, entete: str = _BASE):
    texte = entete + corps + "end fevt\n"
    return importer_genealogie(GeneWebParser(validate=False).parse_string(texte), empreinte="t")


def _types(lot):
    return sorted(f.type_evenement for f in lot.factoides if f.type_evenement)


@pytest.mark.parametrize(
    "tag,type_attendu",
    [
        ("marc", "contrat_mariage"),
        ("marb", "bans_mariage"),
        ("marl", "licence_mariage"),
        ("nmar", "non_mariage"),
        ("nmen", "non_mention"),
        ("anul", "annulation"),
        ("pacs", "pacs"),
        ("resi", "residence"),
        ("sep", "separation"),
        ("enga", "engagement"),
    ],
)
def test_tag_familial_a_son_propre_type(tag, type_attendu):
    assert type_attendu in _types(_lot(f"#{tag} 1704 #p Lyon\n"))


def test_tag_libre_garde_son_ecriture_comme_type():
    assert "Hypotheque" in _types(_lot("#Hypotheque 1704\n"))


def test_wnote_d_un_contrat_devient_note_de_participation():
    lot = _lot("#marc 1704\nwit m: LEROY Paul\nwnote notaire\n")
    assert [p.note for p in lot.participations if p.note] == ["notaire"]


def test_familles_sans_conjoint_ont_des_cles_distinctes():
    texte = (
        "fam ? ? + ? ?\nbeg\n- h Pierre\nend\n"
        "fam ? ? + ? ?\nbeg\n- f Anne\nend\n"
    )
    lot = importer_genealogie(GeneWebParser(validate=False).parse_string(texte), empreinte="t")
    cles = {f.cle_famille for f in lot.factoides if f.cle_famille}
    assert len(cles) == 2
