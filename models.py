# models.py
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, func, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Boolean
from database import Base

class UserReport(Base):
    __tablename__ = "user_reports"
    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    segment_id = Column(String, nullable=True)   # store as string for generality
    issues = Column(JSON, nullable=True)         # list of strings
    image_url = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RouteLog(Base):
    __tablename__ = "route_logs"
    id = Column(Integer, primary_key=True, index=True)
    start_lat = Column(Float, nullable=False)
    start_lng = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lng = Column(Float, nullable=False)
    distance_m = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    points = Column(JSON, nullable=False)   # list of [lat, lng]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SegmentStat(Base):
    __tablename__ = "segment_stats"
    segment_id = Column(String, primary_key=True, index=True)
    total_reports = Column(Integer, default=0, nullable=False)
    bad_reports = Column(Integer, default=0, nullable=False)
    crowd_score = Column(Float, default=0.0, nullable=False)   # 0..1
    detection_score = Column(Float, default=0.0, nullable=False) # 0..1 (higher → worse)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

