"""Normalisation des noms et clé phonétique française (décision 20).

Écrites dans le projet, sans dépendance : la clé est une règle versionnée au même
titre que les indices qui l'emploient (``regle:onomastique:nom_prenom:v1``).
"""

import re
import unicodedata
from typing import List, Tuple

_LIGATURES = str.maketrans({"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE", "ß": "ss"})

# Appliquées dans l'ordre, sur une forme en minuscules : chaque produit est écrit
# en majuscules pour qu'une règle suivante ne le réinterprète pas (gu + i → G, et
# non J).
_REGLES_PHONETIQUES: List[Tuple[str, str]] = [
    ("ph", "F"),
    ("th", "T"),
    ("ck", "K"),
    ("qu", "K"),
    ("q", "K"),
    ("gu(?=[eiy])", "G"),
    ("g(?=[eiy])", "J"),
    ("c(?=[eiy])", "S"),
    ("c", "K"),
    ("eau", "O"),
    ("au", "O"),
    ("ai", "E"),
    ("ei", "E"),
    ("y", "I"),
    ("w", "V"),
    ("z", "S"),
    ("h", ""),
]
_DOUBLES = re.compile(r"(.)\1+")
_FINALES_MUETTES = re.compile(r"(?<=.)[STDX]+$")


def normaliser(texte: str) -> str:
    """Minuscules, sans diacritiques ni ligatures, mots séparés par une espace."""
    decompose = unicodedata.normalize("NFKD", texte.translate(_LIGATURES))
    sans_accents = "".join(c for c in decompose if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^0-9a-z]+", " ", sans_accents.lower()).split())


def premier_prenom(prenoms: str) -> str:
    """Premier prénom normalisé (``Pierre_Jean`` → ``pierre``), vide à défaut."""
    mots = normaliser(prenoms).split()
    return mots[0] if mots else ""


def _cle_mot(mot: str) -> str:
    for motif, produit in _REGLES_PHONETIQUES:
        mot = re.sub(motif, produit, mot)
    return _FINALES_MUETTES.sub("", _DOUBLES.sub(r"\1", mot.upper()))


def cle_phonetique(texte: str) -> str:
    """Clé phonétique française, mot à mot.

    PH/F, TH/T, C et G durs ou doux, QU/K, Y/I, W/V, Z/S, EAU/AU/O, AI/EI/E,
    H muet, consonnes doublées réduites, finales muettes (S, T, D, X) ôtées.
    """
    texte = texte.replace("ç", "s").replace("Ç", "S")
    return " ".join(_cle_mot(mot) for mot in normaliser(texte).split())
