"""Identifications initiales de l'import GeneWeb (décision 19, R9, R11, R24).

Une personne par clé GeneWeb, chaque masque de la clé rattaché par une
identification « certain » versée « actif » par le contributeur ``import_geneweb``.
Au réimport, la personne est réutilisée, les anciennes identifications sont
retirées par ``audit_retractation`` et une décision humaine divergente fait verser
les nouvelles en « proposé ».
"""

import sqlite3
from datetime import datetime, timezone

import pytest

from chronologia.persistence.identification import ecrire_identifications_import
from chronologia.persistence.schema import creer_schema
from chronologia.services.importation import importer_fichier_geneweb

V1 = """fam MARTIN Jean 1680 + DUPONT Marie 1685
beg
- h Pierre 1710
- f Anne 1712
end

fam MARTIN Pierre + DURAND Claire
beg
- h Luc 1740
end
"""

# Anne change de sexe (modification), Luc disparaît (rétractation), Rose arrive.
V2 = """fam MARTIN Jean 1680 + DUPONT Marie 1685
beg
- h Pierre 1710
- h Anne 1712
- f Rose 1715
end

fam MARTIN Pierre + DURAND Claire
"""

JEAN, ANNE, LUC, ROSE = (
    "gw:pers:MARTIN_Jean_0", "gw:pers:MARTIN_Anne_0",
    "gw:pers:MARTIN_Luc_0", "gw:pers:MARTIN_Rose_0",
)  # fmt: skip


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    creer_schema(c)
    return c


@pytest.fixture
def fichier(tmp_path):
    chemin = tmp_path / "base.gw"
    chemin.write_text(V1, encoding="utf-8")
    return chemin


def _un(con, sql, *params):
    return con.execute(sql, params).fetchone()[0]


def _cles(con, lot_id):
    rows = con.execute(
        "SELECT DISTINCT cle_externe FROM source_masque WHERE lot_id=?", (lot_id,)
    )
    return {r[0] for r in rows}


def _personne_de(con, lot_id, cle):
    """Personnes visées par les identifications des masques de la clé dans le lot."""
    rows = con.execute(
        "SELECT DISTINCT i.personne_id FROM interp_ident_personne i"
        " JOIN source_masque m ON m.id = i.masque_id"
        " WHERE m.lot_id = ? AND m.cle_externe = ?",
        (lot_id, cle),
    )
    return {r[0] for r in rows}


def _actifs(con, lot_id):
    """Couples (masque, personne) actifs pour les masques du lot."""
    rows = con.execute(
        "SELECT a.masque_id, a.personne_id FROM interp_ident_personne_actif a"
        " JOIN source_masque m ON m.id = a.masque_id WHERE m.lot_id = ?",
        (lot_id,),
    )
    return set(rows)


def _humain(con):
    con.execute(
        "INSERT OR IGNORE INTO interp_contributeur (nom, type) VALUES ('historien', 'humain')"
    )
    return _un(con, "SELECT id FROM interp_contributeur WHERE nom = 'historien'")


def _decision(con, ident_id, statut):
    with con:
        con.execute(
            "INSERT INTO interp_ident_personne_statut (ident_id, statut, contributeur_id, date)"
            " VALUES (?, ?, ?, ?)",
            (ident_id, statut, _humain(con), datetime.now(timezone.utc).isoformat()),
        )


def _idents_import(con, lot_id, cle):
    rows = con.execute(
        "SELECT i.id FROM interp_ident_personne i JOIN source_masque m ON m.id = i.masque_id"
        " JOIN interp_contributeur c ON c.id = i.contributeur_id"
        " WHERE m.lot_id = ? AND m.cle_externe = ? AND c.nom = 'import_geneweb'"
        " ORDER BY i.id",
        (lot_id, cle),
    )
    return [r[0] for r in rows]


def _reimporter(con, fichier, texte=V2):
    fichier.write_text(texte, encoding="utf-8")
    return importer_fichier_geneweb(con, fichier)


# Premier import


def test_une_personne_par_cle(con, fichier):
    r = importer_fichier_geneweb(con, fichier)
    refs = [
        row[0] for row in con.execute("SELECT ref FROM interp_personne ORDER BY ref")
    ]
    assert refs == sorted(_cles(con, r.lot_id))
    assert _un(con, "SELECT COUNT(DISTINCT lot_id) FROM interp_personne") == 1


def test_chaque_masque_actif_vers_la_personne_de_sa_cle(con, fichier):
    r = importer_fichier_geneweb(con, fichier)
    attendu = set(
        con.execute(
            "SELECT m.id, p.id FROM source_masque m JOIN interp_personne p"
            " ON p.ref = m.cle_externe WHERE m.lot_id = ?",
            (r.lot_id,),
        )
    )
    assert _actifs(con, r.lot_id) == attendu
    assert len(attendu) == _un(con, "SELECT COUNT(*) FROM source_masque")


def test_plusieurs_masques_reunis_sur_une_personne(con, fichier):
    r = importer_fichier_geneweb(con, fichier)
    pierre = "gw:pers:MARTIN_Pierre_0"
    assert (
        _un(con, "SELECT COUNT(*) FROM source_masque WHERE cle_externe = ?", pierre) > 1
    )
    assert len(_personne_de(con, r.lot_id, pierre)) == 1


def test_identifications_certaines_et_rattachees_au_lot(con, fichier):
    r = importer_fichier_geneweb(con, fichier)
    lignes = set(
        con.execute(
            "SELECT i.degre, i.lot_id, c.nom, c.type FROM interp_ident_personne i"
            " JOIN interp_contributeur c ON c.id = i.contributeur_id"
        )
    )
    assert lignes == {("certain", r.lot_id, "import_geneweb", "import")}


def test_rapport_du_premier_import(con, fichier):
    r = importer_fichier_geneweb(con, fichier)
    b = r.bilan_identification
    assert b is not None
    assert b.personnes_creees == len(_cles(con, r.lot_id))
    assert b.personnes_reutilisees == 0
    assert b.identifications_actives == _un(con, "SELECT COUNT(*) FROM source_masque")
    assert b.identifications_proposees == 0


def test_contributeur_canonique_unique(con, fichier, tmp_path):
    importer_fichier_geneweb(con, fichier)
    autre = tmp_path / "autre.gw"
    autre.write_text("fam MARTIN Jean + DUPONT Marie\n", encoding="utf-8")
    importer_fichier_geneweb(con, autre)
    assert _un(con, "SELECT COUNT(*) FROM interp_contributeur") == 1


def test_deux_bases_ne_partagent_pas_leurs_personnes(con, fichier, tmp_path):
    """Une clé GeneWeb n'est unique que dans sa base : pas de fusion entre fichiers."""
    a = importer_fichier_geneweb(con, fichier)
    autre = tmp_path / "autre.gw"
    autre.write_text("fam MARTIN Jean + DUPONT Marie\n", encoding="utf-8")
    b = importer_fichier_geneweb(con, autre)
    assert _personne_de(con, a.lot_id, JEAN).isdisjoint(
        _personne_de(con, b.lot_id, JEAN)
    )


# Idempotence


def test_reimport_identique_n_ecrit_rien(con, fichier):
    importer_fichier_geneweb(con, fichier)
    avant = [
        _un(con, f"SELECT COUNT(*) FROM {t}")
        for t in (
            "interp_personne",
            "interp_ident_personne",
            "interp_ident_personne_statut",
        )
    ]
    r = importer_fichier_geneweb(con, fichier)
    apres = [
        _un(con, f"SELECT COUNT(*) FROM {t}")
        for t in (
            "interp_personne",
            "interp_ident_personne",
            "interp_ident_personne_statut",
        )
    ]
    assert r.statut == "identique_ignore" and r.bilan_identification is None
    assert apres == avant


def test_reecrire_un_lot_deja_traite_n_ecrit_rien(con, fichier):
    r = importer_fichier_geneweb(con, fichier)
    avant = _un(con, "SELECT COUNT(*) FROM interp_ident_personne_statut")
    with con:
        b = ecrire_identifications_import(con, r.lot_id)
    assert _un(con, "SELECT COUNT(*) FROM interp_ident_personne_statut") == avant
    assert (b.personnes_creees, b.identifications_actives) == (0, 0)


# Réimport avec différentiel


def test_reimport_reutilise_les_personnes(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    b = _reimporter(con, fichier)
    for cle in (JEAN, ANNE):
        assert _personne_de(con, b.lot_id, cle) == _personne_de(con, a.lot_id, cle)
    assert _un(con, "SELECT COUNT(*) FROM interp_personne WHERE ref = ?", ROSE) == 1
    bilan = b.bilan_identification
    assert bilan is not None
    assert bilan.personnes_creees == 1  # Rose
    assert bilan.personnes_reutilisees == len(_cles(con, b.lot_id)) - 1


def test_reimport_retire_les_anciennes_identifications_par_motif(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    _reimporter(con, fichier)
    motifs = dict(
        con.execute(
            "SELECT m.cle_externe, GROUP_CONCAT(DISTINCT r.motif) FROM audit_retractation r"
            " JOIN interp_ident_personne i ON i.id = r.cible_id"
            " JOIN source_masque m ON m.id = i.masque_id"
            " WHERE r.cible_table = 'interp_ident_personne' AND m.lot_id = ?"
            " GROUP BY m.cle_externe",
            (a.lot_id,),
        )
    )
    assert motifs[JEAN] == "reconduction"
    assert motifs[ANNE] == "modification"
    assert motifs[LUC] == "retractation"
    nb_anciennes = _un(
        con,
        "SELECT COUNT(*) FROM interp_ident_personne i JOIN source_masque m"
        " ON m.id = i.masque_id WHERE m.lot_id = ?",
        a.lot_id,
    )
    assert (
        sum(
            1
            for _ in con.execute(
                "SELECT 1 FROM audit_retractation WHERE cible_table = 'interp_ident_personne'"
            )
        )
        == nb_anciennes
    )


def test_vue_active_ne_porte_que_le_lot_nouveau(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    b = _reimporter(con, fichier)
    assert _actifs(con, a.lot_id) == set()
    assert len(_actifs(con, b.lot_id)) == _un(
        con, "SELECT COUNT(*) FROM source_masque WHERE lot_id = ?", b.lot_id
    )


def test_cle_disparue_garde_sa_personne_sans_identification_active(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    _reimporter(con, fichier)
    (luc,) = _personne_de(con, a.lot_id, LUC)
    assert _un(con, "SELECT COUNT(*) FROM interp_personne WHERE id = ?", luc) == 1
    assert (
        _un(
            con,
            "SELECT COUNT(*) FROM interp_ident_personne_actif WHERE personne_id = ?",
            luc,
        )
        == 0
    )


# Primauté du chercheur (R24)


def test_rejet_humain_preserve_au_reimport(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    _decision(con, _idents_import(con, a.lot_id, JEAN)[0], "rejete")
    b = _reimporter(con, fichier)
    statuts_jean = {
        s
        for (s,) in con.execute(
            "SELECT s.statut FROM interp_ident_personne_statut s"
            " JOIN interp_ident_personne i ON i.id = s.ident_id"
            " JOIN source_masque m ON m.id = i.masque_id"
            " WHERE m.lot_id = ? AND m.cle_externe = ?",
            (b.lot_id, JEAN),
        )
    }
    assert statuts_jean == {"propose"}
    nb_jean = len(_idents_import(con, b.lot_id, JEAN))
    assert b.bilan_identification is not None
    assert b.bilan_identification.identifications_proposees == nb_jean
    pierre = _idents_import(con, b.lot_id, "gw:pers:MARTIN_Pierre_0")
    assert _un(
        con,
        "SELECT COUNT(*) FROM interp_ident_personne_actif WHERE id IN (%s)"
        % ",".join("?" * len(pierre)),
        *pierre,
    ) == len(pierre)


def test_activation_humaine_vers_une_autre_personne_preservee(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    ident = _idents_import(con, a.lot_id, ANNE)[0]
    _decision(con, ident, "rejete")
    with con:
        autre = con.execute(
            "INSERT INTO interp_personne (ref) VALUES ('P-autre')"
        ).lastrowid
        masque = _un(
            con, "SELECT masque_id FROM interp_ident_personne WHERE id = ?", ident
        )
        nouvelle = con.execute(
            "INSERT INTO interp_ident_personne (masque_id, personne_id, degre,"
            " contributeur_id, date) VALUES (?, ?, 'probable', ?, '2026-10-30')",
            (masque, autre, _humain(con)),
        ).lastrowid
    _decision(con, nouvelle, "actif")
    b = _reimporter(con, fichier)
    assert b.bilan_identification is not None
    assert b.bilan_identification.identifications_proposees == len(
        _idents_import(con, b.lot_id, ANNE)
    )


def test_accord_humain_n_empeche_pas_l_activation(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    _decision(con, _idents_import(con, a.lot_id, JEAN)[0], "actif")
    b = _reimporter(con, fichier)
    assert b.bilan_identification is not None
    assert b.bilan_identification.identifications_proposees == 0


def test_la_derniere_decision_humaine_fait_foi(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    ident = _idents_import(con, a.lot_id, JEAN)[0]
    _decision(con, ident, "rejete")
    _decision(con, ident, "actif")
    b = _reimporter(con, fichier)
    assert b.bilan_identification is not None
    assert b.bilan_identification.identifications_proposees == 0


def test_rejet_humain_persiste_sur_plusieurs_reimports(con, fichier):
    a = importer_fichier_geneweb(con, fichier)
    _decision(con, _idents_import(con, a.lot_id, JEAN)[0], "rejete")
    _reimporter(con, fichier)
    c = _reimporter(con, fichier, V1 + "\nfam MARTIN Luc + DURAND Rose\n")
    assert c.bilan_identification is not None
    assert c.bilan_identification.identifications_proposees == len(
        _idents_import(con, c.lot_id, JEAN)
    )
