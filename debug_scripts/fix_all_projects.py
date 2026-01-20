import sys
import os

sys.path.append(os.getcwd())

from core.database import SessionLocal
from core import models

def fix_all_projects():
    """
    Fixes all projects by linking orphaned stats to campaigns.
    Creates campaigns if they don't exist.
    """
    db = SessionLocal()
    try:
        print("=" * 80)
        print("ИСЛОҲИ ҲАМАИ ПРОЕКТҲО (FIX ALL PROJECTS)")
        print("=" * 80)
        
        # Get all clients
        clients = db.query(models.Client).order_by(models.Client.name).all()
        
        total_campaigns_created = 0
        total_stats_linked = 0
        fixed_projects = []
        
        for client in clients:
            print(f"\n{'='*80}")
            print(f"Проект: {client.name}")
            print(f"{'='*80}")
            
            # Check for orphaned Yandex stats
            orphaned_yandex = db.query(models.YandexStats).filter(
                models.YandexStats.client_id == client.id,
                models.YandexStats.campaign_id == None
            ).count()
            
            # Check for orphaned VK stats
            orphaned_vk = db.query(models.VKStats).filter(
                models.VKStats.client_id == client.id,
                models.VKStats.campaign_id == None
            ).count()
            
            if orphaned_yandex == 0 and orphaned_vk == 0:
                print("✓ Ҳама чиз дуруст аст (No orphaned stats)")
                continue
            
            print(f"⚠️  Маълумоти бе кампания:")
            print(f"  YandexStats: {orphaned_yandex} сатр")
            print(f"  VKStats: {orphaned_vk} сатр")
            
            # Get integration for this client
            integration = db.query(models.Integration).filter(
                models.Integration.client_id == client.id
            ).first()
            
            if not integration:
                print("❌ Интегратсия нест - наметавонем ислоҳ кунем")
                continue
            
            print(f"\nИнтегратсия: {integration.platform.value}")
            
            campaigns_created = 0
            stats_linked = 0
            
            # Fix Yandex stats
            if orphaned_yandex > 0:
                print("\nИслоҳи YandexStats...")
                
                # Get unique campaign names
                unique_campaigns = db.query(
                    models.YandexStats.campaign_name
                ).filter(
                    models.YandexStats.client_id == client.id,
                    models.YandexStats.campaign_id == None
                ).distinct().all()
                
                for (campaign_name,) in unique_campaigns:
                    if not campaign_name:
                        continue
                    
                    # Check if campaign exists
                    existing = db.query(models.Campaign).filter(
                        models.Campaign.integration_id == integration.id,
                        models.Campaign.name == campaign_name
                    ).first()
                    
                    if not existing:
                        # Create new campaign
                        new_campaign = models.Campaign(
                            integration_id=integration.id,
                            external_id=f"historical_{campaign_name.replace(' ', '_')}",
                            name=campaign_name,
                            is_active=True
                        )
                        db.add(new_campaign)
                        db.flush()
                        campaigns_created += 1
                        print(f"  ✓ Эҷод: {campaign_name}")
                        
                        # Link stats
                        count = db.query(models.YandexStats).filter(
                            models.YandexStats.client_id == client.id,
                            models.YandexStats.campaign_name == campaign_name,
                            models.YandexStats.campaign_id == None
                        ).update({"campaign_id": new_campaign.id})
                        stats_linked += count
                    else:
                        # Link to existing campaign
                        count = db.query(models.YandexStats).filter(
                            models.YandexStats.client_id == client.id,
                            models.YandexStats.campaign_name == campaign_name,
                            models.YandexStats.campaign_id == None
                        ).update({"campaign_id": existing.id})
                        stats_linked += count
                        if count > 0:
                            print(f"  ✓ Пайваст: {campaign_name} ({count} сатр)")
            
            # Fix VK stats (similar logic)
            if orphaned_vk > 0:
                print("\nИслоҳи VKStats...")
                
                unique_campaigns = db.query(
                    models.VKStats.campaign_name
                ).filter(
                    models.VKStats.client_id == client.id,
                    models.VKStats.campaign_id == None
                ).distinct().all()
                
                for (campaign_name,) in unique_campaigns:
                    if not campaign_name:
                        continue
                    
                    existing = db.query(models.Campaign).filter(
                        models.Campaign.integration_id == integration.id,
                        models.Campaign.name == campaign_name
                    ).first()
                    
                    if not existing:
                        new_campaign = models.Campaign(
                            integration_id=integration.id,
                            external_id=f"historical_{campaign_name.replace(' ', '_')}",
                            name=campaign_name,
                            is_active=True
                        )
                        db.add(new_campaign)
                        db.flush()
                        campaigns_created += 1
                        print(f"  ✓ Эҷод: {campaign_name}")
                        
                        count = db.query(models.VKStats).filter(
                            models.VKStats.client_id == client.id,
                            models.VKStats.campaign_name == campaign_name,
                            models.VKStats.campaign_id == None
                        ).update({"campaign_id": new_campaign.id})
                        stats_linked += count
                    else:
                        count = db.query(models.VKStats).filter(
                            models.VKStats.client_id == client.id,
                            models.VKStats.campaign_name == campaign_name,
                            models.VKStats.campaign_id == None
                        ).update({"campaign_id": existing.id})
                        stats_linked += count
                        if count > 0:
                            print(f"  ✓ Пайваст: {campaign_name} ({count} сатр)")
            
            if campaigns_created > 0 or stats_linked > 0:
                print(f"\nНатиҷа барои {client.name}:")
                print(f"  Кампанияҳои нав: {campaigns_created}")
                print(f"  Сатрҳои пайвастшуда: {stats_linked}")
                
                total_campaigns_created += campaigns_created
                total_stats_linked += stats_linked
                fixed_projects.append(client.name)
        
        db.commit()
        
        print(f"\n{'='*80}")
        print("ХУЛОСАИ УМУМӢ (SUMMARY)")
        print(f"{'='*80}")
        print(f"Проектҳои ислоҳшуда: {len(fixed_projects)}")
        for p in fixed_projects:
            print(f"  - {p}")
        print(f"\nҶамъи кампанияҳои нав: {total_campaigns_created}")
        print(f"Ҷамъи сатрҳои пайвастшуда: {total_stats_linked}")
        print(f"{'='*80}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Хато: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_projects()
