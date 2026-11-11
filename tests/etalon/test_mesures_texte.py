"""Mesures CER et WER : micro-moyennes par commune, source, type et tranche."""

from fractions import Fraction

from chronologia.etalon.mesures_texte import (
    PaireTexte,
    mesurer_textes,
    normaliser_espaces,
)

P = (1872, 1911)


def _p(ref, hyp, commune="Villefictive", type_="naissance", annee=1875, illisible=False, source="machine"):
    return PaireTexte(commune, source, type_, annee, ref, hyp, illisible)


def _ligne(lignes, type_="*", tranche="*", commune="Villefictive"):
    (ligne,) = [x for x in lignes if (x.commune, x.type, x.tranche) == (commune, type_, tranche)]
    return ligne


def test_identique_zero():
    t = _ligne(mesurer_textes([_p("Pierre Martin, laboureur", "Pierre Martin, laboureur")], P, 10))
    assert t.cer == 0 and t.wer == 0 and t.n_unites == 1


def test_abreviation_est_une_erreur():
    t = _ligne(mesurer_textes([_p("Jean Bapt.", "Jean Baptiste")], P, 10))
    assert t.cer is not None and t.cer > 0 and t.wer == 0.5


def test_nfc_seulement():
    decompose = "Rosé"  # e + accent combinant
    assert normaliser_espaces(decompose) == "Rosé"
    assert normaliser_espaces("  a \t b\n c  ") == "a b c"
    t = _ligne(mesurer_textes([_p("Rosé  Songe", decompose + " Songe")], P, 10))
    assert t.cer == 0


def test_casse_comptee():
    t = _ligne(mesurer_textes([_p("Martin", "martin")], P, 10))
    assert t.editions_car == 1 and t.longueur_car == 6 and t.editions_mots == 1


def test_ponctuation_comptee():
    t = _ligne(mesurer_textes([_p("Martin,", "Martin")], P, 10))
    assert t.editions_car == 1


def test_micro_moyenne():
    lignes = mesurer_textes([_p("a" * 100, "a" * 90), _p("b" * 10, "c" * 10, type_="deces")], P, 10)
    t = _ligne(lignes)
    assert (t.editions_car, t.longueur_car) == (20, 110)
    assert t.cer == float(Fraction(20, 110))
    assert _ligne(lignes, "deces", "1872-1881").cer == 1.0


def test_reference_vide_comptee_a_part():
    t = _ligne(mesurer_textes([_p("", "quelque chose"), _p("abc", "abc")], P, 10))
    assert t.references_vides == 1 and t.longueur_car == 3 and t.cer == 0
    seule = _ligne(mesurer_textes([_p("   ", "x")], P, 10))
    assert seule.cer is None and seule.wer is None and seule.references_vides == 1


def test_illisible_exclu_et_compte():
    t = _ligne(mesurer_textes([_p("abc", "xyz", illisible=True), _p("abc", "abc")], P, 10))
    assert t.illisibles == 1 and t.cer == 0 and t.longueur_car == 3
    assert t.n_unites == 2


def test_communes_jamais_cumulees():
    lignes = mesurer_textes([_p("abc", "abc"), _p("abc", "xbc", commune="Autreville")], P, 10)
    etoiles = [x for x in lignes if x.type == "*"]
    assert sorted(x.commune for x in etoiles) == ["Autreville", "Villefictive"]
    assert all(x.commune in ("Autreville", "Villefictive") for x in lignes)
    assert _ligne(lignes, commune="Villefictive").cer == 0


def test_sources_separees():
    lignes = mesurer_textes([_p("abc", "abc"), _p("abc", "xbc", source="socface")], P, 10)
    assert sorted((x.source, x.cer) for x in lignes if x.type == "*") == [("machine", 0.0), ("socface", 1 / 3)]


def test_remontee_dans_tranche_avant():
    lignes = mesurer_textes([_p("abc", "abc", annee=1860)], P, 10)
    assert _ligne(lignes, "naissance", "avant-1872").n_unites == 1


def test_aucun_texte_dans_le_resultat():
    lignes = mesurer_textes([_p("ZZSENTINELLE Martin", "ZZSENTINELLE Martn")], P, 10)
    assert "ZZSENTINELLE" not in repr(lignes) and "Mart" not in repr(lignes)
