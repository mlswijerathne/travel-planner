"""
Shared Context Manager - Centralized trip data storage for multi-agent coordination

This module provides a central state management system that prevents agents from:
1. Re-asking questions that have already been answered
2. Making redundant "I'm ready" announcements
3. Working without access to already-collected data

All agents read from and write to this shared context.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class TripContext:
    """Centralized trip data structure shared across all agents."""
    
    # Core trip details (collected once by intake agent)
    destinations: List[str] = field(default_factory=list)
    trip_duration: str = ""
    travel_dates: str = ""
    interests: List[str] = field(default_factory=list)
    budget_range: str = ""
    group_size: int = 1
    special_requirements: str = ""
    starting_location: str = ""
    
    # Flags to track what data has been collected
    has_core_info: bool = False
    has_weather_info: bool = False
    has_safety_info: bool = False
    has_route_info: bool = False
    has_budget_info: bool = False
    has_activity_info: bool = False
    has_draft_plan: bool = False
    
    # Specialist agent outputs
    weather_data: Dict[str, Any] = field(default_factory=dict)
    safety_data: Dict[str, Any] = field(default_factory=dict)
    route_data: Dict[str, Any] = field(default_factory=dict)
    budget_data: Dict[str, Any] = field(default_factory=dict)
    activity_data: Dict[str, Any] = field(default_factory=dict)
    
    # Error tracking (for single reporting)
    errors: List[Dict[str, str]] = field(default_factory=list)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class SharedContextManager:
    """
    Manages shared context across all agents in the multi-agent system.
    
    Key Features:
    1. Single source of truth for trip data
    2. Prevents duplicate data collection
    3. Tracks which data has been gathered
    4. Consolidates error reporting
    """
    
    _instance = None
    _contexts: Dict[str, TripContext] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_or_create_context(self, session_id: str) -> TripContext:
        """Get existing context or create new one for a session."""
        if session_id not in self._contexts:
            self._contexts[session_id] = TripContext()
        return self._contexts[session_id]
    
    def update_core_info(
        self,
        session_id: str,
        destinations: List[str],
        trip_duration: str,
        travel_dates: str = "",
        interests: List[str] = None,
        budget_range: str = "",
        group_size: int = 1,
        special_requirements: str = "",
        starting_location: str = ""
    ) -> TripContext:
        """Update core trip information (done once at intake)."""
        ctx = self.get_or_create_context(session_id)
        ctx.destinations = destinations
        ctx.trip_duration = trip_duration
        ctx.travel_dates = travel_dates
        ctx.interests = interests or []
        ctx.budget_range = budget_range
        ctx.group_size = group_size
        ctx.special_requirements = special_requirements
        ctx.starting_location = starting_location or (destinations[0] if destinations else "")
        ctx.has_core_info = True
        ctx.last_updated = datetime.now().isoformat()
        return ctx
    
    def update_specialist_data(
        self,
        session_id: str,
        specialist: str,
        data: Dict[str, Any]
    ) -> None:
        """Update data from a specialist agent."""
        ctx = self.get_or_create_context(session_id)
        
        if specialist == "weather":
            ctx.weather_data = data
            ctx.has_weather_info = True
        elif specialist == "safety":
            ctx.safety_data = data
            ctx.has_safety_info = True
        elif specialist == "route":
            ctx.route_data = data
            ctx.has_route_info = True
        elif specialist == "budget":
            ctx.budget_data = data
            ctx.has_budget_info = True
        elif specialist == "activity":
            ctx.activity_data = data
            ctx.has_activity_info = True
        
        ctx.last_updated = datetime.now().isoformat()
    
    def add_error(self, session_id: str, source: str, error_msg: str) -> None:
        """Track an error (for single consolidated reporting later)."""
        ctx = self.get_or_create_context(session_id)
        ctx.errors.append({
            "source": source,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_errors_summary(self, session_id: str) -> str:
        """Get consolidated error summary for final report."""
        ctx = self.get_or_create_context(session_id)
        if not ctx.errors:
            return ""
        
        unique_errors = {}
        for err in ctx.errors:
            key = f"{err['source']}:{err['error']}"
            if key not in unique_errors:
                unique_errors[key] = err
        
        summary = "⚠️ Data Limitations:\n"
        for err in unique_errors.values():
            summary += f"  - {err['source']}: {err['error']}\n"
        
        return summary
    
    def is_ready_for_specialists(self, session_id: str) -> bool:
        """Check if core info is collected and specialists can proceed."""
        ctx = self.get_or_create_context(session_id)
        return ctx.has_core_info
    
    def get_context_summary(self, session_id: str) -> str:
        """Get a formatted summary of collected data for agents."""
        ctx = self.get_or_create_context(session_id)
        
        if not ctx.has_core_info:
            return "No trip details collected yet."
        
        summary = f"""
TRIP CONTEXT (Already Collected - DO NOT ASK AGAIN):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Destinations: {', '.join(ctx.destinations)}
Duration: {ctx.trip_duration}
Dates: {ctx.travel_dates}
Interests: {', '.join(ctx.interests)}
Budget: {ctx.budget_range}
Group Size: {ctx.group_size}
Starting Point: {ctx.starting_location}
Special Requirements: {ctx.special_requirements or 'None'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA STATUS:
- Weather: {'✅ Collected' if ctx.has_weather_info else '⏳ Pending'}
- Safety: {'✅ Collected' if ctx.has_safety_info else '⏳ Pending'}
- Routes: {'✅ Collected' if ctx.has_route_info else '⏳ Pending'}
- Budget: {'✅ Collected' if ctx.has_budget_info else '⏳ Pending'}
- Activities: {'✅ Collected' if ctx.has_activity_info else '⏳ Pending'}
"""
        return summary.strip()
    
    def to_state_dict(self, session_id: str) -> Dict[str, Any]:
        """Convert context to a dictionary for ADK session state."""
        ctx = self.get_or_create_context(session_id)
        return {
            "trip_context": {
                "destinations": ctx.destinations,
                "trip_duration": ctx.trip_duration,
                "travel_dates": ctx.travel_dates,
                "interests": ctx.interests,
                "budget_range": ctx.budget_range,
                "group_size": ctx.group_size,
                "starting_location": ctx.starting_location,
                "special_requirements": ctx.special_requirements,
            },
            "data_collected": {
                "weather": ctx.has_weather_info,
                "safety": ctx.has_safety_info,
                "route": ctx.has_route_info,
                "budget": ctx.has_budget_info,
                "activity": ctx.has_activity_info,
            },
            "errors": ctx.errors
        }
    
    def clear_context(self, session_id: str) -> None:
        """Clear context for a session."""
        if session_id in self._contexts:
            del self._contexts[session_id]


# Global singleton instance
context_manager = SharedContextManager()


def get_context_for_agent(session_id: str = "default") -> str:
    """Helper function for agents to quickly get context summary."""
    return context_manager.get_context_summary(session_id)


def has_trip_details(session_id: str = "default") -> bool:
    """Check if trip details have been collected."""
    return context_manager.is_ready_for_specialists(session_id)
