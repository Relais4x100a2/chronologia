"""Repérage de sources dans les listes d'inventaires d'archives (data.gouv.fr).

Trois listes copiées dans ``ressources/inventaires-archives/`` et tenues à jour
par ``tools/maj_inventaires.py`` : Archives nationales (``an``), archives
départementales (``ad``) et communales (``ac``) publiées sur FranceArchives.

Ce module sert au repérage (chantier 1 du projet Hesdin, et tout autre terrain) :
quels fonds parlent d'une commune, sur quelle période. Il ne crée aucun fait ni
aucune information de la couche Source (R2) : un inventaire n'est pas un passage.
Les listes ne décrivent que le niveau haut de chaque instrument de recherche
(``<archdesc>``) ; l'absence d'une commune ne prouve pas l'absence de sources.
"""

from __future__ import annotations

import csv
import gzip
import io
import re
import sys
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

DOSSIER_DEFAUT = Path(__file__).resolve().parents[2] / "ressources" / "inventaires-archives"
NIVEAUX = ("an", "ad", "ac")

csv.field_size_limit(sys.maxsize)

_FRANCEARCHIVES = re.compile(r"^(FRA[CD]\d+)/")


@dataclass(frozen=True)
class Inventaire:
    niveau: str  # an | ad | ac
    identifiant: str  # FRAN_IR_… ou chemin du fichier EAD sur FranceArchives
    service: str  # FRAN, FRAD062, FRAC080001…
    departement: str
    commune: str
    insee: str
    titre: str
    cotes: str
    dates: str
    debut: int | None
    fin: int | None
    producteur: str
    lieux: tuple[str, ...] = field(default=())
    url: str = ""


def normaliser(texte: str) -> str:
    """Minuscules sans accents, ponctuation réduite à des espaces."""
    t = unicodedata.normalize("NFKD", texte)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^0-9a-z]+", " ", t).split())


def _annee(valeur: str) -> int | None:
    """Année sur 3 ou 4 chiffres en tête (« 1794 », « 1794-01-01 », « 1872.0 »)."""
    m = re.match(r"^\s*(\d{3,4})(?!\d)", valeur or "")
    return int(m.group(1)) if m else None


def _ligne(niveau: str, r: dict[str, str]) -> Inventaire:
    if niveau == "an":
        return Inventaire(
            niveau="an", identifiant=r["fran_ir"], service="FRAN", departement="",
            commune="", insee="", titre=(r["titre"] or r["intitulé"]).strip(),
            cotes=r["cotes"], dates=r["dates"], debut=_annee(r["date_debut"]),
            fin=_annee(r["date_fin"]), producteur=r["producteur"], url=r["url_slv"],
        )  # fmt: skip
    m = _FRANCEARCHIVES.match(r["fichier"])
    return Inventaire(
        niveau=niveau, identifiant=r["fichier"], service=m.group(1) if m else "",
        departement=r["_departement"], commune=r["_commune"], insee=r["_insee"],
        titre=" ".join((r["titre"] or r["intitule"]).split()), cotes=r["cotes"],
        dates=r["dates"], debut=_annee(r["_date_debut"]), fin=_annee(r["_date_fin"]),
        producteur=r["producteur"],
        lieux=tuple(x for x in r["index_lieu"].split("|") if x),
    )  # fmt: skip


def charger(
    dossier: Path = DOSSIER_DEFAUT, niveaux: Iterable[str] = NIVEAUX
) -> Iterator[Inventaire]:
    for niveau in niveaux:
        chemin = dossier / f"{niveau}.csv.gz"
        with gzip.open(chemin, "rt", encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                yield _ligne(niveau, r)


def charger_texte(niveau: str, texte: str) -> list[Inventaire]:
    """Lecture d'un CSV non compressé (tests, fichiers téléchargés à la main)."""
    return [_ligne(niveau, r) for r in csv.DictReader(io.StringIO(texte, newline=""))]


@dataclass
class Resultat:
    retenus: list[Inventaire]
    sans_dates: int  # retenus malgré l'absence de dates exploitables (R24)


def rechercher(
    inventaires: Iterable[Inventaire],
    *,
    lieu: str | None = None,
    insee: str | None = None,
    departement: str | None = None,
    mots: str | None = None,
    debut: int | None = None,
    fin: int | None = None,
) -> Resultat:
    """Filtre les inventaires. Tous les critères donnés doivent être satisfaits.

    - ``lieu`` : le nom (normalisé, en mots entiers) figure dans la commune, le
      titre ou l'index des lieux. « Hesdin » trouve donc aussi « Vieil-Hesdin » :
      au chercheur de trier, rien n'est écarté pour lui.
    - ``insee`` : code exact (listes ad et ac ; renseigné pour 14 % des ad).
    - ``mots`` : tous les mots dans le titre, les cotes ou le producteur.
    - ``debut``/``fin`` : chevauchement de période. Un inventaire sans dates
      exploitables est gardé et compté à part, jamais écarté en silence.
    """
    motif_lieu = re.compile(rf"(^| ){re.escape(normaliser(lieu))}( |$)") if lieu else None
    dep = normaliser(departement) if departement else None
    liste_mots = normaliser(mots).split() if mots else []
    retenus: list[Inventaire] = []
    sans_dates = 0
    for inv in inventaires:
        if insee is not None and inv.insee != insee:
            continue
        if dep is not None and normaliser(inv.departement) != dep:
            continue
        if motif_lieu is not None:
            cible = normaliser(" ".join((inv.commune, inv.titre, *inv.lieux)))
            if not motif_lieu.search(cible):
                continue
        if liste_mots:
            cible = normaliser(" ".join((inv.titre, inv.cotes, inv.producteur)))
            if not all(re.search(rf"(^| ){re.escape(m)}", cible) for m in liste_mots):
                continue
        if debut is not None or fin is not None:
            if inv.debut is None and inv.fin is None:
                sans_dates += 1
            else:
                a = inv.debut if inv.debut is not None else inv.fin
                b = inv.fin if inv.fin is not None else inv.debut
                assert a is not None and b is not None
                if (fin is not None and a > fin) or (debut is not None and b < debut):
                    continue
        retenus.append(inv)
    return Resultat(retenus, sans_dates)
