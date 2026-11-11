"""Tirage stratifié rejouable, pilotes et seconde lecture."""

from collections import Counter
from pathlib import Path

import pytest

from chronologia.etalon.donnees import DonneesDansLeDepot, racine_depot
from chronologia.etalon.tirage import (
    PlanTirage,
    Tirage,
    Tire,
    ecrire_tirage,
    repartir,
    tirer,
    tirer_seconde_lecture,
    tranche_de,
    tranches,
)

FIX = Path(__file__).parent / "fixtures"
CADRE = FIX / "cadre_synthetique.csv"
CANDIDATS = FIX / "candidats_synthetique.csv"
PLAN = PlanTirage(
    commune="Villefictive", n_actes=30, pages_par_denombrement=2, n_remontee=2, n_pilote_actes=5
)
ANNEES_RECENSEMENT = [1872, 1876, 1881, 1886, 1891, 1896, 1901, 1906, 1911]


def _tirer(graine=42, plan=PLAN, cadre=CADRE, candidats=CANDIDATS):
    return tirer(cadre, candidats, plan, graine)


def _par(t, categorie):
    return [x for x in t.tires if x.categorie == categorie]


def _repartition_de(t):
    return dict(
        Counter((x.type, tranche_de(x.annee, (1872, 1911), 10)) for x in _par(t, "acte"))
    )


def test_tranches():
    assert tranches((1872, 1911), 10) == [(1872, 1881), (1882, 1891), (1892, 1901), (1902, 1911)]
    assert tranche_de(1875, (1872, 1911), 10) == "1872-1881"
    assert tranche_de(1860, (1872, 1911), 10) == "avant-1872"
    with pytest.raises(ValueError):
        tranche_de(1912, (1872, 1911), 10)


def test_repartir_proportionnel():
    # Règle (C) : 1 par strate, puis le solde (7) au plus fort reste : 4,2 / 2,1 / 0,7.
    assert repartir({("a", "1"): 60, ("b", "1"): 30, ("c", "1"): 10}, 10) == {
        ("a", "1"): 5,
        ("b", "1"): 3,
        ("c", "1"): 2,
    }


def test_repartir_minimum_un():
    assert repartir({("a", "1"): 1, ("b", "1"): 1, ("c", "1"): 98}, 10) == {
        ("a", "1"): 1,
        ("b", "1"): 1,
        ("c", "1"): 8,
    }


def test_repartir_plafond_redistribue():
    assert repartir({("a", "1"): 2, ("b", "1"): 100}, 50) == {("a", "1"): 2, ("b", "1"): 48}
    assert repartir({("a", "1"): 2, ("b", "1"): 3}, 5) == {("a", "1"): 2, ("b", "1"): 3}


def test_repartir_egalite_departagee_par_ordre():
    assert repartir({("a", "1"): 5, ("b", "1"): 5}, 3) == {("a", "1"): 2, ("b", "1"): 1}


def test_repartir_ignore_strates_vides():
    assert repartir({("a", "1"): 4, ("b", "1"): 0}, 2) == {("a", "1"): 2}


def test_repartir_strates_trop_nombreuses():
    with pytest.raises(ValueError, match="strates_trop_nombreuses"):
        repartir({("a", "1"): 5, ("b", "1"): 5, ("c", "1"): 5}, 2)


def test_repartir_population_insuffisante():
    with pytest.raises(ValueError, match="population_insuffisante"):
        repartir({("a", "1"): 2, ("b", "1"): 3}, 6)


def test_repartition_imposee_invalide_refusee():
    base = _repartition_de(_tirer())
    total_faux = dict(base)
    total_faux[next(iter(base))] += 1
    with pytest.raises(ValueError, match="repartition_total"):
        _tirer(plan=PlanTirage(**{**PLAN.__dict__, "repartition": total_faux}))
    vide = dict(base)
    cle = next(iter(base))
    vide[cle] -= 1
    vide[("mariage", "1800-1809")] = 1
    with pytest.raises(ValueError, match="repartition_strate_vide"):
        _tirer(plan=PlanTirage(**{**PLAN.__dict__, "repartition": vide}))
    trop = {("naissance", "1872-1881"): 500}
    with pytest.raises(ValueError, match="repartition_hors_effectif"):
        _tirer(plan=PlanTirage(**{**PLAN.__dict__, "n_actes": 500, "repartition": trop}))


def test_repartition_imposee_respectee():
    t = _tirer()
    imposee = _repartition_de(t)
    t2 = _tirer(plan=PlanTirage(**{**PLAN.__dict__, "repartition": imposee}))
    assert _repartition_de(t2) == imposee


def test_meme_graine_meme_csv(tmp_path):
    ecrire_tirage(_tirer(), tmp_path / "a")
    ecrire_tirage(_tirer(), tmp_path / "b")
    assert (tmp_path / "a" / "tirage.csv").read_bytes() == (tmp_path / "b" / "tirage.csv").read_bytes()
    assert (tmp_path / "a" / "tirage.meta.json").exists()


def test_graine_differente_tirage_different():
    assert _tirer(1).tires != _tirer(2).tires


def test_empreintes_changent_avec_chaque_entree(tmp_path):
    base = _tirer().empreintes
    assert set(base) == {"cadre", "candidats", "repartition", "parametres"}

    def change(t):
        return {k for k in base if base[k] != t.empreintes[k]}

    cadre = tmp_path / "cadre.csv"
    cadre.write_text(CADRE.read_text(encoding="utf-8").replace(",8,9 E 999/1", ",108,9 E 999/1", 1), encoding="utf-8")
    assert change(_tirer(cadre=cadre)) == {"cadre"}
    cand = tmp_path / "candidats.csv"
    cand.write_text(CANDIDATS.read_text(encoding="utf-8") + "Villefictive,deces,1861,2,9 E 998/3\n", encoding="utf-8")
    assert change(_tirer(candidats=cand)) == {"candidats"}
    imposee = _repartition_de(_tirer())
    assert change(_tirer(plan=PlanTirage(**{**PLAN.__dict__, "repartition": imposee}))) == {"repartition"}
    assert change(_tirer(plan=PlanTirage(**{**PLAN.__dict__, "n_actes": 31}))) == {"parametres"}


def test_annee_pilote_exclue_des_actes():
    for graine in range(5):
        t = _tirer(graine)
        pilotes = _par(t, "pilote_acte")
        assert len(pilotes) == 5 and {p.annee for p in pilotes} == {t.annee_pilote}
        assert all(a.annee != t.annee_pilote for a in _par(t, "acte"))


def test_page_pilote_exclue_mais_denombrement_complet():
    for graine in range(5):
        t = _tirer(graine)
        pages = _par(t, "recensement")
        assert Counter(p.annee for p in pages) == {a: 2 for a in ANNEES_RECENSEMENT}
        assert all((p.annee, p.rang) != t.page_pilote for p in pages)
        (pilote,) = _par(t, "pilote_recensement")
        assert (pilote.annee, pilote.rang) == t.page_pilote


def test_lacunes_declarees(tmp_path):
    t = _tirer()
    assert 1890 in t.annees_absentes and 1905 in t.annees_absentes
    assert 1903 in t.annees_absentes and 1880 not in t.annees_absentes
    cadre = tmp_path / "cadre.csv"
    texte = CADRE.read_text(encoding="utf-8").replace("Villefictive,deces,1902,1,9 E 999/3\n", "")
    cadre.write_text(texte, encoding="utf-8")
    assert ("deces", "1902-1911") in _tirer(cadre=cadre).strates_vides


def test_effectifs_du_plan():
    t = _tirer()
    compte = Counter(x.categorie for x in t.tires)
    assert compte == {
        "acte": 30,
        "recensement": 2 * len(ANNEES_RECENSEMENT),
        "remontee": 2,
        "pilote_acte": 5,
        "pilote_recensement": 1,
    }
    assert all(x.annee < 1872 for x in _par(t, "remontee"))


def test_pas_de_doublon():
    for graine in range(5):
        t = _tirer(graine)
        assert len({(x.type, x.annee, x.rang) for x in t.tires}) == len(t.tires)


def test_rangs_dans_le_registre():
    effectifs = {}
    for ligne in CADRE.read_text(encoding="utf-8").splitlines()[1:]:
        _, type_, annee, n, _ = ligne.split(",")
        effectifs[(type_, int(annee))] = int(n)
    for x in _tirer().tires:
        if x.categorie != "remontee":
            assert 1 <= x.rang <= effectifs[(x.type, x.annee)]


def test_remontee_candidat_apres_periode_refuse(tmp_path):
    cand = tmp_path / "candidats.csv"
    cand.write_text(CANDIDATS.read_text(encoding="utf-8") + "Villefictive,deces,1872,2,9 E 999/3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="remontee_hors_periode"):
        _tirer(candidats=cand)


def _tirage_factice(n_actes, n_remontee=0):
    tires = [Tire("V", "acte", "naissance", 1880, r, "c") for r in range(1, n_actes - n_remontee + 1)]
    tires += [Tire("V", "remontee", "naissance", 1860, r, "c") for r in range(1, n_remontee + 1)]
    tires += [Tire("V", "pilote_acte", "deces", 1890, 1, "c"), Tire("V", "pilote_recensement", "recensement", 1891, 1, "c")]
    return Tirage(tires=tires, annee_pilote=1890, page_pilote=(1891, 1), graine=1, empreintes={}, strates_vides=[], annees_absentes=[])


def test_seconde_lecture_plafond_superieur():
    for n, attendu in ((45, 5), (110, 11)):
        t = _tirage_factice(n, n_remontee=5)
        seconde = tirer_seconde_lecture(t, graine_seconde=7)
        assert len(seconde) == attendu and len(set(seconde)) == attendu
        assert set(seconde) <= {x for x in t.tires if x.categorie in ("acte", "remontee")}
    t = _tirage_factice(45)
    assert tirer_seconde_lecture(t, 7) == tirer_seconde_lecture(t, 7)


def test_ecrire_tirage_refuse_le_depot():
    with pytest.raises(DonneesDansLeDepot):
        ecrire_tirage(_tirer(), racine_depot() / "tirage_interdit")
    assert not (racine_depot() / "tirage_interdit").exists()
