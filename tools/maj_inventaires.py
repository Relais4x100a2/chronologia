#!/usr/bin/env python3
"""Met à jour les listes d'inventaires d'archives copiées dans le dépôt.

Trois jeux de data.gouv.fr (Licence Ouverte 2.0) : inventaires des Archives
nationales (salle des inventaires virtuelle), inventaires d'archives
départementales et d'archives communales publiés sur FranceArchives.

Pour chaque jeu déclaré dans ``ressources/inventaires-archives/sources.json`` :
1. lire les métadonnées du jeu par l'API de data.gouv.fr ;
2. choisir la ressource CSV principale (exactement une, sinon erreur) ;
3. si son empreinte SHA-1 n'a pas changé depuis le manifeste, ne rien faire ;
4. sinon télécharger, vérifier l'empreinte annoncée, vérifier que les colonnes
   sont celles attendues et que le nombre de lignes ne s'effondre pas, puis
   écrire la copie compressée (gzip déterministe) et le manifeste.

Rien n'est accepté en silence (R24) : un changement de colonnes ou une baisse
forte du nombre de lignes arrête l'outil (code 1) sans rien écrire. La mise à
jour automatique ne fait que proposer une demande de fusion ; un humain la
relit et la fusionne (R18).

Bibliothèque standard seulement, pour tourner dans GitHub Actions sans
installer le projet.

Usage :
    python3 tools/maj_inventaires.py              # met à jour si besoin
    python3 tools/maj_inventaires.py --verifier   # code 3 si une mise à jour existe
    python3 tools/maj_inventaires.py --accepter-baisse   # accepte une baisse forte
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

RACINE = Path(__file__).resolve().parents[1]
DOSSIER = RACINE / "ressources" / "inventaires-archives"
API = "https://www.data.gouv.fr/api/1/datasets/{}/"
AGENT = "chronologia-maj-inventaires/1 (+https://github.com/relais4x100a2/chronologia)"
BAISSE_MAX = 0.2  # au-delà de 20 % de lignes en moins, on s'arrête

csv.field_size_limit(sys.maxsize)


class Refus(Exception):
    """Mise à jour refusée : le motif est affiché, rien n'est écrit."""


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=120) as rep:
        return bytes(rep.read())


def choisir_ressource(jeu: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    motif = re.compile(source["motif_titre"], re.IGNORECASE)
    candidates = [
        r for r in jeu["resources"]
        if (r.get("format") or "").lower() == "csv"
        and r.get("type") == "main"
        and motif.search(r.get("title") or "")
    ]  # fmt: skip
    if len(candidates) != 1:
        titres = [r.get("title") for r in jeu["resources"]]
        raise Refus(
            f"{source['cle']} : {len(candidates)} ressource(s) CSV principale(s) "
            f"correspondent à « {source['motif_titre']} » (attendu : 1). Ressources : {titres}"
        )
    choisie: dict[str, Any] = candidates[0]
    return choisie


def analyser_csv(contenu: bytes) -> tuple[list[str], int]:
    texte = contenu.decode("utf-8-sig")
    lecteur = csv.reader(io.StringIO(texte, newline=""))
    entete = next(lecteur)
    return entete, sum(1 for _ in lecteur)


def gzip_deterministe(contenu: bytes) -> bytes:
    """gzip sans date ni nom de fichier : une même donnée donne les mêmes octets."""
    tampon = io.BytesIO()
    with gzip.GzipFile(fileobj=tampon, mode="wb", compresslevel=9, mtime=0, filename="") as g:
        g.write(contenu)
    return tampon.getvalue()


def traiter(
    source: dict[str, Any], ancien: dict[str, Any] | None, accepter_baisse: bool
) -> tuple[dict[str, Any], bytes | None]:
    """Renvoie l'entrée de manifeste et le contenu compressé (None si inchangé)."""
    jeu = json.loads(_get(API.format(source["jeu_id"])))
    res = choisir_ressource(jeu, source)
    somme = res.get("checksum") or {}
    sha1_annonce = somme.get("value") if somme.get("type") == "sha1" else None
    fichier = DOSSIER / source["fichier"]

    if (
        ancien is not None
        and sha1_annonce is not None
        and ancien.get("sha1") == sha1_annonce
        and fichier.is_file()
    ):
        return ancien, None

    brut = _get(res["url"])
    sha1 = hashlib.sha1(brut).hexdigest()
    if sha1_annonce is not None and sha1 != sha1_annonce:
        raise Refus(f"{source['cle']} : empreinte SHA-1 {sha1} ≠ annoncée {sha1_annonce}")
    if ancien is not None and ancien.get("sha1") == sha1 and fichier.is_file():
        return ancien, None

    entete, lignes = analyser_csv(brut)
    if entete != source["colonnes"]:
        raise Refus(
            f"{source['cle']} : colonnes changées.\n  attendues : {source['colonnes']}\n"
            f"  reçues    : {entete}\nMettre à jour sources.json et le lecteur "
            "(chronologia/ressources/inventaires.py) après examen."
        )
    if ancien is not None and not accepter_baisse:
        avant = int(ancien.get("lignes", 0))
        if avant and lignes < avant * (1 - BAISSE_MAX):
            raise Refus(
                f"{source['cle']} : {lignes} lignes contre {avant} auparavant "
                f"(baisse > {BAISSE_MAX:.0%}). Relancer avec --accepter-baisse après examen."
            )

    entree = {
        "cle": source["cle"],
        "fichier": source["fichier"],
        "jeu_id": source["jeu_id"],
        "jeu_titre": jeu.get("title", "").strip(),
        "jeu_page": jeu.get("page"),
        "licence": jeu.get("license"),
        "ressource_id": res["id"],
        "ressource_titre": res.get("title"),
        "ressource_url": res["url"],
        "ressource_modifiee": res.get("last_modified"),
        "sha1": sha1,
        "sha256": hashlib.sha256(brut).hexdigest(),
        "octets": len(brut),
        "lignes": lignes,
    }
    return entree, gzip_deterministe(brut)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--verifier", action="store_true", help="ne rien écrire ; code 3 si à jour à faire")
    p.add_argument("--accepter-baisse", action="store_true")
    args = p.parse_args(argv)

    sources = json.loads((DOSSIER / "sources.json").read_text(encoding="utf-8"))["sources"]
    chemin_manifeste = DOSSIER / "manifeste.json"
    manifeste: dict[str, Any] = (
        json.loads(chemin_manifeste.read_text(encoding="utf-8"))
        if chemin_manifeste.is_file() else {"jeux": []}
    )  # fmt: skip
    anciens = {e["cle"]: e for e in manifeste["jeux"]}

    entrees: list[dict[str, Any]] = []
    a_ecrire: list[tuple[Path, bytes]] = []
    try:
        for source in sources:
            entree, contenu = traiter(source, anciens.get(source["cle"]), args.accepter_baisse)
            entrees.append(entree)
            etat = "inchangé" if contenu is None else "nouvelle version"
            print(f"{source['cle']:<4} {etat:<17} {entree['lignes']:>7} lignes  "
                  f"{entree['ressource_modifiee']}")  # fmt: skip
            if contenu is not None:
                a_ecrire.append((DOSSIER / source["fichier"], contenu))
    except Refus as e:
        print(f"refus : {e}", file=sys.stderr)
        return 1

    if not a_ecrire:
        print("aucune mise à jour")
        return 0
    if args.verifier:
        print(f"{len(a_ecrire)} jeu(x) à mettre à jour")
        return 3
    for chemin, contenu in a_ecrire:
        chemin.write_bytes(contenu)
    chemin_manifeste.write_text(
        json.dumps({"jeux": entrees}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(a_ecrire)} jeu(x) mis à jour ; manifeste réécrit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
