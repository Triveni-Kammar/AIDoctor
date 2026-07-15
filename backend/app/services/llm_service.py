from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings
from typing import Dict, Any
import json


class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.1
        )
    
    async def fill_form_from_description(self, description: str) -> Dict[str, Any]:
        """
        Use LLM to extract structured form data from natural language description
        """
        system_prompt = """
        You are an AI assistant for a Healthcare Professional CRM system.
        Extract structured information from the interaction description and format it as JSON.
        
        Extract the following fields if present:
        - hcp_name: Name of the healthcare professional
        - interaction_type: Type of interaction (Meeting, Call, Email, etc.)
        - date: Date of interaction (YYYY-MM-DD format)
        - time: Time of interaction (HH:MM format)
        - attendees: Other people present
        - topics_discussed: Key topics discussed
        - sentiment: HCP sentiment (Positive, Neutral, Negative)
        - outcomes: Key outcomes or agreements
        - follow_up_actions: Next steps
        - materials: List of materials shared
        - samples: List of samples distributed
        
        Return only valid JSON. If a field is not found, set it to null.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Interaction description: {description}")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Parse JSON from response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            form_data = json.loads(content.strip())
            return form_data
        except json.JSONDecodeError:
            # Fallback to basic extraction
            return {
                "hcp_name": None,
                "interaction_type": "Meeting",
                "date": None,
                "time": None,
                "attendees": None,
                "topics_discussed": description,
                "sentiment": "Neutral",
                "outcomes": None,
                "follow_up_actions": None,
                "materials": [],
                "samples": []
            }
    
    async def correct_form_data(self, current_data: Dict[str, Any], correction_instruction: str) -> Dict[str, Any]:
        """
        Use LLM to correct form data based on user instruction
        """
        system_prompt = """
        You are an AI assistant for a Healthcare Professional CRM system.
        Apply the user's correction instruction to the current form data.
        
        Return the updated form data as valid JSON.
        Only change the fields that need correction based on the instruction.
        Keep all other fields unchanged.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
            Current form data:
            {json.dumps(current_data, indent=2)}
            
            Correction instruction:
            {correction_instruction}
            
            Return the updated form data as JSON.
            """)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            updated_data = json.loads(content.strip())
            return updated_data
        except json.JSONDecodeError:
            return current_data
    
    async def generate_followup_suggestions(self, interaction_context: Dict[str, Any]) -> list:
        """
        Generate AI-suggested follow-up actions based on interaction context
        """
        system_prompt = """
        You are an AI assistant for a Healthcare Professional CRM system.
        Generate 3-5 relevant follow-up actions based on the interaction context.
        
        Consider:
        - Topics discussed
        - HCP sentiment
        - Outcomes achieved
        - Materials/samples shared
        
        Return suggestions as a JSON array of strings.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Interaction context: {json.dumps(interaction_context, indent=2)}")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            suggestions = json.loads(content.strip())
            return suggestions if isinstance(suggestions, list) else []
        except json.JSONDecodeError:
            return ["Schedule follow-up meeting", "Send additional information"]
    
    async def chat_response(self, conversation_history: list, user_message: str) -> str:
        """
        Generate a conversational response
        """
        system_prompt = """
        You are an AI assistant for a Healthcare Professional (HCP) CRM system.
        Your role is to help field representatives log interactions with HCPs.
        
        You can:
        - Extract information from natural language descriptions
        - Fill form fields automatically
        - Validate form data
        - Suggest follow-up actions
        - Correct mistakes in logged data
        
        Always be helpful, accurate, and professional.
        """
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(HumanMessage(content=msg.get("content", "")))  # Convert to Human for context
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        response = await self.llm.ainvoke(messages)
        return response.content


llm_service = LLMService()
