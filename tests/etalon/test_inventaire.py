"""Tableau d'inventaire, correspondance Socface et registre des vérifications."""

from pathlib import Path

from chronologia.etalon.inventaire import (
    charger_correspondance,
    charger_inventaire,
    charger_verifications,
    lacunes,
    resume,
)

FIX = Path(__file__).parent / "fixtures"
ENTETE = (
    "commune,service,type,annee_debut,annee_fin,cote,disponibilite,"
    "nb_vues,estimation_unites,socface,remarques,motif_lacune\n"
)
OK = "Villefictive,AD00,naissances,1872,1881,c1,en_ligne,10,20,,,\n"


def _ecrire(tmp_path, contenu, nom="inventaire.csv"):
    chemin = tmp_path / nom
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


def test_fixture_valide():
    unites, erreurs = charger_inventaire(FIX / "inventaire_synthetique.csv")
    assert erreurs == []
    assert len(unites) == 6
    assert unites[0].annee_debut == 1872 and unites[0].nb_vues == 240
    assert unites[2].nb_vues is None


def test_absent_sans_motif_est_une_erreur(tmp_path):
    ligne = "Villefictive,AD00,deces,1902,1911,,absent,,,,,\n"
    unites, erreurs = charger_inventaire(_ecrire(tmp_path, ENTETE + OK + ligne))
    assert len(unites) == 1
    assert len(erreurs) == 1
    assert "ligne 3" in erreurs[0] and "motif_lacune" in erreurs[0]


def test_annee_fin_avant_debut_est_une_erreur(tmp_path):
    ligne = "Villefictive,AD00,deces,1911,1902,c,en_ligne,,,,,\n"
    _, erreurs = charger_inventaire(_ecrire(tmp_path, ENTETE + ligne))
    assert erreurs and "annee_fin" in erreurs[0]


def test_type_inconnu_est_une_erreur(tmp_path):
    ligne = "Villefictive,AD00,ZZSENTINELLE,1872,1881,c,en_ligne,,,,,\n"
    _, erreurs = charger_inventaire(_ecrire(tmp_path, ENTETE + ligne))
    assert erreurs and "colonne type" in erreurs[0]
    assert "ZZSENTINELLE" not in " ".join(erreurs)


def test_entier_invalide_sans_valeur(tmp_path):
    ligne = "Villefictive,AD00,deces,ZZSENTINELLE,1881,c,en_ligne,,,,,\n"
    _, erreurs = charger_inventaire(_ecrire(tmp_path, ENTETE + ligne))
    assert erreurs and "annee_debut" in erreurs[0]
    assert "ZZSENTINELLE" not in " ".join(erreurs)


def test_recensement_sans_socface_est_une_erreur(tmp_path):
    ligne = "Villefictive,AD00,recensement,1872,1872,c,en_ligne,,,,,\n"
    _, erreurs = charger_inventaire(_ecrire(tmp_path, ENTETE + ligne))
    assert erreurs and "socface" in erreurs[0]


def test_colonnes_manquantes_erreur_globale(tmp_path):
    unites, erreurs = charger_inventaire(_ecrire(tmp_path, "commune,type\nV,deces\n"))
    assert unites == []
    assert len(erreurs) == 1 and erreurs[0].startswith("ligne 1 : colonnes manquantes")


def test_encodage_invalide_sans_extrait(tmp_path):
    chemin = tmp_path / "inventaire.csv"
    chemin.write_bytes(ENTETE.encode() + b"ZZSENTINELLE\xff\n")
    unites, erreurs = charger_inventaire(chemin)
    assert unites == [] and erreurs == ["encodage_invalide"]


def test_lacunes():
    unites, _ = charger_inventaire(FIX / "inventaire_synthetique.csv")
    assert [u.type for u in lacunes(unites)] == ["deces"]


def test_resume_ne_contient_ni_cote_ni_remarque():
    unites, _ = charger_inventaire(FIX / "inventaire_synthetique.csv")
    r = resume(unites)
    assert ("Villefictive", "deces", "absent", 1) in r
    assert "9 E 999" not in repr(r) and "COTE-REMARQUE-SECRETE" not in repr(r)
    assert "mairie" not in repr(r)


def test_correspondance_valide():
    lignes, erreurs = charger_correspondance(FIX / "correspondance_synthetique.csv")
    assert erreurs == [] and len(lignes) == 2 and lignes[1].vue == 4


def test_verifications_valides():
    v, erreurs = charger_verifications(FIX / "verifications_synthetique.csv")
    assert erreurs == [] and [x.statut for x in v] == ["repondu", "a_faire"]


def test_verifications_statut_inconnu_refuse(tmp_path):
    contenu = (
        "numero,service,objet,statut,date,reference,stockage_local,stockage_serveur\n"
        "1,AD00,objet,ZZSENTINELLE,,,oui,non\n"
    )
    v, erreurs = charger_verifications(_ecrire(tmp_path, contenu, "verifications.csv"))
    assert v == [] and erreurs and "statut" in erreurs[0]
    assert "ZZSENTINELLE" not in erreurs[0]
