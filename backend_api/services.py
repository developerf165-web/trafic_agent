import httpx
from fastapi import HTTPException
from core import models, schemas
import logging
from automation.yandex_direct import YandexDirectAPI
from automation.yandex_metrica import YandexMetricaAPI

logger = logging.getLogger(__name__)

class IntegrationService:
    @staticmethod
    async def exchange_vk_token(client_id: str, client_secret: str) -> dict:
        """
        Exchanges VK Ads Client ID and Secret for an Access Token.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://ads.vk.com/api/v2/oauth2/token.json",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": client_id,
                        "client_secret": client_secret
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "access_token": data.get("access_token"),
                        "refresh_token": data.get("refresh_token")
                    }
                else:
                    error_data = response.json()
                    error_msg = error_data.get('error_description') or error_data.get('error') or 'Invalid credentials'
                    raise HTTPException(
                        status_code=400, 
                        detail=f"VK Ads Auth Error: {error_msg}"
                    )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to VK Ads: {str(e)}")

    @staticmethod
    async def refresh_yandex_token(refresh_token: str, client_id: str, client_secret: str) -> dict:
        """
        Refreshes Yandex OAuth access token using a refresh token.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth.yandex.ru/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": client_id,
                        "client_secret": client_secret
                    }
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Yandex Refresh Error: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to refresh Yandex token: {e}")
            return None

    @staticmethod
    def map_error(platform: str, error_detail: str) -> str:
        """
        Maps technical API errors to user-friendly messages.
        """
        # Add mapping logic here as more platforms are added
        return error_detail

    @staticmethod
    async def get_profiles(integration, access_token: str):
        """
        Fetch available profiles/accounts for this integration from the platform.
        NOW WITH ENRICHMENT: balance, currency, campaign stats, monthly spend
        """
        
        if integration.platform == models.IntegrationPlatform.YANDEX_DIRECT:
            try:
                from datetime import datetime, timedelta
                profiles = []
                seen_logins = set()
                direct_api = YandexDirectAPI(access_token)

                # 1. Include the personal account itself
                personal_login = integration.account_id
                if personal_login and personal_login.lower() != "unknown" and personal_login.lower() != "none":
                    profiles.append({
                        "login": personal_login, 
                        "name": f"Личный аккаунт ({personal_login})",
                        "type": "personal",
                        "description": "Основной аккаунт авторизации"
                    })
                    seen_logins.add(personal_login.lower())

                # 2. Add agency clients (if any)
                agency_clients = await direct_api.get_agency_clients()
                for ac in agency_clients:
                    login = ac.login
                    if login and login.lower() not in seen_logins:
                        profiles.append({
                            "login": login,
                            "name": ac.name,
                            "type": "agency_client",
                            "description": f"Клиент агентства ({ac.agency or 'Yandex'})"
                        })
                        seen_logins.add(login.lower())

                # 3. Managed logins (shared/editor access)
                clients_info = await direct_api.get_clients()
                for c_info in clients_info:
                    managed = c_info.get("ManagedLogins", [])
                    for m_login in managed:
                        if m_login and m_login.lower() not in seen_logins:
                            profiles.append({
                                "login": m_login,
                                "name": f"Доступный аккаунт ({m_login})",
                                "type": "managed",
                                "description": "Аккаунт с общим доступом"
                            })
                            seen_logins.add(m_login.lower())

                # Final fallback
                if not profiles:
                    display_id = integration.account_id or "Unknown"
                    profiles = [{
                        "login": display_id, 
                        "name": f"Аккаунт ({display_id})",
                        "type": "fallback",
                        "description": "Профиль по умолчанию"
                    }]
                
                # NEW: ENRICH EACH PROFILE with balance, currency, and campaign stats in PARALLEL
                logger.info(f"Enriching {len(profiles)} profiles in parallel...")
                
                async def enrich_task(profile):
                    try:
                        temp_api = YandexDirectAPI(access_token, client_login=profile["login"])
                        
                        # 1. Get balance and currency
                        try:
                            account_info = await temp_api.get_account_info()
                            profile["balance"] = account_info.get("balance", 0.0)
                            profile["currency"] = account_info.get("currency", "RUB")
                        except Exception as balance_err:
                            logger.warning(f"Balance error for {profile['login']}: {balance_err}")
                            profile["balance"] = 0.0
                            profile["currency"] = "RUB"
                        
                        # 2. Get campaign stats
                        try:
                            campaigns = await temp_api.get_campaigns()
                            profile["campaigns_count"] = len(campaigns)
                            profile["active_campaigns"] = len([c for c in campaigns if c.state == "ON"])
                        except Exception as campaigns_err:
                            logger.warning(f"Campaign error for {profile['login']}: {campaigns_err}")
                            profile["campaigns_count"] = 0
                            profile["active_campaigns"] = 0
                        
                        # 3. Calculate monthly spend
                        try:
                            date_to = datetime.now().strftime("%Y-%m-%d")
                            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                            stats = await temp_api.get_report(date_from, date_to, level="campaign")
                            profile["monthly_spend"] = sum(s.get("cost", 0) for s in stats)
                        except Exception as stats_err:
                            logger.warning(f"Spend error for {profile['login']}: {stats_err}")
                            profile["monthly_spend"] = 0.0
                            
                    except Exception as enrich_err:
                        logger.error(f"Global enrichment failure for {profile['login']}: {type(enrich_err).__name__}: {enrich_err}")
                        profile.update({
                            "balance": 0.0, "currency": "RUB", 
                            "campaigns_count": 0, "active_campaigns": 0, "monthly_spend": 0.0
                        })

                # Run all enrichment tasks concurrently
                import asyncio
                await asyncio.gather(*(enrich_task(p) for p in profiles))
                
                logger.info(f"Successfully enriched {len(profiles)} profiles in parallel")
                return profiles
                
            except Exception as e:
                logger.error(f"Error in get_profiles (Yandex): {e}")
                return [{
                    "login": integration.account_id, 
                    "name": f"Аккаунт ({integration.account_id})", 
                    "type": "error",
                    "balance": 0.0,
                    "currency": "RUB",
                    "campaigns_count": 0,
                    "active_campaigns": 0,
                    "monthly_spend": 0.0
                }]

        return []

    @staticmethod
    async def discover_campaigns(db, integration, access_token: str, date_from: str = None, date_to: str = None):
        """
        Fetch campaign list from platform and save/update in DB.
        """
        discovered_campaigns = []
        platform_name = "unknown"

        if integration.platform == models.IntegrationPlatform.YANDEX_DIRECT:
            api_client = YandexDirectAPI(access_token, integration.agency_client_login)
            discovered_campaigns = await api_client.get_campaigns(date_from=date_from, date_to=date_to)
            platform_name = "yandex"
        # elif integration.platform == models.IntegrationPlatform.VK_ADS:
        #    api_client = VKAdsAPI(access_token, integration.account_id)
        #    discovered_campaigns = await api_client.get_campaigns()
        #    platform_name = "vk"

        # Save/Update in DB using an Upsert-like strategy to preserve data integrity
        # 1. Fetch existing campaigns for this integration to map external_id -> campaign
        existing_campaigns = db.query(models.Campaign).filter_by(integration_id=integration.id).all()
        existing_map = {c.external_id: c for c in existing_campaigns}
        
        updated_ids = set()
        
        for dc in discovered_campaigns:
            ext_id = str(dc.id)
            if ext_id in existing_map:
                # Update existing
                campaign = existing_map[ext_id]
                campaign.name = dc.name
                campaign.type = dc.type
                campaign.status = dc.status
                campaign.state = dc.state
                campaign.daily_budget = dc.daily_budget
                campaign.strategy = dc.strategy
                # We don't overwrite is_active here as it might be already set by user
            else:
                # Create new
                campaign = models.Campaign(
                    integration_id=integration.id,
                    external_id=ext_id,
                    name=dc.name,
                    type=dc.type,
                    status=dc.status,
                    state=dc.state,
                    daily_budget=dc.daily_budget,
                    strategy=dc.strategy,
                    is_active=False
                )
                db.add(campaign)
            
            updated_ids.add(ext_id)

        # Optional: Marking campaigns not present in the new discovery as inactive or deleting them
        # For now, we preserve them to avoid data loss, but we could mark them as 'DELETED' or similar.
        
        db.flush()
        return discovered_campaigns, platform_name

    @staticmethod
    async def test_connection(integration, access_token: str):
        """
        Tests connection to the platform APIs.
        """
        
        status_info = {"status": "success", "platform": integration.platform, "details": []}
        
        try:
            if integration.platform == models.IntegrationPlatform.YANDEX_DIRECT:
                # Test Direct API
                direct_api = YandexDirectAPI(access_token, integration.agency_client_login)
                try:
                    await direct_api.get_campaigns()
                    status_info["details"].append("Yandex Direct: OK")
                except Exception as e:
                    status_info["status"] = "failed"
                    status_info["details"].append(f"Yandex Direct: {str(e)}")
                
                # Test Metrica API
                metrica_api = YandexMetricaAPI(access_token)
                try:
                    await metrica_api.get_counters()
                    status_info["details"].append("Yandex Metrica: OK")
                except Exception as e:
                    status_info["details"].append(f"Yandex Metrica: {str(e)}")
                    if status_info["status"] == "success":
                         status_info["status"] = "warning"
            
            # Add VK Ads testing here...
            
        except Exception as e:
            status_info["status"] = "failed"
            status_info["details"].append(f"System Error: {str(e)}")
            
        return status_info
