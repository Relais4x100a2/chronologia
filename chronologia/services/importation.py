"""Service d'import d'un fichier GeneWeb : idempotence, persistance et différentiel."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from geneweb_py import GeneWebParser

from chronologia.adapters.geneweb.diff import comparer_lots
from chronologia.adapters.geneweb.mapper import empreinte_texte, importer_genealogie
from chronologia.persistence.depot import ecrire_lot, relire_lot
from chronologia.persistence.diff import BilanApplicationDiff, ecrire_diff

_FORMAT = "gw"  # valeur de Lot.format posée par le mapper


@dataclass(frozen=True)
class RapportExecutionImport:
    lot_id: int
    empreinte: str
    statut: str  # nouveau | identique_ignore | mis_a_jour
    nb_entites: int
    bilan_diff: Optional[BilanApplicationDiff] = None


def _lot_precedent(con: sqlite3.Connection, nom: str) -> Optional[int]:
    """Dernier lot GeneWeb écrit sous ce nom de fichier."""
    ligne = con.execute(
        "SELECT id FROM source_lot_import WHERE format=? AND fichier=?"
        " ORDER BY id DESC LIMIT 1",
        (_FORMAT, nom),
    ).fetchone()
    return int(ligne[0]) if ligne else None


def importer_fichier_geneweb(
    con: sqlite3.Connection,
    chemin_fichier: Path,
    lot_precedent_id: Optional[int] = None,
) -> RapportExecutionImport:
    """Importe un fichier ``.gw`` : lecture, idempotence, persistance, différentiel.

    Un fichier d'empreinte déjà connue n'est ni relu ni réécrit. Sinon le lot est
    écrit ; s'il existe un lot antérieur (``lot_precedent_id``, à défaut le dernier
    lot de même nom de fichier), le différentiel est appliqué. Écriture du lot et
    du différentiel forment un tout-ou-rien.
    """
    texte = chemin_fichier.read_text(encoding="utf-8")
    empreinte = empreinte_texte(texte)
    connu = con.execute(
        "SELECT id, nb_entites FROM source_lot_import WHERE format=? AND empreinte=?",
        (_FORMAT, empreinte),
    ).fetchone()
    if connu:
        return RapportExecutionImport(connu[0], empreinte, "identique_ignore", connu[1])

    lot_nouveau = importer_genealogie(
        GeneWebParser(validate=False).parse_string(texte),
        fichier=chemin_fichier.name,
        empreinte=empreinte,
    )
    precedent = lot_precedent_id or _lot_precedent(con, chemin_fichier.name)
    con.execute("PRAGMA foreign_keys = ON")
    with con:
        nouveau_id = ecrire_lot(con, lot_nouveau)
        bilan = None
        if precedent is not None:
            diff = comparer_lots(relire_lot(con, precedent), lot_nouveau)
            bilan = ecrire_diff(con, diff, precedent, nouveau_id)
    assert lot_nouveau.lot is not None
    return RapportExecutionImport(
        nouveau_id,
        empreinte,
        "nouveau" if precedent is None else "mis_a_jour",
        lot_nouveau.lot.nb_entites,
        bilan,
    )
