"""CSV d'agrégats des mesures : comptes et taux seulement, jamais un texte transcrit.

Chaque fichier commence par une ligne fixe rappelant que les taux décrivent l'échantillon
tiré, non redressés par les poids du tirage (R29 : un comptage montre ses hypothèses).
"""

import csv
from collections.abc import Iterable, Sequence
from pathlib import Path

from chronologia.etalon.comparaison import Accord, Comparaison
from chronologia.etalon.donnees import verifier_hors_depot
from chronologia.etalon.mesures_texte import LigneMesureTexte

ENTETE = "# taux sur l'échantillon tiré, non redressés ; voir tirage.meta.json"


def _taux(x: float | None) -> str:
    return "" if x is None else f"{x:.4f}"


def _ecrire(chemin: Path, colonnes: Sequence[str], lignes: Iterable[Sequence[object]]) -> None:
    chemin = verifier_hors_depot(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="") as f:
        f.write(ENTETE + "\n")
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(colonnes)
        ecrivain.writerows(lignes)


def ecrire_mesures_champs(c: Comparaison, chemin: Path) -> None:
    _ecrire(
        chemin,
        ("commune", "source", "champ", "vp", "fp", "fn", "partiels", "illisibles", "inventes", "precision", "rappel"),
        (
            (c.commune, c.source, nom, x.vp, x.fp, x.fn, x.partiels, x.illisibles, x.inventes, _taux(x.precision), _taux(x.rappel))
            for nom, x in sorted(c.champs.items())
        ),
    )


def ecrire_mesures_roles(c: Comparaison, chemin: Path) -> None:
    taux_roles = c.roles_corrects / c.personnes_appariees if c.personnes_appariees else None
    _ecrire(
        chemin,
        ("commune", "source", "unites", "personnes_appariees", "roles_corrects", "taux_roles",
         "personnes_manquantes", "personnes_en_trop"),
        [(c.commune, c.source, c.unites, c.personnes_appariees, c.roles_corrects, _taux(taux_roles),
          c.personnes_manquantes, c.personnes_en_trop)],
    )  # fmt: skip


def ecrire_accord(a: Accord, commune: str, chemin: Path) -> None:
    champs = sorted(set(a.concordants) | set(a.discordants) | set(a.desaccords_presence))
    _ecrire(
        chemin,
        ("commune", "source", "champ", "concordants", "discordants", "desaccords_presence", "accord_exact"),
        (
            (commune, "seconde_lecture", nom, a.concordants.get(nom, 0), a.discordants.get(nom, 0),
             a.desaccords_presence.get(nom, 0), _taux(a.accord_exact(nom)))
            for nom in champs
        ),
    )  # fmt: skip


def ecrire_mesures_texte(lignes: Sequence[LigneMesureTexte], chemin: Path) -> None:
    if len({(x.commune, x.source) for x in lignes}) > 1:
        raise ValueError("communes_ou_sources_melangees")
    _ecrire(
        chemin,
        ("commune", "source", "type", "tranche", "n_unites", "editions_car", "longueur_car",
         "editions_mots", "longueur_mots", "cer", "wer", "references_vides", "illisibles"),
        (
            (x.commune, x.source, x.type, x.tranche, x.n_unites, x.editions_car, x.longueur_car,
             x.editions_mots, x.longueur_mots, _taux(x.cer), _taux(x.wer), x.references_vides, x.illisibles)
            for x in lignes
        ),
    )  # fmt: skip
