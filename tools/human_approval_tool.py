"""
Human Approval Tool - Implements Human-in-the-Loop pattern
Pauses workflow for human review and approval of travel plans
"""
import asyncio
from typing import Optional
from datetime import datetime


# Global storage for pending approvals (in production, use a database/queue)
pending_approvals = {}
approval_responses = {}


async def request_human_approval(
    plan_summary: str,
    estimated_budget: str,
    trip_duration: str,
    destinations: str,
    safety_concerns: str = "None identified"
) -> str:
    """
    Sends the travel plan for human review and waits for approval.
    This tool pauses the workflow until the human responds.
    
    Args:
        plan_summary: Brief summary of the proposed travel plan
        estimated_budget: Total estimated budget for the trip
        trip_duration: Duration of the trip (e.g., "5 days")
        destinations: List of main destinations
        safety_concerns: Any safety concerns identified (if any)
    
    Returns:
        Human's decision with any modifications requested
    """
    request_id = f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    approval_request = {
        "request_id": request_id,
        "plan_summary": plan_summary,
        "estimated_budget": estimated_budget,
        "trip_duration": trip_duration,
        "destinations": destinations,
        "safety_concerns": safety_concerns,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # Store the pending approval
    pending_approvals[request_id] = approval_request
    
    # In a real implementation, this would:
    # 1. Send notification to human (email, UI, Slack, etc.)
    # 2. Wait for response via webhook or polling
    # For demo purposes, we return a formatted request for the API to handle
    
    return f"""
🔔 HUMAN APPROVAL REQUIRED

Request ID: {request_id}
Status: PENDING

📋 Plan Summary:
{plan_summary}

💰 Estimated Budget: {estimated_budget}
📅 Duration: {trip_duration}
📍 Destinations: {destinations}

⚠️ Safety Concerns: {safety_concerns}

---
To approve this plan, respond with your decision:
- APPROVED: Proceed with the plan
- APPROVED_WITH_CHANGES: Approve with modifications (specify changes)
- REJECTED: Reject the plan (provide reason)
- REQUEST_CHANGES: Request specific changes before approval

Awaiting human decision...
"""


def submit_approval_decision(
    request_id: str,
    decision: str,
    feedback: Optional[str] = None,
    modifications: Optional[str] = None
) -> str:
    """
    Submit the human's approval decision for a pending request.
    
    Args:
        request_id: The approval request ID
        decision: One of: APPROVED, APPROVED_WITH_CHANGES, REJECTED, REQUEST_CHANGES
        feedback: Optional feedback from the human
        modifications: Optional modifications to apply
    
    Returns:
        Confirmation of the submitted decision
    """
    if request_id not in pending_approvals:
        return f"❌ Error: Request ID '{request_id}' not found"
    
    valid_decisions = ["APPROVED", "APPROVED_WITH_CHANGES", "REJECTED", "REQUEST_CHANGES"]
    if decision.upper() not in valid_decisions:
        return f"❌ Error: Invalid decision. Must be one of: {valid_decisions}"
    
    approval_responses[request_id] = {
        "request_id": request_id,
        "decision": decision.upper(),
        "feedback": feedback,
        "modifications": modifications,
        "responded_at": datetime.now().isoformat()
    }
    
    pending_approvals[request_id]["status"] = decision.upper()
    
    return f"""
✅ Decision Recorded

Request ID: {request_id}
Decision: {decision.upper()}
Feedback: {feedback or 'None'}
Modifications: {modifications or 'None'}

The workflow will now proceed based on this decision.
"""


def get_approval_status(request_id: str) -> str:
    """
    Check the status of an approval request.
    
    Args:
        request_id: The approval request ID to check
    
    Returns:
        Current status of the approval request
    """
    if request_id not in pending_approvals:
        return f"❌ Request ID '{request_id}' not found"
    
    approval = pending_approvals[request_id]
    response = approval_responses.get(request_id)
    
    if response:
        return f"""
📋 Approval Status: {approval['status']}

Original Request:
- Plan: {approval['plan_summary'][:100]}...
- Budget: {approval['estimated_budget']}
- Duration: {approval['trip_duration']}

Human Response:
- Decision: {response['decision']}
- Feedback: {response.get('feedback', 'None')}
- Modifications: {response.get('modifications', 'None')}
- Responded At: {response['responded_at']}
"""
    else:
        return f"""
⏳ Approval Status: PENDING

Request ID: {request_id}
Created: {approval['created_at']}
Awaiting human decision...
"""


def get_all_pending_approvals() -> str:
    """
    Get all pending approval requests.
    
    Returns:
        List of all pending approval requests
    """
    pending = [
        req for req in pending_approvals.values() 
        if req["status"] == "pending"
    ]
    
    if not pending:
        return "✅ No pending approval requests"
    
    result = f"📋 Pending Approvals ({len(pending)}):\n\n"
    for req in pending:
        result += f"""
---
Request ID: {req['request_id']}
Created: {req['created_at']}
Duration: {req['trip_duration']}
Budget: {req['estimated_budget']}
Destinations: {req['destinations']}
"""
    
    return result


def process_human_decision(request_id: str) -> dict:
    """
    Process the human's decision and return structured data for the workflow.
    
    Args:
        request_id: The approval request ID
    
    Returns:
        Dictionary with decision details for workflow processing
    """
    if request_id not in approval_responses:
        return {
            "status": "pending",
            "proceed": False,
            "message": "Awaiting human decision"
        }
    
    response = approval_responses[request_id]
    decision = response["decision"]
    
    if decision == "APPROVED":
        return {
            "status": "approved",
            "proceed": True,
            "message": "Plan approved by human reviewer",
            "modifications": None
        }
    elif decision == "APPROVED_WITH_CHANGES":
        return {
            "status": "approved_with_changes",
            "proceed": True,
            "message": "Plan approved with modifications",
            "modifications": response.get("modifications")
        }
    elif decision == "REJECTED":
        return {
            "status": "rejected",
            "proceed": False,
            "message": f"Plan rejected: {response.get('feedback', 'No reason provided')}",
            "modifications": None
        }
    else:  # REQUEST_CHANGES
        return {
            "status": "changes_requested",
            "proceed": False,
            "message": f"Changes requested: {response.get('modifications', 'See feedback')}",
            "modifications": response.get("modifications")
        }
