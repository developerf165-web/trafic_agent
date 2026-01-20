import httpx
import json
import asyncio
from datetime import date, datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class YandexDirectAPI:
    def __init__(self, access_token: str, client_login: str = None):
        self.report_url = "https://api.direct.yandex.com/json/v5/reports"
        self.campaigns_url = "https://api.direct.yandex.com/json/v5/campaigns"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept-Language": "ru",
            "processingMode": "auto"
        }
        if client_login and client_login.lower() != "unknown":
            self.headers["Client-Login"] = client_login
            logger.info(f"Initialized Yandex API with Agency Client-Login: {client_login}")

    async def _request(self, url: str, payload: dict, max_retries: int = 3) -> dict:
        """
        Base request handler with retries for transient errors and timeouts.
        """
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                    
                    # Track API Units
                    units = response.headers.get("Units")
                    if units:
                        logger.debug(f"Yandex API Units: {units}")

                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            error_code = data["error"].get("error_code")
                            # Retry on specific transient Yandex errors if needed
                            if error_code in [52, 1000, 1001, 1002]: # Temporary issues
                                logger.warning(f"Yandex transient error {error_code}. Retrying ({attempt+1}/{max_retries})...")
                                await asyncio.sleep(2 * (attempt + 1))
                                continue
                            return data
                        return data
                    
                    elif response.status_code >= 500:
                        logger.warning(f"Yandex server error {response.status_code}. Retrying ({attempt+1}/{max_retries})...")
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                        
                    else:
                        logger.error(f"Yandex API HTTP Error: {response.status_code} - {response.text}")
                        return {"error": {"error_msg": f"HTTP {response.status_code}", "text": response.text}}

                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    logger.warning(f"Network/Timeout error: {e}. Retrying ({attempt+1}/{max_retries})...")
                    await asyncio.sleep(2 * (attempt + 1))
                    if attempt == max_retries - 1:
                        raise e
            
            return {"error": {"error_msg": "Max retries reached"}}

    async def get_campaigns(self, date_from: str = None, date_to: str = None) -> List["YandexCampaign"]:
        """
        Fetches the list of all campaigns using the Campaigns service with rich metadata.
        If date_from and date_to are provided, it also fetches performance stats from the Reports service.
        """
        payload = {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": ["Id", "Name", "Status", "State", "Type", "DailyBudget", "Strategy"]
            }
        }
        
        campaigns_list = []
        try:
            data = await self._request(self.campaigns_url, payload)
            if "result" in data and "Campaigns" in data["result"]:
                for c in data["result"]["Campaigns"]:
                    # Extract Daily Budget
                    budget_amount = 0
                    if "DailyBudget" in c and c["DailyBudget"]:
                        budget_amount = c["DailyBudget"].get("Amount", 0) / 1000000
                    
                    # Extract Strategy
                    strategy_type = "UNKNOWN"
                    if "Strategy" in c and c["Strategy"]:
                        if "Search" in c["Strategy"]:
                            strategy_type = c["Strategy"]["Search"].get("BiddingStrategyType", "UNKNOWN")
                        elif "Network" in c["Strategy"]:
                            strategy_type = c["Strategy"]["Network"].get("BiddingStrategyType", "UNKNOWN")

                    campaigns_list.append(YandexCampaign(
                        id=c["Id"],
                        name=c["Name"],
                        status=c.get("Status"),
                        state=c.get("State"),
                        type=c.get("Type"),
                        daily_budget=budget_amount,
                        strategy=strategy_type
                    ))
            elif "error" in data:
                error_msg = data["error"].get("error_msg", "Unknown error")
                raise Exception(f"Yandex API Error: {error_msg}")
        except Exception as e:
            logger.error(f"Error fetching Yandex campaigns: {e}")
            raise e

        # If date range is provided, fetch stats and merge
        if date_from and date_to and campaigns_list:
            try:
                stats = await self.get_report(date_from, date_to, level="campaign")
                # Group stats by campaign_id
                stats_map = {}
                for s in stats:
                    cid = int(s["campaign_id"])
                    if cid not in stats_map:
                        stats_map[cid] = {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0}
                    stats_map[cid]["impressions"] += s["impressions"]
                    stats_map[cid]["clicks"] += s["clicks"]
                    stats_map[cid]["cost"] += s["cost"]
                    stats_map[cid]["conversions"] += s["conversions"]
                
                # Merge into campaigns_list
                for camp in campaigns_list:
                    if camp.id in stats_map:
                        camp.impressions = stats_map[camp.id]["impressions"]
                        camp.clicks = stats_map[camp.id]["clicks"]
                        camp.cost = stats_map[camp.id]["cost"]
                        camp.conversions = stats_map[camp.id]["conversions"]
            except Exception as e:
                logger.warning(f"Failed to fetch report stats for campaigns: {e}")

        return campaigns_list

    async def get_report(self, date_from: str, date_to: str, level: str = "campaign", max_retries: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches a report from Yandex Direct API v5.
        Handles polling for 201/202 statuses and tracks API units.
        """
        field_names = ["Date", "CampaignId", "CampaignName", "Impressions", "Clicks", "Cost", "Conversions"]
        if level == "keyword":
            field_names.insert(2, "Criteria")
            report_type = "CRITERIA_PERFORMANCE_REPORT"
        elif level == "group":
            field_names.insert(2, "AdGroupName")
            report_type = "ADGROUP_PERFORMANCE_REPORT"
        else:
            report_type = "CAMPAIGN_PERFORMANCE_REPORT"

        report_definition = {
            "params": {
                "SelectionCriteria": {
                    "DateFrom": date_from,
                    "DateTo": date_to
                },
                "FieldNames": field_names,
                "ReportName": f"AgencyStats_{level}_{date_from}_{date_to}_{int(datetime.now().timestamp())}",
                "ReportType": report_type,
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "NO"
            }
        }

        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                response = await client.post(
                    self.report_url,
                    json=report_definition,
                    headers=self.headers,
                    timeout=60.0
                )

                # Track API Units (Points)
                units = response.headers.get("Units")
                if units:
                    # Format: used/limit/remaining
                    logger.info(f"Yandex API Units: {units}")

                if response.status_code == 200:
                    return self._parse_tsv(response.text, level)
                
                elif response.status_code in [201, 202]:
                    # Report is being generated or in queue
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.info(f"Report is in progress (Status {response.status_code}). Waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    # Loop continues to retry
                    
                elif response.status_code == 429:
                    # Too Many Requests
                    logger.warning("Yandex API Rate Limit (429) hit. Waiting 10 seconds...")
                    await asyncio.sleep(10)
                    
                elif response.status_code >= 500:
                    # Server error
                    logger.error(f"Yandex Server Error ({response.status_code}). Retrying in 5s...")
                    await asyncio.sleep(5)
                
                else:
                    logger.error(f"Yandex Direct API Error: {response.status_code} - {response.text}")
                    return []

            logger.error("Maximum retries reached for Yandex report generation.")
            return []

    def _parse_tsv(self, tsv_data: str, level: str = "campaign") -> List[Dict[str, Any]]:
        lines = tsv_data.strip().split('\n')
        if not lines:
            return []
        
        results = []
        for line in lines:
            if not line.strip():
                continue
                
            cols = line.split('\t')
            
            # Skip header or summary lines
            if cols[0] in ["Date", "Total", "Total rows:"] or "Total" in cols[0]:
                continue
            
            # Additional check: first column should look like a date (YYYY-MM-DD)
            if len(cols[0]) == 10 and cols[0][4] == '-' and cols[0][7] == '-':
                try:
                    if level in ["keyword", "group"]:
                        if len(cols) >= 8: # These reports have 8 columns
                            results.append({
                                "date": cols[0],
                                "campaign_name": cols[3], # Index 3 is CampaignName
                                "name": cols[2], # Index 2 is AdGroupName or Criteria
                                "impressions": int(cols[4]) if cols[4].isdigit() else 0,
                                "clicks": int(cols[5]) if cols[5].isdigit() else 0,
                                "cost": float(cols[6]) / 1000000 if cols[6].replace('.', '', 1).isdigit() else 0.0,
                                "conversions": int(cols[7]) if cols[7].isdigit() else 0
                            })
                    else:
                        if len(cols) >= 7:
                            results.append({
                                "date": cols[0],
                                "campaign_id": cols[1],
                                "campaign_name": cols[2],
                                "impressions": int(cols[3]) if cols[3].isdigit() else 0,
                                "clicks": int(cols[4]) if cols[4].isdigit() else 0,
                                "cost": float(cols[5]) / 1000000 if cols[5].replace('.', '', 1).isdigit() else 0.0,
                                "conversions": int(cols[6]) if cols[6].isdigit() else 0
                            })
                except (ValueError, IndexError):
                    continue
        return results

    async def get_account_info(self) -> Dict[str, Any]:
        """
        Fetches detailed account info including currency and real cash balance using AccountManagement service.
        """
        url = "https://api.direct.yandex.com/json/v5/accountmanagement"
        payload = {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": ["AccountID", "Amount", "Currency"]
            }
        }
        
        try:
            data = await self._request(url, payload)
            if "result" in data and "Accounts" in data["result"]:
                acc = data["result"]["Accounts"][0]
                return {
                    "account_id": acc.get("AccountID"),
                    "currency": acc.get("Currency"),
                    "balance": float(acc.get("Amount", 0))
                }
            elif "error" in data:
                logger.warning(f"AccountManagement Error: {data['error']}")
        except Exception as e:
            logger.error(f"Failed to fetch account info: {e}")
        
        # Fallback to basic Clients info for currency if AccountManagement fails
        try:
            basic_info = await self.get_clients()
            if basic_info:
                return {
                    "login": basic_info[0].get("Login"),
                    "currency": basic_info[0].get("Currency"),
                    "balance": 0.0
                }
        except:
            pass
            
        return {}

    async def get_clients(self) -> List[Dict[str, Any]]:
        """
        Fetches information about the current client, including ManagedLogins for shared access.
        """
        url = "https://api.direct.yandex.com/json/v5/clients"
        payload = {
            "method": "get",
            "params": {
                "FieldNames": ["Login", "ClientInfo", "Currency"]
            }
        }
        try:
            data = await self._request(url, payload)
            if "result" in data and "Clients" in data["result"]:
                return data["result"]["Clients"]
            elif "error" in data:
                logger.error(f"Yandex Clients API Error: {data['error']}")
        except Exception as e:
            logger.error(f"Failed to fetch Yandex clients: {e}")
        return []

    async def get_agency_clients(self) -> List["YandexProfile"]:
        """
        Fetches the list of all clients for an agency account.
        """
        from .schemas import YandexProfile
        url = "https://api.direct.yandex.com/json/v5/agencyclients"
        payload = {
            "method": "get",
            "params": {
                "SelectionCriteria": {
                    "Archived": "NO"
                },
                "FieldNames": ["Login", "ClientInfo", "RepresentedBy"],
                "Page": {
                    "Limit": 10000 
                }
            }
        }
        try:
            data = await self._request(url, payload)
            if "result" in data and "Clients" in data["result"]:
                profiles = []
                for c in data["result"]["Clients"]:
                    profiles.append(YandexProfile(
                        login=c["Login"],
                        name=c.get("ClientInfo") or c["Login"],
                        type="agency_client",
                        agency=c.get("RepresentedBy", {}).get("Agency", ""),
                        currency=None,
                        balance=0.0
                    ))
                return profiles
            elif "error" in data:
                 logger.error(f"Yandex AgencyClients API Error: {data['error']}")
        except Exception as e:
            logger.error(f"Failed to fetch Yandex agency clients: {e}")
        return []
