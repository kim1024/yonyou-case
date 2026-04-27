"""Migration: add daily_token_quota column to llm_configs table.

Run once:
    cd backend && python -m scripts.migrate_add_daily_token_quota
"""

import sys
from pathlib import Path

# Ensure backend/ is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.database import engine


def migrate():
    column = "daily_token_quota"
    table = "llm_configs"

    with engine.connect() as conn:
        # Check if column already exists (PostgreSQL)
        result = conn.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = :table AND column_name = :column"
            ),
            {"table": table, "column": column},
        )
        if result.fetchone():
            print(f"Column '{column}' already exists on '{table}'. Skipping.")
            return

        conn.execute(
            text(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0")
        )
        conn.commit()
        print(f"Migration complete: added '{column}' to '{table}'.")


if __name__ == "__main__":
    migrate()
