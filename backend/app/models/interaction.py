from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # Meeting, Call, Email, etc.
    date = Column(DateTime, nullable=False)
    time = Column(String(10))  # HH:MM format
    attendees = Column(Text)  # Comma-separated names
    topics_discussed = Column(Text)
    sentiment = Column(String(20))  # Positive, Neutral, Negative
    outcomes = Column(Text)
    follow_up_actions = Column(Text)
    materials_shared = Column(JSON)  # List of material IDs
    samples_distributed = Column(JSON)  # List of sample IDs with quantities
    ai_suggested_followups = Column(JSON)  # List of suggested actions
    voice_note_summary = Column(Text)  # Summary from voice note
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    hcp = relationship("HCP", backref="interactions")
