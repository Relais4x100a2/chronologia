"""Sous-commande ``sources-reperer`` : chercher des fonds dans les listes d'inventaires."""

import argparse
import sys
from collections import Counter
from pathlib import Path

from chronologia.ressources.inventaires import DOSSIER_DEFAUT, NIVEAUX, charger, rechercher


def _reperer(args: argparse.Namespace) -> int:
    if not any((args.lieu, args.insee, args.departement, args.mots)):
        print("erreur : indiquer au moins --lieu, --insee, --departement ou --mots",
              file=sys.stderr)  # fmt: skip
        return 2
    niveaux = args.niveau or list(NIVEAUX)
    manquants = [n for n in niveaux if not (args.dossier / f"{n}.csv.gz").is_file()]
    if manquants:
        print(f"erreur : liste(s) absente(s) dans {args.dossier} : {', '.join(manquants)} "
              "(lancer python3 tools/maj_inventaires.py)", file=sys.stderr)  # fmt: skip
        return 2
    r = rechercher(
        charger(args.dossier, niveaux), lieu=args.lieu, insee=args.insee,
        departement=args.departement, mots=args.mots, debut=args.de, fin=args.a,
    )  # fmt: skip
    for inv in r.retenus[: args.limite]:
        dates = inv.dates.strip() or "s.d."
        ou = inv.departement or "Arch. nationales"
        print(f"{inv.niveau}  {inv.service:<11} {ou[:18]:<18} {dates[:14]:<14} "
              f"{inv.cotes.strip()[:22]:<22} {inv.titre[:90]}")  # fmt: skip
        if args.detail:
            print(f"      {inv.url or inv.identifiant}")
    par_niveau = Counter(inv.niveau for inv in r.retenus)
    detail = ", ".join(f"{n} {par_niveau[n]}" for n in niveaux)
    print(f"{len(r.retenus)} inventaire(s) ({detail})")
    if len(r.retenus) > args.limite:
        print(f"affichés : {args.limite} (option --limite)")
    if r.sans_dates:
        print(f"dont {r.sans_dates} sans dates exploitables, gardés faute de pouvoir trancher")
    return 0


def ajouter_sous_commande(sous: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p = sous.add_parser(
        "sources-reperer",
        help="repérer des fonds dans les inventaires d'archives (AN, AD, AC ; data.gouv.fr)",
    )
    p.add_argument("--lieu", help="commune ou lieu, en mots entiers, sans souci d'accents")
    p.add_argument("--insee", help="code INSEE exact (listes ad et ac)")
    p.add_argument("--departement", help="ex. Pas-de-Calais (listes ad et ac)")
    p.add_argument("--mots", help="mots du titre, des cotes ou du producteur")
    p.add_argument("--de", type=int, help="année de début de la période")
    p.add_argument("--a", type=int, help="année de fin de la période")
    p.add_argument("--niveau", action="append", choices=NIVEAUX,
                   help="an, ad ou ac (répétable ; défaut : les trois)")  # fmt: skip
    p.add_argument("--limite", type=int, default=200)
    p.add_argument("--detail", action="store_true", help="afficher l'adresse ou le fichier EAD")
    p.add_argument("--dossier", type=Path, default=DOSSIER_DEFAUT, help=argparse.SUPPRESS)
    p.set_defaults(action=_reperer)
