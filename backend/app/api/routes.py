from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db_session
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionFillRequest,
    InteractionCorrectRequest
)
from app.services.interaction_service import InteractionService
from app.services.llm_service import llm_service
from typing import List
from groq import AuthenticationError as GroqAuthenticationError

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/interactions/log", response_model=InteractionResponse)
async def log_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db_session)
):
    """
    Log a new HCP interaction
    """
    service = InteractionService(db)
    db_interaction = service.create_interaction(interaction)
    return db_interaction


@router.put("/interactions/{interaction_id}", response_model=InteractionResponse)
async def edit_interaction(
    interaction_id: int,
    updates: InteractionUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Edit an existing interaction
    """
    service = InteractionService(db)
    db_interaction = service.update_interaction(interaction_id, updates)
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction


@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Get interaction details by ID
    """
    service = InteractionService(db)
    db_interaction = service.get_interaction(interaction_id)
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction


@router.get("/interactions/hcp/{hcp_id}", response_model=List[InteractionResponse])
async def get_hcp_interactions(
    hcp_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Get all interactions for a specific HCP
    """
    service = InteractionService(db)
    interactions = service.get_interactions_by_hcp(hcp_id)
    return interactions


@router.post("/agent/fill-form")
async def fill_form_from_description(request: InteractionFillRequest):
    """
    AI fills form fields from natural language description
    """
    # Run through LangGraph pipeline (LLM usage is inside tools/nodes)
    from app.agent.graph import create_fill_form_graph
    import anyio

    graph = create_fill_form_graph()
    initial_state = {"messages": [{"role": "user", "content": request.description}]}

    try:
        result_state = await anyio.to_thread.run_sync(lambda: graph.invoke(initial_state))
    except GroqAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Groq authentication failed. Set a valid GROQ_API_KEY in backend/.env",
        )

    return {"success": True, "state": result_state, "form_data": result_state.get("current_form_data")}


@router.post("/agent/log-from-description")
async def log_from_description(request: InteractionFillRequest):
    """
    End-to-end LangGraph flow: extract -> validate -> followups -> persist interaction.
    """
    from app.agent.graph import create_agent_graph
    import anyio

    graph = create_agent_graph()
    initial_state = {"messages": [{"role": "user", "content": request.description}]}

    try:
        result_state = await anyio.to_thread.run_sync(lambda: graph.invoke(initial_state))
    except GroqAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Groq authentication failed. Set a valid GROQ_API_KEY in backend/.env",
        )

    return {
        "success": True,
        "state": result_state,
        "interaction_id": result_state.get("interaction_id"),
        "form_data": result_state.get("current_form_data"),
    }


@router.post("/agent/correct")
async def correct_form_data(request: InteractionCorrectRequest):
    """
    AI corrects form data based on user instruction
    """
    corrected_data = await llm_service.correct_form_data(
        request.current_data,
        request.correction_instruction
    )
    
    return {
        "success": True,
        "corrected_data": corrected_data
    }


@router.post("/agent/chat")
async def chat_with_agent(request: dict):
    """
    Chat with the AI agent, updating/correcting form data dynamically
    """
    from app.agent.graph import create_chat_graph
    import anyio

    conversation_history = request.get("conversation_history", [])
    user_message = request.get("message", "")
    current_form_data = request.get("current_form_data", {})

    graph = create_chat_graph()
    initial_state = {
        "messages": [*conversation_history, {"role": "user", "content": user_message}],
        "current_form_data": current_form_data
    }

    try:
        result_state = await anyio.to_thread.run_sync(lambda: graph.invoke(initial_state))
    except GroqAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Groq authentication failed. Set a valid GROQ_API_KEY in backend/.env",
        )
    messages = result_state.get("messages") or []
    assistant_msg = next((m for m in reversed(messages) if m.get("role") == "assistant"), None)
    updated_form_data = result_state.get("current_form_data")

    return {
        "success": True, 
        "state": result_state, 
        "response": (assistant_msg or {}).get("content", ""),
        "form_data": updated_form_data
    }


@router.post("/agent/suggest-followups")
async def suggest_followups(request: dict):
    """
    Generate AI-suggested follow-up actions
    """
    interaction_context = request.get("interaction_context", {})
    suggestions = await llm_service.generate_followup_suggestions(interaction_context)
    
    return {
        "success": True,
        "suggestions": suggestions
    }


@router.get("/hcps/search")
async def search_hcps(query: str, db: Session = Depends(get_db_session)):
    """
    Search for HCPs by name
    """
    service = InteractionService(db)
    hcps = service.search_hcp_by_name(query)
    return {
        "success": True,
        "results": [{"id": hcp.id, "name": hcp.name, "specialty": hcp.specialty, "organization": hcp.organization} for hcp in hcps]
    }
