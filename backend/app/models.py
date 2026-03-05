from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)          # Residential, Commercial, Infrastructure, Public, Industrial
    description = Column(Text, default="")
    location = Column(String, default="")
    region = Column(String, default="")
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    participants = Column(JSON, default=list)       # [{"name": str, "role": str, "contact": str}]
    estimated_cost = Column(String, default="")
    cost_value_msek = Column(Float, nullable=True) # numeric for filtering
    timeline_start = Column(String, default="")
    timeline_end = Column(String, default="")
    status = Column(String, default="Planerat")    # Planerat, Pågående, Klart
    source_url = Column(String, default="")
    source_name = Column(String, default="")
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Pydantic schemas ---

class Participant(BaseModel):
    name: str
    role: str
    contact: str = ""


class ProjectOut(BaseModel):
    id: int
    name: str
    type: str
    description: str
    location: str
    region: str
    lat: Optional[float]
    lng: Optional[float]
    participants: List[Participant]
    estimated_cost: str
    cost_value_msek: Optional[float]
    timeline_start: str
    timeline_end: str
    status: str
    source_url: str
    source_name: str
    published_at: datetime

    class Config:
        from_attributes = True


class ProjectList(BaseModel):
    total: int
    projects: List[ProjectOut]


class StatsOut(BaseModel):
    total: int
    by_type: dict
    by_status: dict
    by_region: dict
