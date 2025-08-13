import os
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_dir)

from src.database import db

def run_migrations():
    # Get the directory containing migration files
    migrations_dir = os.path.join(src_dir, 'src', 'database', 'migrations')
    
    # Get all SQL files in the migrations directory, sorted by name
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    
    print(f"Found {len(migration_files)} migration files")
    
    # Create migrations table if it doesn't exist
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Get already executed migrations
    executed_migrations = db.execute_query("SELECT name FROM migrations")
    executed_migrations = {row['name'] for row in executed_migrations}
    
    # Execute pending migrations
    for migration_file in migration_files:
        if migration_file not in executed_migrations:
            print(f"Applying migration: {migration_file}")
            try:
                with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                    sql = f.read()
                
                # Execute each statement separately
                for statement in sql.split(';'):
                    statement = statement.strip()
                    if not statement:
                        continue
                        
                    # Handle PRAGMA and special SQLite commands
                    if statement.upper().startswith('PRAGMA'):
                        # Execute PRAGMA statements directly
                        db.execute_query(statement)
                        continue
                        
                    # Check for ALTER TABLE ADD COLUMN and handle properly
                    if 'ADD COLUMN' in statement.upper() and 'IF NOT EXISTS' not in statement.upper():
                        table_name = statement.split('ADD COLUMN')[0].split('ALTER TABLE')[1].strip()
                        column_name = statement.split('ADD COLUMN')[1].split()[0].strip()
                        
                        # Check if column exists
                        result = db.execute_query(
                            f"SELECT 1 FROM pragma_table_info('{table_name}') WHERE name = ?", 
                            (column_name,),
                            fetch_one=True
                        )
                        
                        if not result:
                            # Column doesn't exist, add it
                            db.execute_query(statement)
                    else:
                        # Execute other statements normally
                        db.execute_query(statement)
                
                # Record the migration
                db.execute_query(
                    "INSERT INTO migrations (name) VALUES (?)",
                    (migration_file,)
                )
                print(f"Successfully applied migration: {migration_file}")
                
            except Exception as e:
                print(f"Error applying migration {migration_file}: {str(e)}")
                return False
    
    print("All migrations applied successfully")
    return True

if __name__ == "__main__":
    run_migrations()
