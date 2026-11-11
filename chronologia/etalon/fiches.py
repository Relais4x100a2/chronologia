"""Fiches structurées de l'étalon : lecture YAML sûre et validation contre des schémas versionnés.

Garde-fou nominatif : aucun message d'erreur ne reprend une valeur lue. On cite le fichier,
le chemin JSON et un code (mot-clé du validateur ou code maison), jamais ``error.message``.
"""

import json
import re
from collections.abc import Mapping
from functools import cache
from pathlib import Path
from typing import Any, Literal

import yaml
from jsonschema import Draft202012Validator

type Json = None | bool | int | float | str | list[Json] | dict[str, Json]
EtatValeur = Literal["lisible", "partiel", "illisible", "absent", "non_applicable"]

_SCHEMAS = Path(__file__).parent / "schemas"
KINDS = {"acte": "acte.schema.json", "page_recensement": "page_recensement.schema.json"}


class _Chargeur(yaml.SafeLoader):
    """SafeLoader sans dates implicites, booléens limités à true/false, clés uniques."""


_Chargeur.yaml_implicit_resolvers = {
    premier: [(tag, rx) for tag, rx in resolveurs if tag not in ("tag:yaml.org,2002:timestamp", "tag:yaml.org,2002:bool")]
    for premier, resolveurs in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
_Chargeur.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|True|false|False)$"), list("tTfF")
)


def _mapping_sans_doublon(chargeur: _Chargeur, noeud: yaml.MappingNode, deep: bool = False) -> Any:
    vues: set[Any] = set()
    for cle, _ in noeud.value:
        valeur = chargeur.construct_object(cle, deep=deep)
        if valeur in vues:
            raise yaml.constructor.ConstructorError(None, None, "cle_dupliquee", cle.start_mark)
        vues.add(valeur)
    return chargeur.construct_mapping(noeud, deep=deep)


_Chargeur.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping_sans_doublon)


def charger_fiche(chemin: Path) -> tuple[dict[str, Json] | None, list[str]]:
    """Lit une fiche YAML. Renvoie (fiche, []) ou (None, [erreur sans extrait du texte])."""
    nom = chemin.name
    try:
        with chemin.open(encoding="utf-8") as f:
            donnees = yaml.load(f, Loader=_Chargeur)
    except UnicodeDecodeError:
        return None, [f"{nom} : encodage_invalide"]
    except yaml.constructor.ConstructorError as e:
        if e.problem == "cle_dupliquee" and e.problem_mark is not None:
            return None, [f"{nom} : cle_dupliquee (ligne {e.problem_mark.line + 1})"]
        return None, [f"{nom} : yaml_invalide{_ligne(e)}"]
    except yaml.YAMLError as e:
        return None, [f"{nom} : yaml_invalide{_ligne(e)}"]
    if not isinstance(donnees, dict):
        return None, [f"{nom} : racine_non_mapping"]
    return donnees, []


def _ligne(e: yaml.YAMLError) -> str:
    marque = getattr(e, "problem_mark", None)
    return f" (ligne {marque.line + 1})" if marque is not None else ""


@cache
def _validateur(kind: str) -> Draft202012Validator:
    schema = json.loads((_SCHEMAS / KINDS[kind]).read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def _chemin(parties: Any) -> str:
    return "/" + "/".join(str(p) for p in parties)


def valider_fiche(fiche: Mapping[str, Json], nom: str) -> list[str]:
    """Erreurs ``"<nom> : <chemin JSON> : <code>"``, triées ; liste vide si la fiche est valide."""
    kind = fiche.get("kind")
    if not isinstance(kind, str) or kind not in KINDS:
        return [f"{nom} : /kind : kind_inconnu"]
    erreurs = sorted(
        (_chemin(e.absolute_path), str(e.validator)) for e in _validateur(kind).iter_errors(fiche)
    )
    if not erreurs:
        erreurs = _controles_croises(fiche)
    return [f"{nom} : {chemin} : {code}" for chemin, code in erreurs]


def _controles_croises(fiche: Mapping[str, Json]) -> list[tuple[str, str]]:
    erreurs: list[tuple[str, str]] = []
    cle, liste, code = (
        ("rang", "personnes", "rang_duplique")
        if fiche["kind"] == "acte"
        else ("ligne", "lignes", "ligne_dupliquee")
    )
    vus: set[Json] = set()
    elements = fiche.get(liste)
    for i, element in enumerate(elements if isinstance(elements, list) else []):
        assert isinstance(element, dict)
        if element[cle] in vus:
            erreurs.append((f"/{liste}/{i}/{cle}", code))
        vus.add(element[cle])
    liens = fiche.get("liens")
    for i, lien in enumerate(liens if isinstance(liens, list) else []):
        assert isinstance(lien, dict)
        for bout in ("de", "vers"):
            if lien[bout] not in vus:
                erreurs.append((f"/liens/{i}/{bout}", "rang_inexistant"))
    return erreurs


def etat_valeur(v: Json) -> EtatValeur:
    """État de lecture d'une valeur transcrite ; ``None`` (ou clé absente) = non applicable."""
    if v is None:
        return "non_applicable"
    if isinstance(v, str):
        return "lisible"
    if isinstance(v, dict):
        if v.get("illisible") is True:
            return "illisible"
        if v.get("illisible") == "partiel":
            return "partiel"
        if v.get("absent") is True:
            return "absent"
    raise ValueError("valeur_non_conforme")


def texte_valeur(v: Json) -> str | None:
    """La chaîne lue (partielle comprise), ou ``None``."""
    etat = etat_valeur(v)
    if etat == "lisible":
        assert isinstance(v, str)
        return v
    if etat == "partiel":
        assert isinstance(v, dict) and isinstance(v["lu"], str)
        return v["lu"]
    return None
