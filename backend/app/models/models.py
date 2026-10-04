from sqlalchemy import Column, Integer, String, Text, Numeric, Date, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
import datetime
from app.core.database import Base
from app.core.config import settings

IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

# Handle geo-boundaries dynamically depending on database type
if IS_SQLITE:
    GeoBoundaryType = Text
else:
    from geoalchemy2 import Geometry
    GeoBoundaryType = Geometry(geometry_type='MULTIPOLYGON', srid=4326)

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    launching_authority = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    launch_date = Column(Date, nullable=True)
    target_beneficiaries = Column(String(255), nullable=True)
    budget_allocated = Column(Numeric(15, 2), nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    regions = relationship("SchemeRegionMapping", back_populates="scheme", cascade="all, delete-orphan")
    mentions = relationship("Mention", back_populates="scheme", cascade="all, delete-orphan")
    impact_scores = relationship("ImpactScore", back_populates="scheme", cascade="all, delete-orphan")


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    geo_boundary = Column(GeoBoundaryType, nullable=True)  # WKT under SQLite, PostGIS geometry under Postgres
    population = Column(Integer, nullable=True)
    demographic_stats = Column(JSON, nullable=True)  # Store NFHS-5 or census stats

    # Relationships
    schemes = relationship("SchemeRegionMapping", back_populates="region", cascade="all, delete-orphan")
    impact_scores = relationship("ImpactScore", back_populates="region", cascade="all, delete-orphan")


class SchemeRegionMapping(Base):
    __tablename__ = "scheme_region_mapping"

    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), primary_key=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), primary_key=True)
    beneficiaries_reached = Column(Integer, default=0)
    budget_utilized = Column(Numeric(15, 2), default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    scheme = relationship("Scheme", back_populates="regions")
    region = relationship("Region", back_populates="schemes")


class Mention(Base):
    __tablename__ = "mentions"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(100), nullable=False)  # e.g., Twitter, Reddit, Hindi News Portal Name
    raw_text = Column(Text, nullable=False)
    language = Column(String(10), default="hi")  # hi, en, hi-en (Hinglish)
    sentiment_score = Column(Numeric(5, 4), nullable=True)  # -1.0 to 1.0
    sentiment_label = Column(String(20), nullable=True)  # Positive, Neutral, Negative
    published_date = Column(DateTime, default=datetime.datetime.utcnow)
    url = Column(Text, nullable=True)

    # Relationships
    scheme = relationship("Scheme", back_populates="mentions")


class ImpactScore(Base):
    __tablename__ = "impact_scores"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)  # 0.00 to 100.00
    reach_component = Column(Numeric(5, 2), default=0.0)
    sentiment_component = Column(Numeric(5, 2), default=0.0)
    adoption_component = Column(Numeric(5, 2), default=0.0)
    shap_explanations = Column(JSON, nullable=True)  # Local explanations of the score
    computed_at = Column(DateTime, default=datetime.datetime.utcnow)
    model_version = Column(String(50), default="v0_heuristic")

    # Relationships
    scheme = relationship("Scheme", back_populates="impact_scores")
    region = relationship("Region", back_populates="impact_scores")
