"""Enfants du bloc ``beg … end`` et événements déclarés sur les lignes de personne."""

from datetime import date

from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie

# Fictif.
TEXTE = """\
fam DUPONT Paul 1720 #bp Dreux +1750 MARTIN Anne
src BMS Chartres
beg
- h Luc 3/3/1751 #bp [Moulin]_-_Dreux #bs Reg_N !5/3/1751 #pp Chartres #ps Reg_B 1790 #dp Dreux
- f Marie 1753
- Jean
end
"""


def _lot():
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(TEXTE), fichier="x.gw"
    )


def _cle(lot, masque_ref):
    return next(m for m in lot.masques if m.ref == masque_ref).cle_externe


def _evts(lot, cle, type_evt):
    """Factoïdes de ce type où la personne est le rôle principal."""
    sortie = []
    for p in lot.participations:
        if _cle(lot, p.masque_ref) == f"gw:pers:{cle}":
            f = next(f for f in lot.factoides if f.ref == p.factoide_ref)
            if f.type_evenement == type_evt:
                sortie.append((f, p.role))
    return sortie


def test_naissance_de_l_enfant_avec_lieu_et_passage_de_la_ligne():
    lot = _lot()
    ((f, role),) = _evts(lot, "DUPONT_Luc_0", "naissance")
    assert role == "ne"
    assert (f.date_brute, f.date_min) == ("3/3/1751", date(1751, 3, 3))
    (m,) = [m for m in lot.mentions_lieu if m.factoide_ref == f.ref]
    assert m.forme_ecrite == "[Moulin]_-_Dreux" and m.forme_normalisee == "Dreux"
    p = next(p for p in lot.passages if p.ref == f.passage_ref)
    assert (p.citation_brute, p.ligne_debut, p.ligne_fin) == ("Reg N", 4, 4)


def test_bapteme_et_deces_de_l_enfant():
    lot = _lot()
    ((b, rb),) = _evts(lot, "DUPONT_Luc_0", "bapteme")
    ((d, rd),) = _evts(lot, "DUPONT_Luc_0", "deces")
    assert (rb, b.date_brute) == ("baptise", "5/3/1751")
    assert (rd, d.date_brute) == ("decede", "1790")


def test_naissance_a_date_seule():
    lot = _lot()
    ((f, _),) = _evts(lot, "DUPONT_Marie_0", "naissance")
    assert f.date_brute == "1753"


def test_enfant_sans_information_n_a_pas_de_factoide_personnel():
    lot = _lot()
    assert not _evts(lot, "DUPONT_Jean_0", "naissance")


def test_parent_de_la_ligne_fam_a_sa_naissance():
    lot = _lot()
    ((f, _),) = _evts(lot, "DUPONT_Paul_0", "naissance")
    assert f.date_brute == "1720"


def test_filiation_vers_les_deux_parents_pour_chaque_enfant():
    lot = _lot()
    sujets = {}
    for r in lot.relations:
        if r.type_relation == "filiation":
            sujets.setdefault(_cle(lot, r.sujet_masque_ref), set()).add(r.orientation)
    assert sujets == {
        "gw:pers:DUPONT_Luc_0": {"pere", "mere"},
        "gw:pers:DUPONT_Marie_0": {"pere", "mere"},
        "gw:pers:DUPONT_Jean_0": {"pere", "mere"},
    }


def test_dates_aberrantes_gardent_le_texte_sans_bornes():
    texte = (
        "fam DUPONT Paul +1750 MARTIN Anne\nbeg\n"
        "- h Luc 30/2/1700\n- f Eve 1/1/99999999999\nend\n"
    )
    lot = importer_genealogie(GeneWebParser(validate=False).parse_string(texte))
    naissances = [f for f in lot.factoides if f.type_evenement == "naissance"]
    assert len(naissances) == 2
    for f in naissances:
        assert f.date_brute and f.date_min is None and f.date_max is None
