"""
Sri Lanka Travel Agent - Agents Package
Multi-Agent System with Review/Critique Pattern
"""
from agents.review_workflow import (
    root_agent_review,
    travel_coordinator_with_review,
    review_workflow,
    initial_plan_generator,
    quality_checker,
    plan_refiner,
    refinement_loop
)

# Export the review pattern as the main agent
root_agent = root_agent_review

__all__ = [
    'root_agent',
    'root_agent_review',
    'travel_coordinator_with_review',
    'review_workflow',
    'initial_plan_generator',
    'quality_checker',
    'plan_refiner',
    'refinement_loop'
]
