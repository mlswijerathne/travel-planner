"""
Sri Lanka Travel Agent - Review/Critique Pattern (Generator-Critic)

ARCHITECTURE:
Uses SequentialAgent with shared Session State for communication:

1. INTAKE AGENT - Conversational greeting, collects trip details
2. GENERATOR AGENT - Creates draft travel plan using specialist agents
3. CRITIC AGENT - Reviews draft for issues, suggests improvements  
4. REFINER AGENT - Applies feedback, produces polished final plan

Session State Communication:
- intake_agent → saves to "trip_details"
- generator → reads "trip_details", saves to "draft_plan"
- critic → reads "draft_plan", saves to "review_feedback"
- refiner → reads "draft_plan" + "review_feedback", saves to "final_plan"

Based on Google ADK Multi-Agent documentation:
https://google.github.io/adk-docs/agents/multi-agents/
"""
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import AgentTool

# Import specialist agents
from agents.specialists.weather_agent import weather_agent
from agents.specialists.safety_agent import safety_agent
from agents.specialists.activity_agent import activity_agent
from agents.specialists.route_agent import route_agent
from agents.specialists.budget_agent import budget_agent


# =============================================================================
# STEP 1: INTAKE AGENT - Conversational Greeting & Data Collection
# =============================================================================
intake_agent = LlmAgent(
    name="IntakeAgent",
    model="gemini-2.0-flash",
    description="Greets users and collects trip requirements through conversation.",
    instruction="""
    You are the friendly intake agent for Sri Lanka travel planning.
    
    YOUR ONLY JOB: Greet users and extract trip details.
    
    WHEN USER SAYS HELLO/HI:
    Respond with:
    "🌴 Welcome! I'm your Sri Lanka Travel Planning Assistant!
    
    I can help you plan an amazing trip with:
    • Real-time weather conditions
    • Safety information
    • Activities and attractions
    • Optimal routes
    • Budget estimates
    
    Tell me about your trip! I need:
    📍 Destinations (e.g., Colombo, Kandy, Ella)
    📅 Travel dates and duration
    💡 Your interests (culture, beaches, adventure, food, etc.)
    💰 Budget level (budget, mid-range, luxury)"
    
    WHEN USER PROVIDES TRIP DETAILS:
    Extract and summarize:
    - Destinations list
    - Duration (number of days)
    - Travel dates
    - Interests/preferences
    - Budget level
    
    Then say: "Great! Let me create a personalized travel plan for you..."
    
    OUTPUT FORMAT - You MUST output in this exact format:
    ```
    TRIP DETAILS EXTRACTED:
    - Destinations: [list destinations]
    - Duration: [X days]
    - Dates: [start date] to [end date]
    - Interests: [list interests]
    - Budget: [budget level]
    
    Creating your personalized plan now...
    ```
    """,
    output_key="trip_details"
)


# =============================================================================
# STEP 2: GENERATOR AGENT - Creates Draft Travel Plan Using Specialist Agents
# =============================================================================

# Wrap specialist agents as tools using AgentTool
weather_agent_tool = AgentTool(agent=weather_agent)
safety_agent_tool = AgentTool(agent=safety_agent)
activity_agent_tool = AgentTool(agent=activity_agent)
route_agent_tool = AgentTool(agent=route_agent)
budget_agent_tool = AgentTool(agent=budget_agent)

plan_generator = LlmAgent(
    name="PlanGenerator",
    model="gemini-2.0-flash",
    description="Creates comprehensive draft travel plans by orchestrating specialist agents.",
    instruction="""
    You are the Plan Generator agent. Your job is to create a detailed travel plan by 
    coordinating with specialist agents.
    
    READ FROM SESSION STATE:
    - {trip_details}: Contains destinations, dates, interests, budget
    
    YOUR TASK - FOLLOW THIS ORDER STRICTLY:
    
    STEP 1: Parse trip details from {trip_details}
    Extract: destinations list, dates, duration, interests, budget level
    
    STEP 2: Call specialist agents ONE BY ONE (not all at once!)
    
    A) First, call WeatherAgent ONCE with ALL destinations:
       Ask: "Get weather for Colombo, Kandy, Nuwara Eliya, Ella, Mirissa, Galle"
       WAIT for response before continuing.
    
    B) Then, call SafetyAgent ONCE:
       Ask: "Get safety info for Sri Lanka and these locations: [destinations]"
       WAIT for response before continuing.
    
    C) Then, call ActivityAgent ONCE with interests:
       Ask: "Find [interests] activities in [destinations]"
       WAIT for response before continuing.
    
    D) Then, call RouteAgent ONCE:
       Ask: "Calculate routes between [destinations] in order"
       WAIT for response before continuing.
    
    E) Finally, call BudgetAgent ONCE:
       Ask: "Estimate costs for [duration] days at [budget level] in Sri Lanka"
       WAIT for response before continuing.
    
    STEP 3: Compile all responses into a day-by-day itinerary
    
    IMPORTANT RULES:
    - Call each agent only ONCE with a comprehensive request
    - DO NOT call multiple agents in parallel
    - WAIT for each agent response before calling the next
    - Include ACTUAL DATA from agent responses (not placeholders)
    - If an agent returns an error, note it and continue
    
    OUTPUT FORMAT:
    ```
    🗓️ DRAFT TRAVEL PLAN
    
    📊 Summary:
    - Total Days: X
    - Destinations: [list]
    - Estimated Budget: $XXX (from BudgetAgent)
    
    📅 Day 1: [Date] - [Location]
    🌤️ Weather: [ACTUAL data from WeatherAgent - temp, conditions]
    ⚠️ Safety: [ACTUAL data from SafetyAgent]
    
    🌅 Morning: [ACTUAL activity from ActivityAgent]
    🌞 Afternoon: [ACTUAL activity from ActivityAgent]  
    🌙 Evening: [ACTUAL activity from ActivityAgent]
    💰 Day Cost: $XX [from BudgetAgent]
    
    [Continue for each day...]
    
    📍 Route Summary: [ACTUAL data from RouteAgent]
    - [Origin] → [Destination]: [X hours Y minutes]
    
    💰 Budget Breakdown: [ACTUAL data from BudgetAgent]
    - Accommodation: $XX
    - Transport: $XX
    - Activities: $XX
    - Food: $XX
    - Total: $XXX
    ```
    
    CRITICAL: Use REAL data from agents, not placeholders like "[from WeatherAgent]"
    """,
    tools=[
        weather_agent_tool,
        safety_agent_tool,
        activity_agent_tool,
        route_agent_tool,
        budget_agent_tool
    ],
    output_key="draft_plan"
)


# =============================================================================
# STEP 3: CRITIC AGENT - Reviews and Critiques the Plan
# =============================================================================
plan_critic = LlmAgent(
    name="PlanCritic",
    model="gemini-2.0-flash",
    description="Reviews draft plans and identifies issues and improvements.",
    instruction="""
    You are the Plan Critic agent. Your job is to review and improve travel plans.
    
    READ FROM SESSION STATE:
    - {trip_details}: Original user requirements
    - {draft_plan}: The generated travel plan
    
    YOUR REVIEW CHECKLIST:
    
    ✅ COMPLETENESS:
    - Are all requested destinations included?
    - Does the duration match the request?
    - Are all interests addressed?
    
    ✅ PRACTICALITY:
    - Are travel times realistic?
    - Is there enough time at each destination?
    - Are there any overly rushed days?
    
    ✅ BUDGET FIT:
    - Does the plan fit the stated budget level?
    - Are cost estimates reasonable?
    
    ✅ SAFETY:
    - Are safety concerns properly addressed?
    - Any risky activities for the locations?
    
    ✅ QUALITY:
    - Are there unique/memorable experiences?
    - Good mix of activities?
    - Photography opportunities included?
    
    ✅ WEATHER CONSIDERATIONS:
    - Activities appropriate for expected weather?
    - Backup options for rainy days?
    
    OUTPUT FORMAT:
    ```
    📋 PLAN REVIEW
    
    ✅ STRENGTHS:
    - [What's good about the plan]
    - [Another strength]
    
    ⚠️ ISSUES FOUND:
    1. [Issue]: [Description]
       💡 Suggestion: [How to fix]
    
    2. [Issue]: [Description]
       💡 Suggestion: [How to fix]
    
    🔧 RECOMMENDED IMPROVEMENTS:
    - [Improvement 1]
    - [Improvement 2]
    
    📊 OVERALL RATING: X/10
    
    🎯 KEY CHANGES NEEDED:
    - [Priority change 1]
    - [Priority change 2]
    ```
    
    Be constructive! Focus on making the plan better, not just criticizing.
    """,
    output_key="review_feedback"
)


# =============================================================================
# STEP 4: REFINER AGENT - Applies Feedback & Creates Final Plan
# =============================================================================
plan_refiner = LlmAgent(
    name="PlanRefiner",
    model="gemini-2.0-flash",
    description="Applies critic feedback to create polished final travel plans.",
    instruction="""
    You are the Plan Refiner agent. Your job is to create the final, polished plan.
    
    READ FROM SESSION STATE:
    - {trip_details}: Original user requirements
    - {draft_plan}: The initial travel plan
    - {review_feedback}: Critic's review and suggestions
    
    YOUR TASK:
    1. Read the draft plan carefully
    2. Review the critic's feedback for issues found
    3. For each issue identified:
       - If it's a DATA issue (wrong prices, missing info, incorrect routes):
         → Call the appropriate specialist agent to get CORRECT data
       - If it's a STRUCTURE issue (timing, formatting, missing sections):
         → Fix it directly in your output
    4. Apply ALL suggestions from the critic's review
    5. Create a polished, user-ready final plan
    
    AVAILABLE SPECIALIST AGENTS:
    - WeatherAgent: Re-check weather if critic found weather issues
    - SafetyAgent: Get additional safety info if missing
    - ActivityAgent: Find alternative activities if suggested
    - RouteAgent: Recalculate routes if timing issues found
    - BudgetAgent: Re-estimate costs if budget doesn't match
    
    ISSUE HANDLING EXAMPLES:
    - Critic says "Budget too high for budget traveler" → Call BudgetAgent for budget-tier options
    - Critic says "Missing activities for Day 2" → Call ActivityAgent for that destination
    - Critic says "Travel time unrealistic" → Call RouteAgent to verify
    
    OUTPUT FORMAT:
    ```
    ✨ YOUR PERSONALIZED SRI LANKA ITINERARY ✨
    
    📊 Trip Overview:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📍 Destinations: [list]
    📅 Duration: [X days / Y nights]
    🗓️ Dates: [start] to [end]
    💰 Estimated Budget: $XXX - $XXX
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📅 DAY 1: [Date] - [Location]
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🌤️ Weather: [conditions]
    
    🌅 Morning (8:00 AM - 12:00 PM):
       • [Activity with details]
       • 📸 Photo Tip: [if applicable]
    
    🌞 Afternoon (12:00 PM - 6:00 PM):
       • [Activity with details]
       • 🍽️ Lunch: [recommendation]
    
    🌙 Evening (6:00 PM onwards):
       • [Activity with details]
       • 🍽️ Dinner: [recommendation]
    
    💡 Day Tips:
       • [Useful tip]
       • [Safety note if needed]
    
    💰 Estimated Day Cost: $XX
    
    [Continue for each day...]
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🚗 TRANSPORTATION SUMMARY
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    • Day X: [Origin] → [Destination] (X hours)
    [Continue for all travel segments]
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    💰 BUDGET BREAKDOWN
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🏨 Accommodation: $XX
    🚗 Transportation: $XX
    🎫 Activities: $XX
    🍽️ Food & Drinks: $XX
    🛍️ Shopping/Misc: $XX
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📊 TOTAL: $XXX - $XXX
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📞 EMERGENCY CONTACTS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    • Police: 119
    • Ambulance: 110
    • Tourist Police: +94 11 242 1052
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ This plan has been reviewed and optimized!
    
    Would you like me to adjust anything?
    ```
    
    Make it BEAUTIFUL and EASY TO READ!
    """,
    tools=[
        weather_agent_tool,
        safety_agent_tool,
        activity_agent_tool,
        route_agent_tool,
        budget_agent_tool
    ],
    output_key="final_plan"
)


# =============================================================================
# MAIN WORKFLOW: SequentialAgent (Generator-Critic Pattern)
# =============================================================================
travel_planning_workflow = SequentialAgent(
    name="TravelPlanningWorkflow",
    description="Complete travel planning workflow with review and refinement.",
    sub_agents=[
        intake_agent,      # Step 1: Greet & collect details
        plan_generator,    # Step 2: Create draft plan with real data
        plan_critic,       # Step 3: Review and critique
        plan_refiner       # Step 4: Apply feedback, create final plan
    ]
)


# =============================================================================
# ROOT AGENT: Entry point for ADK
# =============================================================================
# The root_agent is the entry point that ADK looks for
root_agent = travel_planning_workflow


# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    'root_agent',
    'travel_planning_workflow',
    'intake_agent',
    'plan_generator',
    'plan_critic',
    'plan_refiner'
]
