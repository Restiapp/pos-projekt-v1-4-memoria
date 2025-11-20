"""
Migration Script: Add tags and last_visit columns to customers table
Module 5: Service CRM
Date: 2025-11-20

This script adds the following columns to the customers table:
- tags: JSON array for customer labels/tags (e.g., ['VIP', 'Regular', 'New'])
- last_visit: TIMESTAMP for tracking last customer visit/order
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy import create_engine, text
from backend.service_crm.config import settings


def run_migration():
    """Execute the migration to add tags and last_visit columns."""

    # Create database engine
    engine = create_engine(str(settings.database_url))

    # Read SQL migration file
    sql_file = Path(__file__).parent / "add_customer_tags_and_last_visit.sql"

    with open(sql_file, 'r') as f:
        sql_script = f.read()

    # Execute migration
    try:
        with engine.begin() as connection:
            # Split by semicolons and execute each statement
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]

            for statement in statements:
                if statement and not statement.startswith('--'):
                    print(f"Executing: {statement[:100]}...")
                    connection.execute(text(statement))

            print("✅ Migration completed successfully!")
            print("   - Added 'tags' column (JSON)")
            print("   - Added 'last_visit' column (TIMESTAMP WITH TIME ZONE)")
            print("   - Created index on 'last_visit' for performance")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("🔄 Running migration: Add tags and last_visit to customers table")
    print(f"📊 Database: {str(settings.database_url).split('@')[1]}")

    confirm = input("\nProceed with migration? (yes/no): ")

    if confirm.lower() in ['yes', 'y']:
        run_migration()
    else:
        print("❌ Migration cancelled.")
