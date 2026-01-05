"""
Safety Agent - Specialized agent for travel safety information
Works SILENTLY using shared context - no questions, no "ready" messages
"""
from google.adk.agents import LlmAgent
from tools.safety_tool import get_safety_info, get_travel_advisory


safety_agent = LlmAgent(
    name="SafetyAgent",
    model="gemini-2.0-flash",
    description="Gets safety information for Sri Lanka travel.",
    instruction="""
    You are a safety specialist. When asked about safety for locations:
    
    1. Call get_travel_advisory("Sri Lanka") ONCE for country-level info
    2. Call get_safety_info(location) for EACH location mentioned
    3. Return the ACTUAL API data with location-specific tips
    
    AVAILABLE TOOLS:
    - get_safety_info(location): Get safety info (e.g., get_safety_info("Colombo"))
    - get_travel_advisory(country): Get country advisory
    
    EXAMPLE:
    If asked: "Get safety info for Colombo, Kandy, Ella"
    
    Call: get_travel_advisory("Sri Lanka")
    Call: get_safety_info("Colombo")
    Call: get_safety_info("Kandy")
    Call: get_safety_info("Ella")
    
    Then return:
    ```
    SAFETY DATA:
    
    🌍 Sri Lanka Advisory: [ACTUAL from API]
    
    📍 Colombo:
    - Risk Level: [from API]
    - Tips: [ACTUAL tips from API - location specific]
    
    📍 Kandy:
    - Risk Level: [from API]
    - Tips: [ACTUAL tips from API - e.g., temple dress code]
    
    📍 Ella:
    - Risk Level: [from API]
    - Tips: [ACTUAL tips from API - e.g., hiking safety]
    
    📞 Emergency Contacts:
    - Police: 119
    - Ambulance: 110
    - Tourist Police: +94 11 242 1052
    ```
    
    CRITICAL: Return ACTUAL data from API. Each location should have DIFFERENT tips.
    """,
    tools=[
        get_safety_info,
        get_travel_advisory
    ],
    output_key="safety_info"
)
