PRAGMA foreign_keys = ON;

CREATE TABLE invoice_header (
  invoice_id        INTEGER PRIMARY KEY,
  invoice_number    TEXT NOT NULL UNIQUE,
  customer_id       INTEGER NOT NULL,
  invoice_date      TEXT NOT NULL,          -- ISO-8601 date: YYYY-MM-DD
  due_date          TEXT,                   -- optional
  currency_code     TEXT NOT NULL,          -- e.g., USD
  status            TEXT NOT NULL DEFAULT 'draft',
  subtotal_amount   REAL NOT NULL DEFAULT 0,
  tax_amount        REAL NOT NULL DEFAULT 0,
  total_amount      REAL NOT NULL DEFAULT 0,
  notes             TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE invoice_line (
  line_id           INTEGER PRIMARY KEY,
  invoice_id        INTEGER NOT NULL,
  line_number       INTEGER NOT NULL,
  item_code         TEXT,
  description       TEXT NOT NULL,
  quantity          REAL NOT NULL DEFAULT 1,
  unit_price        REAL NOT NULL DEFAULT 0,
  discount_amount   REAL NOT NULL DEFAULT 0,
  tax_amount        REAL NOT NULL DEFAULT 0,
  line_total        REAL NOT NULL DEFAULT 0,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at        TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (invoice_id)
    REFERENCES invoice_header(invoice_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  UNIQUE (invoice_id, line_number)
);

CREATE INDEX idx_invoice_line_invoice_id
  ON invoice_line(invoice_id);

CREATE INDEX idx_invoice_header_customer_id
  ON invoice_header(customer_id);
