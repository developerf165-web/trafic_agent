import httpx
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class YandexMetricaAPI:
    def __init__(self, access_token: str, client_login: str = None):
        self.base_url = "https://api-metrica.yandex.net/stat/v1/data"
        self.client_login = client_login
        self.headers = {
            "Authorization": f"OAuth {access_token}"
        }

    async def _request(self, method: str, url: str, params: dict = None, max_retries: int = 3) -> dict:
        """
        Base request handler with retries for transient errors and timeouts.
        """
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                try:
                    response = await client.request(method, url, params=params, headers=self.headers, timeout=30.0)
                    
                    if response.status_code == 200:
                        return response.json()
                    
                    elif response.status_code >= 500:
                        logger.warning(f"Metrica server error {response.status_code}. Retrying ({attempt+1}/{max_retries})...")
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                        
                    else:
                        logger.error(f"Metrica API HTTP Error: {response.status_code} - {response.text}")
                        return {"error": f"HTTP {response.status_code}", "text": response.text}

                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    logger.warning(f"Metrica Network/Timeout error: {e}. Retrying ({attempt+1}/{max_retries})...")
                    await asyncio.sleep(2 * (attempt + 1))
                    if attempt == max_retries - 1:
                        raise e
            
            return {"error": "Max retries reached"}

    async def get_stats(self, counter_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """
        Fetches statistics from Yandex Metrica API.
        """
        params = {
            "ids": counter_id,
            "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews",
            "dimensions": "ym:s:date",
            "date1": date_from,
            "date2": date_to,
            "group": "day",
            "sort": "ym:s:date"
        }

        try:
            data = await self._request("GET", self.base_url, params=params)
            if "data" in data:
                results = []
                for row in data.get('data', []):
                    results.append({
                        "date": row['dimensions'][0]['name'],
                        "visits": row['metrics'][0],
                        "users": row['metrics'][1],
                        "pageviews": row['metrics'][2]
                    })
                return results
            return []
        except Exception as e:
            logger.error(f"Error fetching Metrica stats: {e}")
            return []

    async def get_goals_stats(self, counter_id: str, date_from: str, date_to: str, metrics: str = "ym:s:anyGoalConversionRate,ym:s:sumGoalReachesAny") -> List[Dict[str, Any]]:
        """
        Fetches goal conversions from Yandex Metrica.
        """
        params = {
            "ids": counter_id,
            "metrics": metrics,
            "dimensions": "ym:s:date",
            "date1": date_from,
            "date2": date_to
        }

        try:
            data = await self._request("GET", self.base_url, params=params)
            return data.get('data', [])
        except Exception as e:
            logger.error(f"Error fetching Metrica goal stats: {e}")
            return []

    async def get_counters(self) -> List[Dict[str, Any]]:
        """
        Lists all accessible counters.
        """
        url = "https://api-metrica.yandex.net/management/v1/counters"
        params = {}
        if self.client_login:
            params["ulogin"] = self.client_login
            
        try:
            data = await self._request("GET", url, params=params)
            if "counters" in data:
                return data.get('counters', [])
            
            error_msg = f"Failed to fetch counters: {data.get('error')}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Failed to fetch Metrica counters: {e}")
            raise e

    async def get_counter_goals(self, counter_id: str, date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """
        Lists all goals for a specific counter.
        If date_from and date_to are provided, it also fetches reach stats for each goal.
        """
        from .schemas import YandexGoal
        url = f"https://api-metrica.yandex.net/management/v1/counter/{counter_id}/goals"
        params = {}
        if self.client_login:
            params["ulogin"] = self.client_login
            
        goals_data = []
        try:
            data = await self._request("GET", url, params=params)
            if "goals" in data:
                goals_data = data.get('goals', [])
            elif "error" in data:
                logger.error(f"Metrica Goals Error: {data['error']}")
                return []
        except Exception as e:
            logger.error(f"Error fetching Metrica goals: {e}")
            return []

        # Convert to Pydantic models
        results = [
            YandexGoal(
                id=str(g["id"]),
                name=g.get("name") or "Unnamed Goal",
                type=g.get("type") or "GOAL_METRIKA"
            )
            for g in goals_data
        ]

        # If date range is provided, fetch stats (reaches) for these goals
        if date_from and date_to and results:
            try:
                # We need to fetch metrics for each goal. 
                # Metrica allows fetching ym:s:goal<ID>reaches and ym:s:goal<ID>conversionRate
                # But if there are many goals, it might hit limits or be complex.
                # Let's try to fetch grouped stats if possible, or just the summary.
                
                # Fetching conversion rate and reaches for all goals might be large.
                # We'll use a summary report for the counter.
                metrics = "ym:s:anyGoalConversionRate,ym:s:sumGoalReachesAny"
                # Add specific goal metrics for a better breakdown if needed, 
                # but for simplicity we can use the conversion service if available.
                
                # Alternative: Use the 'data' API with goals breakdown
                stats_url = "https://api-metrica.yandex.net/stat/v1/data"
                stats_params = {
                    "ids": counter_id,
                    "metrics": "ym:s:goalReaches,ym:s:goalConversionRate",
                    "dimensions": "ym:s:goalDimension",
                    "date1": date_from,
                    "date2": date_to,
                    "accuracy": "full"
                }
                if self.client_login:
                    stats_params["ulogin"] = self.client_login
                
                stats_data = await self._request("GET", stats_url, params=stats_params)
                if "data" in stats_data:
                    stats_json = stats_data
                    stats_map = {}
                    for row in stats_json.get("data", []):
                        # Dim: ym:s:goalDimension (id)
                        goal_id = str(row["dimensions"][0]["id"])
                        stats_map[goal_id] = {
                            "reaches": int(row["metrics"][0]),
                            "cr": float(row["metrics"][1])
                        }
                    
                    # Merge stats into results
                    for goal in results:
                        if goal.id in stats_map:
                            goal.reaches = stats_map[goal.id]["reaches"]
                            goal.conversion_rate = stats_map[goal.id]["cr"]
            except Exception as e:
                logger.warning(f"Failed to fetch Metrica goal stats: {e}")

        return results
