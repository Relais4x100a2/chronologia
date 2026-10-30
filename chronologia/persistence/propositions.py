"""Écriture des propositions du rapprochement d'homonymes (décision 20, R18, R24, R26).

Chaque proposition retenue devient une identification du contributeur
``apparieur_homonymes`` (agent), au statut « propose », accompagnée de son
faisceau d'indices calculés. Un couple (masque, personne) ayant déjà un
historique d'identification, quel qu'il soit, n'est jamais réécrit (R24).
L'appelant gère la transaction.
"""

import sqlite3
from typing import Iterable

from chronologia.interpretation.homonymes import Proposition

CONTRIBUTEUR_APPARIEUR = "apparieur_homonymes"


def contributeur_apparieur(con: sqlite3.Connection) -> int:
    """Identifiant du contributeur canonique du rapprochement, créé au besoin."""
    con.execute(
        "INSERT INTO interp_contributeur (nom, type) SELECT ?, 'agent'"
        " WHERE NOT EXISTS (SELECT 1 FROM interp_contributeur WHERE nom = ?)",
        (CONTRIBUTEUR_APPARIEUR, CONTRIBUTEUR_APPARIEUR),
    )
    ligne = con.execute(
        "SELECT id FROM interp_contributeur WHERE nom = ?", (CONTRIBUTEUR_APPARIEUR,)
    ).fetchone()
    return int(ligne[0])


def ecrire_propositions(
    con: sqlite3.Connection,
    propositions: Iterable[Proposition],
    contributeur_id: int,
    date: str,
) -> int:
    """Écrit les propositions hors couples déjà identifiés ; rend le nombre écrit."""
    ecrites = 0
    for p in propositions:
        if not p.indices:  # R26 : pas de proposition sans faisceau
            continue
        deja = con.execute(
            "SELECT 1 FROM interp_ident_personne WHERE masque_id = ? AND personne_id = ?",
            (p.masque_id, p.personne_id),
        ).fetchone()
        if deja:
            continue
        ident_id = con.execute(
            "INSERT INTO interp_ident_personne"
            " (masque_id, personne_id, degre, contributeur_id, lot_id, date)"
            " VALUES (?, ?, ?, ?, NULL, ?)",
            (p.masque_id, p.personne_id, p.degre, contributeur_id, date),
        ).lastrowid
        con.execute(
            "INSERT INTO interp_ident_personne_statut"
            " (ident_id, statut, contributeur_id, date) VALUES (?, 'propose', ?, ?)",
            (ident_id, contributeur_id, date),
        )
        con.executemany(
            "INSERT INTO interp_indice (ident_id, type, sens, poids, valeur_masque,"
            " valeur_personne, mode, regle_version) VALUES (?, ?, ?, ?, ?, ?, 'calcule', ?)",
            [
                (ident_id, i.type, i.sens, i.poids, i.valeur_masque,
                 i.valeur_personne, i.regle_version)
                for i in p.indices
            ],
        )  # fmt: skip
        ecrites += 1
    return ecrites
