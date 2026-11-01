"""Ligne de commande : importer, info-lot, rechercher."""

import sqlite3
from pathlib import Path

import geneweb_py
import pytest

from chronologia.cli import main

V1 = Path(geneweb_py.__file__).parents[2] / "tests/fixtures/chronologia_sample_5_7.gw"
V2 = Path(__file__).parent / "fixtures/chronologia_sample_5_7_v2.gw"


@pytest.fixture
def gw(tmp_path):
    chemin = tmp_path / "base.gw"
    chemin.write_text(V1.read_text(encoding="utf-8"), encoding="utf-8")
    return chemin


@pytest.fixture
def db(tmp_path):
    return tmp_path / "chronologia.db"


def _lancer(capsys, *args):
    code = main([str(a) for a in args])
    return code, capsys.readouterr().out


def test_importer_cree_la_base_et_resume(capsys, gw, db):
    code, sortie = _lancer(capsys, "importer", gw, "--base", db)
    assert code == 0 and db.exists()
    assert "nouveau" in sortie
    assert "entités" in sortie
    assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM source_lot_import").fetchone()[0] == 1


def test_reimport_identique_est_signale(capsys, gw, db):
    _lancer(capsys, "importer", gw, "--base", db)
    code, sortie = _lancer(capsys, "importer", gw, "--base", db)
    assert code == 0 and "identique_ignore" in sortie


def test_reimport_modifie_affiche_le_differentiel(capsys, gw, db):
    _lancer(capsys, "importer", gw, "--base", db)
    gw.write_text(V2.read_text(encoding="utf-8"), encoding="utf-8")
    code, sortie = _lancer(capsys, "importer", gw, "--base", db)
    assert code == 0 and "mis_a_jour" in sortie
    assert "rétractations" in sortie and "modifications" in sortie


def test_fichier_absent_donne_un_code_d_erreur(capsys, tmp_path, db):
    code, _ = _lancer(capsys, "importer", tmp_path / "nul.gw", "--base", db)
    assert code == 2


def test_info_lot_liste_puis_detaille(capsys, gw, db):
    _lancer(capsys, "importer", gw, "--base", db)
    code, sortie = _lancer(capsys, "info-lot", "--base", db)
    assert code == 0 and "base.gw" in sortie
    code, detail = _lancer(capsys, "info-lot", "--base", db, "--lot-id", 1)
    assert code == 0 and "source_factoide" in detail
    code, _ = _lancer(capsys, "info-lot", "--base", db, "--lot-id", 99)
    assert code == 2


def test_rechercher_par_personne_date_et_lieu(capsys, gw, db):
    _lancer(capsys, "importer", gw, "--base", db)
    _, sortie = _lancer(capsys, "rechercher", "--base", db, "--personne", "gw:pers:MARTIN_Jean_0")
    assert "naissance" in sortie and "1712" in sortie
    _, sortie = _lancer(capsys, "rechercher", "--base", db, "--date", 1712)
    assert "bapteme" in sortie
    _, sortie = _lancer(capsys, "rechercher", "--base", db, "--lieu", "Saint-Aubin")
    assert "Saint-Aubin" in sortie
    _, sortie = _lancer(
        capsys, "rechercher", "--base", db, "--personne", "gw:pers:MARTIN_Jean_0", "--date", 1790
    )
    assert "naissance" not in sortie  # critères combinés : intersection


def test_rechercher_sans_critere_est_refuse(capsys, gw, db):
    _lancer(capsys, "importer", gw, "--base", db)
    code, _ = _lancer(capsys, "rechercher", "--base", db)
    assert code == 2


def test_base_absente_est_refusee_en_lecture(capsys, tmp_path):
    code, _ = _lancer(capsys, "info-lot", "--base", tmp_path / "nul.db")
    assert code == 2


# --- rapprocher ------------------------------------------------------------

FAMILLE = """fam MARTIN Pierre + DUPONT Marie
beg
- h Jean{naissance}
end

fam MARTIN Jean{vie} +1705 DURAND Claire
"""


def _deux_bases(capsys, tmp_path, db, frere=False):
    a = tmp_path / "base_a.gw"
    a.write_text(FAMILLE.format(naissance=" 1680", vie=" 1680 1740"), encoding="utf-8")
    b = tmp_path / "base_b.gw"
    texte = (
        "fam MARTIN Pierre + DUPONT Marie\nbeg\n- h Jean 1745\nend\n"
        if frere
        else FAMILLE.format(naissance="", vie="")
    )
    b.write_text(texte, encoding="utf-8")
    _lancer(capsys, "importer", a, "--base", db)
    _lancer(capsys, "importer", b, "--base", db)


def test_rapprocher_affiche_le_bilan(capsys, tmp_path, db):
    _deux_bases(capsys, tmp_path, db)
    code, sortie = _lancer(capsys, "rapprocher", "--base", db)
    assert code == 0
    assert "personnes comparées : 8" in sortie
    assert "paires examinées    : 4" in sortie
    assert "paires éliminées    : 0" in sortie
    assert "propositions        : 0 probable(s), 3 possible(s)" in sortie
    assert "déjà identifiés     : 0" in sortie


def test_rapprocher_rejoue_sans_reproposer(capsys, tmp_path, db):
    _deux_bases(capsys, tmp_path, db)
    _lancer(capsys, "rapprocher", "--base", db)
    code, sortie = _lancer(capsys, "rapprocher", "--base", db)
    assert code == 0
    assert "propositions        : 0 probable(s), 0 possible(s)" in sortie
    assert "déjà identifiés     : 3" in sortie


def test_rapprocher_compte_le_veto(capsys, tmp_path, db):
    _deux_bases(capsys, tmp_path, db, frere=True)
    _, sortie = _lancer(capsys, "rapprocher", "--base", db)
    assert "paires éliminées    : 1" in sortie


def test_rapprocher_intra_base(capsys, tmp_path, db):
    gw = tmp_path / "base_d.gw"
    gw.write_text(
        FAMILLE.format(naissance=" 1680", vie=" 1680 1740")
        + "\nfam MARTIN Jean.1 +1705 DURAND Claire.1\n",
        encoding="utf-8",
    )
    _lancer(capsys, "importer", gw, "--base", db)
    _, sortie = _lancer(capsys, "rapprocher", "--base", db)
    assert "paires examinées    : 0" in sortie
    _, sortie = _lancer(capsys, "rapprocher", "--base", db, "--intra-base")
    assert "paires examinées    : 2" in sortie


def test_rapprocher_base_absente(capsys, db):
    code, _ = _lancer(capsys, "rapprocher", "--base", db)
    assert code == 2 and not db.exists()
