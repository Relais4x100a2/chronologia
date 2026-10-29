"""DDL SQLite de la persistance (décision 18).

Les schémas PostgreSQL ``source``, ``interp`` et ``audit`` sont simulés par un
préfixe de table, pour basculer sans toucher à la logique métier. Les dates sont
stockées en TEXT ISO-8601 (comparaison directe). Les triggers R10 et la vue des
factoïdes actifs viennent avec les tests suivants.
"""

import sqlite3

_TABLES = """
CREATE TABLE IF NOT EXISTS source_lot_import (
    id INTEGER PRIMARY KEY,
    format TEXT NOT NULL,
    fichier TEXT,
    empreinte TEXT,
    outil TEXT NOT NULL,
    version TEXT NOT NULL,
    date_import TEXT NOT NULL,
    statut TEXT NOT NULL,
    nb_entites INTEGER NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_lot_format_empreinte
    ON source_lot_import (format, empreinte);

CREATE TABLE IF NOT EXISTS source_passage (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    ref TEXT NOT NULL,
    citation_brute TEXT,
    fichier_source TEXT,
    ligne_debut INTEGER,
    ligne_fin INTEGER,
    transcription TEXT,
    cle_externe TEXT
);
CREATE INDEX IF NOT EXISTS ix_passage_cle_externe ON source_passage (cle_externe);
CREATE UNIQUE INDEX IF NOT EXISTS ux_passage_lot_ref ON source_passage (lot_id, ref);

CREATE TABLE IF NOT EXISTS source_masque (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    ref TEXT NOT NULL,
    passage_id INTEGER NOT NULL REFERENCES source_passage (id),
    nom_ecrit TEXT NOT NULL,
    sexe TEXT,
    cle_externe TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_masque_cle_externe ON source_masque (cle_externe);
CREATE UNIQUE INDEX IF NOT EXISTS ux_masque_lot_ref ON source_masque (lot_id, ref);

CREATE TABLE IF NOT EXISTS source_factoide (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    ref TEXT NOT NULL,
    passage_id INTEGER NOT NULL REFERENCES source_passage (id),
    type_evenement TEXT,
    date_declaree TEXT,
    date_brute TEXT,
    date_min TEXT,
    date_max TEXT,
    calendrier TEXT,
    date_incertaine INTEGER NOT NULL DEFAULT 0,
    cle_famille TEXT
);
CREATE INDEX IF NOT EXISTS ix_factoide_cle_famille ON source_factoide (cle_famille);
CREATE INDEX IF NOT EXISTS ix_factoide_dates ON source_factoide (date_min, date_max);
CREATE UNIQUE INDEX IF NOT EXISTS ux_factoide_lot_ref ON source_factoide (lot_id, ref);

CREATE TABLE IF NOT EXISTS source_participation (
    factoide_id INTEGER NOT NULL REFERENCES source_factoide (id),
    masque_id INTEGER NOT NULL REFERENCES source_masque (id),
    role TEXT NOT NULL,
    ordre INTEGER NOT NULL,
    note TEXT,
    PRIMARY KEY (factoide_id, masque_id, role, ordre)
);
CREATE INDEX IF NOT EXISTS ix_participation_masque ON source_participation (masque_id);

CREATE TABLE IF NOT EXISTS source_relation (
    id INTEGER PRIMARY KEY,
    factoide_id INTEGER NOT NULL REFERENCES source_factoide (id),
    sujet_masque_id INTEGER NOT NULL REFERENCES source_masque (id),
    objet_masque_id INTEGER NOT NULL REFERENCES source_masque (id),
    type_relation TEXT NOT NULL,
    orientation TEXT,
    degre TEXT NOT NULL DEFAULT 'certain'
);
CREATE INDEX IF NOT EXISTS ix_relation_factoide ON source_relation (factoide_id);
CREATE INDEX IF NOT EXISTS ix_relation_sujet ON source_relation (sujet_masque_id);
CREATE INDEX IF NOT EXISTS ix_relation_objet ON source_relation (objet_masque_id);

CREATE TABLE IF NOT EXISTS source_qualite (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    ref TEXT NOT NULL,
    factoide_id INTEGER NOT NULL REFERENCES source_factoide (id),
    masque_id INTEGER NOT NULL REFERENCES source_masque (id),
    categorie TEXT NOT NULL,
    role TEXT NOT NULL,
    valide_debut TEXT,
    valide_fin TEXT,
    rang INTEGER
);
CREATE INDEX IF NOT EXISTS ix_qualite_masque ON source_qualite (masque_id);

CREATE TABLE IF NOT EXISTS source_mention_lieu (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    ref TEXT NOT NULL,
    factoide_id INTEGER NOT NULL REFERENCES source_factoide (id),
    forme_ecrite TEXT NOT NULL,
    forme_normalisee TEXT,
    fonction TEXT NOT NULL,
    masque_id INTEGER REFERENCES source_masque (id),
    qualite_id INTEGER REFERENCES source_qualite (id),
    epoque_designation TEXT NOT NULL DEFAULT 'moderne'
);
CREATE INDEX IF NOT EXISTS ix_mention_lieu_forme ON source_mention_lieu (forme_normalisee);

CREATE TABLE IF NOT EXISTS interp_evenement (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    ref TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interp_ident_evenement (
    id INTEGER PRIMARY KEY,
    factoide_id INTEGER NOT NULL REFERENCES source_factoide (id),
    evenement_id INTEGER NOT NULL REFERENCES interp_evenement (id),
    degre TEXT NOT NULL,
    statut TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ident_evenement_factoide
    ON interp_ident_evenement (factoide_id);

CREATE TABLE IF NOT EXISTS interp_conclusion (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    ref TEXT NOT NULL,
    cible_masque_id INTEGER NOT NULL REFERENCES source_masque (id),
    argument TEXT NOT NULL,
    valeur TEXT
);
CREATE INDEX IF NOT EXISTS ix_conclusion_cible ON interp_conclusion (cible_masque_id);

CREATE TABLE IF NOT EXISTS audit_retractation (
    id INTEGER PRIMARY KEY,
    cible_table TEXT NOT NULL,
    cible_id INTEGER NOT NULL,
    lot_id INTEGER NOT NULL REFERENCES source_lot_import (id),
    motif TEXT,
    date_retractation TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_retractation_cible
    ON audit_retractation (cible_table, cible_id);

CREATE VIEW IF NOT EXISTS source_factoide_actif AS
SELECT f.*
FROM source_factoide f
LEFT JOIN audit_retractation r
  ON r.cible_table = 'source_factoide' AND r.cible_id = f.id
WHERE r.id IS NULL;

CREATE VIEW IF NOT EXISTS interp_conclusion_actif AS
SELECT c.*
FROM interp_conclusion c
LEFT JOIN audit_retractation r
  ON r.cible_table = 'interp_conclusion' AND r.cible_id = c.id
WHERE r.id IS NULL;
"""


def _triggers_append_only(con: sqlite3.Connection) -> str:
    """Un trigger par table et par opération : R10, insertion seule."""
    tables = [
        r[0]
        for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND "
            "(name LIKE 'source\\_%' ESCAPE '\\' OR name LIKE 'interp\\_%' ESCAPE '\\' "
            "OR name LIKE 'audit\\_%' ESCAPE '\\')"
        )
    ]
    return "".join(
        f"CREATE TRIGGER IF NOT EXISTS trg_no_{op.lower()}_{t} BEFORE {op} ON {t} "
        f"BEGIN SELECT RAISE(ABORT, 'R10 violation: {t} est en insertion seule'); END;\n"
        for t in tables
        for op in ("UPDATE", "DELETE")
    )


def creer_schema(con: sqlite3.Connection) -> None:
    """Crée tables, index et triggers R10 (idempotent)."""
    con.executescript(_TABLES)
    con.executescript(_triggers_append_only(con))
