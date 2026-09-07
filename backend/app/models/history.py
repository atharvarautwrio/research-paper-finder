from sqlalchemy import Column, String, Integer, DateTime, Float, JSON
from datetime import datetime
from app.database.session import Base

class SearchHistoryModel(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(512), nullable=False, index=True)
    retrieval_mode = Column(String(32), default="hybrid")
    filters_applied = Column(JSON, nullable=True)
    result_count = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SavedPaperModel(Base):
    __tablename__ = "saved_papers"

    paper_id = Column(String(64), primary_key=True)
    title = Column(String(512), nullable=False)
    authors = Column(JSON, nullable=False)
    publication_year = Column(Integer, nullable=False)
    primary_category = Column(String(64), nullable=False)
    venue = Column(String(256), nullable=False)
    notes = Column(String(1024), nullable=True)
    saved_at = Column(DateTime, default=datetime.utcnow, index=True)
