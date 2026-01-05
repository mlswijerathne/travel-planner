# Sri Lanka Travel Agent - Multi-Agent Architecture

## Overview

This travel planning system uses **Google Agent Development Kit (ADK)** multi-agent architecture with a **Human-in-the-Loop** pattern for critical approval workflows.

Based on: https://google.github.io/adk-docs/agents/multi-agents/

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRAVEL PLANNING WORKFLOW                              │
│                         (SequentialAgent)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 1: Request Analyzer (LlmAgent)                                   │   │
│  │ - Extracts: destinations, duration, interests, budget, dates         │   │
│  │ - Output: request_analysis                                            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 2: Critical Info Gatherer (ParallelAgent)                        │   │
│  │ ┌─────────────────────┐  ┌─────────────────────┐                      │   │
│  │ │   Safety Agent      │  │   Weather Agent     │   ← Run in Parallel │   │
│  │ │ Output: safety_info │  │ Output: weather_info│                      │   │
│  │ └─────────────────────┘  └─────────────────────┘                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 3: Travel Data Gatherer (ParallelAgent)                          │   │
│  │ ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │   │
│  │ │Activity Agent │  │  Route Agent  │  │ Budget Agent  │ ← Parallel   │   │
│  │ │activity_info  │  │  route_info   │  │  budget_info  │               │   │
│  │ └───────────────┘  └───────────────┘  └───────────────┘               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 4: Plan Reviewer Agent (LlmAgent)                                │   │
│  │ - Synthesizes all gathered data                                       │   │
│  │ - Creates comprehensive travel plan                                   │   │
│  │ - Output: draft_plan                                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 5: Human Approval Agent (LlmAgent) 🧑‍💼 HUMAN-IN-THE-LOOP        │   │
│  │ - Reviews draft plan                                                  │   │
│  │ - Calls request_human_approval tool                                   │   │
│  │ - PAUSES for human decision                                           │   │
│  │ - Output: approval_request                                            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 6: Final Response Agent (LlmAgent)                               │   │
│  │ - Processes human decision                                            │   │
│  │ - Delivers final approved plan                                        │   │
│  │ - Output: final_response                                              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Specialized Agents

### 1. Weather Agent
- **Tools**: `get_weather`, `get_weather_forecast`
- **API**: OpenWeatherMap
- **Output Key**: `weather_info`

### 2. Safety Agent
- **Tools**: `get_safety_info`, `get_travel_advisory`
- **API**: Google Places (reviews)
- **Output Key**: `safety_info`

### 3. Route Agent
- **Tools**: `get_route`, `get_directions`, `get_travel_options`
- **API**: Google Maps Distance Matrix & Directions
- **Output Key**: `route_info`

### 4. Budget Agent
- **Tools**: `check_budget`, `get_currency_rate`, `compare_costs`
- **API**: Google Places, Exchange Rate API
- **Output Key**: `budget_info`

### 5. Activity Agent
- **Tools**: `get_activities`, `get_place_details`
- **API**: Google Places
- **Output Key**: `activity_info`

### 6. Plan Reviewer Agent
- **Role**: Synthesizes all data into coherent travel plan
- **Output Key**: `draft_plan`

### 7. Human Approval Agent
- **Tools**: `request_human_approval`
- **Role**: Implements Human-in-the-Loop pattern
- **Output Key**: `approval_request`

### 8. Final Response Agent
- **Role**: Processes approval and delivers final plan
- **Output Key**: `final_response`

## Human-in-the-Loop Pattern

The system implements ADK's Human-in-the-Loop pattern:

```python
# 1. Human Approval Tool pauses workflow
approval_tool = FunctionTool(func=request_human_approval)

# 2. Agent prepares approval request
human_approval_agent = LlmAgent(
    name="HumanApprovalAgent",
    tools=[approval_tool],
    output_key="approval_request"
)

# 3. Human reviews via API
POST /approve
{
    "request_id": "approval_20260101_120000",
    "decision": "APPROVED",  # or APPROVED_WITH_CHANGES, REJECTED, REQUEST_CHANGES
    "feedback": "Looks great!",
    "modifications": null
}

# 4. Workflow continues with decision
```

### Approval Decisions

| Decision | Proceed | Description |
|----------|---------|-------------|
| `APPROVED` | ✅ Yes | Plan is finalized as-is |
| `APPROVED_WITH_CHANGES` | ✅ Yes | Plan modified per human feedback |
| `REJECTED` | ❌ No | Plan rejected, reason provided |
| `REQUEST_CHANGES` | ❌ No | Human requests specific changes |

## API Endpoints

### Planning Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/plan` | Full planning with approval workflow |
| POST | `/quick-plan` | Quick planning without approval |

### Approval Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/approve` | Submit approval decision |
| GET | `/pending-approvals` | List pending approvals |
| GET | `/approval-status/{id}` | Check approval status |

### Session Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/session/{user_id}` | Get session state |
| DELETE | `/session/{user_id}` | Clear session |

## Shared Session State

Agents communicate via shared state:

```python
# Agent 1 writes
output_key="weather_info"  # → state['weather_info']

# Agent 2 reads
instruction="...based on {weather_info}..."  # Reads from state
```

## ADK Primitives Used

1. **LlmAgent**: AI-powered agents with tools
2. **SequentialAgent**: Ordered execution pipeline
3. **ParallelAgent**: Concurrent execution for efficiency
4. **FunctionTool**: Custom tools for human approval
5. **Runner**: Executes agent workflows
6. **InMemorySessionService**: Session/state management

## File Structure

```
travel agent/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys)
├── README.md                   # Project documentation
│
├── config/                     # Configuration
│   ├── __init__.py
│   └── settings.py             # Application settings
│
├── agents/                     # Agent definitions
│   ├── __init__.py
│   ├── orchestrator.py         # Multi-agent orchestrator
│   ├── workflow.py             # Workflow definitions (Sequential/Parallel)
│   └── specialists/            # Specialized domain agents
│       ├── __init__.py
│       ├── weather_agent.py    # Weather specialist
│       ├── safety_agent.py     # Safety specialist
│       ├── route_agent.py      # Route planning specialist
│       ├── budget_agent.py     # Budget specialist
│       ├── activity_agent.py   # Activity finder specialist
│       └── plan_reviewer_agent.py  # Plan synthesizer
│
├── tools/                      # Tool implementations
│   ├── __init__.py
│   ├── weather_tool.py         # OpenWeatherMap API
│   ├── safety_tool.py          # Safety info tools
│   ├── route_tool.py           # Google Maps API
│   ├── budget_tool.py          # Pricing tools
│   ├── activity_tool.py        # Google Places API
│   └── human_approval_tool.py  # Human-in-the-Loop tool
│
└── docs/                       # Documentation
    └── ARCHITECTURE.md         # This file
```

## Running the Application

### Start Multi-Agent API

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENWEATHER_API_KEY=your_key
export GOOGLE_MAPS_API_KEY=your_key
export GOOGLE_API_KEY=your_key

# Run the API
python main.py
# or
uvicorn main_multi:app --reload --port 8000
```

### Example Usage

```bash
# 1. Request a travel plan
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Plan a 5-day trip to Kandy and Sigiriya for wildlife and heritage",
    "user_id": "user123",
    "require_approval": true
  }'

# 2. Check pending approvals
curl http://localhost:8000/pending-approvals

# 3. Submit approval
curl -X POST http://localhost:8000/approve \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "approval_20260101_120000",
    "decision": "APPROVED",
    "user_id": "user123"
  }'
```

## Benefits of Multi-Agent Architecture

1. **Modularity**: Each agent has single responsibility
2. **Parallelism**: Independent tasks run concurrently
3. **Specialization**: Agents optimized for their domain
4. **Maintainability**: Easy to update individual agents
5. **Human Oversight**: Critical decisions require approval
6. **Reusability**: Agents can be reused in other workflows

## References

- [Google ADK Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [Human-in-the-Loop Pattern](https://google.github.io/adk-docs/agents/multi-agents/#human-in-the-loop-pattern)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)
