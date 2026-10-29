"""Lieux (MENTION_LIEU), qualités (#occu, titres) et provenance des rel."""

from datetime import date

from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie

# Fictif. Titre : [nom:type:lieu:début:fin:rang].
TEXTE = """\
fam DUPONT Paul 1720 #occu Laboureur [Comte:titre:Chartres:1750:1760:2] +1750 #mp [Eglise]_-_Chartres MARTIN Anne
src BMS Chartres
beg
- h Luc 1751 #occu Tisserand
end

pevt DUPONT Luc
#bapt 3/3/1751 #p Chartres #s BMS Chartres
end pevt

rel DUPONT Luc
beg
- godp fath: DUPONT Pierre.1
end
"""


def _lot():
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(TEXTE), fichier="x.gw"
    )


def _cles(lot):
    return {m.ref: m.cle_externe.removeprefix("gw:pers:") for m in lot.masques}


def _factoide(lot, type_evenement):
    (f,) = [f for f in lot.factoides if f.type_evenement == type_evenement]
    return f


def test_lieu_d_un_evenement_est_une_mention_moderne():
    lot = _lot()
    f = _factoide(lot, "bapteme")
    (m,) = [m for m in lot.mentions_lieu if m.factoide_ref == f.ref]
    assert (m.forme_ecrite, m.forme_normalisee) == ("Chartres", "Chartres")
    assert (m.fonction, m.epoque_designation) == ("evenement", "moderne")
    assert m.masque_ref is None and m.qualite_ref is None


def test_lieu_du_mariage_garde_la_forme_ecrite_et_le_nom_normalise():
    lot = _lot()
    f = _factoide(lot, "mariage")
    (m,) = [m for m in lot.mentions_lieu if m.factoide_ref == f.ref]
    assert m.forme_ecrite == "[Eglise]_-_Chartres"
    assert m.forme_normalisee == "Chartres"


def test_pas_de_mention_sans_lieu():
    lot = _lot()
    assert all(m.forme_ecrite for m in lot.mentions_lieu)
    assert not [m for m in lot.mentions_lieu if m.factoide_ref == _factoide(lot, "bapteme").ref and m.fonction != "evenement"]


def test_profession_devient_une_qualite():
    lot = _lot()
    cles = _cles(lot)
    professions = {
        (cles[q.masque_ref], q.role) for q in lot.qualites if q.categorie == "profession"
    }
    assert professions == {("DUPONT_Paul_0", "Laboureur"), ("DUPONT_Luc_0", "Tisserand")}


def test_titre_garde_intervalle_rang_et_lieu():
    lot = _lot()
    (q,) = [q for q in lot.qualites if q.categorie == "titre"]
    assert (q.role, q.rang) == ("Comte", 2)
    assert (q.valide_debut, q.valide_fin) == (date(1750, 1, 1), date(1760, 12, 31))
    (m,) = [m for m in lot.mentions_lieu if m.qualite_ref == q.ref]
    assert (m.fonction, m.forme_ecrite) == ("titre", "Chartres")
    assert m.factoide_ref == q.factoide_ref


def test_qualite_est_portee_par_la_ligne_de_la_personne():
    lot = _lot()
    q = next(q for q in lot.qualites if q.role == "Tisserand")
    f = next(f for f in lot.factoides if f.ref == q.factoide_ref)
    p = next(p for p in lot.passages if p.ref == f.passage_ref)
    assert f.type_evenement is None
    assert (p.ligne_debut, p.ligne_fin, p.fichier_source) == (4, 4, "x.gw")


def test_un_factoide_de_qualites_par_personne():
    lot = _lot()
    cles = _cles(lot)
    par_personne: dict[str, set[str]] = {}
    for q in lot.qualites:
        par_personne.setdefault(cles[q.masque_ref], set()).add(q.factoide_ref)
    assert all(len(refs) == 1 for refs in par_personne.values())


def test_relation_rel_garde_sa_ligne_de_provenance():
    lot = _lot()
    r = next(r for r in lot.relations if r.type_relation == "parrainage")
    f = next(f for f in lot.factoides if f.ref == r.factoide_ref)
    p = next(p for p in lot.passages if p.ref == f.passage_ref)
    assert (p.ligne_debut, p.ligne_fin, p.fichier_source) == (13, 13, "x.gw")
