from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    extract_entities_node,
    fill_form_node,
    validate_form_node,
    suggest_followups_node,
    log_interaction_node,
    correct_form_node,
    chat_node
)


def create_agent_graph():
    """
    Create the LangGraph agent for HCP interaction logging
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_entities", extract_entities_node)
    workflow.add_node("fill_form", fill_form_node)
    workflow.add_node("validate_form", validate_form_node)
    workflow.add_node("suggest_followups", suggest_followups_node)
    workflow.add_node("log_interaction", log_interaction_node)
    workflow.add_node("correct_form", correct_form_node)
    workflow.add_node("chat", chat_node)
    
    # Set entry point
    workflow.set_entry_point("extract_entities")
    
    # Define edges
    workflow.add_edge("extract_entities", "fill_form")
    workflow.add_edge("fill_form", "validate_form")
    workflow.add_edge("suggest_followups", "log_interaction")
    workflow.add_edge("log_interaction", END)
    
    # Conditional edge for corrections
    workflow.add_conditional_edges(
        "validate_form",
        should_correct,
        {
            "correct": "correct_form",
            "continue": "suggest_followups"
        }
    )
    
    workflow.add_edge("correct_form", "validate_form")
    
    # Compile the graph
    return workflow.compile()


def create_fill_form_graph():
    """
    Create a LangGraph pipeline that fills + validates + suggests follow-ups,
    without persisting to the database.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("extract_entities", extract_entities_node)
    workflow.add_node("fill_form", fill_form_node)
    workflow.add_node("validate_form", validate_form_node)
    workflow.add_node("suggest_followups", suggest_followups_node)
    workflow.add_node("correct_form", correct_form_node)

    workflow.set_entry_point("extract_entities")

    workflow.add_edge("extract_entities", "fill_form")
    workflow.add_edge("fill_form", "validate_form")

    workflow.add_conditional_edges(
        "validate_form",
        should_correct,
        {
            "correct": "correct_form",
            "continue": "suggest_followups",
        },
    )
    workflow.add_edge("correct_form", "validate_form")
    workflow.add_edge("suggest_followups", END)

    return workflow.compile()


def should_correct(state: AgentState) -> str:
    """
    Determine if correction is needed based on validation errors
    """
    if state.get("validation_errors") and len(state["validation_errors"]) > 0:
        return "correct"
    return "continue"


def create_chat_graph():
    """
    Create a simplified graph for conversational interactions
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("chat", chat_node)
    workflow.set_entry_point("chat")
    workflow.add_edge("chat", END)
    
    return workflow.compile()
