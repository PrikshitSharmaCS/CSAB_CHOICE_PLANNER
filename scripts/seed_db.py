#!/usr/bin/env python3
"""
Seed CSAB database with extracted data.
"""

import sqlite3
import csv
import os
from pathlib import Path

# Database and schema paths
DB_PATH = Path(__file__).parent.parent / "csab.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
EXTRACTED_DIR = Path(__file__).parent.parent / "extracted"

# CSV file paths
INSTITUTES_CSV = EXTRACTED_DIR / "institutes.csv"
PROGRAMS_CSV = EXTRACTED_DIR / "programs.csv"
CUTOFFS_CSV = EXTRACTED_DIR / "cutoffs.csv"


def load_schema(conn):
    """Load and execute schema from SQL file."""
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    print("✓ Schema loaded")


def load_institutes(conn):
    """Load institutes from CSV."""
    cursor = conn.cursor()
    with open(INSTITUTES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO institutes (name) VALUES (?)",
                (row['institute'],)
            )
    conn.commit()
    print("✓ Institutes loaded")


def load_programs(conn):
    """Load programs from CSV."""
    cursor = conn.cursor()
    with open(PROGRAMS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO programs (name) VALUES (?)",
                (row['program'],)
            )
    conn.commit()
    print("✓ Programs loaded")


def load_cutoffs(conn):
    """Load cutoffs from CSV."""
    cursor = conn.cursor()
    
    with open(CUTOFFS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get institute_id
            cursor.execute("SELECT id FROM institutes WHERE name = ?", (row['institute'],))
            institute_result = cursor.fetchone()
            if not institute_result:
                continue
            institute_id = institute_result[0]
            
            # Get program_id
            cursor.execute("SELECT id FROM programs WHERE name = ?", (row['program'],))
            program_result = cursor.fetchone()
            if not program_result:
                continue
            program_id = program_result[0]
            
            cursor.execute(
                """INSERT INTO cutoffs 
                   (institute_id, program_id, quota, seat_type, gender, opening_rank, closing_rank)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (institute_id, program_id, row['quota'], row['seat_type'], row['gender'],
                 int(row['opening_rank']), int(row['closing_rank']))
            )
    conn.commit()
    print("✓ Cutoffs loaded")


def print_summary(conn):
    """Print database summary and sample rows."""
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("DATABASE SUMMARY")
    print("=" * 70)
    
    # Count rows
    cursor.execute("SELECT COUNT(*) FROM institutes")
    institute_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM programs")
    program_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cutoffs")
    cutoff_count = cursor.fetchone()[0]
    
    print(f"\nTotal institutes: {institute_count}")
    print(f"Total programs: {program_count}")
    print(f"Total cutoffs: {cutoff_count}")
    
    # Sample institutes
    print("\n" + "-" * 70)
    print("SAMPLE INSTITUTES (5 rows):")
    print("-" * 70)
    cursor.execute("SELECT id, name FROM institutes LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Name: {row[1]}")
    
    # Sample programs
    print("\n" + "-" * 70)
    print("SAMPLE PROGRAMS (5 rows):")
    print("-" * 70)
    cursor.execute("SELECT id, name FROM programs LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Name: {row[1]}")
    
    # Sample cutoffs
    print("\n" + "-" * 70)
    print("SAMPLE CUTOFFS (5 rows):")
    print("-" * 70)
    cursor.execute("""
        SELECT c.id, i.name, p.name, c.quota, c.seat_type, c.gender, c.opening_rank, c.closing_rank
        FROM cutoffs c
        JOIN institutes i ON c.institute_id = i.id
        JOIN programs p ON c.program_id = p.id
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}")
        print(f"    Institute: {row[1]}")
        print(f"    Program: {row[2]}")
        print(f"    Quota: {row[3]}, Seat Type: {row[4]}, Gender: {row[5]}")
        print(f"    Opening Rank: {row[6]}, Closing Rank: {row[7]}")
    
    print("\n" + "=" * 70)


def main():
    """Main function to create and seed the database."""
    # Remove existing database if present
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")
    
    # Create connection
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        print(f"Creating database: {DB_PATH}\n")
        load_schema(conn)
        load_institutes(conn)
        load_programs(conn)
        load_cutoffs(conn)
        print_summary(conn)
        print(f"\n✓ Database created successfully at: {DB_PATH}")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
