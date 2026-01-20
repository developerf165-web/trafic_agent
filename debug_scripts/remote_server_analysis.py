"""
Remote Server Database Analysis Script
Connects to production PostgreSQL database and analyzes all projects
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Production server database credentials
DB_CONFIG = {
    'host': '89.23.101.59',
    'port': 5432,
    'database': 'saas_project',
    'user': 'postgres',
    'password': '9721'
}

def analyze_remote_database():
    """Analyze all projects in the production database"""
    try:
        print("=" * 80)
        print("ПАЙВАСТИ БА СЕРВЕР (Connecting to server)...")
        print(f"Host: {DB_CONFIG['host']}")
        print("=" * 80)
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n✓ Пайвасти муваффақ! (Connected successfully!)\n")
        
        # Get all clients
        cursor.execute("""
            SELECT id, name, created_at 
            FROM clients 
            ORDER BY name
        """)
        clients = cursor.fetchall()
        
        print(f"Ҷамъи проектҳо (Total projects): {len(clients)}\n")
        
        for client in clients:
            print("=" * 80)
            print(f"ПРОЕКТ: {client['name']}")
            print(f"ID: {client['id']}")
            print("=" * 80)
            
            # Get integrations
            cursor.execute("""
                SELECT id, platform, account_id, agency_client_login, sync_status, last_sync_at
                FROM integrations
                WHERE client_id = %s
            """, (client['id'],))
            integrations = cursor.fetchall()
            
            print(f"\nИнтегратсияҳо: {len(integrations)}")
            for integ in integrations:
                print(f"  - {integ['platform']} (ID: {integ['id']})")
                print(f"    Account: {integ['account_id']}")
                print(f"    Agency Login: {integ['agency_client_login']}")
                print(f"    Sync Status: {integ['sync_status']}")
                print(f"    Last Sync: {integ['last_sync_at']}")
                
                # Get campaigns
                cursor.execute("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active
                    FROM campaigns
                    WHERE integration_id = %s
                """, (integ['id'],))
                camp_stats = cursor.fetchone()
                print(f"    Кампанияҳо: {camp_stats['total']} (Фаъол: {camp_stats['active']})")
            
            # Get stats counts
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN campaign_id IS NULL THEN 1 ELSE 0 END) as orphaned
                FROM yandex_stats
                WHERE client_id = %s
            """, (client['id'],))
            yandex_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN campaign_id IS NULL THEN 1 ELSE 0 END) as orphaned
                FROM vk_stats
                WHERE client_id = %s
            """, (client['id'],))
            vk_stats = cursor.fetchone()
            
            print(f"\nМаълумот:")
            print(f"  YandexStats: {yandex_stats['total']} сатр (Бе кампания: {yandex_stats['orphaned']})")
            print(f"  VKStats: {vk_stats['total']} сатр (Бе кампания: {vk_stats['orphaned']})")
            
            # Check stats with active campaigns
            if yandex_stats['total'] > 0:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM yandex_stats ys
                    JOIN campaigns c ON ys.campaign_id = c.id
                    WHERE ys.client_id = %s AND c.is_active = true
                """, (client['id'],))
                active_stats = cursor.fetchone()
                print(f"\nМаълумот бо кампанияҳои фаъол: {active_stats['count']} сатр")
                
                if active_stats['count'] == 0 and yandex_stats['total'] > 0:
                    print("❌ МУШКИЛӢ: Маълумот ҳаст, вале ба кампанияҳои фаъол пайваст нест!")
            
            # Summary
            print(f"\nХулоса:")
            if len(integrations) == 0:
                print("  ❌ Интегратсия нест")
            if yandex_stats['total'] == 0 and vk_stats['total'] == 0:
                print("  ❌ Маълумот нест")
            elif yandex_stats['orphaned'] > 0 or vk_stats['orphaned'] > 0:
                print("  ⚠️  Маълумот ҳаст, вале баъзеаш ба кампания пайваст нест")
            else:
                print("  ✅ Ҳама чиз дуруст аст")
            
            print()
        
        cursor.close()
        conn.close()
        
        print("=" * 80)
        print("✓ Таҳлил тамом шуд!")
        print("=" * 80)
        
    except psycopg2.Error as e:
        print(f"\n❌ Хатои базаи додаҳо: {e}")
    except Exception as e:
        print(f"\n❌ Хато: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  ДИҚҚАТ: Пеш аз иҷро, пароли базаи додаҳоро дар скрипт навис!")
    print("Агар пароли дуруст надонед, дар сервер ин фармонро иҷро кунед:")
    print("  cat ~/trafic_agent/.env | grep DATABASE_URL")
    print()
    
    response = input("Пароли дуруст навиштед? (y/n): ")
    if response.lower() == 'y':
        analyze_remote_database()
    else:
        print("Пеш аз иҷро, пароли дурустро дар скрипт навис.")
