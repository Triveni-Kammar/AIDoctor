from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InteractionBase(BaseModel):
    hcp_id: int
    interaction_type: str
    date: datetime
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = "Neutral"
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    materials_shared: Optional[List[int]] = []
    samples_distributed: Optional[List[dict]] = []
    ai_suggested_followups: Optional[List[str]] = []
    voice_note_summary: Optional[str] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    hcp_id: Optional[int] = None
    interaction_type: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    materials_shared: Optional[List[int]] = None
    samples_distributed: Optional[List[dict]] = None
    ai_suggested_followups: Optional[List[str]] = None
    voice_note_summary: Optional[str] = None


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InteractionFillRequest(BaseModel):
    description: str = Field(..., description="Natural language description of the interaction")


class InteractionCorrectRequest(BaseModel):
    current_data: dict = Field(..., description="Current form data")
    correction_instruction: str = Field(..., description="Instruction for correction")
