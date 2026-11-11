"""Sous-commandes etalon-inventaire, etalon-tirer et etalon-mesurer."""

import csv
import json
import shutil
from pathlib import Path

import pytest
import yaml

from chronologia import cli
from chronologia.etalon import donnees

FIX = Path(__file__).parent / "fixtures"
FICHES = FIX / "fiches"
NOMS_FICTIFS = ["Imaginaire", "Fictif", "Anatole", "Inventée", "Chimère", "Songe", "cordonnier", "Désiré"]
ENTETE = "# taux sur l'échantillon tiré, non redressés ; voir tirage.meta.json"


@pytest.fixture(autouse=True)
def depot(tmp_path, monkeypatch):
    racine = tmp_path / "depot"
    racine.mkdir()
    monkeypatch.setattr(donnees, "racine_depot", lambda: racine)
    return racine


def _commune(dossier):
    dossier.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIX / "inventaire_synthetique.csv", dossier / "inventaire.csv")
    shutil.copy(FIX / "correspondance_synthetique.csv", dossier / "correspondance_socface.csv")
    shutil.copy(FIX / "verifications_synthetique.csv", dossier / "verifications.csv")
    return dossier


def _fiches(dossier, noms, source="etalon", modifier=None):
    dossier.mkdir(parents=True, exist_ok=True)
    for nom in noms:
        fiche = yaml.safe_load((FICHES / nom).read_text(encoding="utf-8"))
        fiche["meta"]["source"] = source
        if modifier:
            modifier(nom, fiche)
        (dossier / nom).write_text(yaml.safe_dump(fiche, allow_unicode=True), encoding="utf-8")
    return dossier


def _tirer_args(sortie, **kw):
    args = [
        "etalon-tirer", "--cadre", str(FIX / "cadre_synthetique.csv"),
        "--remontee", str(FIX / "candidats_synthetique.csv"), "--commune", "Villefictive",
        "--actes", "30", "--pages-par-denombrement", "2", "--remontee-n", "2",
        "--graine", "42", "--graine-seconde", "7", "--sortie", str(sortie),
    ]  # fmt: skip
    for k, v in kw.items():
        args += [f"--{k.replace('_', '-')}", str(v)]
    return args


def _lire_csv(chemin):
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    assert lignes[0] == ENTETE
    return list(csv.DictReader(lignes[1:]))


def _tout_le_texte(dossier):
    return "".join(p.read_text(encoding="utf-8") for p in dossier.rglob("*") if p.is_file())


def test_inventaire_ok_code_0(tmp_path, capsys):
    code = cli.main(["etalon-inventaire", "--donnees", str(_commune(tmp_path / "v"))])
    out = capsys.readouterr().out
    assert code == 0
    assert "lacunes : 1" in out and "a_faire : 1" in out and "repondu : 1" in out
    assert "9 E 999" not in out and "COTE-REMARQUE-SECRETE" not in out


def test_inventaire_absent_sans_motif_code_2(tmp_path, capsys):
    dossier = _commune(tmp_path / "v")
    texte = (dossier / "inventaire.csv").read_text(encoding="utf-8").replace("registres restés en mairie", "")
    (dossier / "inventaire.csv").write_text(texte, encoding="utf-8")
    assert cli.main(["etalon-inventaire", "--donnees", str(dossier)]) == 2
    err = capsys.readouterr().err
    assert "inventaire.csv : ligne 5 : colonne motif_lacune : obligatoire" in err


def test_inventaire_sans_fichier_code_2(tmp_path, capsys):
    (tmp_path / "vide").mkdir()
    assert cli.main(["etalon-inventaire", "--donnees", str(tmp_path / "vide")]) == 2
    assert "inventaire.csv absent" in capsys.readouterr().err


def test_tirer_ecrit_les_trois_fichiers(tmp_path, capsys):
    sortie = tmp_path / "tirage"
    assert cli.main(_tirer_args(sortie)) == 0
    assert {p.name for p in sortie.iterdir()} == {"tirage.csv", "tirage.meta.json", "seconde_lecture.csv"}
    meta = json.loads((sortie / "tirage.meta.json").read_text(encoding="utf-8"))
    assert meta["graine"] == 42 and meta["graine_seconde"] == 7
    seconde = list(csv.DictReader((sortie / "seconde_lecture.csv").open(encoding="utf-8")))
    assert len(seconde) == 4  # ceil(0,10 × 32)
    out = capsys.readouterr().out
    assert "acte : 30" in out and "annee pilote :" in out and "annees absentes :" in out


def test_tirer_repartition_imposee(tmp_path):
    rep = tmp_path / "rep.csv"
    rep.write_text("type,tranche,n\nnaissance,1872-1881,1\nmariage,1882-1891,1\n", encoding="utf-8")
    sortie = tmp_path / "t"
    assert cli.main(_tirer_args(sortie, actes=2, repartition=rep)) == 0
    tires = list(csv.DictReader((sortie / "tirage.csv").open(encoding="utf-8")))
    assert sorted(t["type"] for t in tires if t["categorie"] == "acte") == ["mariage", "naissance"]


def test_tirer_code_erreur_sans_valeur(tmp_path, capsys):
    assert cli.main(_tirer_args(tmp_path / "t", actes=100000)) == 2
    assert "population_insuffisante" in capsys.readouterr().err


def test_tirer_sans_graine_refuse(tmp_path):
    args = _tirer_args(tmp_path / "t")
    i = args.index("--graine")
    with pytest.raises(SystemExit):
        cli.main(args[:i] + args[i + 2 :])
    j = args.index("--graine-seconde")
    with pytest.raises(SystemExit):
        cli.main(args[:j] + args[j + 2 :])


def _mesurer(tmp_path, etalon, autre, source="machine", *extra):
    sortie = tmp_path / "mesures"
    code = cli.main(
        ["etalon-mesurer", "--etalon", str(etalon), "--autre", str(autre), "--source", source,
         "--sortie", str(sortie), *extra]
    )  # fmt: skip
    return code, sortie


def test_mesurer_fichier_sans_pendant_compte_en_fn(tmp_path, capsys):
    etalon = _fiches(tmp_path / "e", ["acte_naissance.yaml", "acte_mariage.yaml"])
    autre = _fiches(tmp_path / "a", ["acte_naissance.yaml"], source="machine")
    code, sortie = _mesurer(tmp_path, etalon, autre)
    assert code == 0
    lignes = {r["champ"]: r for r in _lire_csv(sortie / "Villefictive" / "machine" / "mesures_champs.csv")}
    assert (lignes["personne.nom"]["vp"], lignes["personne.nom"]["fn"]) == ("5", "3")
    roles = _lire_csv(sortie / "Villefictive" / "machine" / "mesures_roles.csv")
    assert roles[0]["personnes_manquantes"] == "3" and roles[0]["unites"] == "2"
    assert "sans pendant : 1" in capsys.readouterr().out


def test_mesurer_fiche_invalide_code_2_sans_valeur(tmp_path, capsys):
    def casser(nom, fiche):
        fiche["personnes"][0]["role"] = "ZZSENTINELLE"

    etalon = _fiches(tmp_path / "e", ["acte_naissance.yaml"])
    autre = _fiches(tmp_path / "a", ["acte_naissance.yaml"], source="machine", modifier=casser)
    code, sortie = _mesurer(tmp_path, etalon, autre)
    out, err = capsys.readouterr()
    assert code == 2
    assert "acte_naissance.yaml : /personnes/0/role : enum" in err
    assert "ZZSENTINELLE" not in out + err
    assert not sortie.exists() or "ZZSENTINELLE" not in _tout_le_texte(sortie)


def test_mesurer_seconde_lecture_produit_accord(tmp_path):
    def relire(nom, fiche):
        fiche["meta"]["lecture"] = "seconde"
        fiche["personnes"][1]["profession"] = "cordonier"

    etalon = _fiches(tmp_path / "e", ["acte_naissance.yaml", "acte_mariage.yaml"])
    seconde = _fiches(tmp_path / "s", ["acte_naissance.yaml"], modifier=relire)
    code, sortie = _mesurer(tmp_path, etalon, seconde, "seconde_lecture")
    assert code == 0
    dossier = sortie / "Villefictive" / "seconde_lecture"
    assert not (dossier / "mesures_champs.csv").exists()
    lignes = {r["champ"]: r for r in _lire_csv(dossier / "accord.csv")}
    assert lignes["personne.profession"]["accord_exact"] == "0.5000"


def test_mesurer_textes(tmp_path):
    etalon = _fiches(tmp_path / "e", ["acte_naissance.yaml", "acte_illisible.yaml"])
    autre = _fiches(tmp_path / "a", ["acte_naissance.yaml", "acte_illisible.yaml"], source="machine")
    te, ta = tmp_path / "te", tmp_path / "ta"
    te.mkdir()
    ta.mkdir()
    (te / "acte_naissance.txt").write_text("Paul Désiré Fictif", encoding="utf-8")
    (ta / "acte_naissance.txt").write_text("Paul Desiré Fictif", encoding="utf-8")
    (te / "acte_illisible.txt").write_text("xx", encoding="utf-8")
    code, sortie = _mesurer(
        tmp_path, etalon, autre, "machine", "--textes-etalon", str(te), "--textes-autre", str(ta)
    )
    assert code == 0
    lignes = _lire_csv(sortie / "Villefictive" / "machine" / "mesures_texte.csv")
    (total,) = [r for r in lignes if r["type"] == "*"]
    assert total["editions_car"] == "1" and total["illisibles"] == "1" and total["n_unites"] == "2"


def test_sortie_sans_donnee_nominative(tmp_path, capsys):
    def varier(nom, fiche):
        liste = "lignes" if fiche["kind"] == "page_recensement" else "personnes"
        fiche[liste][1]["nom"] = "Fictive"

    etalon = _fiches(tmp_path / "e", ["acte_naissance.yaml", "acte_mariage.yaml", "page_recensement.yaml"])
    autre = _fiches(tmp_path / "a", ["acte_naissance.yaml", "page_recensement.yaml"], "machine", varier)
    te, ta = tmp_path / "te", tmp_path / "ta"
    te.mkdir()
    ta.mkdir()
    (te / "acte_naissance.txt").write_text("Anatole Imaginaire maire, Jean Fictif cordonnier", encoding="utf-8")
    (ta / "acte_naissance.txt").write_text("Anatole Imaginaire maire, Jean Fictive cordonier", encoding="utf-8")
    code, sortie = _mesurer(tmp_path, etalon, autre, "machine", "--textes-etalon", str(te), "--textes-autre", str(ta))
    assert code == 0
    out, err = capsys.readouterr()
    tout = out + err + _tout_le_texte(sortie)
    for nom in NOMS_FICTIFS:
        assert nom not in tout, nom


@pytest.mark.parametrize("commande", ["etalon-inventaire", "etalon-tirer", "etalon-mesurer"])
def test_chaque_sous_commande_refuse_le_depot(tmp_path, depot, capsys, commande):
    if commande == "etalon-inventaire":
        args = ["etalon-inventaire", "--donnees", str(_commune(depot / "v"))]
    elif commande == "etalon-tirer":
        args = _tirer_args(depot / "t")
    else:
        etalon = _fiches(tmp_path / "e", ["acte_naissance.yaml"])
        args = ["etalon-mesurer", "--etalon", str(etalon), "--autre", str(etalon), "--source", "machine",
                "--sortie", str(depot / "m")]  # fmt: skip
    assert cli.main(args) == 2
    assert "erreur : données dans le dépôt" in capsys.readouterr().err
    assert not (depot / "t").exists() and not (depot / "m").exists()


def test_sortie_existante_lien_vers_depot_refusee(tmp_path, depot, capsys):
    cible = depot / "cible"
    cible.mkdir()
    lien = tmp_path / "lien"
    lien.symlink_to(cible)
    assert cli.main(_tirer_args(lien)) == 2
    assert "données dans le dépôt" in capsys.readouterr().err
    assert list(cible.iterdir()) == []
