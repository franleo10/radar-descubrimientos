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

-- Gente online: último aviso de cada huella anónima (la crea también /api/online si falta).
CREATE TABLE IF NOT EXISTS presence (
  voter TEXT PRIMARY KEY,
  seen  INTEGER NOT NULL
);

-- Panel de administración (también se crean solas desde functions/_lib.js -> ensureSchema).
CREATE TABLE IF NOT EXISTS bans (
  key     TEXT PRIMARY KEY,         -- huella anónima o huella del mail
  kind    TEXT NOT NULL,            -- 'voter' o 'email'
  name    TEXT NOT NULL DEFAULT '', -- nombre que usaba, para reconocerlo en el panel
  reason  TEXT NOT NULL DEFAULT '',
  created INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rejected (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  slug       TEXT NOT NULL,
  name       TEXT NOT NULL,
  email_hash TEXT NOT NULL,
  body       TEXT NOT NULL,
  reason     TEXT NOT NULL,         -- por qué no lo publicó la moderación automática
  voter      TEXT NOT NULL,
  created    INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS rejected_by_created ON rejected (created);
