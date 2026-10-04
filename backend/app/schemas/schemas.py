from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
import datetime
from decimal import Decimal

# Base Schema Disclaimer as required by Non-Functional Requirements
ESTIMATED_DISCLAIMER = "Impact scores are model-assisted estimates for policy ranking and do not constitute official government ground truth."

class SchemeCreate(BaseModel):
    name: str = Field(..., description="Name of the state scheme")
    launching_authority: str = Field(..., description="Launching authority or department")
    category: Optional[str] = Field(None, description="Category of the scheme")
    budget_allocated: Optional[float] = Field(None, description="Total budget in INR")
    description: Optional[str] = Field(None, description="Scheme description and goals")

class MentionCreate(BaseModel):
    scheme_id: int = Field(..., description="ID of the related scheme")
    source: str = Field(..., description="Source of the review (e.g., Twitter, Reddit)")
    raw_text: str = Field(..., description="Post content or text review")
    language: Optional[str] = Field("hi", description="Language of the mention (hi/en/hi-en)")
    sentiment_score: Optional[float] = Field(0.0, description="Sentiment score (-1.0 to 1.0)")
    sentiment_label: Optional[str] = Field("Neutral", description="Sentiment label (Positive/Neutral/Negative)")
    url: Optional[str] = Field(None, description="Direct URL path if available")

class RegionBase(BaseModel):
    state: str
    district: str
    population: Optional[int] = None
    demographic_stats: Optional[Dict[str, Any]] = None

class RegionResponse(RegionBase):
    id: int
    geo_boundary: Optional[str] = None  # WKT string representation

    class Config:
        from_attributes = True

class MentionBase(BaseModel):
    source: str
    raw_text: str
    language: Optional[str] = "hi"
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[datetime.datetime] = None

class MentionResponse(MentionBase):
    id: int
    scheme_id: int

    class Config:
        from_attributes = True

class ImpactScoreResponse(BaseModel):
    id: int
    scheme_id: int
    region_id: int
    district_name: Optional[str] = None
    score: float
    reach_component: float
    sentiment_component: float
    adoption_component: float
    shap_explanations: Optional[Dict[str, Any]] = None
    computed_at: datetime.datetime
    model_version: str
    disclaimer: str = ESTIMATED_DISCLAIMER

    class Config:
        from_attributes = True

class SchemeBase(BaseModel):
    name: str
    launching_authority: str
    category: Optional[str] = None
    launch_date: Optional[datetime.date] = None
    target_beneficiaries: Optional[str] = None
    budget_allocated: Optional[float] = None
    description: Optional[str] = None
    source_url: Optional[str] = None

class SchemeResponse(SchemeBase):
    id: int
    created_at: datetime.datetime
    average_impact_score: Optional[float] = None
    disclaimer: str = ESTIMATED_DISCLAIMER

    class Config:
        from_attributes = True

class SchemeDetailResponse(SchemeResponse):
    impact_scores: List[ImpactScoreResponse] = []
    recent_mentions: List[MentionResponse] = []
