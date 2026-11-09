"""
parse_pdf.py
============
Robust parser for the CSAB ORCR (Opening Rank / Closing Rank) PDF.

Fixes applied
-------------
1. Uses extract_tables() (plural) – handles multiple tables per page.
2. Header guard – skips repeated header rows that appear mid-table.
3. Forward-fill – repairs multi-line / merged rows where cells are None.
4. Column-variant normalisation – maps known alternate column names to
   the canonical 7-column schema.
5. Three-layer validation report – ensures no cutoff rows are silently lost.
6. Per-page logging – prints page number + rows extracted from each page.

Output (written to `extracted/`)
---------------------------------
  institutes.csv / institutes.json
  programs.csv   / programs.json
  cutoffs.csv    / cutoffs.json

Usage
-----
  python scripts/parse_pdf.py
"""

import json
import logging
import pathlib
import sys

import pandas as pd
import pdfplumber

# ---------------------------------------------------------------------------
# Logging setup – prints to console with timestamp and level
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger("parse_pdf")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR  = pathlib.Path(__file__).resolve().parent
ROOT_DIR    = SCRIPT_DIR.parent                                  # project root
PDF_PATH    = ROOT_DIR / "DATA" / "CSAB FOLDER.pdf"
OUTPUT_DIR  = ROOT_DIR / "extracted"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Canonical column schema (7 fields)
# ---------------------------------------------------------------------------
CANONICAL_COLUMNS = [
    "institute",
    "program",
    "quota",
    "seat_type",
    "gender",
    "opening_rank",
    "closing_rank",
]

# All known variants (lowercase, stripped) → canonical name
# Add more variants here if the PDF uses different spellings.
COLUMN_VARIANT_MAP = {
    "institute"                            : "institute",
    "institute name"                       : "institute",
    "institution"                          : "institute",
    "academic program name"                : "program",
    "program name"                         : "program",
    "programme name"                       : "program",
    "branch"                               : "program",
    "quota"                                : "quota",
    "seat type"                            : "seat_type",
    "seattype"                             : "seat_type",
    "category"                             : "seat_type",
    "gender"                               : "gender",
    "gender pool"                          : "gender",
    "opening rank"                         : "opening_rank",
    "or"                                   : "opening_rank",
    "closing rank"                         : "closing_rank",
    "cr"                                   : "closing_rank",
}

# Words that identify a row as a header (used by the header guard)
HEADER_KEYWORDS = {"institute", "quota", "opening rank", "closing rank", "seat type"}

# ---------------------------------------------------------------------------
# Value normalisation maps (applied after extraction)
# ---------------------------------------------------------------------------
QUOTA_MAP = {
    "home state"             : "HS",
    "home state for goa"     : "HS",
    "other state"            : "OS",
    "all india"              : "AI",
    "dasa ciwg"              : "DASA_CIWG",
    "dasa- ciwg"             : "DASA_CIWG",    # stray space from PDF
    "dasa non ciwg"          : "DASA_NON_CIWG",
    "dasa- non ciwg"         : "DASA_NON_CIWG", # stray space from PDF
    "jammu & kashmir"        : "JK",
    "jammu & kashmir (ut)"   : "JK",            # full UT label from PDF
    "jammu and kashmir"      : "JK",
    "j&k"                    : "JK",
}

SEAT_TYPE_MAP = {
    "open"             : "OPEN",
    "ews"              : "EWS",
    "obc ncl"          : "OBC-NCL",
    "obc-ncl"          : "OBC-NCL",
    "obc- ncl"         : "OBC-NCL",  # stray space from PDF
    "sc"               : "SC",
    "st"               : "ST",
    "open (pwd)"       : "OPEN-PWD",
    "open (pwbd)"      : "OPEN-PWD",
    "open-pwd"         : "OPEN-PWD",
    "ews (pwd)"        : "EWS-PWD",
    "ews-pwd"          : "EWS-PWD",
    "obc ncl (pwd)"    : "OBC-NCL-PWD",
    "obc- ncl (pwd)"   : "OBC-NCL-PWD", # stray space from PDF
    "obc-ncl (pwd)"    : "OBC-NCL-PWD",
    "sc (pwd)"         : "SC-PWD",
    "st (pwd)"         : "ST-PWD",
}

GENDER_MAP = {
    "gender-neutral"                              : "GN",
    "gender neutral"                              : "GN",
    "female-only (including supernumerary)"       : "F",
    "female only (including supernumerary)"       : "F",
    "female-only"                                 : "F",
    "female only"                                 : "F",
}

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def clean_cell(val) -> str | None:
    """Strip whitespace and embedded newlines; return None for empty cells."""
    if val is None:
        return None
    s = str(val).strip().replace("\n", " ").replace("\r", " ")
    return s if s else None


def is_header_row(row: list) -> bool:
    """Return True if the row looks like a column-header row."""
    lowered = {(clean_cell(c) or "").lower() for c in row}
    return bool(lowered & HEADER_KEYWORDS)


def map_header(raw_header: list) -> list | None:
    """
    Map a raw header row to canonical column names.
    Returns None if the mapping fails for more than one column.
    """
    mapped = []
    failures = []
    for cell in raw_header:
        key = (clean_cell(cell) or "").lower().strip()
        canonical = COLUMN_VARIANT_MAP.get(key)
        if canonical:
            mapped.append(canonical)
        else:
            failures.append(repr(cell))

    if len(failures) > 1:
        return None   # caller will log a warning
    return mapped


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract_all_rows(pdf_path: pathlib.Path):
    """
    Open the PDF and extract every data row from every table on every page.

    Returns
    -------
    rows        : list[list[str|None]]  – raw data rows (no headers)
    header      : list[str]             – canonical column names
    stats       : dict                  – per-page and aggregate counters
    """
    rows: list[list] = []
    header: list[str] | None = None
    stats = {
        "pages_processed"    : 0,
        "tables_found"       : 0,
        "raw_rows_seen"      : 0,
        "header_rows_skipped": 0,
        "malformed_skipped"  : 0,
        "per_page"           : [],   # list of (page_no, tables, rows_added)
    }

    with pdfplumber.open(str(pdf_path)) as pdf:
        total_pages = len(pdf.pages)
        log.info(f"PDF opened: {pdf_path.name}  |  Total pages: {total_pages}")

        for page_no, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()        # FIX 1: plural – all tables on page
            page_rows_added = 0

            if not tables:
                log.debug(f"  Page {page_no:>4}: no tables found")
                stats["per_page"].append((page_no, 0, 0))
                continue

            stats["pages_processed"] += 1
            stats["tables_found"]    += len(tables)

            for tbl_idx, table in enumerate(tables, start=1):
                for row_idx, raw_row in enumerate(table):
                    stats["raw_rows_seen"] += 1

                    # Clean individual cells
                    row = [clean_cell(c) for c in raw_row]

                    # FIX 2: Header guard – detect and skip repeated headers
                    if is_header_row(row):
                        if header is None:
                            # First header encounter – derive canonical columns
                            mapped = map_header(row)
                            if mapped is None:
                                log.warning(
                                    f"  Page {page_no}, table {tbl_idx}, row {row_idx}: "
                                    f"header mapping failed for row: {row}"
                                )
                                stats["malformed_skipped"] += 1
                                continue
                            header = mapped
                            log.info(
                                f"  Page {page_no}, table {tbl_idx}: "
                                f"header detected -> {header}"
                            )
                        else:
                            # Repeated header row – skip it
                            log.debug(
                                f"  Page {page_no}, table {tbl_idx}, row {row_idx}: "
                                f"repeated header skipped"
                            )
                            stats["header_rows_skipped"] += 1
                        continue

                    # Guard: we must have a header before accepting data rows
                    if header is None:
                        log.warning(
                            f"  Page {page_no}: data row encountered before any header – skipped: {row}"
                        )
                        stats["malformed_skipped"] += 1
                        continue

                    # FIX 4: Column count validation
                    if len(row) != len(header):
                        log.warning(
                            f"  Page {page_no}, table {tbl_idx}, row {row_idx}: "
                            f"column count mismatch "
                            f"(expected {len(header)}, got {len(row)}) – skipped: {row}"
                        )
                        stats["malformed_skipped"] += 1
                        continue

                    rows.append(row)
                    page_rows_added += 1

            log.info(
                f"  Page {page_no:>4}/{total_pages}: "
                f"{len(tables)} table(s) found, "
                f"{page_rows_added} data row(s) added  "
                f"[running total: {len(rows)}]"
            )
            stats["per_page"].append((page_no, len(tables), page_rows_added))

    return rows, header, stats


# ---------------------------------------------------------------------------
# Build DataFrame with forward-fill and value normalisation
# ---------------------------------------------------------------------------

def build_dataframe(rows: list, header: list) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=header)

    # FIX 3: Forward-fill institute and program columns
    #         (handles multi-line / merged cells where continuation rows are None)
    ff_before = df[["institute", "program"]].isna().sum().sum()
    df["institute"] = df["institute"].ffill()
    df["program"]   = df["program"].ffill()
    ff_after = df[["institute", "program"]].isna().sum().sum()
    ff_fixed = int(ff_before - ff_after)
    if ff_fixed:
        log.info(f"Forward-fill repaired {ff_fixed} empty institute/program cell(s)")

    # Normalise categorical fields (lowercase comparison for robustness)
    def normalise(series, mapping):
        return series.map(
            lambda v: mapping.get((v or "").lower().strip(), v)
        )

    df["quota"]     = normalise(df["quota"],     QUOTA_MAP)
    df["seat_type"] = normalise(df["seat_type"], SEAT_TYPE_MAP)
    df["gender"]    = normalise(df["gender"],    GENDER_MAP)

    # Parse rank columns – strip commas, convert to integer
    for col in ["opening_rank", "closing_rank"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
            .pipe(pd.to_numeric, errors="coerce")
            .astype("Int64")
        )

    return df, ff_fixed


# ---------------------------------------------------------------------------
# Validation report
# ---------------------------------------------------------------------------

def validate(df: pd.DataFrame, stats: dict, ff_fixed: int):
    raw_seen        = stats["raw_rows_seen"]
    header_skipped  = stats["header_rows_skipped"]
    malformed       = stats["malformed_skipped"]
    written         = len(df)
    accounted       = written + header_skipped + malformed

    null_open  = int(df["opening_rank"].isna().sum())
    null_close = int(df["closing_rank"].isna().sum())

    print("\n" + "=" * 55)
    print("  VALIDATION REPORT")
    print("=" * 55)
    print(f"  Total raw rows seen (all pages)  : {raw_seen:>7,}")
    print(f"  Header rows skipped              : {header_skipped:>7,}")
    print(f"  Malformed / short rows skipped   : {malformed:>7,}")
    print(f"  Rows written to cutoffs.csv      : {written:>7,}")
    print(f"  Forward-filled cells repaired    : {ff_fixed:>7,}")
    print("-" * 55)
    print(f"  Rows accounted for               : {accounted:>7,}")

    if accounted != raw_seen:
        lost = raw_seen - accounted
        print(f"\n  [WARNING] {lost} row(s) are unaccounted for!")
        print(f"     (raw_seen={raw_seen} != written+skipped={accounted})")
    else:
        print(f"\n  [OK] All rows accounted for. No silent data loss.")

    if null_open or null_close:
        print(f"\n  [WARNING] Null/unparseable opening_rank : {null_open}")
        print(f"     Null/unparseable closing_rank  : {null_close}")
        print(f"     Review `extracted/cutoffs.csv` for these rows.")
    else:
        print(f"  [OK] All rank values parsed successfully.")
    print("=" * 55 + "\n")

    if accounted != raw_seen:
        raise RuntimeError(
            f"{raw_seen - accounted} row(s) were silently lost during extraction. "
            "Review the log above for warnings."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=== CSAB ORCR PDF Parser starting ===")

    if not PDF_PATH.exists():
        log.error(f"PDF not found: {PDF_PATH}")
        sys.exit(1)

    # Step 1 – Extract raw rows
    rows, header, stats = extract_all_rows(PDF_PATH)

    if not rows or header is None:
        log.error("No data rows extracted. Check warnings above.")
        sys.exit(1)

    log.info(
        f"Extraction complete: "
        f"{stats['pages_processed']} pages processed, "
        f"{stats['tables_found']} table(s) found, "
        f"{len(rows)} raw data rows collected."
    )

    # Step 2 – Build normalised DataFrame
    df, ff_fixed = build_dataframe(rows, header)

    # Step 3 – Split into logical tables
    institutes = (
        df[["institute"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    programs = (
        df[["program"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    cutoffs = df.copy()

    # Step 4 – Save to CSV and JSON
    institutes.to_csv(OUTPUT_DIR / "institutes.csv", index=False)
    programs.to_csv(  OUTPUT_DIR / "programs.csv",   index=False)
    cutoffs.to_csv(   OUTPUT_DIR / "cutoffs.csv",    index=False)

    institutes.to_json(OUTPUT_DIR / "institutes.json", orient="records", indent=2)
    programs.to_json(  OUTPUT_DIR / "programs.json",   orient="records", indent=2)
    cutoffs.to_json(   OUTPUT_DIR / "cutoffs.json",    orient="records", indent=2)

    log.info(f"Files written to: {OUTPUT_DIR}")

    # Step 5 – Print the summary requested by the user
    print("\n" + "=" * 55)
    print("  EXTRACTION SUMMARY")
    print("=" * 55)
    print(f"  Institutes extracted : {len(institutes):>7,}")
    print(f"  Programs extracted   : {len(programs):>7,}")
    print(f"  Cutoff rows extracted: {len(cutoffs):>7,}")
    print("=" * 55)

    print("\nFirst 10 cutoff rows (as JSON):")
    print(json.dumps(cutoffs.head(10).to_dict(orient="records"), indent=2, ensure_ascii=False))

    # Step 6 – Validate (raises RuntimeError on silent data loss)
    validate(cutoffs, stats, ff_fixed)

    log.info("=== Parser finished successfully ===")


if __name__ == "__main__":
    main()
