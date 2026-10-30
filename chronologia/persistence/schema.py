"""DDL SQLite de la persistance (décision 18).

Les schémas PostgreSQL ``source``, ``interp`` et ``audit`` sont simulés par un
préfixe de table, pour basculer sans toucher à la logique métier. Les dates sont
stockées en TEXT ISO-8601 (comparaison directe). Toutes les tables sont en
insertion seule (R10). L'identification MASQUE → PERSONNE (décision 19) garde ses
décisions dans un journal (R25), contrôlé à l'insertion par R11 et R18.
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
    cible_masque_id INTEGER REFERENCES source_masque (id),
    argument TEXT NOT NULL,
    valeur TEXT
);
CREATE INDEX IF NOT EXISTS ix_conclusion_cible ON interp_conclusion (cible_masque_id);

CREATE TABLE IF NOT EXISTS interp_conclusion_effet (
    id INTEGER PRIMARY KEY,
    conclusion_id INTEGER NOT NULL REFERENCES interp_conclusion (id),
    type TEXT NOT NULL,
    cible_type TEXT NOT NULL,
    cible_id INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_conclusion_effet_conclusion
    ON interp_conclusion_effet (conclusion_id);
CREATE INDEX IF NOT EXISTS ix_conclusion_effet_cible
    ON interp_conclusion_effet (cible_type, cible_id);

CREATE TABLE IF NOT EXISTS interp_contributeur (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('humain', 'agent', 'import'))
);

CREATE TABLE IF NOT EXISTS interp_personne (
    id INTEGER PRIMARY KEY,
    lot_id INTEGER REFERENCES source_lot_import (id),
    ref TEXT NOT NULL,
    uri TEXT,
    acces TEXT,
    cle_externe TEXT,
    same_as_id INTEGER REFERENCES interp_personne (id)
);
CREATE INDEX IF NOT EXISTS ix_personne_cle_externe ON interp_personne (cle_externe);
CREATE INDEX IF NOT EXISTS ix_personne_same_as ON interp_personne (same_as_id);

CREATE TABLE IF NOT EXISTS interp_ident_personne (
    id INTEGER PRIMARY KEY,
    masque_id INTEGER NOT NULL REFERENCES source_masque (id),
    personne_id INTEGER NOT NULL REFERENCES interp_personne (id),
    degre TEXT NOT NULL CHECK (degre IN ('certain', 'probable', 'possible')),
    contributeur_id INTEGER NOT NULL REFERENCES interp_contributeur (id),
    lot_id INTEGER REFERENCES source_lot_import (id),
    date TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ident_personne_masque ON interp_ident_personne (masque_id);
CREATE INDEX IF NOT EXISTS ix_ident_personne_personne
    ON interp_ident_personne (personne_id);

CREATE TABLE IF NOT EXISTS interp_ident_personne_statut (
    id INTEGER PRIMARY KEY,
    ident_id INTEGER NOT NULL REFERENCES interp_ident_personne (id),
    statut TEXT NOT NULL CHECK (statut IN ('propose', 'actif', 'rejete')),
    conclusion_id INTEGER REFERENCES interp_conclusion (id),
    contributeur_id INTEGER NOT NULL REFERENCES interp_contributeur (id),
    date TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ident_personne_statut_ident
    ON interp_ident_personne_statut (ident_id, date, id);

CREATE TABLE IF NOT EXISTS interp_indice (
    id INTEGER PRIMARY KEY,
    ident_id INTEGER NOT NULL REFERENCES interp_ident_personne (id),
    type TEXT NOT NULL,
    sens TEXT NOT NULL CHECK (sens IN ('pour', 'contre', 'neutre')),
    poids REAL,
    valeur_masque TEXT,
    valeur_personne TEXT,
    mode TEXT NOT NULL CHECK (mode IN ('calcule', 'juge')),
    regle_version TEXT,
    factoide_id INTEGER REFERENCES source_factoide (id),
    conclusion_id INTEGER REFERENCES interp_conclusion (id)
);
CREATE INDEX IF NOT EXISTS ix_indice_ident ON interp_indice (ident_id);

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

-- R25 : le statut courant d'une identification est la dernière ligne de son
-- journal (date, puis id pour départager deux décisions de même date).
CREATE VIEW IF NOT EXISTS interp_ident_personne_actif AS
SELECT ip.*
FROM interp_ident_personne ip
JOIN interp_ident_personne_statut s ON s.ident_id = ip.id
WHERE s.statut = 'actif'
  AND s.id = (
    SELECT s2.id FROM interp_ident_personne_statut s2
    WHERE s2.ident_id = ip.id
    ORDER BY s2.date DESC, s2.id DESC
    LIMIT 1
  );

-- R11 : une seule identification active par masque ; rejeter l'autre d'abord.
CREATE TRIGGER IF NOT EXISTS trg_r11_ident_personne_actif
BEFORE INSERT ON interp_ident_personne_statut
WHEN NEW.statut = 'actif' AND EXISTS (
  SELECT 1 FROM interp_ident_personne_actif a
  JOIN interp_ident_personne n ON n.id = NEW.ident_id
  WHERE a.masque_id = n.masque_id AND a.id <> NEW.ident_id
)
BEGIN
  SELECT RAISE(ABORT, 'R11 violation: le masque a deja une identification active');
END;

-- R18 : la machine propose, l'humain décide ; un agent ne fait que proposer
-- (un désaccord s'exprime par un indice « contre », jamais par un rejet).
CREATE TRIGGER IF NOT EXISTS trg_r18_ident_personne_agent
BEFORE INSERT ON interp_ident_personne_statut
WHEN NEW.statut <> 'propose' AND EXISTS (
  SELECT 1 FROM interp_contributeur c
  WHERE c.id = NEW.contributeur_id AND c.type = 'agent'
)
BEGIN
  SELECT RAISE(ABORT, 'R18 violation: un agent ne peut que proposer une identification');
END;
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
