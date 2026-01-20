from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class YandexProfile(BaseModel):
    login: str
    name: str
    type: str  # personal, agency_client, managed
    description: Optional[str] = None
    agency: Optional[str] = None
    currency: Optional[str] = None
    balance: Optional[float] = None
    # NEW: Campaign statistics for enriched profile display
    campaigns_count: Optional[int] = 0
    active_campaigns: Optional[int] = 0
    monthly_spend: Optional[float] = 0.0

class YandexCampaign(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    status: Optional[str] = None
    state: Optional[str] = None
    daily_budget: Optional[float] = None
    strategy: Optional[str] = None
    # Stats fields for preview
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    cost: Optional[float] = 0.0
    conversions: Optional[int] = 0

class YandexGoal(BaseModel):
    id: str
    name: str
    type: str  # GOAL_METRIKA, etc.
    is_primary: bool = False
    reaches: Optional[int] = 0
    conversion_rate: Optional[float] = 0.0
