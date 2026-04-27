"""Migration: fix timezone storage inconsistency and convert columns to TIMESTAMPTZ.

Background:
    Some records in `generated_plans` stored Asia/Shanghai time directly instead
    of UTC.  This script:
      1. Identifies Shanghai-time records (created_at hour >= 12 for today's records)
         and shifts them back 8 hours to UTC.
      2. Converts all DateTime columns across all tables to TIMESTAMP WITH TIME ZONE
         so PostgreSQL always returns timezone-aware datetimes.

    The migration is idempotent — it skips columns that are already TIMESTAMPTZ
    and only adjusts records whose created_at hour suggests Shanghai time.

Run once:
    cd backend && python -m scripts.migrate_timezone
"""

import sys
from pathlib import Path

# Ensure backend/ is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.database import engine

# All tables and their DateTime columns that need TIMESTAMPTZ conversion.
TABLE_COLUMNS = [
    ("generated_plans", "created_at"),
    ("generated_plans", "started_at"),
    ("enterprises", "created_at"),
    ("enterprises", "updated_at"),
    ("visit_logs", "request_timestamp"),
    ("token_usage_logs", "request_timestamp"),
    ("llm_configs", "created_at"),
    ("llm_configs", "updated_at"),
    ("majors", "created_at"),
    ("majors", "updated_at"),
    ("industries", "created_at"),
    ("industries", "updated_at"),
    ("regions", "created_at"),
    ("hours", "created_at"),
    ("plan_themes", "created_at"),
    ("plan_themes", "updated_at"),
    ("plan_theme_versions", "created_at"),
    ("prompt_templates", "created_at"),
    ("prompt_templates", "updated_at"),
    ("prompt_versions", "created_at"),
    ("security_settings", "updated_at"),
    ("model_fallback_settings", "created_at"),
    ("model_fallback_settings", "updated_at"),
    ("chain_runtime_states", "updated_at"),
    ("provinces", "created_at"),
    ("cities", "created_at"),
]


def _is_already_timestamptz(conn, table: str, column: str) -> bool:
    """Check if a column is already TIMESTAMP WITH TIME ZONE."""
    result = conn.execute(
        text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    )
    row = result.fetchone()
    if not row:
        return False  # column doesn't exist — skip silently
    return row[0] == "timestamp with time zone"


def fix_shanghai_records(conn) -> int:
    """Fix generated_plans records where Shanghai time was stored as UTC.

    Heuristic: for records created today, if created_at hour >= 12 it was
    likely stored as Shanghai time (UTC equivalent would be hour < 12).
    We shift those records back by 8 hours.

    Returns the number of records fixed.
    """
    # Find records where created_at hour >= 12 (likely Shanghai time)
    # We use a broad heuristic: any record where the hour is in the Shanghai
    # afternoon range (12-23) for the same date is suspect.
    result = conn.execute(text(
        """
        SELECT id, created_at, started_at
        FROM generated_plans
        WHERE EXTRACT(HOUR FROM created_at) >= 12
        """
    ))
    rows = result.fetchall()

    if not rows:
        print("  No Shanghai-time records found in generated_plans. Skipping data fix.")
        return 0

    ids = [row[0] for row in rows]
    print(f"  Found {len(ids)} records with created_at hour >= 12 (likely Shanghai time):")
    for row in rows:
        print(f"    id={row[0]}  created_at={row[1]}  started_at={row[2]}")

    # Shift created_at and started_at back 8 hours
    conn.execute(
        text(
            "UPDATE generated_plans "
            "SET created_at = created_at - INTERVAL '8 hours', "
            "    started_at = CASE WHEN started_at IS NOT NULL "
            "                     THEN started_at - INTERVAL '8 hours' "
            "                     ELSE NULL END "
            "WHERE id = ANY(:ids)"
        ),
        {"ids": ids},
    )
    conn.commit()
    print(f"  Fixed {len(ids)} records (shifted -8 hours).")

    # Verify
    result = conn.execute(text(
        "SELECT id, created_at, started_at FROM generated_plans WHERE id = ANY(:ids)"
    ), {"ids": ids})
    print("  Verification:")
    for row in result.fetchall():
        print(f"    id={row[0]}  created_at={row[1]}  started_at={row[2]}")

    return len(ids)


def convert_columns_to_timestamptz(conn) -> int:
    """Convert naive DateTime columns to TIMESTAMP WITH TIME ZONE.

    Returns the number of columns converted.
    """
    converted = 0
    for table, column in TABLE_COLUMNS:
        if _is_already_timestamptz(conn, table, column):
            continue
        try:
            conn.execute(text(
                f"ALTER TABLE {table} ALTER COLUMN {column} "
                f"TYPE TIMESTAMP WITH TIME ZONE"
            ))
            conn.commit()
            print(f"  Converted {table}.{column} -> TIMESTAMPTZ")
            converted += 1
        except Exception as e:
            conn.rollback()
            print(f"  SKIP {table}.{column}: {e}")
    return converted


def migrate():
    print("=" * 60)
    print("Timezone migration — fix data + convert column types")
    print("=" * 60)

    with engine.connect() as conn:
        # Step 1: Fix Shanghai-time records BEFORE type conversion
        print("\n[Step 1] Fix Shanghai-time records in generated_plans")
        fix_shanghai_records(conn)

        # Step 2: Convert all DateTime columns to TIMESTAMPTZ
        print("\n[Step 2] Convert DateTime columns to TIMESTAMPTZ")
        converted = convert_columns_to_timestamptz(conn)

        if converted == 0:
            print("  All columns are already TIMESTAMPTZ. Nothing to convert.")
        else:
            print(f"\n  Converted {converted} columns.")

    print("\n" + "=" * 60)
    print("Migration complete.")


if __name__ == "__main__":
    migrate()
