"""Listes d'inventaires d'archives : lecture, recherche, sous-commande, outil de mise à jour."""

import argparse
import gzip
import importlib.util
import json
from pathlib import Path

import pytest

from chronologia.ressources.commandes import ajouter_sous_commande
from chronologia.ressources.inventaires import (
    DOSSIER_DEFAUT,
    _annee,
    charger,
    charger_texte,
    normaliser,
    rechercher,
)

RACINE = Path(__file__).resolve().parents[2]
SOURCES = json.loads((DOSSIER_DEFAUT / "sources.json").read_text(encoding="utf-8"))["sources"]
COLONNES = {s["cle"]: s["colonnes"] for s in SOURCES}


def _csv(niveau: str, *lignes: dict[str, str]) -> str:
    cols = COLONNES[niveau]
    texte = ",".join(cols) + "\n"
    for ligne in lignes:
        texte += ",".join(f'"{ligne.get(c, "")}"' for c in cols) + "\n"
    return texte


AD = _csv(
    "ad",
    {"_departement": "Pas-de-Calais", "titre": "Fonds 4 E 81. Hesdin. Étude n° 81.",
     "cotes": "4 E 81/1-362", "dates": "1705-1890", "_date_debut": "1705",
     "_date_fin": "1890", "fichier": "FRAD062/ape-frad062_ir_4e_081_01.xml"},
    {"_departement": "Pas-de-Calais", "titre": "2 H - Abbaye d'Auchy-lès-Hesdin",
     "_date_debut": "1079", "_date_fin": "1765", "fichier": "FRAD062/x.xml"},
    {"_departement": "Somme", "titre": "Recensement de la population", "cotes": "6M",
     "index_lieu": "Lanchères (Somme, France)|Abbeville", "fichier": "FRAD080/r.xml"},
    {"_departement": "Somme", "titre": "Plans", "_commune": "Lanchères", "_insee": "80463",
     "_date_debut": "1971.0", "fichier": "FRAD080/p.xml"},
)  # fmt: skip
AN = _csv("an", {"fran_ir": "FRAN_IR_000001", "intitulé": "Dossiers de Légion d'honneur",
                 "cotes": "BB/33/1", "url_slv": "https://exemple/FRAN_IR_000001"})  # fmt: skip


def test_normaliser_et_annee():
    assert normaliser("Auchy-lès-HESDIN") == "auchy les hesdin"
    assert [_annee(v) for v in ("1872", "1794-01-01", "1971.0", "", "12", "19720101")] == [
        1872, 1794, 1971, None, None, None]  # fmt: skip


def test_lecture_des_deux_formes():
    ad = charger_texte("ad", AD)
    assert ad[0].service == "FRAD062" and (ad[0].debut, ad[0].fin) == (1705, 1890)
    assert ad[2].lieux == ("Lanchères (Somme, France)", "Abbeville")
    an = charger_texte("an", AN)[0]
    assert an.titre == "Dossiers de Légion d'honneur" and an.service == "FRAN"
    assert an.url.endswith("FRAN_IR_000001")


def test_lieu_en_mots_entiers_sans_accents():
    ad = charger_texte("ad", AD)
    titres = [i.titre for i in rechercher(ad, lieu="hesdin").retenus]
    assert len(titres) == 2  # « Auchy-lès-Hesdin » est gardé : au chercheur de trier
    assert len(rechercher(ad, lieu="Lancheres").retenus) == 2  # index des lieux et commune
    assert rechercher(ad, lieu="Hesd").retenus == []


def test_insee_departement_mots():
    ad = charger_texte("ad", AD)
    assert [i.titre for i in rechercher(ad, insee="80463").retenus] == ["Plans"]
    assert len(rechercher(ad, departement="pas de calais").retenus) == 2
    assert [i.cotes for i in rechercher(ad, mots="recensement").retenus] == ["6M"]


def test_periode_sans_dates_gardee_et_comptee():
    r = rechercher(charger_texte("ad", AD), departement="Somme", debut=1872, fin=1911)
    assert [i.titre for i in r.retenus] == ["Recensement de la population"]
    assert r.sans_dates == 1  # « Plans » (1971) écarté, le recensement sans dates gardé
    r = rechercher(charger_texte("ad", AD), lieu="Hesdin", debut=1800, fin=1900)
    assert [i.cotes for i in r.retenus] == ["4 E 81/1-362"]


@pytest.fixture
def dossier(tmp_path):
    (tmp_path / "ad.csv.gz").write_bytes(gzip.compress(AD.encode("utf-8")))
    (tmp_path / "an.csv.gz").write_bytes(gzip.compress(AN.encode("utf-8")))
    return tmp_path


def _lancer(capsys, *argv):
    p = argparse.ArgumentParser()
    ajouter_sous_commande(p.add_subparsers(dest="c", required=True))
    args = p.parse_args(["sources-reperer", *argv])
    return args.action(args), capsys.readouterr()


def test_sous_commande(capsys, dossier):
    code, sortie = _lancer(capsys, "--lieu", "Hesdin", "--niveau", "ad", "--niveau", "an",
                           "--dossier", str(dossier))  # fmt: skip
    assert code == 0 and "4 E 81/1-362" in sortie.out
    assert "2 inventaire(s) (ad 2, an 0)" in sortie.out
    code, sortie = _lancer(capsys, "--departement", "Somme", "--de", "1872", "--a", "1911",
                           "--niveau", "ad", "--dossier", str(dossier))  # fmt: skip
    assert "dont 1 sans dates exploitables" in sortie.out


def test_sous_commande_refuse_sans_critere_ou_sans_liste(capsys, dossier):
    assert _lancer(capsys, "--dossier", str(dossier))[0] == 2
    code, sortie = _lancer(capsys, "--lieu", "x", "--dossier", str(dossier))  # ac absent
    assert code == 2 and "ac" in sortie.err


def test_listes_du_depot_conformes_au_manifeste():
    manifeste = json.loads((DOSSIER_DEFAUT / "manifeste.json").read_text(encoding="utf-8"))
    for entree in manifeste["jeux"]:
        n = sum(1 for _ in charger(DOSSIER_DEFAUT, [entree["cle"]]))
        assert n == entree["lignes"], entree["cle"]


def _outil():
    spec = importlib.util.spec_from_file_location("maj_inventaires", RACINE / "tools/maj_inventaires.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_outil_gzip_deterministe_et_choix_de_ressource():
    m = _outil()
    assert m.gzip_deterministe(b"abc") == m.gzip_deterministe(b"abc")
    assert gzip.decompress(m.gzip_deterministe(b"abc")) == b"abc"
    jeu = {"resources": [
        {"title": "FRAD_inventaires_archivesdepartementales.csv", "format": "csv", "type": "main"},
        {"title": "FRAD_remplissage_champs.csv", "format": "csv", "type": "main"},
    ]}  # fmt: skip
    source = {"cle": "ad", "motif_titre": "inventaires.*departementales"}
    assert m.choisir_ressource(jeu, source)["title"].startswith("FRAD_inv")
    jeu["resources"].append(dict(jeu["resources"][0]))
    with pytest.raises(m.Refus):
        m.choisir_ressource(jeu, source)


def test_outil_refuse_colonnes_changees_et_baisse(monkeypatch, tmp_path):
    m = _outil()
    monkeypatch.setattr(m, "DOSSIER", tmp_path)
    contenu = b"a,b\n1,2\n"
    jeu = {"title": "t", "resources": [{"id": "r", "title": "inventaires x", "format": "csv",
                                         "type": "main", "url": "u"}]}  # fmt: skip
    monkeypatch.setattr(m, "_get", lambda url: json.dumps(jeu).encode() if "api" in url else contenu)
    source = {"cle": "x", "fichier": "x.csv.gz", "jeu_id": "j", "motif_titre": "inventaires",
              "colonnes": ["a", "c"]}  # fmt: skip
    with pytest.raises(m.Refus, match="colonnes"):
        m.traiter(source, None, False)
    source["colonnes"] = ["a", "b"]
    with pytest.raises(m.Refus, match="baisse"):
        m.traiter(source, {"sha1": "autre", "lignes": 10}, False)
    entree, octets = m.traiter(source, {"sha1": "autre", "lignes": 10}, True)
    assert entree["lignes"] == 1 and gzip.decompress(octets) == contenu
