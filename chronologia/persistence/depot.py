"""Écriture d'un lot d'import dans la base SQLite (atomique, insertion seule)."""

import sqlite3
from datetime import datetime
from typing import Dict, Optional

from chronologia.adapters.geneweb.mapper import LotImport


class LotDejaPersiste(Exception):
    """Un lot de même format et de même empreinte est déjà en base."""

    def __init__(self, empreinte: str) -> None:
        super().__init__(f"lot déjà persisté (empreinte {empreinte})")
        self.empreinte = empreinte


def _iso(valeur: object) -> Optional[str]:
    return valeur.isoformat() if valeur is not None else None  # type: ignore[attr-defined]


def persister_lot(con: sqlite3.Connection, lot_import: LotImport) -> int:
    """Persiste un lot complet en une seule transaction ; retourne l'id du lot.

    Tout ou rien : une erreur en cours d'écriture annule toutes les lignes.

    Raises:
        LotDejaPersiste: même format et même empreinte déjà en base.
        ValueError: le lot n'a pas de métadonnées de provenance.
    """
    lot = lot_import.lot
    if lot is None:
        raise ValueError("LotImport sans métadonnées de provenance (lot)")
    con.execute("PRAGMA foreign_keys = ON")
    with con:
        if lot.empreinte is not None and con.execute(
            "SELECT 1 FROM source_lot_import WHERE format=? AND empreinte=?",
            (lot.format, lot.empreinte),
        ).fetchone():
            raise LotDejaPersiste(lot.empreinte)
        lot_id = con.execute(
            "INSERT INTO source_lot_import (format, fichier, empreinte, outil, version,"
            " date_import, statut, nb_entites) VALUES (?,?,?,?,?,?,?,?)",
            (lot.format, lot.fichier, lot.empreinte, lot.outil, lot.version,
             lot.date.isoformat(), lot.statut, lot.nb_entites),
        ).lastrowid  # fmt: skip
        assert lot_id is not None

        def inserer(sql: str, valeurs: tuple) -> int:  # type: ignore[type-arg]
            return con.execute(sql, valeurs).lastrowid or 0

        passages: Dict[str, int] = {
            p.ref: inserer(
                "INSERT INTO source_passage (lot_id, ref, citation_brute, fichier_source,"
                " ligne_debut, ligne_fin, transcription, cle_externe)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (lot_id, p.ref, p.citation_brute, p.fichier_source, p.ligne_debut,
                 p.ligne_fin, p.transcription, p.cle_externe),
            )
            for p in lot_import.passages
        }  # fmt: skip
        masques: Dict[str, int] = {
            m.ref: inserer(
                "INSERT INTO source_masque (lot_id, ref, passage_id, nom_ecrit, sexe,"
                " cle_externe) VALUES (?,?,?,?,?,?)",
                (lot_id, m.ref, passages[m.passage_ref], m.nom_ecrit, m.sexe,
                 m.cle_externe),
            )
            for m in lot_import.masques
        }  # fmt: skip
        factoides: Dict[str, int] = {
            f.ref: inserer(
                "INSERT INTO source_factoide (lot_id, ref, passage_id, type_evenement,"
                " date_declaree, date_brute, date_min, date_max, calendrier,"
                " date_incertaine, cle_famille) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (lot_id, f.ref, passages[f.passage_ref], f.type_evenement,
                 f.date_declaree, f.date_brute, _iso(f.date_min), _iso(f.date_max),
                 f.calendrier, int(f.date_incertaine), f.cle_famille),
            )
            for f in lot_import.factoides
        }  # fmt: skip
        qualites: Dict[str, int] = {
            q.ref: inserer(
                "INSERT INTO source_qualite (lot_id, ref, factoide_id, masque_id,"
                " categorie, role, valide_debut, valide_fin, rang)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (lot_id, q.ref, factoides[q.factoide_ref], masques[q.masque_ref],
                 q.categorie, q.role, _iso(q.valide_debut), _iso(q.valide_fin), q.rang),
            )
            for q in lot_import.qualites
        }  # fmt: skip
        for ml in lot_import.mentions_lieu:
            inserer(
                "INSERT INTO source_mention_lieu (lot_id, ref, factoide_id,"
                " forme_ecrite, forme_normalisee, fonction, masque_id, qualite_id,"
                " epoque_designation) VALUES (?,?,?,?,?,?,?,?,?)",
                (lot_id, ml.ref, factoides[ml.factoide_ref], ml.forme_ecrite,
                 ml.forme_normalisee, ml.fonction,
                 masques[ml.masque_ref] if ml.masque_ref else None,
                 qualites[ml.qualite_ref] if ml.qualite_ref else None,
                 ml.epoque_designation),
            )  # fmt: skip
        for p in lot_import.participations:
            inserer(
                "INSERT INTO source_participation (factoide_id, masque_id, role, ordre,"
                " note) VALUES (?,?,?,?,?)",
                (factoides[p.factoide_ref], masques[p.masque_ref], p.role, p.ordre,
                 p.note),
            )  # fmt: skip
        for r in lot_import.relations:
            inserer(
                "INSERT INTO source_relation (factoide_id, sujet_masque_id,"
                " objet_masque_id, type_relation, orientation, degre)"
                " VALUES (?,?,?,?,?,?)",
                (factoides[r.factoide_ref], masques[r.sujet_masque_ref],
                 masques[r.objet_masque_ref], r.type_relation, r.orientation, r.degre),
            )  # fmt: skip
        evenements: Dict[str, int] = {
            e.ref: inserer(
                "INSERT INTO interp_evenement (lot_id, ref) VALUES (?,?)",
                (lot_id, e.ref),
            )
            for e in lot_import.evenements
        }
        for i in lot_import.ident_evenements:
            inserer(
                "INSERT INTO interp_ident_evenement (factoide_id, evenement_id, degre,"
                " statut) VALUES (?,?,?,?)",
                (factoides[i.factoide_ref], evenements[i.evenement_ref], i.degre,
                 i.statut),
            )  # fmt: skip
        for c in lot_import.conclusions:
            inserer(
                "INSERT INTO interp_conclusion (lot_id, ref, cible_masque_id, argument,"
                " valeur) VALUES (?,?,?,?,?)",
                (lot_id, c.ref, masques[c.cible_masque_ref], c.argument, c.valeur),
            )
    return lot_id


def retracter_factoide(
    con: sqlite3.Connection,
    lot_origine_id: int,
    factoide_ref: str,
    motif: str,
    lot_id: Optional[int] = None,
    maintenant: Optional[datetime] = None,
) -> int:
    """Retire un factoïde du suivi actif sans le supprimer (R10) ; retourne l'id de la rétractation.

    ``factoide_ref`` est cherché dans le lot ``lot_origine_id`` qui l'a écrit ;
    ``lot_id`` est le lot dont le différentiel motive la rétractation (par défaut,
    le lot d'origine).

    Raises:
        KeyError: aucun factoïde de ce lot n'a cette référence.
    """
    ligne = con.execute(
        "SELECT id FROM source_factoide WHERE lot_id=? AND ref=?",
        (lot_origine_id, factoide_ref),
    ).fetchone()
    if ligne is None:
        raise KeyError(factoide_ref)
    with con:
        return con.execute(
            "INSERT INTO audit_retractation (cible_table, cible_id, lot_id, motif,"
            " date_retractation) VALUES ('source_factoide', ?, ?, ?, ?)",
            (ligne[0], lot_id or lot_origine_id, motif, (maintenant or datetime.now()).isoformat()),
        ).lastrowid or 0
