"""
Remote Server Data Fix Script
Connects to production PostgreSQL database and links orphaned stats to campaigns
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Production server database credentials (cloned from local .env)
DB_CONFIG = {
    'host': '89.23.101.59',
    'port': 5432,
    'database': 'saas_project',
    'user': 'postgres',
    'password': '9721'
}

def fix_remote_database():
    """Find and link orphaned stats for all projects on the production server"""
    try:
        print("=" * 80)
        print("ПАЙВАСТИ БА СЕРВЕР (Connecting to server)...")
        print(f"Host: {DB_CONFIG['host']}")
        print("=" * 80)
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False # We want a transaction
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n✓ Пайвасти муваффақ! (Connected successfully!)\n")
        
        # Get all clients
        cursor.execute("SELECT id, name FROM clients")
        clients = cursor.fetchall()
        
        total_campaigns_created = 0
        total_stats_linked = 0
        
        for client in clients:
            print("-" * 60)
            print(f"Таҳлили проект: {client['name']}")
            
            # Check for orphaned Yandex stats
            cursor.execute("""
                SELECT DISTINCT campaign_name 
                FROM yandex_stats 
                WHERE client_id = %s AND campaign_id IS NULL AND campaign_name IS NOT NULL
            """, (client['id'],))
            orphaned_campaign_names = [row['campaign_name'] for row in cursor.fetchall()]
            
            if not orphaned_campaign_names:
                print("  ✓ Маълумоти бе кампания нест.")
                continue
                
            print(f"  ⚠️  Дарёфт шуд: {len(orphaned_campaign_names)} кампанияи бе пайваст")
            
            # Get an integration to attach campaigns to
            cursor.execute("""
                SELECT id FROM integrations 
                WHERE client_id = %s AND platform = 'YANDEX_DIRECT' 
                LIMIT 1
            """, (client['id'],))
            integration = cursor.fetchone()
            
            if not integration:
                print("  ❌ Интегратсия барои ин проект ёфт нашуд. Наметавонам ислоҳ кунам.")
                continue
                
            for name in orphaned_campaign_names:
                # Check if campaign already exists for this integration
                cursor.execute("""
                    SELECT id FROM campaigns 
                    WHERE integration_id = %s AND name = %s
                """, (integration['id'], name))
                existing = cursor.fetchone()
                
                campaign_id = None
                if existing:
                    campaign_id = existing['id']
                    print(f"  ✓ Истифодаи кампанияи мавҷуда: {name}")
                else:
                    # Create new campaign
                    new_id = str(uuid.uuid4())
                    ext_id = f"hist_{name.replace(' ', '_')[:20]}"
                    cursor.execute("""
                        INSERT INTO campaigns (id, integration_id, external_id, name, is_active, created_at)
                        VALUES (%s, %s, %s, %s, true, NOW())
                        RETURNING id
                    """, (new_id, integration['id'], ext_id, name))
                    campaign_id = cursor.fetchone()['id']
                    total_campaigns_created += 1
                    print(f"  + Эҷоди кампанияи нав: {name}")
                
                # Link stats
                cursor.execute("""
                    UPDATE yandex_stats 
                    SET campaign_id = %s 
                    WHERE client_id = %s AND campaign_name = %s AND campaign_id IS NULL
                """, (campaign_id, client['id'], name))
                total_stats_linked += cursor.rowcount
                
        conn.commit()
        print("\n" + "=" * 80)
        print("НАТИҶАИ ИСЛОҲ (FIX RESULTS):")
        print(f"  Кампанияҳои сохташуда: {total_campaigns_created}")
        print(f"  Сатрҳои пайвастшуда: {total_stats_linked}")
        print("=" * 80)
        print("✓ Ҳамаи тағйиротҳо захира шуданд (Committed successfully).")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        if conn: conn.rollback()
        print(f"\n❌ Хатои базаи додаҳо: {e}")
    except Exception as e:
        if conn: conn.rollback()
        print(f"\n❌ Хато: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  ДИҚҚАТ: Ин скрипт маълумотро дар СЕРВЕР иваз мекунад!")
    confirm = input("Шумо мутмаин ҳастед? (yes/no): ")
    if confirm.lower() == 'yes':
        fix_remote_database()
    else:
        print("Ислоҳ бекор карда шуд.")
