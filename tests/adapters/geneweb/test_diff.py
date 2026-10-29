"""Différentiel de deux lots d'un même corpus (5.8, étape 6)."""

from pathlib import Path

import geneweb_py
import pytest
from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb import importer_genealogie
from chronologia.adapters.geneweb.diff import comparer_lots

V1 = Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
V2 = Path(__file__).parents[2] / "fixtures/chronologia_sample_5_7_v2.gw"


def _lot(chemin: Path):
    texte = chemin.read_text(encoding="utf-8")
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(texte),
        fichier=chemin.name,
        empreinte=chemin.name,  # empreintes distinctes, contenu fictif
    )


@pytest.fixture(scope="module")
def diff():
    return comparer_lots(_lot(V1), _lot(V2))


def _cles(ecarts, genre):
    return {e.cle for e in ecarts if e.genre == genre}


def test_nouvel_enfant_est_un_ajout_de_personne_et_de_naissance(diff):
    assert _cles(diff.ajouts, "personne") == {"gw:pers:MARTIN_Anne_0"}
    assert any(
        e.genre == "factoide" and e.nouveau.type_evenement == "naissance"
        and e.nouveau.date_brute == "1714"
        for e in diff.ajouts
    )


def test_date_de_bapteme_precisee_est_une_modification(diff):
    (mod,) = [
        e for e in diff.modifications
        if e.genre == "factoide" and e.nouveau.type_evenement == "bapteme"
    ]
    assert (mod.ancien.date_brute, mod.nouveau.date_brute) == ("3/3/1712", "4/3/1712")
    assert "date" in mod.champs and "participants" not in mod.champs


def test_deces_supprime_est_une_retraction_qui_garde_l_ancien_fait(diff):
    (ret,) = [e for e in diff.retractions if e.genre == "factoide"]
    assert ret.ancien.type_evenement == "deces" and ret.nouveau is None
    assert ret.ancien.date_brute == "~1790"


def test_faits_inchanges_sont_invariants_malgre_le_decalage_des_lignes(diff):
    types = {e.nouveau.type_evenement for e in diff.invariants if e.genre == "factoide"}
    assert {"mariage", "naissance"} <= types
    assert _cles(diff.invariants, "personne") >= {"gw:pers:MARTIN_Jean_0"}


def test_lot_compare_a_lui_meme_n_a_que_des_invariants():
    lot = _lot(V1)
    d = comparer_lots(lot, lot)
    assert not (d.ajouts or d.modifications or d.retractions) and d.invariants


def test_comparaison_pure_les_lots_ne_changent_pas():
    a, b = _lot(V1), _lot(V2)
    avant = (a.factoides, a.masques, b.factoides)
    comparer_lots(a, b)
    assert avant == (a.factoides, a.masques, b.factoides)


def _lot_notes(*notes: str):
    corps = "".join(f"notes MARTIN Jean\nbeg\n{n}\nend notes\n\n" for n in notes)
    texte = "fam MARTIN Pierre +1705 DUBOIS Marie\nbeg\n- h Jean 1712\nend\n\n" + corps
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(texte), empreinte=str(hash(texte))
    )


def _concl(ecarts):
    return [e for e in ecarts if e.genre == "conclusion"]


def test_note_identique_est_invariante():
    d = comparer_lots(_lot_notes("Marchand drapier."), _lot_notes("Marchand drapier."))
    (e,) = _concl(d.invariants)
    assert e.cle.startswith("gw:pers:MARTIN_Jean_0") and not _concl(d.modifications)


def test_note_modifiee_garde_ancien_et_nouveau_texte():
    d = comparer_lots(_lot_notes("Marchand drapier."), _lot_notes("Marchand de laine."))
    (e,) = _concl(d.modifications)
    assert (e.ancien.argument, e.nouveau.argument) == (
        "Marchand drapier.",
        "Marchand de laine.",
    )
    assert e.champs == ("argument",)


def test_note_ajoutee_et_note_retiree():
    vide = _lot_notes()
    avec = _lot_notes("Marchand drapier.")
    (aj,) = _concl(comparer_lots(vide, avec).ajouts)
    assert aj.nouveau.argument == "Marchand drapier."
    (ret,) = _concl(comparer_lots(avec, vide).retractions)
    assert ret.ancien.argument == "Marchand drapier." and ret.nouveau is None


def _lot_wnote(texte_note: str):
    texte = (
        "pevt MARTIN Jean\n#bapt 1712\nwit m: LEROY Paul\n"
        f"wnote {texte_note}\nend pevt\n"
    )
    return importer_genealogie(
        GeneWebParser(validate=False).parse_string(texte), empreinte=texte_note
    )


def test_wnote_devient_note_de_la_participation_du_temoin():
    lot = _lot_wnote("Parrain venu de Chartres")
    notes = [p.note for p in lot.participations if p.note]
    assert notes == ["Parrain venu de Chartres"]


def test_wnote_modifiee_est_une_modification_de_factoide():
    d = comparer_lots(_lot_wnote("Parrain de Chartres"), _lot_wnote("Parrain de Dreux"))
    assert [e.champs for e in d.modifications if e.genre == "factoide"] == [
        ("participants",)
    ]
