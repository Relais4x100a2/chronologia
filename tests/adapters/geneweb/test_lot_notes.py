"""LOT_IMPORT, clés externes stables, réimport idempotent et notes."""

import hashlib
from datetime import datetime, timezone

import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import LotDejaImporte, importer_genealogie

# Fictif.
TEXTE = """\
fam DUPONT Paul +1750 MARTIN Anne
comm Mariage contesté
src BMS Chartres
beg
- h Luc
end

pevt DUPONT Luc
#bapt 3/3/1751 #p Chartres
note Acte lisible
end pevt

notes DUPONT Paul
beg
Laboureur aisé.
end notes
"""
MAINTENANT = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)


def _lot(**kw):
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(TEXTE),
        fichier="x.gw",
        empreinte=hashlib.sha256(TEXTE.encode()).hexdigest(),
        maintenant=MAINTENANT,
        **kw,
    )


def test_lot_porte_fichier_empreinte_date_et_effectif():
    lot = _lot()
    l = lot.lot
    assert (l.format, l.fichier, l.statut) == ("gw", "x.gw", "actif")
    assert l.empreinte == hashlib.sha256(TEXTE.encode()).hexdigest()
    assert l.date == MAINTENANT
    assert l.nb_entites == (
        len(lot.passages) + len(lot.masques) + len(lot.factoides)
        + len(lot.participations) + len(lot.relations) + len(lot.evenements)
        + len(lot.ident_evenements) + len(lot.qualites) + len(lot.mentions_lieu)
        + len(lot.conclusions)
    )


def test_cles_externes_stables_et_prefixees():
    lot = _lot()
    assert {m.cle_externe for m in lot.masques} >= {"gw:pers:DUPONT_Paul_0"}
    court = lot.lot.empreinte[:12]
    for p in lot.passages:
        assert p.cle_externe == f"gw:pass:{court}:{p.ligne_debut}_{p.ligne_fin}"


def test_reimport_du_meme_fichier_est_refuse():
    empreinte = _lot().lot.empreinte
    with pytest.raises(LotDejaImporte) as e:
        _lot(lots_connus={empreinte})
    assert e.value.empreinte == empreinte


def test_note_d_evenement_et_comm_vont_dans_la_transcription():
    lot = _lot()
    transcriptions = {p.transcription for p in lot.passages if p.transcription}
    assert transcriptions == {"Acte lisible", "Mariage contesté"}


def test_note_de_personne_devient_une_conclusion_sur_le_masque():
    lot = _lot()
    (c,) = lot.conclusions
    assert c.argument == "Laboureur aisé."
    m = next(m for m in lot.masques if m.ref == c.cible_masque_ref)
    assert m.cle_externe == "gw:pers:DUPONT_Paul_0"
    assert c.valeur is None


def test_factoides_de_famille_portent_une_cle_deterministe():
    lot = _lot()
    cles = {f.cle_famille for f in lot.factoides if f.cle_famille}
    assert cles == {"gw:fam:DUPONT_Paul_0__MARTIN_Anne_0"}
    types = {f.type_evenement for f in lot.factoides if f.cle_famille}
    assert types == {"mariage", None}  # mariage + filiation
    assert all(f.cle_famille is None for f in lot.factoides if f.type_evenement == "bapteme")


def test_parent_inconnu_donne_inconnu():
    g = GeneWebParser(validate=False).parse_string("fam DUPONT Paul +1750 #mp Chartres ? ?\n")
    lot = importer_genealogie(g, fichier="y.gw")
    assert {f.cle_famille for f in lot.factoides if f.cle_famille} == {
        "gw:fam:DUPONT_Paul_0__inconnu"
    }
