from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    current_form_data: Optional[Dict[str, Any]]
    extracted_entities: Optional[Dict[str, Any]]
    interaction_id: Optional[int]
    hcp_id: Optional[int]
    validation_errors: Optional[List[str]]
    suggested_followups: Optional[List[str]]
    correction_result: Optional[Dict[str, Any]]
