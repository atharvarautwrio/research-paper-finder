from sqlalchemy import Column, String, Integer, Text, Float, DateTime, JSON
from datetime import datetime
from app.database.session import Base

class PaperModel(Base):
    __tablename__ = "papers"

    paper_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(512), nullable=False, index=True)
    authors = Column(JSON, nullable=False)  # List of strings
    abstract = Column(Text, nullable=False)
    keywords = Column(JSON, nullable=False)  # List of strings
    categories = Column(JSON, nullable=False)  # List of strings
    primary_category = Column(String(64), index=True)
    publication_year = Column(Integer, nullable=False, index=True)
    venue = Column(String(256), nullable=False, index=True)
    citation_count = Column(Integer, default=0, index=True)
    doi = Column(String(128), nullable=True)
    url = Column(String(512), nullable=True)
    pdf_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "categories": self.categories,
            "primary_category": self.primary_category,
            "publication_year": self.publication_year,
            "venue": self.venue,
            "citation_count": self.citation_count,
            "doi": self.doi,
            "url": self.url,
            "pdf_url": self.pdf_url,
        }
