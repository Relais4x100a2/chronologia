"""Comparaison des fiches par position : champs, rôles, détection, accord entre lectures."""

import copy
from pathlib import Path

import pytest

from chronologia.etalon.comparaison import comparer_fiches, comparer_lectures, cumuler
from chronologia.etalon.fiches import charger_fiche

FICHES = Path(__file__).parent / "fixtures" / "fiches"


def _fiche(nom="acte_naissance.yaml"):
    fiche, erreurs = charger_fiche(FICHES / nom)
    assert not erreurs and fiche is not None
    return fiche


def _machine(fiche):
    autre = copy.deepcopy(fiche)
    autre["meta"]["source"] = "machine"
    return autre


def _personne(fiche, rang):
    (p,) = [p for p in fiche["personnes"] if p["rang"] == rang]
    return p


def test_fiche_identique_tout_vrai_positif():
    etalon = _fiche()
    c = comparer_fiches(etalon, _machine(etalon))
    assert c.commune == "Villefictive" and c.source == "machine" and c.unites == 1
    assert all(x.fp == 0 and x.fn == 0 for x in c.champs.values())
    assert c.champs["personne.nom"].vp == 5 and c.champs["personne.nom"].precision == 1.0
    assert c.champs["date_acte"].vp == 1
    assert c.personnes_appariees == 5 and c.roles_corrects == 5
    assert c.personnes_manquantes == 0 and c.personnes_en_trop == 0


def test_profession_differente_fp_et_fn():
    etalon = _fiche()
    autre = _machine(etalon)
    _personne(autre, 2)["profession"] = "cordonier"
    x = comparer_fiches(etalon, autre).champs["personne.profession"]
    assert (x.vp, x.fp, x.fn) == (1, 1, 1)
    assert x.precision == 0.5 and x.rappel == 0.5


def test_espaces_et_nfc_ne_comptent_pas():
    etalon = _fiche()
    autre = _machine(etalon)
    _personne(autre, 2)["prenoms"] = "  Jean   Bapt. "
    assert comparer_fiches(etalon, autre).champs["personne.prenoms"].fp == 0


def test_illisible_et_partiel_comptes_a_part():
    etalon = _fiche()
    c = comparer_fiches(etalon, _machine(etalon))
    assert c.champs["personne.prenoms"].partiels == 1
    assert c.champs["personne.profession"].illisibles == 1
    assert c.champs["personne.prenoms"].vp == 4


def test_case_vide_remplie_par_machine_est_fp():
    etalon = _fiche()
    autre = _machine(etalon)
    _personne(autre, 4)["profession"] = "ménagère"
    x = comparer_fiches(etalon, autre).champs["personne.profession"]
    assert x.fp == 1 and x.fn == 0
    autre2 = _machine(etalon)
    del _personne(autre2, 4)["profession"]
    assert comparer_fiches(etalon, autre2).champs["personne.profession"].fp == 0


def test_non_applicable_ignore():
    etalon = _fiche("page_recensement.yaml")
    autre = _machine(etalon)
    autre["lignes"][0]["patron"] = "Imaginaire"
    x = comparer_fiches(etalon, autre).champs["ligne.patron"]
    assert (x.vp, x.fp, x.fn) == (0, 0, 0)


def test_role_inverse_pere_temoin():
    etalon = _fiche()
    autre = _machine(etalon)
    _personne(autre, 2)["role"] = "temoin"
    _personne(autre, 5)["role"] = "declarant"
    c = comparer_fiches(etalon, autre)
    assert c.personnes_appariees == 5 and c.roles_corrects == 3
    seuls = copy.deepcopy(etalon)
    seuls["personnes"] = [_personne(seuls, 2), _personne(seuls, 5)]
    seuls["liens"] = []
    autre = _machine(seuls)
    _personne(autre, 2)["role"], _personne(autre, 5)["role"] = "temoin", "declarant"
    c = comparer_fiches(seuls, autre)
    assert c.personnes_appariees == 2 and c.roles_corrects == 0


def test_personne_omise_donne_fn_sur_tous_ses_champs():
    etalon = _fiche()
    autre = _machine(etalon)
    autre["personnes"] = [p for p in autre["personnes"] if p["rang"] != 2]
    c = comparer_fiches(etalon, autre)
    assert c.personnes_manquantes == 1 and c.personnes_appariees == 4
    for champ in ("nom", "prenoms", "age", "profession", "domicile"):
        assert c.champs[f"personne.{champ}"].fn == 1, champ
    assert all(x.fp == 0 for x in c.champs.values())


def test_omission_ne_peut_pas_ameliorer_le_score():
    etalon = _fiche()
    complet = comparer_fiches(etalon, _machine(etalon)).champs["personne.nom"]
    autre = _machine(etalon)
    autre["personnes"] = []
    vide = comparer_fiches(etalon, autre).champs["personne.nom"]
    assert vide.rappel == 0.0 and vide.rappel < complet.rappel


def test_personne_en_trop_donne_fp():
    etalon = _fiche()
    autre = _machine(etalon)
    autre["personnes"].append({"rang": 9, "role": "temoin", "nom": "Ajouté", "prenoms": {"illisible": True}})
    c = comparer_fiches(etalon, autre)
    assert c.personnes_en_trop == 1
    assert c.champs["personne.nom"].fp == 1 and c.champs["personne.prenoms"].fp == 0


def test_ligne_appariee_par_position_meme_si_menage_faux():
    etalon = _fiche("page_recensement.yaml")
    autre = _machine(etalon)
    autre["lignes"][2]["menage"] = "3"
    c = comparer_fiches(etalon, autre)
    assert c.personnes_appariees == 3
    x = c.champs["ligne.menage"]
    assert (x.vp, x.fp, x.fn) == (2, 1, 1)
    assert c.champs["ligne.nom"].fp == 0


def test_accord_symetrique():
    a = _fiche()
    b = copy.deepcopy(a)
    b["meta"]["lecture"] = "seconde"
    _personne(b, 2)["profession"] = "cordonier"
    _personne(b, 3)["nom"] = {"illisible": True}
    ab, ba = comparer_lectures(a, b), comparer_lectures(b, a)
    assert ab == ba
    assert ab.desaccords_presence["personne.nom"] == 1
    assert ab.accord_exact("personne.nom") == 1.0


def test_accord_une_concordance_une_discordance_vaut_un_demi():
    a = _fiche()
    b = copy.deepcopy(a)
    _personne(b, 2)["profession"] = "cordonier"
    accord = comparer_lectures(a, b)
    assert accord.concordants["personne.profession"] == 1
    assert accord.discordants["personne.profession"] == 1
    assert accord.accord_exact("personne.profession") == 0.5
    assert accord.accord_exact("champ_inconnu") is None


def test_cumuler_somme():
    etalon = _fiche()
    c = cumuler([comparer_fiches(etalon, _machine(etalon))] * 2)
    assert c.unites == 2 and c.champs["personne.nom"].vp == 10 and c.personnes_appariees == 10


def test_cumuler_refuse_deux_communes():
    etalon = _fiche()
    ailleurs = copy.deepcopy(etalon)
    ailleurs["commune"] = "Autreville"
    with pytest.raises(ValueError, match="communes_ou_sources_melangees"):
        cumuler([comparer_fiches(etalon, _machine(etalon)), comparer_fiches(ailleurs, _machine(ailleurs))])
    seconde = copy.deepcopy(etalon)
    seconde["meta"]["lecture"] = "seconde"
    with pytest.raises(ValueError, match="communes_ou_sources_melangees"):
        cumuler([comparer_fiches(etalon, _machine(etalon)), comparer_fiches(etalon, seconde)])


def test_aucun_texte_dans_le_resultat():
    etalon = _fiche()
    autre = _machine(etalon)
    _personne(autre, 2)["nom"] = "ZZSENTINELLE"
    assert "ZZSENTINELLE" not in repr(comparer_fiches(etalon, autre))
    assert "ZZSENTINELLE" not in repr(comparer_lectures(etalon, autre))
