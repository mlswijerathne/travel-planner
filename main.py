"""
Sri Lanka Travel Agent - Multi-Agent API with Human-in-the-Loop Pattern

This FastAPI application provides:
1. Full travel planning with human approval workflow
2. Quick planning for simple queries
3. Approval management endpoints for human-in-the-loop
4. Session management for multi-turn conversations

Based on Google ADK Multi-Agent architecture:
https://google.github.io/adk-docs/agents/multi-agents/
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv
import os

load_dotenv()

# Import multi-agent orchestrator
from agents.orchestrator import (
    process_request,
    process_approval,
    get_pending_approvals,
    get_session_state,
    clear_session,
    simple_process
)

# Import approval management for status checks
from tools.human_approval_tool import (
    get_approval_status,
    pending_approvals
)

app = FastAPI(
    title="Sri Lanka Travel Agent - Multi-Agent API",
    description="""
    AI-powered travel planning for Sri Lanka using Google ADK Multi-Agent System.
    
    Features:
    - Multi-agent architecture with specialized agents
    - Human-in-the-loop approval workflow
    - Real-time data from OpenWeatherMap, Google Maps, and Google Places
    - Parallel processing for efficient data gathering
    """,
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class TravelRequest(BaseModel):
    """Request model for travel planning."""
    query: str = Field(..., description="User's travel planning query")
    user_id: Optional[str] = Field("default_user", description="Unique user identifier")
    require_approval: Optional[bool] = Field(True, description="Whether to require human approval")


class TravelResponse(BaseModel):
    """Response model for travel planning."""
    status: str
    response: str
    user_id: str
    session_id: Optional[str] = None
    approval_required: Optional[bool] = False
    pending_approval: Optional[dict] = None


class ApprovalRequest(BaseModel):
    """Request model for submitting approval decision."""
    request_id: str = Field(..., description="The approval request ID")
    decision: str = Field(..., description="APPROVED, APPROVED_WITH_CHANGES, REJECTED, or REQUEST_CHANGES")
    feedback: Optional[str] = Field(None, description="Optional feedback from reviewer")
    modifications: Optional[str] = Field(None, description="Optional modifications to apply")
    user_id: Optional[str] = Field("default_user", description="User identifier")


class ApprovalResponse(BaseModel):
    """Response model for approval submission."""
    status: str
    decision: str
    proceed: bool
    message: str
    response: Optional[str] = None
    modifications: Optional[str] = None


class PendingApproval(BaseModel):
    """Model for pending approval details."""
    request_id: str
    plan_summary: str
    estimated_budget: str
    trip_duration: str
    destinations: str
    safety_concerns: str
    status: str
    created_at: str


class SimpleRequest(BaseModel):
    """Simple request for backward compatibility."""
    query: str


class SimpleResponse(BaseModel):
    """Simple response for backward compatibility."""
    plan: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
def read_root():
    """Welcome endpoint with API information."""
    return {
        "message": "Welcome to the Sri Lanka Travel Agent - Multi-Agent API",
        "version": "2.0",
        "features": [
            "Multi-agent architecture",
            "Human-in-the-loop approval",
            "Parallel data gathering",
            "Real-time APIs"
        ],
        "endpoints": {
            "/plan": "Full planning with approval workflow",
            "/quick-plan": "Quick planning without approval",
            "/approve": "Submit approval decision",
            "/pending-approvals": "Get pending approvals",
            "/approval-status/{request_id}": "Check approval status",
            "/session/{user_id}": "Get session state",
            "/clear-session/{user_id}": "Clear user session"
        }
    }


@app.post("/plan", response_model=TravelResponse)
async def generate_plan(request: TravelRequest):
    """
    Generate a travel plan using the multi-agent system.
    
    This endpoint:
    1. Analyzes your travel request
    2. Gathers safety, weather, activity, route, and budget info in parallel
    3. Synthesizes a comprehensive travel plan
    4. Requests human approval before finalizing (if require_approval=True)
    """
    try:
        result = process_request(
            user_input=request.query,
            user_id=request.user_id,
            require_approval=request.require_approval
        )
        
        if result["status"] == "success":
            return TravelResponse(
                status="success",
                response=result["response"],
                user_id=result["user_id"],
                session_id=result.get("session_id"),
                approval_required=result.get("approval_required", False),
                pending_approval=result.get("pending_approval")
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quick-plan", response_model=SimpleResponse)
async def quick_plan(request: SimpleRequest):
    """
    Quick travel planning without human approval.
    Use for simple queries or quick information requests.
    """
    try:
        result = simple_process(request.query)
        return SimpleResponse(plan=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approve", response_model=ApprovalResponse)
async def submit_approval(request: ApprovalRequest):
    """
    Submit a human approval decision for a pending travel plan.
    
    Decisions:
    - APPROVED: Proceed with the plan as-is
    - APPROVED_WITH_CHANGES: Approve with specified modifications
    - REJECTED: Reject the plan (provide reason in feedback)
    - REQUEST_CHANGES: Request specific changes before approval
    """
    valid_decisions = ["APPROVED", "APPROVED_WITH_CHANGES", "REJECTED", "REQUEST_CHANGES"]
    if request.decision.upper() not in valid_decisions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid decision. Must be one of: {valid_decisions}"
        )
    
    try:
        result = process_approval(
            request_id=request.request_id,
            decision=request.decision.upper(),
            feedback=request.feedback,
            modifications=request.modifications,
            user_id=request.user_id
        )
        
        return ApprovalResponse(
            status=result["status"],
            decision=result["decision"],
            proceed=result.get("proceed", False),
            message=result.get("message", ""),
            response=result.get("response"),
            modifications=result.get("modifications")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pending-approvals", response_model=List[PendingApproval])
async def list_pending_approvals():
    """Get all pending approval requests."""
    pending = get_pending_approvals()
    return [
        PendingApproval(
            request_id=req["request_id"],
            plan_summary=req["plan_summary"],
            estimated_budget=req["estimated_budget"],
            trip_duration=req["trip_duration"],
            destinations=req["destinations"],
            safety_concerns=req["safety_concerns"],
            status=req["status"],
            created_at=req["created_at"]
        )
        for req in pending
    ]


@app.get("/approval-status/{request_id}")
async def check_approval_status(request_id: str):
    """Check the status of a specific approval request."""
    if request_id not in pending_approvals:
        raise HTTPException(status_code=404, detail=f"Request ID '{request_id}' not found")
    
    return pending_approvals[request_id]


@app.get("/session/{user_id}")
async def get_user_session(user_id: str):
    """Get the current session state for a user."""
    state = get_session_state(user_id)
    if "error" in state:
        raise HTTPException(status_code=404, detail=state["error"])
    return state


@app.delete("/session/{user_id}")
async def clear_user_session(user_id: str):
    """Clear a user's session to start fresh."""
    result = clear_session(user_id)
    return result


# =============================================================================
# LEGACY ENDPOINTS (Backward Compatibility)
# =============================================================================

@app.post("/plan-legacy", response_model=SimpleResponse)
async def generate_plan_legacy(request: SimpleRequest):
    """
    Legacy endpoint for backward compatibility.
    Uses simple processing without approval workflow.
    """
    try:
        result = simple_process(request.query)
        return SimpleResponse(plan=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "multi_agent": True,
        "human_in_the_loop": True,
        "pending_approvals": len(get_pending_approvals())
    }


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
