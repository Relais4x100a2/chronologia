"""Comparaison de fiches par position (rang ou ligne), jamais par valeur mesurée.

Un seul décompte sert trois usages : machine contre étalon, Socface contre étalon, seconde
lecture contre première. Une omission compte en faux négatif, un ajout en faux positif :
aucune omission ne peut améliorer un score. Les résultats ne contiennent que des comptes.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from chronologia.etalon.fiches import Json, etat_valeur, texte_valeur
from chronologia.etalon.mesures_texte import normaliser_espaces

CHAMPS_RACINE = ("date_acte", "date_evenement", "lieu")
_HORS_CHAMPS = {"rang", "ligne", "role"}

type Element = Mapping[str, Json]


@dataclass
class CompteChamp:
    vp: int = 0
    fp: int = 0
    fn: int = 0
    partiels: int = 0
    illisibles: int = 0

    @property
    def precision(self) -> float | None:
        return self.vp / (self.vp + self.fp) if self.vp + self.fp else None

    @property
    def rappel(self) -> float | None:
        return self.vp / (self.vp + self.fn) if self.vp + self.fn else None


@dataclass
class Comparaison:
    commune: str
    source: str
    champs: dict[str, CompteChamp] = field(default_factory=dict)
    roles_corrects: int = 0
    personnes_appariees: int = 0
    personnes_manquantes: int = 0
    personnes_en_trop: int = 0
    unites: int = 0

    def champ(self, nom: str) -> CompteChamp:
        return self.champs.setdefault(nom, CompteChamp())


@dataclass
class Accord:
    concordants: dict[str, int] = field(default_factory=dict)
    discordants: dict[str, int] = field(default_factory=dict)
    desaccords_presence: dict[str, int] = field(default_factory=dict)

    def accord_exact(self, champ: str) -> float | None:
        c, d = self.concordants.get(champ, 0), self.discordants.get(champ, 0)
        return c / (c + d) if c + d else None


def _source(fiche: Mapping[str, Json]) -> str:
    meta = fiche.get("meta")
    if not isinstance(meta, dict):
        return "inconnue"
    if meta.get("lecture") == "seconde":
        return "seconde_lecture"
    return str(meta.get("source", "inconnue"))


def _texte(v: Json) -> str | None:
    t = texte_valeur(v)
    return None if t is None else normaliser_espaces(t)


def _decompter(compte: CompteChamp, etalon: Json, autre: Json) -> None:
    """Applique la table de décompte (tâche 6) à un champ."""
    etat = etat_valeur(etalon)
    donne = _texte(autre)
    if etat == "lisible":
        ref = _texte(etalon)
        if donne is None:
            compte.fn += 1
        elif donne == ref:
            compte.vp += 1
        else:
            compte.fp += 1
            compte.fn += 1
    elif etat == "partiel":
        compte.partiels += 1
    elif etat == "illisible":
        compte.illisibles += 1
    elif etat == "absent" and donne is not None:
        compte.fp += 1


def _structure(fiche: Mapping[str, Json]) -> tuple[str, str, str]:
    if fiche.get("kind") == "page_recensement":
        return "lignes", "ligne", "ligne"
    return "personnes", "rang", "personne"


def _elements(fiche: Mapping[str, Json], liste: str, cle: str) -> dict[Json, Element]:
    brut = fiche.get(liste)
    return {e[cle]: e for e in (brut if isinstance(brut, list) else []) if isinstance(e, dict)}


def _paires(
    etalon: Mapping[str, Json], autre: Mapping[str, Json]
) -> tuple[str, list[tuple[Element | None, Element | None]]]:
    liste, cle, prefixe = _structure(etalon)
    a, b = _elements(etalon, liste, cle), _elements(autre, liste, cle)
    cles = sorted(set(a) | set(b), key=str)
    return prefixe, [(a.get(k), b.get(k)) for k in cles]


def _champs(*elements: Element | None) -> list[str]:
    return sorted({k for e in elements if e is not None for k in e} - _HORS_CHAMPS)


def comparer_fiches(etalon: Mapping[str, Json], autre: Mapping[str, Json]) -> Comparaison:
    c = Comparaison(commune=str(etalon.get("commune", "")), source=_source(autre), unites=1)
    for nom in CHAMPS_RACINE:
        if nom in etalon or nom in autre:
            _decompter(c.champ(nom), etalon.get(nom), autre.get(nom))
    prefixe, paires = _paires(etalon, autre)
    for e, x in paires:
        if e is not None and x is not None:
            c.personnes_appariees += 1
            c.roles_corrects += int(e.get("role") == x.get("role"))
        elif e is not None:
            c.personnes_manquantes += 1
        else:
            c.personnes_en_trop += 1
        for nom in _champs(e, x):
            v_etalon = e.get(nom) if e is not None else None
            v_autre = x.get(nom) if x is not None else None
            if e is None:
                if _texte(v_autre) is not None:
                    c.champ(f"{prefixe}.{nom}").fp += 1
            else:
                _decompter(c.champ(f"{prefixe}.{nom}"), v_etalon, v_autre)
    return c


def _incrementer(compteur: dict[str, int], cle: str) -> None:
    compteur[cle] = compteur.get(cle, 0) + 1


def _accorder(accord: Accord, nom: str, v1: Json, v2: Json) -> None:
    lisible1, lisible2 = etat_valeur(v1) == "lisible", etat_valeur(v2) == "lisible"
    if lisible1 and lisible2:
        egal = _texte(v1) == _texte(v2)
        _incrementer(accord.concordants if egal else accord.discordants, nom)
    elif lisible1 or lisible2:
        _incrementer(accord.desaccords_presence, nom)


def comparer_lectures(premiere: Mapping[str, Json], seconde: Mapping[str, Json]) -> Accord:
    """Accord entre deux lectures, symétrique, sur les champs lisibles des deux côtés."""
    accord = Accord()
    for nom in CHAMPS_RACINE:
        _accorder(accord, nom, premiere.get(nom), seconde.get(nom))
    prefixe, paires = _paires(premiere, seconde)
    for e1, e2 in paires:
        for nom in _champs(e1, e2):
            v1 = e1.get(nom) if e1 is not None else None
            v2 = e2.get(nom) if e2 is not None else None
            _accorder(accord, f"{prefixe}.{nom}", v1, v2)
    return accord


def cumuler(comparaisons: Iterable[Comparaison]) -> Comparaison:
    liste = list(comparaisons)
    if not liste:
        raise ValueError("aucune_comparaison")
    if len({(c.commune, c.source) for c in liste}) > 1:
        raise ValueError("communes_ou_sources_melangees")
    total = Comparaison(commune=liste[0].commune, source=liste[0].source)
    for c in liste:
        for nom, x in c.champs.items():
            t = total.champ(nom)
            t.vp, t.fp, t.fn = t.vp + x.vp, t.fp + x.fp, t.fn + x.fn
            t.partiels, t.illisibles = t.partiels + x.partiels, t.illisibles + x.illisibles
        total.roles_corrects += c.roles_corrects
        total.personnes_appariees += c.personnes_appariees
        total.personnes_manquantes += c.personnes_manquantes
        total.personnes_en_trop += c.personnes_en_trop
        total.unites += c.unites
    return total
