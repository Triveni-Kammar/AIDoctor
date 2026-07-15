from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from app.agent.tools import AGENT_TOOLS
from app.agent.state import AgentState
from app.config import settings
from typing import Dict, Any


def initialize_llm():
    """Initialize the Groq LLM"""
    return ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.1
    )


def extract_entities_node(state: AgentState) -> AgentState:
    """
    Extract entities from the user's description using the extract_entities tool
    """
    llm = initialize_llm()
    
    # Get the latest message
    last_message = state["messages"][-1] if state["messages"] else {}
    description = last_message.get("content", "")
    
    # Use the extract_entities tool
    from app.agent.tools import extract_entities
    result = extract_entities.invoke({"description": description})
    
    state["extracted_entities"] = result["entities"]
    
    # Add AI message about extraction
    state["messages"].append({
        "role": "assistant",
        "content": f"I've extracted the following information from your description:\n"
                   f"HCP: {result['entities'].get('hcp_name', 'Not found')}\n"
                   f"Type: {result['entities'].get('interaction_type', 'Not found')}\n"
                   f"Sentiment: {result['entities'].get('sentiment', 'Neutral')}\n"
                   f"Topics: {result['entities'].get('topics_discussed', 'Not found')}"
    })
    
    return state


def fill_form_node(state: AgentState) -> AgentState:
    """
    Fill the form with extracted entities using LLM to structure the data
    """
    llm = initialize_llm()
    
    entities = state.get("extracted_entities", {})
    
    # Structure the form data
    form_data = {
        "hcp_name": entities.get("hcp_name"),
        "interaction_type": entities.get("interaction_type", "Meeting"),
        "date": entities.get("date"),
        "time": entities.get("time"),
        "attendees": entities.get("attendees"),
        "topics_discussed": entities.get("topics_discussed"),
        "sentiment": entities.get("sentiment", "Neutral"),
        "outcomes": entities.get("outcomes"),
        "follow_up_actions": entities.get("follow_up_actions"),
        "materials_shared": entities.get("materials", []),
        "samples_distributed": entities.get("samples", [])
    }
    
    state["current_form_data"] = form_data
    
    # Add AI message
    state["messages"].append({
        "role": "assistant",
        "content": "I've filled the form with the extracted information. Please review and let me know if any corrections are needed."
    })
    
    return state


def validate_form_node(state: AgentState) -> AgentState:
    """
    Validate the current form data
    """
    from app.agent.tools import validate_interaction
    
    form_data = state.get("current_form_data", {})
    result = validate_interaction.invoke({"interaction_data": form_data})
    
    state["validation_errors"] = result["errors"] if not result["is_valid"] else []
    
    if result["is_valid"]:
        state["messages"].append({
            "role": "assistant",
            "content": "Form validation passed. All required fields are complete."
        })
    else:
        state["messages"].append({
            "role": "assistant",
            "content": f"Validation found {len(result['errors'])} error(s): {', '.join(result['errors'])}"
        })
    
    return state


def suggest_followups_node(state: AgentState) -> AgentState:
    """
    Generate AI-suggested follow-up actions
    """
    from app.agent.tools import suggest_followups
    
    form_data = state.get("current_form_data", {})
    result = suggest_followups.invoke({"interaction_context": form_data})
    
    state["suggested_followups"] = result["suggestions"]
    
    # Update form data with suggestions
    if state["current_form_data"]:
        state["current_form_data"]["ai_suggested_followups"] = result["suggestions"]
    
    return state


def log_interaction_node(state: AgentState) -> AgentState:
    """
    Log the interaction to the database
    """
    from app.agent.tools import log_interaction
    
    form_data = state.get("current_form_data", {})
    
    # Add HCP ID (would come from search in production)
    if not form_data.get("hcp_id") and form_data.get("hcp_name"):
        # In production, this would search and get the actual ID
        form_data["hcp_id"] = 1  # Mock ID
    
    result = log_interaction.invoke({"interaction_data": form_data})
    
    state["interaction_id"] = result["interaction_id"]
    
    state["messages"].append({
        "role": "assistant",
        "content": f"Interaction logged successfully! Interaction ID: {result['interaction_id']}"
    })
    
    return state


def correct_form_node(state: AgentState) -> AgentState:
    """
    Correct form data based on user feedback
    """
    llm = initialize_llm()
    
    last_message = state["messages"][-1] if state["messages"] else {}
    correction_instruction = last_message.get("content", "")
    current_data = state.get("current_form_data", {})
    
    # Use LLM to understand and apply corrections
    import json
    prompt = f"""
    Current form data:
    {json.dumps(current_data, indent=2)}
    
    User correction instruction:
    {correction_instruction}
    
    Apply the correction to the form data. Return the updated form data as JSON.
    Only change the fields that need correction based on the instruction.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        updated_data = json.loads(response.content)
        state["current_form_data"] = updated_data
        state["correction_result"] = {"success": True, "updated_fields": list(updated_data.keys())}
        
        state["messages"].append({
            "role": "assistant",
            "content": "I've applied the correction. Please review the updated form."
        })
    except:
        state["messages"].append({
            "role": "assistant",
            "content": "I couldn't apply the correction automatically. Please specify which field needs to be changed."
        })
    
    return state


def chat_node(state: AgentState) -> AgentState:
    """
    General chat node for conversational interactions, which updates/corrects form data.
    """
    llm = initialize_llm()
    import json
    
    # Get conversation history
    messages = state["messages"]
    current_form_data = state.get("current_form_data") or {
        "hcp_name": "",
        "hcp_id": None,
        "interaction_type": "Meeting",
        "date": "",
        "time": "",
        "attendees": "",
        "topics_discussed": "",
        "sentiment": "Neutral",
        "outcomes": "",
        "follow_up_actions": "",
        "materials_shared": [],
        "samples_distributed": [],
        "ai_suggested_followups": [],
        "voice_note_summary": ""
    }
    
    # Format messages for langchain
    lc_messages = []
    # We will pass the conversation history
    for msg in messages[:-1]:  # Exclude the latest user message which we will add after
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
            
    # System prompt
    system_prompt = f"""
You are an AI assistant for a Healthcare Professional (HCP) CRM system.
Your role is to help field representatives log interactions with HCPs by filling out a form automatically based on conversation.

The user is NOT allowed to edit the form manually. They will describe the interaction, and you must automatically extract and fill/correct the form fields.

Here is the CURRENT form data before this turn:
{json.dumps(current_form_data, indent=2)}

The form data keys and types are:
- hcp_name (string|null)
- interaction_type (string, must be one of: "Meeting", "Call", "Email")
- date (string|null, YYYY-MM-DD format)
- time (string|null, HH:MM format)
- attendees (string|null)
- topics_discussed (string|null)
- sentiment (string, one of: "Positive", "Neutral", "Negative")
- outcomes (string|null)
- follow_up_actions (string|null)
- materials_shared (array of objects with keys `id` and `name`. Allowed materials:
  1: "Product X Brochure"
  2: "Clinical Trial Results PDF"
  3: "Product Presentation"
  4: "Peer-Reviewed Publication"
  5: "Sample Kit Information")
- samples_distributed (array of objects with keys `id`, `name`, and `quantity`. Allowed samples:
  1: "Product X Sample Pack"
  2: "Product Y Sample Pack"
  3: "Product Z Sample Pack")

Task:
1. Analyze the user's message and the conversation history.
2. Determine if the user is providing new details, correcting a mistake / updating an existing field (e.g. "Actually the meeting was yesterday", "No, the sentiment was positive", "Remove the Sample Pack"), or just chatting.
3. Update the form data accordingly. For corrections, overwrite the incorrect fields. Preserve all fields that are not corrected or updated.
4. If the user mentions sharing a material or giving samples, parse those and add them to `materials_shared` and `samples_distributed` arrays with their correct ids and names. If they ask to remove a material or sample, remove it.
5. Perform validation checks:
   - Check if `date` is in valid YYYY-MM-DD format.
   - Check if `time` is in valid HH:MM format.
   - If there's an error, explain it politely in the response and do NOT apply invalid formats.
6. Generate a conversational, helpful response for the chat.
   - Tell the user what you updated or corrected (e.g. "I've filled the HCP name as Dr. Smith...").
   - If they just said hello, greet them.
   - If there are missing mandatory fields (hcp_name, interaction_type, date), prompt the user for them.
7. Generate 3-5 relevant follow-up actions based on the updated form details and update the `ai_suggested_followups` field in the form data (as a list of strings).

Return a valid JSON object ONLY. Do not write any text outside of the JSON block. The JSON block must have exactly these keys:
- "assistant_response": "your conversational response to the user"
- "updated_form_data": the complete updated form data dictionary (with all fields preserved, including any unchanged fields).
"""

    lc_messages.insert(0, SystemMessage(content=system_prompt.strip()))
    
    # Add the latest user message
    lc_messages.append(HumanMessage(content=messages[-1]["content"]))
    
    # Invoke LLM
    response = llm.invoke(lc_messages)
    content = (response.content or "").strip()
    
    # Clean up and parse JSON
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    try:
        parsed_result = json.loads(content.strip())
        assistant_response = parsed_result.get("assistant_response", "I've processed your message.")
        updated_form_data = parsed_result.get("updated_form_data", current_form_data)
    except Exception as e:
        print(f"Error parsing agent JSON response: {e}, Raw response: {content}")
        # Fallback to chat response and no form update
        assistant_response = content
        updated_form_data = current_form_data
        
    state["current_form_data"] = updated_form_data
    state["messages"].append({
        "role": "assistant",
        "content": assistant_response
    })
    
    return state
