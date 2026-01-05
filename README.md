# Sri Lanka Travel Agent - Coordinator Multi-Agent System

An AI-powered travel planning system for Sri Lanka using **Google Agent Development Kit (ADK)** with **Coordinator Pattern** architecture for intelligent, LLM-driven delegation to specialist agents.

## Architecture

**Coordinator Pattern with Sub-Agents**: Single TravelCoordinator with LLM-driven transfer_to_agent() delegation
- 🎯 **LLM-Driven Transfer**: Intelligent routing via transfer_to_agent()
- 💬 **Conversational**: Natural multi-turn dialogue with dynamic specialist access
- 🔧 **Flexible**: Handles simple queries to comprehensive trip planning
- 🧠 **Intelligent**: LLM understands context and routes appropriately

```
TravelCoordinator (LLM Agent)
├─→ WeatherAgent (sub-agent: weather data)
├─→ SafetyAgent (sub-agent: travel advisories)
├─→ ActivityAgent (sub-agent: attractions & experiences)
├─→ RouteAgent (sub-agent: distances & travel times)
├─→ BudgetAgent (sub-agent: cost estimates)
└─→ PlanReviewerAgent (sub-agent: plan synthesis)
```

## Features

✅ **LLM-Driven Delegation** - transfer_to_agent() for intelligent routing  
✅ **Sub-Agent Hierarchy** - Clean parent-child relationships  
✅ **Real-Time Data** - OpenWeatherMap, Google Maps, Google Places  
✅ **Session Management** - Multi-turn conversations with context  
✅ **Human Approval** - Optional review workflow  
✅ **Natural Conversation** - LLM decides when and how to delegate  

## Project Structure

```
travel agent/
├── main.py                 # FastAPI entry point
├── config/                 # Configuration settings
│   └── settings.py
├── agents/                 # Agent definitions
│   ├── agent.py            # Root agent export for ADK
│   ├── orchestrator.py     # Multi-agent orchestrator
│   ├── workflow.py         # TravelCoordinator + specialists
│   └── specialists/        # Domain specialist agents
│       ├── weather_agent.py
│       ├── safety_agent.py
│       ├── route_agent.py
│       ├── budget_agent.py
│       ├── activity_agent.py
│       └── plan_reviewer_agent.py
├── tools/                  # Tool implementations
│   ├── weather_tool.py     # OpenWeatherMap API
│   ├── safety_tool.py      # Safety information
│   ├── route_tool.py       # Google Maps API
│   ├── budget_tool.py      # Pricing tools
│   ├── activity_tool.py    # Google Places API
│   ├── shared_context.py   # Shared state utilities
│   └── human_approval_tool.py  # Human-in-the-Loop (optional)
└── docs/
    ├── ARCHITECTURE.md     # Detailed architecture docs
    └── IMPROVEMENTS.md     # Future enhancements
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables** in `.env`:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key
   GOOGLE_MAPS_API_KEY=your_maps_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

## Running the Application

### Method 1: ADK Web Interface (Recommended)
```bash
adk web
# Open browser to http://127.0.0.1:8000
```

### Method 2: FastAPI Server
```bash
# Development
uvicorn main:app --reload --port 8000

# Production
python main.py
```

### Method 3: Python Script
```python
from agents.orchestrator import simple_process

response = simple_process("Plan a 5-day trip to Sri Lanka")
print(response)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/plan` | Full planning (with optional approval) |
| POST | `/quick-plan` | Quick query without approval |
| POST | `/approve` | Submit approval decision (optional) |
| GET | `/pending-approvals` | List pending approvals |
| GET | `/session/{user_id}` | Get session state |
| DELETE | `/session/{user_id}` | Clear session |
| GET | `/health` | Health check |

## Usage Examples

### Simple Query
```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Colombo?"}'
```

### Full Trip Planning
```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Plan a 5-day cultural tour: Colombo, Kandy, Sigiriya. Budget traveler.",
    "user_id": "user123"
  }'
```

### Quick Query (Faster)
```bash
curl -X POST http://localhost:8000/quick-plan \
  -H "Content-Type: application/json" \
  -d '{"query": "How long from Colombo to Galle?"}'
```

### With Human Approval (Optional)
```bash
# 1. Request with approval
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{"query": "...", "require_approval": true}'

# 2. Submit approval
curl -X POST http://localhost:8000/approve \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "approval_20260101_120000",
    "decision": "APPROVED"
  }'
```

## How It Works

1. **User Query** → TravelCoordinator receives request
2. **LLM Decision** → Coordinator's LLM analyzes query type
3. **Dynamic Routing** → Calls appropriate specialist(s)
   - Simple query: Single specialist
   - Complex plan: Multiple specialists or ParallelDataGatherer
4. **Response** → Coordinator synthesizes and returns result

**Example Flow:**
```
"What's the weather in Ella?" 
  → Coordinator calls WeatherAgent only
  → Fast, focused response

"Plan a 5-day trip"
  → Coordinator calls ParallelDataGatherer
  → All specialists run concurrently
  → PlanReviewerAgent synthesizes
  → Comprehensive itinerary
```

## Architecture Details

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation on:
- Coordinator Pattern implementation
- Agent communication patterns
- AgentTool vs sub_agents approach
- Parallel execution strategy
- Session state management

## Key Technologies

- **Google ADK** - Agent Development Kit
- **Google Gemini 2.0 Flash** - LLM for agents
- **FastAPI** - REST API framework
- **Pydantic** - Data validation
- **OpenWeatherMap API** - Weather data
- **Google Maps API** - Routes & directions
- **Google Places API** - Activities & attractions

---

**Architecture**: Coordinator Pattern  
**ADK Version**: Python v0.1.0  
**Last Updated**: January 5, 2026

MIT
```
