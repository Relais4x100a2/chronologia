"""Sous-commandes ``etalon-inventaire``, ``etalon-tirer`` et ``etalon-mesurer``.

Garde-fous : chaque chemin lu ou écrit passe par ``verifier_hors_depot`` ; aucune sortie ne
reprend une valeur lue (noms, cotes, remarques) ; une erreur inattendue est rendue sans valeur.
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from chronologia.etalon.comparaison import (
    Accord,
    Comparaison,
    comparer_fiches,
    comparer_lectures,
    cumuler,
)
from chronologia.etalon.donnees import DonneesDansLeDepot, verifier_hors_depot
from chronologia.etalon.fiches import Json, charger_fiche, valider_fiche
from chronologia.etalon.inventaire import (
    charger_correspondance,
    charger_inventaire,
    charger_verifications,
    lacunes,
    resume,
)
from chronologia.etalon.mesures_texte import PaireTexte, mesurer_textes
from chronologia.etalon.rapport import (
    ecrire_accord,
    ecrire_mesures_champs,
    ecrire_mesures_roles,
    ecrire_mesures_texte,
)
from chronologia.etalon.tirage import (
    COLONNES_TIRAGE,
    PlanTirage,
    Strate,
    ecrire_tirage,
    tirer,
    tirer_seconde_lecture,
)

# Un code d'erreur maison : minuscules ASCII, chiffres, ponctuation simple ; jamais une valeur lue.
_CODE = re.compile(r"[a-z0-9_ :;,/.-]+")


def _erreur(message: str) -> int:
    print(f"erreur : {message}", file=sys.stderr)
    return 2


def _protege(action: Callable[[argparse.Namespace], int]) -> Callable[[argparse.Namespace], int]:
    def enveloppe(args: argparse.Namespace) -> int:
        try:
            return action(args)
        except DonneesDansLeDepot:
            return _erreur("données dans le dépôt")
        except ValueError as e:
            message = str(e)
            return _erreur(message if _CODE.fullmatch(message) else f"valeur_invalide ({type(e).__name__})")
        except OSError as e:
            return _erreur(f"lecture_ou_ecriture_impossible ({type(e).__name__})")

    return enveloppe


# --- etalon-inventaire -------------------------------------------------------------------


def _inventaire(args: argparse.Namespace) -> int:
    dossier = verifier_hors_depot(args.donnees)
    chemin = verifier_hors_depot(dossier / "inventaire.csv")
    if not chemin.is_file():
        return _erreur("inventaire.csv absent")
    unites, erreurs = charger_inventaire(chemin)
    messages = [f"inventaire.csv : {e}" for e in erreurs]
    statuts: Counter[str] = Counter()
    correspondance = verifier_hors_depot(dossier / "correspondance_socface.csv")
    if correspondance.is_file():
        messages += [f"correspondance_socface.csv : {e}" for e in charger_correspondance(correspondance)[1]]
    verifications = verifier_hors_depot(dossier / "verifications.csv")
    if verifications.is_file():
        liste, erreurs_v = charger_verifications(verifications)
        messages += [f"verifications.csv : {e}" for e in erreurs_v]
        statuts.update(v.statut for v in liste)
    if messages:
        for m in messages:
            _erreur(m)
        return 2
    for commune, type_, disponibilite, n in resume(unites):
        print(f"{commune}\t{type_}\t{disponibilite}\t{n}")
    print(f"lacunes : {len(lacunes(unites))}")
    for statut in ("a_faire", "demande", "repondu"):
        print(f"verifications {statut} : {statuts[statut]}")
    return 0


# --- etalon-tirer ------------------------------------------------------------------------


def _charger_repartition(chemin: Path) -> dict[Strate, int]:
    with verifier_hors_depot(chemin).open(encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f))
    repartition: dict[Strate, int] = {}
    for i, ligne in enumerate(lignes, start=2):
        n = (ligne.get("n") or "").strip()
        if not n.isdigit() or not ligne.get("type") or not ligne.get("tranche"):
            raise ValueError(f"repartition_invalide : ligne {i}")
        repartition[(ligne["type"].strip(), ligne["tranche"].strip())] = int(n)
    return repartition


def _tirer(args: argparse.Namespace) -> int:
    cadre = verifier_hors_depot(args.cadre)
    remontee = verifier_hors_depot(args.remontee) if args.remontee else None
    sortie = verifier_hors_depot(args.sortie)
    plan = PlanTirage(
        commune=args.commune,
        n_actes=args.actes,
        pages_par_denombrement=args.pages_par_denombrement,
        n_remontee=args.remontee_n,
        periode=(args.periode[0], args.periode[1]),
        largeur_tranche=args.largeur_tranche,
        repartition=_charger_repartition(args.repartition) if args.repartition else None,
        n_pilote_actes=args.pilote_actes,
    )
    t = tirer(cadre, remontee, plan, args.graine)
    seconde = tirer_seconde_lecture(t, args.graine_seconde)
    ecrire_tirage(t, sortie)
    meta_chemin = verifier_hors_depot(sortie / "tirage.meta.json")
    meta = json.loads(meta_chemin.read_text(encoding="utf-8"))
    meta["graine_seconde"] = args.graine_seconde
    meta_chemin.write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with verifier_hors_depot(sortie / "seconde_lecture.csv").open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(COLONNES_TIRAGE)
        for x in sorted(seconde, key=lambda x: (x.categorie, x.type, x.annee, x.rang)):
            ecrivain.writerow((x.commune, x.categorie, x.type, x.annee, x.rang, x.cote))
    for categorie, n in sorted(Counter(x.categorie for x in t.tires).items()):
        print(f"{categorie} : {n}")
    print(f"seconde lecture : {len(seconde)}")
    print(f"annee pilote : {t.annee_pilote}")
    print(f"page pilote : {t.page_pilote[0]} p. {t.page_pilote[1]}")
    print(f"strates vides : {', '.join('/'.join(s) for s in t.strates_vides) or 'aucune'}")
    print(f"annees absentes : {', '.join(map(str, t.annees_absentes)) or 'aucune'}")
    return 0


# --- etalon-mesurer ----------------------------------------------------------------------


def _lire_fiches(dossier: Path) -> tuple[dict[str, dict[str, Json]], list[str]]:
    fiches: dict[str, dict[str, Json]] = {}
    erreurs: list[str] = []
    for chemin in sorted(verifier_hors_depot(dossier).glob("*.yaml")):
        fiche, e = charger_fiche(verifier_hors_depot(chemin))
        if fiche is not None:
            e = valider_fiche(fiche, chemin.name)
        erreurs += e
        if fiche is not None and not e:
            fiches[chemin.stem] = fiche
    return fiches, erreurs


def _vide_comme(fiche: Mapping[str, Json]) -> dict[str, Json]:
    """Fiche sans contenu de même nature : sert de pendant à une fiche non appariée."""
    liste = "lignes" if fiche.get("kind") == "page_recensement" else "personnes"
    return {"kind": fiche.get("kind"), "commune": fiche.get("commune"), liste: [], "meta": {}}


def _type_unite(fiche: Mapping[str, Json]) -> str:
    return "recensement" if fiche.get("kind") == "page_recensement" else str(fiche.get("type_acte"))


def _illisible(fiche: Mapping[str, Json]) -> bool:
    meta = fiche.get("meta")
    return isinstance(meta, dict) and meta.get("illisible") is True


def _lire_texte(dossier: Path | None, nom: str) -> str | None:
    if dossier is None:
        return None
    chemin = verifier_hors_depot(dossier / f"{nom}.txt")
    return chemin.read_text(encoding="utf-8") if chemin.is_file() else None


def _mesurer(args: argparse.Namespace) -> int:
    sortie = verifier_hors_depot(args.sortie)
    textes_etalon = verifier_hors_depot(args.textes_etalon) if args.textes_etalon else None
    textes_autre = verifier_hors_depot(args.textes_autre) if args.textes_autre else None
    etalon, erreurs_e = _lire_fiches(args.etalon)
    autre, erreurs_a = _lire_fiches(args.autre)
    if erreurs_e or erreurs_a:
        for m in erreurs_e + erreurs_a:
            _erreur(m)
        return 2
    seconde = args.source == "seconde_lecture"
    sans_pendant = len(set(etalon) ^ set(autre))
    comparaisons: dict[str, list[Comparaison]] = {}
    accords: dict[str, Accord] = {}
    for nom in sorted(set(etalon) | set(autre)):
        e, a = etalon.get(nom), autre.get(nom)
        if seconde:
            if e is not None and a is not None:
                _cumuler_accord(accords.setdefault(str(e.get("commune")), Accord()), comparer_lectures(e, a))
            continue
        ref = e if e is not None else _vide_comme(a or {})
        hyp = a if a is not None else _vide_comme(ref)
        c = comparer_fiches(ref, hyp)
        c.source = args.source
        comparaisons.setdefault(c.commune, []).append(c)
    paires = [
        PaireTexte(
            commune=str(fiche.get("commune")),
            source=args.source,
            type=_type_unite(fiche),
            annee=an if isinstance(an := fiche.get("annee"), int) else 0,
            reference=ref_texte,
            hypothese=_lire_texte(textes_autre, nom) or "",
            illisible=_illisible(fiche),
        )
        for nom, fiche in sorted(etalon.items())
        if (ref_texte := _lire_texte(textes_etalon, nom)) is not None
    ]
    for commune, liste in sorted(comparaisons.items()):
        total = cumuler(liste)
        ecrire_mesures_champs(total, sortie / commune / args.source / "mesures_champs.csv")
        ecrire_mesures_roles(total, sortie / commune / args.source / "mesures_roles.csv")
    for commune, accord in sorted(accords.items()):
        ecrire_accord(accord, commune, sortie / commune / "seconde_lecture" / "accord.csv")
    lignes = mesurer_textes(paires, (args.periode[0], args.periode[1]), args.largeur_tranche)
    for commune in sorted({x.commune for x in lignes}):
        ecrire_mesures_texte(
            [x for x in lignes if x.commune == commune], sortie / commune / args.source / "mesures_texte.csv"
        )
    print(f"fiches etalon : {len(etalon)} ; fiches comparees : {len(autre)} ; sans pendant : {sans_pendant}")
    print(f"textes mesures : {len(paires)}")
    return 0


def _cumuler_accord(total: Accord, a: Accord) -> None:
    for cible, source in (
        (total.concordants, a.concordants),
        (total.discordants, a.discordants),
        (total.desaccords_presence, a.desaccords_presence),
    ):
        for cle, n in source.items():
            cible[cle] = cible.get(cle, 0) + n


# --- branchement -------------------------------------------------------------------------


def _periode(p: argparse.ArgumentParser) -> None:
    p.add_argument("--periode", type=int, nargs=2, default=[1872, 1911], metavar=("DEBUT", "FIN"))
    p.add_argument("--largeur-tranche", type=int, default=10)


def ajouter_sous_commandes(sous: Any) -> None:
    """Ajoute les trois sous-commandes de l'étalon au sous-parseur de ``chronologia``."""
    inv = sous.add_parser("etalon-inventaire", help="valider l'inventaire d'une commune (agrégats)")
    inv.add_argument("--donnees", type=Path, required=True, help="dossier de la commune, hors dépôt")
    inv.set_defaults(action=_protege(_inventaire))

    tir = sous.add_parser("etalon-tirer", help="tirer l'étalon (graines obligatoires)")
    tir.add_argument("--cadre", type=Path, required=True)
    tir.add_argument("--remontee", type=Path, default=None, help="candidats de remontée")
    tir.add_argument("--commune", required=True)
    tir.add_argument("--actes", type=int, required=True)
    tir.add_argument("--pages-par-denombrement", type=int, required=True)
    tir.add_argument("--remontee-n", type=int, default=0)
    tir.add_argument("--pilote-actes", type=int, default=5)
    tir.add_argument("--graine", type=int, required=True)
    tir.add_argument("--graine-seconde", type=int, required=True)
    tir.add_argument("--repartition", type=Path, default=None, help="CSV type,tranche,n")
    tir.add_argument("--sortie", type=Path, required=True)
    _periode(tir)
    tir.set_defaults(action=_protege(_tirer))

    mes = sous.add_parser("etalon-mesurer", help="mesurer une source contre l'étalon (agrégats)")
    mes.add_argument("--etalon", type=Path, required=True)
    mes.add_argument("--autre", type=Path, required=True)
    mes.add_argument("--source", choices=("machine", "socface", "seconde_lecture"), required=True)
    mes.add_argument("--textes-etalon", type=Path, default=None)
    mes.add_argument("--textes-autre", type=Path, default=None)
    mes.add_argument("--sortie", type=Path, required=True)
    _periode(mes)
    mes.set_defaults(action=_protege(_mesurer))
