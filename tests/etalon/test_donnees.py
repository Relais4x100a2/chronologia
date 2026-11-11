"""Garde-fou : les données du projet vivent hors du dépôt."""

import pytest

from chronologia.etalon import donnees
from chronologia.etalon.donnees import DonneesDansLeDepot, verifier_hors_depot


def test_chemin_hors_depot_accepte(tmp_path):
    attendu = (tmp_path / "hesdin").resolve()
    assert verifier_hors_depot(tmp_path / "hesdin", racine=tmp_path / "depot") == attendu


def test_chemin_dans_le_depot_refuse(tmp_path):
    with pytest.raises(DonneesDansLeDepot):
        verifier_hors_depot(tmp_path / "depot" / "donnees", racine=tmp_path / "depot")


def test_racine_elle_meme_refusee(tmp_path):
    with pytest.raises(DonneesDansLeDepot):
        verifier_hors_depot(tmp_path / "depot", racine=tmp_path / "depot")


def test_lien_symbolique_vers_le_depot_refuse(tmp_path):
    (tmp_path / "depot").mkdir()
    lien = tmp_path / "lien"
    lien.symlink_to(tmp_path / "depot")
    with pytest.raises(DonneesDansLeDepot):
        verifier_hors_depot(lien / "x", racine=tmp_path / "depot")


def test_racine_par_defaut_resolue_a_l_appel(tmp_path, monkeypatch):
    monkeypatch.setattr(donnees, "racine_depot", lambda: tmp_path / "depot")
    with pytest.raises(DonneesDansLeDepot):
        verifier_hors_depot(tmp_path / "depot" / "x")


def test_racine_depot_reelle_contient_pyproject():
    assert (donnees.racine_depot() / "pyproject.toml").is_file()
