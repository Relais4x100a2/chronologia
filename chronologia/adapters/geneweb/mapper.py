"""Projection d'une ``Genealogy`` toldot vers la couche Source de Chronologia.

Règles de la section 5 du modèle. Rien n'est résolu ici (R13) : chaque événement
GeneWeb donne un passage, un factoïde, des masques et des participations, plus
un EVENEMENT relié par une IDENT_EVENEMENT « certain » (5.2).
"""

import hashlib
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from typing import Any, Collection, Dict, List, Optional, Sequence, Tuple

from geneweb_py.core.date import Date
from geneweb_py.core.event import Event, WitnessKind
from geneweb_py.core.exceptions import UnsupportedCalendarError
from geneweb_py.core.genealogy import Genealogy
from geneweb_py.core.family import Family
from geneweb_py.core.person import Person, RelationType
from geneweb_py.core.place import parse_place

from chronologia import __version__
from chronologia.modele.entites import (
    Evenement,
    Conclusion,
    Factoide,
    IdentEvenement,
    Lot,
    Masque,
    MentionLieu,
    Participation,
    Passage,
    Qualite,
    Relation,
)

_TYPES_EVENEMENT = {
    "BIRTH": "naissance",
    "BAPTISM": "bapteme",
    "DEATH": "deces",
    "BURIAL": "inhumation",
    "MARRIAGE": "mariage",
    "DIVORCE": "divorce",
}
_RELIGIEUX = {"bapteme", "mariage"}
_ROLE_PRINCIPAL = {
    "naissance": "ne",
    "bapteme": "baptise",
    "deces": "decede",
    "inhumation": "inhume",
}
_TYPES_RELATION = {
    RelationType.ADOPTION: "adoption",
    RelationType.RECOGNITION: "reconnaissance",
    RelationType.CANDIDATE: "parent_candidat",
    RelationType.GODPARENT: "parrainage",
    RelationType.FOSTER: "nourricier",
}
_ORIENTATIONS = {"fath": "pere", "moth": "mere"}


@dataclass(frozen=True)
class LotImport:
    passages: Tuple[Passage, ...]
    masques: Tuple[Masque, ...]
    factoides: Tuple[Factoide, ...]
    participations: Tuple[Participation, ...]
    relations: Tuple[Relation, ...]
    evenements: Tuple[Evenement, ...]
    ident_evenements: Tuple[IdentEvenement, ...]
    qualites: Tuple[Qualite, ...] = ()
    mentions_lieu: Tuple[MentionLieu, ...] = ()
    conclusions: Tuple[Conclusion, ...] = ()
    lot: Optional[Lot] = None


class LotDejaImporte(Exception):
    """Un lot d'empreinte identique existe déjà : le réimport est refusé."""

    def __init__(self, empreinte: str) -> None:
        super().__init__(f"lot déjà importé (empreinte {empreinte})")
        self.empreinte = empreinte


def _bornes(date_gw: Date) -> Tuple[Optional[date], Optional[date]]:
    """Bornes de la date, sans toucher au texte déclaré."""
    try:
        return date_gw.to_bounds()
    except UnsupportedCalendarError:
        return None, None


def _cle_famille(famille: Family) -> str:
    """Clé de réimport stable d'une famille (indépendante de l'ordre du fichier)."""
    return f"gw:fam:{famille.husband_id or 'inconnu'}__{famille.wife_id or 'inconnu'}"


def _role_temoin(temoin: Dict[str, Any], type_evt: str) -> str:
    genre: Optional[str] = temoin.get("type")
    kind = temoin.get("witness_kind")
    if kind == WitnessKind.GODPARENT:
        return {"m": "parrain", "f": "marraine"}.get(genre or "", "parrain_ou_marraine")
    if kind == WitnessKind.OFFICER:
        return "celebrant" if type_evt in _RELIGIEUX else "officier"
    return "temoin"


class _Constructeur:
    def __init__(self, fichier: Optional[str], empreinte: Optional[str] = None) -> None:
        self.fichier = fichier
        self.court = empreinte[:12] if empreinte else "local"
        self.conclusions: List[Conclusion] = []
        self.passages: List[Passage] = []
        self.masques: List[Masque] = []
        self.factoides: List[Factoide] = []
        self.participations: List[Participation] = []
        self.relations: List[Relation] = []
        self.evenements: List[Evenement] = []
        self.idents: List[IdentEvenement] = []
        self.qualites: List[Qualite] = []
        self.mentions: List[MentionLieu] = []

    def passage(
        self,
        citation: Optional[str],
        debut: Optional[int],
        fin: Optional[int],
        notes: Sequence[str] = (),
    ) -> Passage:
        p = Passage(
            f"P{len(self.passages) + 1}", citation, self.fichier, debut, fin,
            "\n".join(notes) or None,
            f"gw:pass:{self.court}:{debut}_{fin}",
        )
        self.passages.append(p)
        return p

    def masque(
        self, passage: Passage, cle: str, genealogie: Genealogy
    ) -> Masque:
        for m in self.masques:
            if m.passage_ref == passage.ref and m.cle_externe == f"gw:pers:{cle}":
                return m
        personne = genealogie.persons.get(cle)
        sexe, nom = None, cle
        if personne is not None:
            sexe = personne.gender.name.lower()
            nom = f"{personne.first_name} {personne.last_name}"
        m = Masque(
            f"M{len(self.masques) + 1}", passage.ref, nom, sexe, f"gw:pers:{cle}"
        )
        self.masques.append(m)
        return m

    def factoide(
        self,
        passage: Passage,
        type_evenement: Optional[str],
        date_gw: Optional[Date],
        cle_famille: Optional[str] = None,
    ) -> Factoide:
        texte = brute = mini = maxi = None
        incertaine = False
        if date_gw is not None:
            texte = date_gw.display_text
            brute = date_gw.raw_text
            mini, maxi = _bornes(date_gw)
            incertaine = getattr(date_gw.prefix, "name", None) == "MAYBE"
        f = Factoide(
            f"F{len(self.factoides) + 1}",
            passage.ref,
            type_evenement,
            texte,
            mini,
            maxi,
            None,
            incertaine,
            brute,
            cle_famille,
        )
        self.factoides.append(f)
        return f

    def lieu(
        self,
        factoide: Factoide,
        ecrit: Optional[str],
        fonction: str = "evenement",
        qualite: Optional[Qualite] = None,
    ) -> None:
        decompose = parse_place(ecrit)
        if decompose is None:
            return
        self.mentions.append(
            MentionLieu(
                f"L{len(self.mentions) + 1}",
                factoide.ref,
                decompose.raw,
                decompose.name,
                fonction,
                None,
                qualite.ref if qualite else None,
            )
        )

    def evenement_certain(self, factoide: Factoide) -> None:
        e = Evenement(f"E{len(self.evenements) + 1}")
        self.evenements.append(e)
        self.idents.append(IdentEvenement(factoide.ref, e.ref, "certain", "actif"))

    def evenement_personnel(
        self, personne: Person, evt: Event, genealogie: Genealogy
    ) -> None:
        type_evt = _TYPES_EVENEMENT.get(evt.event_type.name, evt.event_type.name.lower())
        passage = self.passage(evt.source, evt.start_line, evt.end_line, evt.notes)
        factoide = self.factoide(passage, type_evt, evt.date)
        self.lieu(factoide, evt.place)
        principal = self.masque(passage, personne.unique_id, genealogie)
        ordre = 1
        role = _ROLE_PRINCIPAL.get(type_evt, "sujet")
        self.participations.append(
            Participation(factoide.ref, principal.ref, role, ordre)
        )
        for temoin in evt.witnesses:
            ordre += 1
            m = self.masque(passage, temoin["person_id"], genealogie)
            self.participations.append(
                Participation(factoide.ref, m.ref, _role_temoin(temoin, type_evt), ordre)
            )
        self.evenement_certain(factoide)

    def _conjoints(
        self, famille: Family, passage: Passage, genealogie: Genealogy
    ) -> List[Tuple[Masque, str]]:
        res: List[Tuple[Masque, str]] = []
        if famille.husband_id:
            res.append((self.masque(passage, famille.husband_id, genealogie), "epoux"))
        if famille.wife_id:
            res.append((self.masque(passage, famille.wife_id, genealogie), "epouse"))
        return res

    def evenement_familial(
        self,
        famille: Family,
        type_evt: str,
        date_gw: Optional[Date],
        citation: Optional[str],
        debut: Optional[int],
        fin: Optional[int],
        temoins: List[Dict[str, Any]],
        genealogie: Genealogy,
        lieu: Optional[str] = None,
        notes: Sequence[str] = (),
    ) -> None:
        passage = self.passage(citation, debut, fin, notes)
        factoide = self.factoide(passage, type_evt, date_gw, _cle_famille(famille))
        self.lieu(factoide, lieu)
        ordre = 0
        for masque, role in self._conjoints(famille, passage, genealogie):
            ordre += 1
            self.participations.append(
                Participation(factoide.ref, masque.ref, role, ordre)
            )
        for temoin in temoins:
            ordre += 1
            m = self.masque(passage, temoin["person_id"], genealogie)
            self.participations.append(
                Participation(factoide.ref, m.ref, _role_temoin(temoin, type_evt), ordre)
            )
        self.evenement_certain(factoide)

    def famille(self, famille: Family, genealogie: Genealogy) -> None:
        citation = famille.marriage_source or famille.family_source
        debut, fin = famille.start_line, famille.end_line
        premier = len(self.passages)
        mariages = [
            e for e in famille.events if e.event_type.name == "MARRIAGE"
        ]
        # Un fevt #marr remplace le mariage de la ligne fam (même fait, mieux décrit).
        if mariages:
            for e in mariages:
                self.evenement_familial(
                    famille, "mariage", e.date, e.source or citation,
                    e.start_line, e.end_line, e.witnesses, genealogie, e.place,
                    e.notes,
                )
        elif famille.marriage_date or famille.marriage_place or famille.marriage_source:
            self.evenement_familial(
                famille, "mariage", famille.marriage_date, citation,
                debut, fin, famille.witnesses, genealogie, famille.marriage_place,
            )
        if famille.divorce_date:
            self.evenement_familial(
                famille, "divorce", famille.divorce_date, citation,
                debut, fin, [], genealogie,
            )
        for e in famille.events:
            if e.event_type.name in ("MARRIAGE", "DIVORCE"):
                continue
            type_evt = _TYPES_EVENEMENT.get(e.event_type.name, e.event_type.name.lower())
            self.evenement_familial(
                famille, type_evt, e.date, e.source or citation,
                e.start_line, e.end_line, e.witnesses, genealogie, e.place,
                e.notes,
            )
        self.filiation(famille, genealogie)
        self.commentaire_famille(famille, premier)

    def commentaire_famille(self, famille: Family, premier: int) -> None:
        """Le ``comm`` va sur le passage de la ligne ``fam`` (à défaut, le premier)."""
        if not famille.comments or premier >= len(self.passages):
            return
        cibles = range(premier, len(self.passages))
        i = next(
            (
                k for k in cibles
                if (self.passages[k].ligne_debut, self.passages[k].ligne_fin)
                == (famille.start_line, famille.end_line)
            ),
            premier,
        )
        texte = "\n".join(c for c in (self.passages[i].transcription, *famille.comments) if c)
        self.passages[i] = replace(self.passages[i], transcription=texte)

    def notes_personne(self, personne: Person, genealogie: Genealogy) -> None:
        for note in personne.notes:
            passage = self.passage(None, personne.start_line, personne.end_line)
            masque = self.masque(passage, personne.unique_id, genealogie)
            self.conclusions.append(
                Conclusion(f"C{len(self.conclusions) + 1}", masque.ref, note)
            )

    def filiation(self, famille: Family, genealogie: Genealogy) -> None:
        if not famille.children:
            return
        # Un factoïde sans type porte toute la filiation de la famille.
        passage = self.passage(
            famille.common_children_source or famille.family_source,
            famille.start_line,
            famille.end_line,
        )
        factoide = self.factoide(passage, None, None, _cle_famille(famille))
        for enfant in famille.children:
            sujet = self.masque(passage, enfant.person_id, genealogie)
            for parent, orientation in (
                (famille.husband_id, "pere"),
                (famille.wife_id, "mere"),
            ):
                if parent:
                    objet = self.masque(passage, parent, genealogie)
                    self.relations.append(
                        Relation(
                            factoide.ref, sujet.ref, objet.ref, "filiation",
                            orientation,
                        )
                    )

    def qualites_personne(self, personne: Person, genealogie: Genealogy) -> None:
        if not personne.occupation and not personne.titles:
            return
        # Un factoïde sans type par personne porte ses qualités (R2).
        passage = self.passage(None, personne.start_line, personne.end_line)
        factoide = self.factoide(passage, None, None)
        masque = self.masque(passage, personne.unique_id, genealogie)
        if personne.occupation:
            self.qualites.append(
                Qualite(
                    f"Q{len(self.qualites) + 1}", factoide.ref, masque.ref,
                    "profession", personne.occupation,
                )
            )
        for titre in personne.titles:
            debut = _bornes(titre.start_date)[0] if titre.start_date else None
            fin = _bornes(titre.end_date)[1] if titre.end_date else None
            q = Qualite(
                f"Q{len(self.qualites) + 1}", factoide.ref, masque.ref,
                "titre", titre.name, debut, fin, titre.number or None,
            )
            self.qualites.append(q)
            self.lieu(factoide, titre.place, "titre", q)

    def relations_typees(self, personne: Person, genealogie: Genealogy) -> None:
        for lien in personne.relation_links:
            passage = self.passage(None, lien.start_line, lien.end_line)
            factoide = self.factoide(passage, None, None)
            sujet = self.masque(passage, personne.unique_id, genealogie)
            objet = self.masque(passage, lien.target_person_key, genealogie)
            degre = "possible" if lien.relation_type == RelationType.CANDIDATE else "certain"
            self.relations.append(
                Relation(
                    factoide.ref,
                    sujet.ref,
                    objet.ref,
                    _TYPES_RELATION[lien.relation_type],
                    _ORIENTATIONS.get(lien.parent_role.value) if lien.parent_role else None,
                    degre,
                )
            )


def empreinte_texte(texte: str) -> str:
    """SHA-256 du contenu d'un fichier ``.gw`` (UTF-8)."""
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def importer_genealogie(
    genealogie: Genealogy,
    fichier: Optional[str] = None,
    empreinte: Optional[str] = None,
    maintenant: Optional[datetime] = None,
    lots_connus: Collection[str] = (),
) -> LotImport:
    """Projette une généalogie toldot vers les entités de la couche Source.

    Refuse (``LotDejaImporte``) un fichier dont l'empreinte est dans ``lots_connus``.
    """
    if empreinte is not None and empreinte in lots_connus:
        raise LotDejaImporte(empreinte)
    c = _Constructeur(fichier, empreinte)
    for personne in list(genealogie.persons.values()):
        for evt in personne.events:
            c.evenement_personnel(personne, evt, genealogie)
        c.relations_typees(personne, genealogie)
        c.qualites_personne(personne, genealogie)
        c.notes_personne(personne, genealogie)
    for famille in list(genealogie.families.values()):
        c.famille(famille, genealogie)
    effectif = (
        len(c.passages) + len(c.masques) + len(c.factoides) + len(c.participations)
        + len(c.relations) + len(c.evenements) + len(c.idents) + len(c.qualites)
        + len(c.mentions) + len(c.conclusions)
    )
    lot = Lot(
        "gw", fichier, empreinte, "chronologia", __version__,
        maintenant or datetime.now(timezone.utc), "actif", effectif,
    )
    return LotImport(
        tuple(c.passages),
        tuple(c.masques),
        tuple(c.factoides),
        tuple(c.participations),
        tuple(c.relations),
        tuple(c.evenements),
        tuple(c.idents),
        tuple(c.qualites),
        tuple(c.mentions),
        tuple(c.conclusions),
        lot,
    )
