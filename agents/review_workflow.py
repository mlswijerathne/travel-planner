"""
Sri Lanka Travel Agent - Review/Critique Pattern with Iterative Refinement

This module implements the Review/Critique Pattern from ADK documentation:
https://google.github.io/adk-docs/agents/multi-agents/#reviewcritique-pattern-generator-critic

Architecture:
User → TravelCoordinator → Specialists (via AgentTool) → QualityChecker →
   If insufficient → PlanRefiner (re-calls specialists) → QualityChecker →
   Loop until quality is sufficient → Final response to user

Key Design Decision:
- Specialists are called via AgentTool (explicit invocation)
- This avoids ADK Single Parent Rule conflicts
- Multiple agents can call the same specialists without parent conflicts

Based on ADK patterns:
1. Review/Critique Pattern (Generator-Critic)
2. Iterative Refinement Pattern
3. LoopAgent for quality checking
4. AgentTool for explicit specialist invocation
"""
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent, BaseAgent
from google.adk.tools import AgentTool
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from typing import AsyncGenerator

# Import specialist agents
from agents.specialists.weather_agent import weather_agent
from agents.specialists.safety_agent import safety_agent
from agents.specialists.activity_agent import activity_agent
from agents.specialists.route_agent import route_agent
from agents.specialists.budget_agent import budget_agent


# =============================================================================
# AGENT TOOLS - Wrap specialists as tools (avoids Single Parent Rule)
# =============================================================================
weather_tool = AgentTool(agent=weather_agent)
safety_tool = AgentTool(agent=safety_agent)
activity_tool = AgentTool(agent=activity_agent)
route_tool = AgentTool(agent=route_agent)
budget_tool = AgentTool(agent=budget_agent)

# List of all specialist tools
specialist_tools = [weather_tool, safety_tool, activity_tool, route_tool, budget_tool]


# =============================================================================
# QUALITY CHECKER AGENT - Determines if plan needs refinement
# =============================================================================
quality_checker = LlmAgent(
    name="QualityChecker",
    model="gemini-2.0-flash",
    description="Reviews travel plans and determines if they meet quality standards.",
    instruction="""
    You are the Quality Checker for travel plans. Review the current plan from the conversation.
    
    📋 REVIEW CRITERIA:
    1. **Completeness**: All requirements addressed? (weather, safety, activities, routes, budget)
    2. **Data Quality**: Real data (not placeholders) from specialists?
    3. **Practicality**: Realistic travel times and schedules?
    4. **Safety**: Safety concerns addressed?
    5. **Budget Alignment**: Matches budget requirements?
    6. **Activity Mix**: Balanced activities matching interests?
    
    📊 REVIEW THE DRAFT PLAN:
    Look at the previous messages for the draft plan and user requirements.
    
    ✅ OUTPUT:
    Respond with ONLY one of these two words:
    - "pass" - if plan meets all criteria and has real data
    - "fail" - if plan needs improvement
    
    If "fail", also explain what's missing or needs improvement.
    
    Be strict - only mark as "pass" if the plan has:
    - Real, specific data (not "popular places" or "various activities")
    - Weather information for all destinations
    - Safety advisories
    - Realistic routes with actual times
    - Proper budget breakdown with numbers
    """,
    output_key="quality_status"
)


# =============================================================================
# STOP CHECKER - Custom agent to escalate when quality is sufficient
# =============================================================================
class StopChecker(BaseAgent):
    """
    Checks if quality_status is 'pass' and escalates to stop the loop.
    Based on ADK Iterative Refinement Pattern.
    """
    def __init__(self):
        super().__init__(
            name="StopChecker", 
            description="Checks if plan quality is sufficient to stop refinement loop."
        )
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status_text = ctx.session.state.get("quality_status", "fail")
        iteration = ctx.session.state.get("refinement_iteration", 0)
        
        # Increment iteration counter
        ctx.session.state["refinement_iteration"] = iteration + 1
        
        # Check if status contains "pass"
        should_stop = "pass" in str(status_text).lower()
        
        # Provide feedback
        if should_stop:
            message = f"✅ Plan quality is sufficient after {iteration + 1} iteration(s). Finalizing..."
        else:
            message = f"🔄 Plan needs refinement (iteration {iteration + 1}). Improving..."
        
        # Create Content object for the Event
        content = types.Content(
            role="model",
            parts=[types.Part.from_text(text=message)]
        )
        
        yield Event(
            author=self.name,
            content=content,
            actions=EventActions(escalate=should_stop)
        )


# =============================================================================
# PLAN REFINER - Improves plan based on quality checker feedback
# =============================================================================
plan_refiner = LlmAgent(
    name="PlanRefiner",
    model="gemini-2.0-flash",
    description="Improves travel plans by re-consulting specialists for missing data.",
    instruction="""
    You are the Plan Refiner. Your job is to improve the travel plan based on feedback.
    
    📝 REVIEW THE CONVERSATION:
    Look at previous messages to see:
    - Quality feedback on what's missing or needs improvement
    - Current plan that needs improvement
    - Original user requirements
    
    🔧 YOUR TASK:
    1. Read the quality feedback to identify what's missing
    2. Call the appropriate specialist tools to get missing data
    3. Update the plan with the new data
    
    💡 AVAILABLE TOOLS:
    - WeatherAgent: Call for weather data
    - SafetyAgent: Call for safety information
    - ActivityAgent: Call for activities and attractions
    - RouteAgent: Call for route and travel times
    - BudgetAgent: Call for budget breakdown
    
    After getting updated data from specialists, create an improved plan.
    
    📋 OUTPUT FORMAT:
    Create a comprehensive travel plan with ALL data from specialists.
    Include specific details, times, prices - no placeholders!
    """,
    tools=specialist_tools,  # Use AgentTool - no parent conflict
    output_key="draft_plan"
)


# =============================================================================
# INITIAL PLAN GENERATOR - Creates first draft from user requirements
# =============================================================================
initial_plan_generator = LlmAgent(
    name="InitialPlanGenerator",
    model="gemini-2.0-flash",
    description="Creates initial travel plan draft by gathering data from ALL specialists.",
    instruction="""
    You create the initial travel plan draft by consulting ALL specialists.
    
    📋 USER REQUIREMENTS:
    Read the user's trip requirements from the conversation history.
    Look for: destinations, dates, interests, and budget.
    
    🎯 YOUR PROCESS - CALL ALL 5 SPECIALIST TOOLS:
    You MUST call ALL 5 specialist tools. Do NOT skip any.
    
    1. Call WeatherAgent tool - Get weather for all destinations
    2. Call SafetyAgent tool - Get safety info for all locations  
    3. Call ActivityAgent tool - Get activities matching user interests
    4. Call RouteAgent tool - Calculate routes between destinations
    5. Call BudgetAgent tool - Estimate costs and breakdown
    
    After ALL specialists respond, create the comprehensive plan.
    
    💾 OUTPUT FORMAT:
    
    ## 🌴 Sri Lanka Travel Plan
    **Dates**: [dates from requirements]
    **Budget**: [budget from requirements]
    **Destinations**: [list destinations]
    
    ### 🌤️ Weather Summary
    [ACTUAL weather data from WeatherAgent - temperatures, conditions]
    
    ### ⚠️ Safety Information
    [ACTUAL safety data from SafetyAgent - advisories, tips]
    
    ### 📅 Day-by-Day Itinerary
    **Day 1**: 
    - Morning: [activity from ActivityAgent]
    - Afternoon: [activity]
    - Travel: [route info from RouteAgent with times]
    
    **Day 2**: [continue for all days]
    ...
    
    ### 💰 Budget Breakdown
    [ACTUAL budget data from BudgetAgent - accommodation, transport, food, activities]
    
    ### 🎯 Recommended Activities
    [ACTUAL activities from ActivityAgent with ratings and details]
    
    ⚠️ IMPORTANT RULES:
    - Call ALL 5 specialist tools before creating the plan
    - Use REAL data from specialist responses (not placeholders)
    - Include specific numbers, times, prices
    - Do NOT stop until plan is complete
    """,
    tools=specialist_tools,  # Use AgentTool - no parent conflict
    output_key="draft_plan"
)


# =============================================================================
# REVIEW WORKFLOW - Iterative Refinement with Quality Checking
# =============================================================================
# This implements the Iterative Refinement Pattern from ADK docs
refinement_loop = LoopAgent(
    name="RefinementLoop",
    max_iterations=3,  # Maximum 3 refinement attempts
    sub_agents=[
        quality_checker,    # Checks if plan meets criteria
        StopChecker(),      # Escalates if quality is sufficient
        plan_refiner        # Refines plan if quality check failed
    ]
)

# Main review workflow using Sequential Pattern
review_workflow = SequentialAgent(
    name="ReviewWorkflow",
    sub_agents=[
        initial_plan_generator,  # Step 1: Generate initial draft
        refinement_loop          # Step 2: Iteratively refine until quality is sufficient
    ]
)


# =============================================================================
# COORDINATOR WITH REVIEW WORKFLOW
# =============================================================================
travel_coordinator_with_review = LlmAgent(
    name="TravelCoordinatorWithReview",
    model="gemini-2.0-flash",
    description="Travel coordinator that uses iterative review and refinement to ensure high-quality plans.",
    instruction="""
    You are the Travel Coordinator with built-in quality assurance for Sri Lanka travel planning.
    
    🎯 YOUR ROLE:
    1. Greet users and collect their travel requirements
    2. IMMEDIATELY start the planning workflow - DO NOT ask unnecessary follow-up questions
    3. Save requirements to state['user_requirements'] 
    4. Transfer to ReviewWorkflow to generate and refine the plan
    5. Present the final plan to the user
    
    💬 GREETING (when user says hi/hello):
    "🌴 Welcome to Sri Lanka Travel Planning with Quality Assurance!
    
    I create comprehensive travel plans with built-in quality review to ensure:
    ✅ Real-time accurate data
    ✅ Practical and realistic itineraries
    ✅ Safety and budget considerations
    ✅ Complete activity recommendations
    
    Tell me about your trip: destinations, dates, interests, and budget."
    
    🚀 WHEN USER PROVIDES TRIP DETAILS:
    DO NOT ask for more clarification. Work with what the user provides.
    If they say "beaches", use popular beaches like Bentota, Unawatuna, Mirissa.
    If they don't specify activities, suggest based on their interests.
    
    IMMEDIATELY:
    1. Acknowledge their requirements briefly
    2. Save to state['user_requirements'] with all details
    3. Say "Creating your personalized travel plan with quality assurance..."
    4. Transfer to ReviewWorkflow: transfer_to_agent(agent_name='ReviewWorkflow')
    
    📋 EXAMPLE:
    User: "Plan a 4-day trip to beaches and Nuwara Eliya, budget 5M LKR"
    You: "Great! Creating your 4-day Sri Lanka adventure to beaches and Nuwara Eliya...
          I'll gather weather, safety, activities, routes, and budget information."
    Then: transfer_to_agent(agent_name='ReviewWorkflow')
    
    ⚠️ IMPORTANT:
    - Do NOT ask which specific beaches - suggest them yourself
    - Do NOT ask for more activity details - use their interests
    - ALWAYS proceed to ReviewWorkflow after getting basic requirements
    - The ReviewWorkflow will handle all data gathering automatically
    
    📊 AFTER WORKFLOW COMPLETES:
    When ReviewWorkflow returns (state['draft_plan'] is set):
    - Present the final plan with nice formatting
    - Mention quality was verified
    - Offer to make modifications if needed
    """,
    sub_agents=[review_workflow],
    output_key="final_response"
)


# =============================================================================
# ROOT AGENT FOR REVIEW PATTERN
# =============================================================================
root_agent_review = travel_coordinator_with_review


# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    'root_agent_review',
    'travel_coordinator_with_review',
    'review_workflow',
    'initial_plan_generator',
    'quality_checker',
    'plan_refiner',
    'refinement_loop',
    # Tools
    'weather_tool',
    'safety_tool',
    'activity_tool',
    'route_tool',
    'budget_tool'
]
