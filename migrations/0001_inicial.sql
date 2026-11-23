-- Base de datos de WastedMap (Cloudflare D1): votos, confirmaciones y comentarios.

CREATE TABLE IF NOT EXISTS reactions (
  slug    TEXT NOT NULL,
  voter   TEXT NOT NULL,            -- huella anónima, no es la IP
  kind    TEXT NOT NULL CHECK (kind IN ('like', 'dislike')),
  created INTEGER NOT NULL,
  PRIMARY KEY (slug, voter)
);

CREATE TABLE IF NOT EXISTS confirms (
  slug    TEXT NOT NULL,
  voter   TEXT NOT NULL,
  created INTEGER NOT NULL,
  PRIMARY KEY (slug, voter)
);

CREATE TABLE IF NOT EXISTS comments (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  slug       TEXT NOT NULL,
  name       TEXT NOT NULL,
  email_hash TEXT NOT NULL,         -- nunca el mail: solo su huella
  body       TEXT NOT NULL,
  voter      TEXT NOT NULL,
  created    INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS comments_by_slug ON comments (slug, created);
CREATE INDEX IF NOT EXISTS comments_by_voter ON comments (voter, created);
