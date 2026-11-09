-- CSAB Database Schema

CREATE TABLE IF NOT EXISTS institutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cutoffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institute_id INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    quota TEXT,
    seat_type TEXT,
    gender TEXT,
    opening_rank INTEGER,
    closing_rank INTEGER,
    FOREIGN KEY (institute_id) REFERENCES institutes(id),
    FOREIGN KEY (program_id) REFERENCES programs(id)
);

CREATE INDEX IF NOT EXISTS idx_cutoffs_institute ON cutoffs(institute_id);
CREATE INDEX IF NOT EXISTS idx_cutoffs_program ON cutoffs(program_id);
