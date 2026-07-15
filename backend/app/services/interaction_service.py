from sqlalchemy.orm import Session
from app.models.interaction import Interaction
from app.models.hcp import HCP
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from typing import List, Optional
from datetime import datetime


class InteractionService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_interaction(self, interaction: InteractionCreate) -> Interaction:
        """
        Create a new interaction
        """
        db_interaction = Interaction(**interaction.model_dump())
        self.db.add(db_interaction)
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction
    
    def get_interaction(self, interaction_id: int) -> Optional[Interaction]:
        """
        Get an interaction by ID
        """
        return self.db.query(Interaction).filter(Interaction.id == interaction_id).first()
    
    def get_interactions_by_hcp(self, hcp_id: int) -> List[Interaction]:
        """
        Get all interactions for a specific HCP
        """
        return self.db.query(Interaction).filter(Interaction.hcp_id == hcp_id).all()
    
    def update_interaction(self, interaction_id: int, updates: InteractionUpdate) -> Optional[Interaction]:
        """
        Update an existing interaction
        """
        db_interaction = self.get_interaction(interaction_id)
        if not db_interaction:
            return None
        
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_interaction, field, value)
        
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction
    
    def delete_interaction(self, interaction_id: int) -> bool:
        """
        Delete an interaction
        """
        db_interaction = self.get_interaction(interaction_id)
        if not db_interaction:
            return False
        
        self.db.delete(db_interaction)
        self.db.commit()
        return True
    
    def search_hcp_by_name(self, name: str) -> List[HCP]:
        """
        Search for HCPs by name
        """
        return self.db.query(HCP).filter(HCP.name.ilike(f"%{name}%")).all()
