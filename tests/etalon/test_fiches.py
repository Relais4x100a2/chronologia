"""Schémas versionnés et lecture sûre des fiches structurées."""

from pathlib import Path

import pytest

from chronologia.etalon.fiches import (
    charger_fiche,
    etat_valeur,
    texte_valeur,
    valider_fiche,
)

FICHES = Path(__file__).parent / "fixtures" / "fiches"
NOMS = ["acte_naissance.yaml", "acte_mariage.yaml", "page_recensement.yaml", "acte_illisible.yaml"]


def _fiche(nom="acte_naissance.yaml"):
    fiche, erreurs = charger_fiche(FICHES / nom)
    assert erreurs == [] and fiche is not None
    return fiche


def _ecrire(tmp_path, texte):
    chemin = tmp_path / "f.yaml"
    chemin.write_text(texte, encoding="utf-8")
    return chemin


@pytest.mark.parametrize("nom", NOMS)
def test_fixtures_valides(nom):
    assert valider_fiche(_fiche(nom), nom) == []


def test_role_inconnu_refuse_sans_valeur():
    fiche = _fiche()
    fiche["personnes"][0]["role"] = "ZZSENTINELLE"
    erreurs = valider_fiche(fiche, "x.yaml")
    assert erreurs == ["x.yaml : /personnes/0/role : enum"]


def test_valeur_transcrite_invalide_sans_valeur():
    fiche = _fiche()
    fiche["personnes"][1]["nom"] = {"normalise": "ZZSENTINELLE"}
    erreurs = valider_fiche(fiche, "x.yaml")
    assert erreurs and all("ZZSENTINELLE" not in e for e in erreurs)
    assert erreurs[0].startswith("x.yaml : /personnes/1/nom : ")


def test_champ_inconnu_refuse():
    fiche = _fiche()
    fiche["nom_normalise"] = "x"
    assert valider_fiche(fiche, "x.yaml") == ["x.yaml : / : additionalProperties"]


def test_kind_inconnu_refuse():
    fiche = _fiche()
    fiche["kind"] = "ZZSENTINELLE"
    assert valider_fiche(fiche, "x.yaml") == ["x.yaml : /kind : kind_inconnu"]


def test_yaml_malforme_sans_extrait(tmp_path):
    fiche, erreurs = charger_fiche(_ecrire(tmp_path, "a: 1\nnom: ZZSENTINELLE: [\n"))
    assert fiche is None
    assert len(erreurs) == 1 and erreurs[0].startswith("f.yaml : yaml_invalide (ligne ")
    assert "ZZSENTINELLE" not in erreurs[0]


def test_date_non_citee_reste_chaine(tmp_path):
    fiche, _ = charger_fiche(_ecrire(tmp_path, "d: 1872-03-05\n"))
    assert fiche == {"d": "1872-03-05"}


def test_seuls_true_false_sont_booleens(tmp_path):
    fiche, _ = charger_fiche(_ecrire(tmp_path, "a: yes\nb: No\nc: true\nd: off\n"))
    assert fiche == {"a": "yes", "b": "No", "c": True, "d": "off"}


def test_cle_dupliquee_refusee(tmp_path):
    fiche, erreurs = charger_fiche(_ecrire(tmp_path, "nom: A\nnom: ZZSENTINELLE\n"))
    assert fiche is None and erreurs == ["f.yaml : cle_dupliquee (ligne 2)"]


def test_racine_liste_refusee(tmp_path):
    fiche, erreurs = charger_fiche(_ecrire(tmp_path, "- a\n- b\n"))
    assert fiche is None and erreurs == ["f.yaml : racine_non_mapping"]


def test_rang_duplique_refuse():
    fiche = _fiche()
    fiche["personnes"][1]["rang"] = 1
    assert "x.yaml : /personnes/1/rang : rang_duplique" in valider_fiche(fiche, "x.yaml")


def test_ligne_dupliquee_refusee():
    fiche = _fiche("page_recensement.yaml")
    fiche["lignes"][2]["ligne"] = 1
    assert "x.yaml : /lignes/2/ligne : ligne_dupliquee" in valider_fiche(fiche, "x.yaml")


def test_lien_vers_rang_absent_refuse():
    fiche = _fiche()
    fiche["liens"][0]["vers"] = 99
    assert "x.yaml : /liens/0/vers : rang_inexistant" in valider_fiche(fiche, "x.yaml")


def test_etat_valeur():
    assert etat_valeur("Pierre") == "lisible"
    assert etat_valeur({"illisible": "partiel", "lu": "Mar"}) == "partiel"
    assert etat_valeur({"illisible": True}) == "illisible"
    assert etat_valeur({"absent": True}) == "absent"
    assert etat_valeur(None) == "non_applicable"


def test_texte_valeur():
    assert texte_valeur("Pierre") == "Pierre"
    assert texte_valeur({"illisible": "partiel", "lu": "Mar"}) == "Mar"
    assert texte_valeur({"illisible": True}) is None
    assert texte_valeur({"absent": True}) is None
    assert texte_valeur(None) is None
