"""Tirage stratifié rejouable de l'étalon (§8.5 à 8.7) : pilotes, actes, recensements, remontée.

Tout est déterminé par le cadre, les candidats, le plan et la graine (empreintes à l'appui).
Le générateur est parcouru dans un ordre fixe : pilote d'état civil, pilote de recensement,
strates triées, recensements par année, remontée.
"""

import csv
import hashlib
import json
import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date
from fractions import Fraction
from pathlib import Path

from chronologia.etalon._csv import Ligne, ValeurInvalide, charger, choix, entier, texte
from chronologia.etalon.donnees import verifier_hors_depot

type Strate = tuple[str, str]
type Unite = tuple[str, int, int]  # (type, annee, rang)

TYPES_ETAT_CIVIL = ("naissance", "mariage", "deces")
TYPES_CADRE = (*TYPES_ETAT_CIVIL, "recensement")
# Dénombrements généraux de la période : un dénombrement attendu sans page est déclaré (R24).
ANNEES_RECENSEMENT = (1872, 1876, 1881, 1886, 1891, 1896, 1901, 1906, 1911)
COLONNES_CADRE = ("commune", "type", "annee", "nb_unites", "cote")
COLONNES_CANDIDATS = ("commune", "type", "annee", "rang", "cote")
COLONNES_TIRAGE = ("commune", "categorie", "type", "annee", "rang", "cote")


@dataclass(frozen=True)
class LigneCadre:
    commune: str
    type: str
    annee: int
    nb_unites: int
    cote: str


@dataclass(frozen=True)
class PlanTirage:
    commune: str
    n_actes: int
    pages_par_denombrement: int
    n_remontee: int
    periode: tuple[int, int] = (1872, 1911)
    largeur_tranche: int = 10
    repartition: Mapping[Strate, int] | None = None
    n_pilote_actes: int = 5


@dataclass(frozen=True)
class Tire:
    commune: str
    categorie: str
    type: str
    annee: int
    rang: int
    cote: str


@dataclass(frozen=True)
class Tirage:
    tires: list[Tire]
    annee_pilote: int
    page_pilote: tuple[int, int]
    graine: int
    empreintes: dict[str, str]
    strates_vides: list[Strate]
    annees_absentes: list[int]
    denombrements_tires: list[int] = field(default_factory=list)
    denombrements_vides: list[int] = field(default_factory=list)
    version: str = field(default="1")


def tranches(periode: tuple[int, int], largeur: int) -> list[tuple[int, int]]:
    debut, fin = periode
    return [(a, min(a + largeur - 1, fin)) for a in range(debut, fin + 1, largeur)]


def tranche_de(annee: int, periode: tuple[int, int], largeur: int) -> str:
    if annee < periode[0]:
        return f"avant-{periode[0]}"
    for debut, fin in tranches(periode, largeur):
        if debut <= annee <= fin:
            return f"{debut}-{fin}"
    raise ValueError("annee_apres_periode")


def _ligne_cadre(ligne: Ligne) -> LigneCadre:
    nb = entier(ligne, "nb_unites")
    return LigneCadre(
        commune=texte(ligne, "commune"),
        type=choix(ligne, "type", TYPES_CADRE),
        annee=entier(ligne, "annee"),
        nb_unites=nb,
        cote=texte(ligne, "cote", obligatoire=nb > 0),
    )


def charger_cadre(chemin: Path) -> tuple[list[LigneCadre], list[str]]:
    return charger(chemin, COLONNES_CADRE, _ligne_cadre)


def _candidat(ligne: Ligne) -> Tire:
    rang = entier(ligne, "rang")
    if rang < 1:
        raise ValeurInvalide("rang", "superieur_a_zero_attendu")
    return Tire(
        commune=texte(ligne, "commune"),
        categorie="remontee",
        type=choix(ligne, "type", TYPES_ETAT_CIVIL),
        annee=entier(ligne, "annee"),
        rang=rang,
        cote=texte(ligne, "cote"),
    )


def _plus_fort_reste(poids: Mapping[Strate, int], n: int) -> dict[Strate, int]:
    """Répartit ``n`` proportionnellement à ``poids`` ; égalités de reste départagées par l'ordre."""
    total = sum(poids.values())
    quotas = {s: Fraction(n * p, total) for s, p in poids.items()}
    parts = {s: math.floor(q) for s, q in quotas.items()}
    reste = n - sum(parts.values())
    ordre = sorted(poids, key=lambda s: (-(quotas[s] - parts[s]), s))
    for s in ordre[:reste]:
        parts[s] += 1
    return parts


def repartir(effectifs: Mapping[Strate, int], n: int) -> dict[Strate, int]:
    """1 acte par strate non vide, puis le solde au plus fort reste, plafonné à l'effectif."""
    pleins = {s: e for s, e in sorted(effectifs.items()) if e > 0}
    if n < len(pleins):
        raise ValueError("strates_trop_nombreuses")
    if n > sum(pleins.values()):
        raise ValueError("population_insuffisante")
    alloc = dict.fromkeys(pleins, 1)
    solde = n - len(pleins)
    while solde > 0:
        actifs = {s: e for s, e in pleins.items() if alloc[s] < e}
        ajout = _plus_fort_reste(actifs, solde)
        solde = 0
        for s, k in ajout.items():
            alloc[s] += k
            excedent = max(0, alloc[s] - pleins[s])
            alloc[s] -= excedent
            solde += excedent
    return alloc


def _valider_repartition(
    repartition: Mapping[Strate, int], effectifs: Mapping[Strate, int], n: int
) -> dict[Strate, int]:
    if sum(repartition.values()) != n:
        raise ValueError("repartition_total")
    for s, k in repartition.items():
        if effectifs.get(s, 0) == 0:
            raise ValueError("repartition_strate_vide")
        if not 0 <= k <= effectifs[s]:
            raise ValueError("repartition_hors_effectif")
    return dict(repartition)


def _sha(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def _json_trie(objet: object) -> bytes:
    return json.dumps(objet, sort_keys=True, ensure_ascii=False).encode("utf-8")


def _empreintes(cadre: Path, candidats: Path | None, plan: PlanTirage) -> dict[str, str]:
    repartition = (
        None
        if plan.repartition is None
        else sorted([list(s), k] for s, k in plan.repartition.items())
    )
    parametres = {k: v for k, v in asdict(plan).items() if k != "repartition"}
    return {
        "cadre": _sha(cadre.read_bytes()),
        "candidats": _sha(candidats.read_bytes() if candidats is not None else b""),
        "repartition": _sha(_json_trie(repartition)),
        "parametres": _sha(_json_trie(parametres)),
    }


def _charger_ou_lever(lignes: tuple[list[LigneCadre], list[str]], plan: PlanTirage) -> list[LigneCadre]:
    cadre, erreurs = lignes
    if erreurs:
        raise ValueError("cadre_invalide : " + " ; ".join(erreurs))
    vus: set[tuple[str, int]] = set()
    for lc in cadre:
        if lc.commune != plan.commune:
            raise ValueError("cadre_commune_differente")
        if not plan.periode[0] <= lc.annee <= plan.periode[1]:
            raise ValueError("cadre_annee_hors_periode")
        if (lc.type, lc.annee) in vus:
            raise ValueError("cadre_doublon")
        vus.add((lc.type, lc.annee))
    return cadre


def _remontee(candidats: Path | None, plan: PlanTirage) -> list[Tire]:
    if candidats is None:
        if plan.n_remontee:
            raise ValueError("remontee_sans_candidats")
        return []
    liste, erreurs = charger(candidats, COLONNES_CANDIDATS, _candidat)
    if erreurs:
        raise ValueError("candidats_invalides : " + " ; ".join(erreurs))
    if any(c.annee >= plan.periode[0] for c in liste):
        raise ValueError("remontee_hors_periode")
    if any(c.commune != plan.commune for c in liste):
        raise ValueError("candidats_commune_differente")
    if len(liste) < plan.n_remontee:
        raise ValueError("remontee_insuffisante")
    return sorted(liste, key=lambda c: (c.type, c.annee, c.rang))


def tirer(cadre: Path, candidats_remontee: Path | None, plan: PlanTirage, graine: int) -> Tirage:
    lignes = _charger_ou_lever(charger_cadre(cadre), plan)
    remontee = _remontee(candidats_remontee, plan)
    rng = random.Random(graine)
    cotes = {(lc.type, lc.annee): lc.cote for lc in lignes}
    tires: list[Tire] = []

    def tire(categorie: str, u: Unite) -> Tire:
        return Tire(plan.commune, categorie, u[0], u[1], u[2], cotes[(u[0], u[1])])

    etat_civil = [lc for lc in lignes if lc.type in TYPES_ETAT_CIVIL]
    par_annee: dict[int, list[Unite]] = {}
    for lc in sorted(etat_civil, key=lambda x: (x.annee, x.type)):
        par_annee.setdefault(lc.annee, []).extend((lc.type, lc.annee, r) for r in range(1, lc.nb_unites + 1))

    # 1. Pilote d'état civil : une année ayant assez d'actes ; tous ses actes sont exclus.
    eligibles = sorted(a for a, us in par_annee.items() if len(us) >= max(1, plan.n_pilote_actes))
    if not eligibles:
        raise ValueError("pilote_impossible")
    annee_pilote = rng.choice(eligibles)
    tires += [tire("pilote_acte", u) for u in rng.sample(par_annee[annee_pilote], plan.n_pilote_actes)]

    # 2. Pilote de recensement : une page parmi toutes ; seule elle est exclue.
    pages: dict[int, list[Unite]] = {}
    for lc in sorted((x for x in lignes if x.type == "recensement"), key=lambda x: x.annee):
        if lc.nb_unites:
            pages[lc.annee] = [("recensement", lc.annee, r) for r in range(1, lc.nb_unites + 1)]
    toutes_pages = [p for a in sorted(pages) for p in pages[a]]
    if not toutes_pages:
        raise ValueError("pilote_recensement_impossible")
    pilote_page = rng.choice(toutes_pages)
    tires.append(tire("pilote_recensement", pilote_page))

    # 3. Actes : strates (type, tranche) hors année pilote.
    strates: dict[Strate, list[Unite]] = {
        (t, f"{d}-{f}"): [] for t in TYPES_ETAT_CIVIL for d, f in tranches(plan.periode, plan.largeur_tranche)
    }
    for annee, unites in par_annee.items():
        if annee == annee_pilote:
            continue
        for u in unites:
            strates[(u[0], tranche_de(annee, plan.periode, plan.largeur_tranche))].append(u)
    effectifs = {s: len(us) for s, us in strates.items()}
    allocation = (
        repartir(effectifs, plan.n_actes)
        if plan.repartition is None
        else _valider_repartition(plan.repartition, effectifs, plan.n_actes)
    )
    for s in sorted(allocation):
        tires += [tire("acte", u) for u in rng.sample(sorted(strates[s]), allocation[s])]

    # 4. Recensements : pages_par_denombrement pages par année, page pilote exclue.
    for annee in sorted(pages):
        restantes = [p for p in pages[annee] if p != pilote_page]
        if len(restantes) < plan.pages_par_denombrement:
            raise ValueError("pages_insuffisantes")
        tires += [tire("recensement", p) for p in rng.sample(restantes, plan.pages_par_denombrement)]

    # 5. Remontée.
    tires += rng.sample(remontee, plan.n_remontee)

    annees_absentes = sorted(
        a
        for a in range(plan.periode[0], plan.periode[1] + 1)
        if any(not any(u[0] == t for u in par_annee.get(a, [])) for t in TYPES_ETAT_CIVIL)
    )
    attendus = {a for a in ANNEES_RECENSEMENT if plan.periode[0] <= a <= plan.periode[1]}
    attendus |= {lc.annee for lc in lignes if lc.type == "recensement"}
    return Tirage(
        tires=tires,
        annee_pilote=annee_pilote,
        page_pilote=(pilote_page[1], pilote_page[2]),
        graine=graine,
        empreintes=_empreintes(cadre, candidats_remontee, plan),
        strates_vides=sorted(s for s, e in effectifs.items() if e == 0),
        annees_absentes=annees_absentes,
        denombrements_tires=sorted(pages),
        denombrements_vides=sorted(attendus - set(pages)),
    )


def tirer_seconde_lecture(t: Tirage, graine_seconde: int, proportion: float = 0.10) -> list[Tire]:
    """``ceil(proportion × actes de l'étalon, remontée comprise)`` actes, jamais un pilote."""
    pool = sorted(
        (x for x in t.tires if x.categorie in ("acte", "remontee")),
        key=lambda x: (x.categorie, x.type, x.annee, x.rang),
    )
    k = math.ceil(Fraction(str(proportion)) * len(pool))
    return random.Random(graine_seconde).sample(pool, k)


def _trier(tires: Sequence[Tire]) -> list[Tire]:
    return sorted(tires, key=lambda x: (x.categorie, x.type, x.annee, x.rang))


def ecrire_tirage(t: Tirage, dossier: Path) -> None:
    """Écrit ``tirage.csv`` (trié, déterministe) et ``tirage.meta.json``, hors du dépôt."""
    csv_chemin = verifier_hors_depot(dossier / "tirage.csv")
    meta_chemin = verifier_hors_depot(dossier / "tirage.meta.json")
    dossier.mkdir(parents=True, exist_ok=True)
    with csv_chemin.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(COLONNES_TIRAGE)
        for x in _trier(t.tires):
            ecrivain.writerow((x.commune, x.categorie, x.type, x.annee, x.rang, x.cote))
    meta = {k: v for k, v in asdict(t).items() if k != "tires"}
    meta["date"] = date.today().isoformat()
    meta_chemin.write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
