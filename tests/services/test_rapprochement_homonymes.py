"""Service de rapprochement d'homonymes sur des bases synthétiques croisées (décision 20).

Vérifie R18 (l'agent ne fait que proposer), R24 (un rejet humain tient, rien
n'est reproposé) et R26 (faisceau calculé, degré possible ou probable).
"""

import sqlite3
from datetime import datetime, timezone

import pytest

from chronologia.persistence.propositions import CONTRIBUTEUR_APPARIEUR
from chronologia.persistence.schema import creer_schema
from chronologia.services.importation import importer_fichier_geneweb
from chronologia.services.rapprochement import proposer_rapprochements

BASE_A = """fam MARTIN Pierre + DUPONT Marie
beg
- h Jean 1680
end

fam MARTIN Jean 1680 1740 +1705 DURAND Claire
"""

# La même famille saisie par un autre auteur : homonymes compatibles.
BASE_B = """fam MARTIN Pierre + DUPONT Marie
beg
- h Jean
end

fam MARTIN Jean +1705 DURAND Claire
"""

# Un frère homonyme, né après la mort du Jean de la base A.
BASE_C = """fam MARTIN Pierre + DUPONT Marie
beg
- h Jean 1745
end
"""


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    return c


@pytest.fixture
def importer(con, tmp_path):
    def _importer(nom, texte):
        chemin = tmp_path / nom
        chemin.write_text(texte, encoding="utf-8")
        return importer_fichier_geneweb(con, chemin).lot_id

    return _importer


def _propositions(con):
    """(nom du masque, base du masque, base de la personne, degré), triés."""
    rows = con.execute(
        "SELECT m.nom_ecrit, lm.fichier, lp.fichier, i.degre"
        " FROM interp_ident_personne i"
        " JOIN interp_contributeur c ON c.id = i.contributeur_id AND c.nom = ?"
        " JOIN source_masque m ON m.id = i.masque_id"
        " JOIN source_lot_import lm ON lm.id = m.lot_id"
        " JOIN interp_personne p ON p.id = i.personne_id"
        " JOIN source_lot_import lp ON lp.id = p.lot_id",
        (CONTRIBUTEUR_APPARIEUR,),
    )
    return sorted(rows)


def _idents_agent(con):
    return [
        r[0]
        for r in con.execute(
            "SELECT i.id FROM interp_ident_personne i JOIN interp_contributeur c"
            " ON c.id = i.contributeur_id WHERE c.nom = ?",
            (CONTRIBUTEUR_APPARIEUR,),
        )
    ]


def _nb_actifs(con):
    return con.execute("SELECT COUNT(*) FROM interp_ident_personne_actif").fetchone()[0]


def test_propose_les_homonymes_compatibles(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    proposer_rapprochements(con)
    # Jean : masque de filiation (nom + parents) et de mariage (nom + conjoint) ;
    # Claire : masque de mariage. Le nom seul (Pierre, Marie) reste sous le seuil.
    assert _propositions(con) == [
        ("Claire DURAND", "base_b.gw", "base_a.gw", "possible"),
        ("Jean MARTIN", "base_b.gw", "base_a.gw", "possible"),
        ("Jean MARTIN", "base_b.gw", "base_a.gw", "possible"),
    ]


def test_rapport(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    r = proposer_rapprochements(con)
    assert r.personnes_comparees == 8
    assert r.paires_examinees == 4  # Pierre, Marie, Jean, Claire
    assert r.paires_eliminees == 0
    assert (r.propositions_possibles, r.propositions_probables) == (3, 0)
    assert r.masques_sous_seuil > 0
    assert r.couples_deja_identifies == 0


def test_r18_l_agent_ne_fait_que_proposer(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    actifs = _nb_actifs(con)
    proposer_rapprochements(con)
    assert _nb_actifs(con) == actifs
    statuts = con.execute(
        "SELECT s.statut, c.nom, c.type FROM interp_ident_personne_statut s"
        " JOIN interp_contributeur c ON c.id = s.contributeur_id"
        " WHERE s.ident_id IN (SELECT value FROM json_each(?))",
        (str(_idents_agent(con)),),
    ).fetchall()
    assert len(statuts) == 3
    assert set(statuts) == {("propose", CONTRIBUTEUR_APPARIEUR, "agent")}


def test_r26_chaque_proposition_a_son_faisceau_calcule(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    proposer_rapprochements(con)
    for ident in _idents_agent(con):
        indices = con.execute(
            "SELECT type, sens, poids, mode, regle_version FROM interp_indice"
            " WHERE ident_id = ?",
            (ident,),
        ).fetchall()
        assert indices
        assert all(mode == "calcule" and regle for _, _, _, mode, regle in indices)
    degres = {r[0] for r in con.execute("SELECT degre FROM interp_ident_personne"
                                        " WHERE id IN (SELECT value FROM json_each(?))",
                                        (str(_idents_agent(con)),))}  # fmt: skip
    assert degres <= {"possible", "probable"}


def test_indice_neutre_conserve(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    proposer_rapprochements(con)
    neutres = con.execute(
        "SELECT poids, regle_version FROM interp_indice WHERE sens = 'neutre'"
    ).fetchall()
    assert neutres and set(neutres) == {(0.0, "regle:chrono:v1")}


def test_rejouer_n_ecrit_rien(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    proposer_rapprochements(con)
    avant = _propositions(con)
    nb_indices = con.execute("SELECT COUNT(*) FROM interp_indice").fetchone()[0]
    r = proposer_rapprochements(con)
    assert _propositions(con) == avant
    assert con.execute("SELECT COUNT(*) FROM interp_indice").fetchone()[0] == nb_indices
    assert (r.propositions_possibles, r.propositions_probables) == (0, 0)
    assert r.couples_deja_identifies == 3


def test_r24_un_rejet_humain_n_est_pas_repropose(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    proposer_rapprochements(con)
    rejetee = _idents_agent(con)[0]
    with con:
        con.execute(
            "INSERT INTO interp_contributeur (nom, type) VALUES ('historien', 'humain')"
        )
        con.execute(
            "INSERT INTO interp_ident_personne_statut (ident_id, statut, contributeur_id, date)"
            " SELECT ?, 'rejete', id, ? FROM interp_contributeur WHERE nom = 'historien'",
            (rejetee, datetime.now(timezone.utc).isoformat()),
        )
    proposer_rapprochements(con)
    assert len(_idents_agent(con)) == 3
    dernier = con.execute(
        "SELECT statut FROM interp_ident_personne_statut WHERE ident_id = ?"
        " ORDER BY date DESC, id DESC LIMIT 1",
        (rejetee,),
    ).fetchone()[0]
    assert dernier == "rejete"


def test_veto_chronologique_frere_homonyme(con, importer):
    importer("base_a.gw", BASE_A)
    importer("base_c.gw", BASE_C)
    r = proposer_rapprochements(con)
    assert [p for p in _propositions(con) if p[0] == "Jean MARTIN"] == []
    assert r.paires_eliminees == 1


def test_meme_base_ignoree_par_defaut(con, importer):
    importer(
        "base_d.gw",
        BASE_A + "\nfam MARTIN Jean.1 +1705 DURAND Claire.1\n",
    )
    assert proposer_rapprochements(con).paires_examinees == 0
    assert proposer_rapprochements(con, intra_base=True).paires_examinees == 2


def test_tout_ou_rien(con, importer, monkeypatch):
    importer("base_a.gw", BASE_A)
    importer("base_b.gw", BASE_B)
    import chronologia.services.rapprochement as service

    def panne(*args, **kwargs):
        raise RuntimeError("panne simulée")

    monkeypatch.setattr(service, "ecrire_propositions", panne)
    with pytest.raises(RuntimeError):
        proposer_rapprochements(con)
    assert _propositions(con) == []
    assert (
        con.execute(
            "SELECT COUNT(*) FROM interp_contributeur WHERE nom = ?",
            (CONTRIBUTEUR_APPARIEUR,),
        ).fetchone()[0]
        == 0
    )
