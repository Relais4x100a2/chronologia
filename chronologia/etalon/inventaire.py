"""Tableau d'inventaire (§8.2), correspondance Socface ↔ vues et registre des vérifications.

Un manque se saisit comme lacune motivée (décision 39) : ``motif_lacune`` est obligatoire
quand ``disponibilite = absent``.
"""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from chronologia.etalon._csv import (
    Ligne,
    ValeurInvalide,
    charger,
    choix,
    entier,
    entier_ou_vide,
    texte,
)

COLONNES_INVENTAIRE = (
    "commune", "service", "type", "annee_debut", "annee_fin", "cote", "disponibilite",
    "nb_vues", "estimation_unites", "socface", "remarques", "motif_lacune",
)  # fmt: skip
TYPES = (
    "naissances", "mariages", "deces", "nmd", "tables_decennales",
    "recensement", "publications", "inscription_maritime",
)  # fmt: skip
DISPONIBILITES = ("en_ligne", "salle_lecture", "absent")
SOCFACE = ("oui", "non", "partiel")
COLONNES_CORRESPONDANCE = ("commune", "annee", "page_socface", "cote", "vue")
COLONNES_VERIFICATIONS = (
    "numero", "service", "objet", "statut", "date", "reference",
    "stockage_local", "stockage_serveur",
)  # fmt: skip
STATUTS = ("a_faire", "demande", "repondu")
OUI_NON = ("oui", "non", "inconnu")


@dataclass(frozen=True)
class UniteInventaire:
    commune: str
    service: str
    type: str
    annee_debut: int
    annee_fin: int
    cote: str
    disponibilite: str
    nb_vues: int | None
    estimation_unites: int | None
    socface: str
    remarques: str
    motif_lacune: str


@dataclass(frozen=True)
class CorrespondanceSocface:
    commune: str
    annee: int
    page_socface: str
    cote: str
    vue: int


@dataclass(frozen=True)
class Verification:
    numero: int
    service: str
    objet: str
    statut: str
    date: str
    reference: str
    stockage_local: str
    stockage_serveur: str


def _unite(ligne: Ligne) -> UniteInventaire:
    type_ = choix(ligne, "type", TYPES)
    debut, fin = entier(ligne, "annee_debut"), entier(ligne, "annee_fin")
    if fin < debut:
        raise ValeurInvalide("annee_fin", "avant_annee_debut")
    disponibilite = choix(ligne, "disponibilite", DISPONIBILITES)
    socface = choix(ligne, "socface", SOCFACE, vide_permis=type_ != "recensement")
    motif = texte(ligne, "motif_lacune", obligatoire=disponibilite == "absent")
    return UniteInventaire(
        commune=texte(ligne, "commune"),
        service=texte(ligne, "service"),
        type=type_,
        annee_debut=debut,
        annee_fin=fin,
        cote=texte(ligne, "cote", obligatoire=disponibilite != "absent"),
        disponibilite=disponibilite,
        nb_vues=entier_ou_vide(ligne, "nb_vues"),
        estimation_unites=entier_ou_vide(ligne, "estimation_unites"),
        socface=socface,
        remarques=texte(ligne, "remarques", obligatoire=False),
        motif_lacune=motif,
    )


def _correspondance(ligne: Ligne) -> CorrespondanceSocface:
    return CorrespondanceSocface(
        commune=texte(ligne, "commune"),
        annee=entier(ligne, "annee"),
        page_socface=texte(ligne, "page_socface"),
        cote=texte(ligne, "cote"),
        vue=entier(ligne, "vue"),
    )


def _verification(ligne: Ligne) -> Verification:
    return Verification(
        numero=entier(ligne, "numero"),
        service=texte(ligne, "service"),
        objet=texte(ligne, "objet"),
        statut=choix(ligne, "statut", STATUTS),
        date=texte(ligne, "date", obligatoire=False),
        reference=texte(ligne, "reference", obligatoire=False),
        stockage_local=choix(ligne, "stockage_local", OUI_NON),
        stockage_serveur=choix(ligne, "stockage_serveur", OUI_NON),
    )


def charger_inventaire(chemin: Path) -> tuple[list[UniteInventaire], list[str]]:
    return charger(chemin, COLONNES_INVENTAIRE, _unite)


def charger_correspondance(chemin: Path) -> tuple[list[CorrespondanceSocface], list[str]]:
    return charger(chemin, COLONNES_CORRESPONDANCE, _correspondance)


def charger_verifications(chemin: Path) -> tuple[list[Verification], list[str]]:
    return charger(chemin, COLONNES_VERIFICATIONS, _verification)


def lacunes(unites: Sequence[UniteInventaire]) -> list[UniteInventaire]:
    return [u for u in unites if u.disponibilite == "absent"]


def resume(unites: Sequence[UniteInventaire]) -> list[tuple[str, str, str, int]]:
    """Agrégats seulement : (commune, type, disponibilité, nombre d'unités), triés."""
    compte = Counter((u.commune, u.type, u.disponibilite) for u in unites)
    return sorted((c, t, d, n) for (c, t, d), n in compte.items())
