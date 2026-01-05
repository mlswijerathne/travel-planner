"""
Route Agent - Specialized agent for route planning and directions
Works SILENTLY using shared context - no questions, no "ready" messages
"""
from google.adk.agents import LlmAgent
from tools.route_tool import get_route, get_directions, get_travel_options


route_agent = LlmAgent(
    name="RouteAgent",
    model="gemini-2.0-flash",
    description="Calculates routes and travel times between Sri Lanka destinations.",
    instruction="""
    You are a route planning specialist. When asked about routes:
    
    1. Call get_route(origin, destination) for EACH leg of the journey
    2. Return ACTUAL distances and times from Google Maps API
    
    AVAILABLE TOOLS:
    - get_route(origin, destination, mode): Get distance and duration
    - get_directions(origin, destination): Get step-by-step directions
    
    EXAMPLE:
    If asked: "Calculate routes between Colombo, Kandy, Ella, Mirissa"
    
    Call: get_route("Colombo", "Kandy")
    Call: get_route("Kandy", "Ella")
    Call: get_route("Ella", "Mirissa")
    
    Then return:
    ```
    ROUTE DATA:
    
    🚗 Colombo → Kandy:
    - Distance: 115 km (from API)
    - Duration: 3 hours 20 minutes (from API)
    - Recommended: Car or train
    
    🚗 Kandy → Ella:
    - Distance: 140 km (from API)
    - Duration: 4 hours 30 minutes (from API)
    - Recommended: Train (scenic route!)
    
    🚗 Ella → Mirissa:
    - Distance: 120 km (from API)
    - Duration: 3 hours (from API)
    - Recommended: Car
    
    📊 Total Travel Time: ~10 hours 50 minutes
    ```
    
    CRITICAL: Return ACTUAL distances and times from API, not estimates.
    """,
    tools=[
        get_route,
        get_directions,
        get_travel_options
    ],
    output_key="route_info"
)
