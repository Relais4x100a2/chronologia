"""Rapprochement d'homonymes par faisceau d'indices (décision 20, R26) : calcul pur.

Aucun accès SQL : les profils sont construits en mémoire, sur des noms fictifs.
"""

from datetime import date
from typing import Optional, Sequence

import pytest

from chronologia.interpretation.homonymes import (
    BAREME_V1,
    decider,
    evaluer_masque,
    rapprocher,
)
from chronologia.interpretation.normalisation import (
    cle_phonetique,
    normaliser,
    premier_prenom,
)
from chronologia.interpretation.profils import (
    FaitDate,
    MasqueObserve,
    NomPersonne,
    ProfilPersonne,
)
from chronologia.interpretation.regles import (
    REGLE_CHRONO,
    REGLE_ONOMASTIQUE,
    REGLE_RESEAU,
    Indice,
    regle_chrono,
    regle_onomastique,
    regle_reseau,
)

# --- Aides -----------------------------------------------------------------


def fait(role: str, annee: int, fin: Optional[int] = None) -> FaitDate:
    return FaitDate(role, date(annee, 1, 1), date(fin or annee, 12, 31))


def nom(texte: str) -> NomPersonne:
    """``"MARTIN Pierre_Jean"`` : nom puis prénoms."""
    n, _, p = texte.partition(" ")
    return NomPersonne(n, p)


def masque(
    masque_id: int,
    texte: str,
    faits: Sequence[FaitDate] = (),
    pere: Optional[str] = None,
    mere: Optional[str] = None,
    conjoints: Sequence[str] = (),
) -> MasqueObserve:
    return MasqueObserve(
        masque_id,
        nom(texte),
        tuple(faits),
        nom(pere) if pere else None,
        nom(mere) if mere else None,
        tuple(nom(c) for c in conjoints),
    )


def profil(personne_id: int, base: str, *masques: MasqueObserve) -> ProfilPersonne:
    return ProfilPersonne(personne_id, base, tuple(masques))


def sens_poids(indices: Sequence[Indice]) -> list[tuple[str, float]]:
    return [(i.sens, i.poids) for i in indices]


def pour(poids: float) -> Indice:
    return Indice("test", "pour", poids, "", "", "regle:test:v1")


def contre(poids: float) -> Indice:
    return Indice("test", "contre", poids, "", "", "regle:test:v1")


# --- Normalisation ---------------------------------------------------------


@pytest.mark.parametrize(
    ("brut", "attendu"),
    [
        ("MARTIN", "martin"),
        ("Éléonore", "eleonore"),
        ("Pierre_Jean", "pierre jean"),
        ("  Marie   Anne ", "marie anne"),
        ("D'ARGENT", "d argent"),
        ("Œudes", "oeudes"),
        ("Lætitia", "laetitia"),
        ("François", "francois"),
    ],
)
def test_normaliser(brut, attendu):
    assert normaliser(brut) == attendu


def test_premier_prenom():
    assert premier_prenom("Pierre_Jean") == "pierre"
    assert premier_prenom("") == ""


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("Philippe", "Filipe"),  # PH/F, consonne doublée
        ("DUPONT", "DUPOND"),  # finale muette
        ("Marye", "Marie"),  # Y/I
        ("Mathieu", "Matthieu"),  # TH, doublement
        ("Jacques", "Jacque"),
        ("Jehan", "Jean"),  # H muet
        ("Catherine", "Katherine"),
        ("Françoise", "Fransoise"),  # ç avant normalisation
        ("Guillaume", "Guilhaume"),
        ("Élisabeth", "Elizabeth"),
        ("Pierre_Jean", "pierre jean"),
    ],
)
def test_cle_phonetique_rapproche_les_variantes(a, b):
    assert cle_phonetique(a) == cle_phonetique(b)


@pytest.mark.parametrize(
    ("a", "b"),
    [("MARTIN", "DURAND"), ("Jean", "Jeanne"), ("Louis", "Louise"), ("Guy", "Jui")],
)
def test_cle_phonetique_distingue(a, b):
    assert cle_phonetique(a) != cle_phonetique(b)


def test_cle_phonetique_de_chaine_vide():
    assert cle_phonetique("") == ""


# --- Onomastique -----------------------------------------------------------


def test_onomastique_egalite_normalisee():
    a = profil(1, "a", masque(10, "MARTIN Éloi"))
    indices = regle_onomastique(masque(20, "Martin Eloi"), a)
    assert sens_poids(indices) == [("pour", 1.0)]
    i = indices[0]
    assert (i.type, i.regle_version) == ("onomastique", REGLE_ONOMASTIQUE)
    assert REGLE_ONOMASTIQUE == "regle:onomastique:nom_prenom:v1"
    assert (i.valeur_masque, i.valeur_personne) == ("martin eloi", "martin eloi")


def test_onomastique_variante_phonetique():
    a = profil(1, "a", masque(10, "DUPONT Philippe"))
    assert sens_poids(regle_onomastique(masque(20, "DUPOND Filipe"), a)) == [
        ("pour", 0.5)
    ]


def test_onomastique_prenom_secondaire():
    a = profil(1, "a", masque(10, "MARTIN Pierre"))
    assert sens_poids(regle_onomastique(masque(20, "MARTIN Pierre_Jean"), a)) == [
        ("pour", 0.5)
    ]


def test_onomastique_noms_sans_rapport():
    a = profil(1, "a", masque(10, "DURAND Paul"))
    assert regle_onomastique(masque(20, "MARTIN Jean"), a) == []


def test_onomastique_meme_prenom_autre_nom():
    a = profil(1, "a", masque(10, "DURAND Jean"))
    assert regle_onomastique(masque(20, "MARTIN Jean"), a) == []


# --- Chronologie -----------------------------------------------------------


def chrono(m: MasqueObserve, p: ProfilPersonne) -> list[tuple[str, float]]:
    return sens_poids(regle_chrono(m, p))


def test_chrono_fait_de_vivant_avant_la_naissance():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("ne", 1680)]))
    indices = regle_chrono(masque(20, "MARTIN Jean", [fait("epoux", 1650)]), a)
    assert sens_poids(indices) == [("contre", 2.0)]
    assert (indices[0].type, indices[0].regle_version) == ("chronologie", REGLE_CHRONO)
    assert REGLE_CHRONO == "regle:chrono:v1"
    assert "1650" in indices[0].valeur_masque
    assert "1680" in indices[0].valeur_personne


def test_chrono_naissance_apres_un_fait_de_vivant_de_la_personne():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("epoux", 1700)]))
    assert ("contre", 2.0) in chrono(masque(20, "MARTIN Jean", [fait("ne", 1750)]), a)


def test_chrono_fait_de_vivant_apres_le_deces():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("decede", 1690)]))
    assert ("contre", 2.0) in chrono(
        masque(20, "MARTIN Jean", [fait("baptise", 1700)]), a
    )


def test_chrono_fait_de_vivant_apres_l_inhumation():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("inhume", 1690)]))
    assert ("contre", 2.0) in chrono(
        masque(20, "MARTIN Jean", [fait("temoin", 1700)]), a
    )


def test_chrono_mention_posthume_ignoree():
    # « fils de feu Jean » : une mention où Jean ne tient pas un rôle de vivant.
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("decede", 1700)]))
    m = masque(20, "MARTIN Jean", [fait("sujet", 1750)])
    assert all(s != "contre" for s, _ in chrono(m, a))


def test_chrono_inhumation_dans_l_annee_du_deces():
    a = profil(
        1,
        "a",
        masque(
            10,
            "MARTIN Jean",
            [FaitDate("decede", date(1699, 12, 1), date(1699, 12, 1))],
        ),
    )
    m = masque(
        20, "MARTIN Jean", [FaitDate("inhume", date(1700, 6, 1), date(1700, 6, 1))]
    )
    assert chrono(m, a) == [("neutre", 0.0)]


def test_chrono_inhumation_trop_tardive():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("decede", 1699)]))
    assert ("contre", 2.0) in chrono(
        masque(20, "MARTIN Jean", [fait("inhume", 1702)]), a
    )


def test_chrono_ecart_de_plus_de_110_ans():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("temoin", 1650)]))
    assert chrono(masque(20, "MARTIN Jean", [fait("temoin", 1770)]), a) == [
        ("contre", 2.0)
    ]


def test_chrono_ecart_de_moins_de_110_ans():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("temoin", 1650)]))
    assert chrono(masque(20, "MARTIN Jean", [fait("temoin", 1740)]), a) == [
        ("neutre", 0.0)
    ]


def test_chrono_dates_compatibles_indice_neutre():
    a = profil(
        1, "a", masque(10, "MARTIN Jean", [fait("ne", 1680), fait("decede", 1740)])
    )
    indices = regle_chrono(masque(20, "MARTIN Jean", [fait("epoux", 1705)]), a)
    assert sens_poids(indices) == [("neutre", 0.0)]
    assert indices[0].regle_version == REGLE_CHRONO


def test_chrono_sans_date_aucun_indice():
    a = profil(1, "a", masque(10, "MARTIN Jean", [fait("ne", 1680)]))
    assert regle_chrono(masque(20, "MARTIN Jean"), a) == []
    assert (
        regle_chrono(masque(20, "MARTIN Jean", [FaitDate("ne", None, None)]), a) == []
    )


def test_chrono_personne_sans_date_aucun_indice():
    a = profil(1, "a", masque(10, "MARTIN Jean"))
    assert regle_chrono(masque(20, "MARTIN Jean", [fait("epoux", 1705)]), a) == []


# --- Réseau familial -------------------------------------------------------


def test_reseau_parents_concordants():
    a = profil(
        1, "a", masque(10, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie")
    )
    m = masque(20, "MARTIN Jean", pere="Martin Pierre", mere="DUPONT Marie")
    indices = regle_reseau(m, a)
    assert sens_poids(indices) == [("pour", 2.0)]
    assert (indices[0].type, indices[0].regle_version) == ("filiation", REGLE_RESEAU)
    assert REGLE_RESEAU == "regle:reseau:famille:v1"


def test_reseau_parents_differents():
    a = profil(
        1, "a", masque(10, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie")
    )
    m = masque(20, "MARTIN Jean", pere="MARTIN Louis", mere="DUPONT Marie")
    assert sens_poids(regle_reseau(m, a)) == [("contre", 1.5)]


def test_reseau_parent_inconnu_d_un_cote():
    a = profil(1, "a", masque(10, "MARTIN Jean", pere="MARTIN Pierre"))
    m = masque(20, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie")
    assert regle_reseau(m, a) == []


def test_reseau_parents_variante_orthographique_sans_indice():
    a = profil(
        1, "a", masque(10, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie")
    )
    m = masque(20, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPOND Marie")
    assert regle_reseau(m, a) == []


def test_reseau_meme_conjoint():
    a = profil(1, "a", masque(10, "MARTIN Jean", conjoints=["DURAND Claire"]))
    m = masque(20, "MARTIN Jean", conjoints=["DURAND Claire"])
    indices = regle_reseau(m, a)
    assert sens_poids(indices) == [("pour", 1.5)]
    assert indices[0].type == "conjoint"


def test_reseau_conjoints_differents_aucun_indice():
    a = profil(1, "a", masque(10, "MARTIN Jean", conjoints=["DURAND Claire"]))
    assert regle_reseau(masque(20, "MARTIN Jean", conjoints=["LEROY Anne"]), a) == []


# --- Barème ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("indices", "degre"),
    [
        ([pour(1.0)], None),
        ([pour(1.0), pour(1.0)], "possible"),
        ([pour(1.0), pour(2.0)], "possible"),
        ([pour(2.0), pour(1.5)], "probable"),
        ([pour(1.0), pour(2.0), pour(1.5)], "probable"),
        ([pour(9.0)], "probable"),  # jamais « certain »
        ([pour(1.0), pour(2.0), pour(1.5), contre(1.5)], "possible"),
        ([pour(1.0), pour(2.0), pour(1.5), contre(2.0)], None),  # veto
    ],
)
def test_decider(indices, degre):
    assert decider(indices).degre == degre


def test_decider_score_et_veto():
    d = decider(
        [pour(1.0), pour(2.0), Indice("t", "neutre", 0.0, "", "", "r"), contre(1.5)]
    )
    assert (d.score, d.veto) == (1.5, False)
    assert decider([pour(5.0), contre(2.0)]).veto is True


def test_bareme_v1():
    assert (BAREME_V1.veto, BAREME_V1.possible, BAREME_V1.probable) == (2.0, 2.0, 3.5)


def test_evaluer_masque_reunit_les_trois_regles():
    a = profil(
        1, "a",
        masque(10, "MARTIN Jean", [fait("ne", 1680)], pere="MARTIN Pierre", mere="DUPONT Marie"),
    )  # fmt: skip
    m = masque(
        20,
        "MARTIN Jean",
        [fait("epoux", 1705)],
        pere="MARTIN Pierre",
        mere="DUPONT Marie",
    )
    ev = evaluer_masque(m, a)
    assert {i.regle_version for i in ev.indices} == {
        REGLE_ONOMASTIQUE, REGLE_CHRONO, REGLE_RESEAU
    }  # fmt: skip
    assert (ev.score, ev.degre, ev.veto) == (3.0, "possible", False)


# --- Moteur : candidats, orientation, veto par personne ----------------------


def deux_bases() -> tuple[ProfilPersonne, ProfilPersonne]:
    """Jean de la base a (personne 1) et Jean de la base b (personne 2), compatibles."""
    a = profil(
        1, "a",
        masque(10, "MARTIN Jean", [fait("ne", 1680)]),
        masque(11, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie"),
        masque(12, "MARTIN Jean", [fait("epoux", 1705)], conjoints=["DURAND Claire"]),
    )  # fmt: skip
    b = profil(
        2, "b",
        masque(20, "MARTIN Jean", [fait("baptise", 1680)]),
        masque(21, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie"),
        masque(22, "MARTIN Jean", [fait("epoux", 1705)], conjoints=["DURAND Claire"]),
    )  # fmt: skip
    return a, b


def test_rapprocher_propose_les_masques_de_la_personne_recente():
    a, b = deux_bases()
    res = rapprocher([b, a])
    couples = {(p.masque_id, p.personne_id, p.degre) for p in res.propositions}
    # Masque 20 : nom seul (1,0) sous le seuil ; 21 : nom + parents ; 22 : nom + conjoint.
    assert couples == {(21, 1, "possible"), (22, 1, "possible")}
    assert res.paires_examinees == 1
    assert res.paires_eliminees == 0
    assert res.masques_sous_seuil == 1


def test_rapprocher_conserve_le_faisceau_complet():
    a, b = deux_bases()
    p22 = next(p for p in rapprocher([a, b]).propositions if p.masque_id == 22)
    assert sorted((i.type, i.sens) for i in p22.indices) == [
        ("chronologie", "neutre"), ("conjoint", "pour"), ("onomastique", "pour"),
    ]  # fmt: skip
    assert p22.score == 2.5


def test_rapprocher_jamais_certain():
    a = profil(
        1, "a",
        masque(10, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie", conjoints=["DURAND Claire"]),
    )  # fmt: skip
    b = profil(
        2, "b",
        masque(20, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie", conjoints=["DURAND Claire"]),
    )  # fmt: skip
    (p,) = rapprocher([a, b]).propositions
    assert (p.degre, p.score) == ("probable", 4.5)


def test_rapprocher_veto_chronologique_elimine_la_paire_entiere():
    # Même nom, mêmes parents : un frère homonyme né après la mort du premier.
    a = profil(
        1, "a",
        masque(10, "MARTIN Jean", [fait("ne", 1700), fait("decede", 1701)]),
        masque(11, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie"),
    )  # fmt: skip
    b = profil(
        2, "b",
        masque(20, "MARTIN Jean", [fait("ne", 1703)]),
        masque(21, "MARTIN Jean", pere="MARTIN Pierre", mere="DUPONT Marie"),
    )  # fmt: skip
    res = rapprocher([a, b])
    assert res.propositions == ()
    assert (res.paires_examinees, res.paires_eliminees) == (1, 1)


def test_rapprocher_ignore_une_meme_base_par_defaut():
    a, b = deux_bases()
    b = ProfilPersonne(b.personne_id, "a", b.masques)
    assert rapprocher([a, b]).paires_examinees == 0
    assert {p.masque_id for p in rapprocher([a, b], intra_base=True).propositions} == {
        21,
        22,
    }


def test_rapprocher_ne_compare_pas_des_noms_differents():
    a, _ = deux_bases()
    c = profil(
        3, "c", masque(30, "DURAND Paul", pere="MARTIN Pierre", mere="DUPONT Marie")
    )
    assert rapprocher([a, c]).paires_examinees == 0


def test_rapprocher_bloque_sur_la_cle_phonetique():
    a, _ = deux_bases()
    c = profil(
        3, "c", masque(30, "MARTTIN Jehan", pere="MARTIN Pierre", mere="DUPONT Marie")
    )
    res = rapprocher([a, c])
    assert res.paires_examinees == 1
    # Variante phonétique (0,5) + parents (2,0).
    assert [(p.masque_id, p.degre, p.score) for p in res.propositions] == [
        (30, "possible", 2.5)
    ]


def test_rapprocher_saute_les_couples_deja_identifies():
    a, b = deux_bases()
    res = rapprocher([a, b], deja_identifies={(21, 1)})
    assert {p.masque_id for p in res.propositions} == {22}
    assert res.couples_deja_identifies == 1


def test_rapprocher_trois_bases_une_paire_par_couple():
    a, b = deux_bases()
    c = ProfilPersonne(
        3,
        "c",
        tuple(
            MasqueObserve(m.masque_id + 10, m.nom, m.faits, m.pere, m.mere, m.conjoints)
            for m in b.masques
        ),
    )
    res = rapprocher([c, a, b])
    assert res.paires_examinees == 3
    # Chaque masque de la personne la plus récente vers la plus ancienne.
    assert {(p.masque_id, p.personne_id) for p in res.propositions} == {
        (21, 1), (22, 1), (31, 1), (32, 1), (31, 2), (32, 2),
    }  # fmt: skip
