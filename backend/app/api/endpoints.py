from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import Scheme, Region, SchemeRegionMapping, Mention, ImpactScore
from app.schemas.schemas import (
    SchemeResponse,
    SchemeDetailResponse,
    RegionResponse,
    MentionResponse,
    ImpactScoreResponse,
    SchemeCreate,
    MentionCreate
)

router = APIRouter()

@router.get("/schemes", response_model=List[SchemeResponse])
def list_schemes(
    search: Optional[str] = Query(None, description="Search by scheme name or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[str] = Query(None, description="Filter by level: 'state' or 'central'"),
    db: Session = Depends(get_db)
):
    query = db.query(Scheme)
    if search:
        query = query.filter((Scheme.name.ilike(f"%{search}%")) | (Scheme.description.ilike(f"%{search}%")))
    if category:
        query = query.filter(Scheme.category == category)
    if level == 'central':
        query = query.filter(Scheme.launching_authority.ilike('%Government of India%'))
    elif level == 'state':
        query = query.filter(~Scheme.launching_authority.ilike('%Government of India%'))
    
    schemes = query.all()
    results = []
    
    for s in schemes:
        # Calculate average impact score across regions for listing
        scores = [float(iscore.score) for iscore in s.impact_scores]
        avg_score = sum(scores) / len(scores) if scores else None
        
        scheme_dict = SchemeResponse.from_orm(s)
        scheme_dict.average_impact_score = round(avg_score, 2) if avg_score is not None else None
        results.append(scheme_dict)
        
    # Sort results by average_impact_score in descending order
    results.sort(key=lambda x: x.average_impact_score if x.average_impact_score is not None else -1, reverse=True)
        
    return results


@router.get("/schemes/{scheme_id}", response_model=SchemeDetailResponse)
def get_scheme_detail(scheme_id: int, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    # Calculate average impact score
    scores = [float(iscore.score) for iscore in scheme.impact_scores]
    avg_score = sum(scores) / len(scores) if scores else None

    # Format impact scores with district names
    impact_score_responses = []
    for iscore in scheme.impact_scores:
        region = db.query(Region).filter(Region.id == iscore.region_id).first()
        score_resp = ImpactScoreResponse(
            id=iscore.id,
            scheme_id=iscore.scheme_id,
            region_id=iscore.region_id,
            district_name=region.district if region else "Unknown",
            score=float(iscore.score),
            reach_component=float(iscore.reach_component),
            sentiment_component=float(iscore.sentiment_component),
            adoption_component=float(iscore.adoption_component),
            shap_explanations=iscore.shap_explanations,
            computed_at=iscore.computed_at,
            model_version=iscore.model_version
        )
        impact_score_responses.append(score_resp)

    recent_mentions = db.query(Mention).filter(Mention.scheme_id == scheme_id).order_by(Mention.published_date.desc()).limit(10).all()
    mention_responses = [MentionResponse.from_orm(m) for m in recent_mentions]

    detail = SchemeDetailResponse.from_orm(scheme)
    detail.average_impact_score = round(avg_score, 2) if avg_score is not None else None
    detail.impact_scores = impact_score_responses
    detail.recent_mentions = mention_responses

    return detail


@router.get("/regions", response_model=List[RegionResponse])
def list_regions(db: Session = Depends(get_db)):
    regions = db.query(Region).all()
    results = []
    for r in regions:
        reg_dict = RegionResponse.from_orm(r)
        reg_dict.geo_boundary = str(r.geo_boundary) if r.geo_boundary else None
        results.append(reg_dict)
    return results


@router.get("/regions/{region_id}/schemes", response_model=List[ImpactScoreResponse])
def get_region_scheme_scores(region_id: int, db: Session = Depends(get_db)):
    scores = db.query(ImpactScore).filter(ImpactScore.region_id == region_id).all()
    results = []
    for iscore in scores:
        region = db.query(Region).filter(Region.id == iscore.region_id).first()
        results.append(
            ImpactScoreResponse(
                id=iscore.id,
                scheme_id=iscore.scheme_id,
                region_id=iscore.region_id,
                district_name=region.district if region else "Unknown",
                score=float(iscore.score),
                reach_component=float(iscore.reach_component),
                sentiment_component=float(iscore.sentiment_component),
                adoption_component=float(iscore.adoption_component),
                shap_explanations=iscore.shap_explanations,
                computed_at=iscore.computed_at,
                model_version=iscore.model_version
            )
        )
    return results


@router.get("/mentions", response_model=List[MentionResponse])
def list_mentions(
    scheme_id: Optional[int] = None,
    sentiment_label: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Mention)
    if scheme_id:
        query = query.filter(Mention.scheme_id == scheme_id)
    if sentiment_label:
        query = query.filter(Mention.sentiment_label == sentiment_label)
    
    mentions = query.order_by(Mention.published_date.desc()).all()
    return [MentionResponse.from_orm(m) for m in mentions]


@router.get("/comparison")
def compare_schemes(scheme1_id: int, scheme2_id: int, db: Session = Depends(get_db)):
    s1 = db.query(Scheme).filter(Scheme.id == scheme1_id).first()
    s2 = db.query(Scheme).filter(Scheme.id == scheme2_id).first()

    if not s1 or not s2:
        raise HTTPException(status_code=404, detail="One or both schemes not found")

    scores_s1 = [float(i.score) for i in s1.impact_scores]
    scores_s2 = [float(i.score) for i in s2.impact_scores]

    avg_s1 = sum(scores_s1) / len(scores_s1) if scores_s1 else 0
    avg_s2 = sum(scores_s2) / len(scores_s2) if scores_s2 else 0

    return {
        "scheme1": {
            "id": s1.id,
            "name": s1.name,
            "category": s1.category,
            "budget_allocated": float(s1.budget_allocated) if s1.budget_allocated else 0,
            "average_impact_score": round(avg_s1, 2)
        },
        "scheme2": {
            "id": s2.id,
            "name": s2.name,
            "category": s2.category,
            "budget_allocated": float(s2.budget_allocated) if s2.budget_allocated else 0,
            "average_impact_score": round(avg_s2, 2)
        },
        "disclaimer": "Impact scores are model-assisted estimates for policy ranking."
    }


@router.post("/schemes", response_model=SchemeResponse)
def create_scheme(scheme_in: SchemeCreate, db: Session = Depends(get_db)):
    # 1. Create Scheme record
    db_scheme = Scheme(
        name=scheme_in.name,
        launching_authority=scheme_in.launching_authority,
        category=scheme_in.category,
        budget_allocated=scheme_in.budget_allocated,
        description=scheme_in.description
    )
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)

    # 2. Automatically create default mappings and impact scores for the 3 महाराष्ट्र districts
    regions = db.query(Region).all()
    for r in regions:
        # Create mapping
        mapping = SchemeRegionMapping(
            scheme_id=db_scheme.id,
            region_id=r.id,
            beneficiaries_reached=r.population // 100 if r.population else 1000,
            budget_utilized=float(db_scheme.budget_allocated) * 0.1 if db_scheme.budget_allocated else 100000.0
        )
        db.add(mapping)

        # Create Baseline Impact Score (e.g. 50 + random variance)
        import random
        reach_pct = float(random.randint(50, 75))
        sentiment_pct = 50.0  # baseline neutral sentiment
        adoption_pct = float(random.randint(40, 70))
        
        # score formula: 0.4*reach + 0.3*sentiment + 0.3*adoption
        score = round((0.4 * reach_pct) + (0.3 * sentiment_pct) + (0.3 * adoption_pct), 2)
        
        impact_score = ImpactScore(
            scheme_id=db_scheme.id,
            region_id=r.id,
            score=score,
            reach_component=reach_pct,
            sentiment_component=sentiment_pct,
            adoption_component=adoption_pct,
            shap_explanations={
                "base_value": 60.0,
                "contributions": {
                    "reach_level": round(reach_pct - 60.0, 2),
                    "budget_utilization": round(adoption_pct - 60.0, 2),
                    "sentiment_rating": round(sentiment_pct - 50.0, 2)
                }
            },
            model_version="v0_heuristic"
        )
        db.add(impact_score)
    
    db.commit()
    db.refresh(db_scheme)
    
    # Calculate average score for response mapping
    scores = [float(iscore.score) for iscore in db_scheme.impact_scores]
    avg_score = sum(scores) / len(scores) if scores else None
    
    scheme_dict = SchemeResponse.from_orm(db_scheme)
    scheme_dict.average_impact_score = round(avg_score, 2) if avg_score is not None else None
    return scheme_dict


@router.post("/mentions", response_model=MentionResponse)
def create_mention(mention_in: MentionCreate, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == mention_in.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
        
    db_mention = Mention(
        scheme_id=mention_in.scheme_id,
        source=mention_in.source,
        raw_text=mention_in.raw_text,
        language=mention_in.language,
        sentiment_score=mention_in.sentiment_score,
        sentiment_label=mention_in.sentiment_label,
        url=mention_in.url
    )
    db.add(db_mention)
    db.commit()
    db.refresh(db_mention)

    # Re-calculate sentiment component and update ImpactScore records for this scheme
    all_mentions = db.query(Mention).filter(Mention.scheme_id == mention_in.scheme_id).all()
    
    # Simple sentiment score mapping to 0-100% component score
    avg_sent = sum(float(m.sentiment_score) for m in all_mentions) / len(all_mentions) if all_mentions else 0.0
    sentiment_component_val = round((avg_sent + 1.0) * 50.0, 2) # e.g. sentiment score 0.0 maps to 50%
    
    # Update impact scores in each region
    impact_scores = db.query(ImpactScore).filter(ImpactScore.scheme_id == mention_in.scheme_id).all()
    for iscore in impact_scores:
        iscore.sentiment_component = sentiment_component_val
        # Recalculate score
        reach = float(iscore.reach_component)
        adoption = float(iscore.adoption_component)
        iscore.score = round((0.4 * reach) + (0.3 * sentiment_component_val) + (0.3 * adoption), 2)
        
        # update SHAP contributions
        contribs = iscore.shap_explanations or {}
        contribs_dict = contribs.get("contributions", {})
        contribs_dict["sentiment_rating"] = round(sentiment_component_val - 50.0, 2)
        iscore.shap_explanations = {
            "base_value": 60.0,
            "contributions": contribs_dict
        }
    
    db.commit()
    return db_mention
