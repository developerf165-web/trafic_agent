from sqlalchemy import create_engine, inspect
from core.database import SQLALCHEMY_DATABASE_URL
import sys

def debug_db():
    print(f"Checking connection to: {SQLALCHEMY_DATABASE_URL}")
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        connection = engine.connect()
        print("✅ Connection successful!")
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {', '.join(tables)}")
        
        for table in ['users', 'clients', 'integrations', 'campaigns']:
            if table in tables:
                print(f"\nSchema for table '{table}':")
                columns = inspector.get_columns(table)
                for col in columns:
                    print(f"  - {col['name']}: {col['type']} (Nullable: {col['nullable']})")
                
                # Check for indexes and constraints
                pk = inspector.get_pk_constraint(table)
                print(f"  PK: {pk.get('constrained_columns')}")
                
                fks = inspector.get_foreign_keys(table)
                for fk in fks:
                    print(f"  FK: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            else:
                print(f"\n⚠️ Table '{table}' NOT FOUND!")
        
        connection.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_db()
