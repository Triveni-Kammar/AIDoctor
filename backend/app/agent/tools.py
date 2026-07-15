from langchain_core.tools import tool
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import json


@tool
def log_interaction(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log an HCP interaction to the database.
    Uses LLM for summarization and entity extraction.
    
    Args:
        interaction_data: Dictionary containing interaction details including
            hcp_id, interaction_type, date, time, attendees, topics_discussed,
            sentiment, outcomes, follow_up_actions, materials_shared, samples_distributed
    
    Returns:
        Dictionary with success status and interaction ID
    """
    # Persist to SQL database using SQLAlchemy session
    from app.database import SessionLocal
    from app.models.interaction import Interaction

    db = SessionLocal()
    try:
        payload = dict(interaction_data or {})

        # Normalize date (FastAPI/Pydantic might already send ISO strings)
        date_val = payload.get("date")
        if isinstance(date_val, str) and date_val:
            try:
                payload["date"] = datetime.fromisoformat(date_val)
            except ValueError:
                # keep as-is; validation tool will catch format problems
                pass

        db_interaction = Interaction(**payload)
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)

        return {
            "success": True,
            "interaction_id": db_interaction.id,
            "message": "Interaction logged successfully",
            "data": payload,
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to log interaction: {e}"}
    finally:
        db.close()


@tool
def edit_interaction(interaction_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Edit an existing logged interaction.
    Allows modification of logged data with AI validation.
    
    Args:
        interaction_id: ID of the interaction to edit
        updates: Dictionary of fields to update with new values
    
    Returns:
        Dictionary with success status and updated data
    """
    from app.database import SessionLocal
    from app.models.interaction import Interaction

    db = SessionLocal()
    try:
        db_interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not db_interaction:
            return {"success": False, "message": "Interaction not found", "interaction_id": interaction_id}

        update_payload = dict(updates or {})
        if "date" in update_payload and isinstance(update_payload["date"], str) and update_payload["date"]:
            try:
                update_payload["date"] = datetime.fromisoformat(update_payload["date"])
            except ValueError:
                pass

        for field, value in update_payload.items():
            if hasattr(db_interaction, field):
                setattr(db_interaction, field, value)

        db.commit()
        db.refresh(db_interaction)

        return {
            "success": True,
            "interaction_id": interaction_id,
            "message": "Interaction updated successfully",
            "updated_fields": list(update_payload.keys()),
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to edit interaction: {e}", "interaction_id": interaction_id}
    finally:
        db.close()


@tool
def search_hcp(query: str) -> Dict[str, Any]:
    """
    Search for HCPs in the database by name, specialty, or organization.
    
    Args:
        query: Search term for HCP
    
    Returns:
        Dictionary with list of matching HCPs
    """
    from app.database import SessionLocal
    from app.models.hcp import HCP

    db = SessionLocal()
    try:
        q = (query or "").strip()
        if not q:
            return {"success": True, "results": [], "count": 0}

        hcps = db.query(HCP).filter(HCP.name.ilike(f"%{q}%")).limit(10).all()
        results = [
            {"id": h.id, "name": h.name, "specialty": h.specialty, "organization": h.organization}
            for h in hcps
        ]
        return {"success": True, "results": results, "count": len(results)}
    finally:
        db.close()


@tool
def extract_entities(description: str) -> Dict[str, Any]:
    """
    Extract key entities from natural language description.
    Extracts: HCP name, date, time, interaction type, topics, sentiment, outcomes, attendees
    
    Args:
        description: Natural language description of the interaction
    
    Returns:
        Dictionary with extracted entities
    """
    # LLM-powered extraction (mandatory LLM usage)
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage
    from app.config import settings

    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.1,
    )

    system_prompt = """
You are an AI assistant for a Healthcare Professional CRM system.
Extract structured interaction entities from the user's text.

Return ONLY valid JSON with these keys:
- hcp_name (string|null)
- date (string|null)  // YYYY-MM-DD if present
- time (string|null)  // HH:MM if present
- interaction_type (string|null) // e.g., Meeting, Call, Email
- attendees (string|null)
- topics_discussed (string|null)
- sentiment (string) // Positive|Neutral|Negative
- outcomes (string|null)
- follow_up_actions (string|null)
- materials (array of strings)
- samples (array of strings)
"""

    resp = llm.invoke(
        [
            SystemMessage(content=system_prompt.strip()),
            HumanMessage(content=f"Text:\n{description}".strip()),
        ]
    )

    content = (resp.content or "").strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    try:
        entities = json.loads(content.strip())
    except json.JSONDecodeError:
        # fallback minimal structure if model returns malformed JSON
        entities = {
            "hcp_name": None,
            "date": None,
            "time": None,
            "interaction_type": None,
            "attendees": None,
            "topics_discussed": description,
            "sentiment": "Neutral",
            "outcomes": None,
            "follow_up_actions": None,
            "materials": [],
            "samples": [],
        }

    # normalize sentiment
    sent = (entities.get("sentiment") or "Neutral").capitalize()
    if sent not in {"Positive", "Neutral", "Negative"}:
        sent = "Neutral"
    entities["sentiment"] = sent

    return {"success": True, "entities": entities}


@tool
def get_hcp_profile(hcp_id: int) -> Dict[str, Any]:
    """
    Retrieve HCP profile and recent interaction stats for sales planning.
    """
    from app.database import SessionLocal
    from app.models.hcp import HCP
    from app.models.interaction import Interaction

    db = SessionLocal()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return {"success": False, "message": "HCP not found"}

        recent = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.date.desc())
            .limit(5)
            .all()
        )

        return {
            "success": True,
            "hcp": {
                "id": hcp.id,
                "name": hcp.name,
                "specialty": hcp.specialty,
                "organization": hcp.organization,
                "contact_info": hcp.contact_info,
            },
            "recent_interactions": [
                {"id": i.id, "interaction_type": i.interaction_type, "date": i.date.isoformat(), "sentiment": i.sentiment}
                for i in recent
            ],
        }
    finally:
        db.close()


@tool
def next_best_action(interaction_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sales-oriented next best action recommendation for the rep.
    """
    sentiment = (interaction_context.get("sentiment") or "Neutral").capitalize()
    topics = (interaction_context.get("topics_discussed") or "").lower()

    if sentiment == "Negative":
        nba = "Escalate to MSL and share evidence addressing objections"
    elif "trial" in topics or "phase" in topics:
        nba = "Offer a short data deep-dive with Medical Affairs"
    elif sentiment == "Positive":
        nba = "Propose a follow-up meeting and explore KOL/referral opportunities"
    else:
        nba = "Send a concise recap + relevant material and schedule follow-up"

    return {"success": True, "recommendation": nba}


@tool
def suggest_followups(interaction_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-suggested follow-up actions based on interaction context.
    Analyzes topics, sentiment, outcomes to suggest relevant next steps.
    
    Args:
        interaction_context: Dictionary with interaction details including
            topics_discussed, sentiment, outcomes, hcp_specialty
    
    Returns:
        Dictionary with list of suggested follow-up actions
    """
    topics = interaction_context.get("topics_discussed", "").lower()
    sentiment = interaction_context.get("sentiment", "Neutral")
    outcomes = interaction_context.get("outcomes", "").lower()
    
    suggestions = []
    
    # Base suggestions
    suggestions.append("Schedule follow-up meeting in 2 weeks")
    
    # Topic-specific suggestions
    if "product" in topics or "efficacy" in topics:
        suggestions.append("Send clinical trial data PDF")
        suggestions.append("Share peer-reviewed publication")
    
    if "phase iii" in topics or "trial" in topics:
        suggestions.append("Provide Phase III trial results summary")
        suggestions.append("Schedule presentation with medical affairs")
    
    if "advisory" in topics or "board" in topics:
        suggestions.append("Add to advisory board invite list")
        suggestions.append("Send advisory board charter document")
    
    if "sample" in topics:
        suggestions.append("Follow up on sample usage feedback")
        suggestions.append("Schedule sample replenishment visit")
    
    # Sentiment-based suggestions
    if sentiment == "Positive":
        suggestions.append("Request referral to colleague")
        suggestions.append("Explore KOL partnership opportunities")
    elif sentiment == "Negative":
        suggestions.append("Schedule medical science liaison visit")
        suggestions.append("Address specific concerns with data")
    
    # Outcome-based suggestions
    if "agreed" in outcomes or "committed" in outcomes:
        suggestions.append("Send meeting summary confirmation")
        suggestions.append("Set calendar reminder for agreed actions")
    
    return {
        "success": True,
        "suggestions": suggestions[:5]  # Return top 5 suggestions
    }


@tool
def validate_interaction(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate interaction data for completeness and accuracy.
    Checks required fields, data formats, and logical consistency.
    
    Args:
        interaction_data: Dictionary with interaction form data
    
    Returns:
        Dictionary with validation status and list of errors/warnings
    """
    errors = []
    warnings = []
    
    # Required field validation
    required_fields = ["hcp_id", "interaction_type", "date"]
    for field in required_fields:
        if field not in interaction_data or not interaction_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Date validation
    if "date" in interaction_data:
        try:
            datetime.fromisoformat(str(interaction_data["date"]))
        except (ValueError, TypeError):
            errors.append("Invalid date format")
    
    # Time validation
    if "time" in interaction_data and interaction_data["time"]:
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, interaction_data["time"]):
            errors.append("Invalid time format (use HH:MM)")
    
    # Sentiment validation
    if "sentiment" in interaction_data:
        valid_sentiments = ["Positive", "Neutral", "Negative"]
        if interaction_data["sentiment"] not in valid_sentiments:
            errors.append(f"Invalid sentiment. Must be one of: {valid_sentiments}")
    
    # Warnings
    if not interaction_data.get("topics_discussed"):
        warnings.append("No topics discussed - consider adding key discussion points")
    
    if not interaction_data.get("outcomes"):
        warnings.append("No outcomes recorded - consider adding interaction outcomes")
    
    return {
        "success": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0
    }


# List of all tools for the agent
AGENT_TOOLS = [
    log_interaction,
    edit_interaction,
    search_hcp,
    get_hcp_profile,
    extract_entities,
    suggest_followups,
    validate_interaction,
    next_best_action,
]
