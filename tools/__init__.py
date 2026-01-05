"""
Travel Agent Tools Package - All tools use REAL APIs only
Includes Human-in-the-Loop approval tools
"""
from tools.weather_tool import get_weather, get_weather_forecast
from tools.route_tool import get_route, get_directions, get_travel_options
from tools.safety_tool import get_safety_info, get_travel_advisory
from tools.budget_tool import check_budget, get_currency_rate, compare_costs
from tools.activity_tool import get_activities, get_place_details
from tools.human_approval_tool import (
    request_human_approval,
    submit_approval_decision,
    get_approval_status,
    get_all_pending_approvals,
    process_human_decision
)

__all__ = [
    # Weather (OpenWeatherMap API)
    'get_weather',
    'get_weather_forecast',
    
    # Routes (Google Maps Distance Matrix & Directions API)
    'get_route',
    'get_directions',
    'get_travel_options',
    
    # Safety (Google Places Reviews)
    'get_safety_info',
    'get_travel_advisory',
    
    # Budget (Google Places + Exchange Rate API)
    'check_budget',
    'get_currency_rate',
    'compare_costs',
    
    # Activities (Google Places API)
    'get_activities',
    'get_place_details',
    
    # Human-in-the-Loop Approval
    'request_human_approval',
    'submit_approval_decision',
    'get_approval_status',
    'get_all_pending_approvals',
    'process_human_decision'
]
