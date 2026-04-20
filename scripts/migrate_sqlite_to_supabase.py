import argparse
import sqlite3
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch


DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[1] / "db.sqlite3"
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql" / "schema_supabase.sql"


def discover_sqlite_path(project_root):
    candidates = [
        project_root / "db.sqlite3",
        project_root / "database.sqlite3",
        project_root / "app.db",
        project_root / "database.db",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def parse_args():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to Supabase Postgres")
    parser.add_argument("--sqlite-path", default=str(DEFAULT_SQLITE_PATH), help="Path to SQLite database file")
    parser.add_argument("--postgres-url", required=True, help="Supabase Postgres connection URL")
    parser.add_argument("--schema-path", default=str(DEFAULT_SCHEMA_PATH), help="Path to Postgres schema SQL file")
    parser.add_argument("--dry-run", action="store_true", help="Read and verify only; do not write to Postgres")
    return parser.parse_args()


def split_sql_statements(sql_text):
    return [s.strip() for s in sql_text.split(";") if s.strip()]


def load_schema(pg_conn, schema_path):
    schema_sql = Path(schema_path).read_text(encoding="utf-8")
    with pg_conn.cursor() as cursor:
        for statement in split_sql_statements(schema_sql):
            cursor.execute(statement)
    pg_conn.commit()


def get_sqlite_tables(sqlite_conn):
    cursor = sqlite_conn.cursor()
    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [row[0] for row in cursor.fetchall()]


def get_table_columns(sqlite_conn, table_name):
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def fetch_rows(sqlite_conn, table_name, columns):
    cursor = sqlite_conn.cursor()
    quoted_cols = ", ".join(columns)
    cursor.execute(f"SELECT {quoted_cols} FROM {table_name}")
    return cursor.fetchall()


def copy_table(pg_conn, table_name, columns, rows):
    if not rows:
        return 0

    insert_stmt = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(sql.Identifier(c) for c in columns),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
    )
    with pg_conn.cursor() as cursor:
        execute_batch(cursor, insert_stmt.as_string(pg_conn), rows, page_size=500)
    return len(rows)


def reset_sequence(pg_conn, table_name):
    with pg_conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT pg_get_serial_sequence(%s, 'id')
            """,
            (table_name,),
        )
        seq_row = cursor.fetchone()
        if not seq_row or not seq_row[0]:
            return
        sequence_name = seq_row[0]
        cursor.execute(
            sql.SQL(
                "SELECT setval({}, COALESCE((SELECT MAX(id) FROM {}), 1), true)"
            ).format(
                sql.Literal(sequence_name),
                sql.Identifier(table_name),
            )
        )


def get_postgres_count(pg_conn, table_name):
    with pg_conn.cursor() as cursor:
        cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
        return cursor.fetchone()[0]


def main():
    args = parse_args()
    sqlite_path = Path(args.sqlite_path)

    # If default path does not exist, try auto-discovery before failing.
    if not sqlite_path.exists() and sqlite_path == DEFAULT_SQLITE_PATH:
        discovered = discover_sqlite_path(Path(__file__).resolve().parents[1])
        if discovered:
            sqlite_path = discovered

    if not sqlite_path.exists():
        raise FileNotFoundError(
            "SQLite DB not found.\n"
            f"Tried: {sqlite_path}\n"
            "Pass the explicit source DB path:\n"
            "python scripts/migrate_sqlite_to_supabase.py "
            "--sqlite-path \"D:/path/to/your.sqlite3\" --postgres-url \"<your_supabase_postgres_url>\""
        )

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(args.postgres_url)

    try:
        load_schema(pg_conn, args.schema_path)

        table_order = [
            "users",
            "doctors",
            "patients",
            "reports",
            "report_anomalies",
            "chat_messages",
            "tasks",
            "shared_reports",
            "report_comments",
            "referrals",
            "patient_vitals",
            "appointments",
            "prescriptions",
            "notifications",
            "documents",
            "messages",
            "audit_logs",
            "doctor_schedules",
            "risk_scores",
        ]

        existing = set(get_sqlite_tables(sqlite_conn))
        migration_tables = [t for t in table_order if t in existing]
        skipped = sorted(existing - set(migration_tables))

        print("== SQLite -> Supabase migration ==")
        print(f"SQLite source: {sqlite_path}")
        print(f"Dry run: {args.dry_run}")
        if skipped:
            print(f"Skipping unmanaged tables: {', '.join(skipped)}")

        for table_name in migration_tables:
            columns = get_table_columns(sqlite_conn, table_name)
            rows = fetch_rows(sqlite_conn, table_name, columns)
            print(f"{table_name}: source rows={len(rows)}")

            if args.dry_run:
                continue

            with pg_conn.cursor() as cursor:
                cursor.execute(sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(sql.Identifier(table_name)))
            inserted = copy_table(pg_conn, table_name, columns, rows)
            reset_sequence(pg_conn, table_name)
            pg_conn.commit()

            target_count = get_postgres_count(pg_conn, table_name)
            print(f"{table_name}: inserted={inserted}, target rows={target_count}")

        if args.dry_run:
            print("Dry run complete. No data was written to Supabase.")
        else:
            print("Migration complete.")
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
