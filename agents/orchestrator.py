"""
Sri Lanka Travel Agent - Multi-Agent Orchestrator
Uses Google ADK Multi-Agent System with Human-in-the-Loop Pattern

This orchestrator provides:
1. Full planning workflow with human approval
2. Approval management for human-in-the-loop pattern
"""
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import the main agent
from agents.workflow import root_agent

# Import approval management
from tools.human_approval_tool import (
    submit_approval_decision,
    get_approval_status,
    get_all_pending_approvals,
    process_human_decision,
    pending_approvals,
    approval_responses
)

load_dotenv()

# =============================================================================
# SESSION MANAGEMENT
# =============================================================================
session_service = InMemorySessionService()

# Store active sessions for multi-turn conversations
active_sessions = {}


def get_or_create_session(user_id: str = "default_user"):
    """Get existing session or create new one for a user."""
    if user_id not in active_sessions:
        session = session_service.create_session(
            app_name="sri_lanka_travel_agent",
            user_id=user_id
        )
        active_sessions[user_id] = session
    return active_sessions[user_id]


# =============================================================================
# RUNNER FOR WORKFLOW
# =============================================================================

# Main planning agent runner
planning_runner = Runner(
    agent=root_agent,
    app_name="sri_lanka_travel_agent",
    session_service=session_service
)


# =============================================================================
# MAIN PROCESSING FUNCTIONS
# =============================================================================

def process_request(user_input: str, user_id: str = "default_user", require_approval: bool = True) -> dict:
    """
    Process a travel planning request through the multi-agent system.
    
    Args:
        user_input: The user's travel planning request
        user_id: Unique identifier for the user session
        require_approval: Whether to use full workflow with human approval
    
    Returns:
        Dictionary containing response, status, and approval info if applicable
    """
    session = get_or_create_session(user_id)
    
    try:
        # Use the main planning workflow
        response = planning_runner.run(
            user_id=user_id,
            session_id=session.id,
            new_message=user_input
        )
        
        # Extract the final response
        result = {
            "status": "success",
            "response": response.text if hasattr(response, 'text') else str(response),
            "user_id": user_id,
            "session_id": session.id,
            "require_approval": require_approval
        }
        
        # Check for pending approvals
        pending = [
            req for req in pending_approvals.values() 
            if req["status"] == "pending"
        ]
        
        if pending:
            result["pending_approval"] = pending[-1]  # Most recent
            result["approval_required"] = True
        else:
            result["approval_required"] = False
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id
        }


def process_approval(
    request_id: str,
    decision: str,
    feedback: str = None,
    modifications: str = None,
    user_id: str = "default_user"
) -> dict:
    """
    Process a human approval decision.
    
    Args:
        request_id: The approval request ID
        decision: APPROVED, APPROVED_WITH_CHANGES, REJECTED, or REQUEST_CHANGES
        feedback: Optional feedback from reviewer
        modifications: Optional modifications to apply
        user_id: User identifier for session context
    
    Returns:
        Result of the approval processing
    """
    # Submit the decision
    result = submit_approval_decision(request_id, decision, feedback, modifications)
    
    # Process the decision
    decision_result = process_human_decision(request_id)
    
    # If approved, continue the workflow
    if decision_result["proceed"]:
        session = get_or_create_session(user_id)
        
        # Continue workflow with approval result
        continuation_message = f"""
        Human approval received:
        - Decision: {decision}
        - Feedback: {feedback or 'None'}
        - Modifications: {modifications or 'None'}
        
        Please proceed with the final response.
        """
        
        try:
            response = planning_runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=continuation_message
            )
            
            return {
                "status": "success",
                "decision": decision,
                "proceed": True,
                "response": response.text if hasattr(response, 'text') else str(response),
                "message": decision_result["message"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "decision": decision
            }
    else:
        return {
            "status": "success",
            "decision": decision,
            "proceed": False,
            "message": decision_result["message"],
            "modifications": decision_result.get("modifications")
        }


def get_pending_approvals() -> list:
    """Get all pending approval requests."""
    return [
        req for req in pending_approvals.values() 
        if req["status"] == "pending"
    ]


def get_session_state(user_id: str = "default_user") -> dict:
    """Get the current session state for debugging/monitoring."""
    if user_id in active_sessions:
        session = active_sessions[user_id]
        return {
            "session_id": session.id,
            "user_id": user_id,
            "state": dict(session.state) if hasattr(session, 'state') else {}
        }
    return {"error": "No active session for user"}


def clear_session(user_id: str = "default_user"):
    """Clear a user's session to start fresh."""
    if user_id in active_sessions:
        del active_sessions[user_id]
    return {"status": "session_cleared", "user_id": user_id}


# =============================================================================
# SIMPLE INTERFACE (Backward Compatible)
# =============================================================================

def simple_process(user_input: str) -> str:
    """
    Simple interface for backward compatibility.
    Returns just the response text.
    """
    result = process_request(user_input, require_approval=False)
    if result["status"] == "success":
        return result["response"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


# Legacy function name for backward compatibility
def process_request_legacy(user_input: str) -> str:
    """Legacy function for backward compatibility."""
    return simple_process(user_input)
