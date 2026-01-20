import sys
import os

sys.path.append(os.getcwd())

from core.database import SessionLocal
from core import models
from sqlalchemy import func

def analyze_all_projects():
    db = SessionLocal()
    try:
        print("=" * 80)
        print("ТАҲЛИЛИ ҲАМАИ ПРОЕКТҲО (ALL PROJECTS ANALYSIS)")
        print("=" * 80)
        
        # Get all clients
        clients = db.query(models.Client).order_by(models.Client.name).all()
        
        for client in clients:
            print(f"\n{'='*80}")
            print(f"ПРОЕКТ: {client.name}")
            print(f"ID: {client.id}")
            print(f"{'='*80}")
            
            # Get integrations
            integrations = db.query(models.Integration).filter(
                models.Integration.client_id == client.id
            ).all()
            
            print(f"\nИнтегратсияҳо: {len(integrations)}")
            for integ in integrations:
                print(f"  - {integ.platform.value} (ID: {integ.id})")
                print(f"    Account: {integ.account_id}")
                print(f"    Agency Login: {integ.agency_client_login}")
                
                # Get campaigns for this integration
                campaigns = db.query(models.Campaign).filter(
                    models.Campaign.integration_id == integ.id
                ).all()
                
                active_campaigns = [c for c in campaigns if c.is_active]
                inactive_campaigns = [c for c in campaigns if not c.is_active]
                
                print(f"    Кампанияҳо: {len(campaigns)} (Фаъол: {len(active_campaigns)}, Ғайрифаъол: {len(inactive_campaigns)})")
            
            # Get stats
            yandex_stats = db.query(models.YandexStats).filter(
                models.YandexStats.client_id == client.id
            ).all()
            
            vk_stats = db.query(models.VKStats).filter(
                models.VKStats.client_id == client.id
            ).all()
            
            print(f"\nМаълумот:")
            print(f"  YandexStats: {len(yandex_stats)} сатр")
            print(f"  VKStats: {len(vk_stats)} сатр")
            
            # Check orphaned stats (stats without campaign_id)
            orphaned_yandex = db.query(models.YandexStats).filter(
                models.YandexStats.client_id == client.id,
                models.YandexStats.campaign_id == None
            ).count()
            
            orphaned_vk = db.query(models.VKStats).filter(
                models.VKStats.client_id == client.id,
                models.VKStats.campaign_id == None
            ).count()
            
            if orphaned_yandex > 0 or orphaned_vk > 0:
                print(f"\n⚠️  МАЪЛУМОТИ БЕ КАМПАНИЯ (Orphaned Stats):")
                print(f"  YandexStats: {orphaned_yandex} сатр")
                print(f"  VKStats: {orphaned_vk} сатр")
            
            # Check stats with active campaigns
            if len(yandex_stats) > 0:
                stats_with_active = db.query(models.YandexStats).join(
                    models.Campaign, models.YandexStats.campaign_id == models.Campaign.id
                ).filter(
                    models.YandexStats.client_id == client.id,
                    models.Campaign.is_active == True
                ).count()
                
                print(f"\nМаълумот бо кампанияҳои фаъол: {stats_with_active} сатр")
                
                if stats_with_active == 0 and len(yandex_stats) > 0:
                    print("❌ МУШКИЛӢ: Маълумот ҳаст, вале ба кампанияҳои фаъол пайваст нест!")
            
            # Summary
            print(f"\nХулоса:")
            if len(integrations) == 0:
                print("  ❌ Интегратсия нест")
            if len(yandex_stats) == 0 and len(vk_stats) == 0:
                print("  ❌ Маълумот нест")
            elif orphaned_yandex > 0 or orphaned_vk > 0:
                print("  ⚠️  Маълумот ҳаст, вале баъзеаш ба кампания пайваст нест")
            else:
                print("  ✅ Ҳама чиз дуруст аст")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Хато: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    analyze_all_projects()
