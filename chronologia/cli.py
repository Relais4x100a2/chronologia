"""Ligne de commande : ``python -m chronologia importer | info-lot | rechercher``."""

import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence, Set

from chronologia.persistence.requetes import (
    rechercher_par_intervalle,
    rechercher_par_lieu,
    rechercher_par_personne,
)
from chronologia.persistence.schema import creer_schema
from chronologia.services.importation import importer_fichier_geneweb

_TABLES_DU_LOT = (
    "source_passage", "source_masque", "source_factoide", "source_qualite",
    "source_mention_lieu", "interp_evenement", "interp_conclusion",
)  # fmt: skip


def _erreur(message: str) -> int:
    print(f"erreur : {message}", file=sys.stderr)
    return 2


def _ouvrir_existante(base: Path) -> Optional[sqlite3.Connection]:
    if not base.exists():
        return None
    con = sqlite3.connect(base)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def _importer(args: argparse.Namespace) -> int:
    fichier: Path = args.fichier
    if not fichier.is_file():
        return _erreur(f"fichier introuvable : {fichier}")
    con = sqlite3.connect(args.base)
    try:
        creer_schema(con)
        r = importer_fichier_geneweb(con, fichier, args.lot_precedent)
    finally:
        con.close()
    print(f"statut      : {r.statut}")
    print(f"lot         : {r.lot_id}")
    print(f"empreinte   : {r.empreinte[:12]}")
    print(f"entités     : {r.nb_entites}")
    if r.bilan_diff is not None:
        b = r.bilan_diff
        print(
            f"différentiel : {b.reconductions} reconductions, "
            f"{b.modifications} modifications, {b.retractions} rétractations"
        )
    return 0


def _info_lot(args: argparse.Namespace) -> int:
    con = _ouvrir_existante(args.base)
    if con is None:
        return _erreur(f"base introuvable : {args.base}")
    try:
        if args.lot_id is None:
            for r in con.execute(
                "SELECT id, date_import, fichier, empreinte, nb_entites, statut"
                " FROM source_lot_import ORDER BY id"
            ):
                print(f"{r[0]:>4}  {r[1][:19]}  {r[2] or '-'}  {str(r[3])[:12]}"
                      f"  {r[4]} entités  {r[5]}")  # fmt: skip
            return 0
        lot = con.execute(
            "SELECT id, format, fichier, empreinte, outil, version, date_import,"
            " statut, nb_entites FROM source_lot_import WHERE id=?",
            (args.lot_id,),
        ).fetchone()
        if lot is None:
            return _erreur(f"lot {args.lot_id} inconnu")
        for nom, valeur in zip(
            ("lot", "format", "fichier", "empreinte", "outil", "version", "date",
             "statut", "entités"), lot):  # fmt: skip
            print(f"{nom:<10}: {valeur}")
        for table in _TABLES_DU_LOT:
            n = con.execute(
                f"SELECT COUNT(*) FROM {table} WHERE lot_id=?", (args.lot_id,)
            ).fetchone()[0]
            print(f"{table:<22}: {n}")
        n = con.execute(
            "SELECT COUNT(*) FROM audit_retractation WHERE lot_id=?", (args.lot_id,)
        ).fetchone()[0]
        print(f"{'audit_retractation':<22}: {n} (motivées par ce lot)")
    finally:
        con.close()
    return 0


def _rechercher(args: argparse.Namespace) -> int:
    if args.personne is None and args.lieu is None and args.date is None:
        return _erreur("indiquer au moins un critère : --personne, --lieu ou --date")
    con = _ouvrir_existante(args.base)
    if con is None:
        return _erreur(f"base introuvable : {args.base}")
    try:
        selections: List[Set[int]] = []
        if args.personne is not None:
            selections.append({f.id for f in rechercher_par_personne(con, args.personne)})
        if args.lieu is not None:
            selections.append({f.id for f in rechercher_par_lieu(con, args.lieu)})
        if args.date is not None:
            selections.append({
                f.id for f in rechercher_par_intervalle(
                    con, date(args.date, 1, 1), date(args.date, 12, 31)
                )
            })  # fmt: skip
        ids = sorted(set.intersection(*selections))
        for i in ids:
            f = con.execute(
                "SELECT type_evenement, date_declaree FROM source_factoide WHERE id=?", (i,)
            ).fetchone()
            lieux = [r[0] for r in con.execute(
                "SELECT forme_ecrite FROM source_mention_lieu WHERE factoide_id=?", (i,))]
            gens = [f"{r[0]} ({r[1]})" for r in con.execute(
                "SELECT m.nom_ecrit, p.role FROM source_participation p"
                " JOIN source_masque m ON m.id = p.masque_id WHERE p.factoide_id=?"
                " ORDER BY p.ordre", (i,))]  # fmt: skip
            print(f"{f[1] or '-':<12} {f[0] or '-':<12} "
                  f"{', '.join(lieux) or '-':<16} {'; '.join(gens)}")  # fmt: skip
        print(f"{len(ids)} fait(s)")
    finally:
        con.close()
    return 0


def _parseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chronologia")
    sous = p.add_subparsers(dest="commande", required=True)

    imp = sous.add_parser("importer", help="importer un fichier GeneWeb (.gw)")
    imp.add_argument("fichier", type=Path)
    imp.add_argument("--base", type=Path, required=True)
    imp.add_argument("--lot-precedent", type=int, default=None)
    imp.set_defaults(action=_importer)

    info = sous.add_parser("info-lot", help="lister les lots ou détailler l'un d'eux")
    info.add_argument("--base", type=Path, required=True)
    info.add_argument("--lot-id", type=int, default=None)
    info.set_defaults(action=_info_lot)

    rech = sous.add_parser("rechercher", help="faits actifs par personne, lieu ou année")
    rech.add_argument("--base", type=Path, required=True)
    rech.add_argument("--personne", help="clé externe, ex. gw:pers:NOM_Prenom_0")
    rech.add_argument("--lieu")
    rech.add_argument("--date", type=int, help="année")
    rech.set_defaults(action=_rechercher)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parseur().parse_args(argv)
    return int(args.action(args))


if __name__ == "__main__":
    sys.exit(main())
