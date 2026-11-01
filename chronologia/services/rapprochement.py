"""Service de rapprochement d'homonymes entre bases (décision 20).

Lit les profils actifs, applique le moteur pur et écrit ses propositions en une
seule transaction : tout ou rien.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from chronologia.interpretation.homonymes import rapprocher
from chronologia.persistence.lecture_profils import couples_identifies, lire_profils
from chronologia.persistence.propositions import (
    contributeur_apparieur,
    ecrire_propositions,
)


@dataclass(frozen=True)
class RapportRapprochement:
    personnes_comparees: int
    paires_examinees: int
    paires_eliminees: int  # veto sur au moins un masque de la paire
    masques_sous_seuil: int
    couples_deja_identifies: int
    propositions_possibles: int
    propositions_probables: int


def proposer_rapprochements(
    con: sqlite3.Connection, intra_base: bool = False
) -> RapportRapprochement:
    """Propose des identifications entre homonymes compatibles ; l'humain décide (R18)."""
    con.execute("PRAGMA foreign_keys = ON")
    with con:
        profils = lire_profils(con)
        resultat = rapprocher(profils, couples_identifies(con), intra_base)
        contributeur_id = contributeur_apparieur(con)
        ecrire_propositions(
            con,
            resultat.propositions,
            contributeur_id,
            datetime.now(timezone.utc).isoformat(),
        )
    degres = [p.degre for p in resultat.propositions]
    return RapportRapprochement(
        personnes_comparees=len(profils),
        paires_examinees=resultat.paires_examinees,
        paires_eliminees=resultat.paires_eliminees,
        masques_sous_seuil=resultat.masques_sous_seuil,
        couples_deja_identifies=resultat.couples_deja_identifies,
        propositions_possibles=degres.count("possible"),
        propositions_probables=degres.count("probable"),
    )
