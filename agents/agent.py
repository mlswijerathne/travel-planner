"""
Sri Lanka Travel Agent - Root Agent Definition for ADK
This file exports the root_agent for the ADK CLI to discover.

Architecture: Review/Critique Pattern with Iterative Refinement
- TravelCoordinatorWithReview orchestrates specialist sub-agents
- QualityChecker reviews plans for completeness
- LoopAgent refines until quality is sufficient
"""
from agents.review_workflow import root_agent_review, travel_coordinator_with_review

# ADK expects 'root_agent' as the main entry point
# Using the review pattern for automatic quality checking
root_agent = root_agent_review
agent = root_agent_review

__all__ = [
    'root_agent',
    'agent',
    'travel_coordinator_with_review'
]
